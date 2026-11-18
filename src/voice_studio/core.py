"""Lightweight, dependency-free VoiceStudio core utilities."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def validate_identifier(value: str, *, field: str = "identifier") -> str:
    """Validate a stable local ID suitable for profile/project directory names."""
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"invalid {field}: use 1-64 letters, digits, '_' or '-'")
    return value


def resolve_workspace_path(root: str | Path, relative: str) -> Path:
    """Resolve a workspace-relative path while rejecting traversal and symlinks."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("path must be a non-empty POSIX relative path")
    candidate_part = PurePosixPath(relative)
    if candidate_part.is_absolute() or any(part in {"", ".", ".."} for part in relative.split("/")):
        raise ValueError("path must not be absolute or contain traversal components")

    workspace = Path(root).resolve()
    candidate = workspace.joinpath(*candidate_part.parts)
    current = workspace
    for part in candidate_part.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("workspace paths must not traverse symlinks")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise ValueError("resolved path escapes the workspace") from exc
    return resolved


@dataclass(frozen=True, slots=True)
class VoiceStudioPaths:
    """Canonical local directories; construction never creates or downloads data."""
    root: Path

    @classmethod
    def at(cls, root: str | Path) -> "VoiceStudioPaths":
        return cls(Path(root).resolve())

    @property
    def models(self) -> Path:
        return resolve_workspace_path(self.root, "models")

    @property
    def voice_profiles(self) -> Path:
        return resolve_workspace_path(self.root, "voice_profiles")

    @property
    def projects(self) -> Path:
        return resolve_workspace_path(self.root, "voice_projects")

    @property
    def outputs(self) -> Path:
        return resolve_workspace_path(self.root, "outputs")

    def project_file(self, project_id: str, relative: str = "project.json") -> Path:
        validate_identifier(project_id, field="project_id")
        return resolve_workspace_path(self.root, f"voice_projects/{project_id}/{relative}")
