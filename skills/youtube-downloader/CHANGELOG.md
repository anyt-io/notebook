# Changelog

## [0.2.0] - 2026-02-10

### Added
- `download_cover.py` — Download YouTube video cover/thumbnail images
  - Auto-detects image format (jpg, png, webp) from thumbnail URL
  - Supports custom filename via `-n` flag, defaults to video ID
- Cover image download step in `youtube-video-summarizer` notebook
- Cover image included in compiled summary markdown header

### Changed
- Updated SKILL.md with cover download documentation
- Updated `Download-Info` task in notebook to fetch cover alongside video and transcript
- Updated `compile-markdown` task to embed cover image in summary header

## [0.1.1] - 2025-01-15

### Added
- `download_transcript.py` — Download YouTube video transcripts in text, JSON, or SRT format
- Language selection support for transcripts
- Tests for transcript downloader

### Changed
- Updated SKILL.md with transcript download documentation

## [0.1.0] - 2025-01-10

### Added
- Initial release
- `download_video.py` — Download YouTube videos with customizable quality and format
- Support for quality presets (best, 1080p, 720p, 480p, 360p, worst)
- Support for output formats (mp4, webm, mkv)
- Audio-only download mode (mp3)
- Video metadata display (title, duration, uploader)
