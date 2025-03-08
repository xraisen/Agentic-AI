"""
Agentic Core Module for Agentic AI

This module integrates all components (file operations, system operations,
and conversation management) with the core AI system, providing a unified interface
for the application.
"""

import os
import logging
import json
from typing import Optional, Dict, List, Any, Union, Tuple
from pathlib import Path
import traceback
from datetime import datetime
import asyncio

# Import core components
from src.core.file_operations import FileOperationManager
from src.core.system_operations import SystemOperationManager
from src.core.conversation_manager import ConversationManager

# Modified import for AI engine
try:
    from src.core.ai_engine import AIEngine
    has_ai_engine = True
except ImportError:
    has_ai_engine = False
    logger = logging.getLogger("agentic_ai.core")
    logger.warning("AI Engine module not found. AI functionality will be disabled.")

# Get logger
logger = logging.getLogger("agentic_ai.core")


class AgenticCore:
    """
    Core integration class for Agentic AI
    
    This class integrates all components (file operations, system operations,
    and conversation management) with the core AI system, providing a unified
    interface for the application.
    """
    
    def __init__(self, config_path: str = "config.json", workspace_path: Optional[str] = None):
        """
        Initialize Agentic Core
        
        Args:
            config_path: Path to configuration file
            workspace_path: Path to workspace directory (defaults to current directory)
        """
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        logger.info(f"Initializing Agentic Core with workspace: {self.workspace_path}")
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.config_path = config_path
        
        # Create directories
        self._setup_directories()
        
        # Initialize components
        self.file_manager = FileOperationManager(workspace_path=self.workspace_path)
        self.system_manager = SystemOperationManager(workspace_path=self.workspace_path)
        self.conversation_manager = ConversationManager(db_path="logs/conversations.db")
        
        # Initialize AI engine (if module exists)
        self.ai_engine = None
        if has_ai_engine:
            try:
                self.ai_engine = AIEngine(config_path=self.config_path)
                logger.info("AI Engine initialized successfully")
            except Exception as e:
                logger.error(f"AI Engine initialization failed: {str(e)}")
        else:
            logger.error("AI Engine module not found. AI functionality will be disabled.")
    
    def _load_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary or None if loading failed
        """
        try:
            # Check if config file exists
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return None
            
            # Read configuration
            with open(config_path, "r") as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in configuration file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
    
    def _setup_directories(self) -> None:
        """Create necessary directories"""
        directories = ["logs", "cache", "config", "exports", "temp"]
        for directory in directories:
            path = self.workspace_path / directory
            path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {path}")
    
    async def _get_ai_response_async(self, user_input: str) -> str:
        """
        Get response from AI engine asynchronously
        
        Args:
            user_input: User input text
            
        Returns:
            AI response text
        """
        if not self.ai_engine:
            return "AI Engine is not initialized. Please check your configuration."
        
        try:
            return await self.ai_engine.get_response(user_input)
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}"
    
    def process_user_request(self, user_input: str) -> str:
        """
        Process a user request and generate a response
        
        Args:
            user_input: User input text
            
        Returns:
            AI response text
        """
        try:
            # Log user input
            logger.info(f"Processing user request: {user_input[:50]}...")
            
            # Add user message to conversation history
            self.conversation_manager.add_user_message(user_input)
            
            # Get AI response
            if not self.ai_engine:
                response = "AI Engine is not initialized. Please check your configuration."
            else:
                # Using asyncio to call the async method
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self._get_ai_response_async(user_input))
            
            # Add assistant message to conversation history
            self.conversation_manager.add_assistant_message(response)
            
            return response
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return f"Error: {str(e)}"
    
    def execute_file_operation(self, operation: str, *args, **kwargs) -> Any:
        """
        Execute a file operation
        
        Args:
            operation: Operation name
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Check if operation exists
            if not hasattr(self.file_manager, operation):
                logger.error(f"Unknown file operation: {operation}")
                return None
            
            # Get operation method
            method = getattr(self.file_manager, operation)
            
            # Execute operation
            logger.info(f"Executing file operation: {operation}")
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = f"Error executing file operation {operation}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return None
    
    def execute_system_operation(self, operation: str, *args, **kwargs) -> Any:
        """
        Execute a system operation
        
        Args:
            operation: Operation name
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Check if operation exists
            if not hasattr(self.system_manager, operation):
                logger.error(f"Unknown system operation: {operation}")
                return None
            
            # Get operation method
            method = getattr(self.system_manager, operation)
            
            # Execute operation
            logger.info(f"Executing system operation: {operation}")
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = f"Error executing system operation {operation}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return None
    
    def get_conversation_history(self, days_ago: Optional[int] = None, conversation_id: Optional[str] = None) -> Optional[Any]:
        """
        Get conversation history
        
        Args:
            days_ago: Number of days ago (to get conversations from a specific day)
            conversation_id: Specific conversation ID (to get a single conversation)
            
        Returns:
            Conversation history
        """
        try:
            if days_ago is not None:
                return self.conversation_manager.find_conversations_by_date(days_ago)
            elif conversation_id is not None:
                return self.conversation_manager.get_conversation_history(conversation_id)
            else:
                return self.conversation_manager.get_recent_conversations()
        except Exception as e:
            error_msg = f"Error retrieving conversation history: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return None
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a system command
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            return self.system_manager.execute_command(command)
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return 1, "", str(e)
    
    def shutdown(self) -> None:
        """Perform cleanup and shutdown operations"""
        logger.info("Shutting down Agentic Core")
        # Any cleanup operations go here


# Create a default instance for easy import
default_core = AgenticCore()


# Helper functions for easy use
def process_user_request(user_input: str) -> str:
    """Process a user request and generate a response"""
    return default_core.process_user_request(user_input)

def execute_file_operation(operation: str, *args, **kwargs) -> Any:
    """Execute a file operation"""
    return default_core.execute_file_operation(operation, *args, **kwargs)

def execute_system_operation(operation: str, *args, **kwargs) -> Any:
    """Execute a system operation"""
    return default_core.execute_system_operation(operation, *args, **kwargs)

def get_conversation_history(days_ago: Optional[int] = None, conversation_id: Optional[str] = None) -> Optional[Any]:
    """Get conversation history"""
    return default_core.get_conversation_history(days_ago, conversation_id)

def execute_command(command: str) -> Tuple[int, str, str]:
    """Execute a system command"""
    return default_core.execute_command(command) 