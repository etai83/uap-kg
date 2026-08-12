#!/usr/bin/env bash
# Install or refresh tools/audio_transcriber (MLX Whisper + pyannote).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AT="$ROOT/tools/audio_transcriber"

if [[ ! -f "$AT/transcribe.py" ]]; then
  echo "Cloning razamit/audio_transcriber into tools/..."
  mkdir -p "$ROOT/tools"
  git clone --depth 1 https://github.com/razamit/audio_transcriber "$AT"
  rm -rf "$AT/.git"
fi

cd "$AT"
./setup.sh --with-diarization
echo
echo "OK. Example:"
echo "  $AT/.venv/bin/python $ROOT/scripts/transcribe_audio_transcriber.py data/audio/<id>.wav --lang en --speakers"
