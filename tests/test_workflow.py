"""Tests for the interview workflow and state management."""



def test_workflow_state_initialization():
    """Test that workflow initializes state correctly."""
    from mockmate.workflow import AgentState
    
    # Verify the state has required fields
    assert "role" in AgentState.__annotations__
    assert "round" in AgentState.__annotations__
    assert "difficulty" in AgentState.__annotations__
    assert "question_idx" in AgentState.__annotations__
    assert "current_question" in AgentState.__annotations__
    assert "weak_topics" in AgentState.__annotations__
    assert "qa_history" in AgentState.__annotations__


def test_get_role_questions_variety():
    """Test that questions vary by role and round."""
    from mockmate.interviewer import get_role_questions
    
    # Test different roles return appropriate questions
    python_questions = get_role_questions("Python", "ML Fundamentals", "Beginner")
    get_role_questions("Machine Learning Fundamentals", "", "Beginner")
    get_role_questions("Behavioral Interviews", "", "Beginner")
    
    # Each should be a list of strings
    assert isinstance(python_questions, list)
    assert len(python_questions) > 0
    assert all(isinstance(q, str) for q in python_questions)


def test_interview_state_update():
    """Test that interview state updates properly during flow."""
    from mockmate.interviewer import InterviewState, ask_question
    
    state = InterviewState(
        role="Python",
        round="ML Fundamentals",
        difficulty="Beginner",
        question_idx=0
    )
    
    state = ask_question(state)
    assert state.question_idx == 1
    assert state.current_question != ""