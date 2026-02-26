---
name: wavespeed-keling-motion
description: Transfer motion from reference videos to animate still images using WaveSpeed AI Kling v2.6 Motion Control API. Use when user wants to apply video motion to a static image, create animated characters from photos using motion references, or produce AI-driven motion transfer videos.
---

# WaveSpeed Kling Motion Control

Transfer motion from reference videos to animate still images using the WaveSpeed AI Kling v2.6 Motion Control API.

## Prerequisites

- `uv` (Python package manager)
- `WAVESPEED_API_KEY` environment variable set with a valid WaveSpeed AI API key (get one at https://wavespeed.ai)

## How It Works

Motion control transfers movement from a reference video to a still image:
1. Provide a **still image** of the subject you want to animate
2. Provide a **reference video** with the desired motion
3. Choose **character orientation** to match the subject's direction to either the image or video
4. The API animates the image using the motion from the video

## Configuration Parameters

| Parameter | CLI Flag | Values |
|---|---|---|
| Character orientation | `--orientation` | `image` (default), `video` |
| Prompt | positional or `--prompt` | Positive prompt for generation |
| Negative prompt | `--negative-prompt` | Negative prompt to avoid unwanted elements |
| Keep audio | `--keep-audio` | Preserve original video audio (default: true) |

## Usage

Run from the skill folder (`skills/wavespeed-keling-motion/`):

### Basic motion transfer

```bash
uv run --project runtime runtime/generate_motion.py --image person.png --video dance.mp4
```

### With prompt guidance

```bash
uv run --project runtime runtime/generate_motion.py "A person dancing gracefully" \
  --image person.png --video dance.mp4
```

### Character orientation from video

Use when the reference video's character direction should be preserved:

```bash
uv run --project runtime runtime/generate_motion.py --image face.png --video nod.mp4 \
  --orientation video
```

### With negative prompt

```bash
uv run --project runtime runtime/generate_motion.py "A robot walking" \
  --image robot.png --video walk.mp4 \
  --negative-prompt "blurry, distorted, low quality"
```

### Discard original audio

```bash
uv run --project runtime runtime/generate_motion.py --image singer.png --video lip_sync.mp4 \
  --no-keep-audio
```

### Custom output

```bash
uv run --project runtime runtime/generate_motion.py --image cat.png --video stretch.mp4 \
  --filename cat_stretch.mp4 -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- Output filenames: `motion_YYYYMMDD_HHMMSS.mp4` (timestamp-based) or custom via `--filename`.
- Videos are MP4 format.

## Limitations

- Image inputs: max 10MB, formats: PNG, JPEG. Min 300px width/height. Aspect ratio 1:2.5 to 2.5:1.
- Video inputs: max 10MB, formats: MP4, MOV. Min 300px width/height. Aspect ratio 1:2.5 to 2.5:1.
- API requires top-up to activate. Keys without top-up will not work.
- Safety filters may block certain content.
