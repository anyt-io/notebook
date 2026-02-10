# Commit and PR

Commit changes, fix any code quality issues, push to remote, and create a pull request.

## Arguments

$ARGUMENTS

## Instructions

1. Discover all Python skills with a runtime:
   ```bash
   ls -d skills/*/runtime/pyproject.toml 2>/dev/null | xargs -I{} dirname {} | xargs -I{} dirname {}
   ```

2. For each discovered skill, from its `runtime/` directory, run formatting to auto-fix issues:
   ```bash
   uv run ruff format .
   ```

3. For each discovered skill, from its `runtime/` directory, run lint checks:
   ```bash
   uv run ruff check .
   ```
   - If check fails with unfixable errors, stop and notify the user

4. For each discovered skill, from its `runtime/` directory, run type checking:
   ```bash
   uv run python -m pyright .
   ```
   - If typecheck has errors:
     - For minor issues (1-3 errors): Fix them automatically
     - For major issues (4+ errors or complex problems): Stop and notify the user with a summary of the issues

5. For each discovered skill, from its `runtime/` directory, run tests:
   ```bash
   uv run pytest tests/ -v
   ```
   - If tests fail, stop and notify the user with a summary of failures

6. Validate all skills:
   ```bash
   cd skills/pspm-skill-creator && uv run --project runtime runtime/validate_all_skills.py ../../skills
   ```
   - If validation fails, stop and notify the user

7. Stage all changes (including any auto-fixed files):
   ```bash
   git add -A
   ```

8. Review what will be committed:
   ```bash
   git status
   git diff --cached --stat
   ```

9. Create a commit:
   - If $ARGUMENTS provided, use it as the commit message
   - If no arguments, analyze the staged changes and generate an appropriate commit message
   - Follow conventional commit format (feat:, fix:, chore:, docs:, refactor:, etc.)

10. Push to remote with upstream tracking:
    ```bash
    git push -u origin HEAD
    ```

11. Create a pull request using GitHub CLI:
    ```bash
    gh pr create --fill
    ```
    - If the push or PR creation fails, notify the user with the error

12. Show the PR URL to the user
