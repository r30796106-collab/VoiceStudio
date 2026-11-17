"""Bounded WAV inspection and hashing using only the Python standard library."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import wave

DEFAULT_MAX_FILE_BYTES = 500 * 1024 * 1024
DEFAULT_MAX_DURATION_SECONDS = 30 * 60


@dataclass(frozen=True, slots=True)
class AudioInfo:
    path: str
    file_bytes: int
    sample_rate: int
    channels: int
    sample_width_bytes: int
    frames: int
    duration_seconds: float
    compression: str


def _regular_file(path: str | Path, max_file_bytes: int) -> Path:
    target = Path(path).expanduser()
    if target.is_symlink():
        raise ValueError("audio file must not be a symlink")
    if type(max_file_bytes) is not int or max_file_bytes < 1:
        raise ValueError("max_file_bytes must be a positive integer")
    try:
        resolved = target.resolve(strict=True)
        if target.is_symlink() or not resolved.is_file():
            raise ValueError("audio input must be a regular file")
        size = resolved.stat().st_size
    except OSError as exc:
        raise ValueError(f"audio file is unavailable: {exc}") from exc
    if size < 1:
        raise ValueError("audio file is empty")
    if size > max_file_bytes:
        raise ValueError("audio file exceeds the configured size limit")
    return resolved


def sha256_file(path: str | Path, *, max_file_bytes: int = DEFAULT_MAX_FILE_BYTES) -> str:
    """Hash a bounded regular file without loading it all into memory."""
    target = _regular_file(path, max_file_bytes)
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_wav(
    path: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_duration_seconds: float = DEFAULT_MAX_DURATION_SECONDS,
) -> AudioInfo:
    """Validate uncompressed PCM WAV metadata before a model reads the audio."""
    if isinstance(max_duration_seconds, bool) or not isinstance(max_duration_seconds, (int, float)):
        raise ValueError("max_duration_seconds must be a positive finite number")
    if not math.isfinite(max_duration_seconds) or max_duration_seconds <= 0:
        raise ValueError("max_duration_seconds must be a positive finite number")
    target = _regular_file(path, max_file_bytes)
    try:
        with wave.open(str(target), "rb") as audio:
            channels = audio.getnchannels()
            sample_width = audio.getsampwidth()
            sample_rate = audio.getframerate()
            frames = audio.getnframes()
            compression = audio.getcomptype()
            if compression != "NONE":
                raise ValueError("only uncompressed PCM WAV audio is supported")
            if channels not in {1, 2}:
                raise ValueError("WAV must be mono or stereo")
            if sample_width not in {1, 2, 3, 4}:
                raise ValueError("unsupported PCM sample width")
            if not 8_000 <= sample_rate <= 96_000:
                raise ValueError("WAV sample rate must be between 8 kHz and 96 kHz")
            if frames < 1:
                raise ValueError("WAV contains no audio frames")
            duration = frames / sample_rate
            if duration > max_duration_seconds:
                raise ValueError("WAV exceeds the configured duration limit")
    except (wave.Error, EOFError, OSError) as exc:
        raise ValueError(f"invalid or unsupported WAV file: {exc}") from exc
    return AudioInfo(
        path=str(target),
        file_bytes=target.stat().st_size,
        sample_rate=sample_rate,
        channels=channels,
        sample_width_bytes=sample_width,
        frames=frames,
        duration_seconds=duration,
        compression=compression,
    )
