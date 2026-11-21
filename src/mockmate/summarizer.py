"""Context management module - message trimming and summarization."""


from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


def trim_conversation_history(
    messages: list[BaseMessage],
    max_messages: int = 10,
    keep_system_message: bool = True,
) -> list[BaseMessage]:
    """Trim conversation history to prevent uncontrolled context growth.
    
    Keeps system messages intact and retains the most recent user/assistant turns.
    """
    if len(messages) <= max_messages:
        return messages
        
    system_messages = []
    other_messages = []
    
    for msg in messages:
        if isinstance(msg, SystemMessage) and keep_system_message:
            system_messages.append(msg)
        else:
            other_messages.append(msg)
            
    # Keep the most recent messages up to max_messages - system_messages length
    target_count = max_messages - len(system_messages)
    trimmed_other = other_messages[-target_count:] if target_count > 0 else []
    
    return system_messages + trimmed_other


def summarize_conversation(
    messages: list[BaseMessage],
    llm=None,
) -> str:
    """Summarize conversation history into a concise context summary."""
    if not messages:
        return ""
        
    summary_parts = []
    for msg in messages:
        role = "System" if isinstance(msg, SystemMessage) else "User" if isinstance(msg, HumanMessage) else "Interviewer"
        content = msg.content if hasattr(msg, "content") else str(msg)
        summary_parts.append(f"{role}: {content[:100]}...")
        
    return "Summary of previous context:\n" + "\n".join(summary_parts[-5:])