---
name: gemini-video
description: Generate videos using Google Gemini Veo 3.1 API and concatenate video clips. Use when user wants to create videos from text prompts, generate videos from images, animate with first/last frame interpolation, use reference images for character consistency, produce short video clips with native audio, or merge multiple video clips into one. Supports text-to-video, image-to-video, reference images, first/last frame interpolation, aspect ratios, resolution control, and video concatenation.
---

# Gemini Video

Generate videos using the Google Gemini Veo 3.1 API.

## Prerequisites

- `uv` (Python package manager)
- `GEMINI_API_KEY` environment variable set with a valid Google AI API key (get one at https://aistudio.google.com/apikey)

## Gemini Veo 3.1 API Guidelines

**SDK:** `google-genai` (`google-generativeai` is deprecated -- do not use).

### Available Models

| Model | ID | Best For |
|---|---|---|
| Veo 3.1 | `veo-3.1-generate-preview` | Highest quality, 720p/1080p/4k, native audio, reference images, interpolation |
| Veo 3.1 Fast | `veo-3.1-fast-generate-preview` | Speed-optimized, good quality with audio |

### Generation Modes

| Mode | CLI Flags | Description |
|---|---|---|
| Text-to-video | `"prompt"` | Generate from text description only |
| Image-to-video | `--image first.png` | Animate an image (used as first frame) |
| Interpolation | `--image first.png --last-frame last.png` | Generate video transitioning between two frames |
| Reference images | `--reference img1.png --reference img2.png` | Guide content with up to 3 reference images for character/style consistency |

### Configuration Parameters

| Parameter | CLI Flag | Values |
|---|---|---|
| `aspect_ratio` | `--aspect-ratio` | `"16:9"` (default), `"9:16"` |
| `resolution` | `--resolution` | `"720p"` (default), `"1080p"`, `"4k"` |
| `duration_seconds` | `--duration` | `4`, `6`, `8` (must be `8` for 1080p/4k and reference images) |
| `negative_prompt` | `--negative-prompt` | Free text (e.g., `"cartoon, low quality"`) |
| `person_generation` | `--person-generation` | `"allow_all"`, `"allow_adult"`, `"dont_allow"` |

### Reference Images

Provide up to 3 reference images to preserve a subject's appearance (person, character, product) in the output video. Each reference is tagged as `"asset"`.

```python
reference = types.VideoGenerationReferenceImage(
    image=image_object,
    reference_type="asset"
)
config = types.GenerateVideosConfig(
    reference_images=[ref1, ref2, ref3],
)
```

### First / Last Frame Interpolation

Specify the first and/or last frame to control how the video begins and ends. The first frame is passed as the primary `image` input; the last frame goes into `config.last_frame`.

```python
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=first_image,
    config=types.GenerateVideosConfig(last_frame=last_image),
)
```

### Prompting Best Practices

- **Subject**: Object, person, animal, or scenery.
- **Action**: What the subject is doing (walking, running, turning).
- **Style**: Film style keywords (sci-fi, film noir, cartoon).
- **Camera**: Aerial view, close-up, dolly shot, POV.
- **Audio**: Use quotes for dialogue, describe sound effects and ambient noise. Veo 3.1 generates native audio from prompt cues.
- **Negative prompts**: Describe what to exclude (don't use "no" or "don't").

### Limitations

- Request latency: 11 seconds to 6 minutes.
- Generated videos stored on server for 2 days only.
- Videos are watermarked with SynthID.
- Safety filters may block certain prompts.
- `1080p` and `4k` require `duration=8`.
- Reference images require `duration=8`.

## Usage

Run from the skill folder (`skills/gemini-video/`):

### Text-to-video

```bash
uv run --project runtime runtime/generate_video.py "A cinematic shot of a majestic lion in the savannah"
```

### Image-to-video (animate a starting frame)

```bash
uv run --project runtime runtime/generate_video.py "The scene comes to life" --image start.png
```

### First + last frame interpolation

```bash
uv run --project runtime runtime/generate_video.py "A flower blooming in timelapse" --image first.png --last-frame last.png
```

### Reference images (character/style consistency)

```bash
uv run --project runtime runtime/generate_video.py "A robot walks through a neon city at night" \
  --reference robot_front.png --reference robot_side.png --reference city_bg.png
```

### Portrait video (9:16)

```bash
uv run --project runtime runtime/generate_video.py "A majestic waterfall" --aspect-ratio 9:16
```

### High-resolution (4k)

```bash
uv run --project runtime runtime/generate_video.py "Drone view of the Grand Canyon at sunset" --resolution 4k
```

### Fast model for quick iteration

```bash
uv run --project runtime runtime/generate_video.py "A cat playing piano" --model veo-3.1-fast-generate-preview
```

### With negative prompt

```bash
uv run --project runtime runtime/generate_video.py "A cinematic lion shot" --negative-prompt "cartoon, drawing, low quality"
```

### Control duration

```bash
uv run --project runtime runtime/generate_video.py "A quick action scene" --duration 4
```

### Custom output

```bash
uv run --project runtime runtime/generate_video.py "Ocean waves" --filename ocean.mp4 -o path/to/output/
```

## Concatenate Videos

Merge multiple video clips into a single video file using ffmpeg (no re-encoding).

### Prerequisites

- `ffmpeg` must be installed and available on PATH

### Concatenate specific files

```bash
uv run --project runtime runtime/concat_videos.py scene_01.mp4 scene_02.mp4 scene_03.mp4
```

### Concatenate all videos in a directory

```bash
uv run --project runtime runtime/concat_videos.py --dir video/
```

### Custom output path

```bash
uv run --project runtime runtime/concat_videos.py --dir video/ -o final_video.mp4
```

### Custom glob pattern

```bash
uv run --project runtime runtime/concat_videos.py --dir video/ --pattern "scene_*.mp4"
```

## Output

- Default output directory: `output/` inside the skill folder.
- Output filenames: `veo_YYYYMMDD_HHMMSS.mp4` (timestamp-based) or custom via `--filename`.
- Veo 3.1 videos include natively generated audio.
- Concat output: `concat.mp4` in the output directory (or custom path via `-o`).
