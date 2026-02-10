# Start New Branch

Create a new git branch based on origin/main with a date-time based name.

## Arguments

$ARGUMENTS

## Instructions

1. Fetch the latest from origin:
   ```
   git fetch origin
   ```

2. Create and checkout a new branch based on origin/main with a name using the current date and time (up to minutes) in the format: `dev/YYYY-MM-DD_HH-MM_<slug>`

   - Convert the arguments to a slug (lowercase, spaces to hyphens, remove special characters)
   - If no arguments provided, omit the slug suffix

   Examples:
   - With argument "add playright tests": `dev/2025-12-31_14-30_add-playright-tests`
   - Without argument: `dev/2025-12-31_14-30`

3. Confirm the branch was created successfully by showing `git status`
