# Sync from Upstream

Pull documentation updates from the private anyt-io repo into this public notebook repo.

## Arguments

$ARGUMENTS

## Instructions

You are pulling documentation from the private `anyt-io` repo into the public `notebook` repo. Follow these steps:

### Step 1: Parse Arguments

Check if arguments were provided:
- No args or empty: Auto-detect changes and sync everything out of date
- `--check`: Dry run — show what would change without making modifications
- `--readme-only`: Sync only the README
- `--changelog-only`: Sync only the CHANGELOG
- `--examples-only`: Sync only example notebooks

### Step 2: Identify Repos

- **Source (private)**: `/Users/bsheng/work/anyt-io`
- **Target (this repo)**: `/Users/bsheng/work/notebook`

### Step 3: Verify Source Repo Exists

```bash
ls /Users/bsheng/work/anyt-io/README.md
```

If the source repo isn't available, abort with a clear message.

### Step 4: Analyze What Needs Syncing

Compare these files:

1. **README.md**
   - Source: `/Users/bsheng/work/anyt-io/README.md`
   - Target: `README.md` (this repo)
   - Note: This repo's README is more polished and user-facing. Don't blindly copy — merge new features/changes into the existing structure.

2. **CHANGELOG.md**
   - Source: `/Users/bsheng/work/anyt-io/apps/notebook/CHANGELOG.md`
   - Target: `CHANGELOG.md`
   - Copy the full changelog.

3. **examples/**
   - Source: Look for example `.anyt.md` files in anyt-io (check `apps/notebook-cli/`, `apps/notebook/examples/`)
   - Target: `examples/`
   - Sync new or updated example notebooks.

### Important: Stub Files — Do NOT Overwrite

These files in this repo are **stubs** pointing to canonical sources elsewhere. Do NOT replace them with full copies:
- `docs/anyt-notebook-spec.md` — stub pointing to docs.anyt.io (canonical: `anyt-io/docs/anyt-notebook-spec.md`)
- `docs/pspm-cli-guide.md` — stub pointing to pspm.dev docs
- `docs/PRODUCT.md` — native to this repo, not synced from anyt-io

### Step 5: Create a Branch

```bash
git checkout main
git pull origin main
git checkout -b sync-from-upstream-$(date +%Y%m%d)
```

### Step 6: Sync Files

**README.md**: Merge changes — preserve demo GIF, Requirements section, Documentation links. Update feature descriptions and commands.

**CHANGELOG.md**: Copy the full changelog from `anyt-io/apps/notebook/CHANGELOG.md`.

**examples/**: Copy updated examples. Preserve examples that only exist in this repo.

### Step 7: Commit and Create PR

```bash
git add -A
git commit -m "docs: sync from upstream anyt-io"
git push -u origin HEAD
gh pr create --title "docs: sync from upstream" --body "Pull latest documentation from the private anyt-io repo."
```

### Step 8: Show Summary

Display:
- Files updated
- PR URL
- Any files that were skipped

## Notes

- This is the inverse of anyt-io's `/update-public-repo` command — either can be used
- Always create a branch and PR, never push directly to main
- The stub files in `docs/` must not be overwritten
