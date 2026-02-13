---
schema: "2.0"
name: page-to-rednote
description: Convert a blog page into Xiaohongshu/Rednote card images
workdir: rednote_output
dependencies:
  rednote: 0.1.0
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

# page-to-rednote

<note id="overview" label="Overview">
## Page to Rednote Cards

This notebook converts a blog page into Xiaohongshu/Rednote-style card images (1080x1440px PNG).

### Pipeline
1. **Input** — Enter blog URL, select template and options
2. **Setup** — Install rednote skill and create directories
3. **Fetch & Extract** — AI fetches the page and extracts article content
4. **Review Content** — Verify extracted article before card generation
5. **Generate Card Markdown** — AI reformats content into card-sized sections
6. **Render Cards** — Use rednote skill to generate PNG card images
7. **Review Cards** — Verify final card images
</note>

<input id="blog-settings" label="Blog Settings">
## Blog Settings

Enter the blog URL and configure card generation options.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "blogUrl",
      "type": "text",
      "label": "Blog URL",
      "description": "URL of the blog post to convert",
      "required": true,
      "placeholder": "https://z.ai/blog/glm-5"
    },
    {
      "name": "template",
      "type": "select",
      "label": "Card Template",
      "description": "Visual style for the generated cards",
      "default": "apple-notes",
      "options": [
        { "value": "apple-notes", "label": "Apple Notes (default)" },
        { "value": "swiss", "label": "Swiss" },
        { "value": "magazine", "label": "Magazine" },
        { "value": "aurora", "label": "Aurora" },
        { "value": "dark", "label": "Dark" },
        { "value": "corporate", "label": "Corporate" },
        { "value": "blank", "label": "Blank" }
      ]
    },
    {
      "name": "watermark",
      "type": "text",
      "label": "Watermark",
      "description": "Watermark text on cards (leave empty for default 'AnyT')",
      "placeholder": "@MyHandle"
    },
    {
      "name": "language",
      "type": "select",
      "label": "Language",
      "description": "Language for card UI elements",
      "default": "en",
      "options": [
        { "value": "en", "label": "English" },
        { "value": "zh", "label": "中文" }
      ]
    }
  ]
}
</form>
</input>

<shell id="install-skill" label="Install Skill & Setup">
#!/bin/bash
echo "=== Installing rednote skill ==="
npx @anytio/pspm@latest add @user/anyt/rednote -y
</shell>

<task id="fetch-extract" label="Fetch & Extract Content">
## Fetch Blog Page and Extract Content

Fetch the blog page at the **Blog URL** provided by the user, extract and translate the article content.

### Requirements
1. Use the WebFetch tool to fetch the blog page URL from user input
2. Extract the article content:
   - **Title**: The main article title
   - **Body**: The full article text in markdown format, preserving headings, lists, bold/italic, and code blocks
   - **Images**: Keep original image URLs as-is (do not download images locally)
3. **Translate the entire article** into the **Language** selected by the user. If the user selected 中文, translate all content (title, body) into Chinese. If the user selected English, translate into English. If the article is already in the target language, keep it as-is.
4. Save the translated article as `article.md` with:
   - The title as an H1 heading
   - The full body text in clean markdown in the target language
   - Image references using their original URLs (e.g., `![description](https://example.com/image.png)`)
5. Report what was extracted: title, word count, number of images referenced, and the language it was translated to

**Output:** article.md
</task>

<break id="review-content" label="Review Extracted Content">
## Review Extracted Content

Check `article.md` to verify the content was extracted correctly.

**Things to check:**
- Is the article title correct?
- Is the body text complete and well-formatted?
- Are image URLs intact and pointing to valid sources?

Edit `article.md` manually if any adjustments are needed before generating cards.
</break>

<task id="generate-card-markdown" label="Generate Card Markdown">
## Generate Card Markdown

Read `article.md` and reformat it into a continuous markdown document suitable for rednote cards.

### Requirements
1. Read `article.md` and understand the full article content
2. Create `cards.md` formatted for the rednote skill:
   - Start with the article title as a heading and a brief hook/summary
   - Write the content as a **continuous flowing markdown document** — do NOT manually insert `---` page breaks. The rednote skill will automatically paginate long content into cards based on the card height. Just write naturally.
   - Use `==text==` to highlight key terms, numbers, or takeaways
   - Include relevant images using their original URLs where they fit naturally
   - Use headings (##, ###) to organize topics
   - Write substantive, information-dense content — fill the space with valuable insights rather than leaving cards sparse
   - Preserve the most important information and insights from the article
   - End with a summary section of key takeaways as bullet points
3. Write the card content in the same language as `article.md`

### Rednote Markdown Tips
- `==highlighted text==` creates highlighted/marked text
- Single newlines are treated as line breaks
- The skill auto-paginates long content into multiple cards — no need to manually split with `---`
- Only use `---` if you want to force a page break at a specific point (e.g., separating the title page from content)
- Images can use original URLs from the source article

**Output:** cards.md
</task>

<task id="render-cards" label="Render Card Images">
## Render Cards Using Rednote Skill

Use the rednote skill to generate PNG card images from `cards.md`.

### Requirements
1. Read the user's selected **Card Template**, **Watermark**, and **Language** from input
2. Run the rednote skill CLI to generate cards:
   ```
   pnpm -C .skills/rednote/runtime generate cards.md -t <template> --watermark "<watermark>" --lang <lang> -o cards/
   ```
   - Use the template selected by the user (default: `apple-notes`)
   - Use the watermark text if provided, otherwise omit the `--watermark` flag to use the default
   - Use the language selected by the user (default: `en`)
3. After generation, list all files in `cards/` with their sizes
4. Report how many card images were generated

**Output:** cards/xhs-card-*.png
</task>

<break id="review-cards" label="Review Cards">
## Review Generated Cards

Open the `cards/` folder to review the generated Xiaohongshu card images.

**Things to check:**
- Are the cards visually appealing and readable?
- Is the text properly sized and not overflowing?
- Are images rendering correctly on the cards?
- Is the content split across cards in a logical way?

If cards need adjustment:
- Edit `cards.md` to adjust content, then re-run the **Render Card Images** step
- Try a different template by going back to **Blog Settings**
</break>

<note id="complete" label="Complete">
## Cards Generated

### Generated Files
```
rednote_output/
├── article.md              # Extracted article content
├── cards.md                # Card-formatted markdown
└── cards/                  # Final card images (1080x1440px)
    └── xhs-card-*.png
```

### Next Steps
- Open `cards/` to access your Xiaohongshu card images
- Share the cards on Xiaohongshu/Rednote or other social platforms
- Re-run individual steps to adjust content or try different templates
</note>

