---
schema: "2.0"
name: product-video
version: 2.0.0
workdir: anyt_workspace
---

# product-video

<note id="overview" label="Overview">
## Product Video Pipeline

This notebook generates a professional product demo video using **Remotion** (programmatic video framework).

### Flow
1. **Setup** - Install Remotion skill, scaffold project
2. **Product Info** - Confirm product name, description, and logo path
3. **Storyboard + Voiceover + Scenes** - AI auto-generates everything
4. **Review** - Preview and continue to render
5. **Render** - Final video output with audio

User interaction is minimal — just confirm product info, then review before render.
</note>

<note id="skill-setup" label="Add Skills">
## Remotion Skill Setup

This pipeline uses the **remotion-best-practices** skill to give the AI agent domain knowledge about Remotion's APIs, animation patterns, and best practices.

### Install Skills CLI (one-time global install)
```bash
npm install skills -g
```

### Add Remotion Skill to Workspace
```bash
npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices -y
```

The skill provides 35+ rule files covering media embedding, animation patterns, scene transitions, TailwindCSS integration, subtitle rendering, and more.
</note>

<shell id="install-skills">
#!/bin/bash
echo "=== Installing Skills CLI ==="
npm install skills -g
echo ""
echo "=== Adding Remotion Best Practices Skill to Workspace ==="
npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices -y

echo ""
echo "=== Verify Installed Skills ==="
npx skills list 2>/dev/null || echo "Skills installed successfully"
echo ""
ls -la .skills/ 2>/dev/null || true
</shell>

<input id="product-info">
## Product Information

Confirm or update the product details for the video:

<form type="json">
{
  "fields": [
    {
      "name": "productName",
      "type": "text",
      "label": "Product Name",
      "required": true,
      "default": "AnyT Notebook"
    },
    {
      "name": "productDescription",
      "type": "textarea",
      "label": "Product Description",
      "required": true,
      "default": "AnyT Notebook is the workflow development environment for AI agents. AI agents today work like chatbots — you give them a prompt, hope they get everything right in one shot, and when things break halfway through, you start over. AnyT Notebook changes this by giving AI agents a workflow layer: visible steps, human checkpoints, and recoverable state.\n\nThe Problem:\n- AI agents have no visibility — you can't see the plan before it runs\n- No control — you can't pause, review, or redirect mid-execution\n- No recovery — if step 4 of 8 fails, you redo everything from scratch\n- No separation — AI handles things a simple shell command could do faster\n\nThe Solution:\nAnyT Notebook brings a Jupyter-style notebook interface to AI agent workflows. Break complex tasks into discrete cells, add human review checkpoints where they matter, mix AI and deterministic steps, and run with full visibility and control.\n\nFive Cell Types:\n- Task: AI agent executes natural language instructions (Claude Code, Codex)\n- Shell: Run scripts directly — fast, deterministic, no AI overhead\n- Input: Pause for user input with forms (text, select, checkbox)\n- Note: Markdown documentation and progress checkpoints\n- Break: Pause execution for human review before continuing\n\nWorkflow Development Lifecycle:\n- Create: Write cells — tasks for AI, shell for scripts, notes for docs\n- Debug: Add break cells as checkpoints, run step by step, inspect outputs\n- Iterate: Review results, fix failing steps, add/remove cells as needed\n- Harden: Remove breakpoints when confident, run end-to-end\n- Share: Version the .anyt.md file, share debugged workflows with your team",
      "rows": 8
    },
    {
      "name": "logoPath",
      "type": "text",
      "label": "Logo Image Path",
      "required": true,
      "default": "../apps/vscode/icon.png",
      "placeholder": "Path to product logo image (png/svg)"
    }
  ]
}
</form>
</input>

<task id="setup-remotion">
## Setup Remotion Project

Create a new Remotion video project using pnpm as the package manager.

### Requirements
1. Create a new Remotion project in the `remotion-video/` directory using pnpm:
   - Use the Remotion CLI: `pnpm create video@latest remotion-video`
   - Choose the **Hello World** template as a starting point
   - Use **pnpm** as the package manager
2. After project creation, install additional dependencies with pnpm:
   ```bash
   cd remotion-video
   pnpm add @remotion/tailwind tailwindcss
   ```
