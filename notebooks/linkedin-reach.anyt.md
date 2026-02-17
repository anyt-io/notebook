---
schema: "2.0"
name: linkedin-reach
description: Find LinkedIn connections matching specific criteria and send
  personalized cold outreach about AnyT Notebook
workdir: linkedin_reach
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

# linkedin-reach

<note id="overview" label="Overview">
## LinkedIn Outreach Pipeline

Find people from your LinkedIn connections who match specific criteria, review the candidate list, and send personalized outreach messages introducing AnyT Notebook.

### Pipeline
1. **Setup** — Install agent-browser skill
2. **LinkedIn Login** — Open LinkedIn in browser, log in with email/password
3. **Confirm Login** — Verify you're logged in (or skip if Google OAuth was blocked)
4. **Fallback** — Auto-detects login status; falls back to Chrome profile + CDP if needed
5. **Search Criteria** — Define who you want to find (e.g., worked at Apple and Uber)
4. **Search Connections** — AI browses LinkedIn to find matching connections
5. **Review Candidates** — Review, update, or remove candidates from the list
6. **Outreach Settings** — Finalize candidate list and add optional meeting link
7. **Compose Messages** — AI drafts personalized cold reach emails
8. **Review Messages** — Verify message content before sending
9. **Send Outreach** — Send LinkedIn messages to each candidate
</note>

<shell id="install-browser" label="Install Agent Browser">
#!/bin/bash
set -e

echo "=== Installing agent-browser CLI ==="
npm install -g agent-browser

echo "=== Installing agent-browser skill ==="
npx @anytio/pspm@latest add github:vercel-labs/agent-browser/skills/agent-browser -y

echo "Done."
</shell>

<shell id="linkedin-login" label="Open LinkedIn for Login">
#!/bin/bash
echo "=== Opening LinkedIn in agent-browser ==="
echo "A browser window will open. Log into LinkedIn if not already logged in."
echo ""
echo "NOTE: If you use 'Sign in with Google', Chromium may block it."
echo "In that case, use LinkedIn email/password login directly."
echo "Or close this window — the next step will fall back to your Chrome profile."
echo ""

# Open LinkedIn in headed mode with a persistent session name.
# Cookies and localStorage are saved to disk automatically.
agent-browser --session-name linkedin --headed open "https://www.linkedin.com/feed/" &

echo ""
echo "Browser window opened. Log in if needed, then continue to the next step."
</shell>

<break id="confirm-login" label="Confirm LinkedIn Login">
## Confirm LinkedIn Login

A browser window should be open with LinkedIn.

- **If already logged in** — you should see your LinkedIn feed. Click Continue.
- **If not logged in** — log in with your LinkedIn email/password, then click Continue.
- **If Google sign-in is blocked** — don't worry, click Continue and the next step will fall back to using your Chrome profile instead.

The session is saved automatically. You won't need to log in again for future runs.
</break>

<shell id="linkedin-login-fallback" label="Fallback: Use Chrome Profile">
#!/bin/bash
# This step checks if the session-name login worked.
# If not, it falls back to launching Chrome with your existing profile via CDP.
# Your Chrome profile already has LinkedIn logged in via Google OAuth.

echo "=== Checking LinkedIn login status ==="

# Test if the session-name approach worked by checking for a LinkedIn page
LOGIN_CHECK=$(agent-browser --session-name linkedin get url 2>&1 || true)

if echo "$LOGIN_CHECK" | grep -q "linkedin.com"; then
  echo "Session login OK. Using agent-browser session."
  echo "SESSION_MODE=session" > .browser-mode
  exit 0
fi

echo "Session login not available. Falling back to Chrome profile + CDP..."
echo ""

# Kill any previous agent-browser Chromium
pkill -f "chromium.*--session-name" 2>/dev/null || true

# Copy Chrome profile to a dedicated automation directory (one-time)
AUTOMATION_DIR="$HOME/.chrome-linkedin-automation"
CHROME_DEFAULT="$HOME/Library/Application Support/Google/Chrome/Default"

