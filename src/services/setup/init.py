#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
System Setup and Initialization
Combines user directory initialization and port configuration management.
"""

import json
import os
from pathlib import Path

from src.logging import get_logger
from src.services.path_service import get_path_service

# Initialize logger for setup operations
_setup_logger = None


def _get_setup_logger():
    """Get logger for setup operations"""
    global _setup_logger
    if _setup_logger is None:
        _setup_logger = get_logger("Setup")
    return _setup_logger


# ============================================================================
# User Directory Initialization
# ============================================================================


def init_user_directories(project_root: Path | None = None) -> None:
    """
    Initialize user data directories if they don't exist.

    Creates the following directory structure:
    data/user/
    ├── agent/                    # All Agent interaction history
    │   ├── solve/
    │   │   └── sessions.json
    │   ├── chat/
    │   │   └── sessions.json
    │   ├── question/
    │   ├── research/
    │   │   └── reports/
    │   ├── co-writer/
    │   │   ├── audio/
    │   │   └── tool_calls/
    │   ├── guide/
    │   ├── run_code_workspace/
    │   └── logs/
    │
    ├── workspace/
    │   ├── notebook/
    │   └── memory/               # Personalization memory storage
    │
    └── settings/
        └── interface.json

    Args:
        project_root: Project root directory (ignored, kept for API compatibility)
    """
    # Use PathService for all paths
    path_service = get_path_service()
    user_data_dir = path_service.user_data_dir

    # Check if user directory exists and is empty
    user_dir_exists = user_data_dir.exists()
    user_dir_empty = False
    if user_dir_exists:
        try:
            # Check if directory is empty (no files or subdirectories)
            user_dir_empty = not any(user_data_dir.iterdir())
        except (OSError, PermissionError) as e:
            # If we can't check directory contents, assume it's not empty
            logger = _get_setup_logger()
            logger.warning(f"Cannot check if user directory is empty: {e}")
            user_dir_empty = False

    if not user_dir_exists or user_dir_empty:
        logger = _get_setup_logger()
        logger.info("\n" + "=" * 80)
        logger.info("INITIALIZING USER DATA DIRECTORY")
        logger.info("=" * 80)

        if not user_dir_exists:
            logger.info(f"Creating user data directory: {user_data_dir}")
        else:
            logger.info(f"User data directory is empty, initializing: {user_data_dir}")

        # Create main user directory
        user_data_dir.mkdir(parents=True, exist_ok=True)

        # Create agent directories
        agent_modules = ["solve", "chat", "question", "research", "co-writer", "guide", "run_code_workspace", "logs"]
        for module in agent_modules:
            dir_path = path_service.get_agent_dir(module)
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.success(f"Created: agent/{module}/")

        # Create co-writer subdirectories
        co_writer_subdirs = ["audio", "tool_calls"]
        co_writer_dir = path_service.get_co_writer_dir()
        for subdir_name in co_writer_subdirs:
            subdir_path = co_writer_dir / subdir_name
            subdir_path.mkdir(parents=True, exist_ok=True)
            logger.success(f"Created: agent/co-writer/{subdir_name}/")

        # Create research subdirectories
        reports_dir = path_service.get_research_reports_dir()
        reports_dir.mkdir(parents=True, exist_ok=True)
        logger.success("Created: agent/research/reports/")

        # Create workspace/notebook directory
        notebook_dir = path_service.get_notebook_dir()
        notebook_dir.mkdir(parents=True, exist_ok=True)
        logger.success("Created: workspace/notebook/")

        # Create workspace/memory directory for personalization
        memory_dir = path_service.get_memory_dir()
        memory_dir.mkdir(parents=True, exist_ok=True)
        logger.success("Created: workspace/memory/")

        # Create settings directory and interface.json
        settings_dir = path_service.get_settings_dir()
        settings_dir.mkdir(parents=True, exist_ok=True)
        interface_file = path_service.get_settings_file("interface")
        if not interface_file.exists():
            initial_settings = {"theme": "light", "language": "en", "output_language": "en"}
            try:
                with open(interface_file, "w", encoding="utf-8") as f:
                    json.dump(initial_settings, f, indent=2, ensure_ascii=False)
                logger.success("Created: settings/interface.json")
            except Exception as e:
                logger.warning(f"Failed to create settings/interface.json: {e}")

        logger.info("=" * 80)
        logger.success("User data directory initialization complete!")
        logger.info("=" * 80 + "\n")
    else:
        # Directory exists and is not empty, just ensure all subdirectories exist
        _ensure_directories_exist(path_service)


def _ensure_directories_exist(path_service) -> None:
    """
    Ensure all required directories exist (silent mode for existing installations).
    """
    # Agent directories
    agent_modules = ["solve", "chat", "question", "research", "co-writer", "guide", "run_code_workspace", "logs"]
    for module in agent_modules:
        path_service.get_agent_dir(module).mkdir(parents=True, exist_ok=True)

    # Co-writer subdirectories
    path_service.get_co_writer_tool_calls_dir().mkdir(parents=True, exist_ok=True)
    path_service.get_co_writer_audio_dir().mkdir(parents=True, exist_ok=True)

    # Research reports directory
    path_service.get_research_reports_dir().mkdir(parents=True, exist_ok=True)

    # Workspace/notebook directory
    path_service.get_notebook_dir().mkdir(parents=True, exist_ok=True)

    # Workspace/memory directory for personalization
    path_service.get_memory_dir().mkdir(parents=True, exist_ok=True)

    # Settings directory and interface.json
    settings_dir = path_service.get_settings_dir()
    settings_dir.mkdir(parents=True, exist_ok=True)
    interface_file = path_service.get_settings_file("interface")
    if not interface_file.exists():
        initial_settings = {"theme": "light", "language": "en", "output_language": "en"}
        try:
            with open(interface_file, "w", encoding="utf-8") as f:
                json.dump(initial_settings, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silent fail if file creation fails but directory exists


# ============================================================================
# Port Configuration Management
# ============================================================================
# Ports are configured via environment variables in .env file:
#   BACKEND_PORT=8001   (default: 8001)
#   FRONTEND_PORT=3782  (default: 3782)
# ============================================================================


def get_backend_port(project_root: Path | None = None) -> int:
    """
    Get backend port from environment variable.

    Configure in .env file: BACKEND_PORT=8001

    Returns:
        Backend port number (default: 8001)
    """
    env_port = os.environ.get("BACKEND_PORT", "8001")
    try:
        return int(env_port)
    except ValueError:
        logger = _get_setup_logger()
        logger.warning(f"Invalid BACKEND_PORT: {env_port}, using default 8001")
        return 8001


def get_frontend_port(project_root: Path | None = None) -> int:
    """
    Get frontend port from environment variable.

    Configure in .env file: FRONTEND_PORT=3782

    Returns:
        Frontend port number (default: 3782)
    """
    env_port = os.environ.get("FRONTEND_PORT", "3782")
    try:
        return int(env_port)
    except ValueError:
        logger = _get_setup_logger()
        logger.warning(f"Invalid FRONTEND_PORT: {env_port}, using default 3782")
        return 3782


def get_ports(project_root: Path | None = None) -> tuple[int, int]:
    """
    Get both backend and frontend ports from configuration.

    Args:
        project_root: Project root directory (if None, will try to detect)

    Returns:
        Tuple of (backend_port, frontend_port)

    Raises:
        SystemExit: If ports are not configured
    """
    backend_port = get_backend_port(project_root)
    frontend_port = get_frontend_port(project_root)
    return (backend_port, frontend_port)


__all__ = [
    # User directory initialization
    "init_user_directories",
    # Port configuration (from .env)
    "get_backend_port",
    "get_frontend_port",
    "get_ports",
]
