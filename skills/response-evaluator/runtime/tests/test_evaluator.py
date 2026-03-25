"""Tests for the main evaluator."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluator import ResponseEvaluator
from models import EvaluationReport, ResponseEvaluation


class TestResponseEvaluator:
    def setup_method(self) -> None:
        self.evaluator = ResponseEvaluator()

    def test_evaluate_single_response(self) -> None:
        """Verify single response evaluation structure."""
        question = {
            "question_id": "q1",
            "text": "What is machine learning?",
            "expected_keywords": ["algorithm", "data", "model", "prediction"],
            "known_facts": ["Machine learning uses algorithms to learn from data."],
        }
        response = "Machine learning is a field where algorithms learn from data to make predictions using models."

        result = self.evaluator.evaluate_response(response, question)
        assert isinstance(result, ResponseEvaluation)
        assert 0.0 <= result.relevance_score <= 1.0
        assert 0.0 <= result.coherence_score <= 1.0
        assert 0.0 <= result.completeness_score <= 1.0
        assert 0.0 <= result.hallucination_score <= 1.0
        assert 1 <= result.ordinal_rank <= 5
        assert 0.0 <= result.confidence <= 1.0

    def test_evaluate_session(self) -> None:
        """Verify full session evaluation."""
        transcript = [
            {
                "response_id": "r1",
                "question_id": "q1",
                "response": "Machine learning uses algorithms to learn patterns from data.",
            },
            {
                "response_id": "r2",
                "question_id": "q2",
                "response": "Deep learning is a subset of machine learning using neural networks.",
            },
        ]
        question_bank = {
            "q1": {
                "question_id": "q1",
                "text": "What is machine learning?",
                "expected_keywords": ["algorithm", "data", "learn"],
                "known_facts": [],
            },
            "q2": {
                "question_id": "q2",
                "text": "What is deep learning?",
                "expected_keywords": ["neural", "network", "machine learning"],
                "known_facts": [],
            },
        }

        report = self.evaluator.evaluate_session(transcript, question_bank)
        assert isinstance(report, EvaluationReport)
        assert len(report.evaluations) == 2
        assert report.aggregate_score > 0
        assert report.confidence_interval[0] <= report.confidence_interval[1]

    def test_evaluation_report_structure(self) -> None:
        """Verify all fields are present in the evaluation report."""
        transcript = [
            {
                "response_id": "r1",
                "question_id": "q1",
                "response": "Test response.",
            },
        ]
        question_bank = {
            "q1": {
                "question_id": "q1",
                "text": "Test question?",
                "expected_keywords": ["test"],
                "known_facts": [],
            },
        }

        report = self.evaluator.evaluate_session(transcript, question_bank)
        report_dict = report.to_dict()

        assert "session_id" in report_dict
        assert "evaluations" in report_dict
        assert "colliding_answers" in report_dict
        assert "aggregate_score" in report_dict
        assert "confidence_interval" in report_dict
        assert "hallucination_count" in report_dict
        assert "recommendations" in report_dict

        # Check evaluation structure
        eval_dict = report_dict["evaluations"][0]
        assert "response_id" in eval_dict
        assert "original_response" in eval_dict
        assert "relevance_score" in eval_dict
        assert "coherence_score" in eval_dict
        assert "completeness_score" in eval_dict
        assert "hallucination_score" in eval_dict
        assert "ordinal_rank" in eval_dict
        assert "confidence" in eval_dict
        assert "flags" in eval_dict

    def test_empty_response_evaluation(self) -> None:
        """Empty response should get low scores."""
        question = {
            "question_id": "q1",
            "text": "What is Python?",
            "expected_keywords": ["programming"],
            "known_facts": [],
        }
        result = self.evaluator.evaluate_response("", question)
        assert result.relevance_score == 0.0
        assert result.completeness_score == 0.0
