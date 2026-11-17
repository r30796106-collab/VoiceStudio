"""Local-only storage for consent-validated voice profile metadata."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from .consent import VoiceConsent, validate_profile_id


class VoiceProfileStore:
    """Persist profile metadata without copying or committing source recordings."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser()
        for ancestor in (self.root, *self.root.parents):
            if ancestor.is_symlink():
                raise ValueError("voice profile root path must not contain symlinks")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.root.is_symlink() or not self.root.is_dir():
            raise ValueError("voice profile root must be a regular directory")
        self.root = self.root.resolve(strict=True)
        os.chmod(self.root, 0o700)

    def create_profile(self, profile_id: str, consent: VoiceConsent) -> Path:
        profile_id = validate_profile_id(profile_id)
        if not isinstance(consent, VoiceConsent):
            raise TypeError("consent must be a validated VoiceConsent record")
        target = self.root / f"{profile_id}.json"
        if target.is_symlink():
            raise ValueError("profile metadata target must not be a symlink")
        if target.exists():
            raise FileExistsError(f"voice profile already exists: {profile_id}")
        payload = {
            "schema_version": 1,
            "profile_id": profile_id,
            "consent": consent.to_dict(),
        }
        encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        fd, temporary = tempfile.mkstemp(prefix=".profile-", dir=self.root)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            # Hard-link publication is atomic and refuses to overwrite a file
            # created by another process after the initial existence check.
            os.link(temporary, target, follow_symlinks=False)
            os.unlink(temporary)
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise
        return target

    def load_profile(self, profile_id: str) -> dict:
        profile_id = validate_profile_id(profile_id)
        target = self.root / f"{profile_id}.json"
        if target.is_symlink() or not target.is_file():
            raise FileNotFoundError(f"voice profile not found: {profile_id}")
        payload = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or set(payload) != {"schema_version", "profile_id", "consent"}:
            raise ValueError("voice profile metadata has an invalid schema")
        if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
            raise ValueError("unsupported voice profile schema version")
        if payload["profile_id"] != profile_id:
            raise ValueError("voice profile ID does not match its filename")
        consent = VoiceConsent.from_dict(payload["consent"])
        return {"schema_version": 1, "profile_id": profile_id, "consent": consent}
