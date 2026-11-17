"""Safe WAV metadata inspection for VoiceStudio's audio pipeline."""
from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AudioInfo:
    path: Path
    channels: int
    sample_width_bytes: int
    sample_rate_hz: int
    frame_count: int
    duration_seconds: float


def inspect_wav(path: str | Path) -> AudioInfo:
    """Read WAV metadata without loading audio samples into memory."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        with wave.open(str(source), "rb") as stream:
            channels = stream.getnchannels()
            sample_width = stream.getsampwidth()
            sample_rate = stream.getframerate()
            frames = stream.getnframes()
            compression = stream.getcomptype()
            if compression != "NONE":
                raise ValueError("only uncompressed PCM WAV files are supported")
            if channels < 1 or sample_width not in {1, 2, 3, 4} or sample_rate < 1:
                raise ValueError("WAV contains unsupported audio parameters")
            duration = frames / sample_rate
            return AudioInfo(
                path=source.resolve(),
                channels=channels,
                sample_width_bytes=sample_width,
                sample_rate_hz=sample_rate,
                frame_count=frames,
                duration_seconds=duration,
            )
    except (wave.Error, EOFError) as exc:
        raise ValueError(f"invalid or unsupported WAV file: {source}") from exc
