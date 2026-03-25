"""Generate structured question banks from parsed document data."""

from __future__ import annotations

import hashlib
from typing import Any

from config import MAX_DIFFICULTY, MIN_DIFFICULTY


class QuestionGenerator:
    """Generates interview-style questions from parsed document output."""

    def __init__(self, domain: str = "general") -> None:
        self.domain = domain

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_bank(self, parsed: dict[str, Any]) -> dict[str, Any]:
        """Produce a full question bank from parsed document data.

        Args:
            parsed: Output of ``DocumentParser.parse_file`` or ``parse_text``.

        Returns:
            A dict with ``metadata`` and ``questions`` keys.
        """
        questions: list[dict[str, Any]] = []

        questions.extend(self._questions_from_key_terms(parsed.get("key_terms", [])))
        questions.extend(self._questions_from_rules(parsed.get("rules", [])))
        questions.extend(self._questions_from_sections(parsed.get("sections", [])))

        # Deduplicate by question text
        seen_texts: set[str] = set()
        unique: list[dict[str, Any]] = []
        for q in questions:
            if q["text"] not in seen_texts:
                seen_texts.add(q["text"])
                unique.append(q)

        # Assign sequential IDs
        for idx, q in enumerate(unique, start=1):
            q["id"] = f"Q{idx:03d}"

        return {
            "metadata": {
                "source_file": parsed.get("source_file", "<unknown>"),
                "domain": self.domain,
                "total_questions": len(unique),
            },
            "questions": unique,
        }

    # ------------------------------------------------------------------
    # Internal question generators
    # ------------------------------------------------------------------

    def _questions_from_key_terms(self, key_terms: list[dict[str, str]]) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        for term_entry in key_terms:
            term = term_entry.get("term", "")
            definition = term_entry.get("definition", "")
            if not term:
                continue
            keywords = self._extract_keywords(definition)
            questions.append(
                {
                    "id": "",
                    "text": f'What is the definition of "{term}"?',
                    "category": "definition",
                    "difficulty": 2,
                    "expected_answer_keywords": keywords,
                    "source_section": "",
                    "domain": self.domain,
                }
            )
        return questions

    def _questions_from_rules(self, rules: list[dict[str, str]]) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        for rule in rules:
            rule_text = rule.get("text", "")
            source = rule.get("source_section", "")
            if not rule_text:
                continue
            keywords = self._extract_keywords(rule_text)
            # Determine sub-category based on content
            category = self._classify_rule(rule_text)
            difficulty = self._estimate_difficulty(rule_text)
            questions.append(
                {
                    "id": "",
                    "text": f"Explain the following requirement: {rule_text}",
                    "category": category,
                    "difficulty": difficulty,
                    "expected_answer_keywords": keywords,
                    "source_section": source,
                    "domain": self.domain,
                }
            )
        return questions

    def _questions_from_sections(self, sections: list[dict[str, str]]) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        for section in sections:
            heading = section.get("heading", "")
            content = section.get("content", "")
            if not heading or not content or len(content) < 40:
                continue
            keywords = self._extract_keywords(content)
            questions.append(
                {
                    "id": "",
                    "text": f'Describe the key points covered in "{heading}".',
                    "category": "procedure",
                    "difficulty": 3,
                    "expected_answer_keywords": keywords,
                    "source_section": heading,
                    "domain": self.domain,
                }
            )
        return questions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_keywords(text: str, max_keywords: int = 5) -> list[str]:
        """Extract the most relevant keywords from a text snippet."""
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "shall",
            "should",
            "may",
            "might",
            "must",
            "can",
            "could",
            "of",
            "in",
            "to",
            "for",
            "with",
            "on",
            "at",
            "from",
            "by",
            "as",
            "or",
            "and",
            "not",
            "no",
            "if",
            "but",
            "that",
            "this",
            "it",
            "its",
            "any",
            "all",
            "each",
            "than",
            "such",
            "into",
            "also",
            "who",
            "which",
            "when",
            "where",
        }
        import re

        words = re.findall(r"[a-zA-Z]{3,}", text.lower())
        # Score by frequency, excluding stop words
        freq: dict[str, int] = {}
        for w in words:
            if w not in stop_words:
                freq[w] = freq.get(w, 0) + 1
        # Sort by frequency descending, then alphabetically for stability
        ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        return [w for w, _ in ranked[:max_keywords]]

    @staticmethod
    def _classify_rule(text: str) -> str:
        """Classify a rule sentence into a question category."""
        lower = text.lower()
        if "eligible" in lower or "eligibility" in lower or "qualify" in lower:
            return "eligibility"
        if "exception" in lower or "unless" in lower or "except" in lower:
            return "exception"
        if "procedure" in lower or "step" in lower or "process" in lower or "file" in lower:
            return "procedure"
        return "rule"

    @staticmethod
    def _estimate_difficulty(text: str) -> int:
        """Heuristically estimate question difficulty (1-5) based on text complexity."""
        length = len(text.split())
        if length < 10:
            return max(MIN_DIFFICULTY, 1)
        if length < 20:
            return 2
        if length < 35:
            return 3
        if length < 50:
            return 4
        return min(MAX_DIFFICULTY, 5)

    @staticmethod
    def _stable_id(text: str) -> str:
        """Generate a stable short hash for deduplication."""
        return hashlib.sha256(text.encode()).hexdigest()[:8]
