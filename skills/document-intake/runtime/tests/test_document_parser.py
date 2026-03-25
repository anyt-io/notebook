"""Tests for the DocumentParser class."""

from __future__ import annotations

import pytest

from document_parser import DocumentParser

SAMPLE_TEXT = """\
# Immigration Rules

## Section 1: Definitions

"Applicant" means any person who submits an application for immigration benefits.

"Sponsor" refers to a lawful permanent resident who files a petition on behalf of a family member.

## Section 2: Eligibility Requirements

An applicant must be at least 18 years of age. The applicant shall provide valid identification.
Any person who is prohibited from entry under Section 212 may not apply.

## Section 3: Filing Procedures

The applicant shall file Form I-130 with the appropriate service center.
Each petition must be accompanied by the required filing fee.
"""


@pytest.fixture
def parser() -> DocumentParser:
    return DocumentParser()


class TestParseTextContent:
    def test_returns_expected_keys(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        assert "source_file" in result
        assert "sections" in result
        assert "key_terms" in result
        assert "rules" in result
        assert "raw_text" in result

    def test_raw_text_preserved(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        assert result["raw_text"] == SAMPLE_TEXT

    def test_parse_plain_text(self, parser: DocumentParser) -> None:
        simple = "All applicants must submit Form I-485."
        result = parser.parse_text(simple)
        assert result["raw_text"] == simple


class TestExtractSections:
    def test_section_count(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        # The markdown headings should create multiple sections
        assert len(result["sections"]) >= 3

    def test_section_has_heading_and_content(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        for section in result["sections"]:
            assert "heading" in section
            assert "content" in section
            assert len(section["content"]) > 0

    def test_single_block_text(self, parser: DocumentParser) -> None:
        text = "This is a simple paragraph with no headings at all."
        result = parser.parse_text(text)
        assert len(result["sections"]) == 1
        assert result["sections"][0]["heading"] == "Main"


class TestExtractKeyTerms:
    def test_finds_defined_terms(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        term_names = [t["term"] for t in result["key_terms"]]
        assert "Applicant" in term_names
        assert "Sponsor" in term_names

    def test_term_has_definition(self, parser: DocumentParser) -> None:
        result = parser.parse_text(SAMPLE_TEXT)
        for term in result["key_terms"]:
            assert "term" in term
            assert "definition" in term
            assert len(term["definition"]) > 0

    def test_no_terms_in_plain_text(self, parser: DocumentParser) -> None:
        result = parser.parse_text("No special definitions here.")
        assert result["key_terms"] == []


class TestSupportedFormats:
    def test_supported_formats_returns_set(self) -> None:
        formats = DocumentParser.supported_formats()
        assert isinstance(formats, set)

    def test_includes_expected_extensions(self) -> None:
        formats = DocumentParser.supported_formats()
        assert ".pdf" in formats
        assert ".txt" in formats
        assert ".md" in formats
        assert ".markdown" in formats

    def test_rejects_unsupported_format(self, parser: DocumentParser, tmp_path: pytest.TempPathFactory) -> None:
        bad_file = tmp_path / "file.docx"  # type: ignore[operator]
        bad_file.write_text("content")  # type: ignore[union-attr]
        with pytest.raises(ValueError, match="Unsupported file format"):
            parser.parse_file(bad_file)  # type: ignore[arg-type]
