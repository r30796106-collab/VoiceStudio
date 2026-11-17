"""VoiceStudio: offline-first, consent-based Hindi-English voice tools."""

from .audio import AudioInfo, inspect_wav, sha256_file
from .consent import VoiceConsent
from .profiles import VoiceProfileStore
from .text import detect_language_hint, normalize_text, split_sentences

__all__ = [
    "AudioInfo",
    "inspect_wav",
    "sha256_file",
    "VoiceConsent",
    "VoiceProfileStore",
    "detect_language_hint",
    "normalize_text",
    "split_sentences",
]
