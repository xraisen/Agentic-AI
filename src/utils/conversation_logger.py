"""
Conversation History Logger System for Agentic AI

This module provides functionality to log, store, and retrieve conversation
history between the user and the AI assistant.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import sqlite3
import threading

# Get logger
logger = logging.getLogger("agentic_ai")


class ConversationEntry:
    """Class to represent a conversation entry"""
    
    def __init__(self, 
                 role: str,
                 content: str,
                 timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize conversation entry
        
        Args:
            role: Role of the speaker (user, assistant)
            content: Content of the message
            timestamp: When the message was sent
            metadata: Additional metadata
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp else datetime.now()
        self.metadata = metadata if metadata else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEntry':
        """Create from dictionary after deserialization"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class Conversation:
    """Class to represent a conversation"""
    
    def __init__(self, 
                 conversation_id: str,
                 title: str,
                 start_time: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            title: Title of the conversation
            start_time: When the conversation started
            metadata: Additional metadata
        """
        self.conversation_id = conversation_id
        self.title = title
        self.start_time = start_time if start_time else datetime.now()
        self.end_time: Optional[datetime] = None
        self.entries: List[ConversationEntry] = []
        self.metadata = metadata if metadata else {}
    
    def add_entry(self, entry: ConversationEntry) -> None:
        """Add entry to conversation"""
        self.entries.append(entry)
        self.end_time = entry.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "entries": [entry.to_dict() for entry in self.entries],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create from dictionary after deserialization"""
        conversation = cls(
            conversation_id=data["conversation_id"],
            title=data["title"],
            start_time=datetime.fromisoformat(data["start_time"]),
            metadata=data.get("metadata", {})
        )
        
        if data["end_time"]:
            conversation.end_time = datetime.fromisoformat(data["end_time"])
        
        for entry_data in data["entries"]:
            conversation.entries.append(ConversationEntry.from_dict(entry_data))
        
        return conversation


class ConversationLogger:
    """Logger for conversations between user and AI assistant"""
    
    def __init__(self, db_path: str = "logs/conversations.db"):
        """
        Initialize conversation logger
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger("agentic_ai.conversations")
        self._lock = threading.RLock()
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    metadata TEXT
                )
                ''')
                
                # Create entries table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                )
                ''')
                
                # Create index on conversation_id and timestamp
                cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_entries_conversation_timestamp
                ON entries (conversation_id, timestamp)
                ''')
                
                conn.commit()
                conn.close()
                
                self.logger.info("Initialized conversation database")
            except Exception as e:
                self.logger.error(f"Error initializing database: {str(e)}")
    
    def create_conversation(self, 
                           title: str,
                           conversation_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new conversation
        
        Args:
            title: Title of the conversation
            conversation_id: Unique identifier (generated if None)
            metadata: Additional metadata
            
        Returns:
            str: Conversation ID
        """
        with self._lock:
            try:
                # Generate ID if not provided
                if conversation_id is None:
                    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
                
                # Create conversation object
                conversation = Conversation(
                    conversation_id=conversation_id,
                    title=title,
                    metadata=metadata
                )
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO conversations (conversation_id, title, start_time, metadata) VALUES (?, ?, ?, ?)",
                    (
                        conversation.conversation_id,
                        conversation.title,
                        conversation.start_time.isoformat(),
                        json.dumps(conversation.metadata)
                    )
                )
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Created conversation {conversation_id}")
                return conversation_id
            except Exception as e:
                self.logger.error(f"Error creating conversation: {str(e)}")
                return ""
    
    def add_entry(self,
                 conversation_id: str,
                 role: str,
                 content: str,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add entry to conversation
        
        Args:
            conversation_id: Conversation ID
            role: Role of the speaker (user, assistant)
            content: Content of the message
            metadata: Additional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                # Create entry
                entry = ConversationEntry(
                    role=role,
                    content=content,
                    metadata=metadata
                )
                
                # Store in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Update conversation end time
                cursor.execute(
                    "UPDATE conversations SET end_time = ? WHERE conversation_id = ?",
                    (entry.timestamp.isoformat(), conversation_id)
                )
                
                # Add entry
                cursor.execute(
                    "INSERT INTO entries (conversation_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                    (
                        conversation_id,
                        entry.role,
                        entry.content,
                        entry.timestamp.isoformat(),
                        json.dumps(entry.metadata)
                    )
                )
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Added entry to conversation {conversation_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error adding entry: {str(e)}")
                return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None if not found
        """
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get conversation
                cursor.execute(
                    "SELECT * FROM conversations WHERE conversation_id = ?",
                    (conversation_id,)
                )
                
                row = cursor.fetchone()
                if not row:
                    conn.close()
                    return None
                
                # Create conversation object
                conversation = Conversation(
                    conversation_id=row["conversation_id"],
                    title=row["title"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                )
                
                if row["end_time"]:
                    conversation.end_time = datetime.fromisoformat(row["end_time"])
                
                # Get entries
                cursor.execute(
                    "SELECT * FROM entries WHERE conversation_id = ? ORDER BY timestamp",
                    (conversation_id,)
                )
                
                for entry_row in cursor.fetchall():
                    entry = ConversationEntry(
                        role=entry_row["role"],
                        content=entry_row["content"],
                        timestamp=datetime.fromisoformat(entry_row["timestamp"]),
                        metadata=json.loads(entry_row["metadata"]) if entry_row["metadata"] else {}
                    )
                    conversation.entries.append(entry)
                
                conn.close()
                return conversation
            except Exception as e:
                self.logger.error(f"Error getting conversation: {str(e)}")
                return None
    
    def list_conversations(self, 
                          days: Optional[int] = None,
                          limit: int = 100,
                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        List conversations
        
        Args:
            days: Number of days to look back (None for all)
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversation summaries
        """
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM conversations"
                params = []
                
                if days is not None:
                    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
                    query += " WHERE start_time >= ?"
                    params.append(cutoff)
                
                query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        "conversation_id": row["conversation_id"],
                        "title": row["title"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                conn.close()
                return conversations
            except Exception as e:
                self.logger.error(f"Error listing conversations: {str(e)}")
                return []
    
    def get_conversations_by_date(self, date: Union[str, datetime]) -> List[Dict[str, Any]]:
        """
        Get conversations from a specific date
        
        Args:
            date: Date to filter by (YYYY-MM-DD or datetime object)
            
        Returns:
            List of conversation summaries
        """
        with self._lock:
            try:
                # Normalize date
                if isinstance(date, str):
                    date_obj = datetime.fromisoformat(date.split('T')[0])
                else:
                    date_obj = date
                
                start_of_day = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0).isoformat()
                end_of_day = datetime(date_obj.year, date_obj.month, date_obj.day, 23, 59, 59).isoformat()
                
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM conversations WHERE start_time >= ? AND start_time <= ? ORDER BY start_time",
                    (start_of_day, end_of_day)
                )
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        "conversation_id": row["conversation_id"],
                        "title": row["title"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                conn.close()
                return conversations
            except Exception as e:
                self.logger.error(f"Error getting conversations by date: {str(e)}")
                return []
    
    def search_conversations(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search conversations by content
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of conversation summaries
        """
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # First find entries matching the query
                cursor.execute(
                    """
                    SELECT DISTINCT conversation_id
                    FROM entries
                    WHERE content LIKE ?
                    LIMIT ?
                    """,
                    (f"%{query}%", limit)
                )
                
                conversation_ids = [row["conversation_id"] for row in cursor.fetchall()]
                
                if not conversation_ids:
                    conn.close()
                    return []
                
                # Then get the conversations
                placeholders = ", ".join(["?"] * len(conversation_ids))
                cursor.execute(
                    f"SELECT * FROM conversations WHERE conversation_id IN ({placeholders}) ORDER BY start_time DESC",
                    conversation_ids
                )
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        "conversation_id": row["conversation_id"],
                        "title": row["title"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                conn.close()
                return conversations
            except Exception as e:
                self.logger.error(f"Error searching conversations: {str(e)}")
                return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Delete entries first (due to foreign key constraint)
                cursor.execute(
                    "DELETE FROM entries WHERE conversation_id = ?",
                    (conversation_id,)
                )
                
                # Delete conversation
                cursor.execute(
                    "DELETE FROM conversations WHERE conversation_id = ?",
                    (conversation_id,)
                )
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Deleted conversation {conversation_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error deleting conversation: {str(e)}")
                return False
    
    def summary_for_days_ago(self, days_ago: int) -> Dict[str, Any]:
        """
        Get a summary of conversations from a specific number of days ago
        
        Args:
            days_ago: Number of days ago
            
        Returns:
            Summary dictionary
        """
        target_date = datetime.now() - timedelta(days=days_ago)
        conversations = self.get_conversations_by_date(target_date)
        
        if not conversations:
            return {
                "date": target_date.strftime("%Y-%m-%d"),
                "conversations": [],
                "count": 0,
                "found": False
            }
        
        summaries = []
        for conv in conversations:
            conversation = self.get_conversation(conv["conversation_id"])
            if conversation:
                # Create a summary of the conversation
                sample_entries = conversation.entries[:2]  # Just include the beginning
                summaries.append({
                    "conversation_id": conversation.conversation_id,
                    "title": conversation.title,
                    "start_time": conversation.start_time.isoformat(),
                    "sample": [{"role": e.role, "content": e.content[:100] + "..." 
                               if len(e.content) > 100 else e.content} 
                               for e in sample_entries]
                })
        
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "conversations": summaries,
            "count": len(summaries),
            "found": True
        }
    
    def export_conversation(self, conversation_id: str, format: str = "json") -> Optional[str]:
        """
        Export conversation to a specific format
        
        Args:
            conversation_id: Conversation ID
            format: Export format (json, text, markdown)
            
        Returns:
            Exported conversation as string, None if error
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        try:
            if format == "json":
                return json.dumps(conversation.to_dict(), indent=2)
            elif format == "text":
                lines = [f"Conversation: {conversation.title}"]
                lines.append(f"Date: {conversation.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append("")
                
                for entry in conversation.entries:
                    role = "User" if entry.role == "user" else "Assistant"
                    lines.append(f"{role} ({entry.timestamp.strftime('%H:%M:%S')}):")
                    lines.append(entry.content)
                    lines.append("")
                
                return "\n".join(lines)
            elif format == "markdown":
                lines = [f"# Conversation: {conversation.title}"]
                lines.append(f"**Date:** {conversation.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append("")
                
                for entry in conversation.entries:
                    role = "**User**" if entry.role == "user" else "**Assistant**"
                    lines.append(f"{role} ({entry.timestamp.strftime('%H:%M:%S')}):")
                    lines.append("")
                    lines.append(entry.content)
                    lines.append("")
                
                return "\n".join(lines)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error exporting conversation: {str(e)}")
            return None


# Create a default instance for easy import
default_conversation_logger = ConversationLogger()


# Helper functions for easy use
def create_conversation(title: str, 
                       conversation_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new conversation"""
    return default_conversation_logger.create_conversation(title, conversation_id, metadata)

def add_entry(conversation_id: str,
             role: str,
             content: str,
             metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Add entry to conversation"""
    return default_conversation_logger.add_entry(conversation_id, role, content, metadata)

def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get conversation by ID"""
    return default_conversation_logger.get_conversation(conversation_id)

def list_conversations(days: Optional[int] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict[str, Any]]:
    """List conversations"""
    return default_conversation_logger.list_conversations(days, limit, offset)

def search_conversations(query: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Search conversations by content"""
    return default_conversation_logger.search_conversations(query, limit)

def get_conversations_by_date(date: Union[str, datetime]) -> List[Dict[str, Any]]:
    """Get conversations from a specific date"""
    return default_conversation_logger.get_conversations_by_date(date)

def summary_for_days_ago(days_ago: int) -> Dict[str, Any]:
    """Get a summary of conversations from a specific number of days ago"""
    return default_conversation_logger.summary_for_days_ago(days_ago)

def export_conversation(conversation_id: str, format: str = "json") -> Optional[str]:
    """Export conversation to a specific format"""
    return default_conversation_logger.export_conversation(conversation_id, format)

def delete_conversation(conversation_id: str) -> bool:
    """Delete conversation"""
    return default_conversation_logger.delete_conversation(conversation_id) 