# VoiceStudio Architecture

## 1. Project Purpose
Independent Hindi-English voice cloning, TTS and dubbing
application designed for Android Termux.

## 2. Core Modules

### Core
- Configuration
- Input validation
- Project management
- File management

### Voice Profiles
- Profile creation
- Consent tracking
- Reference audio management
- Profile metadata

### Speech Engine
- Text normalization
- Language detection
- TTS model interface
- Voice cloning model interface

### Dubbing
- Script segmentation
- Voice assignment
- Audio generation
- Audio synchronization

### Audio
- WAV export
- MP3 export
- Audio inspection

## 3. Operating Principles
- Offline-first.
- Open-source models preferred.
- No mandatory paid APIs.
- No mandatory cloud GPU.
- Termux compatibility is a priority.
- Model compatibility must be tested before installation.
- Never clone a person's voice without permission.

## 4. Privacy
- Voice recordings remain local by default.
- Personal voice profiles are excluded from Git.
- Generated audio is excluded from Git.
- Model weights are excluded from Git.

## 5. Development Strategy
1. Build lightweight core modules.
2. Add tests before integrating heavy models.
3. Benchmark memory and storage usage.
4. Select compatible Hindi-English models.
5. Implement independent TTS and dubbing workflows.
6. Integrate with AnimeRecapBot only after standalone testing.

## 6. Current Constraints
- Android ARM64
- Termux
- Python 3.14.8
- Approximately 3.7 GB device RAM
- Offline operation preferred
