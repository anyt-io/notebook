---
schema: "2.0"
name: gemini-image-playground
description: Generate and edit images using Google Gemini API — text-to-image,
  image editing, aspect ratios, and high-resolution output
workdir: anyt_workspace_gemini_image
agents:
  - id: claude-default
    name: Claude Code
    type: claude
    default: true
    permissionMode: bypassPermissions
  - id: codex-default
    name: Codex
    type: codex
    permissionMode: dangerously-bypass
---

# gemini-image-playground

<note id="overview" label="Overview">
## Gemini Image Playground

Generate and edit images using Google Gemini's native image generation models.

### Pipeline
1. **Setup** — Validate `.env` has `GEMINI_API_KEY`, install gemini-image skill
2. **Generate** — Create images from text prompts with configurable model, aspect ratio, and resolution
3. **Review** — Review generated images
4. **Edit** — Edit an existing image with text instructions
5. **Review** — Compare original and edited images

### Models
- **Nano Banana** (`gemini-2.5-flash-image`) — Fast, efficient, great for iteration
- **Nano Banana Pro** (`gemini-3-pro-image-preview`) — Professional quality, supports high-res (2K/4K)

### Prerequisites
- `GEMINI_API_KEY` in `.env` file (get one at https://aistudio.google.com/apikey)
</note>

<shell id="check-env" label="Check Environment">
#!/bin/bash
echo "=== Checking GEMINI_API_KEY ==="

if [ -z "$GEMINI_API_KEY" ]; then
  echo ""
  echo "ERROR: GEMINI_API_KEY environment variable is not set!"
  echo ""
  echo "Add this line to your .env file (next to the notebook):"
  echo "  GEMINI_API_KEY=your-api-key-here"
  echo ""
  echo "Get an API key at: https://aistudio.google.com/apikey"
  exit 1
fi

MASKED="${GEMINI_API_KEY:0:2}...${GEMINI_API_KEY: -2}"
echo "GEMINI_API_KEY loaded: $MASKED"
echo ""
echo "Environment OK"
</shell>

<shell id="install-skill" label="Install Skill">
#!/bin/bash
echo "=== Installing gemini-image skill ==="
npx @anytio/pspm@latest add @user/anyt/gemini-image -y

echo ""
echo "=== Setup output directories ==="
mkdir -p generated edited
</shell>

<input id="generate-config" label="Image Generation Settings">
## Generate an Image

Configure the text-to-image generation settings.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "prompt",
      "type": "textarea",
      "label": "Prompt",
      "description": "Describe the image you want to generate. Be specific about scene, style, lighting, and composition.",
      "required": true,
      "default": "A cozy coffee shop interior with warm golden lighting, exposed brick walls, wooden tables, and a barista preparing a latte with intricate latte art. Shot from a low angle with a shallow depth of field, soft bokeh in the background.",
      "rows": 4
    },
    {
      "name": "model",
      "type": "select",
      "label": "Model",
      "description": "Nano Banana is fast; Nano Banana Pro supports high-res and advanced reasoning",
      "default": "gemini-2.5-flash-image",
      "options": [
        { "value": "gemini-2.5-flash-image", "label": "Nano Banana (fast)" },
        { "value": "gemini-3-pro-image-preview", "label": "Nano Banana Pro (high quality)" }
      ]
    },
    {
      "name": "aspectRatio",
      "type": "select",
      "label": "Aspect Ratio",
      "default": "1:1",
      "options": [
        { "value": "1:1", "label": "1:1 (Square)" },
        { "value": "16:9", "label": "16:9 (Landscape)" },
        { "value": "9:16", "label": "9:16 (Portrait)" },
        { "value": "4:3", "label": "4:3 (Standard)" },
        { "value": "3:2", "label": "3:2 (Photo)" },
        { "value": "21:9", "label": "21:9 (Ultrawide)" }
      ]
    },
    {
      "name": "imageSize",
      "type": "select",
      "label": "Resolution (Nano Banana Pro only)",
      "default": "default",
      "options": [
        { "value": "default", "label": "Default" },
        { "value": "1K", "label": "1K" },
        { "value": "2K", "label": "2K" },
        { "value": "4K", "label": "4K" }
      ]
    },
    {
      "name": "count",
      "type": "select",
      "label": "Number of Images",
      "default": "1",
      "options": [
        { "value": "1", "label": "1" },
        { "value": "2", "label": "2" },
        { "value": "3", "label": "3" },
        { "value": "4", "label": "4" }
      ]
    }
  ]
}
</form>
</input>

