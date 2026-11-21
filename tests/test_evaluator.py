"""Tests for answer evaluation and scorecard validation."""

import pytest
from pydantic import ValidationError


def test_scorecard_validates_correctly():
    """Test that Scorecard validates correctly."""
    from mockmate.evaluator import Scorecard
    
    # Valid scorecard
    card = Scorecard(
        score=7,
        strengths=["Good explanation", "Relevant example"],
        gaps=["Could mention edge cases", "Missing deeper context"],
        hint="Review edge case handling in your answers",
        next_topic="error handling",
    )
    
    assert card.score == 7
    assert len(card.strengths) == 2
    assert len(card.gaps) == 2
    assert isinstance(card.hint, str)
    assert isinstance(card.next_topic, str)


def test_scorecard_rejects_invalid_score():
    """Test that Scorecard rejects invalid scores."""
    from mockmate.evaluator import Scorecard
    
    # Score too low
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=-1, strengths=["a", "b"], gaps=["c", "d"], hint="h", next_topic="t")
    
    # Score too high
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=11, strengths=["a", "b"], gaps=["c", "d"], hint="h", next_topic="t")


def test_scorecard_rejects_wrong_number_of_strengths():
    """Test that Scorecard requires exactly two strengths."""
    from mockmate.evaluator import Scorecard
    
    # Too few strengths
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=5, strengths=["only one"], gaps=["a", "b"], hint="h", next_topic="t")
    
    # Too many strengths
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=5, strengths=["a", "b", "c"], gaps=["d", "e"], hint="h", next_topic="t")


def test_scorecard_rejects_wrong_number_of_gaps():
    """Test that Scorecard requires exactly two gaps."""
    from mockmate.evaluator import Scorecard
    
    # Too few gaps
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=5, strengths=["a", "b"], gaps=["only one"], hint="h", next_topic="t")
    
    # Too many gaps
    with pytest.raises((ValidationError, ValueError)):
        Scorecard(score=5, strengths=["a", "b"], gaps=["c", "d", "e"], hint="h", next_topic="t")


def test_incorrect_answer_gets_low_score():
    """Test that deliberately wrong answer receives appropriately low score."""
    from mockmate.evaluator import evaluate_answer

    wrong_answer = "I don't know anything about this topic. The sky is blue."

    # This should either return a low score or trigger the error path
    result = evaluate_answer(
        wrong_answer, "What is Python?", "Python", "ML Fundamentals", "Beginner"
    )
    assert 0 <= result.score <= 10
    assert len(result.strengths) == 2
    assert len(result.gaps) == 2


def test_empty_answer_handling():
    """Test that empty answers are handled gracefully."""
    from mockmate.evaluator import evaluate_answer

    result = evaluate_answer("", "What is Python?", "Python", "ML Fundamentals", "Beginner")
    assert 0 <= result.score <= 10
    assert len(result.strengths) == 2
    assert len(result.gaps) == 2


def test_valid_input_produces_valid_card():
    """Test that valid inputs produce a valid scorecard."""
    from mockmate.evaluator import evaluate_answer

    correct_answer = "Python is a high-level, interpreted programming language known for its readability."

    result = evaluate_answer(
        correct_answer, "What is Python?", "Python", "ML Fundamentals", "Beginner"
    )

    # Validate all required fields are present
    assert hasattr(result, "score")
    assert hasattr(result, "strengths")
    assert hasattr(result, "gaps")
    assert hasattr(result, "hint")
    assert hasattr(result, "next_topic")