"""Tests for session setup functionality."""

from unittest.mock import patch

import pytest


@pytest.mark.parametrize("role_input,expected_role", [
    ("Python", "Python"),
    ("ML Engineer", "ML Engineer"),
    ("just start", "Python"),
    ("", "Python"),
])
def test_prompt_session_setup_roles(role_input, expected_role):
    """Test that different role inputs are handled correctly."""
    from mockmate.main import prompt_session_setup
    
    # Non-"just start" paths need round_name and difficulty prompts too
    if role_input.lower() == "just start" or role_input == "":
        with patch('rich.prompt.Prompt.ask', return_value="just start"):
            role, _round_name, _difficulty = prompt_session_setup()
            assert role == expected_role
    else:
        with patch('rich.prompt.Prompt.ask', side_effect=[role_input, "DSA", "Beginner"]):
            role, _round_name, _difficulty = prompt_session_setup()
            assert role == expected_role


def test_just_start_uses_defaults():
    """Test that 'just start' input uses sensible defaults."""
    from mockmate.main import prompt_session_setup
    
    with patch('rich.prompt.Prompt.ask', return_value="just start"):
        role, round_name, difficulty = prompt_session_setup()
        assert role == "Python"
        assert round_name == "ML Fundamentals"
        assert difficulty == "Beginner"


def test_custom_parameters_are_preserved():
    """Test that custom parameters are preserved."""
    from mockmate.main import prompt_session_setup
    
    with patch('rich.prompt.Prompt.ask', side_effect=["ML Engineer", "DSA", "Advanced"]):
        role, round_name, difficulty = prompt_session_setup()
        assert role == "ML Engineer"
        assert round_name == "DSA"
        assert difficulty == "Advanced"


def test_question_index_limits_output():
    """Test that question index is respected."""
    from mockmate.interviewer import InterviewState, get_role_questions
    
    # Test that questions are retrieved by correct indices
    questions = get_role_questions("Python", "ML Fundamentals", "Beginner")
    assert len(questions) >= 3  # Should have at least 3 questions for beginner level
    
    state = InterviewState(question_idx=0)
    state.current_question = questions[0] if questions else ""
    assert state.question_idx == 0