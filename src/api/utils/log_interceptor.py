"""
Log Interceptor for WebSocket streaming
=======================================

Re-exports handlers from the unified logging system.
Kept for backwards compatibility.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Re-export from unified logging system
from src.core.logging.handlers import (
    JSONFileHandler,
    LogInterceptor,
    WebSocketLogHandler,
    create_task_logger,
)

__all__ = [
    "WebSocketLogHandler",
    "LogInterceptor",
    "JSONFileHandler",
    "create_task_logger",
]
