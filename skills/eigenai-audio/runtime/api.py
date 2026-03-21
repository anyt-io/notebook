"""EigenAI API interaction: TTS generation, ASR transcription, voice upload, and streaming."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import (
    API_URL,
    AUDIO_MIME_TYPES,
    REQUEST_TIMEOUT,
    SUPPORTED_AUDIO_EXTENSIONS,
    UPLOAD_TIMEOUT,
    UPLOAD_URL,
    WS_URL,
    ApiError,
    OutputError,
    ValidationError,
)


def validate_audio_file(path: Path) -> None:
    """Validate an audio file for transcription. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Audio file not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))})"
        )


def validate_voice_file(path: Path) -> None:
    """Validate a voice reference file. Raises ValidationError if invalid."""
    if not path.exists():
        raise ValidationError(f"Voice reference file not found: {path}")
    if not path.is_file():
        raise ValidationError(f"Not a file: {path}")
    valid_exts = {".wav", ".mp3", ".m4a", ".ogg"}
    if path.suffix.lower() not in valid_exts:
        raise ValidationError(
            f"Unsupported voice file format '{path.suffix}': {path} (supported: {', '.join(sorted(valid_exts))})"
        )


def generate_tts(
    api_key: str,
    text: str,
    model: str = "higgs2p5",
    voice: str | None = None,
    voice_file: Path | None = None,
    voice_id: str | None = None,
    voice_url: str | None = None,
    speed: float | None = None,
    # ChatterBox-specific
    language_id: str | None = None,
    exaggeration: float | None = None,
    temperature: float | None = None,
    diffusion_steps: int | None = None,
    seed: int | None = None,
    # Qwen3-specific
    language: str | None = None,
    instructions: str | None = None,
    response_format: str | None = None,
) -> bytes:
    """Generate speech from text using the EigenAI API. Returns audio bytes."""
    headers = {"Authorization": f"Bearer {api_key}"}
    data: dict[str, str] = {"model": model, "text": text}
    files: dict[str, tuple[str, bytes, str]] = {}

    # Voice selection
    if voice:
        data["voice"] = voice
    if voice_id:
        data["voice_id"] = voice_id
    if voice_url:
        data["voice_url"] = voice_url

    # Voice settings (speed)
    if speed is not None:
        data["voice_settings"] = json.dumps({"speed": speed})

    # Model-specific parameters
    if model == "chatterbox":
        if language_id:
            data["language_id"] = language_id
        if exaggeration is not None:
            data["exaggeration"] = str(exaggeration)
        if temperature is not None:
            data["temperature"] = str(temperature)
        if diffusion_steps is not None:
            data["diffusion_steps"] = str(diffusion_steps)
        if seed is not None:
            data["seed"] = str(seed)
        # Voice file for ChatterBox uses audio_prompt_file
        if voice_file:
            validate_voice_file(voice_file)
            mime = AUDIO_MIME_TYPES.get(voice_file.suffix.lower(), "audio/wav")
            files = {"audio_prompt_file": (voice_file.name, voice_file.read_bytes(), mime)}
    elif model == "qwen3-tts":
        if language:
            data["language"] = language
        if instructions:
            data["instructions"] = instructions
        if response_format:
            data["response_format"] = response_format
        # Voice file for Qwen3 not directly supported; use voice_url or voice_id
    else:
        # Higgs Audio V2.5
        if voice_file:
            validate_voice_file(voice_file)
            mime = AUDIO_MIME_TYPES.get(voice_file.suffix.lower(), "audio/wav")
            files = {"voice_reference_file": (voice_file.name, voice_file.read_bytes(), mime)}

    # Build multipart fields: text fields as (None, value), file fields as (name, bytes, mime)
    multipart: dict[str, Any] = {}
    for key, value in data.items():
        multipart[key] = (None, value)
    if files:
        multipart.update(files)

    try:
        response = requests.post(API_URL, headers=headers, files=multipart, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ApiError(f"TTS API call failed: {e}") from e

    return response.content


def transcribe(
    api_key: str,
    audio_path: Path,
    model: str = "whisper_v3_turbo",
    language: str = "en",
    response_format: str = "json",
) -> str:
    """Transcribe an audio file using the EigenAI API. Returns response text."""
    validate_audio_file(audio_path)

    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": model,
        "language": language,
        "response_format": response_format,
    }
    mime = AUDIO_MIME_TYPES.get(audio_path.suffix.lower(), "audio/mpeg")

    # Build multipart fields
    multipart: dict[str, Any] = {}
    for key, value in data.items():
        multipart[key] = (None, value)

    try:
        with open(audio_path, "rb") as f:
            multipart["file"] = (audio_path.name, f, mime)
            response = requests.post(API_URL, headers=headers, files=multipart, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
    except requests.RequestException as e:
        raise ApiError(f"Transcription API call failed: {e}") from e

    if response_format == "json":
        try:
            return json.dumps(response.json(), indent=2, ensure_ascii=False)
        except ValueError:
            return response.text
    return response.text


def upload_voice(
    api_key: str,
    voice_file: Path,
    model: str = "higgs2p5",
) -> str:
    """Upload a voice reference file and return the voice_id."""
    validate_voice_file(voice_file)

    headers = {"Authorization": f"Bearer {api_key}"}
    mime = AUDIO_MIME_TYPES.get(voice_file.suffix.lower(), "audio/wav")

    try:
        with open(voice_file, "rb") as f:
            multipart: dict[str, Any] = {
                "model": (None, model),
                "voice_reference_file": (voice_file.name, f, mime),
            }
            response = requests.post(UPLOAD_URL, headers=headers, files=multipart, timeout=UPLOAD_TIMEOUT)
            response.raise_for_status()
    except requests.RequestException as e:
        raise ApiError(f"Voice upload failed: {e}") from e

    try:
        return response.json()["voice_id"]
    except (ValueError, KeyError) as e:
        raise ApiError(f"Unexpected upload response: {response.text}") from e


def stream_tts(
    api_key: str,
    text: str,
    model: str = "higgs2p5",
    voice: str | None = None,
    voice_id: str | None = None,
    voice_url: str | None = None,
    voice_settings: dict[str, float] | None = None,
    # ChatterBox-specific
    language_id: str | None = None,
    exaggeration: float | None = None,
    temperature: float | None = None,
    # Qwen3-specific
    language: str | None = None,
    instructions: str | None = None,
) -> bytes:
    """Stream TTS over WebSocket connection. Returns collected PCM audio bytes (16-bit, 24kHz, mono)."""
    try:
        import websockets
    except ImportError:
        raise ApiError("websockets package required for streaming. Install with: uv add websockets") from None

    async def _stream() -> bytes:
        async with websockets.connect(WS_URL) as ws:
            # Authenticate
            await ws.send(json.dumps({"token": api_key, "model": model}))

            # Build TTS request
            request: dict[str, Any] = {"text": text}
            if voice:
                request["voice"] = voice
            if voice_id:
                request["voice_id"] = voice_id
            if voice_url:
                request["voice_url"] = voice_url
            if voice_settings:
                request["voice_settings"] = voice_settings
            if language_id:
                request["language_id"] = language_id
            if exaggeration is not None:
                request["exaggeration"] = exaggeration
            if temperature is not None:
                request["temperature"] = temperature
            if language:
                request["language"] = language
            if instructions:
                request["instructions"] = instructions

            await ws.send(json.dumps(request))

            # Collect audio chunks
            chunks: list[bytes] = []
            async for message in ws:
                if isinstance(message, bytes):
                    chunks.append(message)
                else:
                    data = json.loads(message)
                    if data.get("type") == "complete":
                        break
            return b"".join(chunks)

    try:
        return asyncio.run(_stream())
    except Exception as e:
        if isinstance(e, ApiError):
            raise
        raise ApiError(f"WebSocket streaming failed: {e}") from e


def save_audio(audio_data: bytes, output_dir: Path, fmt: str = "wav") -> Path:
    """Save audio data to the output directory. Returns the saved file path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"eigenai_{timestamp}.{fmt}"
    path = output_dir / filename

    try:
        path.write_bytes(audio_data)
    except OSError as e:
        raise OutputError(f"Failed to save audio: {e}") from e

    return path
