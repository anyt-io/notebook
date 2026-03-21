---
name: eigenai-audio
description: Generate speech and transcribe audio using EigenAI API. Use when user wants to convert text to speech, clone voices, transcribe audio files, stream real-time audio, upload voice references, or generate multilingual audio. Supports TTS with Higgs Audio V2.5, ChatterBox, and Qwen3 TTS models, ASR with Whisper V3 Turbo, WebSocket streaming, and voice upload.
---

# EigenAI Audio

Generate speech from text and transcribe audio using the EigenAI Model API.

## Prerequisites

- `uv` (Python package manager)
- `EIGENAI_API_KEY` environment variable set with a valid EigenAI API key

## EigenAI Audio API Guidelines

**Authoritative references:**
- https://docs.eigenai.com/products/model-api/api-reference/generate-audio
- https://docs.eigenai.com/products/model-api/api-reference/stream-audio
- https://docs.eigenai.com/products/model-api/api-reference/upload-voice

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `https://api-web.eigenai.com/api/v1/generate` | POST | TTS generation and ASR transcription |
| `https://api-web.eigenai.com/api/v1/generate/upload` | POST | Upload voice reference files |
| `wss://api-web.eigenai.com/api/v1/generate/ws` | WebSocket | Real-time streaming TTS |

**Content-Type:** `multipart/form-data` (REST endpoints)

**Authentication:** `Authorization: Bearer YOUR_API_KEY` (REST) or `{"token": "YOUR_API_KEY"}` (WebSocket)

### Available Models

| Model | ID | Type | Best For |
|---|---|---|---|
| Whisper V3 Turbo | `whisper_v3_turbo` | ASR | Fast audio transcription, 99 languages |
| Higgs ASR 3 | `higgs_asr_3` | ASR | Detailed transcription with timing metadata |
| Higgs Audio V2.5 | `higgs2p5` | TTS | High-quality speech synthesis, voice cloning |
| ChatterBox Voice Twin | `chatterbox` | TTS | Expressive voice cloning, fine-grained control |
| Qwen3 TTS | `qwen3-tts` | TTS | Multilingual TTS, style/emotion control, multiple output formats |

### TTS Parameters (Higgs Audio V2.5)

| Parameter | Type | Required | Details |
|---|---|---|---|
| `model` | string | Yes | `higgs2p5` |
| `text` | string | Yes | Text to synthesize |
| `voice` | string | No | Preset voice (e.g., `Linda`, `Jack`) |
| `voice_reference_file` | file | No | Voice cloning sample (WAV, MP3) |
| `voice_id` | string | No | Stored voice ID |
| `voice_url` | string | No | External voice reference URL |
| `voice_name` | string | No | Saved voice library name |
| `voice_settings` | string | No | JSON with `speed` (default `1.0`) |
| `sampling` | string | No | JSON: `temperature` (1.0), `top_p` (0.95), `top_k` (50) |
| `stream` | boolean | No | `true` for SSE streaming; `false` returns WAV file |

### TTS Parameters (ChatterBox)

| Parameter | Type | Required | Details |
|---|---|---|---|
| `model` | string | Yes | `chatterbox` |
| `text` | string | Yes | Max 1,000 characters recommended |
| `language_id` | string | No | Language code; 23 languages (default: `en`) |
| `audio_prompt_file` | file | No | Voice reference (WAV/MP3/M4A/OGG, max 30s) |
| `voice_id` | string | No | Stored voice ID |
| `exaggeration` | number | No | Expressiveness 0.0-1.0+ (default: 0.5) |
| `temperature` | number | No | Sampling temperature (default: 0.8) |
| `diffusion_steps` | number | No | Quality/latency trade-off (default: 5) |
| `seed` | integer | No | Reproducibility seed (null = random) |
| `stream` | boolean | No | Streaming option |

### TTS Parameters (Qwen3 TTS)

