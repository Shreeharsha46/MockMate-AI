"""Human-in-the-Loop approval module for sensitive/destructive operations."""

from collections.abc import Callable


def request_human_approval(
    action_description: str,
    target_file: str,
    proposed_content: str | None = None,
    interactive_fn: Callable | None = None,
) -> tuple[str, str | None]:
    """Request human-in-the-loop approval before sensitive file operations.
    
    Actions:
    1. Approve: Execute original change
    2. Edit: Modify proposed change before approval
    3. Reject: Cancel operation leaving original untouched
    
    Returns:
        Tuple of (decision, final_content) where decision is one of "approve", "edit", "reject"
    """
    print("\n" + "=" * 60)
    print("HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Action: {action_description}")
    print(f"Target file: {target_file}")
    
    if proposed_content is not None:
        print("\nProposed Content / Changes:")
        print("-" * 40)
        print(proposed_content)
        print("-" * 40)
        
    print("\nPlease choose an option:")
    print("1. Approve - Execute the operation as proposed")
    print("2. Edit - Modify proposed changes before executing")
    print("3. Reject - Cancel operation (leave original untouched)")
    
    if interactive_fn:
        return interactive_fn(proposed_content)
        
    choice = input("\nEnter choice (1/2/3 or Approve/Edit/Reject): ").strip().lower()
    
    if choice in ["1", "approve", "a"]:
        print("\n[APPROVED] Operation will proceed.")
        return ("approve", proposed_content)
    elif choice in ["2", "edit", "e"]:
        print("\n[EDIT MODE] Enter new content below (end with empty line or Ctrl+Z):")
        if proposed_content:
            print(f"Current content preview: {proposed_content[:100]}...")
        
        # Get line-by-line input for editing
        lines = []
        try:
            while True:
                line = input()
                if not line and lines:  # Empty line ends input if already typed something
                    break
                lines.append(line)
        except EOFError:
            pass
            
        edited_content = "\n".join(lines) if lines else proposed_content
        print("\n[EDITED] Proceeding with modified content.")
        return ("edit", edited_content)
    else:
        print("\n[REJECTED] Operation cancelled. Target file left untouched.")
        return ("reject", None)