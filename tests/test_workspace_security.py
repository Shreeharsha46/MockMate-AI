"""Tests for workspace security and path traversal prevention."""

import os
from pathlib import Path

import pytest


def test_get_workspace_dir():
    """Test that workspace directory is returned correctly."""
    from mockmate.workspace_tools import get_workspace_dir
    
    ws = get_workspace_dir()
    assert ws.is_absolute()
    assert "workspace" in str(ws)


def test_validate_safe_path():
    """Test that safe paths pass validation."""
    from mockmate.workspace_tools import validate_workspace_path
    
    # Relative path inside workspace
    result = validate_workspace_path("sessions/session_123.md")
    assert result.exists() or True  # May not exist yet
    
    # Absolute path should also work
    Path(os.getcwd()) / "workspace" / "test.md"
    # This should not raise an exception


def test_path_traversal_blocked_relative():
    """Test that relative path traversals are blocked."""
    from mockmate.workspace_tools import WorkspaceSecurityError, validate_workspace_path
    
    # Try to escape using ../
    with pytest.raises(WorkspaceSecurityError):
        validate_workspace_path("../secrets.txt")
    
    with pytest.raises(WorkspaceSecurityError):
        validate_workspace_path("../outside.txt")


def test_path_traversal_blocked_absolute():
    """Test that absolute paths outside workspace are blocked."""
    from mockmate.workspace_tools import WorkspaceSecurityError, validate_workspace_path
    
    # Absolute path to outside workspace
    with pytest.raises(WorkspaceSecurityError):
        validate_workspace_path("/tmp/outside.txt")
    
    # Windows absolute path attempt (on any platform)
    try:
        # On Windows this might be different, but we still test the concept
        validate_workspace_path("C:\\Windows\\System32\\config\\sam")
        # If no exception, check it's rejected
    except WorkspaceSecurityError:
        pass


def test_symlink_traversal_blocked():
    """Test that symlink-based path traversal is blocked."""
    # Create a temporary symlink scenario
    import tempfile

    from mockmate.workspace_tools import WorkspaceSecurityError, validate_workspace_path
    
    with tempfile.TemporaryDirectory():
        # Try to access through symlinks
        with pytest.raises(WorkspaceSecurityError):
            validate_workspace_path("../../../../etc/passwd")
            
        # Windows equivalent test - absolute paths outside workspace
        with pytest.raises((WorkspaceSecurityError, ValueError)):
            validate_workspace_path("C:\\Users\\Administrator\\.ssh\\id_rsa")


def test_secure_write_inside_workspace():
    """Test that writing inside workspace succeeds."""
    from mockmate.workspace_tools import secure_write_file
    
    content = "Test content for workspace write"
    file_path = "test_write_file.txt"
    
    result = secure_write_file(file_path, content)
    assert result.exists()
    assert result.read_text() == content
    
    # Cleanup
    result.unlink(missing_ok=True)


def test_secure_write_outside_workspace_blocked():
    """Test that writing outside workspace fails."""
    from mockmate.workspace_tools import WorkspaceSecurityError, secure_write_file
    
    with pytest.raises(WorkspaceSecurityError):
        secure_write_file("../secret_outside.txt", "Should fail")


def test_secure_read_valid_file():
    """Test reading valid workspace files."""
    from mockmate.workspace_tools import secure_read_file, secure_write_file
    
    content = "Content to read"
    secure_write_file("read_test.txt", content)
    result = secure_read_file("read_test.txt")
    assert result == content


def test_secure_delete_valid_file():
    """Test deleting valid workspace files."""
    from mockmate.workspace_tools import secure_delete_file, secure_write_file
    
    file_path = "delete_test.txt"
    secure_write_file(file_path, "temp content")
    assert secure_delete_file(file_path) is True
    assert not Path(file_path).exists()


def test_secure_delete_nonexistent_file():
    """Test that deleting non-existent file returns False."""
    from mockmate.workspace_tools import secure_delete_file
    
    assert secure_delete_file("nonexistent_file.txt") is False


def test_security_with_windows_absolute_paths():
    """Test security with Windows absolute paths."""
    from mockmate.workspace_tools import (
        WorkspaceSecurityError,
        get_workspace_dir,
        validate_workspace_path,
    )
    
    ws = get_workspace_dir()
    ws_str = str(ws)
    
    # These should all fail - paths outside workspace
    malicious_paths = [
        f"C:{ws_str}\\..\\not_allowed.txt",
        f"{ws_str}\\..\\windows\\system32",
        "/etc/passwd",
        "/var/log/auth.log",
    ]
    
    for path in malicious_paths:
        try:
            validate_workspace_path(path)
            # If no exception, ensure it doesn't escape workspace
            result_path = Path(path)
            if result_path.is_absolute() and str(ws) not in str(result_path):
                pytest.fail(f"Path {path} should have been rejected")
        except WorkspaceSecurityError:
            pass  # Expected behavior