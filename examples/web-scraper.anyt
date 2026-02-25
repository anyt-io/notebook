---
schema: "2.0"
name: web-scraper
workdir: scraper_output
inputs:
  targetUrl: https://example.com
  outputFormat: json
---

# Web Scraper

A notebook that demonstrates scraping and processing web content.

<note id="overview">
## Web Scraper Pipeline

This notebook:
1. Sets up directory structure
2. Scrapes target URL
3. Reviews scraped content
4. Parses and extracts data
5. Validates the output
</note>

<shell id="setup">
#!/bin/bash
mkdir -p data/raw data/processed logs
echo "Directory structure created"
ls -la data/
</shell>

<task id="scrape">
Scrape the target URL specified in inputs and save the raw HTML.

Requirements:
1. Fetch the HTML content from the target URL
2. Save to data/raw/page.html
3. Log the page title and content length

**Output:** data/raw/page.html
</task>

<input id="review-scraped">
## Review Scraped Data

Please review the raw HTML in `data/raw/page.html` and verify:
- Content was fetched successfully
- No errors or access blocks
- All expected sections are present

**Actions:**
- `continue` - Proceed with parsing
- `retry` - Re-scrape the page
</input>

<task id="parse">
Parse the HTML from data/raw/page.html and extract structured data.

Extract:
- Page title
- All headings (h1-h6)
- All links with their text and URLs
- Meta description if present

Save as JSON to data/processed/data.json

**Output:** data/processed/data.json
</task>

<break id="review-checkpoint">
Review the parsed data in data/processed/data.json before validation.

Check that the extracted data is accurate and complete.
</break>

<task id="validate">
Validate the extracted data for completeness.

Check:
1. All required fields are present
2. URLs are valid format
3. No empty or null values

Log any issues to logs/validation.log
Create a summary report at logs/summary.txt

**Output:** logs/validation.log, logs/summary.txt
</task>

<note id="complete">
## Scraping Complete

Output files:
- `data/raw/page.html` - Raw HTML
- `data/processed/data.json` - Extracted data
- `logs/validation.log` - Validation results
- `logs/summary.txt` - Summary report
</note>
