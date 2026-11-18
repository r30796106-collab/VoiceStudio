from datetime import datetime, timedelta, timezone

import pytest

from voice_studio.consent import VoiceConsent
from voice_studio.dubbing import DubbingSegment, build_dubbing_plan
from voice_studio.timeline import build_audio_timeline

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def approved_plan():
    consent = VoiceConsent(
        consent_id="consent-a",
        subject_label="Speaker A",
        granted_by="Speaker A",
        scopes=frozenset({"dubbing"}),
        granted_at=NOW,
        expires_at=NOW + timedelta(days=1),
    )
    segments = [
        DubbingSegment(i, f"Source {i}", f"Target {i}", "hi", "speaker-a", "consent-a")
        for i in range(2)
    ]
    return build_dubbing_plan(segments, {"consent-a": consent}, at=NOW)


def test_builds_contiguous_timeline_with_optional_gaps():
    timeline = build_audio_timeline(approved_plan(), [1200, 800], gap_ms=150)
    assert timeline.clip_count == 2
    assert [(clip.start_ms, clip.end_ms) for clip in timeline.clips] == [
        (0, 1200), (1350, 2150)
    ]
    assert timeline.duration_ms == 2150


def test_rejects_duration_count_and_invalid_values():
    plan = approved_plan()
    with pytest.raises(ValueError, match="one duration"):
        build_audio_timeline(plan, [100])
    with pytest.raises(ValueError, match="positive integers"):
        build_audio_timeline(plan, [100, 0])
    with pytest.raises(ValueError, match="gap_ms"):
        build_audio_timeline(plan, [100, 100], gap_ms=-1)


def test_rejects_unapproved_or_wrong_plan_type():
    with pytest.raises(TypeError, match="DubbingPlan"):
        build_audio_timeline(object(), [100, 100])
