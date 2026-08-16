"""JSON-backed navigator store. Mutations persist under data/ui_store.json."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import Lock

from .seed import PILOT_VIDEOS, SEED

ROOT = Path(__file__).resolve().parents[3]
STORE_PATH = ROOT / "data" / "ui_store.json"
TRANSCRIPTS = ROOT / "data" / "transcripts"
AUDIO = ROOT / "data" / "audio"
_lock = Lock()


def _disk_asr(video_id: str) -> tuple[str, str]:
    """Return (asr, extraction) from local files."""
    has_spans = (TRANSCRIPTS / f"{video_id}.spans.json").is_file()
    has_wav = (AUDIO / f"{video_id}.wav").is_file()
    if has_spans:
        return "complete", "partial" if video_id == "uVVqFg2v7ro" else "pending"
    if has_wav:
        return "audio_ready", "pending"
    return "queued", "pending"


def _enrich(video: dict) -> dict:
    asr, extraction = _disk_asr(video["id"])
    video = dict(video)
    video["asr"] = asr
    video["extraction"] = extraction
    return video


def _merge_catalog(data: dict) -> dict:
    """Ensure every pilot video is in the catalog; keep extra ingest rows."""
    by_id = {v["id"]: v for v in data.get("videos") or []}
    merged = []
    seen = set()
    for canon in PILOT_VIDEOS:
        existing = by_id.get(canon["id"], {})
        row = {**canon, **{k: existing[k] for k in existing if k not in {"title", "channel", "handle", "cluster", "pilot"}}}
        row = _enrich({**canon, **row})
        # preserve curator-set title/channel if they registered a stub that we now know
        if existing.get("title") and existing["title"] not in {"Untitled ingest", f"Ingest {canon['id']}"}:
            if existing.get("channel") and existing["channel"] != "Unassigned":
                row["title"] = existing.get("title") or row["title"]
        merged.append(row)
        seen.add(canon["id"])
    for extra in data.get("videos") or []:
        if extra["id"] not in seen:
            extra = _enrich({**_v_fallback(extra), **extra})
            merged.append(extra)
    data["videos"] = merged
    return data


def _v_fallback(v: dict) -> dict:
    return {
        "id": v["id"],
        "channel": v.get("channel") or "Unknown",
        "handle": v.get("handle") or "",
        "title": v.get("title") or v["id"],
        "cluster": v.get("cluster") or "extra",
        "pilot": v.get("pilot") or "",
        "published": v.get("published") or "",
        "duration_s": v.get("duration_s") or 0,
        "asr": "queued",
        "extraction": "pending",
    }


def _default() -> dict:
    return _merge_catalog(deepcopy(SEED))


def load() -> dict:
    with _lock:
        if STORE_PATH.is_file():
            data = json.loads(STORE_PATH.read_text())
        else:
            data = deepcopy(SEED)
        data = _merge_catalog(data)
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text(json.dumps(data, indent=2) + "\n")
        return data


def save(data: dict) -> None:
    with _lock:
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text(json.dumps(data, indent=2) + "\n")


def spans_for_video(video_id: str) -> list[dict]:
    path = TRANSCRIPTS / f"{video_id}.spans.json"
    if not path.is_file():
        return []
    payload = json.loads(path.read_text())
    return payload.get("spans") or []


def reset() -> dict:
    data = _default()
    save(data)
    return data
