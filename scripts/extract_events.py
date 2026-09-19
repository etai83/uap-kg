#!/usr/bin/env python3
"""Propose Event nodes from a diarized spans JSON.

Events are real-world happenings (not video beats). Written into
data/ui_store.json as status=provisional — never auto-live / auto-merged.
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

SYSTEM = """You extract Event candidates from a diarized YouTube interview.

An Event is a REAL-WORLD happening (or coherent multi-day incident) that speakers refer to.
It is NOT a video chapter, ad, greeting, or thematic topic.

Return ONLY a JSON array. Each object:
{
  "name": "short public case label (do not invent branding)",
  "when": "YYYY or YYYY.MM or YYYY.MM.DD or empty",
  "place": "place / theater or empty",
  "actors": ["principal participants in the happening, not the podcast host unless they were there"],
  "topics": ["2-5 short topic tags"],
  "blurb": "1-2 sentences: what is alleged to have happened",
  "match_existing_id": "existing Event id if this is clearly the same happening, else empty",
  "t_start": 12.4,
  "quote": "short supporting quote"
}

Rules:
- Prefer 1-6 Events per chunk. Skip chatter, ads, and pure opinion.
- Topics (hybrids, disclosure, NHI) are NOT Events unless tied to a dated/placed incident.
- If speakers retell a well-known case (Nimitz, Grusch hearing, Immaculate Constellation leak), use that case as the Event.
- t_start must match a line timestamp in the chunk.
"""


def ollama_chat(prompt: str) -> str:
    url = OLLAMA.rstrip("/") + "/api/chat"
    body = json.dumps(
        {
            "model": MODEL,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_predict": 1800},
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


def parse_json_list(raw: str) -> list[dict]:
    raw = (raw or "").strip()
    if not raw:
        return []
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[[\s\S]*", raw)
        if not m:
            return []
        frag = m.group(0)
        if not frag.rstrip().endswith("]"):
            last = frag.rfind("},")
            frag = frag[: last + 1] + "]" if last != -1 else frag.rstrip().rstrip(",") + "]"
        try:
            obj = json.loads(frag)
        except json.JSONDecodeError:
            return []
    if isinstance(obj, dict):
        for key in ("events", "items", "data", "results"):
            if isinstance(obj.get(key), list):
                obj = obj[key]
                break
        else:
            obj = [obj] if obj.get("name") else []
    if not isinstance(obj, list):
        return []
    out = []
    for item in obj:
        if isinstance(item, dict) and (item.get("name") or "").strip():
            out.append(item)
    return out


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


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def merge_candidates(items: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for item in items:
        name = (item.get("name") or "").strip()
        key = (_norm(name), _norm(item.get("when") or ""), _norm(item.get("place") or ""))
        hit = None
        for row in merged:
            rkey = (_norm(row["name"]), _norm(row.get("when") or ""), _norm(row.get("place") or ""))
            if key[0] and (key[0] == rkey[0] or key[0] in rkey[0] or rkey[0] in key[0]):
                if not key[1] or not rkey[1] or key[1][:4] == rkey[1][:4]:
                    hit = row
                    break
        if hit:
            for a in item.get("actors") or []:
                if a and a not in hit["actors"]:
                    hit["actors"].append(a)
            for t in item.get("topics") or []:
                if t and t not in hit["topics"]:
                    hit["topics"].append(t)
            if item.get("blurb") and len(item["blurb"]) > len(hit.get("blurb") or ""):
                hit["blurb"] = item["blurb"]
            if item.get("match_existing_id") and not hit.get("match_existing_id"):
                hit["match_existing_id"] = item["match_existing_id"]
            continue
        actors = [a for a in (item.get("actors") or []) if isinstance(a, str) and a.strip()]
        topics = [t for t in (item.get("topics") or []) if isinstance(t, str) and t.strip()]
        merged.append(
            {
                "name": name[:160],
                "when": (item.get("when") or "").strip()[:32],
                "place": (item.get("place") or "").strip()[:120],
                "actors": actors[:8],
                "topics": topics[:6],
                "blurb": (item.get("blurb") or name).strip()[:500],
                "match_existing_id": (item.get("match_existing_id") or "").strip(),
                "t_start": item.get("t_start"),
                "quote": (item.get("quote") or "")[:300],
            }
        )
    return merged


def next_event_id(existing: list[dict], video_id: str) -> str:
    n = 1
    ids = {e.get("id") for e in existing}
    while True:
        cand = f"EVT-P-{video_id}-{n:02d}"
        if cand not in ids:
            return cand
        n += 1


def persist(video_id: str, candidates: list[dict]) -> list[dict]:
    data = store.load()
    existing = data.get("events") or []
    by_id = {e["id"]: e for e in existing}
    written = []
    for item in candidates:
        match_id = item.get("match_existing_id")
        if match_id and match_id in by_id:
            ev = by_id[match_id]
            vids = ev.setdefault("telling_video_ids", [])
            if video_id not in vids:
                vids.append(video_id)
            written.append(ev)
            continue
        # reuse same proposed name+video
        reuse = next(
            (
                e
                for e in existing
                if video_id in (e.get("telling_video_ids") or [])
                and _norm(e.get("name") or "") == _norm(item["name"])
            ),
            None,
        )
        if reuse:
            written.append(reuse)
            continue
        eid = next_event_id(existing, video_id)
        row = {
            "id": eid,
            "name": item["name"],
            "when": item.get("when") or "",
            "place": item.get("place") or "",
            "actors": item.get("actors") or [],
            "topics": item.get("topics") or [],
            "blurb": item.get("blurb") or item["name"],
            "status": "provisional",
            "lifecycle": "proposed",
            "telling_video_ids": [video_id],
        }
        existing.append(row)
        by_id[eid] = row
        written.append(row)
    data["events"] = existing
    store.save(data)
    return written


def main() -> int:
    video_id = sys.argv[1] if len(sys.argv) > 1 else "yGtVzBbUvx4"
    path = ROOT / "data" / "transcripts" / f"{video_id}.spans.json"
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    payload = json.loads(path.read_text())
    spans = payload.get("spans") or []
    catalog = store.load()
    existing_brief = [
        {
            "id": e["id"],
            "name": e.get("name"),
            "when": e.get("when"),
            "place": e.get("place"),
            "actors": e.get("actors"),
        }
        for e in catalog.get("events") or []
    ]
    # coarse chunks: ~3–4 minutes of speech per window
    size = 120
    chunks = [spans[i : i + size] for i in range(0, len(spans), size)]
    print(f"video={video_id} spans={len(spans)} chunks={len(chunks)} model={MODEL}")
    extracted: list[dict] = []
    catalog_txt = json.dumps(existing_brief, ensure_ascii=False)
    for i, chunk in enumerate(chunks, 1):
        prompt = (
            f"Video {video_id}. Existing Events (match if same happening):\n{catalog_txt}\n\n"
            f"Extract Event candidates from chunk {i}/{len(chunks)}.\n\n"
            + format_chunk(chunk)
        )
        print(f"  chunk {i}/{len(chunks)} ...", flush=True)
        try:
            raw = ollama_chat(prompt)
            items = parse_json_list(raw)
        except Exception as exc:
            print(f"    FAIL {exc}")
            continue
        print(f"    -> {len(items)} events")
        extracted.extend(items)
    merged = merge_candidates(extracted)
    written = persist(video_id, merged)
    print(f"wrote {len(written)} event rows ({len(merged)} unique candidates)")
    for e in written:
        print(f"  {e['id']}: {e.get('name')} [{e.get('when')}] {e.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
