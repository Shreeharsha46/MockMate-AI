"""Tests for approval module."""

from unittest.mock import patch


def test_request_human_approval_approve():
    """Test approval response."""
    from mockmate.approval import request_human_approval
    
    with patch('builtins.input', return_value='approve'):
        decision, content = request_human_approval(
            action_description="Test action",
            target_file="test.txt",
            proposed_content="Test content"
        )
        assert decision == "approve"
        assert content == "Test content"


def test_request_human_approval_reject():
    """Test rejection response."""
    from mockmate.approval import request_human_approval
    
    with patch('builtins.input', return_value='reject'):
        decision, content = request_human_approval(
            action_description="Test action",
            target_file="test.txt",
            proposed_content="Test content"
        )
        assert decision == "reject"
        assert content is None


def test_request_human_approval_edit():
    """Test edit response."""
    from mockmate.approval import request_human_approval
    
    # Use interactive_fn instead of mocking input for simpler test
    def mock_interactive(proposed):
        return ("edit", "Edited content here")
    
    decision, content = request_human_approval(
        action_description="Test action",
        target_file="test.txt",
        proposed_content="Original content",
        interactive_fn=mock_interactive
    )
    assert decision == "edit"
    assert content == "Edited content here"