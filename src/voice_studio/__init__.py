"""VoiceStudio: independent voice and dubbing toolkit."""

__version__ = "0.1.0"

from .core import VoiceStudioPaths, resolve_workspace_path, validate_identifier

__all__ = ["VoiceStudioPaths", "resolve_workspace_path", "validate_identifier"]
