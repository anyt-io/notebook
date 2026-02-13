# PSPM CLI Guide

PSPM (Prompt Skill Package Manager) is a CLI tool for managing prompt skills across AI coding agents. It provides commands for authentication, configuration, skill management, and publishing.

## Installation

```bash
# Install globally
npm install -g @anytio/pspm

# Or use with npx
npx @anytio/pspm <command>
```

## Command Reference

```
Usage: pspm [options] [command]

Prompt Skill Package Manager for AI coding agents

Options:
  -V, --version                              output the version number
  -h, --help                                 display help for command

Commands:
  config                                     Manage PSPM configuration
  login [options]                            Log in via browser or with an API key
  logout                                     Log out and clear stored credentials
  whoami                                     Show current user information
  init [options]                             Create a new pspm.json manifest in the current directory
  migrate [options]                          Migrate from old directory structure (.skills/, skill-lock.json)
  add [options] <specifiers...>              Add one or more skills
  remove|rm <name>                           Remove an installed skill
  list|ls [options]                          List installed skills
  install|i [options] [specifiers...]        Install skills from lockfile, or add and install specific packages
  link [options]                             Recreate agent symlinks without reinstalling
  update [options]                           Update all skills to latest compatible versions
  version <bump>                             Bump package version (major, minor, patch)
  publish [options]                          Publish current directory as a skill
  unpublish [options] <specifier>            Remove a published skill version (only within 72 hours of publishing)
  access [options] [specifier]               Change package visibility (public/private)
  deprecate [options] <specifier> [message]  Mark a skill version as deprecated (alternative to unpublish after 72 hours)
  help [command]                             display help for command
```

## Authentication

### Login

Authenticate with an API key:

```bash
pspm login --api-key <key>
```

Or use browser-based OAuth:

```bash
pspm login
```

### Logout

Remove stored credentials:

```bash
pspm logout
```

### Who Am I

Display current user information:

```bash
pspm whoami

# Output:
#   Username: myuser
#   User ID: user_123
#   Registry: https://registry.pspm.dev
```

## Configuration

### Show Configuration

Display resolved configuration and config file locations:

```bash
pspm config show

# Output:
#   Resolved Configuration:
#
#     Registry URL:   https://registry.pspm.dev
#     API Key:        ***
#     Username:       myuser
#
#   Config Locations:
#     User config:    /Users/you/.pspmrc
#     Project config: (none)
#
#   Environment Variables:
#     PSPM_REGISTRY_URL: (not set)
#     PSPM_API_KEY:      (not set)
```

### Initialize Project Config

Create a `.pspmrc` file in the current directory:

```bash
pspm config init
pspm config init --registry https://custom.example.com
```

## Project Initialization

### Initialize Manifest

Create a new `pspm.json` manifest file in the current directory:

```bash
pspm init                          # Interactive prompts
pspm init -y                       # Use defaults, skip prompts
pspm init -n my-skill              # Specify name
pspm init -d "My skill"            # Specify description
pspm init -a "Your Name"           # Specify author
pspm init -f                       # Overwrite existing pspm.json
```

### Migrate from Old Structure

Migrate from old directory structure (`.skills/`, `skill-lock.json`):

```bash
pspm migrate                       # Perform migration
pspm migrate --dry-run             # Preview changes without applying
```

## Skill Management

### Add Skill

Add a skill to the project and install it:

```bash
pspm add <specifier> [--agent <agents>]

# Registry specifier formats:
pspm add @user/bsheng/vite_slides           # Latest version
pspm add @user/bsheng/vite_slides@2.0.0     # Specific version
pspm add @user/bsheng/vite_slides@^2.0.0    # Semver range

# GitHub specifier formats:
pspm add github:owner/repo                  # Entire repo, default branch
pspm add github:owner/repo@main             # Entire repo, specific branch
pspm add github:owner/repo/path/to/skill    # Subdirectory, default branch
pspm add github:owner/repo/path@v1.0.0      # Subdirectory with tag/ref

# Local directory specifiers (for development):
pspm add file:../my-skill                   # Relative path
pspm add file:./local-skill                 # Current directory relative
pspm add file:/absolute/path/to/skill       # Absolute path

# Add multiple skills at once:
pspm add @user/alice/skill1 @user/bob/skill2

# Agent options:
pspm add @user/skill --agent claude-code,cursor  # Link to multiple agents
pspm add github:owner/repo --agent none          # Skip symlink creation
pspm add @user/skill -y                          # Skip agent selection prompt
```

