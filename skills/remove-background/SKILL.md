---
name: remove-background
description: Remove background from images. Use when user wants to remove, strip, or delete image backgrounds, make transparent PNGs, or isolate subjects from photos. Supports single and batch processing with multiple AI models.
---

# Remove Background

## Prerequisites

- `uv` (Python package manager)

## Usage

Run from the skill folder (`skills/remove-background/`):

### Remove background from a single image

```bash
uv run --project runtime runtime/remove_bg.py path/to/image.png
```

### Specify output directory

```bash
uv run --project runtime runtime/remove_bg.py image.png -o path/to/output/
```

### Choose a model

```bash
uv run --project runtime runtime/remove_bg.py image.png -m birefnet-general
```

Available models: `u2net` (default), `u2netp`, `u2net_human_seg`, `u2net_cloth_seg`, `silueta`, `isnet-general-use`, `isnet-anime`, `birefnet-general`, `birefnet-general-lite`, `birefnet-portrait`, `birefnet-dis`, `birefnet-hrsod`, `birefnet-cod`, `birefnet-massive`, `bria-rmbg`.

### Batch processing

```bash
uv run --project runtime runtime/remove_bg.py img1.png img2.jpg img3.webp
```

### Output as mask only

```bash
uv run --project runtime runtime/remove_bg.py image.png --mask-only
```

## Output

- Output files are saved as PNG with transparent backgrounds (or grayscale masks with `--mask-only`).
- Output filenames follow the pattern `<original_name>_nobg.png` (or `<original_name>_mask.png`).
- Default output directory: `output/` inside the skill folder.

## Limitations

- Models are downloaded on first use (~30-170 MB each) to `~/.u2net/`.
- CPU-only by default. GPU acceleration requires installing `onnxruntime-gpu` separately.
- Supported input formats: PNG, JPEG, WebP, BMP, TIFF.
