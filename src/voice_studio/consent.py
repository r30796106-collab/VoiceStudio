"""Explicit, time-bounded consent records for voice operations.

This module stores no recordings, embeddings, or biometric templates. It only
validates consent metadata supplied by the application or user.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

_ALLOWED_SCOPES = frozenset({"tts", "dubbing", "voice_conversion", "voice_cloning"})
_MAX_LABEL_LENGTH = 120


def _aware_utc(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class VoiceConsent:
    """A narrowly scoped consent grant for one identified voice subject."""

    consent_id: str
    subject_label: str
    granted_by: str
    scopes: frozenset[str]
    granted_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        from .core import validate_identifier

        validate_identifier(self.consent_id, field="consent_id")
        for field, value in (("subject_label", self.subject_label), ("granted_by", self.granted_by)):
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > _MAX_LABEL_LENGTH:
                raise ValueError(f"{field} must contain 1-{_MAX_LABEL_LENGTH} characters")
        if not isinstance(self.scopes, frozenset) or not self.scopes:
            raise ValueError("scopes must be a non-empty frozenset")
        if any(not isinstance(scope, str) or scope not in _ALLOWED_SCOPES for scope in self.scopes):
            raise ValueError("scopes contain an unsupported voice operation")
        granted = _aware_utc(self.granted_at, "granted_at")
        expires = _aware_utc(self.expires_at, "expires_at")
        if expires <= granted:
            raise ValueError("expires_at must be later than granted_at")
        if self.revoked_at is not None:
            revoked = _aware_utc(self.revoked_at, "revoked_at")
            if revoked < granted:
                raise ValueError("revoked_at cannot be earlier than granted_at")

    def permits(self, scope: str, *, at: datetime | None = None) -> bool:
        """Return true only while this grant is active for the requested scope."""
        if scope not in _ALLOWED_SCOPES or scope not in self.scopes:
            return False
        instant = _aware_utc(at or datetime.now(timezone.utc), "at")
        return (
            self.revoked_at is None
            and self.granted_at.astimezone(timezone.utc) <= instant
            < self.expires_at.astimezone(timezone.utc)
        )

    def revoke(self, *, at: datetime | None = None) -> "VoiceConsent":
        """Return a revoked copy; the original immutable record is unchanged."""
        instant = _aware_utc(at or datetime.now(timezone.utc), "at")
        if instant < self.granted_at.astimezone(timezone.utc):
            raise ValueError("revocation cannot predate consent")
        return VoiceConsent(
            consent_id=self.consent_id,
            subject_label=self.subject_label,
            granted_by=self.granted_by,
            scopes=self.scopes,
            granted_at=self.granted_at,
            expires_at=self.expires_at,
            revoked_at=instant,
        )
