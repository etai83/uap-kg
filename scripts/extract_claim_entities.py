#!/usr/bin/env python3
"""Propose claim entities from a diarized spans file, using Jev for the judgments.

Code finds candidate phrases and copies them from the spans. Jev decides
whether each candidate is an entity and which type it is. Jev does not write
the words. Accepted entities are proposed, not verified findings.

--refine reads an existing entity file. It drops sentence fragments, asks Jev
which remaining entities matter, and rebuilds the case from that set. It does
not extract again and it does not merge a second time.

--projects judges project names and writes that type into the entity file.
A matching name changes to project. A new name is appended. Other entities stay.

Requires TYPESAFE_API_KEY in the environment or in .env at the repo root.
A candidates-only run does not call Jev.

Examples:
  python scripts/extract_claim_entities.py --self-check
  python scripts/extract_claim_entities.py K4gYHs84BIc --candidates-only
  python scripts/extract_claim_entities.py K4gYHs84BIc
  python scripts/extract_claim_entities.py K4gYHs84BIc --refine
  python scripts/extract_claim_entities.py K4gYHs84BIc --projects
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.extract.claim_entities import (  # noqa: E402
    IMPORTANT_NOUL,
    JevClient,
    JevError,
    apply_project_entities,
    candidate_report,
    extract,
    judge_importance,
    load_api_key,
    load_wordlist,
    merge_into_case,
    norm,
    polish_entities,
    rebuild_case_from_refined,
    refined_payload,
    result_payload,
    self_check,
)

DEFAULT_VIDEO = "K4gYHs84BIc"
SPAN_FALLBACK = Path("/Users/itaiharpaz/Code/uap-kg/data/transcripts")
BORLAND_CASE = ROOT / "src" / "uap_kg" / "web" / "data" / "borland_case.json"
CORE_PROBES = (
    "dylan borland",
    "jesse",
    "nasa hangar",
    "united states air force",
    "equilateral triangle",
    "langley",
    "arrow",
    "tim phillips",
    "george knapp",
    "lockheed martin",
    "glenn gaffney",
    "special access program",
    "memorandum for record",
    "congress",
    "cia",
    "white light",
    "2012",
    "0130",
    "j wicks",
)

# Episode-local notes. They tell Jev who a speaker label is. They do not
# turn a named person into the claimant.
SPEAKER_NOTES = {
    "K4gYHs84BIc": {
        "SPEAKER_09": "Dylan Borland, the guest. He is the claimant when this label speaks a claim.",
        "SPEAKER_10": "Jesse Michels, the host. A question is not a world claim.",
        "SPEAKER_04": "A recording played in the episode. Not Dylan Borland.",
        "SPEAKER_05": "A recording played in the episode. Not Dylan Borland.",
    }
}


def spans_path(video_id: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    local = ROOT / "data" / "transcripts" / f"{video_id}.spans.json"
    if local.is_file():
        return local
    fallback = SPAN_FALLBACK / f"{video_id}.spans.json"
    return fallback


def load_spans(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    spans = payload.get("spans") if isinstance(payload, dict) else payload
    if not isinstance(spans, list):
        raise SystemExit(f"{path} has no spans list")
    return spans


def probe_report(entities: list[dict]) -> list[str]:
    by_name: dict[str, list[dict]] = defaultdict(list)
    for entity in entities:
        by_name[norm(entity.get("name") or "")].append(entity)
    lines = []
    for probe in CORE_PROBES:
        rows = by_name.get(probe) or []
        if not rows:
            lines.append(f"probe {probe}: absent")
            continue
        for entity in rows:
            score = entity.get("important")
            reason = entity.get("drop_reason")
            if reason in {"fragment", "covered"}:
                state = reason
            elif not isinstance(score, (int, float)):
                state = "unscored"
            elif float(score) >= IMPORTANT_NOUL:
                state = "keep"
            else:
                state = "drop"
            score_text = f"{float(score):.3f}" if isinstance(score, (int, float)) else "-"
            lines.append(f"probe {probe}: {state} {score_text} {entity.get('type')}")
    return lines


def run_refine(args: argparse.Namespace, key: str) -> int:
    """Filter an existing extraction. Do not call extract or merge_into_case."""
    out = Path(args.out) if args.out else ROOT / "data" / "entities" / f"{args.video_id}.entities.json"
    if not out.is_file():
        print(f"missing {out}. Run the extractor once before --refine.", file=sys.stderr)
        return 1
    payload = json.loads(out.read_text())
    if "apikey_" in json.dumps(payload):
        print("refusing to refine a file that contains a key", file=sys.stderr)
        return 1

    cache_dir = ROOT / "data" / "jev_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    backup = cache_dir / f"{args.video_id}.entities.pre-refine.json"
    if not backup.exists():
        shutil.copy(out, backup)
    case_path = Path(args.case) if args.case else (BORLAND_CASE if args.video_id == DEFAULT_VIDEO else None)
    case_backup = cache_dir / f"{args.video_id}.case.pre-refine.json"
    if case_path and case_path.is_file() and not case_backup.exists():
        shutil.copy(case_path, case_backup)

    entities = [dict(entity) for entity in payload.get("entities") or []]
    polished, local_drops = polish_entities(entities)
    print(f"polish kept={len(polished)} dropped={len(local_drops)}", flush=True)
    client = JevClient(key, model=args.model, cache_path=cache_dir / f"{args.video_id}.claim_entities.jsonl")
    try:
        scored = judge_importance(polished, client, workers=args.workers)
    except JevError as exc:
        print(str(exc).replace(key, "[redacted]"), file=sys.stderr)
        return 1

    kept = []
    weak = []
    for entity in scored:
        if float(entity.get("important") or 0) >= IMPORTANT_NOUL:
            kept.append(entity)
        else:
            entity["drop_reason"] = "not_important"
            weak.append(entity)
    dropped = local_drops + weak
    for line in probe_report(kept + dropped):
        print(line)
    for entity in sorted(dropped, key=lambda item: (item.get("drop_reason") or "", norm(item.get("name") or ""))):
        score = entity.get("important")
        score_text = f"{float(score):.3f}" if isinstance(score, (int, float)) else "-"
        print(f"drop {entity.get('drop_reason')} {score_text} {entity.get('type')} {entity.get('name')}")
    print(
        f"kept={len(kept)} dropped={len(dropped)} requests={client.requests} "
        f"cache_hits={client.cache_hits} tokens={client.input_tokens}",
        flush=True,
    )

    refined = refined_payload(
        payload,
        kept,
        dropped,
        requests=client.requests,
        cache_hits=client.cache_hits,
        input_tokens=client.input_tokens,
    )
    encoded = json.dumps(refined)
    if "apikey_" in encoded:
        print("refusing to write output that contains a key", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(refined, indent=2) + "\n")
    print(f"wrote {out}")

    if case_path and case_path.is_file():
        case = json.loads(case_path.read_text())
        claims_before = json.dumps(case.get("claims"))
        persons_before = json.dumps(case.get("persons"))
        links_before = json.dumps(case.get("links"))
        rebuild_case_from_refined(case, kept)
        # Claim text, persons, and claim-claim links stay. Only entity_ids may shrink.
        def _without_ids(raw: str) -> str:
            rows = json.loads(raw)
            for row in rows:
                row.pop("entity_ids", None)
            return json.dumps(rows)

        if _without_ids(claims_before) != _without_ids(json.dumps(case.get("claims"))):
            print("refusing to write the case because claim text changed", file=sys.stderr)
            return 1
        if persons_before != json.dumps(case.get("persons")) or links_before != json.dumps(case.get("links")):
            print("refusing to write the case because persons or links changed", file=sys.stderr)
            return 1
        if "apikey_" in json.dumps(case):
            print("refusing to write a case that contains a key", file=sys.stderr)
            return 1
        case_path.write_text(json.dumps(case, indent=2) + "\n")
        print(f"rebuilt {case_path} entities={len(case['entities'])}")
    return 0


def run_projects(args: argparse.Namespace, key: str) -> int:
    """Judge project surfaces and merge them into the existing entity file."""
    path = spans_path(args.video_id, args.spans)
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else ROOT / "data" / "entities" / f"{args.video_id}.entities.json"
    if not out.is_file():
        print(f"missing {out}. Run the extractor once before --projects.", file=sys.stderr)
        return 1
    payload = json.loads(out.read_text())
    if "apikey_" in json.dumps(payload):
        print("refusing to update a file that contains a key", file=sys.stderr)
        return 1
    spans = load_spans(path)
    words = load_wordlist()
    cache_dir = ROOT / "data" / "jev_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    client = JevClient(key, model=args.model, cache_path=cache_dir / f"{args.video_id}.projects.jsonl")
    print(f"video={args.video_id} spans={len(spans)} model={args.model} projects", flush=True)
    try:
        result = extract(
            args.video_id,
            spans,
            client,
            words=words,
            speaker_notes=SPEAKER_NOTES.get(args.video_id),
            workers=args.workers,
            max_calls=args.max_calls,
            only_type="project",
        )
    except JevError as exc:
        print(str(exc).replace(key, "[redacted]"), file=sys.stderr)
        return 1
    counts = apply_project_entities(payload, result.entities)
    stats = payload.setdefault("stats", {})
    if not isinstance(stats, dict):
        stats = {}
        payload["stats"] = stats
    stats["project_pass"] = {
        "added": counts["added"],
        "retagged": counts["retagged"],
        "accepted": [entity.get("name") for entity in result.entities],
        "requests": client.requests,
        "cache_hits": client.cache_hits,
    }
    encoded = json.dumps(payload)
    if "apikey_" in encoded:
        print("refusing to write output that contains a key", file=sys.stderr)
        return 1
    out.write_text(json.dumps(payload, indent=2) + "\n")
    names = ", ".join(entity.get("name") or "" for entity in result.entities) or "none"
    print(
        f"accepted={len(result.entities)} added={counts['added']} retagged={counts['retagged']} "
        f"requests={client.requests} cache_hits={client.cache_hits}",
        flush=True,
    )
    print(f"projects: {names}")
    print(f"wrote {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract proposed entities from spans with Jev.")
    parser.add_argument("video_id", nargs="?", default=DEFAULT_VIDEO)
    parser.add_argument("--spans", help="Path to a *.spans.json file")
    parser.add_argument("--out", help="Where to write the entity JSON")
    parser.add_argument("--case", help="Case JSON to merge accepted entities into")
    parser.add_argument("--candidates-only", action="store_true", help="Find candidates and do not call Jev")
    parser.add_argument("--refine", action="store_true", help="Drop fragments, then ask Jev which entities matter")
    parser.add_argument("--projects", action="store_true", help="Judge project names and add that entity type")
    parser.add_argument("--self-check", action="store_true", help="Run local checks and exit")
    parser.add_argument("--model", default="jev-latest")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-calls", type=int, default=2000)
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return 0

    if args.refine and args.candidates_only or args.projects and (args.refine or args.candidates_only):
        print("Use only one of --refine, --candidates-only, or --projects.", file=sys.stderr)
        return 1

    if args.projects:
        key = load_api_key(ROOT)
        if not key:
            print("TYPESAFE_API_KEY is missing. Put it in the environment or in .env and retry.", file=sys.stderr)
            return 1
        return run_projects(args, key)

    if args.refine:
        key = load_api_key(ROOT)
        if not key:
            print("TYPESAFE_API_KEY is missing. Put it in the environment or in .env and retry.", file=sys.stderr)
            return 1
        return run_refine(args, key)

    path = spans_path(args.video_id, args.spans)
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    spans = load_spans(path)
    words = load_wordlist()

    if args.candidates_only:
        report = candidate_report(spans, words)
        print(f"video={args.video_id} spans={report['spans']} file={path}")
        print(
            f"occurrences={report['candidate_occurrences']} unique={report['unique_norms']} "
            f"selected={report['selected_occurrences']} batches={report['batches']}"
        )
        missed = [name for name, hit in report["probe_hits"].items() if not hit]
        print("probes missed:", ", ".join(missed) if missed else "none")
        print("sample:", ", ".join(report["sample"][:40]))
        return 0 if not missed else 2

    key = load_api_key(ROOT)
    if not key:
        print("TYPESAFE_API_KEY is missing. Put it in the environment or in .env and retry.", file=sys.stderr)
        return 1

    case_path = Path(args.case) if args.case else (BORLAND_CASE if args.video_id == DEFAULT_VIDEO else None)
    claims = None
    case = None
    if case_path and case_path.is_file():
        case = json.loads(case_path.read_text())
        claims = case.get("claims") or []

    out = Path(args.out) if args.out else ROOT / "data" / "entities" / f"{args.video_id}.entities.json"
    cache = ROOT / "data" / "jev_cache" / f"{args.video_id}.claim_entities.jsonl"
    client = JevClient(key, model=args.model, cache_path=cache)
    print(f"video={args.video_id} spans={len(spans)} model={args.model}", flush=True)
    try:
        result = extract(
            args.video_id,
            spans,
            client,
            words=words,
            speaker_notes=SPEAKER_NOTES.get(args.video_id),
            workers=args.workers,
            max_calls=args.max_calls,
            claims=claims,
        )
    except JevError as exc:
        print(exc, file=sys.stderr)
        return 1

    payload = result_payload(result)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"entities={payload['stats']['entities']} review={payload['stats']['review_mentions']} "
        f"requests={payload['stats']['requests']} cache_hits={payload['stats']['cache_hits']} "
        f"tokens={payload['stats']['input_tokens']}"
    )
    print(f"wrote {out}")
    if payload["stats"]["errors"]:
        print(f"span errors: {len(payload['stats']['errors'])}")
        for line in payload["stats"]["errors"][:8]:
            print(f"  {line}")

    if case is not None and case_path is not None:
        merge_into_case(case, result)
        case_path.write_text(json.dumps(case, indent=2) + "\n")
        print(f"merged entities into {case_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
