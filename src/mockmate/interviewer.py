from dataclasses import dataclass, field

from langchain_ollama import ChatOllama


@dataclass
class InterviewState:
    """State for the interview workflow."""
    role: str = ""
    round: str = ""
    difficulty: str = ""
    question_idx: int = 0
    current_question: str = ""
    student_answer: str = ""
    scorecard: object | None = None
    weak_topics: list = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    thread_id: str = ""


def get_interviewer_model():
    """Get the LLM model for the interviewer."""
    from .config import get_config
    config = get_config()
    provider = config["model_provider"]
    model_name = config["model_name"]
    api_base = config["api_base"]
    
    if provider == "ollama":
        return ChatOllama(
            model=model_name,
            base_url=api_base,
            temperature=0.7,
        )
    else:
        return ChatOllama(
            model=model_name,
            base_url=api_base,
            temperature=0.7,
        )


def get_role_questions(role: str, round_name: str, difficulty: str) -> list[str]:
    """Get questions for a specific role/round/difficulty combination."""
    questions_bank = {
        "Python": {
            "ML Fundamentals": {
                "Beginner": [
                    "What is the difference between a list and a tuple in Python?",
                    "Explain the concept of polymorphism in Python.",
                    "What are Python decorators and how do you use them?",
                ],
                "Intermediate": [
                    "Explain the MRO (Method Resolution Order) in Python inheritance.",
                    "What are context managers and how do you implement them using 'with' statement?",
                    "Explain the difference between lists, tuples, and sets in Python.",
                ],
                "Advanced": [
                    "Explain the GIL (Global Interpreter Lock) and its impact on multithreading.",
                    "What are metaclasses and how do they work in Python?",
                    "Explain Python's descriptor protocol.",
                ],
            },
        },
        "Machine Learning Fundamentals": {
            "Beginner": [
                "What is the difference between supervised and unsupervised learning?",
                "Explain the bias-variance tradeoff.",
                "What is overfitting and how can you prevent it?",
            ],
        },
        "DBMS": {
            "Beginner": [
                "What is the difference between SQL and NoSQL databases?",
                "Explain the concept of a primary key.",
                "What is a JOIN and what types of JOINs do you know?",
            ],
        },
        "Software Engineering": {
            "Beginner": [
                "What is the difference between vertical and horizontal scaling?",
                "Explain the concept of a REST API.",
                "What is version control and why is it important?",
            ],
        },
        "Behavioral Interviews": {
            "Beginner": [
                "Tell me about a time you faced a challenge at work.",
                "Describe a situation where you worked in a team.",
                "What is your greatest professional achievement?",
            ],
        },
    }
    
    role_questions = questions_bank.get(role, questions_bank.get("Software Engineering", {}))
    if isinstance(role_questions, dict):
        round_questions = role_questions.get(round_name, role_questions.get("Beginner", ["Tell me about your experience."]))
        if isinstance(round_questions, dict):
            difficulty_questions = round_questions.get(difficulty, ["Tell me about your experience."])
        else:
            difficulty_questions = round_questions
    else:
        difficulty_questions = role_questions
    
    return difficulty_questions if isinstance(difficulty_questions, list) else [str(difficulty_questions)]


def ask_question(state: InterviewState) -> InterviewState:
    """Ask the next question based on current state."""
    if state.question_idx >= 5:
        state.current_question = "Interview complete! Let's review your performance."
        return state
    
    role = state.role or "Software Engineer"
    round_name = state.round or "Technical"
    difficulty = state.difficulty or "Beginner"
    
    questions = get_role_questions(role, round_name, difficulty)
    
    if state.question_idx < len(questions):
        state.current_question = questions[state.question_idx]
    else:
        state.current_question = f"Tell me more about your experience in {role} ({round_name})."
    
    state.question_idx += 1
    return state
