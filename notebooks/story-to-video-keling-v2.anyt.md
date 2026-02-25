---
schema: "2.0"
name: story-to-video-keling-v2
description: Generate a short AI video from a story idea using Gemini Image for
  scene keyframes and Kling Video for video generation with start/end frame
  control
version: 1.0.0
workdir: anyt_workspace_story_to_video_keling_v2
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

# story-to-video-keling-v2

<note id="overview" label="Overview">
## Story-to-Video Pipeline v2 (Keling + Scene Keyframes)

This notebook generates a short AI video from a story idea using **Gemini Image** (Nano Banana) to create **keyframe images** for each scene and **Kling Video O3** (fal.ai) to generate videos with precise start/end frame control.

### How It Works
Unlike the basic pipeline that only uses character references, this version generates **start and end frame images** for every scene. Kling Video then interpolates between these keyframes, producing videos with precise visual control and smooth scene-to-scene transitions.

### Flow
1. **Check Environment** — Verify `GEMINI_API_KEY`, `FAL_KEY`, `uv`, and `ffmpeg`
2. **Install Skills** — Add gemini-image and keling-video skills
3. **Story Input** — Enter your story idea (default: a visually striking Tokyo cat story)
4. **Generate Character** — Create the main character's frontal reference image
5. **Enrich Story** — Expand into 3 scenes with detailed visual descriptions
6. **Generate Keyframes** — For each scene, generate a start frame and end frame image with Nano Banana
7. **Generate Videos** — Use Kling Video reference-to-video with `--element`, `--start-image`, and `--end-image` per scene
8. **Concat Video** — Merge all scene clips into one final video

### Key Features
- **Start/end frame control** — Each scene has AI-generated keyframe images that guide the video
- **Scene chaining** — End frame of scene N becomes the start frame of scene N+1
- **Character consistency** — `@Element1` reference maintained across all scenes
- **8-second scenes** — 3 scenes at 8 seconds each = 24-second final video

All steps have defaults so you can run end-to-end quickly for testing.
</note>

<shell id="check-env" label="Check Environment">
#!/bin/bash
echo "=== Checking Environment ==="

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: GEMINI_API_KEY is not set."
  echo ""
  echo "Get an API key at: https://aistudio.google.com/apikey"
  echo "Then set it:"
  echo '  export GEMINI_API_KEY="your-key-here"'
  echo "Or add it to your .env file."
  exit 1
fi
echo "GEMINI_API_KEY is set."

echo ""
if [ -z "$FAL_KEY" ]; then
  echo "ERROR: FAL_KEY is not set."
  echo ""
  echo "Get an API key at: https://fal.ai/dashboard/keys"
  echo "Then set it:"
  echo '  export FAL_KEY="your-key-here"'
  echo "Or add it to your .env file."
  exit 1
fi
echo "FAL_KEY is set."

echo ""
echo "=== Checking uv ==="
if command -v uv &> /dev/null; then
  echo "uv $(uv --version) found"
else
  echo "ERROR: uv is not installed. Install from https://docs.astral.sh/uv/"
  exit 1
fi

echo ""
echo "=== Checking ffmpeg ==="
if command -v ffmpeg &> /dev/null; then
  echo "ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
  echo "WARNING: ffmpeg is not installed. Video concatenation will not work."
  echo "Install from https://ffmpeg.org/ or via your package manager."
fi

echo ""
echo "=== Environment OK ==="
</shell>

<shell id="install-skills" label="Install Skills">
#!/bin/bash
echo "=== Installing Gemini Image Skill ==="
npx @anytio/pspm@latest add @user/anyt/gemini-image -y

echo ""
echo "=== Installing Keling Video Skill ==="
npx @anytio/pspm@latest add @user/anyt/keling-video -y

echo ""
echo "=== Verify Installed Skills ==="
ls -la .pspm/skills/ 2>/dev/null || echo "Skills directory not found"
echo ""
echo "=== Setup Output Directories ==="
mkdir -p character story keyframes video
echo "Created: character/ story/ keyframes/ video/"
</shell>

<input id="story-input" label="Story Idea">
## What's Your Story?

Enter a story concept. The default story is designed to showcase smooth scene transitions with vivid visuals.

