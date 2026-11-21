"""Persistent memory module using SqliteSaver checkpointer."""

import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer(db_path: str = "workspace/checkpoints.db") -> SqliteSaver:
    """Get or create SqliteSaver checkpointer."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)


def get_weak_topics(file_path: str = "workspace/weak-topics.md") -> list:
    """Read weak topics from saved Markdown file."""
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        topics = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "* ")):
                topic = line[2:].strip()
                if topic:
                    topics.append(topic)
        return topics
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading weak topics: {e}")
        return []


def save_weak_topics(topics: list, file_path: str = "workspace/weak-topics.md") -> None:
    """Save weak topics to Markdown file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    unique_topics = list(dict.fromkeys(topics))
    
    content = "# Tracked Weak Topics\n\n"
    for topic in unique_topics:
        content += f"- {topic}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)