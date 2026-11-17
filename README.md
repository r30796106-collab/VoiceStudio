# VoiceStudio

An independent, open-source-first voice cloning, text-to-speech and dubbing project for Android/Termux.

## Primary goals

- Hindi and English speech generation.
- Consent-based personal voice profiles.
- Voice cloning and independent dubbing workflows.
- Offline-first operation with no paid API or cloud GPU requirement by default.
- Android ARM64 / Termux compatibility.

## Safety and privacy

- Voice profile creation requires an explicit, timezone-stamped consent record.
- Consent is scoped to TTS, voice cloning and/or dubbing operations.
- Do not clone or synthesize another person's voice without their explicit permission.
- Personal voice profiles, source recordings, generated audio and model weights are local-only and excluded from Git.
- No model is downloaded or executed by the current core foundation.

## Current implementation

- consent.py: strict consent schema and validation.
- profiles.py: local metadata store with owner-only file permissions and safe profile IDs.
- text.py: Unicode-normalized Hindi/English text preparation, language hints and sentence segmentation.
- audio.py: bounded PCM WAV inspection and streaming SHA-256 hashing before audio is passed to a model.
- Python 3.12–3.14 CI and automated tests.

## Setup

Run from the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

On Termux, use the Python environment available for the device. The current foundation has no mandatory third-party runtime dependencies.

## Example: create a consented profile metadata record

```python
from voice_studio import VoiceConsent, VoiceProfileStore

consent = VoiceConsent(
    consent_id="consent-001",
    voice_owner="self",
    consent_granted=True,
    consent_recorded_at="2026-11-17T10:00:00+05:30",
    consent_method="self_attested",
    source_audio_sha256="a" * 64,
    scopes=("tts", "voice_cloning"),
)
store = VoiceProfileStore("voice_profiles")
store.create_profile("my-voice", consent)
```

This stores consent metadata only; it does not ingest audio or run a voice model.

## Next milestones

1. Audio inspection and format validation using Python standard-library WAV support.
2. TTS backend interface and small-model compatibility benchmarks on Android ARM64.
3. Consent-gated voice-cloning adapter after model licensing, memory use and quality are verified.
4. Dubbing timeline, synchronization and export.
5. Offline integration and end-to-end Termux testing.

See docs/ARCHITECTURE.md for module boundaries and constraints.