### Remove Skill

```bash
pspm remove <name>
pspm rm <name>

# Examples:
pspm remove vite_slides
pspm rm @user/bsheng/vite_slides
```

### List Skills

```bash
pspm list
pspm ls

# JSON output for scripting
pspm list --json

# Example output:
# Installed skills:
#
#   @user/alice/code-review@1.2.0 (registry)
#     -> .claude/skills/code-review
#
#   github:owner/repo/skills/react-tips (main@abc1234)
#     -> .claude/skills/react-tips, .cursor/skills/react-tips
#
# Total: 2 skill(s) (1 registry, 1 github)
```

### Install Skills

Install all skills from the lockfile:

```bash
pspm install
pspm i

# With options:
pspm install --frozen-lockfile           # CI/CD mode - fail if lockfile missing
pspm install --dir ./vendor/skills       # Install to specific directory
pspm install --agent claude-code,cursor  # Link to multiple agents
pspm install --agent none                # Skip symlink creation
pspm install -y                          # Skip agent selection prompt

# Install specific packages (like npm):
pspm install @user/alice/skill1 github:org/repo
```

### Link Skills

Recreate agent symlinks without reinstalling (useful after adding agents):

```bash
pspm link
pspm link --agent claude-code,cursor  # Link to specific agents
pspm link -y                          # Skip agent selection prompt
```

### Update Skills

```bash
pspm update
pspm update --dry-run    # Preview updates without applying
```

## Versioning

### Bump Version

Bump the package version in `pspm.json` without publishing (similar to `npm version`):

```bash
pspm version <bump>

# Bump types:
pspm version major      # 1.0.0 → 2.0.0
pspm version minor      # 1.0.0 → 1.1.0
pspm version patch      # 1.0.0 → 1.0.1

# Options:
pspm version patch --dry-run   # Preview what would change
```

The command:
- Reads the current version from `pspm.json`
- Increments the version according to semver rules
- Writes the updated version back to `pspm.json`
- Outputs the new version (e.g., `v1.0.1`)

## Publishing

### Publish Skill

Publish the current directory as a skill:

```bash
pspm publish
pspm publish --bump patch    # Auto-bump version (major, minor, patch)
pspm publish --bump minor --tag beta
pspm publish --access public # Publish and make public in one step
```

**Required `pspm.json` fields:**
- `name` - Skill name (e.g., `@user/username/skillname`)
- `version` - Semver version

**Optional `pspm.json` fields:**
- `description` - Skill description
- `author` - Author name
- `files` - Files to include (default: `["pspm.json", "SKILL.md", "runtime", "scripts", "data"]`)

### Unpublish Skill

Remove a published skill version (only within 72 hours of publishing):

```bash
pspm unpublish <specifier> --force

# Delete specific version
pspm unpublish @user/bsheng/vite_slides@2.0.0 --force

# Delete all versions
pspm unpublish @user/bsheng/vite_slides --force
```

### Deprecate Skill

Mark a skill version as deprecated (alternative to unpublish after 72 hours):

```bash
pspm deprecate <specifier> [message]

# Deprecate with message
pspm deprecate @user/bsheng/old-skill@1.0.0 "Use @user/bsheng/new-skill instead"

# Remove deprecation
pspm deprecate @user/bsheng/old-skill@1.0.0 --undo
```

## Visibility

### Change Package Visibility

Change a package's visibility between public and private:

```bash
# Make current package public
pspm access --public

# Make specific package public
pspm access @user/bsheng/vite_slides --public
```

**Important:** Making a package public is irreversible (following npm conventions). Public packages cannot be made private again.

- **Private packages** (default): Require authentication to download
- **Public packages**: Anyone can download without authentication

## Configuration Files

### User Config: `~/.pspmrc`

INI format configuration file:

```ini
; PSPM Configuration

registry = https://registry.pspm.dev
authToken = sk_...
username = myuser

; Multi-registry: Scope mappings (optional)
@myorg:registry = https://corp.pspm.io

; Multi-registry: Per-registry tokens (optional)
//pspm.dev:authToken = sk_public_token
//corp.pspm.io:authToken = sk_corp_token
```

### Project Config: `.pspmrc`

Project-specific configuration (optional):

```ini
; Project-specific PSPM configuration

registry = https://custom.example.com
```

