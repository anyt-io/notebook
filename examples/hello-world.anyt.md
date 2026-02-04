---
name: hello-world
version: 1.0.0
workdir: hello_output
---

# Hello World

A simple workflow to get started with AnyT Notebook.

<note id="intro">
## Welcome to AnyT Notebook

This is your first workflow! It demonstrates:
- Task cells for AI execution
- Shell cells for scripts
- Note cells for documentation
</note>

<task id="create-greeting">
Create a file called `hello.txt` with a friendly greeting message.

Include today's date and a fun fact about programming.

**Output:** hello.txt
</task>

<shell id="show-file">
#!/bin/bash
echo "=== Contents of hello.txt ==="
cat hello.txt
</shell>

<task id="create-goodbye">
Create a file called `goodbye.txt` with a farewell message.

Make it encouraging for someone learning to code.

**Output:** goodbye.txt
</task>

<note id="complete">
## Workflow Complete

You've successfully run your first AnyT workflow!

Check the `hello_output` folder for the generated files.
</note>
