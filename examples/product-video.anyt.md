---
name: product-video
version: 1.0.0
workdir: video_output
inputs:
  productName: My Product
  videoType: demo
  duration: 85
  language: en-US
  outputFormats: 1080p,720p
  enableBgm: true
  enableSubtitles: true
---

# Product Video Production

A comprehensive workflow for creating professional product videos.

<note id="overview">
## Product Video Pipeline

This workflow orchestrates video production through 6 stages:

1. **Storyboarding** - Design scenes and write voiceover scripts
2. **User Review** - Checkpoint for approving the storyboard
3. **Recording** - Capture screen recordings (for demo videos)
4. **Voiceover** - Generate text-to-speech narration
5. **Background Music** - Mix BGM with voiceover (optional)
6. **Subtitles** - Generate subtitle files (optional)
7. **Compositing** - Final video rendering

### Inputs
- `productName`: Name of the product
- `videoType`: demo | slideshow | mixed
- `duration`: Target duration in seconds
- `language`: en-US | zh-CN
- `outputFormats`: Comma-separated (1080p, 720p, vertical, square)
- `enableBgm`: Include background music
- `enableSubtitles`: Generate subtitles
</note>

<shell id="setup">
#!/bin/bash
mkdir -p working public/recordings public/audio out
echo "Video production directories created"
</shell>

<task id="storyboard">
## Design Video Storyboard

Create a detailed storyboard for the product video based on the inputs.

Requirements:
1. Design scenes appropriate for the video type
2. Write voiceover scripts for each scene
3. Ensure total duration matches target (±2 seconds tolerance)

Output Files:
- `working/scenes.json` - Scene configuration with timing
- `working/voiceover_segments.json` - Voiceover text with timing

**Output:** working/scenes.json, working/voiceover_segments.json
</task>

<input id="review-storyboard">
## Review Generated Storyboard

Please review the storyboard and voiceover scripts before production.

### Files to Review
- `working/scenes.json` - Scene layout and timing
- `working/voiceover_segments.json` - Voiceover text content

### Checklist
- [ ] Scene order and flow makes sense
- [ ] Durations are appropriate for each scene
- [ ] All key product features are covered
- [ ] Voiceover text is accurate and natural
- [ ] Total duration matches target
- [ ] Language and tone are appropriate

**Actions:**
- `continue` - Proceed with video production
- `edit` - Modify the storyboard files manually
- `regenerate` - Discard and regenerate the storyboard
</input>

<task id="recording">
## Capture Screen Recordings

**Conditional:** Runs only if videoType is "demo" or "mixed".

Use Playwright to capture browser-based screen recordings.

Requirements:
1. Set up Playwright with 1920x1080 resolution at 30fps
2. Execute the demo script with automated interactions
3. Log all events with timestamps for sync

**Output:** public/recordings/full_demo.mp4, public/recordings/timeline.json
</task>

<task id="voiceover">
## Generate Voiceover Audio

Generate text-to-speech narration using edge-tts.

Requirements:
1. Read voiceover segments from working/voiceover_segments.json
2. Select appropriate voice based on language
3. Generate and synchronize audio segments
4. Merge into final audio track

**Output:** public/audio/synced_voiceover.mp3, public/audio/voiceover_metadata.json
</task>

<task id="bgm">
## Mix Background Music

**Conditional:** Runs only if enableBgm is true.

Mix background music with voiceover at appropriate volume levels.

Requirements:
1. Select appropriate background music
2. Apply volume ducking based on sections
3. Use FFmpeg for mixing with crossfade transitions

**Output:** public/audio/mixed_audio.mp3
</task>

<task id="subtitles">
## Generate Subtitles

**Conditional:** Runs only if enableSubtitles is true.

Generate subtitle files from voiceover segments.

Requirements:
1. Generate Remotion-compatible JSON format
2. Generate standard SRT format
3. Sync at 30fps frame rate

**Output:** public/subtitles.json, out/subtitles.srt
</task>

<input id="review-assets">
## Review Production Assets

All production assets have been generated. Please review before final compositing.

### Generated Assets
- **Recording:** `public/recordings/full_demo.mp4`
- **Voiceover:** `public/audio/synced_voiceover.mp3`
- **Mixed Audio:** `public/audio/mixed_audio.mp3`
- **Subtitles:** `public/subtitles.json`, `out/subtitles.srt`

### Checklist
- [ ] Voiceover audio is clear and well-paced
- [ ] Background music volume levels are appropriate
- [ ] Subtitles are accurate and properly timed
- [ ] Recording captures all intended interactions

**Actions:**
- `continue` - Proceed to final video rendering
- `edit` - Make manual adjustments to assets
- `redo-voiceover` - Regenerate voiceover
</input>

<task id="compositing">
## Render Final Video

Use Remotion to composite all assets into final video outputs.

Requirements:
1. Load all assets (scenes, audio, subtitles, recording)
2. Create scene components with animations
3. Render in all requested output formats
4. Apply quality settings: CRF 18, H.264 codec

**Output:** out/Video-1080p.mp4, out/Video-720p.mp4
</task>

<note id="complete">
## Workflow Complete

Your video project output:

```
video_output/
├── working/
│   ├── scenes.json
│   └── voiceover_segments.json
├── public/
│   ├── recordings/
│   │   ├── full_demo.mp4
│   │   └── timeline.json
│   ├── audio/
│   │   ├── synced_voiceover.mp3
│   │   ├── mixed_audio.mp3
│   │   └── voiceover_metadata.json
│   └── subtitles.json
└── out/
    ├── Video-1080p.mp4
    ├── Video-720p.mp4
    └── subtitles.srt
```

### Next Steps
1. Review final videos in `out/` directory
2. Upload to your distribution platform
3. Use SRT subtitles for accessibility
</note>