3. Copy the product logo (from `logoPath` in `product-info` input) into the Remotion public directory:
   ```bash
   cp <logoPath> remotion-video/public/logo.png
   ```
4. Show the project structure

### Notes
- The remotion-best-practices skill is already installed in the workspace `.skills/` directory
- Use pnpm for all package management throughout this project

**Output:** remotion-video/package.json, remotion-video/src/Root.tsx
</task>

<task id="storyboard">
## Design Video Storyboard

Create a detailed storyboard and a product markdown brief for the video. Use the product name, description, and logo from the `product-info` input. The logo has been copied to `remotion-video/public/logo.png` by the previous step.

### Requirements
1. First, generate a **product brief** markdown file summarizing the product, its key features, target audience, and value proposition based on the product description
2. **Auto-select** visual style and color scheme that best fits the product:
   - Analyze the product description to determine tone (tech/professional/playful)
   - Choose a primary and accent color that complement the product logo
   - Pick a visual style (modern-minimal, tech-demo, cinematic, or playful)
3. Design 5-7 scenes for a ~60 second video:
   - **Opening** (5-8s): Product logo (use `logo.png`), name, and tagline with entrance animation
   - **Problem** (8-12s): Show the problem the product solves
   - **Solution** (10-15s): Introduce the product as the solution
   - **Features** (15-20s): Highlight 3-4 key features with visuals
   - **Demo** (10-15s): Quick product walkthrough
   - **CTA** (5-8s): Call to action with product URL
4. Write voiceover narration text for each scene in English
5. Assign timing (start frame, duration in frames at 30fps)
6. Define visual elements, transitions, and animations per scene

### Output Files
- `product-brief.md` - Product summary and video creative direction
- `remotion-video/src/data/storyboard.json` - Scene definitions with timing, style, and colors
- `remotion-video/src/data/voiceover.json` - Narration text segments with timing

### Storyboard JSON Structure
```json
{
  "meta": {
    "productName": "...",
    "tagline": "...",
    "totalDuration": 60,
    "fps": 30,
    "style": "modern-minimal",
    "colors": { "primary": "#6366f1", "accent": "#06b6d4", "background": "#0f172a" }
  },
  "scenes": [
    {
      "id": "opening",
      "title": "Opening",
      "startFrame": 0,
      "durationFrames": 180,
      "description": "Product logo entrance with gradient background",
      "voiceover": "Introducing AnyT Notebook...",
      "visuals": { "background": "gradient", "elements": ["logo", "title", "tagline"] },
      "transition": { "type": "fade", "durationFrames": 15 }
    }
  ]
}
```

**Output:** product-brief.md, remotion-video/src/data/storyboard.json, remotion-video/src/data/voiceover.json
</task>

<break id="review-storyboard">
Review the generated storyboard and product brief before proceeding.

Files to check:
- `product-brief.md` - Product summary and creative direction
- `remotion-video/src/data/storyboard.json` - Scene layout, timing, auto-selected style and colors
- `remotion-video/src/data/voiceover.json` - Narration scripts
</break>

<task id="generate-voiceover">
## Generate Voiceover Audio

Generate text-to-speech audio from the voiceover scripts using edge-tts and synchronize with scene timing.

### Requirements
1. Use `uvx` to run edge-tts (no install needed): `uvx edge-tts --voice "..." --text "..." --write-media file.mp3`
2. Read voiceover segments from `remotion-video/src/data/voiceover.json`
3. Select an appropriate voice based on the language:
   - **en-US**: `en-US-GuyNeural` (narrator), `en-US-JennyNeural` (friendly), `en-US-JasonNeural` (tech)
   - **zh-CN**: `zh-CN-YunjianNeural` (tech), `zh-CN-XiaoxiaoNeural` (friendly)
4. For each voiceover segment:
   - Generate audio: `uvx edge-tts --voice "en-US-GuyNeural" --text "..." --write-media segment_XX.mp3`
   - Adjust speech rate if needed to match target duration (`--rate=+10%` or `--rate=-5%`)
5. Place individual segment audio files in `remotion-video/public/audio/`
6. Create an audio metadata file mapping each segment to its audio file and timing

