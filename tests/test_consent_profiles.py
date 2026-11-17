from pathlib import Path

import pytest

from voice_studio import VoiceConsent, VoiceProfileStore


def consent(**overrides):
    values = {
        "consent_id": "consent-001",
        "voice_owner": "self",
        "consent_granted": True,
        "consent_recorded_at": "2026-11-17T10:00:00+05:30",
        "consent_method": "self_attested",
        "source_audio_sha256": "a" * 64,
        "scopes": ("tts", "voice_cloning", "dubbing"),
    }
    values.update(overrides)
    return VoiceConsent(**values)


def test_profile_requires_explicit_consent():
    with pytest.raises(PermissionError, match="explicit recorded consent"):
        consent(consent_granted=False)


def test_profile_rejects_missing_timezone_and_invalid_audio_hash():
    with pytest.raises(ValueError, match="timezone"):
        consent(consent_recorded_at="2026-11-17T10:00:00")
    with pytest.raises(ValueError, match="SHA-256"):
        consent(source_audio_sha256="not-a-hash")


def test_profile_store_round_trip_and_private_permissions(tmp_path: Path):
    store = VoiceProfileStore(tmp_path / "profiles")
    path = store.create_profile("my-voice", consent())
    loaded = store.load_profile("my-voice")
    assert loaded["profile_id"] == "my-voice"
    assert loaded["consent"].consent_id == "consent-001"
    assert path.stat().st_mode & 0o777 == 0o600


def test_profile_store_refuses_overwrite_and_unsafe_ids(tmp_path: Path):
    store = VoiceProfileStore(tmp_path / "profiles")
    store.create_profile("my-voice", consent())
    with pytest.raises(FileExistsError):
        store.create_profile("my-voice", consent())
    for bad in ("../other", "/tmp/voice", ".hidden", "UPPER"):
        with pytest.raises(ValueError):
            store.create_profile(bad, consent())


def test_profile_store_rejects_symlink_root_and_profile(tmp_path: Path):
    real = tmp_path / "real"
    real.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        VoiceProfileStore(alias)
    store = VoiceProfileStore(real)
    (real / "linked.json").symlink_to(tmp_path / "outside.json")
    with pytest.raises(ValueError, match="symlink"):
        store.create_profile("linked", consent())
