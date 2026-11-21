"""LangGraph workflow definition for MockMate interview agent."""

from typing import Any, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph

from .evaluator import evaluate_answer
from .interviewer import get_role_questions
from .memory import get_weak_topics


class AgentState(TypedDict):
    """LangGraph State representation."""
    role: str
    round: str
    difficulty: str
    question_idx: int
    current_question: str
    student_answer: str
    scorecard: dict[str, Any]
    weak_topics: list[str]
    qa_history: list[dict[str, Any]]
    thread_id: str
    session_id: str
    status: str


def setup_node(state: AgentState) -> AgentState:
    """Initialize state and load weak topics if returning student."""
    role = state.get("role") or "Python"
    round_name = state.get("round") or "ML Fundamentals"
    difficulty = state.get("difficulty") or "Beginner"
    
    # Load past weak topics
    existing_weak_topics = get_weak_topics()
    
    state["role"] = role
    state["round"] = round_name
    state["difficulty"] = difficulty
    state["question_idx"] = 0
    state["weak_topics"] = existing_weak_topics
    state["qa_history"] = []
    state["status"] = "in_progress"
    
    return state


def question_node(state: AgentState) -> AgentState:
    """Select the next question based on performance and weak topics."""
    question_idx = state["question_idx"]
    
    if question_idx >= 5:
        state["current_question"] = "Interview Complete"
        state["status"] = "complete"
        return state
        
    role = state["role"]
    round_name = state["round"]
    difficulty = state["difficulty"]
    
    questions = get_role_questions(role, round_name, difficulty)
    
    if question_idx < len(questions):
        state["current_question"] = questions[question_idx]
    else:
        state["current_question"] = f"Explain key concepts of {round_name} in {role}."
        
    return state


def evaluation_node(state: AgentState) -> AgentState:
    """Evaluate student's response using validated scorecard."""
    answer = state.get("student_answer", "")
    question = state.get("current_question", "")
    
    scorecard = evaluate_answer(
        answer=answer,
        question=question,
        role=state["role"],
        round_name=state["round"],
        difficulty=state["difficulty"],
    )
    
    scorecard_dict = scorecard.dict()
    state["scorecard"] = scorecard_dict
    
    # Track weak topic if score is low (< 5)
    if scorecard.score < 5:
        weak_topic = question.split()[0] if question else "general"
        if weak_topic not in state["weak_topics"]:
            state["weak_topics"].append(weak_topic)
            
    # Record QA history
    state["qa_history"].append({
        "question": question,
        "answer": answer,
        "scorecard": scorecard_dict,
    })
    
    # Increment question index
    state["question_idx"] += 1
    
    return state


def build_interview_graph(checkpointer: SqliteSaver = None):
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("setup", setup_node)
    workflow.add_node("ask_question", question_node)
    workflow.add_node("evaluate", evaluation_node)
    
    # Set entry point
    workflow.set_entry_point("setup")
    
    # Define edges
    workflow.add_edge("setup", "ask_question")
    workflow.add_edge("ask_question", "evaluate")
    workflow.add_edge("evaluate", "ask_question")
    
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()