if [ ! -d "$AUTOMATION_DIR/Default" ]; then
  echo "First-time setup: copying Chrome profile..."
  echo "(This may take a moment)"
  mkdir -p "$AUTOMATION_DIR"
  cp -r "$CHROME_DEFAULT" "$AUTOMATION_DIR/Default"
  echo "Profile copied."
else
  echo "Using existing automation profile at $AUTOMATION_DIR"
fi

# Close any existing Chrome to avoid profile lock conflicts
echo ""
echo "Closing Chrome to free the profile lock..."
osascript -e 'quit app "Google Chrome"' 2>/dev/null || true
sleep 3

# Launch Chrome with the automation profile and CDP
echo "Launching Chrome with CDP on port 9222..."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$AUTOMATION_DIR" \
  --no-first-run \
  &

# Wait for CDP to be ready
for i in $(seq 1 10); do
  if curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
    echo "CDP ready on port 9222."
    echo "SESSION_MODE=cdp" > .browser-mode
    exit 0
  fi
  sleep 1
done

echo "ERROR: Could not start Chrome with CDP."
exit 1
</shell>

<input id="search-criteria" label="Search Criteria">
## Who do you want to reach?

Describe who you want to find from your LinkedIn connections. Be as specific or broad as you like.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "searchQuery",
      "type": "textarea",
      "label": "Search Criteria",
      "description": "Describe who you're looking for. Include companies, roles, skills, or any other criteria.",
      "required": true,
      "placeholder": "People who worked at both Apple and Uber, preferably in engineering or product roles",
      "rows": 4
    },
    {
      "name": "maxResults",
      "type": "number",
      "label": "Max Results",
      "description": "Maximum number of candidates to find",
      "default": 20,
      "validation": { "min": 1, "max": 100 }
    }
  ]
}
</form>
</input>

<task id="search-connections" label="Search LinkedIn Connections">
## Search LinkedIn for Matching Connections

Use the agent-browser skill to browse LinkedIn and find connections matching the user's criteria.

### Browser Connection
Read `.browser-mode` to determine which mode to use:
- If `SESSION_MODE=session` → use `agent-browser --session-name linkedin`
- If `SESSION_MODE=cdp` → use `agent-browser --cdp 9222`

### Requirements
1. Read the user's **Search Criteria** and **Max Results** from input
2. Use agent-browser (with the correct mode from `.browser-mode`) to browse LinkedIn:
   - Navigate to LinkedIn's search or "My Network" connections page
   - Search for connections matching the user's described criteria (companies, roles, skills, etc.)
   - Use LinkedIn's search filters as needed to narrow results
3. For each matching connection, collect:
   - **Name**: Full name
   - **Current Title**: Current job title and company
   - **Relevant Experience**: Past roles at the matching companies
   - **LinkedIn Profile URL**: Direct link to their profile
4. Stop after reaching **Max Results** candidates
5. Save the candidate list as `candidates.md` in a markdown table format with columns: Name, Current Title, Relevant Experience, Profile URL
6. Also save structured data as `candidates.json` with an array of candidate objects
7. Report how many candidates were found

**Output:** candidates.md, candidates.json
</task>

<break id="review-candidates" label="Review Candidate List">
## Review Candidate List

Open `candidates.md` to review the list of matching connections found on LinkedIn.

**Things to check:**
- Are these the right people you want to reach out to?
- Is the profile information accurate?
- Are there any people you want to remove from the list?

Edit `candidates.md` and `candidates.json` to:
- **Remove** rows/entries for people you don't want to contact
- **Add** anyone manually if they were missed
- **Update** any incorrect information

Once you're satisfied with the list, continue to the next step.
</break>

<input id="outreach-settings" label="Outreach Settings">
## Outreach Settings

Configure your outreach message options.

&nbsp;

