"""VoiceStudio: independent voice and dubbing toolkit."""

__version__ = "0.1.0"

from .audio import AudioInfo, inspect_wav
from .core import VoiceStudioPaths, resolve_workspace_path, validate_identifier
from .text import TextSegment, normalize_text, segment_text
from .speech import EspeakNGBackend, SpeechEngineError
from .consent import VoiceConsent
from .dubbing import DubbingPlan, DubbingSegment, build_dubbing_plan
from .timeline import AudioTimeline, TimelineClip, build_audio_timeline

__all__ = ["AudioInfo", "VoiceStudioPaths", "inspect_wav", "resolve_workspace_path", "validate_identifier", "TextSegment", "normalize_text", "segment_text", "EspeakNGBackend", "SpeechEngineError", "VoiceConsent", "DubbingPlan", "DubbingSegment", "build_dubbing_plan", "AudioTimeline", "TimelineClip", "build_audio_timeline"]
