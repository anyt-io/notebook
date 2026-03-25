"""Ordinal mapping for free-text responses."""

from config import DEFAULT_CONFIG, EvaluationConfig


class OrdinalMapper:
    """Maps free-text responses to ordinal rankings for statistical comparison."""

    def __init__(self, config: EvaluationConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG

    def map_response(self, response: str, question_id: str, scale: int = 5) -> int:
        """Map a free-text response to an ordinal rank from 1 to scale.

        Uses response length, specificity, and structure as heuristic indicators
        of response quality for ordinal ranking.
        """
        if not response.strip():
            return 1

        score = self._compute_quality_score(response)

        # Map continuous score to ordinal scale
        rank = max(1, min(scale, round(score * (scale - 1)) + 1))
        return rank

    def map_batch(self, responses: list[dict]) -> dict[str, int]:
        """Map multiple responses to ordinal ranks.

        Each response dict must have 'response_id', 'response', and 'question_id' keys.
        """
        result: dict[str, int] = {}
        for item in responses:
            response_id = item["response_id"]
            response = item["response"]
            question_id = item["question_id"]
            scale = item.get("scale", self.config.ordinal_scale)
            result[response_id] = self.map_response(response, question_id, scale)
        return result

    def detect_collisions(self, mappings: dict[str, int], responses: list[dict]) -> list[dict]:
        """Find contradictory answer pairs where similar questions got very different ordinal ranks.

        Each response dict must have 'response_id', 'response', and 'question_id' keys.
        """
        collisions: list[dict] = []
        response_map = {r["response_id"]: r for r in responses}
        ids = list(mappings.keys())

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                id_a, id_b = ids[i], ids[j]
                rank_a, rank_b = mappings[id_a], mappings[id_b]

                if id_a not in response_map or id_b not in response_map:
                    continue

                resp_a = response_map[id_a]
                resp_b = response_map[id_b]

                # Check if questions are related (same question_id or similar)
                if resp_a.get("question_id") == resp_b.get("question_id"):
                    rank_diff = abs(rank_a - rank_b)
                    max_rank = max(mappings.values()) if mappings else 1
                    severity = rank_diff / max(max_rank, 1)

                    if severity >= self.config.collision_severity_threshold:
                        collisions.append(
                            {
                                "response_id_a": id_a,
                                "response_id_b": id_b,
                                "contradiction_description": (
                                    f"Responses to same question '{resp_a.get('question_id')}' "
                                    f"received ranks {rank_a} and {rank_b} (difference: {rank_diff})"
                                ),
                                "severity": round(severity, 4),
                            }
                        )

        return collisions

    def generate_ordinal_list(self, answers: list[str], question_context: str) -> list[dict]:
        """Generate an ordered list of answers with ordinal numbering.

        Per patent's ordinal mapping description, produces a ranked and numbered
        list for comparison and statistical analysis.
        """
        scored: list[tuple[int, str, float]] = []
        for idx, answer in enumerate(answers):
            quality = self._compute_quality_score(answer)
            scored.append((idx, answer, quality))

        # Sort by quality score descending
        scored.sort(key=lambda x: x[2], reverse=True)

        ordinal_list: list[dict] = []
        for rank, (original_idx, answer, quality) in enumerate(scored, start=1):
            ordinal_list.append(
                {
                    "ordinal_rank": rank,
                    "original_index": original_idx,
                    "answer": answer,
                    "quality_score": round(quality, 4),
                    "question_context": question_context,
                }
            )

        return ordinal_list

    def _compute_quality_score(self, response: str) -> float:
        """Compute a heuristic quality score (0-1) for a response."""
        score = 0.0

        # Length score (longer responses tend to be more complete, up to a point)
        words = response.split()
        word_count = len(words)
        if word_count >= 5:
            score += 0.2
        if word_count >= 15:
            score += 0.15
        if word_count >= 30:
            score += 0.1

        # Sentence structure (multiple sentences = more structured)
        import re

        sentences = [s.strip() for s in re.split(r"[.!?]+", response) if s.strip()]
        if len(sentences) >= 2:
            score += 0.15
        if len(sentences) >= 3:
            score += 0.1

        # Vocabulary diversity
        unique_words = set(w.lower() for w in words)
        if words:
            diversity = len(unique_words) / len(words)
            score += diversity * 0.2

        # Contains structured elements (lists, examples)
        if any(marker in response for marker in ["1.", "2.", "- ", "* ", "for example", "such as"]):
            score += 0.1

        return min(1.0, score)
