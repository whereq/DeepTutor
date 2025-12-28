"""
Log Forwarder - Forward logs from question generation and problem solving to unified system log file
"""

from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class SystemLogForwarder(logging.Handler):
    """
    Forward logs to unified system log file
    Used for question generation and problem solving modules, keeping their own logging systems while also writing to unified log
    """

    _system_logger: logging.Logger | None = None
    _initialized = False

    @classmethod
    def get_system_logger(cls) -> logging.Logger:
        """Get unified system logger"""
        if cls._system_logger is None:
            # Get log directory from config (same logic as logger.py)
            try:
                from src.core.core import get_path_from_config, load_config_with_main

                # Use resolve() to get absolute path, ensuring correct project root regardless of working directory
                project_root = Path(__file__).resolve().parent.parent.parent.parent
                config = load_config_with_main("solve_config.yaml", project_root)
                log_dir = get_path_from_config(config, "user_log_dir") or config.get(
                    "paths", {}
                ).get("user_log_dir")
                if log_dir:
                    # Convert relative path to absolute based on project root
                    log_dir_path = Path(log_dir)
                    if not log_dir_path.is_absolute():
                        # Remove leading ./ if present
                        log_dir_str = str(log_dir_path).lstrip("./")
                        log_dir = project_root / log_dir_str
                    else:
                        log_dir = log_dir_path
                else:
                    # Fallback to default: data/user/logs
                    log_dir = project_root / "data" / "user" / "logs"
            except Exception:
                # Fallback to default: data/user/logs
                # Use resolve() to get absolute path
                project_root = Path(__file__).resolve().parent.parent.parent.parent
                log_dir = project_root / "data" / "user" / "logs"

            # Ensure log directory exists
            log_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime("%Y%m%d")
            log_file = log_dir / f"ai_tutor_system_{today}.log"

            # Create system logger
            cls._system_logger = logging.getLogger("ai_tutor.system")
            cls._system_logger.setLevel(logging.DEBUG)

            # Only add file handler, don't add console handler (avoid duplicate output)
            if not cls._system_logger.handlers:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding="utf-8",  # 10MB
                )
                file_handler.setLevel(logging.DEBUG)

                # Custom formatter supporting module_name field
                class SystemLogFormatter(logging.Formatter):
                    def format(self, record):
                        # If no module_name, use default value
                        if not hasattr(record, "module_name"):
                            record.module_name = "system"
                        return super().format(record)

                file_format = SystemLogFormatter(
                    "%(asctime)s | [%(module_name)s] | %(levelname)-8s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                file_handler.setFormatter(file_format)
                cls._system_logger.addHandler(file_handler)

            cls._initialized = True

        return cls._system_logger

    def __init__(self, module_name: str):
        """
        Initialize log forwarder

        Args:
            module_name: Module name (e.g., 'question', 'solve')
        """
        super().__init__()
        self.module_name = module_name
        self.setLevel(logging.DEBUG)

    def emit(self, record: logging.LogRecord):
        """Forward log to unified system log file"""
        try:
            # Get system logger
            system_logger = self.get_system_logger()

            # Add module name to record
            record.module_name = self.module_name

            # Forward log (using same level)
            system_logger.handle(record)
        except Exception:
            # Forward failure should not affect original log
            self.handleError(record)


def attach_system_log_forwarder(logger: logging.Logger, module_name: str):
    """
    Attach system log forwarder to specified logger

    Args:
        logger: Logger to attach forwarder to
        module_name: Module name (e.g., 'question', 'solve')
    """
    # Check if already attached
    for handler in logger.handlers:
        if isinstance(handler, SystemLogForwarder) and handler.module_name == module_name:
            return  # Already attached

    # Add forwarder
    forwarder = SystemLogForwarder(module_name)
    logger.addHandler(forwarder)
