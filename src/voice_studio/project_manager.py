"""Create and inspect VoiceStudio project workspaces."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Settings
from .validation import make_project_id, validate_project_id, validate_project_name


class ProjectManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.settings.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str) -> dict[str, Any]:
        clean_name = validate_project_name(name)
        project_id = make_project_id(clean_name)
        project_dir = self.settings.projects_dir / project_id
        project_dir.mkdir(parents=False, exist_ok=False)
        try:
            for child in ("scripts", "audio", "exports"):
                (project_dir / child).mkdir()
            manifest = {
                "schema_version": 1,
                "project_id": project_id,
                "name": clean_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "created",
            }
            manifest_path = project_dir / "project.json"
            with manifest_path.open("x", encoding="utf-8") as stream:
                json.dump(manifest, stream, ensure_ascii=False, indent=2)
                stream.write("\\n")
            return manifest
        except Exception:
            shutil.rmtree(project_dir, ignore_errors=True)
            raise

    def get_project(self, project_id: str) -> dict[str, Any]:
        safe_id = validate_project_id(project_id)
        manifest_path = self.settings.projects_dir / safe_id / "project.json"
        with manifest_path.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
        if not isinstance(manifest, dict) or manifest.get("project_id") != safe_id:
            raise ValueError("Project manifest does not match its directory.")
        return manifest

    def list_projects(self) -> list[dict[str, Any]]:
        projects = []
        for directory in sorted(self.settings.projects_dir.iterdir(), key=lambda item: item.name):
            if not directory.is_dir() or directory.is_symlink():
                continue
            try:
                projects.append(self.get_project(directory.name))
            except (OSError, ValueError, json.JSONDecodeError):
                # Listing is intentionally read-only and skips invalid entries.
                continue
        return projects
