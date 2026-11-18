import tempfile
import unittest
from pathlib import Path

from src.voice_studio.core import VoiceStudioPaths, resolve_workspace_path, validate_identifier


class TestVoiceStudioCore(unittest.TestCase):
    def test_identifier_validation(self):
        self.assertEqual(validate_identifier("Hindi_voice-1"), "Hindi_voice-1")
        for value in ("", "../escape", "has space", ".hidden", "a" * 65):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_identifier(value)

    def test_standard_paths_are_workspace_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = VoiceStudioPaths.at(tmp)
            self.assertEqual(paths.models, Path(tmp) / "models")
            self.assertEqual(paths.voice_profiles, Path(tmp) / "voice_profiles")
            self.assertEqual(paths.outputs, Path(tmp) / "outputs")
            self.assertEqual(paths.project_file("demo"), Path(tmp) / "voice_projects/demo/project.json")

    def test_rejects_absolute_and_traversal_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            for value in ("../outside", "a/../../outside", "/tmp/outside", "a\\\\outside"):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    resolve_workspace_path(tmp, value)

    def test_rejects_symlink_components(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root.parent / (root.name + "-outside")
            outside.mkdir()
            self.addCleanup(lambda: outside.rmdir())
            (root / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                resolve_workspace_path(root, "linked/file.txt")


if __name__ == "__main__":
    unittest.main()
