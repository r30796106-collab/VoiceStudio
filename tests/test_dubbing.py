from datetime import datetime, timedelta, timezone

import pytest

from voice_studio.consent import VoiceConsent
from voice_studio.dubbing import DubbingSegment, build_dubbing_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def consent(scopes=frozenset({"dubbing"}), *, revoked_at=None):
    return VoiceConsent(
        consent_id="consent-a",
        subject_label="Speaker A",
        granted_by="Speaker A",
        scopes=scopes,
        granted_at=NOW,
        expires_at=NOW + timedelta(days=5),
        revoked_at=revoked_at,
    )


def segment(index=0, **changes):
    values = {
        "index": index,
        "source_text": "Hello.",
        "target_text": "नमस्ते।",
        "language": "hi",
        "voice_id": "speaker-a",
        "consent_id": "consent-a",
    }
    values.update(changes)
    return DubbingSegment(**values)


def test_builds_ordered_plan_only_with_active_dubbing_consent():
    plan = build_dubbing_plan(
        [segment(0), segment(1, source_text="How are you?")],
        {"consent-a": consent()},
        at=NOW,
    )
    assert plan.segment_count == 2
    assert plan.language == "hi"
    assert [item.index for item in plan.segments] == [0, 1]


@pytest.mark.parametrize("grant,at", [
    (consent(frozenset({"tts"})), NOW),
    (consent(), NOW + timedelta(days=5)),
    (consent(revoked_at=NOW), NOW),
])
def test_rejects_missing_expired_or_revoked_dubbing_consent(grant, at):
    with pytest.raises(ValueError, match="consent"):
        build_dubbing_plan([segment()], {"consent-a": grant}, at=at)


def test_rejects_missing_consent_record():
    with pytest.raises(ValueError, match="missing consent"):
        build_dubbing_plan([segment()], {}, at=NOW)


def test_rejects_nonconsecutive_or_mixed_language_segments():
    with pytest.raises(ValueError, match="indexes"):
        build_dubbing_plan([segment(1)], {"consent-a": consent()}, at=NOW)
    with pytest.raises(ValueError, match="same target language"):
        build_dubbing_plan(
            [segment(0), segment(1, language="en")],
            {"consent-a": consent()},
            at=NOW,
        )


def test_rejects_empty_text_and_invalid_voice_identifier():
    with pytest.raises(ValueError, match="source_text"):
        segment(source_text="  ")
    with pytest.raises(ValueError, match="voice_id"):
        segment(voice_id="../outside")


def test_rejects_empty_plan():
    with pytest.raises(ValueError, match="at least one"):
        build_dubbing_plan([], {}, at=NOW)
