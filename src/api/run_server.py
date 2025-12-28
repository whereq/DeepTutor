#!/usr/bin/env python
"""
Uvicorn Server Startup Script
Uses Python API instead of command line to avoid Windows path parsing issues.
"""

import os
import sys

# Force unbuffered output
os.environ["PYTHONUNBUFFERED"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

from pathlib import Path

import uvicorn

if __name__ == "__main__":
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent

    # Change to project root to ensure correct module imports
    os.chdir(str(project_root))

    # Ensure project root is in Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Get port from configuration
    from src.core.setup import get_backend_port

    backend_port = get_backend_port(project_root)

    # Configure reload_excludes to skip temporary files and output directories
    reload_excludes = [
        "**/run_code_workspace/**",  # Code execution workspace
        "**/tmp*/**",  # All temp directories
        "**/__pycache__/**",  # Python cache
        "**/*.pyc",  # Python compiled files
        "**/user/solve/**",  # Solve output directory
        "**/user/question/**",  # Question output directory
        "**/user/research/**",  # Research output directory
        "**/user/co-writer/**",  # Co-Writer output directory
        "**/logs/**",  # Logs directory
        "**/user/logs/**",  # User logs directory
    ]

    # Start uvicorn server with reload enabled
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=backend_port,
        reload=True,
        reload_excludes=reload_excludes,
        log_level="info",
    )