<task id="generate-image" label="Generate Image">
## Generate Image from Prompt

Use the **gemini-image** skill to generate images based on the user's settings.

1. Read the user's **Prompt**, **Model**, **Aspect Ratio**, **Resolution**, and **Number of Images** from the input form
2. Use the gemini-image skill's `generate_image.py` script to generate the image(s)
3. Apply the selected aspect ratio via `--aspect-ratio`
4. If the user selected a Resolution other than "Default" AND the model is `gemini-3-pro-image-preview`, add `--image-size`
5. Set the count via `--count`
6. Save output to the `generated/` folder via `-o generated/`
7. List the output files with their dimensions

**Output:** generated/gemini_*.png
</task>

<break id="review-generated" label="Review Generated Images">
## Review Generated Images

Open the images in the `generated/` folder and review the results.

**Things to check:**
- Does the image match the prompt description?
- Is the composition and style as expected?
- Is the quality acceptable for your use case?
- If multiple images were generated, which one is the best?

If you want to try a different prompt or settings, go back and re-run the generation step. Otherwise, click **Continue** to proceed to image editing.
</break>

<input id="edit-config" label="Image Editing Settings">
## Edit an Image

Select one of the generated images and describe what changes you want.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "inputImage",
      "type": "text",
      "label": "Input Image Path",
      "description": "Path to the image to edit (relative to workspace, e.g., generated/gemini_20260223_143000_1.png)",
      "required": true,
      "placeholder": "generated/gemini_*.png"
    },
    {
      "name": "editPrompt",
      "type": "textarea",
      "label": "Edit Instructions",
      "description": "Describe what to change, add, or remove from the image",
      "required": true,
      "default": "Show the same scene from the opposite side, as if the camera walked around to face the other direction while keeping the same lighting and style",
      "rows": 3
    },
    {
      "name": "editModel",
      "type": "select",
      "label": "Model",
      "default": "gemini-2.5-flash-image",
      "options": [
        { "value": "gemini-2.5-flash-image", "label": "Nano Banana (fast)" },
        { "value": "gemini-3-pro-image-preview", "label": "Nano Banana Pro (high quality)" }
      ]
    }
  ]
}
</form>
</input>

<task id="edit-image" label="Edit Image">
## Edit Image with Text Instructions

Use the **gemini-image** skill to edit the selected image based on the user's instructions.

1. Read the **Input Image Path**, **Edit Instructions**, and **Model** from the input form
2. Use the gemini-image skill's `generate_image.py` script with:
   - The edit prompt as the positional argument
   - `--input` pointing to the user's selected image
   - `--model` set to the user's chosen model
   - `-o edited/` to save to the edited folder
3. After editing, list both the original and edited image files with their dimensions for comparison

**Output:** edited/gemini_*.png
</task>

<break id="review-edited" label="Review Edited Images">
## Review Edited Images

Compare the original image with the edited version.

**Files to check:**
- `generated/` — Original generated images
- `edited/` — Edited images

**Things to check:**
- Were the requested edits applied correctly?
- Is the edit natural and well-blended?
- Did the edit preserve the parts of the image that should not have changed?

If you want to try different edits, go back to the edit step. You can also re-run the generation step with a new prompt.
</break>

<note id="complete" label="Complete">
## Session Complete

### Generated Files
```
anyt_workspace_gemini_image/
├── .env                    # API key (not committed)
├── generated/              # Text-to-image outputs
│   └── gemini_*.png
└── edited/                 # Image editing outputs
    └── gemini_*.png
```

### Next Steps
- Re-run generation or editing cells with different prompts
- Try different models (Nano Banana vs Nano Banana Pro)
- Experiment with aspect ratios and high-resolution output
- Use the generated images in your projects
</note>

