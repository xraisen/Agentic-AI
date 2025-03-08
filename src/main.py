#!/usr/bin/env python3
"""
Agentic AI - Main Application Entry Point
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Add the project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Ensure logs directory exists
logs_dir = os.path.join(ROOT_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(ROOT_DIR, "logs", "agentic_ai.log")),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)

def wait_on_error():
    """Wait for user input before closing the console window on error"""
    if sys.stdout and sys.stdin and sys.stderr and all(hasattr(f, 'isatty') and f.isatty() for f in [sys.stdout, sys.stdin, sys.stderr]):
        print("\nPress Enter to exit...")
        input()

def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting Agentic AI application")
        
        # Import here to avoid circular imports
        from src.agentic_ai.main import main as app_main
        
        # Run the application
        return app_main(sys.argv[1:])
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: {e}")
        print("This could be due to missing dependencies. Try running 'pip install -r requirements.txt'")
        wait_on_error()
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}")
        traceback.print_exc()
        wait_on_error()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 