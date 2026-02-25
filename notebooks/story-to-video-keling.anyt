---
schema: "2.0"
name: story-to-video-keling
description: Generate a short AI video from a story idea using Gemini Image (Nano
  Banana) for character design and Kling Video (fal.ai) for video generation
version: 1.0.0
workdir: anyt_workspace_story_to_video_keling
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

# story-to-video-keling

<note id="overview" label="Overview">
## Story-to-Video Pipeline (Keling)

This notebook generates a short AI video from a story idea using **Gemini Image** (Nano Banana) for character design and **Kling Video O3** (fal.ai) for video generation.

### Flow
1. **Check Environment** - Verify `GEMINI_API_KEY`, `FAL_KEY`, `uv`, and `ffmpeg` are available
2. **Install Skills** - Add gemini-image and keling-video skills
3. **Story Input** - Enter your story idea (default provided for quick test)
4. **Generate Characters** - AI creates 3 named character candidates (`candidate1`, `candidate2`, `candidate3`)
5. **Pick Character** - Choose which character design you like
6. **Character Perspectives** - Generate more angles of the chosen character
7. **Enrich Story** - AI expands the story into scenes with visual descriptions
8. **Generate Video** - Create video clips sequentially, chaining last frames between scenes for smooth transitions
9. **Concat Video** - Merge all scene clips into one final video

### Key Differences from Gemini Video Pipeline
- Uses **Kling Video O3** (fal.ai) instead of Veo 3.1
- Supports **Reference I2V** mode with `@Element1` syntax for character consistency
- **Chains scenes** using last-frame extraction — each scene's start image is the previous scene's last frame
- Provides **standard** and **pro** quality tiers
- Duration range: **3–15 seconds** per scene
- Requires `FAL_KEY` in addition to `GEMINI_API_KEY`

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
mkdir -p characters story video
echo "Created: characters/ story/ video/"
</shell>

<input id="story-input" label="Story Idea">
## What's Your Story?

Enter a story concept. A default is provided so you can quickly test the full pipeline.

