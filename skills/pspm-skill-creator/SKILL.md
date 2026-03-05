---
name: pspm-skill-creator
description: Create new PSPM skills, improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, scaffold a skill project with uv or bun, update or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# PSPM Skill Creator

A skill for creating new PSPM skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any. Then explain them to the user
  - Use the `runtime/generate_review.py` script to show the user the results, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation (and any glaring flaws from the quantitative benchmarks)
- Repeat until satisfied
- Expand the test set and try again at larger scale

Your job is to figure out where the user is in this process and help them progress. Maybe they say "I want to make a skill for X" — help them narrow down what they mean, write a draft, write test cases, figure out evaluation, run prompts, and iterate.

On the other hand, maybe they already have a draft. In this case, go straight to eval/iterate.

Of course, be flexible — if the user says "I don't need evaluations, just vibe with me", do that instead.

After the skill is done, you can run the description improver to optimize triggering.

## Communicating with the User

The skill creator is used by people across a wide range of familiarity with coding jargon. Pay attention to context cues to understand how to phrase your communication! In the default case:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt.

---

## About PSPM Skills

PSPM skills are modular packages that extend AI coding agents (Claude Code, Cursor, Windsurf, Gemini CLI) with specialized capabilities. Each skill is a self-contained folder with documentation, metadata, and an **isolated runtime environment**.

### Skill Structure

```
skills/<skill-name>/
├── SKILL.md              # Usage documentation (loaded by AI agents)
├── pspm.json             # PSPM manifest (name, version, metadata)
├── .pspmignore           # Files excluded from PSPM publishing
├── evals/                # Test cases and input files
│   ├── evals.json        # Test case definitions
│   └── files/            # Input files for tests
├── agents/               # Subagent instructions (optional)
├── references/           # Reference documentation (optional)
├── assets/               # Templates, icons, fonts (optional)
└── runtime/              # Isolated execution environment
    ├── pyproject.toml    # Python: deps + tool config (uv)
    ├── uv.lock           # Python: pinned dependency versions
    ├── package.json      # TypeScript: deps + scripts (bun)
    ├── bun.lock          # TypeScript: pinned dependency versions
    ├── <scripts>.py/.ts  # Flat in runtime/, no nested folders
    └── tests/            # Test files (Python: pytest)
```

### Key Differences from Anthropic Skills

PSPM skills use **isolated runtime environments** instead of bare `scripts/` folders:

| Anthropic skills | PSPM skills |
|------------------|-------------|
| `scripts/foo.py` | `runtime/foo.py` |
| No dependency management | `runtime/pyproject.toml` or `runtime/package.json` |
| `python scripts/foo.py` | `uv run --project runtime runtime/foo.py` |
| `references/` for docs | `references/` for docs (same) |
| `assets/` for templates | `assets/` for templates (same) |

### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (scripts can execute without loading)

**Key patterns:**
- Keep SKILL.md under 500 lines; if approaching this limit, add hierarchy with clear pointers
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

---

## Creating a Skill

### Phase 1: Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections made, input/output formats observed.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them.

### Phase 2: Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs — if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline.

### Phase 3: Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier (kebab-case, max 64 chars)
- **description**: When to trigger, what it does. This is the primary triggering mechanism — include both what the skill does AND specific contexts for when to use it. Note: Claude tends to "undertrigger" skills. Make descriptions a bit "pushy" — include trigger phrases the user might say.
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern:**
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

#### Writing Style

Try to explain to the model why things are important in lieu of heavy-handed MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

For design patterns, see [references/output-patterns.md](references/output-patterns.md) and [references/workflows.md](references/workflows.md).

### Phase 4: Initialize the Skill Project

```bash
uv run --project runtime runtime/init_skill.py <skill-name> --path skills/
```

This creates the full directory structure with template files. For TypeScript skills, add `--type ts`.

**Set up the runtime:**

```bash
# Python
cd skills/<skill-name>/runtime
uv add <runtime-deps>
uv add --dev ruff pyright pytest

# TypeScript
cd skills/<skill-name>/runtime
bun add <runtime-deps>
```

**Write scripts:**

Place scripts directly in `runtime/`. Use `SKILL_DIR = Path(__file__).resolve().parent.parent` for resolving paths relative to the skill root.

Execute from the skill folder:
```bash
# Python
uv run --project runtime runtime/<script>.py [args]

# TypeScript
bun run runtime/<script>.ts [args]
```

### Phase 5: Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `expectations` field, which you'll add later).

---

## Running and Evaluating Test Cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Create directories as you go.

### Step 1: Spawn All Runs (with-skill AND baseline) in the Same Turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While Runs Are in Progress, Draft Assertions

