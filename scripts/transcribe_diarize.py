#!/usr/bin/env python3
"""CLI: local ASR + pyannote diarization → proposed spans JSON.

Requires (install into .venv when ready):
  pip install faster-whisper pyannote.audio torch
  # or: pip install whisperx

Env:
  HF_TOKEN — Hugging Face token with pyannote model access accepted

Examples:
  .venv/bin/python scripts/transcribe_diarize.py data/audio/uVVqFg2v7ro.wav
  .venv/bin/python scripts/transcribe_diarize.py data/audio/smoke.wav --model tiny
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.speech.transcribe import transcribe_and_diarize  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Local ASR + diarization → proposed spans")
    p.add_argument("wav", type=Path, help="16 kHz mono WAV path")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON (default: data/transcripts/<stem>.spans.json)",
    )
    p.add_argument("--model", default="base", help="Whisper size: tiny/base/small/medium/large-v3")
    p.add_argument("--min-speakers", type=int, default=2)
    p.add_argument("--max-speakers", type=int, default=4)
    p.add_argument("--device", default=None, help="cpu or cuda")
    args = p.parse_args()

    out = args.out or (ROOT / "data" / "transcripts" / f"{args.wav.stem}.spans.json")
    spans = transcribe_and_diarize(
        args.wav,
        out,
        model_size=args.model,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        device=args.device,
    )
    print(f"wrote {out} ({len(spans)} spans)")
    for s in spans[:5]:
        print(f"  [{s['t_start']:.1f}-{s['t_end']:.1f}] {s['speaker_label']}: {s['text'][:80]}")
    if len(spans) > 5:
        print(f"  ... +{len(spans) - 5} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
