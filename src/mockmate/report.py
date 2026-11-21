"""Report generation module - creates human-readable session Markdown files."""

from datetime import datetime
from typing import Any

from .workspace_tools import secure_write_file


def generate_session_report(
    session_id: str,
    role: str,
    round_name: str,
    difficulty: str,
    qa_pairs: list[dict[str, Any]],
    weak_topics: list[str],
) -> str:
    """Generate a readable Markdown report for an interview session."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate summary metrics
    total_questions = len(qa_pairs)
    scores = [pair.get("scorecard", {}).get("score", 0) for pair in qa_pairs if "scorecard" in pair]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    report_md = f"""# MockMate Interview Session Report

## Session Details
- **Session ID**: {session_id}
- **Role**: {role}
- **Round**: {round_name}
- **Difficulty**: {difficulty}
- **Date/Time**: {now}
- **Total Questions**: {total_questions}
- **Average Score**: {avg_score:.1f} / 10

---

## Performance Summary
- **Overall Score**: {avg_score:.1f}/10
- **Identified Weak Topics**: {', '.join(weak_topics) if weak_topics else 'None identified'}

---

## Detailed Question & Answer Breakdown

"""

    for i, pair in enumerate(qa_pairs, 1):
        question = pair.get("question", "")
        answer = pair.get("answer", "")
        scorecard = pair.get("scorecard", {})
        
        score = scorecard.get("score", 0) if isinstance(scorecard, dict) else getattr(scorecard, "score", 0)
        strengths = scorecard.get("strengths", []) if isinstance(scorecard, dict) else getattr(scorecard, "strengths", [])
        gaps = scorecard.get("gaps", []) if isinstance(scorecard, dict) else getattr(scorecard, "gaps", [])
        hint = scorecard.get("hint", "") if isinstance(scorecard, dict) else getattr(scorecard, "hint", "")
        next_topic = scorecard.get("next_topic", "") if isinstance(scorecard, dict) else getattr(scorecard, "next_topic", "")
        
        report_md += f"""### Question {i}
**Question**: {question}

**Student Answer**:
> {answer}

**Evaluation**:
- **Score**: {score}/10
- **Strengths**:
  - {strengths[0] if len(strengths) > 0 else 'N/A'}
  - {strengths[1] if len(strengths) > 1 else 'N/A'}
- **Improvement Areas**:
  - {gaps[0] if len(gaps) > 0 else 'N/A'}
  - {gaps[1] if len(gaps) > 1 else 'N/A'}
- **Actionable Hint**: {hint}
- **Suggested Next Topic**: {next_topic}

---
"""

    return report_md


def save_session_report(
    session_id: str,
    role: str,
    round_name: str,
    difficulty: str,
    qa_pairs: list[dict[str, Any]],
    weak_topics: list[str],
) -> str:
    """Save the generated report to workspace/sessions/ directory."""
    report_content = generate_session_report(
        session_id, role, round_name, difficulty, qa_pairs, weak_topics
    )
    
    file_path = f"sessions/session_{session_id}.md"
    saved_path = secure_write_file(file_path, report_content)
    
    return str(saved_path)