"""Standard-library tests for VoiceStudio's core foundation."""
import tempfile
import unittest
from pathlib import Path

from voice_studio.config import Settings
from voice_studio.file_manager import FileManager
from voice_studio.project_manager import ProjectManager
from voice_studio.validation import (
    make_project_id,
    validate_project_name,
    validate_project_id,
    validate_relative_path,
)


class ValidationTests(unittest.TestCase):
    def test_project_name_is_trimmed(self):
        self.assertEqual(validate_project_name("  Demo  "), "Demo")

    def test_invalid_project_names(self):
        for value in ("", "   ", "bad\nname", "x" * 121):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_project_name(value)
        with self.assertRaises(TypeError):
            validate_project_name(None)

    def test_project_id(self):
        self.assertEqual(make_project_id("My First Story!"), "my-first-story")
        with self.assertRaises(ValueError):
            make_project_id("हिन्दी")
        with self.assertRaises(ValueError):
            validate_project_id("../escape")

    def test_relative_paths(self):
        self.assertEqual(validate_relative_path("audio/clip.wav"), "audio/clip.wav")
        for value in ("", "../escape", "a/../b", "/tmp/file", "C:\\temp\\file", "a//b"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_relative_path(value)


class SettingsTests(unittest.TestCase):
    def test_create_directories_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            settings = Settings(Path(temp) / "data")
            settings.create_directories()
            settings.create_directories()
            for path in (settings.projects_dir, settings.profiles_dir, settings.models_dir, settings.outputs_dir):
                self.assertTrue(path.is_dir())


class FileManagerTests(unittest.TestCase):
    def test_write_and_read_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = FileManager(Path(temp) / "managed")
            target = manager.write_bytes("audio/sample.wav", b"voice")
            self.assertEqual(target.read_bytes(), b"voice")
            self.assertEqual(manager.read_bytes("audio/sample.wav"), b"voice")

    def test_reject_non_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = FileManager(Path(temp))
            with self.assertRaises(TypeError):
                manager.write_bytes("file.bin", "not bytes")

    def test_reject_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            outside = base / "outside"
            outside.mkdir()
            root = base / "managed"
            manager = FileManager(root)
            link = root / "escape"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are unavailable on this platform.")
            with self.assertRaises(ValueError):
                manager.write_bytes("escape/file.txt", b"blocked")


class ProjectManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "data")
        self.manager = ProjectManager(self.settings)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_get_and_list_project(self):
        created = self.manager.create_project("Ayaan Story")
        self.assertEqual(created["project_id"], "ayaan-story")
        loaded = self.manager.get_project("ayaan-story")
        self.assertEqual(loaded["name"], "Ayaan Story")
        self.assertEqual(len(self.manager.list_projects()), 1)
        for child in ("scripts", "audio", "exports"):
            self.assertTrue((self.settings.projects_dir / "ayaan-story" / child).is_dir())

    def test_duplicate_project_is_rejected(self):
        self.manager.create_project("Demo")
        with self.assertRaises(FileExistsError):
            self.manager.create_project("Demo")

    def test_missing_project(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.get_project("missing")

    def test_invalid_project_id(self):
        with self.assertRaises(ValueError):
            self.manager.get_project("../outside")


if __name__ == "__main__":
    unittest.main()
