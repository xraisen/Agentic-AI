import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..utils.logger import log_action, log_error, log_debug

class KnowledgeManager:
    """Manages knowledge retrieval and tracking from logs and documentation."""
    
    def __init__(self):
        try:
            self.logs_dir = Path("logs")
            self.docs_dir = Path("docs")
            self.knowledge_cache = {}
            self.last_update = None
            
            # Ensure directories exist
            self.logs_dir.mkdir(exist_ok=True)
            self.docs_dir.mkdir(exist_ok=True)
            
            # Initialize cache
            self.update_knowledge_cache()
            log_action("KnowledgeManager initialized", "Starting knowledge tracking system")
        except Exception as e:
            log_error(e, "Failed to initialize KnowledgeManager")
            raise

    def _load_log_file(self, log_file: str) -> List[Dict[str, Any]]:
        """Load and parse a log file."""
        try:
            log_path = self.logs_dir / log_file
            if not log_path.exists():
                log_debug(f"Log file not found", f"File: {log_file}")
                return []
            
            entries = []
            with open(log_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        # Skip empty lines
                        if not line.strip():
                            continue
                            
                        # Validate line format
                        if len(line) < 31:  # Minimum length for timestamp + level + details
                            log_error(ValueError(f"Invalid line format at line {line_num}"), "Log parsing")
                            continue
                            
                        # Parse log entry
                        timestamp = line[:19]  # YYYY-MM-DD HH:mm:ss
                        level = line[22:30].strip()
                        details = line[31:].strip()
                        
                        # Validate timestamp format
                        try:
                            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            log_error(ValueError(f"Invalid timestamp at line {line_num}"), "Log parsing")
                            continue
                        
                        entries.append({
                            "timestamp": timestamp,
                            "level": level,
                            "details": details
                        })
                    except Exception as e:
                        log_error(e, f"Failed to parse log line {line_num}: {line[:100]}...")
                        continue
            
            return entries
        except Exception as e:
            log_error(e, f"Failed to load log file: {log_file}")
            return []

    def _load_documentation(self) -> Dict[str, str]:
        """Load documentation files."""
        docs = {}
        try:
            for doc_file in ["README.md", "knowledgebase.md", "how-to-use.md"]:
                doc_path = self.docs_dir / doc_file
                if doc_path.exists():
                    try:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty files
                                docs[doc_file] = content
                                log_debug(f"Loaded documentation", f"File: {doc_file}")
                            else:
                                log_debug(f"Skipped empty documentation", f"File: {doc_file}")
                    except Exception as e:
                        log_error(e, f"Failed to load documentation file: {doc_file}")
                        continue
                else:
                    log_debug(f"Documentation file not found", f"File: {doc_file}")
        except Exception as e:
            log_error(e, "Failed to load documentation")
        return docs

    def update_knowledge_cache(self):
        """Update the knowledge cache with latest logs and documentation."""
        try:
            # Load logs
            self.knowledge_cache["logs"] = {
                "app": self._load_log_file("app.log"),
                "error": self._load_log_file("error.log"),
                "history": self._load_log_file("history.log")
            }
            
            # Load documentation
            self.knowledge_cache["docs"] = self._load_documentation()
            
            self.last_update = datetime.now().isoformat()
            log_action("Knowledge cache updated", "Latest data loaded")
        except Exception as e:
            log_error(e, "Failed to update knowledge cache")
            # Keep old cache if update fails
            if not self.knowledge_cache:
                self.knowledge_cache = {"logs": {}, "docs": {}}

    def get_conversation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        if not self.last_update:
            self.update_knowledge_cache()
        
        try:
            history = []
            for entry in self.knowledge_cache["logs"].get("history", []):
                if "Action: Message sent" in entry["details"] or "Action: Response displayed" in entry["details"]:
                    history.append(entry)
                    if len(history) >= limit:
                        break
            return history
        except Exception as e:
            log_error(e, "Failed to get conversation history")
            return []

    def get_recent_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent user actions."""
        if not self.last_update:
            self.update_knowledge_cache()
        
        try:
            actions = []
            for entry in self.knowledge_cache["logs"].get("app", []):
                if entry["level"] == "INFO" and "Action:" in entry["details"]:
                    actions.append(entry)
                    if len(actions) >= limit:
                        break
            return actions
        except Exception as e:
            log_error(e, "Failed to get recent actions")
            return []

    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors."""
        if not self.last_update:
            self.update_knowledge_cache()
        
        try:
            return self.knowledge_cache["logs"].get("error", [])[:limit]
        except Exception as e:
            log_error(e, "Failed to get recent errors")
            return []

    def search_documentation(self, query: str) -> Dict[str, List[str]]:
        """Search documentation for relevant information."""
        if not self.last_update:
            self.update_knowledge_cache()
        
        try:
            results = {}
            if not query.strip():
                return results
                
            query = query.lower()
            for doc_name, content in self.knowledge_cache["docs"].items():
                lines = content.split('\n')
                matches = [line for line in lines if query in line.lower()]
                if matches:
                    results[doc_name] = matches[:5]  # Limit to 5 matches per doc
            return results
        except Exception as e:
            log_error(e, "Failed to search documentation")
            return {}

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics."""
        if not self.last_update:
            self.update_knowledge_cache()
        
        try:
            return {
                "last_update": self.last_update,
                "conversation_count": len(self.get_conversation_history()),
                "action_count": len(self.get_recent_actions()),
                "error_count": len(self.get_recent_errors()),
                "documentation_files": list(self.knowledge_cache["docs"].keys())
            }
        except Exception as e:
            log_error(e, "Failed to get system status")
            return {
                "last_update": None,
                "conversation_count": 0,
                "action_count": 0,
                "error_count": 0,
                "documentation_files": []
            }

    def get_knowledge_summary(self) -> str:
        """Generate a summary of current knowledge state."""
        try:
            status = self.get_system_status()
            recent_actions = self.get_recent_actions(5)
            recent_errors = self.get_recent_errors(3)
            
            summary = [
                f"Knowledge Summary (Last Updated: {status['last_update'] or 'Never'})",
                f"Total Conversations: {status['conversation_count']}",
                f"Recent Actions: {len(recent_actions)}",
                f"Recent Errors: {len(recent_errors)}",
                "\nRecent Actions:",
                *[f"- {action['details']}" for action in recent_actions],
                "\nRecent Errors:",
                *[f"- {error['details']}" for error in recent_errors]
            ]
            
            return "\n".join(summary)
        except Exception as e:
            log_error(e, "Failed to generate knowledge summary")
            return "Error: Failed to generate knowledge summary" 