### Output Files
- `remotion-video/public/audio/vo_00.mp3` to `vo_NN.mp3` - Individual voiceover segments
- `remotion-video/src/data/audio-metadata.json` - Audio file mapping with timing info

**Output:** remotion-video/public/audio/vo_00.mp3, remotion-video/src/data/audio-metadata.json
</task>

<task id="create-scenes">
## Build Remotion Scene Components

Using the storyboard from `remotion-video/src/data/storyboard.json`, create React components for each scene in the Remotion project.

### Requirements
1. Read the storyboard JSON (includes auto-selected style and colors) and audio metadata from `remotion-video/src/data/audio-metadata.json`
2. Create a main composition that sequences all scenes **with audio**
3. Build individual scene components with animations using Remotion's `useCurrentFrame()`, `interpolate()`, and `spring()` APIs
4. Apply the visual style and color scheme from `storyboard.json` meta
5. Use the product logo via `staticFile("logo.png")` in the Opening scene
6. Use TailwindCSS for styling where appropriate
7. Add smooth transitions between scenes (fade, slide, scale)
8. **Audio integration in the main composition:**
   - Use Remotion's `<Audio>` component to embed voiceover segments at correct frame offsets
   - Load audio files via `staticFile()` (e.g., `staticFile("audio/vo_00.mp3")`)
   - Place each voiceover `<Audio>` in a `<Sequence>` matching its `startFrame` from audio-metadata.json

### Scene Components to Create
- `Opening.tsx` - Logo reveal (from `logo.png`), title animation, tagline fade-in
- `Problem.tsx` - Problem statement with icon animations
- `Solution.tsx` - Product introduction with feature preview
- `Features.tsx` - Feature cards with staggered entrance
- `Demo.tsx` - Product screenshots/mockups with annotations
- `CallToAction.tsx` - CTA with product URL, animated button

### Main Composition
- `Video.tsx` - Root composition using `<Series>` to sequence scenes, `<Audio>` for voiceover
- `Root.tsx` - Register composition with correct dimensions and duration

### Follow Remotion best practices from the installed skill:
- Use `<AbsoluteFill>` for scene layouts
- Use `<Sequence>` and `<Series>` for timing
- Use `<Audio>` with `staticFile()` for voiceover
- Use `spring()` for natural animations
- Use `staticFile()` for assets in `/public`

