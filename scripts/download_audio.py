#!/usr/bin/env python3
"""CLI: yt-dlp bestaudio → 16 kHz mono WAV.

Examples:
  .venv/bin/python scripts/download_audio.py https://youtu.be/uVVqFg2v7ro
  .venv/bin/python scripts/download_audio.py fZyKcJQZrDA --section "*0:00-1:00"
  .venv/bin/python scripts/download_audio.py --slice-c2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.speech.download import download_audio  # noqa: E402

# C2 vertical slice from docs/plans/v1-vertical-slice.md
C2_IDS = [
    "fZyKcJQZrDA",  # Area52 Lazar DEBRIEFED 83
    "SSeJ2883nF4",  # Area52 Lazar secret
    "d9tdJ2SkBKQ",  # Jesse weekend Lazar
    "5hhKLqUbrYQ",  # Danny TD Barnes
]


def main() -> int:
    p = argparse.ArgumentParser(description="Download YouTube bestaudio → 16kHz mono WAV")
    p.add_argument("targets", nargs="*", help="YouTube URL or video id")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "audio")
    p.add_argument("--section", default=None, help='e.g. "*0:00-0:45" for smoke tests')
    p.add_argument(
        "--cookies-from-browser",
        default="chrome",
        help="Browser for yt-dlp cookies (empty string to disable)",
    )
    p.add_argument("--slice-c2", action="store_true", help="Download C2 vertical-slice videos")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    targets = list(args.targets)
    if args.slice_c2:
        targets.extend(C2_IDS)
    if not targets:
        p.error("Provide video URL/id or --slice-c2")

    cookies = args.cookies_from_browser or None
    for t in targets:
        print(f"==> {t}")
        r = download_audio(
            t,
            args.out,
            cookies_from_browser=cookies,
            section=args.section,
            force=args.force,
        )
        print(
            f"    id={r.video_id} wav={r.audio_wav} "
            f"duration_s={r.duration_s} raw={r.audio_raw}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
