"""Configuration module for MockMate - reads settings from .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_config():
    """Get configuration from environment variables."""
    return {
        "model_provider": os.getenv("MODEL_PROVIDER", "ollama"),
        "model_name": os.getenv("MODEL_NAME", "llama3.2"),
        "api_base": os.getenv("API_BASE", "http://localhost:11434"),
        "checkpoint_path": os.getenv("CHECKPOINT_PATH", "workspace/checkpoints"),
    }


def validate_config(config):
    """Validate that required config values are present."""
    errors = []
    if not config["model_provider"]:
        errors.append("MODEL_PROVIDER not set")
    if not config["model_name"]:
        errors.append("MODEL_NAME not set")
    return errors