import subprocess
from pathlib import Path

import pytest

from voice_studio.speech import EspeakNGBackend, SpeechEngineError


def test_synthesize_invokes_espeak_without_a_shell(monkeypatch, tmp_path):
    calls = {}

    def fake_run(args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        Path(args[args.index("-w") + 1]).write_bytes(b"RIFF-test")
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    target = tmp_path / "nested" / "hello.wav"
    result = EspeakNGBackend(rate=170).synthesize(
        "  Hello   world! ", target, language="en"
    )
    assert result == target
    assert target.read_bytes() == b"RIFF-test"
    assert calls["args"][:4] == ["espeak-ng", "-v", "en", "-s"]
    assert calls["kwargs"]["check"] is True
    assert calls["kwargs"]["timeout"] == 60
    assert "shell" not in calls["kwargs"]


def test_rejects_empty_text_unknown_language_and_non_wav(tmp_path):
    engine = EspeakNGBackend()
    with pytest.raises(ValueError, match="empty"):
        engine.synthesize("  ", tmp_path / "x.wav")
    with pytest.raises(ValueError, match="language"):
        engine.synthesize("hello", tmp_path / "x.wav", language="fr")
    with pytest.raises(ValueError, match="wav"):
        engine.synthesize("hello", tmp_path / "x.mp3")


def test_reports_missing_espeak_binary(monkeypatch, tmp_path):
    def missing(*args, **kwargs):
        raise FileNotFoundError("espeak-ng")

    monkeypatch.setattr(subprocess, "run", missing)
    with pytest.raises(SpeechEngineError, match="not installed"):
        EspeakNGBackend().synthesize("hello", tmp_path / "x.wav")


def test_reports_synthesis_timeout(monkeypatch, tmp_path):
    def timeout(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(SpeechEngineError, match="timed out"):
        EspeakNGBackend().synthesize("hello", tmp_path / "x.wav")


@pytest.mark.parametrize("rate", [True, 0, 451, 100.5])
def test_rejects_invalid_speech_rate(rate):
    with pytest.raises(ValueError):
        EspeakNGBackend(rate=rate)