<form type="json">
{
  "fields": [
    {
      "name": "storyIdea",
      "type": "textarea",
      "label": "Story Idea",
      "required": true,
      "default": "A tiny robot named Bolt lives in a junkyard. One night, Bolt discovers a glowing crystal that gives him the power to fly. He soars above the city, seeing the world from above for the first time. He finds a lost bird on a rooftop and helps it find its way home, then flies back to the junkyard as the sun rises.",
      "rows": 5,
      "placeholder": "Describe your story idea..."
    },
    {
      "name": "characterName",
      "type": "text",
      "label": "Main Character Name",
      "required": true,
      "default": "Bolt"
    },
    {
      "name": "imageModel",
      "type": "select",
      "label": "Image Model",
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
      "default": "3d-animated",
      "options": [
        { "value": "3d-animated", "label": "3D Animated (Pixar-like)" },
        { "value": "anime", "label": "Anime / Manga" },
        { "value": "watercolor", "label": "Watercolor Illustration" },
        { "value": "photorealistic", "label": "Photorealistic" }
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
      "name": "videoDuration",
      "type": "select",
      "label": "Scene Duration",
      "default": "5",
      "options": [
        { "value": "5", "label": "5 seconds" },
        { "value": "8", "label": "8 seconds" },
        { "value": "10", "label": "10 seconds" },
        { "value": "15", "label": "15 seconds (max)" }
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

<task id="generate-characters" label="Generate Character Concepts">
Using the **gemini-image** skill, generate 3 different character concept images for the main character from `story-input`.

- Use the `imageModel` from `story-input` (default: `gemini-2.5-flash-image`)
- Craft 3 distinct prompts based on the story, character name, and art style — front-facing view, simple background, varying design details (proportions, colors, accessories)
- Use aspect ratio `1:1` for character portraits
- Save with filenames `candidate1.png`, `candidate2.png`, `candidate3.png` in `characters/`
- Each candidate should explore a different visual interpretation of the character

**Output:** characters/candidate1.png, characters/candidate2.png, characters/candidate3.png
</task>

<input id="pick-character" label="Pick Your Character">
## Choose Your Character

Review the 3 generated character candidates in the `characters/` folder and pick your favorite.

<form type="json">
{
  "fields": [
    {
      "name": "chosenImage",
      "type": "select",
      "label": "Chosen Character",
      "required": true,
      "default": "candidate1.png",
      "options": [
        { "value": "candidate1.png", "label": "Candidate 1" },
        { "value": "candidate2.png", "label": "Candidate 2" },
        { "value": "candidate3.png", "label": "Candidate 3" }
      ],
      "description": "Select your favorite character design from the candidates in characters/"
    },
    {
      "name": "feedback",
      "type": "textarea",
      "label": "Feedback (optional)",
      "required": false,
      "default": "Looks great, use this design as-is",
      "rows": 2,
      "placeholder": "Any adjustments? e.g., 'make the eyes bigger' or 'add a scarf'"
    }
  ]
}
</form>
</input>

<task id="character-perspectives" label="Generate Character Perspectives">
Using the **gemini-image** skill, generate 3 additional perspective images of the chosen character from `pick-character`.

- Use the `imageModel` from `story-input` (default: `gemini-2.5-flash-image`)
- Use the chosen image as input to maintain visual consistency
- Generate: **side view**, **action pose** (relevant to the story), **environment shot** (character in the story's setting)
- Apply any user feedback from `pick-character`
- Use aspect ratio `16:9`, save to `characters/perspectives/`

**Output:** characters/perspectives/gemini_*.png (3 images)
</task>

<break id="review-characters" label="Review All Characters">
Review all character images before proceeding to story enrichment and video generation.

Files to check:
- `characters/candidate1.png`, `candidate2.png`, `candidate3.png` - Original 3 character candidates
- `characters/perspectives/` - 3 perspective images of the chosen character

Continue when you're satisfied with the character designs.
</break>

<task id="enrich-story" label="Enrich Story into Scenes">
Expand the story from `story-input` into 3-4 video scenes.

For each scene, write:
- **Video prompt**: Detailed cinematic description (2-3 sentences) — action, camera angle, lighting, mood, character appearance, art style. Use `@Element1` to reference the main character element in the prompt. If `generateAudio` is enabled in `story-input`, include audio cues (dialogue in quotes, sound effects, ambient sounds).
- **Element image**: The best front-facing character image from `characters/` to use as the `--element` frontal image for Kling Video's Reference I2V mode.
- **Element refs**: Pick 1-2 additional angle images from `characters/perspectives/` to use as `--element-ref` for better character consistency.

Save as JSON with this structure:
```json
{
  "title": "Story Title",
  "character": "Character appearance description",
  "artStyle": "chosen style",
  "scenes": [
    {
      "id": 1,
      "title": "Scene Title",
      "videoPrompt": "@Element1 discovers a glowing crystal in the junkyard. Close-up shot, dramatic blue lighting...",
      "elementImage": "characters/candidate1.png",
      "elementRefs": ["characters/perspectives/side_view.png"],
      "duration": "5"
    }
  ]
}
```

Use the `videoDuration` from `story-input` as the default duration for each scene.

**Output:** story/scenes.json
</task>

<task id="generate-videos" label="Generate Videos">
Using the **keling-video** skill, generate videos for each scene in `story/scenes.json` **sequentially**, chaining the last frame of each scene as the start image for the next to create smooth visual continuity.

### Scene 1 (no start image)
- Use the scene's `videoPrompt` as the prompt (includes `@Element1` references)
- Use the scene's `elementImage` with `--element` for character reference (Reference I2V mode)
- Use the scene's `elementRefs` with `--element-ref` flags for additional character angles
- Use `--quality`, `--aspect-ratio`, `--duration` from `story-input`
- If `generateAudio` is enabled, add `--audio`
- Save as `video/scene_01.mp4` using `--filename scene_01.mp4 -o video/`

### Scenes 2+ (chain from previous scene's last frame)
After each scene video is generated:
1. **Extract the last frame** from the previous scene using ffmpeg:
   ```
   ffmpeg -sseof -0.1 -i video/scene_01.mp4 -frames:v 1 -q:v 2 video/scene_01_lastframe.jpg
   ```
2. **Generate the next scene** using the last frame as `--start-image` for visual continuity:
   - Same flags as scene 1
   - Add `--start-image video/scene_01_lastframe.jpg` to seamlessly continue from where the previous scene ended

Repeat for all remaining scenes. Each scene picks up visually from where the last one left off.

**Output:** video/scene_01.mp4, video/scene_02.mp4, video/scene_03.mp4
</task>

<task id="concat-video" label="Concatenate Final Video">
Merge all scene videos into a single final video using ffmpeg.

- Concatenate all scene clips from `video/` in filename order (`scene_01.mp4`, `scene_02.mp4`, ...) to match the story sequence
- Use ffmpeg concat demuxer (no re-encoding) for fast lossless merging
- Save the final video as `video/final.mp4`

**Output:** video/final.mp4
</task>

<note id="complete" label="Pipeline Complete">
## Story-to-Video Complete

### Generated Files
```
characters/candidate1.png     # Character concept option 1
characters/candidate2.png     # Character concept option 2
characters/candidate3.png     # Character concept option 3
characters/perspectives/      # Chosen character from different angles
story/scenes.json             # Enriched story with scene descriptions
video/scene_*.mp4             # Individual video clips
video/final.mp4               # Final concatenated video
```

### What Was Used
- **Gemini Image** (Nano Banana / `gemini-2.5-flash-image`) for character design
- **Kling Video O3** (fal.ai) for video generation with Reference I2V character consistency
- **ffmpeg** for video concatenation

### Next Steps
- Add music or narration to `video/final.mp4` in post-production
- Re-generate individual scenes by re-running the video generation cell
- Try different art styles, quality tiers, or aspect ratios by changing the story input
- Try **pro** quality for higher fidelity video generation
</note>
