"""Transcript sentence extraction and claim context matching."""
from __future__ import annotations

import re
from typing import Any

# Sentence abbreviation filter
_ABBR_RE = re.compile(r"^(mr|mrs|ms|dr|gen|lt|col|sgt|vs|etc|approx|no)\.$", re.I)
_WORD_RE = re.compile(r"\b\w{3,}\b")


def extract_sentences(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Segment a stream of transcript spans into sentences with timing."""
    tokens: list[tuple[str, float, float, Any]] = []
    for s in spans:
        txt = (s.get("text") or "").strip()
        if not txt:
            continue
        words = txt.split()
        if not words:
            continue
        t0 = float(s.get("t_start") or 0)
        t1 = float(s.get("t_end") or 0)
        dur = max(t1 - t0, 0.01)
        for idx, w in enumerate(words):
            wt0 = t0 + (idx / len(words)) * dur
            wt1 = t0 + ((idx + 1) / len(words)) * dur
            tokens.append((w, wt0, wt1, s.get("speaker_label")))

    sentences: list[dict[str, Any]] = []
    cur: list[tuple[str, float, float, Any]] = []

    for tok in tokens:
        cur.append(tok)
        w = tok[0]
        if re.search(r"[.!?]$", w) and not _ABBR_RE.search(w):
            sentences.append({
                "text": " ".join(t[0] for t in cur),
                "t_start": cur[0][1],
                "t_end": cur[-1][2],
                "speaker": cur[0][3],
            })
            cur = []

    if cur:
        sentences.append({
            "text": " ".join(t[0] for t in cur),
            "t_start": cur[0][1],
            "t_end": cur[-1][2],
            "speaker": cur[0][3],
        })

    return sentences


def find_claim_context(
    sentences: list[dict[str, Any]],
    t_start: float | None = None,
    quote: str = "",
    claim_text: str = "",
) -> dict[str, Any]:
    """Find claim sentence, previous sentence, and after sentence from sentences."""
    if not sentences:
        fallback = quote or claim_text or ""
        return {
            "prev": "",
            "sentence": fallback,
            "after": "",
            "t_start": t_start or 0.0,
            "t_end": t_start or 0.0,
            "speaker": None,
        }

    q_words = set(_WORD_RE.findall((quote or "").lower()))
    c_words = set(_WORD_RE.findall((claim_text or "").lower()))
    target_words = q_words or c_words

    best_idx = -1
    best_score = -1.0

    for i, s in enumerate(sentences):
        stext = s["text"].lower()
        score = 0.0
        s_words = set(_WORD_RE.findall(stext))

        if target_words:
            overlap = len(target_words & s_words)
            if overlap > 0:
                score += overlap * 15.0

        if t_start is not None:
            st0 = s["t_start"]
            st1 = s["t_end"]
            if st0 <= t_start <= st1:
                score += 50.0
            elif abs(st0 - t_start) < 4.0:
                score += 30.0
            elif abs(st0 - t_start) < 15.0:
                score += 15.0
            elif abs(st0 - t_start) < 60.0:
                score += 5.0

        if score > best_score:
            best_score = score
            best_idx = i

    if best_idx == -1 and t_start is not None:
        best_idx = min(range(len(sentences)), key=lambda i: abs(sentences[i]["t_start"] - t_start))

    if best_idx == -1:
        best_idx = 0

    prev_sent = sentences[best_idx - 1]["text"] if best_idx > 0 else ""
    curr_sent = sentences[best_idx]["text"]
    next_sent = sentences[best_idx + 1]["text"] if best_idx + 1 < len(sentences) else ""

    return {
        "prev": prev_sent,
        "sentence": curr_sent,
        "after": next_sent,
        "t_start": sentences[best_idx]["t_start"],
        "t_end": sentences[best_idx]["t_end"],
        "speaker": sentences[best_idx].get("speaker"),
    }
