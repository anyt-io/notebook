"""Tests for parse_notebook module."""

import textwrap
from pathlib import Path

import pytest

from parse_notebook import (
    Notebook,
    ParseError,
    extract_form_description,
    extract_form_fields,
    format_form_prompt,
    parse_notebook,
    validate_notebook,
)


@pytest.fixture
def tmp_notebook(tmp_path: Path):
    """Helper to create a temporary notebook file."""

    def _create(content: str) -> Path:
        p = tmp_path / "test.anyt.md"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p

    return _create


class TestParseNotebook:
    def test_minimal_notebook(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test-notebook
            ---

            # test-notebook
            """)
        )
        assert nb.schema == "2.0"
        assert nb.name == "test-notebook"
        assert nb.cells == []

    def test_frontmatter_fields(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: my-notebook
            description: A test notebook
            version: 1.0.0
            workdir: anyt_workspace_test
            env_file: secrets/.env
            ---

            # my-notebook
            """)
        )
        assert nb.name == "my-notebook"
        assert nb.description == "A test notebook"
        assert nb.version == "1.0.0"
        assert nb.workdir == "anyt_workspace_test"
        assert nb.env_file == "secrets/.env"

    def test_parse_task_cell(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <task id="hello" label="Say Hello">
            Create a hello.txt file.

            **Output:** hello.txt
            </task>
            """)
        )
        assert len(nb.cells) == 1
        cell = nb.cells[0]
        assert cell.cell_type == "task"
        assert cell.id == "hello"
        assert cell.label == "Say Hello"
        assert "hello.txt" in cell.content

    def test_parse_shell_cell(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <shell id="setup">
            mkdir -p src
            npm init -y
            </shell>
            """)
        )
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "shell"
        assert "mkdir -p src" in nb.cells[0].content

    def test_parse_input_cell(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <input id="config" label="Configuration">
            ## Project Config

            <form type="json">
            {
              "fields": [
                {"name": "projectName", "type": "text", "label": "Name"}
              ]
            }
            </form>
            </input>
            """)
        )
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "input"
        assert nb.cells[0].label == "Configuration"

    def test_parse_note_cell(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <note id="done" label="Complete">
            ## All done
            </note>
            """)
        )
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "note"

    def test_parse_break_cell_with_skip(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <break id="review" label="Review" skip="true">
            Check the output.
            </break>
            """)
        )
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "break"
        assert nb.cells[0].skip is True

    def test_parse_multiple_cells(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <shell id="setup">
            mkdir -p src
            </shell>

            <task id="create-api">
            Create an API.
            </task>

            <break id="review">
            Review.
            </break>
            """)
        )
        assert len(nb.cells) == 3
        assert [c.cell_type for c in nb.cells] == ["shell", "task", "break"]
        assert [c.id for c in nb.cells] == ["setup", "create-api", "review"]

    def test_agent_attribute(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <task id="reasoning" agent="claude">
            Complex task.
            </task>
            """)
        )
        assert nb.cells[0].agent == "claude"

    def test_missing_frontmatter_raises(self, tmp_notebook):
        with pytest.raises(ParseError):
            parse_notebook(
                tmp_notebook("""\
                # No frontmatter
                <task id="hello">
                Hello
                </task>
                """)
            )

    def test_unclosed_cell_raises(self, tmp_notebook):
        with pytest.raises(ParseError):
            parse_notebook(
                tmp_notebook("""\
                ---
                schema: "2.0"
                name: test
                ---

                # test

                <task id="hello">
                This cell is never closed.
                """)
            )


class TestValidateNotebook:
    def test_valid_notebook(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <task id="hello">
            Hello
            </task>
            """)
        )
        errors = validate_notebook(nb)
        assert errors == []

    def test_wrong_schema_version(self):
        nb = Notebook(schema="1.0", name="test")
        errors = validate_notebook(nb)
        assert any("Schema" in e for e in errors)

    def test_missing_name(self):
        nb = Notebook(schema="2.0", name="")
        errors = validate_notebook(nb)
        assert any("name" in e for e in errors)

    def test_duplicate_ids(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <task id="hello">
            First
            </task>

            <task id="hello">
            Duplicate
            </task>
            """)
        )
        errors = validate_notebook(nb)
        assert any("Duplicate" in e for e in errors)

    def test_invalid_agent(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <task id="hello" agent="invalid">
            Hello
            </task>
            """)
        )
        errors = validate_notebook(nb)
        assert any("agent" in e.lower() for e in errors)

    def test_skip_on_non_break(self):
        from parse_notebook import Cell

        nb = Notebook(schema="2.0", name="test", cells=[Cell(cell_type="task", id="hello", skip=True)])
        errors = validate_notebook(nb)
        assert any("skip" in e for e in errors)


