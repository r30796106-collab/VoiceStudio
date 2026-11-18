"""Deterministic audio timeline metadata for approved dubbing plans.

This module schedules caller-supplied segment durations only. It does not
render, synthesize, decode, or play audio.
"""
from __future__ import annotations

from dataclasses import dataclass

from .dubbing import DubbingPlan


@dataclass(frozen=True, slots=True)
class TimelineClip:
    segment_index: int
    start_ms: int
    duration_ms: int
    voice_id: str

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms


@dataclass(frozen=True, slots=True)
class AudioTimeline:
    clips: tuple[TimelineClip, ...]
    duration_ms: int

    @property
    def clip_count(self) -> int:
        return len(self.clips)


def build_audio_timeline(
    plan: DubbingPlan,
    durations_ms: tuple[int, ...] | list[int],
    *,
    gap_ms: int = 0,
) -> AudioTimeline:
    """Place each approved plan segment sequentially using supplied durations."""
    if not isinstance(plan, DubbingPlan):
        raise TypeError("plan must be a DubbingPlan")
    if not isinstance(durations_ms, (tuple, list)):
        raise TypeError("durations_ms must be a tuple or list")
    if len(durations_ms) != plan.segment_count:
        raise ValueError("one duration is required for each plan segment")
    if type(gap_ms) is not int or gap_ms < 0:
        raise ValueError("gap_ms must be a non-negative integer")
    if any(type(value) is not int or value <= 0 for value in durations_ms):
        raise ValueError("all segment durations must be positive integers")

    cursor = 0
    clips = []
    for segment, duration in zip(plan.segments, durations_ms):
        clip = TimelineClip(
            segment_index=segment.index,
            start_ms=cursor,
            duration_ms=duration,
            voice_id=segment.voice_id,
        )
        clips.append(clip)
        cursor = clip.end_ms + gap_ms

    return AudioTimeline(clips=tuple(clips), duration_ms=clips[-1].end_ms)