<form type="json">
{
  "fields": [
    {
      "name": "senderName",
      "type": "text",
      "label": "Your Name",
      "description": "Your name as it should appear in the message",
      "required": true,
      "placeholder": "John Doe"
    },
    {
      "name": "senderRole",
      "type": "text",
      "label": "Your Role",
      "description": "Your title or role for context",
      "placeholder": "Founder at AnyT"
    },
    {
      "name": "meetingLink",
      "type": "text",
      "label": "Meeting Schedule Link (optional)",
      "description": "Calendly or other scheduling link to include in the message. Leave empty to omit.",
      "placeholder": "https://calendly.com/your-name/30min"
    },
    {
      "name": "tone",
      "type": "select",
      "label": "Message Tone",
      "description": "The tone of your outreach message",
      "default": "friendly-professional",
      "options": [
        { "value": "friendly-professional", "label": "Friendly & Professional" },
        { "value": "casual", "label": "Casual" },
        { "value": "formal", "label": "Formal" }
      ]
    }
  ]
}
</form>
</input>

<task id="compose-messages" label="Compose Outreach Messages">
## Compose Personalized LinkedIn Messages

Read the finalized candidate list and compose personalized cold outreach messages for each candidate.

### Requirements
1. Read `candidates.json` for the finalized candidate list
2. Read the user's **Name**, **Role**, **Meeting Link**, and **Tone** from outreach settings input
3. For each candidate, compose a personalized LinkedIn message that:
   - Opens with a personalized hook referencing their shared connection or their experience at the relevant company
   - Introduces **AnyT Notebook** — a VS Code extension that provides a workflow development environment for AI agents, combining AI tasks, shell scripts, and human review gates in a notebook-style interface
   - Highlights a specific benefit relevant to their background (e.g., for engineers: "automate complex multi-step workflows"; for PMs: "make AI workflows visible and reviewable")
   - If a **Meeting Schedule Link** is provided, include it naturally (e.g., "I'd love to show you a quick demo — feel free to grab a time here: [link]")
   - If no meeting link, end with an open invitation to connect or chat
   - Keep the message concise (under 300 characters for LinkedIn connection messages, or under 1000 characters for InMail-style messages)
   - Match the selected **Tone**
4. Save all messages to `messages.md` with each candidate's name, profile URL, and their personalized message
5. Also save structured data to `messages.json` with an array of objects: `{ name, profileUrl, message }`
6. Report how many messages were composed

**Output:** messages.md, messages.json
</task>

<break id="review-messages" label="Review Messages">
## Review Outreach Messages

Open `messages.md` to review the personalized messages before sending.

**Things to check:**
- Is the personalization accurate for each candidate?
- Is the AnyT Notebook description clear and compelling?
- Is the meeting link included correctly (if provided)?
- Is the tone appropriate?
- Are messages within LinkedIn's character limits?

Edit `messages.md` and `messages.json` to adjust any messages before sending.
</break>

<task id="send-messages" label="Send LinkedIn Messages">
## Send LinkedIn Messages

Use the agent-browser skill to send the personalized outreach messages on LinkedIn.

### Browser Connection
Read `.browser-mode` to determine which mode to use:
- If `SESSION_MODE=session` → use `agent-browser --session-name linkedin`
- If `SESSION_MODE=cdp` → use `agent-browser --cdp 9222`

### Requirements
1. Read `messages.json` for the finalized list of messages
2. For each candidate in the list:
   - Use agent-browser (with the correct mode from `.browser-mode`) to navigate to their LinkedIn profile URL
   - Click "Message" to open the messaging window
   - Paste the personalized message from `messages.json`
   - Send the message
   - Log the result (sent successfully or failed with reason)
3. Save a delivery report as `delivery-report.md` with:
   - Total messages attempted
   - Successfully sent count
   - Failed count with reasons
   - Timestamp for each sent message
4. Also save as `delivery-report.json` for structured data

**Output:** delivery-report.md, delivery-report.json
</task>

<note id="complete" label="Complete">
## Outreach Complete

### Generated Files
```
linkedin_reach/
├── candidates.md          # Candidate list (markdown)
├── candidates.json        # Candidate list (structured)
├── messages.md            # Personalized messages (markdown)
├── messages.json          # Personalized messages (structured)
├── delivery-report.md     # Send results (markdown)
└── delivery-report.json   # Send results (structured)
```

### Next Steps
- Check `delivery-report.md` for any failed deliveries
- Monitor LinkedIn for responses from candidates
- Follow up with candidates who haven't responded after a few days
- Re-run the pipeline with different search criteria to find more candidates
</note>

