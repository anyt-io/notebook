---
name: tiktok-downloader
description: Download TikTok videos, cover images, and screenshots. Use when the user wants to download a TikTok video, extract audio from a TikTok, download cover/thumbnail images, or capture screenshot frames at specific timestamps from TikTok videos.
---

# TikTok Downloader

Download TikTok videos, cover images, and capture screenshots using yt-dlp.

## Prerequisites

- `uv` (Python package manager)
- `ffmpeg`: `brew install ffmpeg`

## Download Video

Run from the skill folder (`skills/tiktok-downloader/`):

```bash
uv run --project runtime runtime/download_video.py "URL" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output directory | `output/` |
| `-f, --format` | mp4, webm, mkv | `mp4` |
| `-a, --audio-only` | Extract audio as MP3 | `false` |

### Examples

```bash
# Download video
uv run --project runtime runtime/download_video.py "https://www.tiktok.com/@user/video/1234567890"

# Download as audio only
uv run --project runtime runtime/download_video.py "https://www.tiktok.com/@user/video/1234567890" -a

# Custom output directory and format
uv run --project runtime runtime/download_video.py "https://www.tiktok.com/@user/video/1234567890" -o downloads/ -f mkv
```

## Download Cover Image

```bash
uv run --project runtime runtime/download_cover.py "URL" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output directory | `output/` |
| `-n, --name` | Custom filename (without extension) | video ID |

Downloads the thumbnail/cover image of a TikTok video. The file extension is detected automatically.

## Capture Screenshots

Capture frame images at specific timestamps without downloading the full video.

```bash
uv run --project runtime runtime/screenshot_video.py "URL" -t "TIMESTAMPS" [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-t, --timestamps` | Comma-separated times: seconds, M:SS, or H:MM:SS | **required** |
| `-o, --output` | Output directory | `output/` |
| `-p, --prefix` | Filename prefix for screenshots | `frame` |
| `-q, --quality` | JPEG quality (1=best, 31=worst) | `2` |

Output files are named `<prefix>_001.jpg`, `<prefix>_002.jpg`, etc. A `manifest.json` is also written with metadata.

## Supported URL Formats

- `https://www.tiktok.com/@user/video/ID`
- `https://vm.tiktok.com/SHORTCODE/`
- `https://m.tiktok.com/v/ID`

## Output

- Default output directory: `output/` inside the skill folder.
- Videos are saved as MP4 by default.
- Cover images use auto-detected extension (.jpg, .png, .webp).

## Limitations

- Single video only (not user profiles or playlists)
- Screenshots require `ffmpeg`
- Some regions or videos may require cookies for access
- TikTok videos are typically short (15s–10min)
