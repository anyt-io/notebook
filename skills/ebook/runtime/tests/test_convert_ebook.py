"""Tests for convert_ebook.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from convert_ebook import (
    DEFAULT_OUTPUT_DIR,
    SKILL_DIR,
    _build_extra_args,
    _output_filename,
    convert_ebook,
    resolve_resource_path,
    validate_cover_image,
    validate_css_file,
    validate_input,
)


class TestDefaultOutputDir:
    def test_output_dir_under_skill_dir(self):
        assert DEFAULT_OUTPUT_DIR == SKILL_DIR / "output"

    def test_skill_dir_is_ebook(self):
        assert SKILL_DIR.name == "ebook"


class TestValidateInput:
    def test_valid_md(self, tmp_path: Path):
        p = tmp_path / "test.md"
        p.write_text("# Hello")
        assert validate_input(p) is None

    def test_valid_markdown_ext(self, tmp_path: Path):
        p = tmp_path / "test.markdown"
        p.write_text("# Hello")
        assert validate_input(p) is None

    def test_missing_file(self, tmp_path: Path):
        result = validate_input(tmp_path / "nonexistent.md")
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_input(tmp_path)
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_extension(self, tmp_path: Path):
        p = tmp_path / "test.txt"
        p.write_text("hello")
        result = validate_input(p)
        assert result is not None
        assert "Unsupported format" in result


class TestValidateCoverImage:
    def test_valid_cover(self, tmp_path: Path):
        p = tmp_path / "cover.png"
        p.write_bytes(b"\x89PNG")
        assert validate_cover_image(p) is None

    def test_valid_jpg_cover(self, tmp_path: Path):
        p = tmp_path / "cover.jpg"
        p.write_bytes(b"\xff\xd8")
        assert validate_cover_image(p) is None

    def test_missing_cover(self, tmp_path: Path):
        result = validate_cover_image(tmp_path / "missing.png")
        assert result is not None
        assert "not found" in result.lower()

    def test_wrong_extension(self, tmp_path: Path):
        p = tmp_path / "cover.txt"
        p.write_text("not an image")
        result = validate_cover_image(p)
        assert result is not None
        assert "Unsupported cover image format" in result


class TestValidateCssFile:
    def test_valid_css(self, tmp_path: Path):
        p = tmp_path / "style.css"
        p.write_text("body { color: red; }")
        assert validate_css_file(p) is None

    def test_missing_css(self, tmp_path: Path):
        result = validate_css_file(tmp_path / "missing.css")
        assert result is not None
        assert "not found" in result.lower()

    def test_wrong_extension(self, tmp_path: Path):
        p = tmp_path / "style.scss"
        p.write_text("body { color: red; }")
        result = validate_css_file(p)
        assert result is not None
        assert "Not a CSS file" in result


class TestResolveResourcePath:
    def test_single_file(self, tmp_path: Path):
        p = tmp_path / "doc.md"
        p.write_text("# Hello")
        result = resolve_resource_path([p])
        assert result == str(tmp_path.resolve())

    def test_deduplication(self, tmp_path: Path):
        p1 = tmp_path / "a.md"
        p2 = tmp_path / "b.md"
        p1.write_text("a")
        p2.write_text("b")
        result = resolve_resource_path([p1, p2])
        # Same dir, should appear only once
        assert result == str(tmp_path.resolve())

    def test_multiple_dirs(self, tmp_path: Path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        p1 = d1 / "a.md"
        p2 = d2 / "b.md"
        p1.write_text("a")
        p2.write_text("b")
        result = resolve_resource_path([p1, p2])
        parts = result.split(":")
        assert len(parts) == 2
        assert str(d1.resolve()) in parts
        assert str(d2.resolve()) in parts


class TestBuildExtraArgs:
    def test_minimal_epub(self):
        args = _build_extra_args(None, None, None, None, "/tmp", "epub")
        assert "--resource-path" in args
        assert "/tmp" in args
        assert "--pdf-engine=weasyprint" not in args

    def test_title_and_author(self):
        args = _build_extra_args("My Book", "Author Name", None, None, "/tmp", "epub")
        idx_title = args.index("--metadata")
        assert args[idx_title + 1] == "title=My Book"
        # Find second --metadata
        idx_author = args.index("--metadata", idx_title + 1)
        assert args[idx_author + 1] == "author=Author Name"

    def test_cover_image(self, tmp_path: Path):
        cover = tmp_path / "cover.png"
        args = _build_extra_args(None, None, cover, None, "/tmp", "epub")
        assert "--epub-cover-image" in args
        assert str(cover) in args

    def test_css(self, tmp_path: Path):
        css = tmp_path / "style.css"
        args = _build_extra_args(None, None, None, css, "/tmp", "epub")
        assert "--css" in args
        assert str(css) in args

    def test_pdf_weasyprint_engine(self):
        args = _build_extra_args(None, None, None, None, "/tmp", "pdf")
        assert "--pdf-engine=weasyprint" in args
        assert "-t" in args
        assert "html" in args

    def test_resource_path_always_present(self):
        args = _build_extra_args(None, None, None, None, "/a:/b", "epub")
        idx = args.index("--resource-path")
        assert args[idx + 1] == "/a:/b"


class TestOutputFilename:
    def test_single_file(self, tmp_path: Path):
        p = tmp_path / "chapter.md"
        assert _output_filename([p], None, "epub") == "chapter.epub"

    def test_multiple_with_title(self, tmp_path: Path):
        p1 = tmp_path / "a.md"
        p2 = tmp_path / "b.md"
        assert _output_filename([p1, p2], "My Great Book!", "epub") == "my-great-book.epub"

    def test_multiple_no_title(self, tmp_path: Path):
        p1 = tmp_path / "a.md"
        p2 = tmp_path / "b.md"
        assert _output_filename([p1, p2], None, "pdf") == "ebook.pdf"


class TestConvertEbook:
    @patch("convert_ebook.pypandoc.convert_file")
    def test_epub_conversion(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        results = convert_ebook([md], "epub", out)

        assert len(results) == 1
        assert results[0] == out / "test.epub"
        mock_convert.assert_called_once()
        call_args = mock_convert.call_args
        assert call_args[0][1] == "epub3"

    @patch("convert_ebook.pypandoc.convert_file")
    def test_pdf_conversion(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        results = convert_ebook([md], "pdf", out)

        assert len(results) == 1
        assert results[0] == out / "test.pdf"
        mock_convert.assert_called_once()
        call_args = mock_convert.call_args
        assert call_args[0][1] == "pdf"
        assert "--pdf-engine=weasyprint" in call_args[1]["extra_args"]

    @patch("convert_ebook.pypandoc.convert_file")
    def test_both_formats(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        results = convert_ebook([md], "both", out)

        assert len(results) == 2
        assert results[0] == out / "test.epub"
        assert results[1] == out / "test.pdf"
        assert mock_convert.call_count == 2

    @patch("convert_ebook.pypandoc.convert_file")
    def test_metadata_passed(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        convert_ebook([md], "epub", out, title="Test Title", author="Test Author")

        extra_args = mock_convert.call_args[1]["extra_args"]
        assert "--metadata" in extra_args
        assert "title=Test Title" in extra_args
        assert "author=Test Author" in extra_args

    @patch("convert_ebook.pypandoc.convert_file")
    def test_filename_from_stem(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "my-chapter.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        results = convert_ebook([md], "epub", out)

        assert results[0].name == "my-chapter.epub"

    @patch("convert_ebook.pypandoc.convert_file")
    def test_multiple_inputs_with_title(self, mock_convert: MagicMock, tmp_path: Path):
        md1 = tmp_path / "ch1.md"
        md2 = tmp_path / "ch2.md"
        md1.write_text("# Ch1")
        md2.write_text("# Ch2")
        out = tmp_path / "out"

        results = convert_ebook([md1, md2], "epub", out, title="My Book")

        assert results[0].name == "my-book.epub"
        call_args = mock_convert.call_args
        assert len(call_args[0][0]) == 2

    @patch("convert_ebook.pypandoc.convert_file")
    def test_creates_output_dir(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "nested" / "output"

        convert_ebook([md], "epub", out)

        assert out.exists()

    @patch("convert_ebook.pypandoc.convert_file", side_effect=RuntimeError("pandoc failed"))
    def test_conversion_error_propagates(self, mock_convert: MagicMock, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("# Hello")
        out = tmp_path / "out"

        with pytest.raises(RuntimeError, match="pandoc failed"):
            convert_ebook([md], "epub", out)
