"""Tests for summarizer module - context trimming."""

from unittest.mock import MagicMock


def test_trim_conversation_short():
    """Test trimming when message count is under limit."""
    from mockmate.summarizer import trim_conversation_history
    
    messages = [MagicMock(content="msg1"), MagicMock(content="msg2")]
    result = trim_conversation_history(messages, max_messages=10)
    assert len(result) == 2


def test_trim_conversation_long():
    """Test that excessive messages are trimmed."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    from mockmate.summarizer import trim_conversation_history
    
    # Create a long list of messages
    messages = []
    messages.append(SystemMessage(content="system"))
    for i in range(15):
        messages.append(HumanMessage(content=f"user {i}"))
        messages.append(AIMessage(content=f"ai {i}"))
    
    result = trim_conversation_history(messages, max_messages=10)
    # Should keep system message and most recent user/ai pairs
    assert len(result) <= 10


def test_summarize_empty():
    """Test summarizing empty message list."""
    from mockmate.summarizer import summarize_conversation
    
    result = summarize_conversation([])
    assert result == ""


def test_summarize_with_messages():
    """Test conversation summarization."""
    from langchain_core.messages import AIMessage, HumanMessage

    from mockmate.summarizer import summarize_conversation
    
    messages = [
        HumanMessage(content="Hello, how are you?"),
        AIMessage(content="I am fine, thank you."),
    ]
    
    result = summarize_conversation(messages)
    assert "Summary" in result or "Human:" in result