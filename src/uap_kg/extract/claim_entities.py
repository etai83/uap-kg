"""Propose entity mentions from a processed transcript, then ask Jev to type them.

Jev is a System One model. It answers Choice and Noul questions. It does not
generate text. This module follows that limit:

1. Code over-finds candidate phrases and copies each one from the span.
2. One System One call per span asks, for each candidate, whether the speakers
   discuss it as an entity and which type it is.
3. Code keeps the copied words. A low judgment goes to review. A rejected
   judgment is counted and dropped. Nothing here is a verified finding.

Entity types match the investigator ontology: named_person, organization,
project, location, object, uap_item, date_time. ``none`` is the escape hatch.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

TYPESAFE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai/v1/systemone").rstrip("/")
DEFAULT_MODEL = "jev-latest"
ACCEPT_NOUL = 0.70
REVIEW_NOUL = 0.45
MIN_TYPE_CONFIDENCE = 0.40
IMPORTANT_NOUL = 0.60
WORDLIST = Path("/usr/share/dict/words")

ENTITY_TYPES = (
    "named_person",
    "organization",
    "project",
    "location",
    "object",
    "uap_item",
    "date_time",
)

TYPE_CRITERIA = {
    "named_person": "A person the words talk about. Not the speaker role by itself.",
    "organization": "A group, service, agency, or company. Not a named program or project.",
    "project": "A named program, investigation, task force, or other effort. Not the agency or company that runs it. Not a person. Not a generic use of the word project.",
    "location": "A place named in the words. Not the place where the video was filmed.",
    "object": "A physical thing, a document, or a vehicle. Not a person, a place, or a UAP item.",
    "uap_item": "A craft, a material sample, a sensor track, or another UAP-relevant item. The mention is not proof that the item exists.",
    "date_time": "A year, a season, a calendar date, a clock time, or a duration the words name. Not the time mark of the video span.",
    "none": "Not an entity. Filler, a verb, a pronoun, or ordinary grammar.",
}

# Named efforts whose parts are ordinary words. A project is not an organization.
PROJECT_PHRASES = (
    "immaculate constellation",
    "manhattan project",
    "project blue book",
    "project blue box",
    "project rubik's cube",
    "uap task force",
    "galileo project",
    "project twinkle",
    "project grudge",
    "project sign",
    "kona blue",
    "blue book",
)
PROJECT_ACRONYMS = frozenset({"uaptf", "aatip", "aawsap", "atip", "osap"})

# Function words. A candidate may not start or end on one of these.
STOP = frozenset(
    """
    a an the and or of to in on for with at from by as is was were be been am are
    i you we they he she it this that these those my your his her our their me him
    them us not no yes yeah uh um like just so but if then than about into over
    after before when what which who how there here up out do did does doing have
    has had would could should can will wont going gonna know think mean said say
    says said well right okay ok really very also because thats it's i'm im dont
    don't didnt didn't cant can't its wasnt it's that's there's here's gonna
    gonna got get come came going look looks looked see saw seen tell told talk
    talking something anything everything someone somebody thing things stuff
    people way kind sort bit lot guy guys really actually basically literally
    maybe perhaps around approximately about near back again still already even
    one ones
    """.split()
)

# In-vocabulary words that are still worth proposing as unigrams in this domain.
# Jev drops the ordinary uses. Common words that are too broad (light, base,
# program, report) stay out of this set. Multiword seeds cover those phrases.
DOMAIN_UNIGRAMS = frozenset(
    """
    craft crafts triangle triangles hangar arrow sap uap ufo ufos nhi orb orbs
    camouflage wormhole barracks runway whistleblower congress nuclear carrier
    carriers alien aliens mfr submarine radar footage alloy tic tac
    """.split()
)

# Multiword phrases whose parts are ordinary English. Longest match wins.
DOMAIN_PHRASES = (
    "united states air force",
    "langley air force base",
    "air force base",
    "air force",
    "special access program",
    "equilateral triangle",
    "nasa hangar",
    "lockheed martin",
    "aircraft carriers",
    "aircraft carrier",
    "nuclear sites",
    "nuclear site",
    "memorandum for record",
    "inspector general",
    "death penalty",
    "white light",
    "black metallic",
    "geospatial intelligence",
    "reverse engineering",
    "active camouflage",
    "unusual material",
    "j wicks",
    "chris sharp",
    "jeremy corbell",
    "james lacatski",
    "eric burleson",
    "david grusch",
    "dave grusch",
    "george knapp",
    "glenn gaffney",
    "tim phillips",
    "robert bigelow",
    "dylan borland",
    "jesse michels",
    *PROJECT_PHRASES,
)

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
CLOCK_RE = re.compile(r"\b(?:[01]\d|2[0-3])[:.]?[0-5]\d\b")
MILITARY_RE = re.compile(r"\b[0-2]\d[0-5]\d\b")
SEASON_RE = re.compile(
    r"\b(?:spring|summer|fall|autumn|winter)(?:\s+of)?\s+(?:19|20)\d{2}\b",
    re.I,
)
DURATION_RE = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    r"(?:to\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+)?"
    r"(?:seconds?|minutes?|hours?)\b",
    re.I,
)
COMMA_NUM_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\s+(?:feet|foot))?\b", re.I)
SITE_RE = re.compile(r"\bS[- ]?4\b", re.I)
ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")

# Names the Borland audit print looks for. Not a filter.
RECALL_PROBES = (
    "dylan borland",
    "jesse",
    "united states air force",
    "nasa hangar",
    "summer of 2012",
    "equilateral triangle",
    "langley",
    "arrow",
    "tim phillips",
    "george knapp",
    "lockheed martin",
    "glenn gaffney",
    "bigelow",
    "special access program",
    "mfr",
    "j wicks",
    "congress",
    "cia",
    "chris sharp",
    "white light",
    "jesse",
    "2012",
    "0130",
)

# A number plus a unit is a measure. Bare numbers are not expanded into phrases.
UNIT_RE = re.compile(
    r"(?<![\d,])\b\d[\d,]*(?:\s+(?:foot|feet|ft|seconds?|minutes?|hours?|years?|miles?|mph))\b",
    re.I,
)


@dataclass(frozen=True)
class Candidate:
    surface: str
    norm: str
    start: int
    end: int


@dataclass
class Occurrence:
    norm: str
    surface: str
    span_index: int
    t_start: float
    t_end: float
    speaker_label: str
    quote: str
    passage: str


@dataclass
class Judgment:
    occurrence: Occurrence
    is_entity: float
    type_choice: str
    type_confidence: float
    type_probabilities: dict[str, float]
    decision: str  # accept | review | reject


@dataclass
class ExtractResult:
    video_id: str
    model: str
    entities: list[dict[str, Any]]
    review: list[dict[str, Any]]
    claim_links: list[dict[str, str]]
    stats: dict[str, Any] = field(default_factory=dict)


def norm(text: str) -> str:
    folded = text.casefold().replace("’", "'")
    folded = re.sub(r"[^a-z0-9'\s]", " ", folded)
    return re.sub(r"\s+", " ", folded).strip()


def is_project_surface(value: str) -> bool:
    """True when the words name an effort the project pass should judge."""
    key = norm(value)
    if not key:
        return False
    if key in {norm(phrase) for phrase in PROJECT_PHRASES} or key in PROJECT_ACRONYMS:
        return True
    parts = key.split()
    return len(parts) >= 2 and parts[0] == "project" and parts[1] not in STOP


def load_wordlist(path: Path = WORDLIST) -> set[str]:
    if not path.is_file():
        return set()
    return {line.strip().casefold() for line in path.read_text(errors="ignore").splitlines() if line.strip()}


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in phrase.split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b", re.I)


_PHRASE_RES = tuple((_phrase_pattern(phrase), phrase) for phrase in sorted(DOMAIN_PHRASES, key=len, reverse=True))


def _add(bucket: dict[str, Candidate], surface: str, start: int, end: int) -> None:
    surface = surface.strip()
    key = norm(surface)
    if len(key) < 2 or key in STOP:
        return
    if key.isdigit() and not re.fullmatch(r"(?:19|20)\d{2}|[0-2]\d[0-5]\d", key):
        return
    # "10,000" also matches a trailing "000". Drop that fragment. Keep 0130.
    if re.match(r"^0{2,}(?:\s|$)", key):
        return
    current = bucket.get(key)
    if current is None or (end - start) > (current.end - current.start):
        bucket[key] = Candidate(surface, key, start, end)


def _marked(token: str, words: set[str], names: set[str] | None = None) -> bool:
    low = token.casefold()
    if low in STOP or len(low) < 2 or token.isdigit():
        return False
    if low in DOMAIN_UNIGRAMS or (names and low in names):
        return True
    if any(char.isdigit() for char in token) and any(char.isalpha() for char in token):
        return True
    if token.isupper() and len(token) >= 2:
        return True
    if any(char.isupper() for char in token[1:]):
        return True
    if low not in words and len(low) >= 3 and low.isalpha():
        return True
    return False


def collect_name_tokens(texts: Iterable[str]) -> set[str]:
    """Dictionary words used as names. Count mid-span capitals, not sentence starts.

    'Jesse' inside a sentence counts. 'During' at the start of a span does not.
    Two such uses put the word on the name list, including later lowercase repeats.
    """
    counts: Counter[str] = Counter()
    for text in texts:
        tokens = list(TOKEN_RE.finditer(text))
        for index, match in enumerate(tokens):
            raw = match.group()
            if len(raw) < 3 or not raw[0].isupper() or raw[1:] != raw[1:].lower():
                continue
            low = raw.casefold()
            if low in STOP:
                continue
            if index == 0:
                continue
            between = text[tokens[index - 1].end() : match.start()]
            if re.search(r"[.!?]", between):
                continue
            counts[low] += 1
    return {token for token, count in counts.items() if count >= 2}


def find_candidates(
    text: str,
    words: set[str],
    frequent: set[tuple[str, ...]] | None = None,
    names: set[str] | None = None,
) -> list[Candidate]:
    """Return verbatim candidate slices from ``text``. Recall is the goal.

    A phrase may contain a marked token. It may not contain a function word.
    Bare numbers stay out. A number plus a unit is kept by UNIT_RE.
    """
    found: dict[str, Candidate] = {}
    frequent = frequent or set()
    names = names or set()

    for pattern in (SEASON_RE, YEAR_RE, DURATION_RE, COMMA_NUM_RE, UNIT_RE, SITE_RE, ACRONYM_RE, CLOCK_RE, MILITARY_RE):
        for match in pattern.finditer(text):
            _add(found, match.group(0), match.start(), match.end())

    for pattern, _phrase in _PHRASE_RES:
        for match in pattern.finditer(text):
            _add(found, match.group(0), match.start(), match.end())

    tokens = list(TOKEN_RE.finditer(text))
    count = len(tokens)
    for start_at in range(count):
        for length in (1, 2, 3, 4):
            end_at = start_at + length
            if end_at > count:
                break
            chunk = tokens[start_at:end_at]
            between_ok = True
            for left, right in zip(chunk, chunk[1:]):
                between = text[left.end() : right.start()]
                if re.search(r"[.!?\n]", between) or not re.fullmatch(r"[\s\-]+", between or " "):
                    between_ok = False
                    break
            if not between_ok:
                continue
            raw_tokens = [item.group() for item in chunk]
            lows = [token.casefold() for token in raw_tokens]
            if any(token in STOP for token in lows):
                continue
            key = tuple(lows)
            marks = [_marked(token, words, names) for token in raw_tokens]
            if length == 1:
                if marks[0]:
                    _add(found, text[chunk[0].start() : chunk[-1].end()], chunk[0].start(), chunk[-1].end())
                continue
            if not any(marks):
                if key in frequent:
                    _add(found, text[chunk[0].start() : chunk[-1].end()], chunk[0].start(), chunk[-1].end())
                continue
            if length == 2 or sum(marks) >= length - 1:
                _add(found, text[chunk[0].start() : chunk[-1].end()], chunk[0].start(), chunk[-1].end())

    return list(found.values())


def frequent_phrases(texts: Iterable[str], min_bi: int = 5, min_tri: int = 3) -> set[tuple[str, ...]]:
    """Repeated content phrases. Used only as extra candidate recall."""
    counts: Counter[tuple[str, ...]] = Counter()
    for text in texts:
        tokens = [match.group().casefold() for match in TOKEN_RE.finditer(text)]
        for size, floor in ((2, min_bi), (3, min_tri)):
            for index in range(0, len(tokens) - size + 1):
                chunk = tuple(tokens[index : index + size])
                if any(token in STOP for token in chunk):
                    continue
                counts[chunk] += 1
    return {chunk for chunk, count in counts.items() if count >= (min_bi if len(chunk) == 2 else min_tri)}


def build_passage(spans: list[dict[str, Any]], index: int) -> str:
    lines = []
    for neighbor in spans[max(0, index - 1) : index + 2]:
        speaker = neighbor.get("speaker_label") or "UNKNOWN"
        text = (neighbor.get("text") or "").replace("\n", " ").strip()
        if text:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def collect_occurrences(
    spans: list[dict[str, Any]],
    words: set[str],
    speaker_notes: dict[str, str] | None = None,
) -> list[Occurrence]:
    texts = [(span.get("text") or "") for span in spans]
    frequent = frequent_phrases(texts)
    names = collect_name_tokens(texts)
    occurrences: list[Occurrence] = []
    notes = speaker_notes or {}
    for index, span in enumerate(spans):
        text = (span.get("text") or "").replace("\n", " ").strip()
        if len(text) < 8:
            continue
        passage = build_passage(spans, index)
        if notes:
            note_lines = [f"{label}: {note}" for label, note in notes.items()]
            passage = "Speaker notes:\n" + "\n".join(note_lines) + "\n\n" + passage
        for candidate in find_candidates(text, words, frequent, names):
            occurrences.append(
                Occurrence(
                    norm=candidate.norm,
                    surface=candidate.surface,
                    span_index=index,
                    t_start=float(span.get("t_start") or 0),
                    t_end=float(span.get("t_end") or 0),
                    speaker_label=span.get("speaker_label") or "UNKNOWN",
                    quote=text,
                    passage=passage,
                )
            )
    return occurrences


def _stable(norm_value: str, words: set[str]) -> bool:
    parts = norm_value.split()
    if len(parts) >= 2 or any(char.isdigit() for char in norm_value):
        return True
    if not parts:
        return False
    return parts[0] not in words


def select_occurrences(occurrences: list[Occurrence], words: set[str]) -> list[Occurrence]:
    """Cap how many times one surface is sent to Jev.

    A stable name (multiword, OOV, number) is judged in up to three passages.
    A common-word unigram is judged in up to twelve passages, spread through
    the video. Code does not copy an accept onto an unjudged common word.
    """
    grouped: dict[str, list[Occurrence]] = defaultdict(list)
    for item in occurrences:
        grouped[item.norm].append(item)
    selected: list[Occurrence] = []
    for key, items in grouped.items():
        items = sorted(items, key=lambda item: item.t_start)
        cap = 3 if _stable(key, words) else 12
        if len(items) <= cap:
            selected.extend(items)
            continue
        if cap == 1:
            selected.append(items[0])
            continue
        step = (len(items) - 1) / (cap - 1)
        picked = []
        seen: set[int] = set()
        for slot in range(cap):
            choice = items[int(round(slot * step))]
            if choice.span_index in seen:
                continue
            seen.add(choice.span_index)
            picked.append(choice)
        selected.extend(picked)
    return selected


def questions_for(candidates: list[str]) -> dict[str, dict[str, Any]]:
    questions: dict[str, dict[str, Any]] = {}
    for index, surface in enumerate(candidates):
        questions[f"is_entity_{index}"] = {
            "type": "noul",
            "instructions": {
                "candidate": surface,
                "question": "In the passage, do the speakers discuss `candidate` as one specific entity?",
            },
            "criteria": {
                "true": "The candidate names one person, organization, project, place, object, UAP item, or date and time that this passage discusses.",
                "false": "The candidate is filler, a generic verb, a pronoun, a fragment that names no thing, or a prompt with no named thing.",
            },
        }
        questions[f"entity_type_{index}"] = {
            "type": "choice",
            "instructions": {
                "candidate": surface,
                "question": "What type of entity is `candidate` in this passage? Choose none if it is not an entity.",
            },
            "criteria": TYPE_CRITERIA,
        }
    return questions


def decide(is_entity: float, type_choice: str, type_confidence: float) -> str:
    if type_choice not in ENTITY_TYPES:
        return "reject"
    if is_entity >= ACCEPT_NOUL and type_confidence >= MIN_TYPE_CONFIDENCE:
        return "accept"
    if is_entity >= REVIEW_NOUL:
        return "review"
    return "reject"


class JevError(RuntimeError):
    pass


class JevClient:
    """Small System One client. Stdlib only, so the script has no extra install."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, cache_path: Path | None = None, timeout: float = 60.0):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.cache_path = cache_path
        self._lock = threading.Lock()
        self._cache: dict[str, dict[str, Any]] = {}
        self.input_tokens = 0
        self.output_tokens = 0
        self.requests = 0
        self.cache_hits = 0
        if cache_path and cache_path.is_file():
            for line in cache_path.read_text().splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self._cache[row["key"]] = row["response"]

    def system_one(self, state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
        payload = {"state": state, "model": self.model, "questions": questions}
        key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        with self._lock:
            cached = self._cache.get(key)
        if cached is not None:
            with self._lock:
                self.cache_hits += 1
            return cached
        body = json.dumps(payload).encode()
        last_error: Exception | None = None
        for attempt in range(6):
            request = urllib.request.Request(
                TYPESAFE_URL,
                data=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    parsed = json.loads(response.read().decode())
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode(errors="replace")[:500]
                last_error = JevError(f"HTTP {exc.code}: {detail}")
                if exc.code not in {429, 500, 502, 503, 529}:
                    raise last_error from exc
                time.sleep(min(30, 2**attempt))
            except (TimeoutError, urllib.error.URLError) as exc:
                last_error = JevError(str(exc))
                time.sleep(min(30, 2**attempt))
        else:
            raise last_error or JevError("Jev request failed")
        usage = parsed.get("usage") or {}
        with self._lock:
            self.requests += 1
            self.input_tokens += int(usage.get("input_tokens") or 0)
            self.output_tokens += int(usage.get("output_tokens") or 0)
            self._cache[key] = parsed
            if self.cache_path:
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                with self.cache_path.open("a") as handle:
                    handle.write(json.dumps({"key": key, "response": parsed}) + "\n")
        return parsed


def _confidence(answer: dict[str, Any]) -> float:
    if "confidence" in answer:
        return float(answer["confidence"])
    probabilities = answer.get("probabilities") or {}
    if not probabilities:
        return 0.0
    return float(max(probabilities.values()))


def judge_span(client: JevClient, occurrences: list[Occurrence]) -> tuple[list[Judgment], str]:
    """Judge every candidate in one span. The span text is the quote."""
    state = {
        "passage": occurrences[0].passage,
        "note": "The speaker label is who spoke. A named person is someone the words talk about. Those two roles differ. An entity mention is not a claim.",
    }
    surfaces = [item.surface for item in occurrences]
    response = client.system_one(state, questions_for(surfaces))
    answers = response.get("answers") or {}
    model = str(response.get("model") or client.model)
    judgments: list[Judgment] = []
    for index, occurrence in enumerate(occurrences):
        entity_answer = answers.get(f"is_entity_{index}") or {}
        type_answer = answers.get(f"entity_type_{index}") or {}
        is_entity = float(entity_answer.get("noul") or 0.0)
        type_choice = str(type_answer.get("choice") or "none")
        probabilities = {str(key): float(value) for key, value in (type_answer.get("probabilities") or {}).items()}
        confidence = _confidence(type_answer)
        judgments.append(
            Judgment(
                occurrence=occurrence,
                is_entity=is_entity,
                type_choice=type_choice,
                type_confidence=confidence,
                type_probabilities=probabilities,
                decision=decide(is_entity, type_choice, confidence),
            )
        )
    return judgments, model


def is_subphrase(short: str, long: str) -> bool:
    short_parts = short.split()
    long_parts = long.split()
    if not short_parts or len(short_parts) >= len(long_parts):
        return False
    width = len(short_parts)
    return any(long_parts[index : index + width] == short_parts for index in range(len(long_parts) - width + 1))


def suppress_fragments(judgments: list[Judgment]) -> list[Judgment]:
    """Drop a shorter same-type accept when the same span has the longer phrase.

    NASA inside NASA hangar stays if the types differ. Triangle inside
    equilateral triangle drops when both are UAP items.
    """
    accepted = [item for item in judgments if item.decision == "accept"]
    drop: set[int] = set()
    by_span: dict[int, list[int]] = defaultdict(list)
    for index, item in enumerate(accepted):
        by_span[item.occurrence.span_index].append(index)
    for indexes in by_span.values():
        for left in indexes:
            for right in indexes:
                if left == right:
                    continue
                a, b = accepted[left], accepted[right]
                if a.type_choice != b.type_choice:
                    continue
                if is_subphrase(a.occurrence.norm, b.occurrence.norm):
                    drop.add(left)
    kept = [item for index, item in enumerate(accepted) if index not in drop]
    rest = [item for item in judgments if item.decision != "accept"]
    return rest + kept


def _mention(item: Judgment) -> dict[str, Any]:
    occurrence = item.occurrence
    if norm(item.occurrence.surface) not in norm(occurrence.quote):
        raise ValueError(f"surface is not in the span: {occurrence.surface!r}")
    return {
        "span_index": occurrence.span_index,
        "t_start": occurrence.t_start,
        "t_end": occurrence.t_end,
        "speaker_label": occurrence.speaker_label,
        "quote": occurrence.quote,
        "surface": occurrence.surface,
        "is_entity": round(item.is_entity, 4),
        "type_choice": item.type_choice,
        "type_confidence": round(item.type_confidence, 4),
    }


def cluster_entities(accepted: list[Judgment]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[Judgment]] = defaultdict(list)
    for item in accepted:
        groups[(item.type_choice, item.occurrence.norm)].append(item)
    entities = []
    for (type_name, _key), items in groups.items():
        items = sorted(items, key=lambda item: item.occurrence.t_start)
        names = Counter(item.occurrence.surface for item in items)
        mentions = [_mention(item) for item in items]
        entities.append(
            {
                "name": names.most_common(1)[0][0],
                "norm": items[0].occurrence.norm,
                "type": type_name,
                "lifecycle": "proposed",
                "judged_by": "jev",
                "mentions": mentions,
            }
        )
    entities.sort(key=lambda item: (item["mentions"][0]["t_start"], item["name"].casefold()))
    for number, entity in enumerate(entities, 1):
        entity["id"] = f"ENT-{number:03d}"
    return entities


def _next_entity_id(entities: list[dict[str, Any]]) -> int:
    highest = 0
    for entity in entities:
        match = re.fullmatch(r"ENT-(\d+)", str(entity.get("id") or ""))
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def apply_project_entities(payload: dict[str, Any], projects: list[dict[str, Any]]) -> dict[str, int]:
    """Add project judgments to an existing entity file.

    The same name keeps its id and becomes a project. A new name is appended.
    Other entities stay as they are.
    """
    entities = payload.setdefault("entities", [])
    by_norm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        by_norm[norm(entity.get("name") or entity.get("norm") or "")].append(entity)
    next_id = _next_entity_id(entities)
    retagged = 0
    added = 0
    for project in projects:
        key = norm(project.get("norm") or project.get("name") or "")
        if not key:
            continue
        rows = by_norm.get(key) or []
        incoming = list(project.get("mentions") or [])
        if rows:
            for row in rows:
                if row.get("type") != "project":
                    row["type"] = "project"
                    retagged += 1
                row["judged_by"] = "jev"
                row["lifecycle"] = row.get("lifecycle") or "proposed"
                seen = {
                    (mention.get("span_index"), mention.get("surface"))
                    for mention in row.get("mentions") or []
                }
                mentions = list(row.get("mentions") or [])
                for mention in incoming:
                    marker = (mention.get("span_index"), mention.get("surface"))
                    if marker in seen:
                        continue
                    seen.add(marker)
                    mentions.append(mention)
                row["mentions"] = mentions
            continue
        created = {
            "name": project.get("name") or key,
            "norm": key,
            "type": "project",
            "lifecycle": "proposed",
            "judged_by": "jev",
            "mentions": incoming,
            "id": f"ENT-{next_id:03d}",
        }
        next_id += 1
        entities.append(created)
        by_norm[key] = [created]
        added += 1
    return {"retagged": retagged, "added": added}


def phrase_in(haystack: str, needle: str) -> bool:
    if len(needle) < 2:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])", haystack) is not None


