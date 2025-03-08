"""
Conversation Manager Core Module for Agentic AI

This module integrates the conversation history logging system with the
core AI functionality, providing memory and context for AI interactions.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
import json

# Import conversation logger
from src.utils.conversation_logger import (
    ConversationLogger, ConversationEntry, Conversation,
    create_conversation, add_entry, get_conversation,
    list_conversations, search_conversations, get_conversations_by_date,
    summary_for_days_ago, export_conversation, delete_conversation
)

# Get logger
logger = logging.getLogger("agentic_ai.core.conversation_manager")


class ConversationManager:
    """
    Manager for AI conversations with memory capabilities
    
    This class integrates the conversation logging system with the core AI,
    allowing it to maintain context, recall past conversations, and provide
    a more coherent user experience.
    """
    
    def __init__(self, db_path: str = "logs/conversations.db"):
        """
        Initialize conversation manager
        
        Args:
            db_path: Path to SQLite database for conversations
        """
        logger.info("Initializing conversation manager")
        
        # Create conversation logger
        self.logger = ConversationLogger(db_path=db_path)
        
        # Current conversation details
        self.current_conversation_id = None
        self.conversation_title = "Untitled Conversation"
        
        # Context window for AI (number of recent messages to include)
        self.context_window = 10
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def start_conversation(self, title: Optional[str] = None) -> str:
        """
        Start a new conversation
        
        Args:
            title: Title of the conversation (auto-generated if None)
            
        Returns:
            str: Conversation ID
        """
        # Generate title if not provided
        if title is None:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self.conversation_title = title
        
        # Create conversation
        self.current_conversation_id = self.logger.create_conversation(
            title=title,
            metadata={"start_time": datetime.now().isoformat()}
        )
        
        logger.info(f"Started new conversation: {title} (ID: {self.current_conversation_id})")
        return self.current_conversation_id
    
    def add_user_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a user message to the current conversation
        
        Args:
            message: User message content
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        # Start a new conversation if none is active
        if self.current_conversation_id is None:
            self.start_conversation()
            
        # At this point self.current_conversation_id must be a valid string
        if not self.current_conversation_id:
            logger.error("Failed to create a new conversation ID")
            return False
        
        # Add entry to conversation
        success = self.logger.add_entry(
            conversation_id=self.current_conversation_id,
            role="user",
            content=message,
            metadata=metadata
        )
        
        logger.info(f"Added user message to conversation: {self.current_conversation_id}")
        return success
    
    def add_assistant_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an assistant message to the current conversation
        
        Args:
            message: Assistant message content
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        # Start a new conversation if none is active
        if self.current_conversation_id is None:
            self.start_conversation()
            
        # At this point self.current_conversation_id must be a valid string
        if not self.current_conversation_id:
            logger.error("Failed to create a new conversation ID")
            return False
        
        # Add entry to conversation
        success = self.logger.add_entry(
            conversation_id=self.current_conversation_id,
            role="assistant",
            content=message,
            metadata=metadata
        )
        
        logger.info(f"Added assistant message to conversation: {self.current_conversation_id}")
        return success
    
    def get_conversation_history(self, conversation_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get the full history of a conversation
        
        Args:
            conversation_id: Conversation ID (current conversation if None)
            
        Returns:
            List of messages or None if conversation not found
        """
        # Use current conversation if none specified
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        # Check if conversation exists
        if conversation_id is None:
            logger.warning("No active conversation")
            return None
        
        # Get conversation
        conversation = self.logger.get_conversation(conversation_id)
        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            return None
        
        # Convert to list of messages
        messages = []
        for entry in conversation.entries:
            messages.append({
                "role": entry.role,
                "content": entry.content,
                "timestamp": entry.timestamp.isoformat(),
                "metadata": entry.metadata
            })
        
        return messages
    
    def get_recent_context(self, conversation_id: Optional[str] = None, window_size: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get recent conversation context for AI input
        
        Args:
            conversation_id: Conversation ID (current conversation if None)
            window_size: Number of recent messages to include (default: self.context_window)
            
        Returns:
            List of messages in format suitable for AI context
        """
        # Use current conversation if none specified
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        # Use default window size if none specified
        if window_size is None:
            window_size = self.context_window
        
        # Check if conversation exists
        if conversation_id is None:
            logger.warning("No active conversation")
            return []
        
        # Get conversation
        conversation = self.logger.get_conversation(conversation_id)
        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            return []
        
        # Get recent messages
        entries = conversation.entries[-window_size:] if len(conversation.entries) > window_size else conversation.entries
        
        # Convert to AI context format
        context = []
        for entry in entries:
            context.append({
                "role": entry.role,
                "content": entry.content
            })
        
        return context
    
    def search_message_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for messages containing specific content
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages with conversation context
        """
        # Search conversations
        conversations = self.logger.search_conversations(query, limit)
        
        results = []
        for conv_summary in conversations:
            # Get full conversation
            conversation = self.logger.get_conversation(conv_summary["conversation_id"])
            if conversation:
                # Find matching entries
                for i, entry in enumerate(conversation.entries):
                    if query.lower() in entry.content.lower():
                        # Get context (previous and next message if available)
                        context = []
                        if i > 0:
                            context.append({
                                "role": conversation.entries[i-1].role,
                                "content": conversation.entries[i-1].content
                            })
                        
                        context.append({
                            "role": entry.role,
                            "content": entry.content
                        })
                        
                        if i < len(conversation.entries) - 1:
                            context.append({
                                "role": conversation.entries[i+1].role,
                                "content": conversation.entries[i+1].content
                            })
                        
                        # Add to results
                        results.append({
                            "conversation_id": conversation.conversation_id,
                            "title": conversation.title,
                            "timestamp": entry.timestamp.isoformat(),
                            "matching_message": {
                                "role": entry.role,
                                "content": entry.content
                            },
                            "context": context
                        })
        
        return results
    
    def find_conversations_by_date(self, days_ago: int) -> Dict[str, Any]:
        """
        Find conversations from a specific number of days ago
        
        Args:
            days_ago: Number of days in the past
            
        Returns:
            Dict with conversation summaries or None if not found
        """
        return self.logger.summary_for_days_ago(days_ago)
    
    def get_conversations_from_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Get conversations from a specific date
        
        Args:
            date_str: Date string in format 'YYYY-MM-DD'
            
        Returns:
            List of conversation summaries
        """
        try:
            # Parse date
            date_obj = datetime.fromisoformat(date_str)
            return self.logger.get_conversations_by_date(date_obj)
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return []
    
    def get_recent_conversations(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations
        
        Args:
            days: Number of days to look back
            limit: Maximum number of conversations
            
        Returns:
            List of conversation summaries
        """
        return self.logger.list_conversations(days=days, limit=limit)
    
    def summarize_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Generate a summary of a conversation
        
        Args:
            conversation_id: Conversation ID (current conversation if None)
            
        Returns:
            Summary text
        """
        # Use current conversation if none specified
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        # Check if conversation exists
        if conversation_id is None:
            logger.warning("No active conversation")
            return "No active conversation"
        
        # Get conversation
        conversation = self.logger.get_conversation(conversation_id)
        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            return f"Conversation not found: {conversation_id}"
        
        # Generate summary
        # This is a simple implementation - a real one would use an AI model
        messages_count = len(conversation.entries)
        user_messages = sum(1 for entry in conversation.entries if entry.role == "user")
        assistant_messages = sum(1 for entry in conversation.entries if entry.role == "assistant")
        duration_mins = 0
        
        if conversation.end_time and conversation.start_time:
            duration = conversation.end_time - conversation.start_time
            duration_mins = duration.total_seconds() / 60
        
        # Get first few messages for context
        first_messages = [entry.content[:100] + "..." for entry in conversation.entries[:2]]
        
        summary = f"Conversation: {conversation.title}\n"
        summary += f"Date: {conversation.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"Duration: {duration_mins:.1f} minutes\n"
        summary += f"Messages: {messages_count} total ({user_messages} user, {assistant_messages} assistant)\n\n"
        summary += "Beginning of conversation:\n"
        for i, msg in enumerate(first_messages):
            role = "User" if conversation.entries[i].role == "user" else "Assistant"
            summary += f"{role}: {msg}\n"
        
        return summary
    
    def export_conversation_to_file(self, 
                                   conversation_id: Optional[str] = None,
                                   output_file: Optional[str] = None,
                                   format: str = "json") -> bool:
        """
        Export a conversation to a file
        
        Args:
            conversation_id: Conversation ID (current conversation if None)
            output_file: Output file path (auto-generated if None)
            format: Export format (json, text, markdown)
            
        Returns:
            bool: Success status
        """
        # Use current conversation if none specified
        if conversation_id is None:
            conversation_id = self.current_conversation_id
        
        # Check if conversation exists
        if conversation_id is None:
            logger.warning("No active conversation")
            return False
        
        # Get conversation
        conversation = self.logger.get_conversation(conversation_id)
        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            return False
        
        # Generate output file path if not specified
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_slug = "".join(c if c.isalnum() else "_" for c in conversation.title)
            output_file = f"exports/conversation_{title_slug}_{timestamp}.{format}"
            os.makedirs("exports", exist_ok=True)
        
        # Export conversation
        content = self.logger.export_conversation(conversation_id, format)
        if content is None:
            logger.error(f"Failed to export conversation: {conversation_id}")
            return False
        
        # Write to file
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Exported conversation to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return False


# Create a default instance for easy import
default_conversation_manager = ConversationManager()


# Helper functions for easy use
def start_conversation(title: Optional[str] = None) -> str:
    """Start a new conversation"""
    return default_conversation_manager.start_conversation(title)

def add_user_message(message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Add a user message to the current conversation"""
    return default_conversation_manager.add_user_message(message, metadata)

def add_assistant_message(message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Add an assistant message to the current conversation"""
    return default_conversation_manager.add_assistant_message(message, metadata)

def get_conversation_history(conversation_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Get the full history of a conversation"""
    return default_conversation_manager.get_conversation_history(conversation_id)

def get_recent_context(conversation_id: Optional[str] = None, window_size: Optional[int] = None) -> List[Dict[str, str]]:
    """Get recent conversation context for AI input"""
    return default_conversation_manager.get_recent_context(conversation_id, window_size)

def search_message_content(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for messages containing specific content"""
    return default_conversation_manager.search_message_content(query, limit)

def find_conversations_by_date(days_ago: int) -> Dict[str, Any]:
    """Find conversations from a specific number of days ago"""
    return default_conversation_manager.find_conversations_by_date(days_ago)

def get_conversations_from_date(date_str: str) -> List[Dict[str, Any]]:
    """Get conversations from a specific date"""
    return default_conversation_manager.get_conversations_from_date(date_str)

def get_recent_conversations(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent conversations"""
    return default_conversation_manager.get_recent_conversations(days, limit)

def summarize_conversation(conversation_id: Optional[str] = None) -> str:
    """Generate a summary of a conversation"""
    return default_conversation_manager.summarize_conversation(conversation_id)

def export_conversation_to_file(conversation_id: Optional[str] = None,
                              output_file: Optional[str] = None,
                              format: str = "json") -> bool:
    """Export a conversation to a file"""
    return default_conversation_manager.export_conversation_to_file(conversation_id, output_file, format) 