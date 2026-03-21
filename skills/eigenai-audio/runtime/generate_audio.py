#!/usr/bin/env python3
"""
Generate speech or transcribe audio using the EigenAI API.
Run with: uv run --project runtime runtime/generate_audio.py <command> [options]

Requires EIGENAI_API_KEY environment variable.
"""

import argparse
import sys
import time
from pathlib import Path

from api import generate_tts, save_audio, stream_tts, transcribe, upload_voice
from config import (
    AVAILABLE_ASR_MODELS,
    AVAILABLE_TTS_MODELS,
    DEFAULT_ASR_MODEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TTS_MODEL,
    QWEN3_LANGUAGES,
    QWEN3_RESPONSE_FORMATS,
    ApiError,
    ConfigError,
    EigenAIAudioError,
    OutputError,
    ValidationError,
    get_api_key,
)

_ERROR_PREFIXES: dict[type[EigenAIAudioError], str] = {
    ConfigError: "Configuration error",
    ValidationError: "Validation error",
    ApiError: "API error",
    OutputError: "Output error",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate speech or transcribe audio using the EigenAI API")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")

    # --- TTS subcommand ---
    tts_parser = subparsers.add_parser("tts", help="Text-to-speech synthesis")
    tts_parser.add_argument("text", help="Text to synthesize into speech")
    tts_parser.add_argument(
        "--model",
        default=DEFAULT_TTS_MODEL,
        choices=AVAILABLE_TTS_MODELS,
        help=f"TTS model to use (default: {DEFAULT_TTS_MODEL})",
    )
    tts_parser.add_argument("--voice", help="Preset voice name (e.g., Linda, Jack)")
    tts_parser.add_argument("--voice-file", help="Path to voice reference audio file for cloning")
    tts_parser.add_argument("--voice-id", help="Stored voice ID")
    tts_parser.add_argument("--voice-url", help="External voice reference URL")
    tts_parser.add_argument("--speed", type=float, help="Speech speed (default: 1.0)")
    # ChatterBox-specific
    tts_parser.add_argument("--language-id", help="Language code for ChatterBox (default: en)")
    tts_parser.add_argument("--exaggeration", type=float, help="Expressiveness for ChatterBox (0.0-1.0+, default: 0.5)")
    tts_parser.add_argument("--temperature", type=float, help="Sampling temperature for ChatterBox (default: 0.8)")
    tts_parser.add_argument("--diffusion-steps", type=int, help="Quality/latency trade-off for ChatterBox (default: 5)")
    tts_parser.add_argument("--seed", type=int, help="Reproducibility seed for ChatterBox")
    # Qwen3-specific
    tts_parser.add_argument("--language", choices=QWEN3_LANGUAGES, help="Language for Qwen3 TTS")
    tts_parser.add_argument("--instructions", help="Style/emotion instructions for Qwen3 TTS")
    tts_parser.add_argument(
        "--response-format",
        choices=QWEN3_RESPONSE_FORMATS,
        help="Output format for Qwen3 TTS (default: wav)",
    )
    tts_parser.add_argument(
        "-o", "--output", default=str(DEFAULT_OUTPUT_DIR), help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    # --- Transcribe subcommand ---
    asr_parser = subparsers.add_parser("transcribe", help="Transcribe audio to text")
    asr_parser.add_argument("file", help="Path to audio file to transcribe")
    asr_parser.add_argument(
        "--model",
        default=DEFAULT_ASR_MODEL,
        choices=AVAILABLE_ASR_MODELS,
        help=f"ASR model to use (default: {DEFAULT_ASR_MODEL})",
    )
    asr_parser.add_argument("--language", default="en", help="Language code (default: en)")
    asr_parser.add_argument(
        "--response-format",
        default="json",
        choices=["json", "text"],
        help="Response format (default: json)",
    )

    # --- Upload voice subcommand ---
    upload_parser = subparsers.add_parser("upload", help="Upload a voice reference file to get a voice_id")
    upload_parser.add_argument("file", help="Path to voice reference audio file (WAV or MP3)")
    upload_parser.add_argument(
        "--model",
        default=DEFAULT_TTS_MODEL,
        choices=AVAILABLE_TTS_MODELS,
        help=f"TTS model to associate with (default: {DEFAULT_TTS_MODEL})",
    )

    # --- Stream TTS subcommand ---
    stream_parser = subparsers.add_parser("stream", help="Stream TTS over WebSocket (outputs PCM)")
    stream_parser.add_argument("text", help="Text to synthesize into speech")
    stream_parser.add_argument(
        "--model",
        default=DEFAULT_TTS_MODEL,
        choices=AVAILABLE_TTS_MODELS,
        help=f"TTS model to use (default: {DEFAULT_TTS_MODEL})",
    )
    stream_parser.add_argument("--voice", help="Preset voice name (e.g., Linda, Jack)")
    stream_parser.add_argument("--voice-id", help="Stored voice ID")
    stream_parser.add_argument("--voice-url", help="External voice reference URL")
    stream_parser.add_argument("--speed", type=float, help="Speech speed (default: 1.0)")
    # ChatterBox-specific
    stream_parser.add_argument("--language-id", help="Language code for ChatterBox (default: en)")
    stream_parser.add_argument("--exaggeration", type=float, help="Expressiveness for ChatterBox (0.0-1.0+)")
    stream_parser.add_argument("--temperature", type=float, help="Sampling temperature for ChatterBox")
    # Qwen3-specific
    stream_parser.add_argument("--language", choices=QWEN3_LANGUAGES, help="Language for Qwen3 TTS")
    stream_parser.add_argument("--instructions", help="Style/emotion instructions for Qwen3 TTS")
    stream_parser.add_argument(
        "-o", "--output", default=str(DEFAULT_OUTPUT_DIR), help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    try:
        # Check configuration
        api_key = get_api_key()
        if not api_key:
            raise ConfigError(
                "EIGENAI_API_KEY environment variable is not set.\n  Set it with: export EIGENAI_API_KEY=your_api_key"
            )

        if args.command == "tts":
            return _handle_tts(api_key, args)
        elif args.command == "transcribe":
            return _handle_transcribe(api_key, args)
        elif args.command == "upload":
            return _handle_upload(api_key, args)
        else:
            return _handle_stream(api_key, args)

    except EigenAIAudioError as e:
        prefix = _ERROR_PREFIXES.get(type(e), "Error")
        print(f"\n{prefix}: {e}", file=sys.stderr)
        return 1


def _handle_tts(api_key: str, args: argparse.Namespace) -> int:
    """Handle the TTS subcommand."""
    voice_file = Path(args.voice_file) if args.voice_file else None
    fmt = args.response_format or "wav"

    # Print summary
    print(f"Model: {args.model}")
    print(f"Text: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    if args.voice:
        print(f"Voice: {args.voice}")
    if voice_file:
        print(f"Voice file: {voice_file}")
    if args.voice_id:
        print(f"Voice ID: {args.voice_id}")
    if args.speed is not None:
        print(f"Speed: {args.speed}")
    if args.model == "chatterbox":
        if args.exaggeration is not None:
            print(f"Exaggeration: {args.exaggeration}")
        if args.temperature is not None:
            print(f"Temperature: {args.temperature}")
        if args.diffusion_steps is not None:
            print(f"Diffusion steps: {args.diffusion_steps}")
        if args.seed is not None:
            print(f"Seed: {args.seed}")
    if args.model == "qwen3-tts":
        if args.language:
            print(f"Language: {args.language}")
        if args.instructions:
            print(f"Instructions: {args.instructions}")
        if args.response_format:
            print(f"Format: {args.response_format}")
    print(f"Output: {args.output}\n")

    # Generate
    start = time.time()
    audio_data = generate_tts(
        api_key=api_key,
        text=args.text,
        model=args.model,
        voice=args.voice,
        voice_file=voice_file,
        voice_id=args.voice_id,
        voice_url=args.voice_url,
        speed=args.speed,
        language_id=args.language_id,
        exaggeration=args.exaggeration,
        temperature=args.temperature,
        diffusion_steps=args.diffusion_steps,
        seed=args.seed,
        language=args.language,
        instructions=args.instructions,
        response_format=args.response_format,
    )
    elapsed = time.time() - start
    print(f"TTS generation took {elapsed:.2f}s ({len(audio_data)} bytes)")

    # Save
    output_dir = Path(args.output)
    saved_path = save_audio(audio_data, output_dir, fmt=fmt)
    print(f"Done! Audio saved to: {saved_path}")
    return 0


def _handle_transcribe(api_key: str, args: argparse.Namespace) -> int:
    """Handle the transcribe subcommand."""
    audio_path = Path(args.file)

    # Print summary
    print(f"Model: {args.model}")
    print(f"File: {audio_path}")
    print(f"Language: {args.language}")
    print(f"Format: {args.response_format}\n")

    # Transcribe
    start = time.time()
    result = transcribe(
        api_key=api_key,
        audio_path=audio_path,
        model=args.model,
        language=args.language,
        response_format=args.response_format,
    )
    elapsed = time.time() - start
    print(f"Transcription took {elapsed:.2f}s")

    print("\nTranscription result:")
    print(result)
    return 0


def _handle_upload(api_key: str, args: argparse.Namespace) -> int:
    """Handle the upload subcommand."""
    voice_path = Path(args.file)

    print(f"File: {voice_path}")
    print(f"Model: {args.model}\n")

    start = time.time()
    voice_id = upload_voice(api_key=api_key, voice_file=voice_path, model=args.model)
    elapsed = time.time() - start

    print(f"Upload took {elapsed:.2f}s")
    print(f"Voice ID: {voice_id}")
    print(f"\nUse this voice_id in TTS requests with: --voice-id {voice_id}")
    return 0


def _handle_stream(api_key: str, args: argparse.Namespace) -> int:
    """Handle the stream subcommand."""
    voice_settings = None
    if args.speed is not None:
        voice_settings = {"speed": args.speed}

    print(f"Model: {args.model}")
    print(f"Text: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    if args.voice:
        print(f"Voice: {args.voice}")
    if args.voice_id:
        print(f"Voice ID: {args.voice_id}")
    print(f"Output: {args.output}\n")

    start = time.time()
    audio_data = stream_tts(
        api_key=api_key,
        text=args.text,
        model=args.model,
        voice=args.voice,
        voice_id=args.voice_id,
        voice_url=args.voice_url,
        voice_settings=voice_settings,
        language_id=getattr(args, "language_id", None),
        exaggeration=args.exaggeration,
        temperature=args.temperature,
        language=args.language,
        instructions=args.instructions,
    )
    elapsed = time.time() - start
    print(f"Stream TTS took {elapsed:.2f}s ({len(audio_data)} bytes PCM)")

    output_dir = Path(args.output)
    saved_path = save_audio(audio_data, output_dir, fmt="pcm")
    print(f"Done! PCM audio saved to: {saved_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
