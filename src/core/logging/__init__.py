"""
Unified Logging System for OpenTutor
=====================================

A clean, consistent logging system with:
- Unified format: [Module] Symbol Message
- English-only output
- File output to ../user/logs/
- WebSocket streaming support
- Color-coded console output

Usage:
    from src.core.logging import get_logger

    logger = get_logger("Solver")
    logger.info("Processing started")
    logger.success("Task completed in 2.3s")
    logger.error("Something went wrong")
"""

from .handlers import (
    LogInterceptor,
    WebSocketLogHandler,
)
from .lightrag_forward import (
    LightRAGLogContext,
)
from .llm_stats import (
    LLMStats,
)
from .logger import (
    Logger,
    LogLevel,
    get_logger,
    reset_logger,
)

__all__ = [
    "LLMStats",
    "LightRAGLogContext",
    "LogInterceptor",
    "LogLevel",
    "Logger",
    "WebSocketLogHandler",
    "get_logger",
    "reset_logger",
]
