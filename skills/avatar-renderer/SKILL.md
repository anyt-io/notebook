---
name: avatar-renderer
description: Render avatar images with emotional facial expressions and generate animation sequences for interview simulations. Use when building interview simulation UIs that need visual avatar representation with dynamic emotional states. Generates avatar frames as PNG images.
---

# Avatar Renderer

Generate avatar images with emotional expressions for interview simulation systems.

## Prerequisites

- `uv` (Python package manager)

## Usage

Render a single avatar frame:

```bash
uv run --project runtime runtime/render.py --emotion neutral --intensity 0.8 --output output/avatar_neutral.png
```

Render an animation sequence from an animation script:

```bash
uv run --project runtime runtime/render.py --script path/to/animation_script.json --output output/frames/
```

Generate avatar sprite sheet:

```bash
uv run --project runtime runtime/render.py --sprite-sheet --output output/sprite_sheet.png
```

### Supported Emotions

neutral, attentive, skeptical, satisfied, stern, surprised, concerned

Each emotion renders with configurable intensity (0.0-1.0) affecting expression magnitude.

### Output

- Single frames as PNG images (512x512 default)
- Animation sequences as numbered PNG frames
- Sprite sheets with all emotions at standard intensities
