"""Download YouTube audio via yt-dlp and convert to 16 kHz mono WAV.

YouTube (2025–2026) often requires a JS runtime for n-challenge solving and
browser cookies when SABR / PO-token experiments block anonymous clients.

Default recipe (personal research; see spec Appendix A legal risk note):

  yt-dlp -f bestaudio URL
  ffmpeg → 16 kHz mono PCM WAV (Whisper / pyannote friendly)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

VIDEO_ID_RE = re.compile(
    r"(?:youtu\.be/|v=|/shorts/|/embed/|youtube\.com/watch\?.*?v=)([A-Za-z0-9_-]{11})"
)


@dataclass
class DownloadResult:
    video_id: str
    url: str
    audio_raw: Path
    audio_wav: Path
    duration_s: Optional[float]
    acquisition_method: str = "yt_dlp_bestaudio_personal_asr"


def extract_video_id(url_or_id: str) -> str:
    s = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = VIDEO_ID_RE.search(s)
    if not m:
        raise ValueError(f"Could not parse YouTube video id from: {url_or_id!r}")
    return m.group(1)


def _require_bin(name: str) -> str:
    # Prefer project .venv first (system yt-dlp is often too old for YouTube 2026).
    root = Path(__file__).resolve().parents[3]
    venv_candidate = root / ".venv" / "bin" / name
    if venv_candidate.is_file():
        return str(venv_candidate)
    path = shutil.which(name)
    if not path:
        raise RuntimeError(
            f"Required binary not found: {name}. "
            f"Install into .venv (e.g. .venv/bin/pip install 'yt-dlp[default]') "
            f"or put {name} on PATH."
        )
    return path


def download_audio(
    url_or_id: str,
    out_dir: Path | str,
    *,
    cookies_from_browser: Optional[str] = "chrome",
    section: Optional[str] = None,
    js_runtime: str = "node",
    force: bool = False,
) -> DownloadResult:
    """
    Download bestaudio for a YouTube video and convert to 16 kHz mono WAV.

    Args:
        url_or_id: Full YouTube URL or 11-char id.
        out_dir: Directory for audio artifacts (created if missing).
        cookies_from_browser: Browser name for yt-dlp --cookies-from-browser, or None.
        section: Optional yt-dlp --download-sections value, e.g. "*0:00-0:45".
        js_runtime: Passed to --js-runtimes (node recommended).
        force: Re-download even if WAV already exists.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    video_id = extract_video_id(url_or_id)
    url = f"https://www.youtube.com/watch?v={video_id}"
    wav_path = out_dir / f"{video_id}.wav"
    meta_path = out_dir / f"{video_id}.download.json"

    if wav_path.is_file() and not force:
        duration = _probe_duration(wav_path)
        raw = _find_raw_sidecar(out_dir, video_id) or wav_path
        return DownloadResult(
            video_id=video_id,
            url=url,
            audio_raw=raw,
            audio_wav=wav_path,
            duration_s=duration,
        )

    ytdlp = _require_bin("yt-dlp")
    ffmpeg = _require_bin("ffmpeg")

    # Intermediate: let yt-dlp choose extension (often webm/m4a)
    tmpl = str(out_dir / f"{video_id}.%(ext)s")
    cmd: list[str] = [
        ytdlp,
        "-f",
        "bestaudio/best",
        "-o",
        tmpl,
        "--no-playlist",
        "--no-overwrites" if not force else "--force-overwrites",
        "--js-runtimes",
        js_runtime,
        "--remote-components",
        "ejs:github",
    ]
    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])
    if section:
        cmd.extend(["--download-sections", section])
    cmd.append(url)

    subprocess.run(cmd, check=True)

    raw_path = _find_raw_sidecar(out_dir, video_id)
    if raw_path is None:
        raise FileNotFoundError(f"yt-dlp finished but no audio file for {video_id} in {out_dir}")

    # Convert to 16 kHz mono PCM for Whisper / pyannote
    conv = [
        ffmpeg,
        "-y",
        "-i",
        str(raw_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]
    subprocess.run(conv, check=True, capture_output=True)

    duration = _probe_duration(wav_path)
    result = DownloadResult(
        video_id=video_id,
        url=url,
        audio_raw=raw_path,
        audio_wav=wav_path,
        duration_s=duration,
    )
    meta_path.write_text(json.dumps(asdict(result), indent=2, default=str) + "\n")
    return result


def _find_raw_sidecar(out_dir: Path, video_id: str) -> Optional[Path]:
    for p in sorted(out_dir.glob(f"{video_id}.*")):
        if p.suffix.lower() in {".webm", ".m4a", ".opus", ".ogg", ".mp3", ".mp4", ".wav"}:
            if p.name == f"{video_id}.wav":
                continue
            return p
    return None


def _probe_duration(path: Path) -> Optional[float]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        out = subprocess.check_output(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
        return float(out) if out else None
    except (subprocess.CalledProcessError, ValueError):
        return None
