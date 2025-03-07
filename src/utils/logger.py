"""
Logging utility for Agentic AI
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, List
from pathlib import Path

def setup_logger(
    log_file: str = "logs/agentic_ai.log",
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_level: str = "INFO",
    log_types: Optional[List[str]] = None
) -> logging.Logger:
    """Setup application logger"""
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("agentic_ai")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create handlers
    handlers = []
    
    # File handler
    if log_types is None or "error" in log_types or "info" in log_types:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
        
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # Add handlers to logger
    for handler in handlers:
        logger.addHandler(handler)
        
    return logger

def log_action(logger: logging.Logger, action: str, details: str) -> None:
    """Log an action with details"""
    logger.info(f"{action}: {details}")

def log_error(logger: logging.Logger, error: Exception, context: str) -> None:
    """Log an error with context"""
    logger.error(f"{context}: {str(error)}", exc_info=True)

def log_warning(logger: logging.Logger, warning: str, context: str) -> None:
    """Log a warning with context"""
    logger.warning(f"{context}: {warning}")

def log_debug(logger: logging.Logger, message: str, context: str) -> None:
    """Log a debug message with context"""
    logger.debug(f"{context}: {message}") 