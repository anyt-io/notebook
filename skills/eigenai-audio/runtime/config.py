"""Configuration constants and exception hierarchy for the eigenai-audio skill."""

import os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"

API_URL = "https://api-web.eigenai.com/api/v1/generate"
UPLOAD_URL = "https://api-web.eigenai.com/api/v1/generate/upload"
WS_URL = "wss://api-web.eigenai.com/api/v1/generate/ws"
REQUEST_TIMEOUT = 120
UPLOAD_TIMEOUT = 60

# Models
DEFAULT_TTS_MODEL = "higgs2p5"
AVAILABLE_TTS_MODELS = ["higgs2p5", "chatterbox", "qwen3-tts"]
DEFAULT_ASR_MODEL = "whisper_v3_turbo"
AVAILABLE_ASR_MODELS = ["whisper_v3_turbo", "higgs_asr_3"]

# Higgs Audio voices
HIGGS_VOICES = ["Linda", "Jack"]

# Qwen3 TTS voices
QWEN3_VOICES = ["Vivian", "Serena", "Uncle_Fu", "Dylan", "Eric", "Ryan", "Aiden", "Ono_Anna", "Sohee"]

# Qwen3 TTS languages
QWEN3_LANGUAGES = [
    "Auto",
    "Chinese",
    "English",
    "French",
    "German",
    "Italian",
    "Japanese",
    "Korean",
    "Portuguese",
    "Russian",
    "Spanish",
]

# Qwen3 TTS output formats
QWEN3_RESPONSE_FORMATS = ["wav", "pcm", "mp3", "flac", "aac", "opus"]

# ASR supported input formats
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm"}

AUDIO_MIME_TYPES: dict[str, str] = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
}


def get_api_key() -> str | None:
    """Return the EigenAI API key from environment, or None if not set."""
    return os.environ.get("EIGENAI_API_KEY")


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class EigenAIAudioError(Exception):
    """Base exception for eigenai-audio skill errors."""


class ConfigError(EigenAIAudioError):
    """Configuration errors (missing API key, invalid settings)."""


class ValidationError(EigenAIAudioError):
    """Input validation errors (bad file, unsupported format)."""


class ApiError(EigenAIAudioError):
    """API call failures."""


class OutputError(EigenAIAudioError):
    """Output/save failures."""
