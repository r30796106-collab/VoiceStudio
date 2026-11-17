"""VoiceStudio: offline-first, consent-based Hindi-English voice tools."""

from .consent import VoiceConsent
from .profiles import VoiceProfileStore
from .text import detect_language_hint, normalize_text, split_sentences

__all__ = [
    "VoiceConsent",
    "VoiceProfileStore",
    "detect_language_hint",
    "normalize_text",
    "split_sentences",
]
