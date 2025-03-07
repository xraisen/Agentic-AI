#!/usr/bin/env python3
"""
Agentic AI - Main Application Entry Point
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add src directory to Python path
src_dir = Path(__file__).resolve().parent
sys.path.append(str(src_dir))

from utils.logger import setup_logger
from config import load_config
from ui.main_window import MainWindow
from api.client import APIClient

class AgenticAI:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        self.config = load_config()
        self.logger = setup_logger()
        self.api_client = APIClient(self.config)
        self.main_window = None
        
    def initialize(self) -> bool:
        """Initialize application components"""
        try:
            self.logger.info("Initializing Agentic AI...")
            
            # Create necessary directories
            self._create_directories()
            
            # Initialize API client
            if not self.api_client.initialize():
                self.logger.error("Failed to initialize API client")
                return False
                
            # Initialize UI
            self.main_window = MainWindow(self.config, self.api_client)
            if not self.main_window.initialize():
                self.logger.error("Failed to initialize main window")
                return False
                
            self.logger.info("Initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            return False
            
    def _create_directories(self) -> None:
        """Create necessary application directories"""
        directories = [
            self.config.get('cache_dir', 'cache'),
            self.config.get('assets_dir', 'assets'),
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def run(self) -> int:
        """Run the application"""
        try:
            if not self.initialize():
                return 1
                
            self.logger.info("Starting Agentic AI...")
            return self.main_window.run()
            
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            return 1
            
def main() -> int:
    """Main entry point"""
    app = AgenticAI()
    return app.run()

if __name__ == "__main__":
    sys.exit(main()) 