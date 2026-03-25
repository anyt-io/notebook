"""Tests for the QuestionGenerator class."""

from __future__ import annotations

from typing import Any

import pytest

from question_generator import QuestionGenerator

SAMPLE_PARSED: dict[str, Any] = {
    "source_file": "test_doc.txt",
    "sections": [
        {
            "heading": "Section 1: Definitions",
            "content": "This section defines key terms used throughout the regulation for immigration proceedings.",
        },
        {
            "heading": "Section 2: Eligibility",
            "content": "An applicant must be at least 18 years old. The sponsor shall demonstrate financial ability.",
        },
    ],
    "key_terms": [
        {"term": "Applicant", "definition": '"Applicant" means any person who submits an application.'},
        {"term": "Sponsor", "definition": '"Sponsor" refers to a lawful permanent resident.'},
    ],
    "rules": [
        {
            "id": "R1",
            "text": "An applicant must be at least 18 years old.",
            "source_section": "Section 2: Eligibility",
        },
        {
            "id": "R2",
            "text": "The sponsor shall demonstrate financial ability to support the beneficiary.",
            "source_section": "Section 2: Eligibility",
        },
    ],
    "raw_text": "...",
}


@pytest.fixture
def generator() -> QuestionGenerator:
    return QuestionGenerator(domain="immigration")


class TestGenerateFromSections:
    def test_generates_questions(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        assert bank["questions"]
        assert len(bank["questions"]) > 0

    def test_metadata_present(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        meta = bank["metadata"]
        assert meta["source_file"] == "test_doc.txt"
        assert meta["domain"] == "immigration"
        assert meta["total_questions"] == len(bank["questions"])

    def test_questions_from_all_sources(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        categories = {q["category"] for q in bank["questions"]}
        # Should have definition questions (from key_terms) and rule questions
        assert "definition" in categories


class TestQuestionStructure:
    def test_required_fields(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        required = {"id", "text", "category", "difficulty", "expected_answer_keywords", "source_section", "domain"}
        for q in bank["questions"]:
            assert required.issubset(q.keys()), f"Missing fields in question: {required - q.keys()}"

    def test_id_format(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        for q in bank["questions"]:
            assert q["id"].startswith("Q")
            # Should be Qnnn format
            assert len(q["id"]) == 4

    def test_domain_matches(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        for q in bank["questions"]:
            assert q["domain"] == "immigration"


class TestDifficultyRange:
    def test_difficulty_within_bounds(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        for q in bank["questions"]:
            assert 1 <= q["difficulty"] <= 5, f"Difficulty {q['difficulty']} out of range for: {q['text']}"

    def test_difficulty_is_int(self, generator: QuestionGenerator) -> None:
        bank = generator.generate_bank(SAMPLE_PARSED)
        for q in bank["questions"]:
            assert isinstance(q["difficulty"], int)


class TestEmptyInput:
    def test_empty_parsed_data(self, generator: QuestionGenerator) -> None:
        empty_parsed: dict[str, Any] = {
            "source_file": "empty.txt",
            "sections": [],
            "key_terms": [],
            "rules": [],
            "raw_text": "",
        }
        bank = generator.generate_bank(empty_parsed)
        assert bank["questions"] == []
        assert bank["metadata"]["total_questions"] == 0

    def test_missing_keys(self, generator: QuestionGenerator) -> None:
        minimal: dict[str, Any] = {"source_file": "minimal.txt"}
        bank = generator.generate_bank(minimal)
        assert bank["questions"] == []
        assert bank["metadata"]["total_questions"] == 0
