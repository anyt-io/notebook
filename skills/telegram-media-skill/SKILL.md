---
name: telegram-media-skill
description: Emit OpenClaw MEDIA lines for Telegram and other chat channels from local files. Use when a user wants to send an existing image or file from disk, turn a relative path into an absolute path, validate that a local file exists, or return reply text that includes MEDIA:/absolute/path on its own line.
---

# Telegram Media Skill

Use this skill when the file already exists locally and the job is to hand it off to OpenClaw chat delivery.

## Workflow

1. Run the bundled runtime script instead of hand-formatting the line.
2. Pass the file path to the script.
3. If you want a caption, pass `--caption`.
4. Return the script output exactly so OpenClaw can parse the `MEDIA:` line.

## Commands

Emit a media line:

```bash
uv run --project runtime runtime/media_line.py /absolute/or/relative/path.png
```

Emit caption plus media line:

```bash
uv run --project runtime runtime/media_line.py /path/to/file.png --caption "Here it is"
```

## Notes

- `MEDIA:` must be on its own line with no leading spaces.
- The script resolves `~` and relative paths into an absolute path.
- The script exits non-zero if the file does not exist or is not a regular file.
- The skill is channel-agnostic even though it is optimized for Telegram/OpenClaw handoff.