<form type="json">
{
  "fields": [
    {
      "name": "storyIdea",
      "type": "textarea",
      "label": "Story Idea",
      "required": true,
      "default": "A stray cat with golden eyes wanders through the rain-soaked alleys of Tokyo at night. She discovers a forgotten paper lantern glowing with an otherworldly blue light. As she touches it with her paw, the entire alley erupts in swirling neon colors — puddles become mirrors reflecting impossible constellations, and paper cranes fold themselves from the rain and take flight. The cat leaps across glowing rooftops, chasing the luminous cranes through a sky painted with auroras, until she reaches the highest rooftop and watches the first light of dawn dissolve the magic into golden mist over the Tokyo skyline.",
      "rows": 6,
      "placeholder": "Describe your story idea... Include vivid visual details for best results."
    },
    {
      "name": "characterName",
      "type": "text",
      "label": "Main Character Name",
      "required": true,
      "default": "Hikari"
    },
    {
      "name": "characterDescription",
      "type": "textarea",
      "label": "Character Appearance",
      "required": true,
      "default": "A sleek Japanese stray cat with striking golden eyes, dark grey fur with subtle tabby stripes, a small notch in her left ear, and a graceful, alert posture",
      "rows": 2,
      "placeholder": "Describe the main character's appearance..."
    },
    {
      "name": "imageModel",
      "type": "select",
      "label": "Image Model (for keyframes)",
      "default": "gemini-2.5-flash-image",
      "options": [
        { "value": "gemini-2.5-flash-image", "label": "Nano Banana (fast, efficient)" },
        { "value": "gemini-3-pro-image-preview", "label": "Nano Banana Pro (higher quality, slower)" }
      ]
    },
    {
      "name": "artStyle",
      "type": "select",
      "label": "Art Style",
      "default": "photorealistic",
      "options": [
        { "value": "photorealistic", "label": "Photorealistic / Cinematic" },
        { "value": "3d-animated", "label": "3D Animated (Pixar-like)" },
        { "value": "anime", "label": "Anime / Manga" },
        { "value": "stylized-cartoon", "label": "Stylized Cartoon" }
      ]
    },
    {
      "name": "videoQuality",
      "type": "select",
      "label": "Video Quality",
      "default": "standard",
      "options": [
        { "value": "standard", "label": "Standard (faster, lower cost)" },
        { "value": "pro", "label": "Pro (higher quality, slower)" }
      ]
    },
    {
      "name": "aspectRatio",
      "type": "select",
      "label": "Video Aspect Ratio",
      "default": "16:9",
      "options": [
        { "value": "16:9", "label": "Landscape (16:9)" },
        { "value": "9:16", "label": "Portrait (9:16)" },
        { "value": "1:1", "label": "Square (1:1)" }
      ]
    },
    {
      "name": "generateAudio",
      "type": "checkbox",
      "label": "Generate native audio for video scenes"
    }
  ]
}
</form>
</input>

<task id="generate-character" label="Generate Character Reference">
Using the **gemini-image** skill, generate a single high-quality frontal reference image of the main character from `story-input`.

- Use the `imageModel` from `story-input` (default: `gemini-2.5-flash-image`)
- Use the `characterDescription` from `story-input` for the character's appearance
- Use the `artStyle` from `story-input`
- Generate a **front-facing, centered** character portrait on a simple neutral background
- Use aspect ratio `1:1` for the character portrait
- Save as `character/frontal.png`

This image will be used as the `--element` reference in every video scene to maintain character consistency.

**Output:** character/frontal.png
</task>

<break id="review-character" label="Review Character">
Review the character reference image at `character/frontal.png`.

This image will be used as the `@Element1` reference across all video scenes.
Continue when you're happy with the character design.
</break>

<task id="enrich-story" label="Enrich Story into 3 Scenes">
Expand the story from `story-input` into exactly **3 scenes** of 8 seconds each.

The scenes must form a **visual chain** — each scene's end state should naturally lead into the next scene's start state. Think of it as storyboarding a continuous camera sequence with 3 cuts.

For each scene, write:
- **title**: Short scene name
- **videoPrompt**: Detailed cinematic description (2-3 sentences) using `@Element1` to reference the main character. Include: action, camera angle, lighting, mood, environment. If `generateAudio` is enabled, include audio cues (ambient sounds, effects) in the prompt.
- **startFramePrompt**: A detailed image generation prompt for the **opening frame** of this scene. Describe the exact composition, character pose, environment, lighting as a single still image. Include the character's appearance and the art style.
- **endFramePrompt**: A detailed image generation prompt for the **closing frame** of this scene. This should visually connect to the next scene's start frame. Include the character's appearance and the art style.

**Important chaining rule:** Scene N's `endFramePrompt` and Scene N+1's `startFramePrompt` should describe the **same moment** from the same angle — they are the same frame at the cut point.

Save as JSON:
```json
{
  "title": "Story Title",
  "character": "Character appearance description",
  "artStyle": "chosen style",
  "scenes": [
    {
      "id": 1,
      "title": "Scene Title",
      "videoPrompt": "@Element1 discovers a glowing lantern in a dark alley. Slow push-in shot, rain falling, blue light illuminating the cat's golden eyes...",
      "startFramePrompt": "A sleek grey tabby cat with golden eyes crouches in a dark rain-soaked Tokyo alley, photorealistic, cinematic lighting...",
      "endFramePrompt": "Close-up of the grey tabby cat touching a glowing blue paper lantern with her paw, neon reflections in puddles, photorealistic...",
      "duration": "8"
    },
    {
      "id": 2,
      "title": "Scene Title",
      "videoPrompt": "...",
      "startFramePrompt": "Close-up of the grey tabby cat touching a glowing blue paper lantern with her paw, neon reflections in puddles, photorealistic...",
      "endFramePrompt": "...",
      "duration": "8"
    }
  ]
}
```

