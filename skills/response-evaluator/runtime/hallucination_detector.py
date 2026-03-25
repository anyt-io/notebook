"""Hallucination detection for interview responses."""

import re
import string

from config import DEFAULT_CONFIG, EvaluationConfig


class HallucinationDetector:
    """Detects hallucinated or fabricated content in responses."""

    def __init__(self, config: EvaluationConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG

    def detect(
        self,
        response: str,
        question: str,
        expected_keywords: list[str],
        context: str = "",
    ) -> float:
        """Return a hallucination score between 0 (no hallucination) and 1 (fully hallucinated).

        Checks keyword relevance, factual grounding against context,
        specificity without basis, and contradiction with known facts.
        """
        if not response.strip():
            return 0.0

        keyword_score = self._check_keyword_relevance(response, expected_keywords)
        grounding_score = self._check_factual_grounding(response, context)
        specificity_score = self._check_unsupported_specificity(response, context, expected_keywords)

        # Weighted combination
        hallucination_score = (
            self.config.keyword_match_weight * (1.0 - keyword_score)
            + self.config.context_grounding_weight * (1.0 - grounding_score)
            + self.config.specificity_weight * specificity_score
        )

        # Apply sensitivity
        hallucination_score = min(1.0, hallucination_score * (0.5 + self.config.hallucination_sensitivity))

        return round(max(0.0, min(1.0, hallucination_score)), 4)

    def flag_fabrications(self, response: str, known_facts: list[str]) -> list[str]:
        """Return a list of potentially fabricated claims in the response."""
        fabrications: list[str] = []
        sentences = self._split_sentences(response)
        known_lower = [f.lower() for f in known_facts]

        for sentence in sentences:
            sentence_stripped = sentence.strip()
            if not sentence_stripped:
                continue

            # Check if sentence contains specific claims (numbers, names, dates)
            has_specific_claim = bool(re.search(r"\b\d{4}\b|\b\d+%|\b\d+\.\d+\b", sentence_stripped)) or bool(
                re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", sentence_stripped)
            )

            if has_specific_claim:
                # Check if any known fact supports this claim
                supported = any(self._text_overlap(sentence_stripped.lower(), fact) > 0.3 for fact in known_lower)
                if not supported:
                    fabrications.append(sentence_stripped)

        return fabrications

    def _check_keyword_relevance(self, response: str, expected_keywords: list[str]) -> float:
        """Check how many expected keywords appear in the response. Returns 0-1."""
        if not expected_keywords:
            return 0.5  # Neutral when no keywords provided

        response_lower = response.lower()
        response_words = set(self._tokenize(response_lower))
        matches = 0
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # Check exact substring or word match
            if keyword_lower in response_lower or keyword_lower in response_words:
                matches += 1

        return matches / len(expected_keywords)

    def _check_factual_grounding(self, response: str, context: str) -> float:
        """Check how well the response is grounded in the provided context. Returns 0-1."""
        if not context.strip():
            return 0.5  # Neutral when no context provided

        response_words = set(self._tokenize(response.lower()))
        context_words = set(self._tokenize(context.lower()))

        if not response_words:
            return 0.5

        # Remove common stop words
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
            "could",
            "should",
            "may",
            "might",
            "can",
            "shall",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "and",
            "but",
            "or",
            "nor",
            "not",
            "so",
            "yet",
            "both",
            "either",
            "neither",
            "each",
            "every",
            "all",
            "any",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "only",
            "own",
            "same",
            "than",
            "too",
            "very",
            "just",
            "because",
            "if",
            "when",
            "that",
            "this",
            "it",
            "i",
            "my",
            "me",
            "we",
            "our",
            "you",
            "your",
            "they",
            "their",
            "them",
            "he",
            "she",
            "his",
            "her",
            "what",
            "which",
            "who",
            "whom",
            "how",
            "where",
            "why",
        }
        content_response = response_words - stop_words
        content_context = context_words - stop_words

        if not content_response:
            return 0.5

        overlap = content_response & content_context
        return len(overlap) / len(content_response)

    def _check_unsupported_specificity(self, response: str, context: str, expected_keywords: list[str]) -> float:
        """Check for highly specific claims not supported by context or keywords. Returns 0-1."""
        specific_patterns = [
            r"\b\d{4}\b",  # Years
            r"\b\d+%",  # Percentages
            r"\b\d+\.\d+\b",  # Decimal numbers
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+",
            r"\b\d+(?:st|nd|rd|th)\b",  # Ordinal numbers
        ]

        specific_claims = 0
        unsupported_claims = 0
        combined_context = (context + " " + " ".join(expected_keywords)).lower()

        for pattern in specific_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                specific_claims += 1
                if match.lower() not in combined_context:
                    unsupported_claims += 1

        if specific_claims == 0:
            return 0.0

        return unsupported_claims / specific_claims

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences."""
        return re.split(r"(?<=[.!?])\s+", text)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple word tokenization."""
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text.split()

    @staticmethod
    def _text_overlap(text_a: str, text_b: str) -> float:
        """Calculate word overlap ratio between two texts."""
        words_a = set(text_a.split())
        words_b = set(text_b.split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        return len(intersection) / max(len(words_a), len(words_b))
