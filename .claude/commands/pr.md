# Create PR

Create a pull request for the current branch.

## Arguments

$ARGUMENTS

## Instructions

1. Check if there are uncommitted changes:
   ```
   git status --porcelain
   ```
   - If there are uncommitted changes, notify the user and suggest using `/commit` first

2. Check if the current branch has been pushed:
   ```
   git status
   ```
   - If not pushed, push with upstream tracking:
     ```
     git push -u origin HEAD
     ```

3. Check if a PR already exists for this branch:
   ```
   gh pr view --json url 2>/dev/null
   ```
   - If PR exists, show the existing PR URL and exit

4. Get the commits on this branch compared to main:
   ```
   git log main..HEAD --oneline
   ```

5. Create a pull request:
   - If $ARGUMENTS provided, use it as the PR title
   - If no arguments, generate a title based on the branch name or commits
   ```
   gh pr create --fill
   ```
   Or with custom title:
   ```
   gh pr create --title "<title>" --body ""
   ```

6. Show the PR URL to the user
