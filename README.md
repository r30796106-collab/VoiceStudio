# VoiceStudio

An independent, open-source-first voice cloning,
text-to-speech and dubbing project.

## Primary Goals
- Hindi and English speech generation
- Consent-based personal voice profiles
- Voice cloning research and implementation
- Independent dubbing workflow
- Offline-first operation
- Android Termux compatibility

## Development Rules
- No paid API dependency by default.
- No cloud GPU dependency.
- Test model compatibility before installation.
- Never use another person's voice without permission.
- Keep AnimeRecapBot integration for a later milestone.

## Current Status
Milestone 1 core foundation has been added on `dev/linux-first`:
- Filesystem settings and directory initialization
- Project-name, project-id, and relative-path validation
- Managed atomic byte-file writes and reads
- Project creation, manifest loading, and listing
- Standard-library unit tests
- GitHub Actions test matrix for Python 3.10–3.14

No speech models or heavyweight ML dependencies are installed by this milestone.
Local and CI test results are pending; this is not yet a completed TTS or voice-cloning application.
