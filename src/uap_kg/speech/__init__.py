"""Speech pipeline: YouTube audio download + local ASR/diarization."""

from .download import download_audio

__all__ = ["download_audio"]
