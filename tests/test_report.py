"""Tests for report generation module."""

from unittest.mock import patch


def test_generate_session_report():
    """Test session report markdown generation."""
    from mockmate.report import generate_session_report
    
    qa_pairs = [
        {
            "question": "What is Python?",
            "answer": "It's a programming language.",
            "scorecard": {
                "score": 7,
                "strengths": ["Good definition", "Clear explanation"],
                "gaps": ["Could mention dynamic typing", "Missing examples"],
                "hint": "Add code examples",
                "next_topic": "variables"
            }
        }
    ]
    
    report = generate_session_report(
        "TEST001",
        "Python Developer",
        "Programming Fundamentals",
        "Beginner",
        qa_pairs,
        ["dynamic_typing"]
    )
    
    assert "TEST001" in report
    assert "Python Developer" in report
    assert "7/10" in report
    assert "dynamic_typing" in report


def test_save_session_report_creates_file():
    """Test that saving report creates file in workspace."""
    from unittest.mock import MagicMock as MMagicMock
    
    with patch('mockmate.report.secure_write_file') as mock_write:
        mock_write.return_value = MMagicMock(path="workspace/sessions/test.md")
        
        from mockmate.report import save_session_report
        save_session_report(
            "TEST002",
            "Software Engineer",
            "DSA",
            "Intermediate",
            [],
            []
        )
        
        assert mock_write.called