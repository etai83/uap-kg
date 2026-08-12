"""Local ASR + pyannote diarization → proposed processed spans (JSON).

Default stack (spec §3 R):
  - ASR: faster-whisper (Whisper)
  - Diarization: pyannote.audio (needs HF token + model agreement)
  - Optional: WhisperX when installed (word alignment + assign_word_speakers)

Output is **proposed** structure only — never auto-live (spec §12).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ProcessedSpan:
    t_start: float
    t_end: float
    text: str
    speaker_label: str
    layer: str = "processed"
    lifecycle: str = "proposed"


def transcribe_and_diarize(
    wav_path: Path | str,
    out_json: Path | str,
    *,
    model_size: str = "base",
    language: str = "en",
    min_speakers: Optional[int] = 2,
    max_speakers: Optional[int] = 4,
    device: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Run local ASR + diarization on a 16 kHz mono WAV.

    Env:
      HF_TOKEN or HUGGING_FACE_HUB_TOKEN — required for pyannote models.
    """
    wav_path = Path(wav_path)
    out_json = Path(out_json)
    if not wav_path.is_file():
        raise FileNotFoundError(wav_path)

    # Prefer WhisperX end-to-end if available
    try:
        spans = _run_whisperx(
            wav_path,
            model_size=model_size,
            language=language,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            device=device,
        )
    except ImportError:
        spans = _run_faster_whisper_plus_pyannote(
            wav_path,
            model_size=model_size,
            language=language,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            device=device,
        )

    payload = {
        "source_wav": str(wav_path),
        "lifecycle": "proposed",
        "layer": "processed",
        "acquisition_note": "personal_asr_yt_dlp",
        "spans": [asdict(s) if isinstance(s, ProcessedSpan) else s for s in spans],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n")
    return payload["spans"]


def _run_whisperx(
    wav_path: Path,
    *,
    model_size: str,
    language: str,
    min_speakers: Optional[int],
    max_speakers: Optional[int],
    device: Optional[str],
) -> list[ProcessedSpan]:
    import whisperx  # type: ignore

    dev = device or ("cuda" if _cuda() else "cpu")
    compute_type = "float16" if dev == "cuda" else "int8"
    model = whisperx.load_model(model_size, dev, compute_type=compute_type, language=language)
    audio = whisperx.load_audio(str(wav_path))
    result = model.transcribe(audio, batch_size=8)

    align_model, metadata = whisperx.load_align_model(language_code=language, device=dev)
    result = whisperx.align(
        result["segments"], align_model, metadata, audio, dev, return_char_alignments=False
    )

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=token, device=dev)
    diarize_segments = diarize_model(
        audio, min_speakers=min_speakers, max_speakers=max_speakers
    )
    result = whisperx.assign_word_speakers(diarize_segments, result)

    spans: list[ProcessedSpan] = []
    for seg in result.get("segments", []):
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        spans.append(
            ProcessedSpan(
                t_start=float(seg["start"]),
                t_end=float(seg["end"]),
                text=text,
                speaker_label=str(seg.get("speaker") or "SPEAKER_UNKNOWN"),
            )
        )
    return spans


def _run_faster_whisper_plus_pyannote(
    wav_path: Path,
    *,
    model_size: str,
    language: str,
    min_speakers: Optional[int],
    max_speakers: Optional[int],
    device: Optional[str],
) -> list[ProcessedSpan]:
    from faster_whisper import WhisperModel  # type: ignore

    dev = device or ("cuda" if _cuda() else "cpu")
    compute_type = "float16" if dev == "cuda" else "int8"
    model = WhisperModel(model_size, device=dev, compute_type=compute_type)
    segments_iter, _info = model.transcribe(str(wav_path), language=language, word_timestamps=True)
    asr_segments = list(segments_iter)

    diar_turns = _pyannote_turns(
        wav_path, min_speakers=min_speakers, max_speakers=max_speakers, device=dev
    )

    spans: list[ProcessedSpan] = []
    for seg in asr_segments:
        text = (seg.text or "").strip()
        if not text:
            continue
        mid = (seg.start + seg.end) / 2.0
        speaker = _speaker_at(diar_turns, mid)
        spans.append(
            ProcessedSpan(
                t_start=float(seg.start),
                t_end=float(seg.end),
                text=text,
                speaker_label=speaker,
            )
        )
    return spans


def _pyannote_turns(
    wav_path: Path,
    *,
    min_speakers: Optional[int],
    max_speakers: Optional[int],
    device: str,
) -> list[tuple[float, float, str]]:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN (or HUGGING_FACE_HUB_TOKEN) required for pyannote diarization. "
            "Accept model terms on Hugging Face, then export the token."
        )

    from pyannote.audio import Pipeline  # type: ignore
    import torch  # type: ignore

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=token,
    )
    if device == "cuda" and torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))

    params: dict[str, Any] = {}
    if min_speakers is not None:
        params["min_speakers"] = min_speakers
    if max_speakers is not None:
        params["max_speakers"] = max_speakers

    diarization = pipeline(str(wav_path), **params)
    turns: list[tuple[float, float, str]] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        label = speaker if str(speaker).startswith("SPEAKER_") else f"SPEAKER_{speaker}"
        turns.append((float(turn.start), float(turn.end), str(label)))
    return turns


def _speaker_at(turns: list[tuple[float, float, str]], t: float) -> str:
    for start, end, spk in turns:
        if start <= t <= end:
            return spk
    # nearest turn
    if not turns:
        return "SPEAKER_UNKNOWN"
    best = min(turns, key=lambda x: min(abs(t - x[0]), abs(t - x[1])))
    return best[2]


def _cuda() -> bool:
    try:
        import torch  # type: ignore

        return bool(torch.cuda.is_available())
    except ImportError:
        return False
