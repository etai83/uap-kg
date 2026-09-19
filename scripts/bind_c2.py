#!/usr/bin/env python3
"""Bind C2 slice claims to Events and Persons. Proposed-safe: does not flip lifecycle."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.web import store  # noqa: E402

C2 = {
    "fZyKcJQZrDA": {
        "host": "Chris Ramsay",
        "guest": "Bob Lazar",
        "event": "EVT-89-014",
        "map": {"SPEAKER_01": "Bob Lazar", "SPEAKER_00": "Chris Ramsay"},
    },
    "SSeJ2883nF4": {
        "host": "Chris Ramsay",
        "guest": "Bob Lazar",
        "event": "EVT-89-014",
        "map": {"SPEAKER_00": "Bob Lazar", "SPEAKER_01": "Chris Ramsay"},
    },
    "d9tdJ2SkBKQ": {
        "host": "Jesse Michels",
        "guest": "Bob Lazar",
        "event": "EVT-89-014",
        "map": {"SPEAKER_00": "Bob Lazar", "SPEAKER_01": "Jesse Michels"},
    },
    "5hhKLqUbrYQ": {
        "host": "Danny Jones",
        "guest": "TD Barnes",
        "event": "EVT-51-IND",
        "map": {"SPEAKER_01": "TD Barnes", "SPEAKER_00": "Danny Jones"},
    },
}

S4_KEYS = (
    "s4",
    "s-4",
    "sport model",
    "element 115",
    "element one fifteen",
    "moscovium",
    "papoose",
    "sector 4",
    "sector four",
    "nine saucer",
    "nine craft",
    "nine flying",
    "gravity amplifier",
    "reactor",
)
BARNES_KEYS = (
    "eg&g",
    "egg",
    "radar site",
    "area 51",
    "groom lake",
    "atomic energy",
    "oxcart",
    "u-2",
    "u2",
)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower())


def majority_speakers(video_id: str) -> tuple[str | None, str | None]:
    path = ROOT / "data" / "audio" / f"{video_id}_speakers.txt"
    if not path.is_file():
        return None, None
    head = path.read_text(errors="replace").splitlines()[:20]
    ranked = []
    for line in head:
        m = re.match(r"\s*(SPEAKER_\d+)\s+", line)
        if m:
            ranked.append(m.group(1))
    guest_label = ranked[0] if ranked else None
    host_label = ranked[1] if len(ranked) > 1 else None
    return guest_label, host_label


def ensure_barnes_event(data: dict) -> dict:
    existing = next((e for e in data["events"] if e["id"] == "EVT-51-IND"), None)
    if existing:
        return existing
    row = {
        "id": "EVT-51-IND",
        "name": "Area 51 industrial program (TD Barnes)",
        "when": "1960s–1970s",
        "place": "Groom Lake / Area 51",
        "actors": ["TD Barnes"],
        "topics": ["Area 51", "Radar", "EG&G"],
        "blurb": "Public claims of EG&G / radar-site work at Groom Lake. Sibling to Lazar S4 intake when keys conflict (industrial program vs S4 reverse-engineering).",
        "status": "provisional",
        "lifecycle": "proposed",
        "telling_video_ids": ["5hhKLqUbrYQ"],
    }
    data["events"].append(row)
    return row


def bind() -> None:
    data = store.load()
    ensure_barnes_event(data)
    maps: dict[str, dict[str, str]] = {}
    for vid, meta in C2.items():
        m = dict(meta.get("map") or {})
        if not m:
            guest_l, host_l = majority_speakers(vid)
            if guest_l:
                m[guest_l] = meta["guest"]
            if host_l:
                m[host_l] = meta["host"]
        maps[vid] = m
        print(f"map {vid}: {m}")

    s4 = next(e for e in data["events"] if e["id"] == "EVT-89-014")
    barnes = next(e for e in data["events"] if e["id"] == "EVT-51-IND")
    for vid, meta in C2.items():
        target = s4 if meta["event"] == "EVT-89-014" else barnes
        vids = target.setdefault("telling_video_ids", [])
        if vid not in vids:
            vids.append(vid)

    bound = 0
    personed = 0
    for c in data["claims"]:
        vid = c.get("video_id")
        if vid not in C2:
            continue
        spk = c.get("speaker_label")
        mapped = maps.get(vid, {}).get(spk)
        if mapped and c.get("person") != mapped:
            # don't overwrite a clearly different named person
            if not c.get("person") or c.get("person") in {C2[vid]["host"], C2[vid]["guest"], None}:
                c["person"] = mapped
                personed += 1
        blob = _norm(" ".join([c.get("claim_text") or "", c.get("quote") or "", c.get("body") or ""]))
        if vid == "5hhKLqUbrYQ":
            if any(k in blob for k in S4_KEYS):
                c["event_id"] = "EVT-89-014"
                bound += 1
            elif any(k in blob for k in BARNES_KEYS) or not c.get("event_id"):
                c["event_id"] = "EVT-51-IND"
                bound += 1
        else:
            if any(k in blob for k in S4_KEYS) or not c.get("event_id"):
                c["event_id"] = "EVT-89-014"
                bound += 1

    store.save(data)
    print(f"personed={personed} bound={bound}")


if __name__ == "__main__":
    bind()