| Parameter | Type | Required | Details |
|---|---|---|---|
| `model` | string | Yes | `qwen3-tts` |
| `text` | string | Yes | Text to synthesize |
| `voice` | string | No | Named speakers: Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee |
| `voice_id` | string | No | Stored voice ID |
| `voice_url` | string | No | External voice reference URL |
| `voice_settings` | string | No | JSON with `speed` (default: 1.0) |
| `language` | string | No | Auto, Chinese, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish |
| `instructions` | string | No | Style/emotion control text |
| `response_format` | string | No | `wav`, `pcm`, `mp3`, `flac`, `aac`, `opus` (default: wav) |
| `stream` | boolean | No | Streaming option |

### ASR Parameters (Whisper V3 Turbo)

| Parameter | Type | Required | Details |
|---|---|---|---|
| `model` | string | Yes | `whisper_v3_turbo` |
| `file` | file | Yes | Audio file (MP3, WAV, M4A, OGG, WebM) |
| `language` | string | No | Language code; 99 languages (default: `en`) |
| `response_format` | string | No | `json` or `text` |

### Upload Voice Parameters

| Parameter | Type | Required | Details |
|---|---|---|---|
| `model` | string | Yes | TTS model: `higgs2p5`, `chatterbox`, or `qwen3-tts` |
| `voice_reference_file` | file | Yes | Voice reference audio (WAV or MP3 recommended) |

**Response:** `{"voice_id": "abc123..."}` — use this `voice_id` in subsequent TTS requests.

### Stream Audio (WebSocket) Parameters

Send after WebSocket authentication (`{"token": "API_KEY", "model": "MODEL"}`):

| Parameter | Type | Required | Details |
|---|---|---|---|
| `text` | string | Yes | Text to synthesize |
| `voice` | string | No | Voice selection (higgs2p5, qwen3-tts) |
| `voice_id` | string | No | Stored voice ID (all models) |
| `voice_url` | string | No | Custom voice URL (higgs2p5, qwen3-tts) |
| `voice_settings` | object | No | Voice config with `speed` (higgs2p5, qwen3-tts) |
| `language_id` | string | No | Language code (chatterbox) |
| `exaggeration` | number | No | Expression intensity (chatterbox) |
| `temperature` | number | No | Response variability (chatterbox) |
| `language` | string | No | Language selection (qwen3-tts) |
| `instructions` | string | No | Synthesis directives (qwen3-tts) |

**Response:** Binary PCM audio chunks (16-bit, 24kHz, mono), then `{"type": "complete"}` JSON.

### Response Format

- **TTS (non-streaming):** Binary audio file (WAV by default; Qwen3 supports wav, pcm, mp3, flac, aac, opus)
- **TTS (streaming WebSocket):** Raw PCM audio chunks (16-bit, 24kHz, mono)
- **ASR:** JSON with transcription text, or plain text
- **Upload:** JSON with `voice_id`

### Python Usage

```python
import requests

url = "https://api-web.eigenai.com/api/v1/generate"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Text-to-speech
data = {"model": "higgs2p5", "text": "Hello world", "voice": "Linda"}
response = requests.post(url, headers=headers, data=data, timeout=120)
with open("speech.wav", "wb") as f:
    f.write(response.content)

# Transcription
with open("audio.mp3", "rb") as audio:
    response = requests.post(
        url, headers=headers,
        data={"model": "whisper_v3_turbo", "language": "en", "response_format": "json"},
        files={"file": ("audio.mp3", audio, "audio/mpeg")},
        timeout=120,
    )
print(response.json())

# Upload voice reference
upload_url = "https://api-web.eigenai.com/api/v1/generate/upload"
with open("reference.wav", "rb") as f:
    response = requests.post(
        upload_url, headers=headers,
        data={"model": "higgs2p5"},
        files={"voice_reference_file": ("reference.wav", f, "audio/wav")},
        timeout=60,
    )
voice_id = response.json()["voice_id"]

# WebSocket streaming
import asyncio, websockets, json
async def stream():
    async with websockets.connect("wss://api-web.eigenai.com/api/v1/generate/ws") as ws:
        await ws.send(json.dumps({"token": "YOUR_API_KEY", "model": "higgs2p5"}))
        await ws.send(json.dumps({"text": "Hello streaming!", "voice": "Linda"}))
        with open("output.pcm", "wb") as f:
            async for msg in ws:
                if isinstance(msg, bytes):
                    f.write(msg)
                elif json.loads(msg).get("type") == "complete":
                    break
asyncio.run(stream())
```

