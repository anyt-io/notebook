---
name: keling-video
description: Generate and edit videos using fal.ai Kling Video O3 API. Use when user wants to create videos from text prompts, animate images into videos, use reference elements for character consistency, edit existing videos, or produce AI-generated video clips. Supports text-to-video, image-to-video, reference-to-video (I2V and V2V), video editing, multi-prompt storyboarding, and native audio generation across standard and pro quality tiers.
---

# Kling Video (fal.ai)

Generate and edit videos using the fal.ai Kling Video O3 API.

## Prerequisites

- `uv` (Python package manager)
- `FAL_KEY` environment variable set with a valid fal.ai API key (get one at https://fal.ai/dashboard/keys)

## Generation Modes

| Mode | Trigger | Endpoint Pattern |
|---|---|---|
| Text-to-video | prompt only | `fal-ai/kling-video/o3/{quality}/text-to-video` |
| Image-to-video | `--image` | `fal-ai/kling-video/o3/{quality}/image-to-video` |
| Reference-to-video | `--element` | `fal-ai/kling-video/o3/{quality}/reference-to-video` |
| Edit video | `--video` | `fal-ai/kling-video/o3/{quality}/video-to-video/edit` |

Mode is auto-detected from arguments. All modes support `standard` and `pro` quality tiers via `--quality`.

## Configuration Parameters

| Parameter | CLI Flag | Values |
|---|---|---|
| Quality | `--quality` | `standard` (default), `pro` |
| Aspect ratio | `--aspect-ratio` | `16:9` (default), `9:16`, `1:1` |
| Duration | `--duration` | `3`–`15` seconds (default: `5`) |
| Audio | `--audio` | Enable native audio generation |
| Multi-prompt | `--multi-prompt` | JSON array or file path |

## Usage

Run from the skill folder (`skills/keling-video/`):

### Text-to-video

```bash
uv run --project runtime runtime/generate_video.py "A cinematic shot of a lion in the savannah"
```

### Text-to-video (pro quality)

```bash
uv run --project runtime runtime/generate_video.py "A cinematic shot of a lion" --quality pro
```

### Image-to-video (animate a starting frame)

```bash
uv run --project runtime runtime/generate_video.py "The scene comes to life" --image start.png
```

### Image-to-video with end frame interpolation

```bash
uv run --project runtime runtime/generate_video.py "A flower blooming in timelapse" --image first.png --end-image last.png
```

### Reference I2V — element with frontal image

Use `@Element1` in the prompt to reference the element:

```bash
uv run --project runtime runtime/generate_video.py "@Element1 walks through a neon city" --element robot.png
```

### Reference I2V — element with additional reference angles

```bash
uv run --project runtime runtime/generate_video.py "@Element1 dances in a ballroom" \
  --element character.png --element-ref side_view.png --element-ref back_view.png
```

### Reference V2V — element with video reference

Provide a video to capture motion and appearance:

```bash
uv run --project runtime runtime/generate_video.py "@Element1 performs the same dance" \
  --element character.png --element-video motion_clip.mp4
```

### Two elements

```bash
uv run --project runtime runtime/generate_video.py "@Element1 and @Element2 meet in a park" \
  --element person_a.png --element person_b.png
```

### Reference with style images

Use `@Image1` in prompt to reference style images:

```bash
uv run --project runtime runtime/generate_video.py "@Element1 in @Image1 environment" \
  --element character.png --ref-image environment.png
```

### Reference with start/end frames

```bash
uv run --project runtime runtime/generate_video.py "@Element1 walks forward" \
  --element character.png --start-image scene_start.png --end-image scene_end.png
```

### Edit video

Use `@Video1` in the prompt to reference the source video:

```bash
uv run --project runtime runtime/generate_video.py "Change the background to a sunset @Video1" --video input.mp4
```

### Edit video with reference images

```bash
uv run --project runtime runtime/generate_video.py "Replace character with @Image1 @Video1" \
  --video input.mp4 --ref-image new_character.png
```

### Edit video — discard original audio

```bash
uv run --project runtime runtime/generate_video.py "Add explosion effects @Video1" \
  --video input.mp4 --no-keep-audio
```

### Advanced: elements via JSON

For complex multi-element setups:

```bash
uv run --project runtime runtime/generate_video.py "@Element1 and @Element2 interact" \
  --elements-json '[{"frontal_image_url":"char_a.png","reference_image_urls":["side_a.png"]},{"frontal_image_url":"char_b.png"}]'
```

### Multi-prompt storyboarding

```bash
uv run --project runtime runtime/generate_video.py \
  --multi-prompt '[{"prompt":"Scene 1: A calm forest","duration":"5"},{"prompt":"Scene 2: A thunderstorm begins","duration":"5"}]'
```

### With audio, portrait, longer duration

```bash
uv run --project runtime runtime/generate_video.py "A waterfall in the mountains" \
  --audio --aspect-ratio 9:16 --duration 10
```

### Custom output

```bash
uv run --project runtime runtime/generate_video.py "Ocean waves" --filename ocean.mp4 -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- Output filenames: `kling_YYYYMMDD_HHMMSS.mp4` (timestamp-based) or custom via `--filename`.
- Videos are MP4 format.

## Limitations

- Image inputs: max 10MB, formats: PNG, JPEG, WebP, GIF.
- Video inputs (edit mode): max 200MB, formats: MP4, MOV, 3–10s duration, 720–2160px.
- Maximum 2 elements per request.
- Maximum 3 reference angle images per element.
- Maximum 4 style reference images (combined with elements).
- Prompt max length: 2,500 characters.
- Duration range: 3–15 seconds.
- Safety filters may block certain prompts.
