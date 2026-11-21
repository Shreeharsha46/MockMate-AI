# MockMate Demo Documentation
# This file contains example inputs and expected outputs for demonstrating the system.

## Basic Run Sequence

### Starting the Application
```bash
cd C:\Users\SHREEHARSHA\MockMate-AI\MockMate
uv run python main.py
```

### Expected Output (with "just start" defaults)
1. Welcome banner displays with title "MockMate - AI-Powered Technical Interviewer"
2. Setup prompts appear asking for role, round, and difficulty
3. After entering "just start":
   - Role: Python
   - Round: ML Fundamentals
   - Difficulty: Beginner
4. System confirms using sensible defaults
5. Session ID is generated and displayed
6. First question appears in a cyan panel

### Example Question Flow
- Question 1: "What is the difference between a list and a tuple in Python?"
- [Student enters answer]
- Evaluation screen shows scorecard table with score/strengths/gaps/hint/next_topic
- Repeat for 5 questions total

### Completion Sequence
1. Final summary display with "[bold green]INTERVIEW SESSION COMPLETE![/bold green]"
2. Path to saved session report displayed
3. Weak topics approval prompt (if applicable)