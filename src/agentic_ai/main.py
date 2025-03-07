"""Main entry point for the Agentic AI application."""

import sys
import os
import logging
from typing import Optional

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now we can import from the project root
from src.agentic_ai.gui import main as gui_main
from src.agentic_ai.cli import main as cli_main
from src.utils.logger import setup_logger

def main(argv: Optional[list[str]] = None) -> int:
    """Run the Agentic AI application.
    
    Args:
        argv: Command line arguments. If None, sys.argv is used.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Set up logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Parse command line arguments
        args = argv if argv is not None else sys.argv[1:]
        
        # Determine whether to run GUI or CLI
        if "--gui" in args or "-g" in args:
            logger.info("Starting Agentic AI GUI")
            return gui_main(args)
        else:
            logger.info("Starting Agentic AI CLI")
            return cli_main(args)
            
    except Exception as e:
        logger.error(f"Error running Agentic AI: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 