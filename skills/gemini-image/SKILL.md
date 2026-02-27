---
name: gemini-image
description: Generate and edit images using Google Gemini API. Use when user wants to create images from text prompts, edit existing images with instructions, iterate on image generation conversationally, or produce AI-generated visuals. Supports text-to-image, image editing, aspect ratios, resolution control, and batch generation.
---

# Gemini Image

Generate and edit images using the Google Gemini API's native image generation capabilities.

## Prerequisites

- `uv` (Python package manager)
- `GEMINI_API_KEY` environment variable set with a valid Google AI API key (get one at https://aistudio.google.com/apikey)

## Gemini Image Generation API Guidelines

**Authoritative reference:** https://ai.google.dev/gemini-api/docs/image-generation.md.txt

**SDK:** `google-genai` (`google-generativeai` is deprecated — do not use).

### Available Models

| Model | ID | Best For |
|---|---|---|
| Nano Banana | `gemini-2.5-flash-image` | Speed and efficiency, high-volume, low-latency tasks |
| Nano Banana 2 | `gemini-3.1-flash-image-preview` | High-quality generation at low latency, improved text rendering and i18n, resolution control |
| Nano Banana Pro | `gemini-3-pro-image-preview` | Professional asset production, advanced reasoning, high-res output |

Legacy models (`gemini-2.0-*`, `gemini-1.5-*`) are deprecated.

### API Specifications

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

**Authentication:** `x-goog-api-key` header or client library with `GEMINI_API_KEY`.

**Request format (text-to-image):**

```json
{
  "contents": [{"parts": [{"text": "prompt"}]}],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

**Request format (image editing — send image + text instruction):**

```json
{
  "contents": [{
    "parts": [
      {"text": "Edit instruction"},
      {"inlineData": {"mimeType": "image/png", "data": "<base64>"}}
    ]
  }],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

**Response:** Candidates contain parts — text parts (model commentary) and inline_data parts (base64 image with MIME type). All generated images include a SynthID watermark.

### Python SDK Usage

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="prompt text",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        candidate_count=1,
        image_config=types.ImageConfig(
            aspect_ratio="16:9",       # optional
            image_size="2K",           # optional: "1K", "2K", "4K" (Nano Banana Pro only)
            person_generation="ALLOW_ADULT",  # optional
        ),
    ),
)
for part in response.candidates[0].content.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = Image.open(io.BytesIO(part.inline_data.data))
        image.save("output.png")
```

### Configuration Parameters

**`response_modalities`**: `["TEXT", "IMAGE"]` — required for image output.

**`candidate_count`**: Number of images to generate per request (1-4).

**`image_config`** options:
- `aspect_ratio`: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`
- `image_size`: `"0.5K"`, `"1K"`, `"2K"`, `"4K"` (Nano Banana 2 and Nano Banana Pro only)
- `person_generation`: `"DONT_ALLOW"`, `"ALLOW_ADULT"`, `"ALLOW_ALL"`

### Advanced Features (Nano Banana 2)

- **Resolution control**: 0.5K, 1K (default), 2K, and 4K generation via `image_size`.
- **Improved text rendering**: Better quality and i18n text rendering within images.
- **Extended aspect ratios**: Additional ratios including `1:4`, `4:1`, `1:8`, `8:1`.
- **Search grounding**: Text and image search integration for real-time data.

### Advanced Features (Nano Banana Pro)

- **High-resolution output**: 1K, 2K, and 4K generation via `image_size`.
- **Text rendering**: Legible, stylized text within images for professional assets.
- **Reference images**: Up to 14 reference images (6 objects, 5 humans for consistency).
- **Google Search grounding**: Real-time data for weather maps, charts, current events via `tools=[{"google_search": {}}]`.
- **Thinking mode**: Advanced reasoning enabled by default; generates interim composition-test images.

### Prompting Best Practices

- Describe the scene narratively — don't just list keywords.
- Specify camera angles, lens types, lighting conditions, and mood.
- Include specific textures, materials, color palettes, and design styles.
- State the desired aspect ratio and composition explicitly.
- For edits: clearly describe what to change, add, or remove.

### Capabilities

- **Text-to-image**: Generate images from text descriptions.
- **Image editing**: Provide an existing image + text instructions to modify, add, or remove elements.
- **Multi-turn conversations**: Iteratively refine images through conversation.
- **Text rendering**: Generate legible, stylized text within images.

### Limitations

- Safety filters may block certain prompts.
- Image quality varies with prompt specificity.
- Maximum input image size: 20MB.
- Supported input formats: PNG, JPEG, WebP, GIF.
- `image_size` is only available with Nano Banana 2 (`gemini-3.1-flash-image-preview`) and Nano Banana Pro (`gemini-3-pro-image-preview`).

## Usage

Run from the skill folder (`skills/gemini-image/`):

### Generate an image from a text prompt

```bash
uv run --project runtime runtime/generate_image.py "A serene mountain lake at sunset with reflections"
```

### Specify aspect ratio

```bash
uv run --project runtime runtime/generate_image.py "A panoramic cityscape" --aspect-ratio 16:9
```

### High-resolution output (Nano Banana Pro)

```bash
uv run --project runtime runtime/generate_image.py "Professional product photo" --model gemini-3-pro-image-preview --image-size 2K
```

### Edit an existing image

```bash
uv run --project runtime runtime/generate_image.py "Remove the background and replace with a beach" --input path/to/image.png
```

### Choose a model

```bash
uv run --project runtime runtime/generate_image.py "A cute robot" --model gemini-3-pro-image-preview
```

### Generate multiple variations

```bash
uv run --project runtime runtime/generate_image.py "Abstract art in watercolor style" --count 3
```

### Person generation control

```bash
uv run --project runtime runtime/generate_image.py "Portrait photo" --person-generation ALLOW_ADULT
```

### Specify output directory

```bash
uv run --project runtime runtime/generate_image.py "A logo design" -o path/to/output/
```

## Output

- Default output directory: `output/` inside the skill folder.
- Output filenames: `gemini_YYYYMMDD_HHMMSS_N.png` (timestamp + sequence number).
- Text responses from the model are printed to stdout alongside the saved file paths.

## Limitations

- Requires a valid `GEMINI_API_KEY` environment variable.
- Safety filters may reject certain prompts without generating images.
- Image editing requires the input image to be under 20MB.
- Supported input formats for editing: PNG, JPEG, WebP, GIF.
- `--image-size` only works with `gemini-3.1-flash-image-preview` and `gemini-3-pro-image-preview`.
