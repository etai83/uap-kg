"""JSON-backed navigator store. Mutations persist under data/ui_store.json."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import Lock

from .seed import SEED

ROOT = Path(__file__).resolve().parents[3]
STORE_PATH = ROOT / "data" / "ui_store.json"
TRANSCRIPTS = ROOT / "data" / "transcripts"
_lock = Lock()


def _default() -> dict:
    return deepcopy(SEED)


def load() -> dict:
    with _lock:
        if STORE_PATH.is_file():
            return json.loads(STORE_PATH.read_text())
        data = _default()
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
