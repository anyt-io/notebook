---
schema: "2.0"
name: youtube-podcast-to-ebook
workdir: anyt_workspace_podcast_ebook
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

# youtube-podcast-to-ebook

<note id="overview" label="Overview">
## YouTube Podcast to Ebook

This notebook converts a YouTube podcast video into a polished magazine-style ebook (EPUB). The AI analyzes the transcript, proposes structured sections with timestamp links, and you refine the outline before the article is generated.

### Pipeline
1. **Input** — Enter the YouTube video URL
2. **Setup** — Install youtube-downloader and ebook skills
3. **Download** — Fetch transcript (text + JSON) and cover image
4. **Analyze** — AI identifies sections, timestamps, and key quotes
5. **Review Sections** — Edit section outline before writing
6. **Screenshots** — Capture video frames at each section's timestamp
7. **Settings** — Choose language, title, author, cover options
8. **Write Article** — AI writes a flowing magazine-style article with embedded screenshots and watch links
9. **Review Article** — Check the article before conversion
10. **Convert** — Generate EPUB using the ebook skill
</note>

<input id="video-url" label="Video URL">
## YouTube Video URL

Paste the YouTube podcast video URL to get started.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "youtubeUrl",
      "type": "text",
      "label": "YouTube URL",
      "description": "The YouTube podcast video URL",
      "required": true,
      "placeholder": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
  ]
}
</form>
</input>

<shell id="install-skills" label="Install Skills">
#!/bin/bash
echo "=== Installing youtube-downloader skill ==="
npx @anytio/pspm@latest add @user/anyt/youtube-downloader -y

echo ""
echo "=== Installing ebook skill ==="
npx @anytio/pspm@latest add @user/anyt/ebook -y

echo ""
echo "=== Verify Installed Skills ==="
ls -la .pspm/skills/anyt/youtube-downloader/ 2>/dev/null && echo "youtube-downloader: OK" || echo "youtube-downloader: MISSING"
ls -la .pspm/skills/anyt/ebook/ 2>/dev/null && echo "ebook: OK" || echo "ebook: MISSING"
</shell>

<task id="download-content" label="Download Content">
## Download Transcript and Cover Image

Use the **youtube-downloader** skill to download content for the **YouTube URL** from user input.

### Requirements
1. Download the transcript in both **text** and **JSON** formats to `transcripts/`
2. Download the cover/thumbnail image to `cover/`
3. Verify all files were created and report file sizes

**Output:** transcripts/<video-id>.txt, transcripts/<video-id>.json, cover/<video-id>.jpg
</task>

<task id="analyze-transcript" label="Analyze Transcript">
## Analyze Transcript and Propose Sections

Read the transcript JSON file from `transcripts/` and analyze the podcast content to propose structured sections.

### Requirements
1. Read the JSON transcript from `transcripts/` (array of segments with `text`, `start`, and `duration` fields)
2. Extract the video ID from the transcript filename
3. Analyze the content and identify **5-10 natural topic sections** based on:
   - Topic changes and thematic shifts
   - Speaker transitions or conversation pivots
   - Logical content boundaries
4. For each section, determine:
   - **Title**: A descriptive, engaging section title
   - **Start/end timestamps**: When the section begins and ends (in seconds)
   - **Key topics**: Main topics covered in the section
   - **Summary**: A brief 1-2 sentence summary
   - **Notable quotes**: 2-3 direct quotes from the transcript worth highlighting
   - **YouTube timestamp link**: Direct link to that moment in the video (e.g., `https://youtube.com/watch?v=VIDEO_ID&t=120`)
   - **Representative timestamp**: A timestamp (in seconds) for capturing a meaningful screenshot — pick a moment in the middle of an important visual/topic moment, not necessarily the start
5. Save the analysis to `sections.json`

