# Model and Runtime Selection (Research)

Status: candidates identified; nothing is downloaded, installed or selected for production yet.

## Runtime candidate

### sherpa-onnx

- Upstream: https://github.com/k2-fsa/sherpa-onnx
- License: Apache-2.0.
- Supports offline speech synthesis and Android ARM64/aarch64, with C++, Python and other language APIs.
- Best current runtime candidate for compact ONNX TTS models.
- Termux-specific Python/native binding compatibility still needs a device test; Android support does not automatically prove Termux compatibility.

## Hindi and English baseline TTS

### Piper VITS through sherpa-onnx

The current HayaiTTS voice catalog lists Hindi Piper voices Pratham, Priyamvada and Rohan in 21 MB, 36 MB and 67 MB variants, with MIT listed for these voice packages. It also lists multiple English Piper voices and compact variants.

- Catalog: https://github.com/HayaiApp/HayaiTTS/blob/main/docs/MODELS.md
- Sherpa-ONNX TTS examples: https://github.com/k2-fsa/sherpa-onnx/tree/master/python-api-examples
- Use a small/medium Hindi and English model as the first baseline.
- Recheck the exact voice model card/license and checksum before any download or redistribution; licenses can vary by individual voice.

Piper provides fixed voices, not reference-audio cloning. It is the low-risk TTS baseline, not the complete cloning solution.

## Hindi voice-cloning candidate

### Pocket TTS Hindi (Saryps Labs)

- Model card: https://huggingface.co/saryps-labs/pocket-tts-hindi
- Early research release: 109.5M parameters, 219 MB BF16 weights.
- Weights: CC BY 4.0; upstream Pocket TTS/Mimi components have separate MIT attribution terms.
- Supports Hindi synthesis and prompt-based voice cloning.
- The model card says consumer-laptop and low-power edge benchmarks are pending.

Decision: research candidate only. Do not treat it as Termux-ready until the exact pinned model/runtime is benchmarked on the target Android ARM64 device. The separate community integration at https://github.com/builderAbhishek/pocket-tts-hindi reports Windows CPU tests, not Android/Termux validation.

## English voice-cloning candidate

The HayaiTTS catalog currently lists Pocket reference-audio cloning models for English at 98 MB and 168 MB, and ZipVoice models for English/Chinese starting at 109 MB. The catalog lists Apache-2.0 for these model packages.

- Catalog: https://github.com/HayaiApp/HayaiTTS/blob/main/docs/MODELS.md
- Verify the underlying model card, exact weight hash and license before use.
- Evaluate a small Pocket or ZipVoice model separately from Hindi; do not assume the Hindi checkpoint supports English.

## Candidates not selected

- Meta MMS Hindi TTS: the model card lists CC BY-NC 4.0. Avoid as the default product dependency because of its non-commercial restriction. https://huggingface.co/facebook/mms-tts-hns
- Vani TTS: promising Android/ONNX direction and Apache-2.0 repo metadata, but the current README contains unresolved merge-conflict markers and describes the work as R&D. Do not integrate until upstream is cleaned and a reproducible release exists. https://github.com/vivek-541/vani-tts
- HayaiTTS: useful model-catalog reference, but its application code is GPL-3.0. Reuse model metadata and upstream runtime information, not application code, unless a future license review approves it.

## Required benchmark before choosing a cloning backend

For each candidate, record:

1. Exact model revision, file SHA-256, license and attribution.
2. Download size and peak memory during model load and synthesis.
3. First-audio latency, total synthesis time and real-time factor.
4. Output sample rate, clipping, silence, pronunciation and intelligibility.
5. Hindi/English and code-switching test cases.
6. Repeated-request stability, process restart behavior and battery/thermal impact.
7. Whether the native runtime actually works in Termux on Android ARM64.

No model weights or packages are downloaded by this milestone. Model installation remains an explicit approval step.
