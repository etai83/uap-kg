#!/usr/bin/env python3
"""Non-interactive bridge to tools/audio_transcriber (MLX Whisper + pyannote).

Uses the vendored https://github.com/razamit/audio_transcriber tool.

Pipeline:
  1) Prefer existing WAV from scripts/download_audio.py
  2) Or pass any audio path ffmpeg can read
  3) English MLX Whisper (+ optional diarization)
  4) Write human .txt next to audio and machine spans JSON under data/transcripts/

Examples:
  tools/audio_transcriber/.venv/bin/python scripts/transcribe_audio_transcriber.py \\
      data/audio/uVVqFg2v7ro.wav --speakers --speakers-count 2

  # From YouTube id (downloads first via uap-kg yt-dlp helper):
  .venv/bin/python scripts/download_audio.py uVVqFg2v7ro --section "*0:00-0:30"
  tools/audio_transcriber/.venv/bin/python scripts/transcribe_audio_transcriber.py \\
      data/audio/uVVqFg2v7ro.wav --speakers
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AT_ROOT = ROOT / "tools" / "audio_transcriber"


def _ensure_import_path() -> None:
    if not AT_ROOT.is_dir():
        sys.exit(
            f"Missing {AT_ROOT}. Clone with:\n"
            "  git clone https://github.com/razamit/audio_transcriber tools/audio_transcriber\n"
            "  cd tools/audio_transcriber && ./setup.sh --with-diarization"
        )
    sys.path.insert(0, str(AT_ROOT))


def main() -> int:
    _ensure_import_path()

    # Imports after path inject (modules live in tools/audio_transcriber)
    import diarization
    from diarization import extract_speaker_turns, label_segments
    from paths import require_ffmpeg
    from profiles import PROFILES
    from transcript_output import (
        format_timestamp,
        write_labelled_transcript,
        write_transcript,
    )
    from transcription import announce_first_run_download, run_transcription

    p = argparse.ArgumentParser(description="Run audio_transcriber non-interactively")
    p.add_argument("audio", type=Path, help="Path to audio (wav/m4a/mp3/…)")
    p.add_argument(
        "--lang",
        default="en",
        choices=sorted(PROFILES.keys()),
        help="Language profile (default en for UAP pilot)",
    )
    p.add_argument("--speakers", action="store_true", help="Enable pyannote diarization")
    p.add_argument(
        "--speakers-count",
        type=int,
        default=None,
        help="Fixed speaker count (omit for auto-detect)",
    )
    p.add_argument(
        "--out-txt",
        type=Path,
        default=None,
        help="Transcript .txt path (default next to audio)",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Machine spans JSON (default data/transcripts/<stem>.spans.json)",
    )
    args = p.parse_args()

    audio_path = args.audio.expanduser().resolve()
    if not audio_path.is_file():
        sys.exit(f"Audio not found: {audio_path}")

    require_ffmpeg()
    profile = PROFILES[args.lang]

    if args.speakers and not diarization.diarization_is_available():
        sys.exit(diarization.INSTALL_HELP)

    stem = audio_path.stem
    out_txt = args.out_txt or audio_path.with_name(
        f"{stem}_speakers.txt" if args.speakers else f"{stem}.txt"
    )
    out_json = args.out_json or (ROOT / "data" / "transcripts" / f"{stem}.spans.json")

    announce_first_run_download(profile)
    started = time.monotonic()

    if args.speakers:
        print("Loading diarization pipeline ...")
        pipeline = diarization.load_diarization_pipeline(diarization.optional_hf_token())
        print("Detecting speaker turns ...")
        turns = extract_speaker_turns(pipeline, str(audio_path), args.speakers_count)
        print(f"  {len(turns)} turn(s) found.")
        print(f"Transcribing as {profile.label} ...")
        result = run_transcription(str(audio_path), profile)
        labelled = label_segments(result.get("segments") or [], turns)
        if not labelled:
            sys.exit("No speech transcribed.")
        write_labelled_transcript(str(out_txt), labelled)
        spans = [
            {
                "t_start": float(e["start"]),
                "t_end": float(e["end"]),
                "text": (e.get("text") or "").strip(),
                "speaker_label": e.get("speaker") or "UNKNOWN",
                "layer": "processed",
                "lifecycle": "proposed",
            }
            for e in labelled
            if (e.get("text") or "").strip()
        ]
    else:
        print(f"Transcribing as {profile.label} (no diarization) ...")
        result = run_transcription(str(audio_path), profile)
        segments = result.get("segments") or []
        write_transcript(str(out_txt), segments, result.get("text"))
        spans = [
            {
                "t_start": float(s.get("start", 0.0)),
                "t_end": float(s.get("end", 0.0)),
                "text": (s.get("text") or "").strip(),
                "speaker_label": "SPEAKER_UNKNOWN",
                "layer": "processed",
                "lifecycle": "proposed",
            }
            for s in segments
            if (s.get("text") or "").strip()
        ]

    payload = {
        "source_audio": str(audio_path),
        "tool": "razamit/audio_transcriber",
        "profile": profile.key,
        "model_repo": profile.repo,
        "diarization": bool(args.speakers),
        "lifecycle": "proposed",
        "layer": "processed",
        "acquisition_note": "personal_asr_yt_dlp_audio_transcriber",
        "spans": spans,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    elapsed = time.monotonic() - started
    print(f"\nTranscript: {out_txt}")
    print(f"Spans JSON: {out_json} ({len(spans)} spans)")
    print(f"Elapsed: {format_timestamp(elapsed)} ({elapsed:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
