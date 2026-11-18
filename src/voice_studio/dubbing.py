"""Consent-gated, deterministic segment plans for dubbing projects.

This module prepares text and authorization metadata only. It does not translate,
synthesize, clone voices, read recordings, or transmit project data.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping

from .consent import VoiceConsent
from .core import validate_identifier
from .text import normalize_text

_SUPPORTED_LANGUAGES = frozenset({"en", "hi"})


@dataclass(frozen=True, slots=True)
class DubbingSegment:
    """One explicitly supplied source/target text pair in timeline order."""

    index: int
    source_text: str
    target_text: str
    language: str
    voice_id: str
    consent_id: str

    def __post_init__(self) -> None:
        if type(self.index) is not int or self.index < 0:
            raise ValueError("segment index must be a non-negative integer")
        if not isinstance(self.source_text, str) or not normalize_text(self.source_text):
            raise ValueError("source_text must not be empty")
        if not isinstance(self.target_text, str) or not normalize_text(self.target_text):
            raise ValueError("target_text must not be empty")
        if self.language not in _SUPPORTED_LANGUAGES:
            raise ValueError("language must be 'en' or 'hi'")
        validate_identifier(self.voice_id, field="voice_id")
        validate_identifier(self.consent_id, field="consent_id")


@dataclass(frozen=True, slots=True)
class DubbingPlan:
    """Validated, ordered plan; segment text remains exactly user supplied."""

    segments: tuple[DubbingSegment, ...]
    language: str

    @property
    def segment_count(self) -> int:
        return len(self.segments)


def build_dubbing_plan(
    segments: Iterable[DubbingSegment],
    consents: Mapping[str, VoiceConsent],
    *,
    at: datetime | None = None,
) -> DubbingPlan:
    """Build a plan only when every segment has active, matching dubbing consent."""
    items = tuple(segments)
    if not items:
        raise ValueError("a dubbing plan requires at least one segment")
    if any(not isinstance(item, DubbingSegment) for item in items):
        raise TypeError("all segments must be DubbingSegment instances")
    indexes = [item.index for item in items]
    if indexes != list(range(len(items))):
        raise ValueError("segment indexes must be unique, ordered, and start at zero")
    languages = {item.language for item in items}
    if len(languages) != 1:
        raise ValueError("all segments in a plan must use the same target language")

    for item in items:
        consent = consents.get(item.consent_id)
        if not isinstance(consent, VoiceConsent) or consent.consent_id != item.consent_id:
            raise ValueError(f"missing consent record for segment {item.index}")
        if not consent.permits("dubbing", at=at):
            raise ValueError(f"active dubbing consent required for segment {item.index}")

    return DubbingPlan(segments=items, language=items[0].language)