class TestExtractFormFields:
    def test_extract_fields_from_input_cell(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <input id="config" label="Configuration">
            ## Configure Your Project

            <form type="json">
            {
              "fields": [
                {"name": "projectName", "type": "text", "label": "Project Name", "required": true},
                {"name": "database", "type": "select", "label": "Database", "default": "sqlite",
                 "options": [{"value": "sqlite", "label": "SQLite"}, {"value": "postgres", "label": "PostgreSQL"}]},
                {"name": "port", "type": "number", "label": "Port", "default": 3000,
                 "validation": {"min": 1024, "max": 65535}},
                {"name": "isPublic", "type": "checkbox", "label": "Public?"},
                {"name": "features", "type": "multiselect", "label": "Features",
                 "options": [{"value": "auth", "label": "Auth"}, {"value": "api", "label": "API"}]}
              ]
            }
            </form>
            </input>
            """)
        )
        cell = nb.cells[0]
        fields = extract_form_fields(cell)
        assert fields is not None
        assert len(fields) == 5

        # Check text field
        assert fields[0].name == "projectName"
        assert fields[0].field_type == "text"
        assert fields[0].required is True

        # Check select field
        assert fields[1].name == "database"
        assert fields[1].field_type == "select"
        assert fields[1].default == "sqlite"
        assert fields[1].options is not None
        assert len(fields[1].options) == 2

        # Check number field with validation
        assert fields[2].name == "port"
        assert fields[2].field_type == "number"
        assert fields[2].validation == {"min": 1024, "max": 65535}

        # Check checkbox field
        assert fields[3].field_type == "checkbox"

        # Check multiselect field
        assert fields[4].field_type == "multiselect"

    def test_extract_fields_returns_none_for_non_input(self):
        from parse_notebook import Cell

        cell = Cell(cell_type="task", id="hello", content="Do something")
        assert extract_form_fields(cell) is None

    def test_extract_fields_returns_none_for_input_without_form(self):
        from parse_notebook import Cell

        cell = Cell(cell_type="input", id="review", content="## Review\n\nCheck the output.")
        assert extract_form_fields(cell) is None

    def test_extract_file_field(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <input id="upload">
            <form type="json">
            {
              "fields": [
                {"name": "logo", "type": "file", "label": "Logo", "accept": "image/*"},
                {"name": "docs", "type": "file", "label": "Docs", "accept": ".pdf", "multiple": true,
                 "validation": {"maxFiles": 5}}
              ]
            }
            </form>
            </input>
            """)
        )
        fields = extract_form_fields(nb.cells[0])
        assert fields is not None
        assert fields[0].accept == "image/*"
        assert fields[0].multiple is False
        assert fields[1].multiple is True
        assert fields[1].validation == {"maxFiles": 5}


class TestExtractFormDescription:
    def test_description_above_form(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <input id="config">
            ## Configure Your Project

            Set up the initial parameters:

            <form type="json">
            {"fields": [{"name": "x", "type": "text", "label": "X"}]}
            </form>
            </input>
            """)
        )
        desc = extract_form_description(nb.cells[0])
        assert desc is not None
        assert "Configure Your Project" in desc
        assert "initial parameters" in desc

    def test_no_form_returns_full_content(self):
        from parse_notebook import Cell

        cell = Cell(cell_type="input", id="review", content="## Review\n\nCheck output.")
        desc = extract_form_description(cell)
        assert desc is not None
        assert "Review" in desc


class TestFormatFormPrompt:
    def test_generates_readable_prompt(self, tmp_notebook):
        nb = parse_notebook(
            tmp_notebook("""\
            ---
            schema: "2.0"
            name: test
            ---

            # test

            <input id="config">
            ## Setup

            <form type="json">
            {
              "fields": [
                {"name": "name", "type": "text", "label": "Project Name", "required": true},
                {"name": "db", "type": "select", "label": "Database",
                 "options": [{"value": "pg", "label": "PostgreSQL"}, {"value": "my", "label": "MySQL"}],
                 "default": "pg"},
                {"name": "port", "type": "number", "label": "Port", "default": 3000,
                 "validation": {"min": 1024, "max": 65535}},
                {"name": "public", "type": "checkbox", "label": "Public Repo"},
                {"name": "feats", "type": "multiselect", "label": "Features",
                 "options": [{"value": "a", "label": "Auth"}, {"value": "b", "label": "API"}]}
              ]
            }
            </form>
            </input>
            """)
        )
        prompt = format_form_prompt(nb.cells[0])
        assert prompt is not None
        assert "Setup" in prompt
        assert "(required)" in prompt
        assert "PostgreSQL" in prompt
        assert "MySQL" in prompt
        assert "[default: pg]" in prompt
        assert "[default: 3000]" in prompt
        assert "Yes/No" in prompt
        assert "Choose one or more" in prompt

    def test_returns_none_for_non_input(self):
        from parse_notebook import Cell

        cell = Cell(cell_type="task", id="hello", content="Do something")
        assert format_form_prompt(cell) is None