Draft quantitative assertions for each test case and explain them to the user. Good assertions are objectively verifiable and have descriptive names.

Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions.

### Step 3: As Runs Complete, Capture Timing Data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade, Aggregate, and Launch the Viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use the fields `text`, `passed`, and `evidence`.

2. **Aggregate into benchmark** — run the aggregation script:
   ```bash
   uv run --project runtime runtime/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration.

3. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` for what to look for.

4. **Launch the viewer**:
   ```bash
   nohup uv run --project runtime runtime/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Cowork / headless environments:** Use `--static <output_path>` to write a standalone HTML file instead of starting a server.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

### Step 5: Read the Feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on test cases where the user had specific complaints.

Kill the viewer server when done:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Improving the Skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to Think About Improvements

1. **Generalize from the feedback.** We're trying to create skills used many times across many different prompts. Rather than put in fiddly overfitty changes, if there's some stubborn issue, try branching out and using different metaphors, or recommending different patterns of working.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the transcripts, not just the final outputs — if the skill is making the model waste time doing unproductive things, try getting rid of those parts.

3. **Explain the why.** Try hard to explain the **why** behind everything. Today's LLMs are smart. If you find yourself writing ALWAYS or NEVER in all caps, reframe and explain the reasoning instead.

4. **Look for repeated work across test cases.** If all 3 test cases resulted in the subagent writing a similar helper script, that's a strong signal the skill should bundle that script.

### The Iteration Loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind Comparison

For situations where you want a more rigorous comparison between two versions of a skill, there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The basic idea is: give two outputs to an independent agent without telling it which is which, and let it judge quality.

This is optional, requires subagents, and most users won't need it.

---

## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Step 1: Generate Trigger Eval Queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic and something a Claude Code or Claude.ai user would actually type. Include file paths, personal context, column names, company names, URLs. Use a mix of different lengths, and focus on edge cases.

### Step 2: Review with User

Present the eval set to the user for review. The user can edit queries, toggle should-trigger, add/remove entries, then export.

### Step 3: Run the Optimization Loop

```bash
uv run --project runtime runtime/run_loop.py \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

This handles the full optimization loop automatically. It splits the eval set into 60% train and 40% held-out test, evaluates the current description, then calls Claude with extended thinking to propose improvements based on what failed. It iterates up to 5 times and returns JSON with `best_description`.

### Step 4: Apply the Result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

---

## Validation and Packaging

### Validate

```bash
uv run --project runtime runtime/validate_skill.py skills/<skill-name>
```

### Package

```bash
uv run --project runtime runtime/package_skill.py skills/<skill-name> [output-dir]
```

Creates a `.skill` file (ZIP archive) for distribution.

---

## Dev Checks (Python)

```bash
cd skills/<skill-name>/runtime
uv run ruff check .
uv run ruff format .
uv run python -m pyright .
uv run pytest tests/ -v
```

### pyproject.toml baseline

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pyright]
pythonVersion = "3.10"
include = ["."]
typeCheckingMode = "standard"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

---

## Prerequisites

- `uv` (Python skills): https://docs.astral.sh/uv/getting-started/installation/
- `bun` (TypeScript skills): https://bun.sh/

---

## Environment-Specific Instructions

### Claude Code

Full workflow with subagents:
- Spawn test runs in parallel
- Use browser-based reviewer
- Description optimization via CLI

### Claude.ai (no subagents)

- No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself
- Skip baseline runs — just use the skill to complete the task
- Present results directly in conversation instead of browser reviewer
- Skip quantitative benchmarking and description optimization (requires `claude -p`)

### Cowork (headless)

- Subagents work (parallel execution)
- Use `--static` mode for HTML viewer
- Feedback downloads as JSON file when user clicks "Submit All Reviews"
- All automation scripts work

---

## Reference Files

The `agents/` directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent.

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The `references/` directory has additional documentation:
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.
- `references/output-patterns.md` — Design patterns for skill output
- `references/workflows.md` — Design patterns for skill workflows

---

## Limitations

- Skill names must be kebab-case, max 64 characters
- SKILL.md description max 1024 characters
- Keep SKILL.md body under 500 lines to minimize context bloat

---

## Core Loop Summary

1. Figure out what the skill is about
2. Draft or edit the skill
3. Run claude-with-access-to-the-skill on test prompts
4. With the user, evaluate the outputs:
   - Create benchmark.json and run `runtime/generate_review.py` to help the user review them
   - Run quantitative evals
5. Repeat until you and the user are satisfied
6. Package the final skill and return it to the user

Good luck!