Notice how scene 1's `endFramePrompt` matches scene 2's `startFramePrompt` — this creates the visual chain.

**Output:** story/scenes.json
</task>

<task id="generate-keyframes" label="Generate Scene Keyframes">
Using the **gemini-image** skill, generate **start frame** and **end frame** images for each scene in `story/scenes.json`.

For each scene:
- Use the `imageModel` from `story-input` (default: `gemini-2.5-flash-image`)
- Use the scene's `startFramePrompt` to generate the start frame image
- Use the scene's `endFramePrompt` to generate the end frame image
- Use the `aspectRatio` from `story-input` (default: 16:9) to match the video output
- Use the character reference image `character/frontal.png` as `--input` to maintain character consistency in every keyframe
- Save with naming convention:
  - `keyframes/scene_01_start.png`, `keyframes/scene_01_end.png`
  - `keyframes/scene_02_start.png`, `keyframes/scene_02_end.png`
  - `keyframes/scene_03_start.png`, `keyframes/scene_03_end.png`

That's 6 images total (2 per scene).

**Output:** keyframes/scene_01_start.png, keyframes/scene_01_end.png, keyframes/scene_02_start.png, keyframes/scene_02_end.png, keyframes/scene_03_start.png, keyframes/scene_03_end.png
</task>

<break id="review-keyframes" label="Review Keyframes">
Review all keyframe images in `keyframes/` before generating videos.

Check that:
- Each scene's start and end frames look visually distinct (there should be clear motion/change between them)
- Scene transitions are smooth: scene N's end frame should look similar to scene N+1's start frame
- The character is recognizable and consistent across all frames
- The art style and mood match the story

Files:
- `keyframes/scene_01_start.png` / `keyframes/scene_01_end.png`
- `keyframes/scene_02_start.png` / `keyframes/scene_02_end.png`
- `keyframes/scene_03_start.png` / `keyframes/scene_03_end.png`

Continue when satisfied.
</break>

<task id="generate-videos" label="Generate Videos">
Using the **keling-video** skill, generate a video for each scene in `story/scenes.json` using **reference-to-video** mode with start/end frame control.

For each scene:
- Use the scene's `videoPrompt` as the prompt (which includes `@Element1` references to the character)
- Use `character/frontal.png` with `--element` for character consistency (Reference I2V mode)
- Use the scene's start frame with `--start-image` (e.g., `keyframes/scene_01_start.png`)
- Use the scene's end frame with `--end-image` (e.g., `keyframes/scene_01_end.png`)
- Use `--quality` from `story-input` (default: `standard`)
- Use `--aspect-ratio` from `story-input` (default: `16:9`)
- Use `--duration 8`
- If `generateAudio` is enabled in `story-input`, add `--audio`
- Save as `video/scene_01.mp4`, `video/scene_02.mp4`, `video/scene_03.mp4`

Generate all 3 scenes. Each scene is independently controlled by its own keyframe images.

**Output:** video/scene_01.mp4, video/scene_02.mp4, video/scene_03.mp4
</task>

<task id="concat-video" label="Concatenate Final Video">
Merge all scene videos into a single final video using ffmpeg.

- Concatenate all scene clips from `video/` in filename order (`scene_01.mp4`, `scene_02.mp4`, `scene_03.mp4`)
- Use ffmpeg concat demuxer (no re-encoding) for fast lossless merging
- Save the final video as `video/final.mp4`

**Output:** video/final.mp4
</task>

<note id="complete" label="Pipeline Complete">
## Story-to-Video Complete

### Generated Files
```
character/frontal.png              # Character reference (used as @Element1)
keyframes/scene_01_start.png       # Scene 1 opening frame
keyframes/scene_01_end.png         # Scene 1 closing frame
keyframes/scene_02_start.png       # Scene 2 opening frame
keyframes/scene_02_end.png         # Scene 2 closing frame
keyframes/scene_03_start.png       # Scene 3 opening frame
keyframes/scene_03_end.png         # Scene 3 closing frame
story/scenes.json                  # Enriched story with scene descriptions
video/scene_01.mp4                 # Scene 1 video (8s)
video/scene_02.mp4                 # Scene 2 video (8s)
video/scene_03.mp4                 # Scene 3 video (8s)
video/final.mp4                    # Final concatenated video (~24s)
```

### What Was Used
- **Gemini Image** (Nano Banana) — Character reference + scene keyframe images
- **Kling Video O3** (fal.ai) — Video generation with Reference I2V + start/end frame interpolation
- **ffmpeg** — Video concatenation

### Technique
Each scene was generated with explicit **start and end frame images**, giving Kling Video precise control over the visual trajectory. Scene transitions are smooth because the end keyframe of each scene matches the start keyframe of the next.

### Next Steps
- Add music or narration to `video/final.mp4` in post-production
- Re-generate individual scenes by updating keyframes and re-running video generation
- Try **pro** quality for higher fidelity
- Experiment with different art styles
</note>

