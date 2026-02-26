---
name: keling-motion
description: Generate motion-controlled videos using fal.ai Kling Video v2.6 motion control API. Use when user wants to transfer motion from a reference video onto a character in an image, create motion-controlled video generation, or animate a character with specific movements from another video. Supports character orientation matching to either the reference image or video.
---

# Kling Motion Control (fal.ai)

Generate motion-controlled videos using the fal.ai Kling Video v2.6 motion control API. Transfer motion from a reference video onto a character in a reference image.

## Prerequisites

- `uv` (Python package manager)
- `FAL_KEY` environment variable set with a valid fal.ai API key (get one at https://fal.ai/dashboard/keys)

## How It Works

Motion control takes two inputs:

1. **Reference image** — defines the character's appearance, background, and visual elements
2. **Reference video** — defines the motion/actions the character will perform

The API generates a new video where the character from the image performs the actions from the video.

## Configuration Parameters

| Parameter | CLI Flag | Values |
|---|---|---|
| Character orientation | `--orientation` | `image` (default, max 10s), `video` (max 30s) |
| Keep original sound | `--keep-sound` / `--no-keep-sound` | Keep reference video audio (default: true) |
| Output filename | `--filename` | Custom output filename |
| Output directory | `-o, --output` | Output directory (default: `output/`) |

### Character Orientation

- **`image`** (default): Generated character orientation matches the reference image. Max duration: 10 seconds.
- **`video`**: Generated character orientation matches the reference video. Max duration: 30 seconds.

## Usage

Run from the skill folder (`skills/keling-motion/`):

### Basic motion transfer

```bash
uv run --project runtime runtime/generate_video.py --image character.png --video dance.mp4
```

### With a descriptive prompt

```bash
uv run --project runtime runtime/generate_video.py "A person dancing gracefully in a ballroom" \
  --image character.png --video dance.mp4
```

### Match character orientation to reference video

```bash
uv run --project runtime runtime/generate_video.py --image character.png --video dance.mp4 \
  --orientation video
```

### Discard original audio

```bash
uv run --project runtime runtime/generate_video.py --image character.png --video motion.mp4 \
  --no-keep-sound
```

### Using URLs instead of local files

```bash
uv run --project runtime runtime/generate_video.py \
  --image https://example.com/character.png \
  --video https://example.com/dance.mp4
```

### Custom output

```bash
uv run --project runtime runtime/generate_video.py --image character.png --video dance.mp4 \
  --filename my_video.mp4 -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- Output filenames: `motion_YYYYMMDD_HHMMSS.mp4` (timestamp-based) or custom via `--filename`.
- Videos are MP4 format.

## Limitations

- Image inputs: max 10MB, formats: PNG, JPEG, WebP, GIF.
- Video inputs: max 200MB, formats: MP4, MOV.
- Character orientation `image`: max 10 seconds output.
- Character orientation `video`: max 30 seconds output.
- Cost: $0.07 per second of generated video.
- Safety filters may block certain inputs.
