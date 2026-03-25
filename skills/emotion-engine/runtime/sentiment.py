"""Keyword-based sentiment analyzer for interview responses."""

from __future__ import annotations

import re

# Positive indicators
POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "happy",
    "pleased",
    "confident",
    "sure",
    "absolutely",
    "definitely",
    "yes",
    "agree",
    "correct",
    "right",
    "exactly",
    "certainly",
    "glad",
    "love",
    "enjoy",
    "proud",
    "accomplished",
    "successful",
    "wonderful",
    "fantastic",
    "amazing",
    "positive",
    "excited",
    "thrilled",
    "delighted",
    "satisfied",
    "thankful",
}

# Negative indicators
NEGATIVE_WORDS = {
    "bad",
    "terrible",
    "awful",
    "hate",
    "dislike",
    "no",
    "never",
    "wrong",
    "mistake",
    "fail",
    "failed",
    "problem",
    "issue",
    "difficult",
    "hard",
    "unfortunately",
    "regret",
    "sorry",
    "disappointed",
    "frustrated",
    "angry",
    "upset",
    "worried",
    "anxious",
    "nervous",
    "afraid",
    "scared",
    "concerned",
    "unhappy",
    "sad",
}

# Hedging / uncertainty words
HEDGING_WORDS = {
    "maybe",
    "perhaps",
    "possibly",
    "might",
    "could",
    "somewhat",
    "sort of",
    "kind of",
    "i think",
    "i guess",
    "i suppose",
    "not sure",
    "not certain",
    "probably",
    "likely",
    "unlikely",
    "it depends",
    "hard to say",
}

# Evasion indicators
EVASION_PHRASES = {
    "i don't remember",
    "i can't recall",
    "that's a good question",
    "let me think",
    "it's complicated",
    "i'd rather not",
    "can we move on",
    "next question",
    "i don't know",
    "no comment",
    "i'm not sure about that",
    "that's not relevant",
    "why do you ask",
    "what do you mean",
    "can you repeat",
    "i'd have to check",
}

# Confidence indicators
CONFIDENCE_WORDS = {
    "absolutely",
    "certainly",
    "definitely",
    "without a doubt",
    "i'm sure",
    "i know",
    "clearly",
    "obviously",
    "of course",
    "no question",
    "undoubtedly",
    "i'm confident",
    "for certain",
    "guaranteed",
    "i believe strongly",
}


class SentimentAnalyzer:
    """Analyzes text sentiment using keyword-based approach."""

    def analyze(self, text: str) -> dict[str, object]:
        """Analyze text and return polarity, subjectivity, and detected keywords.

        Returns:
            dict with keys:
                - polarity: float from -1.0 to 1.0
                - subjectivity: float from 0.0 to 1.0
                - keywords: list of detected sentiment keywords
        """
        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))

        positive_found = words & POSITIVE_WORDS
        negative_found = words & NEGATIVE_WORDS

        # Check multi-word phrases
        positive_phrases: list[str] = []
        negative_phrases: list[str] = []
        hedging_found: list[str] = []

        for phrase in HEDGING_WORDS:
            if phrase in text_lower:
                hedging_found.append(phrase)

        pos_count = len(positive_found) + len(positive_phrases)
        neg_count = len(negative_found) + len(negative_phrases)
        total_sentiment_words = pos_count + neg_count

        # Calculate polarity: -1 to 1
        polarity = 0.0 if total_sentiment_words == 0 else (pos_count - neg_count) / total_sentiment_words

        # Calculate subjectivity: more sentiment words = more subjective
        word_count = max(len(words), 1)
        subjectivity = min(1.0, (total_sentiment_words + len(hedging_found)) / (word_count * 0.5))

        keywords = sorted(
            list(positive_found) + positive_phrases + list(negative_found) + negative_phrases + hedging_found
        )

        return {
            "polarity": round(max(-1.0, min(1.0, polarity)), 3),
            "subjectivity": round(max(0.0, min(1.0, subjectivity)), 3),
            "keywords": keywords,
        }

    def detect_evasion(self, text: str, expected_keywords: list[str] | None = None) -> float:
        """Score how evasive a response is (0.0 = direct, 1.0 = highly evasive).

        Args:
            text: The response text to analyze.
            expected_keywords: Optional keywords expected in a direct answer.
        """
        text_lower = text.lower()
        score = 0.0

        # Check for evasion phrases
        evasion_count = sum(1 for phrase in EVASION_PHRASES if phrase in text_lower)
        score += min(0.5, evasion_count * 0.15)

        # Check for hedging
        hedging_count = sum(1 for phrase in HEDGING_WORDS if phrase in text_lower)
        score += min(0.3, hedging_count * 0.1)

        # Check if expected keywords are missing
        if expected_keywords:
            words_found = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
            if len(expected_keywords) > 0:
                missing_ratio = 1.0 - (words_found / len(expected_keywords))
                score += missing_ratio * 0.2

        # Very short answers can be evasive
        word_count = len(text.split())
        if word_count < 3:
            score += 0.2
        elif word_count < 6:
            score += 0.1

        return round(min(1.0, score), 3)

    def detect_confidence_level(self, text: str) -> float:
        """Detect how confident the speaker sounds (0.0 = uncertain, 1.0 = very confident).

        Args:
            text: The response text to analyze.
        """
        text_lower = text.lower()

        confidence_count = sum(1 for phrase in CONFIDENCE_WORDS if phrase in text_lower)
        hedging_count = sum(1 for phrase in HEDGING_WORDS if phrase in text_lower)

        # Base confidence from word presence
        base_confidence = 0.5
        base_confidence += min(0.4, confidence_count * 0.15)
        base_confidence -= min(0.4, hedging_count * 0.12)

        # Exclamation marks suggest confidence
        if "!" in text:
            base_confidence += 0.05

        # Question marks in responses suggest uncertainty
        question_count = text.count("?")
        base_confidence -= min(0.2, question_count * 0.1)

        return round(max(0.0, min(1.0, base_confidence)), 3)
