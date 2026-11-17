# VoiceStudio Architecture

## 1. Purpose

Independent Hindi-English voice cloning, TTS and dubbing application designed for Android Termux. Offline-first and open-source model support are priorities; cloud services and paid APIs are not default dependencies.

## 2. Implemented core foundation

### Consent and profiles
- consent.py validates explicit permission, timezone-aware recording time, consent method, source-audio SHA-256 and operation scopes.
- profiles.py stores consent metadata locally, rejects unsafe profile IDs and symlink targets, and uses owner-only file permissions.
- Audio recordings, generated audio, model weights and personal profile metadata are excluded from Git.

### Text and audio preparation
- text.py performs Unicode NFC normalization, bounded input validation, Hindi/English script hints and Hindi/English sentence splitting.
- audio.py validates bounded uncompressed PCM WAV metadata and computes streaming SHA-256 hashes without loading entire recordings into memory.
- No translation, network request or model execution is performed.

## 3. Planned modules

### Core
- Configuration and input validation.
- Project and file management.
- Local job tracking.

### Speech engine
- TTS backend protocol.
- Voice-cloning backend protocol.
- Model compatibility and capability checks.
- Hindi/English text normalization and pronunciation support.

### Dubbing
- Script segmentation.
- Voice assignment.
- Audio generation and synchronization.
- WAV/MP3 export and inspection.

## 4. Operating principles

- Offline-first; no mandatory paid APIs or cloud GPU.
- Model compatibility must be benchmarked before download or installation.
- Termux ARM64 compatibility and low-memory execution are release gates.
- Never use another person's voice without explicit permission.
- Model downloads and package installation require explicit approval.
- Keep the first usable version deterministic and testable.

## 5. Privacy and storage

- Voice recordings remain local by default.
- Personal voice profiles are excluded from Git.
- Generated audio is excluded from Git.
- Model weights are excluded from Git.
- Store consent metadata separately from source audio; retain only the minimum information needed to validate permission.

## 6. Device constraints

- Android ARM64 / Termux.
- Python 3.14 compatibility is included in CI.
- Target device memory is limited; model selection must use measured RAM, storage, latency and audio quality rather than model-size claims alone.

## 7. Runtime and model direction

- First TTS baseline: sherpa-onnx with compact Hindi/English Piper VITS voices.
- Voice cloning remains a separate backend: Pocket TTS Hindi is a research candidate; English cloning needs its own model.
- Model choice is gated on exact license/hash review and real Android ARM64/Termux memory, latency, quality and stability benchmarks.
- See docs/MODEL_SELECTION.md for current evidence and rejected candidates.

## 8. Release sequence

1. Complete lightweight core and audio inspection.
2. Benchmark open-source Hindi/English TTS models on the target device.
3. Select a model only after memory, latency, license and quality checks.
4. Implement consent-gated TTS and voice cloning adapters.
5. Add dubbing synchronization and export.
6. Run end-to-end offline Termux tests.
7. Integrate AnimeRecapBot only after standalone validation.
