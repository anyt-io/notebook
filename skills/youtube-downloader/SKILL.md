---
name: youtube-downloader
description: Download YouTube videos, transcripts, cover images, and screenshots. Use when the user wants to download a YouTube video, extract audio, get transcripts/subtitles, download cover/thumbnail images, or capture screenshot frames at specific timestamps without downloading the full video.
---

# YouTube Downloader

## Prerequisites

Ensure `uv` and `ffmpeg` are installed before running any scripts. If missing, install with:
- `uv`: https://docs.astral.sh/uv/getting-started/installation/
- `ffmpeg`: `brew install ffmpeg`

## Download Video

Run from the skill folder (`skills/youtube-downloader/`):

```bash
uv run --project runtime runtime/download_video.py "URL" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output directory | `output/` |
| `-q, --quality` | best, 1080p, 720p, 480p, 360p, worst | `best` |
| `-f, --format` | mp4, webm, mkv | `mp4` |
| `-a, --audio-only` | Extract audio as MP3 | `false` |

## Download Cover Image

```bash
uv run --project runtime runtime/download_cover.py "URL" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output directory | `output/` |
| `-n, --name` | Custom filename (without extension) | video ID |

Downloads the highest-resolution thumbnail/cover image available for the video. The file extension (`.jpg`, `.png`, `.webp`) is detected automatically from the thumbnail URL.

## Download Transcript

```bash
uv run --project runtime runtime/download_transcript.py "URL" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output directory | `output/` |
| `-f, --format` | text, json, srt | `text` |
| `-l, --lang` | Language code | `en` |

If the requested language is unavailable, available languages are listed in the error output.

## Capture Screenshots

Capture frame images at specific timestamps without downloading the full video. Uses the stream URL directly.

```bash
uv run --project runtime runtime/screenshot_video.py "URL" -t "TIMESTAMPS" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-t, --timestamps` | Comma-separated times: seconds, M:SS, or H:MM:SS (e.g., `30,1:15,2:00`) | **required** |
| `-o, --output` | Output directory | `output/` |
| `-p, --prefix` | Filename prefix for screenshots | `frame` |
| `-q, --quality` | JPEG quality (1=best, 31=worst) | `2` |

Output files are named `<prefix>_001.jpg`, `<prefix>_002.jpg`, etc. A `manifest.json` is also written with metadata for each captured frame.

## Limitations

- Single video only (playlists disabled)
- Transcripts require captions to be available on the video
- Video download and screenshots require `ffmpeg`; transcript download does not
