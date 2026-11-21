"""Answer evaluation module using Pydantic for structured scorecard validation."""

import os

from pydantic import BaseModel, Field, validator


class Scorecard(BaseModel):
    """Structured scorecard for answer evaluation."""
    score: int = Field(..., ge=0, le=10, description="Score from 0 to 10")
    strengths: list[str] = Field(..., min_length=2, max_length=2, description="Exactly two strengths")
    gaps: list[str] = Field(..., min_length=2, max_length=2, description="Exactly two improvement areas")
    hint: str = Field(..., description="One actionable hint")
    next_topic: str = Field(..., description="Topic for the next question")

    @validator("score")
    def score_must_be_integer_range(cls, v):
        if not isinstance(v, int):
            raise TypeError("Score must be an integer")
        if v < 0 or v > 10:
            raise ValueError("Score must be between 0 and 10")
        return v

    @validator("strengths")
    def strengths_exactly_two(cls, v):
        if len(v) != 2:
            raise ValueError("Exactly two strengths required")
        return v

    @validator("gaps")
    def gaps_exactly_two(cls, v):
        if len(v) != 2:
            raise ValueError("Exactly two gaps required")
        return v


def evaluate_answer(
    answer: str,
    question: str,
    role: str,
    round_name: str,
    difficulty: str,
) -> Scorecard:
    """Evaluate an answer and return a validated scorecard.
    
    This function uses a LangChain LLM to evaluate the answer and returns
    a Pydantic-validated Scorecard object.
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import ChatOllama
    
    # Initialize model
    provider = os.getenv("MODEL_PROVIDER", "ollama")
    model_name = os.getenv("MODEL_NAME", "llama3.2")
    api_base = os.getenv("API_BASE", "http://localhost:11434")
    
    if provider == "ollama":
        model = ChatOllama(
            model=model_name,
            base_url=api_base,
            temperature=0.3,
        )
    else:
        # Fallback for other providers
        model = ChatOllama(
            model=model_name,
            base_url=api_base,
            temperature=0.3,
        )
    
    # Evaluation prompt
    system_prompt = f"""You are a technical interview evaluator. Evaluate the student's answer to a technical question.

Role: {role}
Round: {round_name}
Difficulty: {difficulty}

Scoring rubric:
- Score 8-10: Excellent answer, demonstrates deep understanding
- Score 5-7: Adequate answer, basic understanding with some gaps
- Score 0-4: Poor answer, significant misunderstandings or incorrect

Return a valid JSON with: score (integer 0-10), strengths (exactly 2 short strings), gaps (exactly 2 short strings), hint (one actionable hint), next_topic (topic for next question).
Be honest - do not give every answer 8/10. A deliberately wrong answer must receive appropriately low score.
"""
    
    human_prompt = f"""Question: {question}

Student answer: {answer}

Evaluate this answer and provide a valid JSON scorecard with exactly:
- score: integer 0-10
- strengths: exactly two meaningful strengths
- gaps: exactly two specific improvement areas
- hint: one actionable hint
- next_topic: the topic for the next question
"""
    
    try:
        import json

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])

        chain = prompt | model
        response = chain.invoke({})

        # Try to parse the response
        content = response.content if hasattr(response, "content") else str(response)

        # Try to find JSON in the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = content[start:end]
            data = json.loads(json_str)
        else:
            data = json.loads(content)

        # Validate and return Scorecard
        return Scorecard(**data)

    except (TypeError, ValueError, json.JSONDecodeError) as e:
        # Return a default poor score if evaluation fails
        print(f"Evaluation error: {e}")
        return Scorecard(
            score=2,
            strengths=["Attempted to answer", "Showed basic willingness"],
            gaps=["Needs improvement in core concepts", "Lacks depth in explanation"],
            hint="Review the fundamental concepts and try again",
            next_topic=question.split()[0] if question else "basics",
        )