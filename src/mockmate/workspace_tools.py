"""Workspace tools module - provides secure file operations restricted to workspace directory."""

from pathlib import Path


class WorkspaceSecurityError(PermissionError):
    """Raised when an operation attempts to escape the authorized workspace directory."""


def get_workspace_dir() -> Path:
    """Get the absolute path to the authorized workspace directory."""
    # Returns workspace/ under project root
    project_root = Path(__file__).parent.parent.parent
    workspace_dir = project_root / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    return workspace_dir.resolve()


def validate_workspace_path(path_str: str) -> Path:
    """Validate that a target path is inside the workspace directory.
    
    Raises WorkspaceSecurityError if the path escapes the workspace.
    """
    workspace_dir = get_workspace_dir()
    
    # Resolve target path
    target_path = Path(path_str)
    if not target_path.is_absolute():
        target_path = (workspace_dir / target_path).resolve()
    else:
        target_path = target_path.resolve()
        
    # Check path traversal
    try:
        # Check if target_path is relative to workspace_dir
        target_path.relative_to(workspace_dir)
    except ValueError:
        raise WorkspaceSecurityError(
            f"Path '{path_str}' escapes authorized workspace directory '{workspace_dir}'"
        )
        
    return target_path


def secure_write_file(path_str: str, content: str) -> Path:
    """Securely write content to a file inside the workspace."""
    validated_path = validate_workspace_path(path_str)
    
    # Ensure parent directory exists
    validated_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(validated_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return validated_path


def secure_read_file(path_str: str) -> str:
    """Securely read content from a file inside the workspace."""
    validated_path = validate_workspace_path(path_str)
    
    if not validated_path.exists():
        raise FileNotFoundError(f"File not found: {path_str}")
        
    with open(validated_path, "r", encoding="utf-8") as f:
        return f.read()


def secure_delete_file(path_str: str) -> bool:
    """Securely delete a file inside the workspace."""
    validated_path = validate_workspace_path(path_str)
    
    if validated_path.exists():
        validated_path.unlink()
        return True
    return False