**Output:** remotion-video/src/Video.tsx, remotion-video/src/Root.tsx, remotion-video/src/scenes/*.tsx
</task>

<task id="subtitles">
## Generate Subtitles

Create subtitle data from the voiceover scripts for the video.

### Requirements
1. Read voiceover segments from `remotion-video/src/data/voiceover.json`
2. Generate Remotion-compatible subtitle component:
   - Parse each voiceover segment into display-friendly chunks (max 2 lines, ~10 words each)
   - Map text to frame ranges at 30fps
   - Style: bottom-center, semi-transparent background, readable font
3. Generate standard SRT file for distribution
4. Integrate the subtitle component into the main Video composition

### Output Files
- `remotion-video/src/components/Subtitles.tsx` - Remotion subtitle overlay component
- `remotion-video/src/data/subtitles.json` - Subtitle timing data
- `remotion-video/out/subtitles.srt` - Standard SRT file

**Output:** remotion-video/src/components/Subtitles.tsx, remotion-video/src/data/subtitles.json
</task>

<break id="review-before-render">
All scenes and audio are ready. You can preview the video locally:

```bash
cd remotion-video && pnpm remotion preview
```

Review the preview, then continue to render the final video.
</break>

<shell id="render-video">
#!/bin/bash
cd remotion-video

echo "=== Rendering Video ==="
pnpm remotion render src/index.ts ProductVideo out/product-video.mp4 \
  --codec=h264 \
  --crf=18

echo ""
echo "=== Render Complete ==="
ls -lh out/
echo ""
echo "Output: remotion-video/out/product-video.mp4"
</shell>

<task id="task-fj1e">
previous cell failed with 
Getting composition

⚡️ Cached bundle. Subsequent renders will be faster.

[stderr] Was not able to close puppeteer page ProtocolError: Protocol error (Target.closeTarget): No target found for targetId
[stderr]     at createProtocolError (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/@remotion+renderer@4.0.419_react-dom@19.2.3_react@19.2.3__react@19.2.3/node_modules/@remotion/renderer/dist/browser/Connection.js:239:25)
[stderr]     at #onMessage (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/@remotion+renderer@4.0.419_react-dom@19.2.3_react@19.2.3__react@19.2.3/node_modules/@remotion/renderer/dist/browser/Connection.js:106:37)
[stderr]     at WebSocket.<anonymous> (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/@remotion+renderer@4.0.419_react-dom@19.2.3_react@19.2.3__react@19.2.3/node_modules/@remotion/renderer/dist/browser/NodeWebSocketTransport.js:58:32)
[stderr]     at callListener (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/ws@8.17.1/node_modules/ws/lib/event-target.js:290:14)
[stderr]     at WebSocket.onMessage (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/ws@8.17.1/node_modules/ws/lib/event-target.js:209:9)
[stderr]     at WebSocket.emit (node:events:518:28)
[stderr]     at Receiver.receiverOnMessage (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/ws@8.17.1/node_modules/ws/lib/websocket.js:1211:20)
[stderr]     at Receiver.emit (node:events:518:28)
[stderr]     at Receiver.dataMessage (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/ws@8.17.1/node_modules/ws/lib/receiver.js:594:14)
[stderr]     at Receiver.getData (/Users/bsheng/work/anyt-notebook/node_modules/.pnpm/ws@8.17.1/node_modules/ws/lib/receiver.js:496:10) {
[stderr]   code: undefined,
[stderr]   originalMessage: 'No target found for targetId'
[stderr] }
An error occurred:

at ../../../node_modules/.pnpm/@remotion+studio@4.0.419_react-dom@19.2.3_react@19.2.3__react@19.2.3/node_modules/@remotion/studio/dist/esm/renderEntry.mjs:312

310 │ const selectedComp = compositions.find((c) => c.id === compId);

311 │ if (!selectedComp) {

312 │   throw new Error(Could not find composition with ID ${compId}. Available compositions: ${compositions.map((c) => c.id).join(", ")});

313 │ }

314 │ const abortController = new AbortController;

315 │ const handle = globalDelayRender(Running the calculateMetadata() function for composition ${compId});

[stderr]  Error  Error: Could not find composition with ID ProductVideo. Available compositions: AnyTNotebook
=== Render Complete ===

total 8

-rw-r--r--@ 1 bsheng  staff   1.8K Feb  5 17:52 subtitles.srt

Output: remotion-video/out/product-video.mp4
</task>

<task id="task-jm7m">
the correct githib url is github.com/anyti-io/notebook , at the same time , it seems the time and voice have some overlap , multiple sound overlap each other , we need add more time gap, regenerate the vidoe
</task>

<note id="complete">
## Pipeline Complete

### Generated Files
```
remotion-video/
├── public/
│   ├── logo.png                     # Product logo
│   └── audio/
│       └── vo_00.mp3 ... vo_NN.mp3  # Voiceover segments
├── src/
│   ├── Root.tsx                 # Composition registration
│   ├── Video.tsx                # Main composition (scenes + audio)
│   ├── scenes/
│   │   ├── Opening.tsx          # Logo reveal + title
│   │   ├── Problem.tsx          # Problem statement
│   │   ├── Solution.tsx         # Product introduction
│   │   ├── Features.tsx         # Feature highlights
│   │   ├── Demo.tsx             # Product walkthrough
│   │   └── CallToAction.tsx     # CTA + URL
│   ├── components/
│   │   └── Subtitles.tsx        # Caption overlay
│   └── data/
│       ├── storyboard.json      # Scene definitions + style + colors
│       ├── voiceover.json       # Narration scripts
│       ├── audio-metadata.json  # Audio file mapping + timing
│       └── subtitles.json       # Caption timing
└── out/
    ├── product-video.mp4        # Final rendered video (with audio)
    └── subtitles.srt            # SRT captions
```

### Next Steps
- Preview: `cd remotion-video && pnpm remotion preview`
- Re-render: `cd remotion-video && pnpm remotion render`
- Different formats: Re-render with `--width` / `--height` flags
</note>

