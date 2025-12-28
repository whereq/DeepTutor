"""
Custom Log Handlers
===================

Handlers for streaming logs to WebSocket, file, etc.
"""

import asyncio
from datetime import datetime
import json
import logging


class WebSocketLogHandler(logging.Handler):
    """
    A logging handler that streams log records to a WebSocket via asyncio Queue.

    Usage:
        queue = asyncio.Queue()
        handler = WebSocketLogHandler(queue)
        logger.addHandler(handler)

        # In WebSocket endpoint:
        while True:
            log_entry = await queue.get()
            await websocket.send_json(log_entry)
    """

    # Symbols for different log types (matching ConsoleFormatter)
    SYMBOLS = {
        "DEBUG": "·",
        "INFO": "○",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "CRITICAL": "✗",
    }

    def __init__(self, queue: asyncio.Queue, include_module: bool = True):
        """
        Initialize WebSocket log handler.

        Args:
            queue: asyncio.Queue to put log entries into
            include_module: Whether to include module name in output
        """
        super().__init__()
        self.queue = queue
        self.include_module = include_module
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord):
        """Emit a log record to the queue."""
        try:
            msg = self.format(record)

            # Get symbol
            display_level = getattr(record, "display_level", record.levelname)
            symbol = getattr(record, "symbol", self.SYMBOLS.get(display_level, "○"))

            # Get module name
            module_name = getattr(record, "module_name", record.name)

            # Build formatted content
            if self.include_module:
                content = f"[{module_name}] {symbol} {msg}"
            else:
                content = f"{symbol} {msg}"

            # Construct structured message
            log_entry = {
                "type": "log",
                "level": display_level,
                "module": module_name,
                "symbol": symbol,
                "content": content,
                "message": msg,
                "timestamp": record.created,
            }

            # Put into queue non-blocking
            try:
                self.queue.put_nowait(log_entry)
            except asyncio.QueueFull:
                pass  # Drop log if queue is full

        except Exception:
            self.handleError(record)


class LogInterceptor:
    """
    Context manager to temporarily attach a WebSocketLogHandler to a logger.

    Usage:
        queue = asyncio.Queue()
        logger = logging.getLogger("ai_tutor.Solver")

        with LogInterceptor(logger, queue):
            # All logs from this logger will be streamed to queue
            solver.solve(problem)
    """

    def __init__(self, logger: logging.Logger, queue: asyncio.Queue, include_module: bool = True):
        """
        Initialize log interceptor.

        Args:
            logger: Logger to intercept
            queue: Queue to stream logs to
            include_module: Whether to include module name in output
        """
        self.logger = logger
        self.handler = WebSocketLogHandler(queue, include_module)

    def __enter__(self):
        """Attach handler on context enter."""
        self.logger.addHandler(self.handler)
        return self.handler

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove handler on context exit."""
        self.logger.removeHandler(self.handler)


class JSONFileHandler(logging.Handler):
    """
    A logging handler that writes structured JSON logs to a file.
    Each line is a valid JSON object (JSONL format).

    Useful for:
    - LLM call logging
    - Structured analysis
    - Log parsing and analysis
    """

    def __init__(self, filepath: str, encoding: str = "utf-8"):
        """
        Initialize JSON file handler.

        Args:
            filepath: Path to log file
            encoding: File encoding
        """
        super().__init__()
        self.filepath = filepath
        self.encoding = encoding
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord):
        """Emit a log record as JSON."""
        try:
            # Build JSON entry
            entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "module": getattr(record, "module_name", record.name),
                "message": self.format(record),
            }

            # Add extra fields if present
            for key in ["symbol", "display_level", "tool_name", "elapsed_ms", "tokens"]:
                if hasattr(record, key):
                    entry[key] = getattr(record, key)

            # Write to file
            with open(self.filepath, "a", encoding=self.encoding) as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception:
            self.handleError(record)


def create_task_logger(
    task_id: str, module_name: str, log_dir: str, queue: asyncio.Queue | None = None
) -> logging.Logger:
    """
    Create a logger for a specific task with file and optional WebSocket output.

    Args:
        task_id: Unique task identifier
        module_name: Module name (e.g., "Solver", "Research")
        log_dir: Directory for log files
        queue: Optional asyncio.Queue for WebSocket streaming

    Returns:
        Configured logger
    """
    from pathlib import Path

    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(f"ai_tutor.{module_name}.{task_id}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    # File handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"{module_name}_{task_id}_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(file_handler)

    # WebSocket handler if queue provided
    if queue is not None:
        ws_handler = WebSocketLogHandler(queue)
        ws_handler.setLevel(logging.INFO)
        logger.addHandler(ws_handler)

    return logger
