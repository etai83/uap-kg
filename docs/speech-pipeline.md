# Speech pipeline: long-form YouTube → local ASR + diarization

**Status:** download verified; **primary ASR tool = [razamit/audio_transcriber](https://github.com/razamit/audio_transcriber)** (MLX + pyannote on Apple Silicon)  
**Spec:** §2.3 / §3 / Appendix A (personal ASR risk)  
**Plan:** [`docs/plans/v1-vertical-slice.md`](plans/v1-vertical-slice.md) M2

## Approach

Long YouTube videos are awkward for caption APIs. For the personal vertical slice we use:

1. **`yt-dlp -f bestaudio`** (plus modern YouTube workarounds)  
2. **ffmpeg** → **16 kHz mono WAV** (or pass any ffmpeg-readable file)  
3. **[`tools/audio_transcriber`](https://github.com/razamit/audio_transcriber)** — MLX Whisper (English turbo) + optional **pyannote** Community-1 diarization  
4. Output human `.txt` + machine **`proposed` spans JSON** (never auto-live)

Name attribution (label → Person) stays a separate curator-gated step (spec §9).

**Apple Silicon only** for the MLX path (this Mac is M1 Pro — supported).

## YouTube download gotchas (2025–2026)

Anonymous downloads often fail (SABR / missing formats / n-challenge). This machine needed:

| Requirement | Why |
|-------------|-----|
| **yt-dlp ≥ 2026.x** in project `.venv` | Old system yt-dlp on Python 3.9 is deprecated / broken |
| **Node.js** + `--js-runtimes node` | n-challenge solving (EJS) |
| **`--cookies-from-browser chrome`** (or safari/firefox) | Session formats when anonymous clients return storyboard-only |
| **ffmpeg** | Section downloads + WAV conversion |

Smoke test succeeded: 20s of `uVVqFg2v7ro` → `webm` → `16 kHz mono wav`.

## Setup

```bash
cd /path/to/uap-kg

# 1) yt-dlp env (repo root)
python3 -m venv .venv
.venv/bin/pip install -U 'yt-dlp[default]'

# 2) audio_transcriber (vendored)
git clone https://github.com/razamit/audio_transcriber tools/audio_transcriber
cd tools/audio_transcriber
./setup.sh --with-diarization    # MLX Whisper + pyannote (~2GB extras)
cd ../..
```

## Commands

```bash
# A) Download YouTube audio → data/audio/<id>.wav
.venv/bin/python scripts/download_audio.py https://youtu.be/uVVqFg2v7ro
.venv/bin/python scripts/download_audio.py fZyKcJQZrDA --section "*0:00-1:00"   # smoke
.venv/bin/python scripts/download_audio.py --slice-c2                          # full C2 (long)

# B) Transcribe + diarize via audio_transcriber (use ITS venv — has mlx/pyannote)
tools/audio_transcriber/.venv/bin/python scripts/transcribe_audio_transcriber.py \
  data/audio/<video_id>.wav --lang en --speakers --speakers-count 2
# → data/audio/<id>_speakers.txt
# → data/transcripts/<id>.spans.json

# Interactive (optional):
#   cd tools/audio_transcriber && TRANSCRIBE_LANG=en .venv/bin/python transcribe.py
```

**Note:** Two venvs by design — root `.venv` for yt-dlp; `tools/audio_transcriber/.venv` for MLX/pyannote (avoids fighting package sets).

## Output shape (proposed)

```json
{
  "source_wav": "data/audio/….wav",
  "lifecycle": "proposed",
  "layer": "processed",
  "acquisition_note": "personal_asr_yt_dlp",
  "spans": [
    {
      "t_start": 12.4,
      "t_end": 18.1,
      "text": "…",
      "speaker_label": "SPEAKER_00",
      "layer": "processed",
      "lifecycle": "proposed"
    }
  ]
}
```

## Provenance fields to record on ingest (when wiring store)

| Field | Value |
|-------|--------|
| track kind | `asr` + `diarization_turns` |
| acquisition_method | `personal_asr` / `yt_dlp_bestaudio_personal_asr` |
| extraction_run | whisper model size + pyannote pipeline id + timestamps |
| video_id | from filename / download metadata |

## Legal / product note

This is a **personal research path**, not a “ToS-cleared product claim” (spec §2.3, Appendix A). Do not commit audio under `data/`. Do not redistribute extracted audio.

## Next wiring

- Store spans as `processed` + `DERIVED_FROM` raw track rows (M2→M5)  
- Episode map host/guest (M3)  
- Claim proposal over spans (M4)  