### Capabilities

- **Text-to-speech:** Convert text to natural-sounding speech with multiple voice options.
- **Voice cloning:** Clone voices from reference audio files or stored voice IDs.
- **Voice upload:** Upload voice references to get reusable voice IDs.
- **Real-time streaming:** Stream TTS over WebSocket for low-latency audio output.
- **Multilingual:** Support for dozens of languages across all models.
- **Audio transcription:** Transcribe audio files to text in 99 languages.
- **Style control:** Adjust expressiveness, speed, temperature, and emotion (model-dependent).
- **Multiple output formats:** WAV, MP3, FLAC, AAC, Opus, PCM (Qwen3 TTS).

### Limitations

- Requires a valid `EIGENAI_API_KEY` environment variable.
- ChatterBox text input should be under 1,000 characters for best results.
- Voice reference files for ChatterBox should be under 30 seconds.
- WebSocket streaming outputs raw PCM (16-bit, 24kHz, mono) — convert with ffmpeg if needed.

## Usage

Run from the skill folder (`skills/eigenai-audio/`):

### Text-to-speech with Higgs Audio

```bash
uv run --project runtime runtime/generate_audio.py tts "Hello, this is a test of the text-to-speech system."
```

### Choose a voice preset

```bash
uv run --project runtime runtime/generate_audio.py tts "Good morning!" --voice Linda
```

### Voice cloning from a reference file

```bash
uv run --project runtime runtime/generate_audio.py tts "Clone my voice" --voice-file path/to/reference.wav
```

### Use ChatterBox model with expressiveness control

```bash
uv run --project runtime runtime/generate_audio.py tts "Very expressive speech" --model chatterbox --exaggeration 0.8
```

### Use Qwen3 TTS with style instructions

```bash
uv run --project runtime runtime/generate_audio.py tts "Breaking news from Tokyo" --model qwen3-tts --language Japanese --instructions "news anchor style, authoritative tone"
```

### Choose output format (Qwen3 TTS)

```bash
uv run --project runtime runtime/generate_audio.py tts "Hello world" --model qwen3-tts --response-format mp3
```

### Transcribe an audio file

```bash
uv run --project runtime runtime/generate_audio.py transcribe path/to/audio.mp3
```

### Transcribe with language hint

```bash
uv run --project runtime runtime/generate_audio.py transcribe path/to/audio.mp3 --language ja
```

### Transcribe with Higgs ASR 3

```bash
uv run --project runtime runtime/generate_audio.py transcribe path/to/audio.wav --model higgs_asr_3
```

### Upload a voice reference

```bash
uv run --project runtime runtime/generate_audio.py upload path/to/reference.wav
```

### Upload voice for a specific model

```bash
uv run --project runtime runtime/generate_audio.py upload path/to/reference.wav --model chatterbox
```

### Use uploaded voice_id for TTS

```bash
uv run --project runtime runtime/generate_audio.py tts "Hello with my cloned voice" --voice-id abc123def456
```

### Stream TTS over WebSocket

```bash
uv run --project runtime runtime/generate_audio.py stream "Real-time streaming audio" --voice Linda
```

### Stream with a different model

```bash
uv run --project runtime runtime/generate_audio.py stream "Expressive streaming" --model chatterbox --exaggeration 0.7
```

### Specify output directory

```bash
uv run --project runtime runtime/generate_audio.py tts "A test" -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- TTS output filenames: `eigenai_YYYYMMDD_HHMMSS.wav` (or appropriate extension for Qwen3 formats).
- Stream output filenames: `eigenai_YYYYMMDD_HHMMSS.pcm` (raw PCM, 16-bit, 24kHz, mono).
- Transcription results are printed to stdout as JSON or plain text.
- Upload results print the `voice_id` to stdout.
