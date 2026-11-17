import hashlib
import wave

import pytest

from voice_studio.audio import inspect_wav, sha256_file


def write_wav(path, *, channels=1, rate=22050, frames=2205, sample_width=2):
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(sample_width)
        audio.setframerate(rate)
        audio.writeframes(b"\x00" * frames * channels * sample_width)
    return path


def test_inspect_wav_and_streaming_hash(tmp_path):
    path = write_wav(tmp_path / "sample.wav")
    info = inspect_wav(path)
    assert info.sample_rate == 22050
    assert info.channels == 1
    assert info.frames == 2205
    assert info.duration_seconds == pytest.approx(0.1)
    assert sha256_file(path) == hashlib.sha256(path.read_bytes()).hexdigest()


def test_inspect_wav_rejects_empty_unsupported_and_oversized_files(tmp_path):
    empty = tmp_path / "empty.wav"
    write_wav(empty, frames=0)
    with pytest.raises(ValueError, match="no audio frames"):
        inspect_wav(empty)
    stereo_three = tmp_path / "three-channel.wav"
    write_wav(stereo_three, channels=3)
    with pytest.raises(ValueError, match="mono or stereo"):
        inspect_wav(stereo_three)
    normal = write_wav(tmp_path / "normal.wav")
    with pytest.raises(ValueError, match="size limit"):
        inspect_wav(normal, max_file_bytes=10)


def test_inspect_wav_enforces_duration_and_sample_rate(tmp_path):
    long_audio = write_wav(tmp_path / "long.wav", rate=8000, frames=16000)
    with pytest.raises(ValueError, match="duration limit"):
        inspect_wav(long_audio, max_duration_seconds=1)
    high_rate = write_wav(tmp_path / "high-rate.wav", rate=192000)
    with pytest.raises(ValueError, match="sample rate"):
        inspect_wav(high_rate)


def test_audio_helpers_reject_symlinks_and_invalid_limits(tmp_path):
    real = write_wav(tmp_path / "real.wav")
    alias = tmp_path / "alias.wav"
    alias.symlink_to(real)
    with pytest.raises(ValueError, match="symlink"):
        inspect_wav(alias)
    with pytest.raises(ValueError, match="symlink"):
        sha256_file(alias)
    with pytest.raises(ValueError, match="max_file_bytes"):
        sha256_file(real, max_file_bytes=0)
    with pytest.raises(ValueError, match="max_duration_seconds"):
        inspect_wav(real, max_duration_seconds=float("nan"))
