import sys
import os
from datetime import datetime
from loguru import logger
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure loguru logger
def setup_logger():
    """Configure the logger with file and console handlers."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )
    
    # Add file handler for history
    logger.add(
        "logs/history.log",
        rotation="1 GB",
        retention="90 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO"
    )
    
    logger.info("Logger initialized")

def log_action(action: str, details: str = ""):
    """Log a user action with details."""
    logger.info(f"Action: {action} | Details: {details}")

def log_error(error: Exception, context: str = ""):
    """Log an error with context."""
    logger.error(f"Error: {str(error)} | Context: {context}")

def log_debug(message: str, context: str = ""):
    """Log a debug message with context."""
    logger.debug(f"Debug: {message} | Context: {context}")

# Initialize logger when module is imported
setup_logger() 