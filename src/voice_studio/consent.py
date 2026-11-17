"""Validated consent records for personal voice-profile operations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
_ALLOWED_SCOPES = frozenset({"tts", "voice_cloning", "dubbing"})


@dataclass(frozen=True, slots=True)
class VoiceConsent:
    """Explicit, auditable permission for a voice owner-controlled profile."""

    consent_id: str
    voice_owner: str
    consent_granted: bool
    consent_recorded_at: str
    consent_method: str
    source_audio_sha256: str
    scopes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.consent_id, str) or not self.consent_id.strip():
            raise ValueError("consent_id is required")
        if not isinstance(self.voice_owner, str) or not self.voice_owner.strip():
            raise ValueError("voice_owner label is required")
        if self.consent_granted is not True:
            raise PermissionError("voice profile operations require explicit recorded consent")
        if not isinstance(self.consent_recorded_at, str):
            raise ValueError("consent_recorded_at must be an ISO-8601 timestamp")
        try:
            recorded = datetime.fromisoformat(self.consent_recorded_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("consent_recorded_at must be an ISO-8601 timestamp") from exc
        if recorded.tzinfo is None:
            raise ValueError("consent_recorded_at must include a timezone")
        if not isinstance(self.consent_method, str) or self.consent_method not in {"self_attested", "written_release", "recorded_release"}:
            raise ValueError("consent_method is not an approved explicit-consent method")
        if not isinstance(self.source_audio_sha256, str) or not _SHA256.fullmatch(self.source_audio_sha256):
            raise ValueError("source_audio_sha256 must be a lowercase SHA-256 digest")
        if not isinstance(self.scopes, tuple) or not self.scopes:
            raise ValueError("at least one consent scope is required")
        if any(not isinstance(scope, str) for scope in self.scopes):
            raise ValueError("consent scopes must be text values")
        if len(set(self.scopes)) != len(self.scopes) or any(scope not in _ALLOWED_SCOPES for scope in self.scopes):
            raise ValueError("consent scopes contain duplicates or unsupported operations")

    def to_dict(self) -> dict[str, Any]:
        return {
            "consent_id": self.consent_id,
            "voice_owner": self.voice_owner,
            "consent_granted": self.consent_granted,
            "consent_recorded_at": self.consent_recorded_at,
            "consent_method": self.consent_method,
            "source_audio_sha256": self.source_audio_sha256,
            "scopes": list(self.scopes),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "VoiceConsent":
        required = {
            "consent_id", "voice_owner", "consent_granted", "consent_recorded_at",
            "consent_method", "source_audio_sha256", "scopes",
        }
        if not isinstance(value, dict) or set(value) != required:
            raise ValueError("consent record has an invalid schema")
        if not isinstance(value["scopes"], list):
            raise ValueError("consent scopes must be an array")
        return cls(
            consent_id=value["consent_id"],
            voice_owner=value["voice_owner"],
            consent_granted=value["consent_granted"],
            consent_recorded_at=value["consent_recorded_at"],
            consent_method=value["consent_method"],
            source_audio_sha256=value["source_audio_sha256"],
            scopes=tuple(value["scopes"]),
        )


def validate_profile_id(profile_id: str) -> str:
    if not isinstance(profile_id, str) or not _PROFILE_ID.fullmatch(profile_id):
        raise ValueError("profile_id must be a short lowercase slug")
    return profile_id
