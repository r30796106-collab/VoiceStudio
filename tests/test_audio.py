import tempfile
import unittest
import wave
from pathlib import Path

from src.voice_studio.audio import inspect_wav


class TestAudioInspection(unittest.TestCase):
    def test_reads_pcm_wav_metadata_without_loading_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.wav"
            with wave.open(str(path), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(16000)
                output.writeframes(bytes(2) * 16000)
            info = inspect_wav(path)
            self.assertEqual(info.channels, 1)
            self.assertEqual(info.sample_width_bytes, 2)
            self.assertEqual(info.sample_rate_hz, 16000)
            self.assertEqual(info.frame_count, 16000)
            self.assertAlmostEqual(info.duration_seconds, 1.0)

    def test_rejects_invalid_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.wav"
            path.write_text("not a wave", encoding="utf-8")
            with self.assertRaises(ValueError):
                inspect_wav(path)

    def test_missing_file_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                inspect_wav(Path(tmp) / "missing.wav")


if __name__ == "__main__":
    unittest.main()
