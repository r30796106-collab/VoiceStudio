"""Safe, atomic file access within a managed directory."""
import os
import tempfile
from pathlib import Path

from .validation import validate_relative_path


class FileManager:
    def __init__(self, root: Path):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative_path: str) -> Path:
        safe = validate_relative_path(relative_path)
        candidate = self.root.joinpath(*safe.split("/"))
        current = self.root
        for part in safe.split("/"):
            current = current / part
            if current.is_symlink():
                raise ValueError("Symbolic links are not allowed in managed paths.")
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Path escapes the managed directory.") from exc
        return resolved

    def write_bytes(self, relative_path: str, data: bytes) -> Path:
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes.")
        target = self._resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Re-check after directory creation to catch pre-existing symlink components.
        target = self._resolve(relative_path)
        fd, temporary_name = tempfile.mkstemp(prefix=".voicestudio-", dir=target.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            # Refuse a symlink target immediately before replacement.
            if target.is_symlink():
                raise ValueError("Symbolic-link targets are not allowed.")
            os.replace(temporary, target)
        except Exception:
            try:
                temporary.unlink(missing_ok=True)
            finally:
                raise
        return target

    def read_bytes(self, relative_path: str) -> bytes:
        target = self._resolve(relative_path)
        return target.read_bytes()
