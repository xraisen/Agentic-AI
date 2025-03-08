"""
Permission Management System for Agentic AI

This module provides a robust permission management system for controlling
access to file system operations and system commands.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional, Set, Any
from datetime import datetime, timedelta
import threading

# Get logger
logger = logging.getLogger("agentic_ai")

# Type hints
PathLike = Union[str, Path]


class PermissionRecord:
    """Class to represent a permission record"""
    
    def __init__(self, 
                 path: PathLike,
                 operations: List[str],
                 granted_by: str = "user",
                 expires_at: Optional[datetime] = None):
        """
        Initialize permission record
        
        Args:
            path: Target path
            operations: Allowed operations (read, write, execute, delete)
            granted_by: Who granted the permission
            expires_at: When the permission expires
        """
        self.path = str(Path(path).resolve())
        self.operations = set(operations)
        self.granted_by = granted_by
        self.expires_at = expires_at
        self.granted_at = datetime.now()
    
    def is_valid(self) -> bool:
        """Check if permission is still valid"""
        if self.expires_at is None:
            return True
        return datetime.now() < self.expires_at
    
    def allows(self, operation: str) -> bool:
        """Check if permission allows operation"""
        return operation in self.operations and self.is_valid()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "path": self.path,
            "operations": list(self.operations),
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PermissionRecord':
        """Create from dictionary after deserialization"""
        record = cls(
            path=data["path"],
            operations=data["operations"],
            granted_by=data["granted_by"]
        )
        record.granted_at = datetime.fromisoformat(data["granted_at"])
        if data["expires_at"]:
            record.expires_at = datetime.fromisoformat(data["expires_at"])
        return record


class PermissionManager:
    """Permission manager for file system and system operations"""
    
    def __init__(self, 
                 config_path: PathLike = "config/permissions.json",
                 auto_save: bool = True,
                 workspace_path: Optional[PathLike] = None):
        """
        Initialize permission manager
        
        Args:
            config_path: Path to permission configuration file
            auto_save: Whether to automatically save changes
            workspace_path: Default workspace path (implicit permissions)
        """
        self.config_path = Path(config_path)
        self.auto_save = auto_save
        self.workspace_path = Path(workspace_path).resolve() if workspace_path else None
        self.permissions: Dict[str, PermissionRecord] = {}
        self.ui_callback = None
        self.logger = logging.getLogger("agentic_ai.permissions")
        
        # Create lock for thread safety
        self._lock = threading.RLock()
        
        # Load existing permissions
        self._load_permissions()
    
    def set_ui_callback(self, callback: callable) -> None:
        """
        Set UI callback for permission requests
        
        The callback should have the signature:
        callback(path: str, operation: str) -> bool
        """
        self.ui_callback = callback
    
    def _load_permissions(self) -> None:
        """Load permissions from configuration file"""
        with self._lock:
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'r') as f:
                        data = json.load(f)
                        
                    # Clear expired permissions
                    now = datetime.now()
                    permissions = {}
                    
                    for path, record_data in data.items():
                        record = PermissionRecord.from_dict(record_data)
                        if record.is_valid():
                            permissions[path] = record
                    
                    self.permissions = permissions
                    self.logger.info(f"Loaded {len(self.permissions)} permission records")
            except Exception as e:
                self.logger.error(f"Error loading permissions: {str(e)}")
                self.permissions = {}
    
    def _save_permissions(self) -> None:
        """Save permissions to configuration file"""
        with self._lock:
            try:
                # Create directory if it doesn't exist
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert permissions to serializable format
                data = {}
                for path, record in self.permissions.items():
                    data[path] = record.to_dict()
                
                with open(self.config_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                self.logger.info(f"Saved {len(self.permissions)} permission records")
            except Exception as e:
                self.logger.error(f"Error saving permissions: {str(e)}")
    
    def check_permission(self, path: PathLike, operation: str) -> bool:
        """
        Check if operation is permitted on the path
        
        Args:
            path: Path to check
            operation: Operation to check (read, write, execute, delete)
            
        Returns:
            bool: True if operation is permitted, False otherwise
        """
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        
        with self._lock:
            # Check workspace implicit permissions
            if self.workspace_path and str(path_obj).startswith(str(self.workspace_path)):
                # Allow read operations within workspace by default
                if operation == "read":
                    return True
                
                # For write/delete/execute, still need explicit permission
                # unless it's within certain safe directories
                safe_dirs = [
                    "logs",
                    "cache",
                    "temp",
                    "output"
                ]
                
                # Check if path is in a safe directory within workspace
                for safe_dir in safe_dirs:
                    safe_path = self.workspace_path / safe_dir
                    if str(path_obj).startswith(str(safe_path)):
                        if operation in ["write", "delete"]:  # Still not allowing execute by default
                            return True
            
            # Check explicit permissions
            # First, check exact path match
            if path_str in self.permissions and self.permissions[path_str].allows(operation):
                return True
            
            # Then check parent directories
            parent = path_obj
            while parent != parent.parent:
                parent = parent.parent
                parent_str = str(parent)
                
                if parent_str in self.permissions:
                    record = self.permissions[parent_str]
                    if record.allows(operation):
                        return True
            
            # No permission found, ask user if callback is set
            if self.ui_callback:
                granted = self.ui_callback(path_str, operation)
                if granted:
                    self.grant_permission(path_str, [operation])
                    return True
            
            return False
    
    def grant_permission(self, 
                         path: PathLike,
                         operations: List[str],
                         duration: Optional[int] = None,
                         granted_by: str = "user") -> None:
        """
        Grant permission for operations on path
        
        Args:
            path: Target path
            operations: Operations to allow (read, write, execute, delete)
            duration: Duration in seconds (None for permanent)
            granted_by: Who granted the permission
        """
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        
        with self._lock:
            # Calculate expiration time
            expires_at = None
            if duration is not None:
                expires_at = datetime.now() + timedelta(seconds=duration)
            
            # Check if permission record already exists
            if path_str in self.permissions:
                # Update existing record
                record = self.permissions[path_str]
                record.operations.update(operations)
                record.granted_by = granted_by
                record.expires_at = expires_at
                record.granted_at = datetime.now()
            else:
                # Create new record
                record = PermissionRecord(
                    path=path_str,
                    operations=operations,
                    granted_by=granted_by,
                    expires_at=expires_at
                )
                self.permissions[path_str] = record
            
            self.logger.info(f"Granted {operations} permission on {path_str}")
            
            # Auto-save if enabled
            if self.auto_save:
                self._save_permissions()
    
    def revoke_permission(self, path: PathLike, operations: Optional[List[str]] = None) -> None:
        """
        Revoke permission for operations on path
        
        Args:
            path: Target path
            operations: Operations to revoke (None for all)
        """
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        
        with self._lock:
            if path_str in self.permissions:
                if operations is None:
                    # Revoke all permissions
                    del self.permissions[path_str]
                    self.logger.info(f"Revoked all permissions on {path_str}")
                else:
                    # Revoke specific operations
                    record = self.permissions[path_str]
                    for op in operations:
                        if op in record.operations:
                            record.operations.remove(op)
                    
                    # Remove record if no operations left
                    if not record.operations:
                        del self.permissions[path_str]
                    
                    self.logger.info(f"Revoked {operations} permission on {path_str}")
                
                # Auto-save if enabled
                if self.auto_save:
                    self._save_permissions()
    
    def list_permissions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active permissions
        
        Returns:
            Dict: Dictionary of path -> permission record
        """
        with self._lock:
            # Remove expired permissions
            to_remove = []
            for path, record in self.permissions.items():
                if not record.is_valid():
                    to_remove.append(path)
            
            for path in to_remove:
                del self.permissions[path]
            
            if to_remove and self.auto_save:
                self._save_permissions()
            
            # Convert to dictionary
            result = {}
            for path, record in self.permissions.items():
                result[path] = record.to_dict()
            
            return result
    
    def clear_permissions(self) -> None:
        """Clear all permissions"""
        with self._lock:
            self.permissions.clear()
            if self.auto_save:
                self._save_permissions()
            self.logger.info("Cleared all permissions")
    
    def has_permission(self, path: PathLike, operation: str) -> bool:
        """
        Check if permission exists without triggering UI callback
        
        Args:
            path: Path to check
            operation: Operation to check
            
        Returns:
            bool: True if permission exists, False otherwise
        """
        # Save current callback
        callback = self.ui_callback
        self.ui_callback = None
        
        # Check permission
        try:
            return self.check_permission(path, operation)
        finally:
            # Restore callback
            self.ui_callback = callback

    def request_permission(self, path: PathLike, operation: str) -> bool:
        """
        Request permission for an operation on a path
        
        Args:
            path: Path to request permission for
            operation: Operation to request permission for
            
        Returns:
            bool: True if permission was granted, False otherwise
        """
        # First check if permission already exists
        if self.check_permission(path, operation):
            return True
            
        # If we have a UI callback, use it to request permission
        if self.ui_callback:
            if self.ui_callback(path, operation):
                # Permission granted, store it
                self.grant_permission(path, [operation])
                return True
            else:
                # Permission denied
                return False
        
        # For specific system drives, grant automatic permission for read operations
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        
        if operation == "read":
            # Auto-grant read permission for root directories (drives)
            if len(path_obj.parts) <= 2:  # e.g., "C:\" or "/home"
                self.grant_permission(path, ["read"], duration=3600)  # Grant for 1 hour
                return True
        
        # No UI callback and no auto-permission, deny by default
        return False


# Create a default instance for easy import
default_permission_manager = PermissionManager()


# Helper functions for easy use
def check_permission(path: PathLike, operation: str) -> bool:
    """Check if operation is permitted on the path"""
    return default_permission_manager.check_permission(path, operation)

def grant_permission(path: PathLike, operations: List[str], duration: Optional[int] = None) -> None:
    """Grant permission for operations on path"""
    default_permission_manager.grant_permission(path, operations, duration)

def revoke_permission(path: PathLike, operations: Optional[List[str]] = None) -> None:
    """Revoke permission for operations on path"""
    default_permission_manager.revoke_permission(path, operations)

def list_permissions() -> Dict[str, Dict[str, Any]]:
    """List all active permissions"""
    return default_permission_manager.list_permissions()

def clear_permissions() -> None:
    """Clear all permissions"""
    default_permission_manager.clear_permissions()

def has_permission(path: PathLike, operation: str) -> bool:
    """Check if permission exists without triggering UI callback"""
    return default_permission_manager.has_permission(path, operation) 