### Manifest: `pspm.json`

Package manifest file (created with `pspm init`):

```json
{
  "name": "@user/username/my-skill",
  "version": "1.0.0",
  "description": "A helpful skill for...",
  "author": "Your Name",
  "files": ["pspm.json", "SKILL.md", "runtime", "scripts", "data"],
  "dependencies": {
    "@user/other/skill": "^1.0.0"
  },
  "githubDependencies": {
    "github:owner/repo/skills/example": "main"
  },
  "localDependencies": {
    "file:../my-local-skill": "*"
  }
}
```

### Lockfile: `pspm-lock.json`

```json
{
  "lockfileVersion": 4,
  "registryUrl": "https://registry.pspm.dev",
  "packages": {
    "@user/bsheng/vite_slides": {
      "version": "2.0.0",
      "resolved": "https://registry.pspm.dev/...",
      "integrity": "sha256-abc123..."
    }
  },
  "githubPackages": {
    "github:owner/repo/path": {
      "version": "abc1234",
      "resolved": "https://github.com/owner/repo",
      "integrity": "sha256-...",
      "gitCommit": "abc1234567890...",
      "gitRef": "main"
    }
  },
  "localPackages": {
    "file:../my-local-skill": {
      "version": "local",
      "path": "../my-local-skill",
      "resolvedPath": "/absolute/path/to/my-local-skill",
      "name": "my-local-skill"
    }
  }
}
```

## Configuration Resolution

Configuration is resolved in priority order:

1. **Environment Variables** (`PSPM_REGISTRY_URL`, `PSPM_API_KEY`) - Highest
2. **Project Config** (`.pspmrc` in project directory)
3. **User Config** (`~/.pspmrc`)
4. **Defaults** - Lowest

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `PSPM_API_KEY` | Override API key |
| `PSPM_DEBUG` | Enable debug logging |
| `GITHUB_TOKEN` | GitHub token for private repos and higher rate limits |

## Directory Structure

```
project/
├── .pspmrc              # Project config (optional)
├── pspm.json            # Manifest with dependencies
├── pspm-lock.json       # Lockfile
├── .pspm/
│   ├── skills/          # Installed skills
│   │   ├── {username}/  # Registry skills
│   │   │   └── {skillname}/
│   │   ├── _github/     # GitHub skills
│   │   │   └── {owner}/
│   │   │       └── {repo}/
│   │   │           └── {path}/
│   │   └── _local/      # Local skill symlinks
│   │       └── {name} -> ../../../path/to/local/skill
│   └── cache/           # Tarball cache
├── .claude/
│   └── skills/          # Symlinks for claude-code agent
└── .cursor/
    └── skills/          # Symlinks for cursor agent (if configured)

~/
└── .pspmrc              # User config
```

## Common Workflows

### CI/CD Integration

```bash
# Use environment variable for authentication
export PSPM_API_KEY=sk_ci_key

# Install with frozen lockfile (fails if lockfile missing or outdated)
pspm install --frozen-lockfile
```

### Local Development Workflow

Use local dependencies to develop and test skills before publishing:

```bash
# Add a local skill for development
pspm add file:../my-skill

# The skill is symlinked, so changes are instant
# No need to reinstall after editing the local skill

# When ready to publish
cd ../my-skill
pspm publish
```

In your `pspm.json`:
```json
{
  "localDependencies": {
    "file:../my-local-skill": "*"
  }
}
```

### Publishing Workflow

```bash
# Initialize a new skill
pspm init

# Edit pspm.json and create SKILL.md
# Then publish with auto-bump
pspm publish --bump patch
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Not logged in" | Run `pspm login --api-key <key>` |
| "Invalid skill specifier" | Use format: `@user/{username}/{name}[@version]` |
| "No lockfile found" | Run `pspm add <specifier>` first |

Enable debug mode for detailed output:

```bash
PSPM_DEBUG=1 pspm <command>
```

## Migration from v0.0.3

If you have an existing `~/.pspm/config.json` from v0.0.3 or earlier, PSPM will automatically migrate your configuration to the new `~/.pspmrc` INI format on first run.

The migration will:
1. Extract credentials from your default profile
2. Create a new `~/.pspmrc` file
3. Remove the old `~/.pspm/config.json`

Use `pspm migrate` to migrate project-level files from old directory structure (`.skills/`, `skill-lock.json`).