### Output Format (`sections.json`)
```json
{
  "videoTitle": "Original Video Title",
  "videoUrl": "https://youtube.com/watch?v=VIDEO_ID",
  "videoId": "VIDEO_ID",
  "totalDuration": 3600,
  "sections": [
    {
      "id": 1,
      "title": "Section Title",
      "startTime": 0,
      "endTime": 300,
      "keyTopics": ["topic1", "topic2"],
      "summary": "Brief summary of this section...",
      "notableQuotes": ["Interesting quote from the speaker...", "Another key quote..."],
      "youtubeLink": "https://youtube.com/watch?v=VIDEO_ID&t=0",
      "representativeTimestamp": 150
    }
  ]
}
```

**Output:** sections.json
</task>

<break id="review-sections" label="Review Sections">
## Review Section Breakdown

Check `sections.json` to verify the proposed sections before the article is written.

**Things to check:**
- Are the section titles descriptive and engaging?
- Should any sections be merged (too granular) or split (too broad)?
- Are there sections covering uninteresting content that should be removed?
- Are the notable quotes accurate and worth highlighting?

Edit `sections.json` directly to adjust titles, merge/split sections, change the recommended length, or remove sections you don't want included.
</break>

<task id="capture-screenshots" label="Capture Screenshots">
## Capture Video Screenshots at Section Timestamps

Use the **youtube-downloader** skill to capture frame images at each section's start timestamp from `sections.json`.

### Requirements
1. Read `sections.json` and collect the `representativeTimestamp` (in seconds) for each section
2. Use the screenshot capture feature of the youtube-downloader skill with:
   - The **YouTube URL** from user input
   - All section start timestamps as a comma-separated list
   - Output to `frames/` directory
   - Prefix: `section`
3. Verify the screenshots were captured and report the results

**Output:** frames/section_001.jpg, frames/section_002.jpg, ...
</task>

<input id="article-settings" label="Article Settings">
## Article Settings

Now that you've seen the content, configure the article output.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "articleLength",
      "type": "select",
      "label": "Article Length",
      "description": "How detailed should the article be",
      "default": "medium",
      "options": [
        { "value": "short", "label": "Short (~1500 words)" },
        { "value": "medium", "label": "Medium (~3000 words)" },
        { "value": "long", "label": "Long (~5000 words)" },
        { "value": "full", "label": "Full (comprehensive, all details)" }
      ]
    },
    {
      "name": "articleLanguage",
      "type": "select",
      "label": "Article Language",
      "description": "Language for the generated article",
      "default": "en",
      "options": [
        { "value": "en", "label": "English" },
        { "value": "zh", "label": "中文" },
        { "value": "ja", "label": "日本語" },
        { "value": "ko", "label": "한국어" },
        { "value": "es", "label": "Español" },
        { "value": "fr", "label": "Français" },
        { "value": "de", "label": "Deutsch" }
      ]
    },
    {
      "name": "titleOverride",
      "type": "text",
      "label": "Article Title (optional)",
      "description": "Leave empty for an AI-generated title based on the content",
      "placeholder": "My Custom Article Title"
    },
    {
      "name": "authorName",
      "type": "text",
      "label": "Author / Source",
      "description": "Author name or podcast source for attribution",
      "placeholder": "The Podcast Name"
    },
    {
      "name": "useCoverImage",
      "type": "checkbox",
      "label": "Use YouTube Thumbnail as Cover",
      "description": "Embed the video thumbnail as the EPUB cover image",
      "default": true
    }
  ]
}
</form>
</input>

<task id="write-article" label="Write Article">
## Write Magazine-Style Article

Read the user-reviewed `sections.json`, the full transcript, and the captured screenshots to write a polished, magazine-style article.

### Requirements
1. Read `sections.json` (user-reviewed), the text transcript from `transcripts/`, and the screenshot files from `frames/`
2. Write the article in the **Article Language** selected by the user
3. Use the **Article Title** if provided, otherwise generate an engaging title from the content
4. Respect the **Article Length** selected by the user:
   - `short`: ~1500 words — concise, key highlights only
   - `medium`: ~3000 words — balanced depth and readability
   - `long`: ~5000 words — detailed coverage of all sections
   - `full`: comprehensive — include all details, quotes, and context from every section with no length constraint

