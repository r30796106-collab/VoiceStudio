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

- Dependency-free workspace and WAV metadata utilities are implemented.
- Hindi/English Unicode text normalization and bounded speech segmentation are available.
- Optional local eSpeak NG WAV synthesis is available through `EspeakNGBackend`.

## Local speech synthesis (optional)

Install eSpeak NG using your trusted operating-system package manager. The Python package does not install native binaries or download models. Example:

```python
from voice_studio import EspeakNGBackend, inspect_wav

output = EspeakNGBackend().synthesize(
    "नमस्ते दुनिया", "outputs/hello.wav", language="hi"
)
print(inspect_wav(output).duration_seconds)
```

The backend runs locally, uses no shell, and supports the `en` and `hi` voice identifiers. Available voice quality and language data depend on the installed eSpeak NG build. This is lightweight baseline TTS, not neural voice cloning.

Run tests with `python -m pytest`.