def link_claims(entities: list[dict[str, Any]], claims: list[dict[str, Any]]) -> list[dict[str, str]]:
    links = []
    for claim in claims:
        haystack = norm((claim.get("quote") or "") + " " + (claim.get("text") or ""))
        for entity in entities:
            if phrase_in(haystack, entity["norm"]):
                links.append({"claim_id": claim["id"], "entity_id": entity["id"], "kind": "about"})
    return links


def load_api_key(root: Path) -> str:
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if key:
        return key
    env_path = root / ".env"
    if env_path.is_file():
        for line in env_path.read_text(errors="ignore").splitlines():
            if line.startswith("TYPESAFE_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def group_selected(selected: list[Occurrence]) -> list[list[Occurrence]]:
    by_span: dict[int, list[Occurrence]] = defaultdict(list)
    for item in selected:
        by_span[item.span_index].append(item)
    batches: list[list[Occurrence]] = []
    for span_index in sorted(by_span):
        items = by_span[span_index]
        # One Choice has no hard cap here. Eight candidates is sixteen questions.
        for offset in range(0, len(items), 8):
            batches.append(items[offset : offset + 8])
    return batches


def _trim_project_occurrences(occurrences: list[Occurrence]) -> list[Occurrence]:
    """Drop a shorter piece, and a known project name with extra trailing words."""
    phrases = {norm(phrase) for phrase in PROJECT_PHRASES} | set(PROJECT_ACRONYMS)
    by_span: dict[int, list[Occurrence]] = defaultdict(list)
    for item in occurrences:
        by_span[item.span_index].append(item)
    kept: list[Occurrence] = []
    for items in by_span.values():
        norms = {item.norm for item in items}
        for item in items:
            if any(is_subphrase(item.norm, other) for other in norms):
                continue
            if any(item.norm.startswith(phrase + " ") for phrase in phrases):
                continue
            kept.append(item)
    return kept


def extract(
    video_id: str,
    spans: list[dict[str, Any]],
    client: JevClient,
    words: set[str] | None = None,
    speaker_notes: dict[str, str] | None = None,
    workers: int = 4,
    max_calls: int = 1000,
    claims: list[dict[str, Any]] | None = None,
    only_type: str | None = None,
) -> ExtractResult:
    if words is None:
        words = load_wordlist()
    occurrences = collect_occurrences(spans, words, speaker_notes)
    if only_type == "project":
        occurrences = [item for item in occurrences if is_project_surface(item.norm)]
        occurrences = _trim_project_occurrences(occurrences)
    selected = select_occurrences(occurrences, words)
    batches = group_selected(selected)
    if len(batches) > max_calls:
        raise JevError(
            f"{len(batches)} Jev calls exceed --max-calls {max_calls}. "
            "Raise the cap to judge every selected candidate."
        )

    from concurrent.futures import ThreadPoolExecutor

    judgments: list[Judgment] = []
    model = client.model
    errors: list[str] = []

    def _one(batch: list[Occurrence]) -> tuple[list[Judgment], str] | str:
        try:
            return judge_span(client, batch)
        except Exception as exc:  # noqa: BLE001 — one span must not abort the corpus
            return f"span {batch[0].span_index}: {exc}"

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for result in pool.map(_one, batches):
            done += 1
            if isinstance(result, str):
                errors.append(result)
            else:
                batch_judgments, model = result
                judgments.extend(batch_judgments)
            if done % 25 == 0 or done == len(batches):
                print(f"  judged {done}/{len(batches)} batches", flush=True)

    combined = suppress_fragments(judgments)
    accepted = [item for item in combined if item.decision == "accept"]
    review = [item for item in combined if item.decision == "review"]
    if only_type:
        accepted = [item for item in accepted if item.type_choice == only_type]
        review = [item for item in review if item.type_choice == only_type]
    entities = cluster_entities(accepted)
    # A stable name that passed, with only one accepted type, keeps every
    # occurrence Jev did not reject. A common-word unigram keeps judged accepts only.
    blocked = {
        (item.occurrence.norm, item.occurrence.span_index)
        for item in combined
        if item.decision in {"reject", "review"}
    }
    types_for_norm: dict[str, set[str]] = defaultdict(set)
    for entity in entities:
        types_for_norm[entity["norm"]].add(entity["type"])
    occurrences_by_key: dict[str, list[Occurrence]] = defaultdict(list)
    for item in occurrences:
        occurrences_by_key[item.norm].append(item)
    for entity in entities:
        all_occurrences = occurrences_by_key.get(entity["norm"], [])
        entity["occurrence_count"] = len(all_occurrences)
        if not _stable(entity["norm"], words) or len(types_for_norm[entity["norm"]]) != 1:
            continue
        seen = {(mention["span_index"], mention["surface"]) for mention in entity["mentions"]}
        type_name = entity["type"]
        extras = []
        for occurrence in all_occurrences:
            marker = (occurrence.span_index, occurrence.surface)
            if marker in seen or (occurrence.norm, occurrence.span_index) in blocked:
                continue
            seen.add(marker)
            extras.append(
                {
                    "span_index": occurrence.span_index,
                    "t_start": occurrence.t_start,
                    "t_end": occurrence.t_end,
                    "speaker_label": occurrence.speaker_label,
                    "quote": occurrence.quote,
                    "surface": occurrence.surface,
                    "is_entity": None,
                    "type_choice": type_name,
                    "type_confidence": None,
                    "copied_from_accept": True,
                }
            )
        entity["mentions"].extend(extras)
        entity["mentions"].sort(key=lambda mention: mention["t_start"])

    review_rows = [_mention(item) | {"decision": "review", "type_choice": item.type_choice} for item in review]
    links = link_claims(entities, claims or [])
    return ExtractResult(
        video_id=video_id,
        model=model,
        entities=entities,
        review=review_rows,
        claim_links=links,
        stats={
            "spans": len(spans),
            "candidate_occurrences": len(occurrences),
            "selected_occurrences": len(selected),
            "batches": len(batches),
            "errors": errors,
            "accepted_mentions": len(accepted),
            "review_mentions": len(review),
            "entities": len(entities),
            "input_tokens": client.input_tokens,
            "output_tokens": client.output_tokens,
            "requests": client.requests,
            "cache_hits": client.cache_hits,
            "gate": {
                "accept_noul": ACCEPT_NOUL,
                "review_noul": REVIEW_NOUL,
                "min_type_confidence": MIN_TYPE_CONFIDENCE,
            },
        },
    )


# Clause glue. A candidate that contains one of these is a sentence fragment.
GLUE = frozenset(
    """
    started sent falsified proved made called directly doesnt dont
    whos wouldnt knows whats hows isnt cant didnt said told says gonna
    gives
    """.split()
)

# Sponsor reads. They are not the account. A pitch quote is skipped when the
# entity also has a quote from the conversation.
PITCH_MARKERS = (
    "checkout",
    "first order",
    "% off",
    "percent off",
    "promo code",
    "use code",
    "sponsored",
    "zbiotics",
    "z-biotics",
    "illumina",
    "face mask",
    "ketone iq",
)


def quote_is_pitch(quote: str) -> bool:
    folded = quote.casefold()
    if any(marker in folded for marker in PITCH_MARKERS):
        return True
    return re.search(r"\b(?:[a-z]-){2,}[a-z]\b", folded) is not None


def _bare_tokens(name: str) -> list[str]:
    return [token.replace("'", "") for token in norm(name).split()]


def is_fragment_name(name: str) -> bool:
    tokens = norm(name).split()
    if not tokens:
        return True
    if tokens[-1].endswith("'s") or (len(tokens) == 1 and tokens[0].endswith("'s")):
        return True
    bare = _bare_tokens(name)
    if bare and bare[0] == "per":
        return True
    return any(token in GLUE for token in bare)


def drop_covered_fragments(entities: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Drop a same-type entity when every mention already sits inside a longer one.

    Triangle stays if a span says triangle without equilateral. Force Base
    drops when that span always says Langley Air Force Base.
    """
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        by_type[entity["type"]].append(entity)
    covered_ids: set[str] = set()
    for group in by_type.values():
        for left in group:
            left_norm = norm(left["name"])
            for right in group:
                right_norm = norm(right["name"])
                if left_norm == right_norm or not is_subphrase(left_norm, right_norm):
                    continue
                quotes = [norm(mention.get("quote") or "") for mention in left.get("mentions") or []]
                if quotes and all(right_norm in quote for quote in quotes):
                    covered_ids.add(left["id"])
                    break
    kept, covered = [], []
    for entity in entities:
        (covered if entity["id"] in covered_ids else kept).append(entity)
    return kept, covered


def polish_entities(entities: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Remove sentence fragments before the importance judgment."""
    kept, fragments = [], []
    for entity in entities:
        if is_fragment_name(entity["name"]):
            fragments.append(entity)
        else:
            kept.append(entity)
    kept, covered = drop_covered_fragments(kept)
    for entity in fragments:
        entity["drop_reason"] = "fragment"
    for entity in covered:
        entity["drop_reason"] = "covered"
    return kept, fragments + covered


def importance_passage(entity: dict[str, Any]) -> str:
    """Up to three distinct quotes, strongest entity judgment first."""
    mentions = entity.get("mentions") or []
    ranked = sorted(
        mentions,
        key=lambda mention: (-(float(mention.get("is_entity") or 0)), -(len(mention.get("quote") or ""))),
    )
    usable = [mention for mention in ranked if (mention.get("quote") or "").strip()]
    conversation = [mention for mention in usable if not quote_is_pitch(mention.get("quote") or "")]
    pool = conversation or usable
    chunks: list[str] = []
    seen: set[str] = set()
    total = 0
    for mention in pool:
        quote = (mention.get("quote") or "").strip()
        key = norm(quote)
        if not quote or key in seen:
            continue
        seen.add(key)
        chunks.append(quote)
        total += len(quote)
        if len(chunks) == 3 or total >= 1500:
            break
    return "\n".join(chunks)


def importance_questions(batch: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    questions: dict[str, dict[str, Any]] = {}
    for index, entity in enumerate(batch):
        questions[f"important_{index}"] = {
            "type": "noul",
            "instructions": {
                "candidate": entity["name"],
                "passage": importance_passage(entity),
                "question": "In `passage`, is `candidate` important to the account the speakers are giving?",
            },
            "criteria": {
                "true": "The speakers use it in the account. It is a person, group, place, object, craft, material, or date the investigation should keep.",
                "false": "An advertisement, a product pitch, a song, a joke, a sentence fragment, or a name with no role in the account.",
            },
        }
    return questions


def judge_importance(
    entities: list[dict[str, Any]],
    client: JevClient,
    workers: int = 4,
) -> list[dict[str, Any]]:
    """Ask Jev whether each surviving entity matters to the account. One score per entity."""
    if not entities:
        return []
    batches = [entities[offset : offset + 12] for offset in range(0, len(entities), 12)]
    scored: list[dict[str, Any] | None] = [None] * len(entities)

    def _one(pair: tuple[int, list[dict[str, Any]]]) -> tuple[int, list[float]]:
        start, batch = pair
        response = client.system_one(
            {"note": "Each question names its own passage and candidate."},
            importance_questions(batch),
        )
        answers = response.get("answers") or {}
        if not answers:
            raise JevError("Jev importance response had no answers")
        values = []
        for index in range(len(batch)):
            answer = answers.get(f"important_{index}") or {}
            if "noul" not in answer:
                raise JevError(f"Jev importance response missing noul for important_{index}")
            values.append(float(answer.get("noul") or 0.0))
        return start, values

    from concurrent.futures import ThreadPoolExecutor, as_completed

    pairs = list(enumerate_batches(batches))
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(_one, pair) for pair in pairs]
        for future in as_completed(futures):
            start, values = future.result()
            for offset, value in enumerate(values):
                entity = entities[start + offset]
                entity["important"] = round(value, 4)
                scored[start + offset] = entity
            done += 1
            print(f"importance {done}/{len(pairs)}", flush=True)
    missing = sum(1 for entity in scored if entity is None)
    if missing:
        raise JevError(f"importance pass left {missing} entities unscored")
    return [entity for entity in scored if entity is not None]


def enumerate_batches(batches: list[list[dict[str, Any]]]) -> list[tuple[int, list[dict[str, Any]]]]:
    offset = 0
    pairs = []
    for batch in batches:
        pairs.append((offset, batch))
        offset += len(batch)
    return pairs


def entity_review_row(entity: dict[str, Any]) -> dict[str, Any]:
    """Keep the judged quote when an accepted entity leaves the proposed set."""
    mentions = entity.get("mentions") or []
    best = max(mentions, key=lambda mention: float(mention.get("is_entity") or 0)) if mentions else {}
    return {
        "surface": entity.get("name"),
        "decision": "review",
        "reason": entity.get("drop_reason") or "review",
        "type_choice": entity.get("type"),
        "important": entity.get("important"),
        "occurrence_count": entity.get("occurrence_count"),
        "span_index": best.get("span_index"),
        "quote": best.get("quote"),
        "speaker_label": best.get("speaker_label"),
        "t_start": best.get("t_start"),
        "t_end": best.get("t_end"),
        "is_entity": best.get("is_entity"),
        "type_confidence": best.get("type_confidence"),
    }


def refined_payload(
    payload: dict[str, Any],
    kept: list[dict[str, Any]],
    dropped: list[dict[str, Any]],
    *,
    requests: int,
    cache_hits: int,
    input_tokens: int,
) -> dict[str, Any]:
    """Replace accepted entities with the ones that matter. Dropped rows stay in review."""
    review = list(payload.get("review") or [])
    review.extend(entity_review_row(entity) for entity in dropped)
    alive = {entity["id"] for entity in kept}
    links = [link for link in (payload.get("claim_links") or []) if link.get("entity_id") in alive]
    stats = dict(payload.get("stats") or {})
    stats["entities"] = len(kept)
    stats["refine"] = {
        "before": len(payload.get("entities") or []),
        "fragment": sum(1 for entity in dropped if entity.get("drop_reason") == "fragment"),
        "covered": sum(1 for entity in dropped if entity.get("drop_reason") == "covered"),
        "not_important": sum(1 for entity in dropped if entity.get("drop_reason") == "not_important"),
        "kept": len(kept),
        "important_noul": IMPORTANT_NOUL,
        "requests": requests,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
    }
    note = payload.get("note") or ""
    extra = " A second pass asked whether each entity matters to the account. Scores below the importance gate stay in review."
    if "second pass" not in note:
        note = note.rstrip() + extra
    cleaned = []
    for entity in kept:
        cleaned.append({key: value for key, value in entity.items() if key != "drop_reason"})
    return {
        **payload,
        "lifecycle": "proposed",
        "note": note,
        "entities": cleaned,
        "review": review,
        "claim_links": links,
        "stats": stats,
    }


def rebuild_case_from_refined(case: dict[str, Any], kept: list[dict[str, Any]]) -> dict[str, Any]:
    """Keep hand entities and the Jev entities that survived refine.

    Does not add entities, does not rewrite claim text, and does not delete
    persons, claims, or claim-to-claim links.
    """
    kept_keys = {(entity["type"], norm(entity["name"])): entity for entity in kept}
    hand: list[dict[str, Any]] = []
    kept_jev: list[dict[str, Any]] = []
    for item in case.get("entities") or []:
        if item.get("judged_by") != "jev":
            item["lifecycle"] = item.get("lifecycle") or "proposed"
            hand.append(item)
            continue
        match = kept_keys.get((item.get("type"), norm(item.get("name") or "")))
        if match is None:
            continue
        item["lifecycle"] = "proposed"
        if "important" in match:
            item["important"] = match["important"]
        kept_jev.append(item)
    case["entities"] = hand + kept_jev
    alive = {item["id"] for item in case["entities"]}
    for claim in case.get("claims") or []:
        claim["entity_ids"] = [entity_id for entity_id in (claim.get("entity_ids") or []) if entity_id in alive]
    return case


def result_payload(result: ExtractResult) -> dict[str, Any]:
    entities = []
    for entity in result.entities:
        row = dict(entity)
        row.pop("norm", None)
        entities.append(row)
    return {
        "video_id": result.video_id,
        "extractor": "jev-claim-entities",
        "model": result.model,
        "lifecycle": "proposed",
        "note": (
            "Each entity is proposed. The surface is copied from a processed span. "
            "Jev chose the type. Jev did not write the words. "
            "A named person is someone the words talk about. "
            "The speaker label is who spoke. Nothing here is a verified finding."
        ),
        "entities": entities,
        "review": result.review,
        "claim_links": result.claim_links,
        "stats": result.stats,
    }


def merge_into_case(case: dict[str, Any], result: ExtractResult) -> dict[str, Any]:
    """Add accepted entities to a case graph. Do not rewrite claim text.

    An existing entity with the same type and normalized name keeps its id.
    New about-links are added when the quote contains the surface.
    Old links stay.
    """
    existing = case.setdefault("entities", [])
    by_key = {(item.get("type"), norm(item.get("name") or "")): item for item in existing}
    max_number = 0
    for item in existing:
        match = re.fullmatch(r"ENT-(\d+)", str(item.get("id") or ""))
        if match:
            max_number = max(max_number, int(match.group(1)))
    id_map: dict[str, str] = {}
    for entity in result.entities:
        key = (entity["type"], entity["norm"])
        current = by_key.get(key)
        mentions = [{k: v for k, v in mention.items() if k != "copied_from_accept" or v} for mention in entity["mentions"]]
        if current is None:
            max_number += 1
            current = {
                "id": f"ENT-{max_number:03d}",
                "name": entity["name"],
                "type": entity["type"],
                "lifecycle": "proposed",
                "judged_by": "jev",
                "mentions": mentions,
            }
            existing.append(current)
            by_key[key] = current
        else:
            current["lifecycle"] = current.get("lifecycle") or "proposed"
            current["judged_by"] = "jev"
            current["mentions"] = mentions
        id_map[entity["id"]] = current["id"]

    linked: dict[str, list[str]] = defaultdict(list)
    for link in result.claim_links:
        target = id_map.get(link["entity_id"])
        if target:
            linked[link["claim_id"]].append(target)
    for claim in case.get("claims") or []:
        extra = linked.get(claim.get("id"), [])
        if not extra:
            continue
        claim["entity_ids"] = list(dict.fromkeys([*(claim.get("entity_ids") or []), *extra]))
    return case


def candidate_report(spans: list[dict[str, Any]], words: set[str] | None = None) -> dict[str, Any]:
    words = load_wordlist() if words is None else words
    occurrences = collect_occurrences(spans, words)
    selected = select_occurrences(occurrences, words)
    batches = group_selected(selected)
    norms = {item.norm for item in occurrences}
    return {
        "spans": len(spans),
        "candidate_occurrences": len(occurrences),
        "unique_norms": len(norms),
        "selected_occurrences": len(selected),
        "batches": len(batches),
        "probe_hits": {probe: probe in norms for probe in RECALL_PROBES},
        "sample": sorted(norms)[:80],
    }


def self_check() -> None:
    words = load_wordlist()
    fixture = (
        "My name is Dylan Borland, a former 1N1 geospatial intelligence "
        "specialist for the United States Air Force. During the summer of 2012, "
        "at approximately 0130, I saw an approximately 100 foot equilateral triangle "
        "take off from near the NASA hangar on the base. "
        "tim phillips himself said triangles are real. "
        "went to Arrow and the IG. Lockheed Martin. j wicks. "
        "Glenn Gaffney of the CIA."
    )
    found = {item.norm for item in find_candidates(fixture, words)}
    required = [
        "dylan borland",
        "1n1",
        "united states air force",
        "summer of 2012",
        "0130",
        "equilateral triangle",
        "nasa hangar",
        "tim phillips",
        "triangles",
        "arrow",
        "ig",
        "lockheed martin",
        "j wicks",
        "glenn gaffney",
        "cia",
    ]
    missing = [item for item in required if item not in found]
    if missing:
        raise SystemExit(f"self-check missing candidates: {missing}")

    if decide(0.91, "location", 0.8) != "accept":
        raise SystemExit("accept gate failed")
    if decide(0.91, "location", 0.2) != "review":
        raise SystemExit("low type confidence should review")
    if decide(0.2, "location", 0.9) != "reject":
        raise SystemExit("low noul should reject")
    if decide(0.95, "none", 0.9) != "reject":
        raise SystemExit("none should reject")
    if decide(0.91, "project", 0.8) != "accept":
        raise SystemExit("project type should accept")
    project_found = {item.norm for item in find_candidates(
        "He reported to the UAP task force during Project Blue Book.",
        words,
    )}
    if "uap task force" not in project_found or "project blue book" not in project_found:
        raise SystemExit(f"project phrases missing: {sorted(project_found)}")
    if not is_project_surface("project blue box") or is_project_surface("the project"):
        raise SystemExit("project surface gate failed")
    project_case = {
        "entities": [
            {"id": "ENT-010", "name": "blue book", "type": "organization", "mentions": [{"span_index": 1, "surface": "blue book"}]},
        ]
    }
    counts = apply_project_entities(
        project_case,
        [{
            "name": "blue book",
            "norm": "blue book",
            "type": "project",
            "mentions": [{"span_index": 2, "surface": "Blue Book"}],
        }],
    )
    if counts != {"retagged": 1, "added": 0} or project_case["entities"][0]["type"] != "project":
        raise SystemExit(f"project retag failed: {counts}")
    if len(project_case["entities"][0]["mentions"]) != 2:
        raise SystemExit("project mention was not kept")
    apply_project_entities(
        project_case,
        [{"name": "Kona Blue", "norm": "kona blue", "type": "project", "mentions": [{"span_index": 3, "surface": "Kona Blue"}]}],
    )
    added = project_case["entities"][-1]
    if added["id"] != "ENT-011" or added["type"] != "project":
        raise SystemExit(f"new project id failed: {added}")

    long = Judgment(
        Occurrence("nasa hangar", "NASA hangar", 1, 1, 2, "SPEAKER_09", "near the NASA hangar", "passage"),
        0.9,
        "location",
        0.8,
        {},
        "accept",
    )
    short = Judgment(
        Occurrence("nasa", "NASA", 1, 1, 2, "SPEAKER_09", "near the NASA hangar", "passage"),
        0.9,
        "organization",
        0.8,
        {},
        "accept",
    )
    fragment = Judgment(
        Occurrence("triangle", "triangle", 1, 1, 2, "SPEAKER_09", "equilateral triangle", "passage"),
        0.9,
        "uap_item",
        0.8,
        {},
        "accept",
    )
    parent = Judgment(
        Occurrence("equilateral triangle", "equilateral triangle", 1, 1, 2, "SPEAKER_09", "equilateral triangle", "passage"),
        0.9,
        "uap_item",
        0.8,
        {},
        "accept",
    )
    kept = [item.occurrence.norm for item in suppress_fragments([long, short, fragment, parent]) if item.decision == "accept"]
    if "nasa" not in kept or "nasa hangar" not in kept:
        raise SystemExit(f"different types must both stay: {kept}")
    if "triangle" in kept or "equilateral triangle" not in kept:
        raise SystemExit(f"same-type fragment must drop: {kept}")

    entities = cluster_entities([long])
    links = link_claims(entities, [{"id": "CLM-1", "quote": "near the NASA hangar", "text": "saw it"}])
    if not links or links[0]["kind"] != "about":
        raise SystemExit("claim link failed")

    if not is_fragment_name("Dylan's") or not is_fragment_name("ODNI started"):
        raise SystemExit("fragment names should drop")
    if not is_fragment_name("James Lukatzky's") or not is_fragment_name("per james lakatsky"):
        raise SystemExit("possessive and per-fragment should drop")
    if is_fragment_name("Dylan Borland") or is_fragment_name("memorandum for record") or is_fragment_name("Rubik's Cube"):
        raise SystemExit("real names are not fragments")
    pitch_passage = importance_passage({
        "name": "Jesse",
        "mentions": [
            {"quote": "15% off when you use Jesse at checkout.", "is_entity": 0.99},
            {"quote": "Think about that, Jesse.", "is_entity": 0.80},
        ],
    })
    if "checkout" in pitch_passage.casefold() or "Think about that, Jesse." not in pitch_passage:
        raise SystemExit(f"pitch quote leaked into the importance passage: {pitch_passage}")
    sample = [
        {"id": "short", "name": "Force Base", "type": "location", "mentions": [{"quote": "Langley Air Force Base"}]},
        {"id": "long", "name": "Langley Air Force Base", "type": "location", "mentions": [{"quote": "Langley Air Force Base"}]},
        {"id": "tri", "name": "triangle", "type": "uap_item", "mentions": [{"quote": "a triangle over the base"}]},
        {"id": "eq", "name": "equilateral triangle", "type": "uap_item", "mentions": [{"quote": "equilateral triangle"}]},
    ]
    polished, removed = polish_entities(sample)
    polished_names = {item["name"] for item in polished}
    if polished_names != {"Langley Air Force Base", "triangle", "equilateral triangle"}:
        raise SystemExit(f"polish kept the wrong names: {sorted(polished_names)}")
    reasons = {item["name"]: item.get("drop_reason") for item in removed}
    if reasons.get("Force Base") != "covered":
        raise SystemExit(f"covered reason missing: {reasons}")

    case = {
        "entities": [
            {"id": "ENT-009", "name": "MFR", "type": "object"},
            {"id": "ENT-100", "name": "CIA doesn't", "type": "organization", "judged_by": "jev"},
            {"id": "ENT-101", "name": "CIA", "type": "organization", "judged_by": "jev"},
        ],
        "claims": [{"id": "CLM-1", "text": "saw it", "quote": "saw it", "entity_ids": ["ENT-009", "ENT-100", "ENT-101"]}],
        "persons": [{"id": "PER-1", "name": "Dylan Borland"}],
        "links": [{"source": "CLM-04", "target": "CLM-02", "kind": "elaborates"}],
    }
    rebuild_case_from_refined(case, [{"name": "CIA", "type": "organization", "important": 0.91}])
    ids = [item["id"] for item in case["entities"]]
    if ids != ["ENT-009", "ENT-101"]:
        raise SystemExit(f"case rebuild ids: {ids}")
    if case["claims"][0]["entity_ids"] != ["ENT-009", "ENT-101"] or case["claims"][0]["text"] != "saw it":
        raise SystemExit("claim text or entity ids changed")
    if case["persons"][0]["name"] != "Dylan Borland" or case["links"][0]["kind"] != "elaborates":
        raise SystemExit("rebuild touched persons or claim links")
    if case["entities"][0]["lifecycle"] != "proposed":
        raise SystemExit("hand entity should stay proposed")
    if case["entities"][1].get("important") != 0.91:
        raise SystemExit("kept entity lost its importance score")
    print("self-check ok", len(found), "fixture candidates")
