"""Filesystem configuration for VoiceStudio."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Locations for user data; source code and personal data stay separate."""

    data_dir: Path

    @classmethod
    def default(cls) -> "Settings":
        return cls(Path.home() / "VoiceStudioData")

    @property
    def projects_dir(self) -> Path:
        return self.data_dir / "projects"

    @property
    def profiles_dir(self) -> Path:
        return self.data_dir / "profiles"

    @property
    def models_dir(self) -> Path:
        return self.data_dir / "models"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    def create_directories(self) -> None:
        for directory in (
            self.data_dir,
            self.projects_dir,
            self.profiles_dir,
            self.models_dir,
            self.outputs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
