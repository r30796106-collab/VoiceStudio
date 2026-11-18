"""Optional local eSpeak NG speech backend; no network or model downloads."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .text import normalize_text

_SUPPORTED_LANGUAGES = frozenset({"en", "hi"})


class SpeechEngineError(RuntimeError):
    """Raised when local speech synthesis is unavailable or fails."""


class EspeakNGBackend:
    """Generate PCM WAV speech using an installed eSpeak NG executable.

    Install eSpeak NG separately through the device's trusted package manager.
    This adapter never invokes a shell, downloads models, or sends text online.
    """

    def __init__(self, *, rate: int = 165, timeout_seconds: int = 60) -> None:
        if type(rate) is not int or not 80 <= rate <= 450:
            raise ValueError("rate must be an integer between 80 and 450")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 600:
            raise ValueError("timeout_seconds must be between 1 and 600")
        self.rate = rate
        self.timeout_seconds = timeout_seconds

    def synthesize(
        self,
        text: str,
        output_path: str | Path,
        *,
        language: str = "en",
    ) -> Path:
        content = normalize_text(text)
        if not content:
            raise ValueError("speech text must not be empty")
        if language not in _SUPPORTED_LANGUAGES:
            raise ValueError("language must be 'en' or 'hi'")
        target = Path(output_path)
        if target.suffix.lower() != ".wav":
            raise ValueError("output_path must use the .wav extension")
        if target.exists() and target.is_dir():
            raise ValueError("output_path must be a file path")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [
                    "espeak-ng", "-v", language, "-s", str(self.rate),
                    "-w", str(target), content,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError as exc:
            raise SpeechEngineError(
                "eSpeak NG is not installed; install it with the trusted OS package manager"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise SpeechEngineError("eSpeak NG synthesis timed out") from exc
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip()[:500]
            raise SpeechEngineError(f"eSpeak NG synthesis failed: {detail}") from exc
        if not target.is_file() or target.stat().st_size == 0:
            raise SpeechEngineError("eSpeak NG did not create a non-empty WAV file")
        return target
