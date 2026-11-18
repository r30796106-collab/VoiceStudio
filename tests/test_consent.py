from datetime import datetime, timedelta, timezone

import pytest

from voice_studio.consent import VoiceConsent


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def grant(**changes):
    values = {
        "consent_id": "voice-001",
        "subject_label": "Speaker A",
        "granted_by": "Speaker A",
        "scopes": frozenset({"tts", "dubbing"}),
        "granted_at": NOW,
        "expires_at": NOW + timedelta(days=30),
    }
    values.update(changes)
    return VoiceConsent(**values)


def test_consent_allows_only_granted_scope_inside_validity_window():
    consent = grant()
    assert consent.permits("tts", at=NOW)
    assert consent.permits("dubbing", at=NOW + timedelta(days=1))
    assert not consent.permits("voice_cloning", at=NOW)
    assert not consent.permits("tts", at=NOW + timedelta(days=30))


def test_revocation_is_immutable_and_blocks_future_use():
    consent = grant()
    revoked = consent.revoke(at=NOW + timedelta(days=2))
    assert consent.revoked_at is None
    assert revoked.revoked_at == NOW + timedelta(days=2)
    assert revoked.permits("tts", at=NOW + timedelta(days=1)) is False


@pytest.mark.parametrize("changes", [
    {"consent_id": "../escape"},
    {"subject_label": " "},
    {"scopes": frozenset({"everything"})},
    {"scopes": frozenset()},
    {"granted_at": datetime(2026, 1, 1)},
    {"expires_at": NOW},
    {"revoked_at": NOW - timedelta(seconds=1)},
])
def test_invalid_consent_is_rejected(changes):
    with pytest.raises(ValueError):
        grant(**changes)


def test_unknown_scope_is_never_permitted():
    assert not grant().permits("training", at=NOW)
