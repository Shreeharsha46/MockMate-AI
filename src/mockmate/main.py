"""Main entry point for MockMate CLI interface."""

import sys
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .approval import request_human_approval
from .evaluator import evaluate_answer
from .interviewer import get_role_questions
from .memory import get_weak_topics
from .report import save_session_report
from .workspace_tools import secure_write_file

console = Console()


def display_welcome():
    """Display welcome banner."""
    console.print(Panel.fit(
        "[bold blue]MockMate[/bold blue] - AI-Powered Technical Interviewer\n"
        "[italic]Master your technical interviews with adaptive, real-time AI feedback[/italic]",
        border_style="blue"
    ))


def prompt_session_setup() -> tuple[str, str, str]:
    """Prompt user for session parameters or use defaults."""
    console.print("\n[bold yellow]--- Interview Setup ---[/bold yellow]")
    console.print("Press ENTER or type 'just start' to use default settings.\n")
    
    role = Prompt.ask("What technical role are you preparing for?", default="just start")
    
    if role.strip().lower() == "just start":
        role = "Python"
        round_name = "ML Fundamentals"
        difficulty = "Beginner"
        console.print("\n[bold green]Using sensible defaults:[/bold green]")
        console.print(f"- Role: {role}")
        console.print(f"- Round: {round_name}")
        console.print(f"- Difficulty: {difficulty}\n")
        return role, round_name, difficulty
        
    round_name = Prompt.ask("Which interview round?", default="ML Fundamentals")
    difficulty = Prompt.ask("What difficulty level?", default="Beginner")
    
    return role.strip(), round_name.strip(), difficulty.strip()


def run_interview():
    """Main interview loop."""
    display_welcome()
    
    # 1. Setup session parameters
    role, round_name, difficulty = prompt_session_setup()
    
    # 2. Check existing weak topics
    existing_weak_topics = get_weak_topics()
    if existing_weak_topics:
        console.print(f"[yellow]Found previously recorded weak topics: {', '.join(existing_weak_topics)}[/yellow]")
        console.print("[yellow]We will focus on these areas during your interview![/yellow]\n")
        
    session_id = str(uuid.uuid4())[:8]
    console.print(f"[bold cyan]Starting Session ID: {session_id}[/bold cyan]\n")
    
    # 3. Get question bank
    questions = get_role_questions(role, round_name, difficulty)
    
    qa_pairs = []
    current_weak_topics = list(existing_weak_topics)
    
    # 4. Conduct 5-question interview loop
    for i in range(5):
        console.print(f"\n[bold magenta]=== Question {i+1} of 5 ===[/bold magenta]")
        
        # Select question
        if i < len(questions):
            question = questions[i]
        else:
            question = f"Describe key concepts in {round_name} related to {role}."
            
        console.print(Panel(f"[bold]{question}[/bold]", title=f"Question {i+1}", border_style="cyan"))
        
        # Get student response
        answer = Prompt.ask("\n[bold green]Your Answer[/bold green]")
        
        if not answer.strip():
            console.print("[yellow]No answer provided. Skipping evaluation.[/yellow]")
            continue
            
        console.print("\n[italic gray]Evaluating your answer...[/italic gray]")
        
        # Evaluate response
        scorecard = evaluate_answer(answer, question, role, round_name, difficulty)
        
        # Display scorecard
        table = Table(title=f"Scorecard: {scorecard.score}/10", border_style="green" if scorecard.score >= 7 else "yellow" if scorecard.score >= 5 else "red")
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="white")
        
        table.add_row("Score", f"{scorecard.score}/10")
        table.add_row("Strengths", "\n".join(f"• {s}" for s in scorecard.strengths))
        table.add_row("Improvement Areas", "\n".join(f"• {g}" for g in scorecard.gaps))
        table.add_row("Actionable Hint", scorecard.hint)
        table.add_row("Next Topic", scorecard.next_topic)
        
        console.print(table)
        
        # Record QA pair
        qa_pairs.append({
            "question": question,
            "answer": answer,
            "scorecard": scorecard,
        })
        
        # Track weak topic if score is low
        if scorecard.score < 5:
            topic = scorecard.next_topic or question.split()[0]
            if topic not in current_weak_topics:
                current_weak_topics.append(topic)
                
    # 5. Session summary & report generation
    console.print("\n[bold green]====================================================[/bold green]")
    console.print("[bold green]          INTERVIEW SESSION COMPLETE!               [/bold green]")
    console.print("[bold green]====================================================[/bold green]\n")
    
    # Save session report
    saved_report_path = save_session_report(
        session_id, role, round_name, difficulty, qa_pairs, current_weak_topics
    )
    console.print(f"[bold cyan]Session report saved to: {saved_report_path}[/bold cyan]")
    
    # Update weak topics file with human-in-the-loop approval
    if current_weak_topics != existing_weak_topics:
        proposed_content = "# Tracked Weak Topics\n\n" + "\n".join(f"- {t}" for t in set(current_weak_topics))
        
        decision, final_content = request_human_approval(
            action_description="Update weak topics tracking file",
            target_file="workspace/weak-topics.md",
            proposed_content=proposed_content,
        )
        
        if decision in ["approve", "edit"] and final_content:
            secure_write_file("weak-topics.md", final_content)
            console.print("[green]Weak topics updated successfully![/green]")
        else:
            console.print("[yellow]Weak topics update cancelled by user.[/yellow]")


def main():
    """Main entry point."""
    try:
        run_interview()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interview session ended by user.[/bold red]")
        sys.exit(0)
    except (OSError, RuntimeError, ValueError) as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()