### Article Structure
Write `article.md` with the following structure:

1. **Title**: H1 heading — the article title
2. **Byline**: Author/source attribution (from user input) and original video link
3. **Outline**: A linked table of contents listing all section titles as markdown anchor links (e.g., `- [Section Title](#section-title)`)
4. **Introduction**: A compelling 2-3 paragraph opening that hooks the reader and sets the stage
5. **Sections**: For each section in `sections.json`:
   - H2 heading with the section title
   - Embed the corresponding screenshot image: `![](frames/section_NNN.jpg)`
   - A short watch link: `[Watch](youtube_link)` — using the section's `youtubeLink`
   - Well-written editorial prose that:
     - Transforms conversational transcript into polished written form
     - Integrates direct quotes naturally (clean up filler words, false starts)
     - Explains technical concepts or jargon for a general audience
     - Maintains the speaker's voice and personality
     - Connects ideas across the conversation
6. **Key Takeaways**: A closing section with bullet-point highlights
7. **Source**: Link back to the original YouTube video

### Writing Guidelines
- Write as a skilled magazine editor — authoritative, engaging, and accessible
- Use H2 headings (`##`) for each section — matching titles from `sections.json`
- Use `![](frames/section_NNN.jpg)` to embed each section's screenshot (section 1 → `section_001.jpg`, section 2 → `section_002.jpg`, etc.)
- Use `[Watch](youtube_link)` as a compact clickable link (not `[Watch this section ▶]`)
- Clean up spoken language into polished prose (remove "um", "like", false starts)
- Preserve the best direct quotes using blockquote format (`>`)
- Explain insider references or technical terms in context
- Each section should flow naturally into the next

**Output:** article.md
</task>

<break id="review-article" label="Review Article">
## Review Article

Review `article.md` before converting to EPUB.

**Things to check:**
- Is the writing quality high and the tone consistent?
- Does the outline at the top list all sections with working anchor links?
- Does each section have an H2 heading, screenshot, and `[Watch]` link?
- Are screenshot images embedded correctly (`![](frames/section_NNN.jpg)`)?
- Is the article in the correct language?
- Are quotes accurate and properly attributed?
- Is the length appropriate for the content?

Edit `article.md` directly to make any final adjustments.
</break>

<task id="convert-epub" label="Convert to EPUB">
## Convert Article to EPUB

Use the **ebook** skill to convert `article.md` into a polished EPUB file.

### Requirements
1. Use the **Article Title** from user input (or extract the H1 from `article.md` if not provided)
2. Use the **Author / Source** from user input
3. If **Use YouTube Thumbnail as Cover** is enabled, include the cover image from `cover/`
4. Convert to EPUB format and save to `output/`
5. **Important:** Pass the title (`-t`) and author (`-a`) to the ebook skill so the output file is named after the title (e.g., `output/my-article-title.epub`), not the default `article.epub`
6. Verify the EPUB was created and report the file size

**Output:** output/<title>.epub
</task>

<note id="complete" label="Complete">
## Ebook Generated

### Generated Files
```
anyt_workspace_podcast_ebook/
├── transcripts/
│   ├── <video-id>.json          # Structured transcript (JSON)
│   └── <video-id>.txt           # Plain text transcript
├── cover/
│   └── <video-id>.jpg           # Video thumbnail
├── frames/
│   ├── section_001.jpg          # Screenshot per section
│   ├── section_002.jpg
│   └── ...
├── sections.json                # Section breakdown (user-reviewed)
├── article.md                   # Magazine-style article with embedded screenshots
└── output/
    └── <title>.epub             # Final EPUB ebook
```

### Next Steps
- Open the EPUB file in your favorite ebook reader (Apple Books, Calibre, etc.)
- Share the ebook or convert to other formats
- Re-run individual cells to adjust sections, article content, or settings
</note>

