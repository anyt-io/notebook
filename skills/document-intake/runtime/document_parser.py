"""Document parser for extracting structured data from domain-specific documents."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from config import DEFINITION_PATTERNS, RULE_INDICATORS, SECTION_HEADING_PATTERN, SUPPORTED_EXTENSIONS


class DocumentParser:
    """Parses PDF, text, and markdown files into structured representations."""

    def __init__(self) -> None:
        self._heading_re = re.compile(SECTION_HEADING_PATTERN, re.MULTILINE)
        self._definition_patterns = [re.compile(p, re.IGNORECASE) for p in DEFINITION_PATTERNS]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(self, path: str | Path) -> dict[str, Any]:
        """Parse a file and return structured data.

        Returns a dict with keys: source_file, sections, key_terms, rules, raw_text.
        """
        filepath = Path(path).resolve()
        self._validate_format(filepath)
        raw_text = self._read_file(filepath)
        return self._build_result(filepath.name, raw_text)

    def parse_text(self, text: str, source_name: str = "<text>") -> dict[str, Any]:
        """Parse raw text content and return structured data."""
        return self._build_result(source_name, text)

    @staticmethod
    def supported_formats() -> set[str]:
        """Return the set of supported file extensions."""
        return set(SUPPORTED_EXTENSIONS)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_result(self, source_name: str, raw_text: str) -> dict[str, Any]:
        sections = self._extract_sections(raw_text)
        key_terms = self._extract_key_terms(raw_text)
        rules = self._extract_rules(raw_text, sections)
        return {
            "source_file": source_name,
            "sections": sections,
            "key_terms": key_terms,
            "rules": rules,
            "raw_text": raw_text,
        }

    @staticmethod
    def _validate_format(filepath: Path) -> None:
        ext = filepath.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            msg = f"Unsupported file format: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            raise ValueError(msg)

    @staticmethod
    def _read_file(filepath: Path) -> str:
        ext = filepath.suffix.lower()
        if ext == ".pdf":
            return DocumentParser._read_pdf(filepath)
        return filepath.read_text(encoding="utf-8")

    @staticmethod
    def _read_pdf(filepath: Path) -> str:
        import pdfplumber

        pages: list[str] = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages)

    def _extract_sections(self, text: str) -> list[dict[str, str]]:
        """Split text into sections based on heading patterns."""
        matches = list(self._heading_re.finditer(text))
        if not matches:
            # No headings found — treat the whole text as one section
            stripped = text.strip()
            if stripped:
                return [{"heading": "Main", "content": stripped}]
            return []

        sections: list[dict[str, str]] = []

        # Capture any content before the first heading
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append({"heading": "Preamble", "content": preamble})

        for i, match in enumerate(matches):
            heading = match.group(0).strip().rstrip(":.)")
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            if content:
                sections.append({"heading": heading, "content": content})

        return sections

    def _extract_key_terms(self, text: str) -> list[dict[str, str]]:
        """Extract defined terms from the text."""
        terms: list[dict[str, str]] = []
        seen: set[str] = set()

        for pattern in self._definition_patterns:
            for match in pattern.finditer(text):
                term = match.group(1).strip()
                if term.lower() in seen or len(term) < 2:
                    continue
                seen.add(term.lower())
                # Grab surrounding sentence as the definition context
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 200)
                snippet = text[start:end]
                # Trim to sentence boundary
                period_pos = snippet.find(".", match.end() - start)
                if period_pos != -1:
                    snippet = snippet[: period_pos + 1]
                terms.append({"term": term, "definition": snippet.strip()})

        return terms

    def _extract_rules(self, text: str, sections: list[dict[str, str]]) -> list[dict[str, str]]:
        """Extract rule-like sentences from the text."""
        rules: list[dict[str, str]] = []
        rule_id = 0

        # Work section by section for better source attribution
        for section in sections:
            sentences = re.split(r"(?<=[.!?])\s+", section["content"])
            for sentence in sentences:
                lower = sentence.lower()
                if any(indicator in lower for indicator in RULE_INDICATORS):
                    rule_id += 1
                    rules.append(
                        {
                            "id": f"R{rule_id}",
                            "text": sentence.strip(),
                            "source_section": section["heading"],
                        }
                    )

        return rules
