---
schema: "2.0"
name: image-background-remover
description: Remove backgrounds from images, review with human-in-the-loop, edit in Photoshop if needed, then upscale final images
workdir: image_output
---

# image-background-remover

<note id="overview" label="Overview">
## Image Background Remover & Upscaler

This notebook provides a complete image processing pipeline:
1. **Input** — Select image(s) or an image directory
2. **Remove Background** — AI-powered background removal using rembg
3. **Review** — Human review of results, edit in Photoshop if needed
4. **Upscale** — Enhance final images using Real-ESRGAN ncnn Vulkan (GPU-accelerated)

### Skills Used
- `remove-background` — rembg-based background removal
- `upscale-image` — Real-ESRGAN ncnn Vulkan upscaling

### Example
Use `skills/remove-background/runtime/tests/demo.png` as a sample image to test the pipeline.
</note>

<input id="image-input" label="Image Input">
## Select Images

Provide the image path(s) or directory to process.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "imagePath",
      "type": "text",
      "label": "Image Path",
      "description": "Path to a single image file or a directory containing images",
      "required": true,
      "default": "demo.png",
      "placeholder": "demo.png or path/to/image/folder"
    },
    {
      "name": "bgModel",
      "type": "select",
      "label": "Background Removal Model",
      "description": "Model for background removal",
      "default": "u2net",
      "options": [
        { "value": "u2net", "label": "u2net (general, default)" },
        { "value": "u2net_human_seg", "label": "u2net_human_seg (people)" },
        { "value": "isnet-general-use", "label": "isnet-general-use" },
        { "value": "birefnet-general", "label": "birefnet-general (high quality)" }
      ]
    },
    {
      "name": "upscaleModel",
      "type": "select",
      "label": "Upscale Model",
      "description": "Model for final upscaling",
      "default": "realesr-animevideov3",
      "options": [
        { "value": "realesr-animevideov3", "label": "animevideov3 (fast, default)" },
        { "value": "realesrgan-x4plus", "label": "x4plus (best quality, slow)" },
        { "value": "realesrgan-x4plus-anime", "label": "x4plus-anime (anime)" }
      ]
    },
    {
      "name": "upscaleFactor",
      "type": "select",
      "label": "Upscale Factor",
      "default": "2",
      "options": [
        { "value": "2", "label": "2x" },
        { "value": "3", "label": "3x" },
        { "value": "4", "label": "4x" }
      ]
    }
  ]
}
</form>
</input>

<shell id="install-skills" label="Install Skills">
#!/bin/bash
echo "=== Installing remove-background skill ==="
npx @anytio/pspm@latest add @user/anyt/remove-background -y

echo ""
echo "=== Installing upscale-image skill ==="
npx @anytio/pspm@latest add @user/anyt/upscale-image -y

echo ""
echo "=== Setup output directories ==="
mkdir -p nobg edited upscaled
</shell>

<task id="remove-backgrounds" label="Remove Backgrounds">
## Remove Background from Images

Use the **remove-background** skill to process the input images.

1. Read the **Image Path** from user input
2. If the path is a directory, find all image files (png, jpg, jpeg, webp) inside it; if a single file, process just that file
3. Use the remove-background skill with the **Background Removal Model** selected by the user
4. Save all output to the `nobg/` folder
5. After processing, list all generated files in `nobg/` with their file sizes and report how many images were processed

**Output:** nobg/*_nobg.png
</task>

<break id="review-backgrounds" label="Review Background Removal">
## Review Background Removal Results

Open the images in `nobg/` folder and review the background removal quality.

**Things to check:**
- Are the subject edges clean and well-defined?
- Is there any leftover background visible?
- Are transparent areas correct?
- Are any parts of the subject accidentally removed?

### If edits are needed
1. Open the image in **Photoshop** (or any image editor)
2. Fix edges, clean up artifacts, or restore accidentally removed parts
3. Save the edited version to the `edited/` folder with the same filename
4. Images in `edited/` will be used for upscaling instead of `nobg/`

If all images look good, click **Continue** to proceed to upscaling.
</break>

<task id="upscale-images" label="Upscale Images">
## Upscale Final Images

Upscale the processed images using the **upscale-image** skill.

1. Check if there are any images in the `edited/` folder (human-edited versions)
2. For each image: if an edited version exists in `edited/` with the same filename, use that; otherwise use the version from `nobg/`
3. Use the upscale-image skill with the **Upscale Model** and **Upscale Factor** selected by the user
4. Save all upscaled output to the `upscaled/` folder
5. After processing, list all generated files in `upscaled/` with their dimensions and file sizes, and report before/after dimensions

**Output:** upscaled/*_upscaled.png
</task>

<break id="review-final" label="Review Final Output">
## Review Final Upscaled Images

Open the images in the `upscaled/` folder and verify the final quality.

**Things to check:**
- Is the upscaling quality acceptable?
- Are edges still clean after upscaling?
- Is the overall image sharp and artifact-free?

If any images need re-processing, go back and adjust the previous steps.
</break>

<note id="complete" label="Complete">
## Pipeline Complete

### Generated Files
```
image_output/
├── nobg/              # Background-removed images (transparent PNG)
├── edited/            # Human-edited images (if any were fixed in Photoshop)
└── upscaled/          # Final upscaled images
```

### Next Steps
- Open `upscaled/` to access your final high-resolution transparent images
- Re-run individual cells to adjust models or reprocess specific images
- Use the final images in your design projects, e-commerce listings, etc.
</note>
