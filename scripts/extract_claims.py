#!/usr/bin/env python3
"""Extract proposed atomic claims from a diarized spans JSON.

Uses local Ollama (ANTHROPIC_BASE_URL / OLLAMA_HOST). Claims are written
into data/ui_store.json as lifecycle=proposed — never live.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.web import store  # noqa: E402

OLLAMA = os.environ.get("OLLAMA_HOST") or os.environ.get("ANTHROPIC_BASE_URL") or "http://localhost:11434"
MODEL = os.environ.get("UAP_EXTRACT_MODEL") or "gemma4:e4b"

# Episode-local SPEAKER_n → Person. Filled after diarization; unknown labels stay None.
PERSON_MAP: dict[str, dict[str, str]] = {
    "uVVqFg2v7ro": {"SPEAKER_11": "Jesse Michels", "SPEAKER_09": "Max"},
    "yGtVzBbUvx4": {"SPEAKER_01": "Jesse Michels", "SPEAKER_00": "Matthew Brown"},
    "1sxmSMzqnmA": {"SPEAKER_00": "Lyn Buchanan", "SPEAKER_01": "Jesse Michels"},
    "SSeJ2883nF4": {"SPEAKER_00": "Bob Lazar", "SPEAKER_01": "Chris Ramsay"},
    "fZyKcJQZrDA": {"SPEAKER_01": "Bob Lazar", "SPEAKER_00": "Chris Ramsay"},
    "5hhKLqUbrYQ": {"SPEAKER_01": "TD Barnes", "SPEAKER_00": "Danny Jones"},
    "d9tdJ2SkBKQ": {"SPEAKER_00": "Bob Lazar", "SPEAKER_01": "Jesse Michels"},
}

SYSTEM = """You extract atomic claims from a diarized YouTube interview transcript.

A claim is ONE checkable assertion a speaker actually made. Not a question.
Not your inference. Not a greeting or backchannel.

Return ONLY a JSON array. Each object:
{
  "claim_text": "short declarative proposition (speaker's assertion, not a quote dump)",
  "quote": "short supporting quote from the transcript",
  "t_start": 12.4,
  "speaker_label": "SPEAKER_09",
  "kind": "world_assertion" | "meta_speech" | "self_report",
  "person_guess": "name if clearly identified, else empty"
}

Rules:
- One proposition per object. Split compounds.
- Attribute to the speaker who uttered the words (use speaker_label from the line).
- Host restating a guest is a host claim (meta_speech), not the guest's.
- Skip questions, ums, and empty chatter.
- Prefer 8-20 high-signal claims per chunk, not every sentence.
- t_start must match a line timestamp in the chunk.
"""


def ollama_chat(prompt: str) -> str:
    url = OLLAMA.rstrip("/") + "/api/chat"
    body = json.dumps(
        {
            "model": MODEL,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_predict": 2500},
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode())
    msg = data.get("message") or {}
    return (msg.get("content") or msg.get("thinking") or "").strip()


def parse_claims(raw: str) -> list[dict]:
    raw = raw.strip()
    if not raw:
        return []
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw)
    def _loads(text: str):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\[[\s\S]*", text)
            if not m:
                raise
            frag = m.group(0)
            # salvage a truncated array by dropping the last incomplete object
            if not frag.rstrip().endswith("]"):
                last = frag.rfind("},")
                if last != -1:
                    frag = frag[: last + 1] + "]"
                else:
                    frag = frag.rstrip().rstrip(",") + "]"
            return json.loads(frag)

    try:
        obj = _loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(obj, dict):
        for key in ("claims", "items", "data", "results"):
            if isinstance(obj.get(key), list):
                obj = obj[key]
                break
        else:
            if obj.get("claim_text"):
                obj = [obj]
            else:
                obj = []
    if not isinstance(obj, list):
        return []
    out = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        text = (item.get("claim_text") or "").strip()
        if not text or len(text) < 12:
            continue
        out.append(item)
    return out


def chunk_spans(spans: list[dict], size: int = 70) -> list[list[dict]]:
    return [spans[i : i + size] for i in range(0, len(spans), size)]


def format_chunk(spans: list[dict]) -> str:
    lines = []
    for s in spans:
        t = float(s.get("t_start") or 0)
        h, rem = divmod(int(t), 3600)
        m, sec = divmod(rem, 60)
        ts = f"{h:02d}:{m:02d}:{sec:02d}"
        spk = s.get("speaker_label") or "UNKNOWN"
        text = (s.get("text") or "").replace("\n", " ").strip()
        if text:
            lines.append(f"[{ts} t={t:.1f}] {spk}: {text}")
    return "\n".join(lines)


def main() -> int:
    video_id = sys.argv[1] if len(sys.argv) > 1 else "uVVqFg2v7ro"
    path = ROOT / "data" / "transcripts" / f"{video_id}.spans.json"
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    payload = json.loads(path.read_text())
    spans = payload.get("spans") or []
    chunks = chunk_spans(spans, 70)
    print(f"video={video_id} spans={len(spans)} chunks={len(chunks)} model={MODEL}")

    extracted: list[dict] = []
    for i, chunk in enumerate(chunks, 1):
        prompt = (
            f"Video {video_id}. Extract atomic claims from this chunk ({i}/{len(chunks)}).\n\n"
            + format_chunk(chunk)
        )
        print(f"  chunk {i}/{len(chunks)} ...", flush=True)
        try:
            raw = ollama_chat(prompt)
            claims = parse_claims(raw)
        except Exception as exc:
            print(f"    FAIL {exc}")
            continue
        print(f"    -> {len(claims)} claims")
        if not claims and raw:
            print(f"    raw[:180]={raw[:180]!r}")
        extracted.extend(claims)
        persist(video_id, extracted)

    print(f"wrote {len(extracted)} proposed claims for {video_id}")
    return 0


def persist(video_id: str, extracted: list[dict]) -> None:
    data = store.load()
    existing = [
        c
        for c in data["claims"]
        if c.get("video_id") != video_id or not str(c.get("id", "")).startswith(f"C-{video_id}-")
    ]
    new_rows = []
    for n, item in enumerate(extracted, 1):
        try:
            t0 = float(item.get("t_start") or 0)
        except (TypeError, ValueError):
            t0 = 0.0
        kind = item.get("kind") if item.get("kind") in {"world_assertion", "meta_speech", "self_report"} else "world_assertion"
        speaker = item.get("speaker_label") or "UNKNOWN"
        person = (item.get("person_guess") or "").strip() or None
        if not person:
            person = PERSON_MAP.get(video_id, {}).get(speaker)
        new_rows.append(
            {
                "id": f"C-{video_id}-{n:03d}",
                "event_id": None,
                "video_id": video_id,
                "claim_text": item["claim_text"].strip()[:400],
                "body": (item.get("quote") or item["claim_text"]).strip()[:600],
                "quote": (item.get("quote") or "")[:400],
                "t_start": t0,
                "t_end": t0 + 8,
                "speaker_label": speaker,
                "person": person,
                "lifecycle": "proposed",
                "kind": kind,
                "layer": "claim",
            }
        )
    data["claims"] = existing + new_rows
    for v in data["videos"]:
        if v["id"] == video_id:
            v["extraction"] = "proposed"
            v["asr"] = "complete"
    store.save(data)


if __name__ == "__main__":
    raise SystemExit(main())
