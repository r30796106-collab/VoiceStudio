"""Input validation helpers shared by VoiceStudio modules."""
import re
from pathlib import PurePosixPath, PureWindowsPath


def validate_project_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Project name must be text.")
    value = name.strip()
    if not value:
        raise ValueError("Project name cannot be empty.")
    if len(value) > 120:
        raise ValueError("Project name cannot exceed 120 characters.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("Project name cannot contain control characters.")
    return value


def make_project_id(name: str) -> str:
    value = validate_project_name(name).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    if not slug:
        raise ValueError("Project name must contain at least one ASCII letter or digit.")
    return slug[:64].rstrip("-")


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("Invalid project id.")
    if len(project_id) > 64:
        raise ValueError("Project id is too long.")
    return project_id


def validate_relative_path(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Path must be text.")
    if not value or not value.strip():
        raise ValueError("Path cannot be empty.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("Path cannot contain control characters.")
    normalized = value.replace("\\", "/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise ValueError("Absolute paths are not allowed.")
    parts = normalized.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("Path contains an unsafe component.")
    return str(posix)
