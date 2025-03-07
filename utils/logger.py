import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logger():
    """Set up the logger with file and console handlers."""
    logger = logging.getLogger("AgenticAI")
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    log_file = logs_dir / f"agentic_ai_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = setup_logger()

def log_action(action: str, details: str = ""):
    """Log an action with optional details."""
    logger.info(f"Action: {action}")
    if details:
        logger.debug(f"Details: {details}")

def log_error(error: Exception, context: str = ""):
    """Log an error with optional context."""
    logger.error(f"Error: {str(error)}")
    if context:
        logger.error(f"Context: {context}")
    logger.exception("Stack trace:")

def log_debug(message: str):
    """Log a debug message."""
    logger.debug(message)

def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)

def log_info(message: str):
    """Log an info message."""
    logger.info(message) 