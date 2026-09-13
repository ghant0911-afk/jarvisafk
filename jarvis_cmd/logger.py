import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "jarvis",
    log_dir: Optional[str] = None,
    level: Optional[int] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
) -> logging.Logger:
    """
    Setup logger with file rotation and console output.

    Args:
        name: Logger name
        log_dir: Directory for log files (from config if None)
        level: Logging level (from config if None)
        max_bytes: Max size of log file before rotation (from config if None)
        backup_count: Number of backup files to keep (from config if None)

    Returns:
        Configured logger instance
    """
    # Import here to avoid circular dependency
    try:
        from jarvis_cmd.config import get_config
        config = get_config()
        log_config = config.get_logging_config()
    except Exception:
        log_config = {
            "log_dir": "data/logs",
            "level": "INFO",
            "max_file_size_mb": 10,
            "backup_count": 5,
        }

    log_dir = log_dir or log_config.get("log_dir", "data/logs")
    level = level or getattr(logging, log_config.get("level", "INFO"))
    max_bytes = max_bytes or (log_config.get("max_file_size_mb", 10) * 1024 * 1024)
    backup_count = backup_count or log_config.get("backup_count", 5)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path / "jarvis.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler
    error_handler = RotatingFileHandler(
        log_path / "errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger


# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
