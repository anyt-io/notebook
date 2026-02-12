---
name: upscale-image
description: Upscale and enhance images using Real-ESRGAN ncnn Vulkan (GPU-accelerated). Use when user wants to upscale, enlarge, enhance, or increase resolution of images. Supports 2x/3x/4x upscaling with models for photos and anime. Auto-downloads binary and models on first run. Works on macOS, Linux, and Windows.
---

# Upscale Image

## Prerequisites

- `uv` (Python package manager)
- GPU with Vulkan support (Metal on macOS, Vulkan on Linux/Windows)

The `realesrgan-ncnn-vulkan` binary and model files are automatically downloaded to `~/.cache/realesrgan-ncnn-vulkan/` on first run.

## Usage

Run from the skill folder (`skills/upscale-image/`):

### Upscale a single image (4x by default)

```bash
uv run --project runtime runtime/upscale.py path/to/image.png
```

### Specify scale factor

```bash
uv run --project runtime runtime/upscale.py image.png -s 2
```

### Choose a model

```bash
uv run --project runtime runtime/upscale.py image.png -m realesrgan-x4plus
```

Available models:

- `realesr-animevideov3` (default) — fast, lightweight, good for most uses
- `realesrgan-x4plus` — highest quality general-purpose (slower)
- `realesrgan-x4plus-anime` — optimized for anime/illustrations

### Specify output directory

```bash
uv run --project runtime runtime/upscale.py image.png -o path/to/output/
```

### Batch processing

```bash
uv run --project runtime runtime/upscale.py img1.png img2.jpg img3.webp
```

## Output

- Output files are saved as PNG.
- Output filenames follow the pattern `<original_name>_upscaled.png`.
- Default output directory: `output/` inside the skill folder.

## Limitations

- `realesrgan-x4plus` is significantly slower than `realesr-animevideov3` on large images.
- Supported input formats: PNG, JPEG, WebP.
- Binary source: [Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan/releases)
- Model source: [Real-ESRGAN releases](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0)
