"""
File Operations Core Module for Agentic AI

This module integrates the file system abstraction layer and permission management
system with the core application. It provides a unified interface for file operations
with proper permission handling and logging.
"""

import os
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, List, Any, Union, Callable
from pathlib import Path

# Import abstraction layers
from src.utils.file_system_interface import FileSystemInterface
from src.utils.permission_manager import PermissionManager

# Type aliases
PathLike = Union[str, Path]
FileContent = Union[str, bytes]

# Get logger
logger = logging.getLogger("agentic_ai.core.file_operations")


class FileOperationManager:
    """
    Manager for file operations with permission handling
    
    This class integrates the file system abstraction layer with the permission
    management system to provide a secure interface for file operations.
    """
    
    def __init__(self, workspace_path: Optional[PathLike] = None):
        """
        Initialize file operation manager
        
        Args:
            workspace_path: Path to the workspace (project root)
        """
        # Set workspace path
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        logger.info(f"Initializing file operation manager with workspace: {self.workspace_path}")
        
        # Create permission manager
        self.permission_manager = PermissionManager(
            config_path="config/permissions.json",
            auto_save=True,
            workspace_path=self.workspace_path
        )
        
        # Set UI callback for permission requests
        self.permission_manager.set_ui_callback(self._permission_request_callback)
        
        # Create file system interface
        self.fs = FileSystemInterface(
            workspace_path=self.workspace_path,
            permission_manager=self.permission_manager
        )
        
        # Root window for dialogs
        self.root = None
    
    def _create_root_if_needed(self):
        """Create Tk root window if it doesn't exist"""
        if self.root is None or not self._is_root_valid():
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the window
    
    def _is_root_valid(self):
        """Check if root window is valid"""
        if self.root is None:
            return False
            
        try:
            return self.root.winfo_exists()
        except tk.TclError:
            return False
    
    def _permission_request_callback(self, path: str, operation: str) -> bool:
        """
        Callback for permission requests
        
        Args:
            path: Path to resource
            operation: Operation type (read, write, execute, delete)
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Create root window if needed
        self._create_root_if_needed()
        
        # Format operation for display
        op_display = {
            "read": "read from",
            "write": "write to",
            "execute": "execute",
            "delete": "delete"
        }.get(operation, operation)
        
        # Show permission request dialog
        response = messagebox.askyesno(
            title="Permission Request",
            message=f"Allow Agentic AI to {op_display}:\n\n{path}?",
            detail="Click Yes to allow this operation, No to deny.",
            icon="question"
        )
        
        if response:
            logger.info(f"User granted {operation} permission for {path}")
            return True
        else:
            logger.info(f"User denied {operation} permission for {path}")
            return False
    
    # File operations with permission handling
    
    def read_file(self, path: PathLike, binary: bool = False) -> Optional[FileContent]:
        """
        Read file content
        
        Args:
            path: Path to file
            binary: Whether to read in binary mode
            
        Returns:
            File content or None if operation fails
        """
        return self.fs.read_file(path, binary)
    
    def write_file(self, path: PathLike, content: FileContent, 
                   binary: bool = False, create_dirs: bool = True) -> bool:
        """
        Write content to file
        
        Args:
            path: Path to file
            content: Content to write
            binary: Whether to write in binary mode
            create_dirs: Whether to create parent directories
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.write_file(path, content, binary, create_dirs)
    
    def append_file(self, path: PathLike, content: FileContent, 
                    binary: bool = False, create_dirs: bool = True) -> bool:
        """
        Append content to file
        
        Args:
            path: Path to file
            content: Content to append
            binary: Whether to append in binary mode
            create_dirs: Whether to create parent directories
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.append_file(path, content, binary, create_dirs)
    
    def delete_file(self, path: PathLike) -> bool:
        """
        Delete a file
        
        Args:
            path: Path to file
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.delete_file(path)
    
    def create_directory(self, path: PathLike) -> bool:
        """
        Create a directory
        
        Args:
            path: Path to directory
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.create_directory(path)
    
    def delete_directory(self, path: PathLike, recursive: bool = False) -> bool:
        """
        Delete a directory
        
        Args:
            path: Path to directory
            recursive: Whether to delete recursively
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.delete_directory(path, recursive)
    
    def list_directory(self, path: PathLike) -> Optional[List[Path]]:
        """
        List contents of a directory
        
        Args:
            path: Path to directory
            
        Returns:
            List of paths or None if operation fails
        """
        return self.fs.list_directory(path)
    
    def file_exists(self, path: PathLike) -> bool:
        """Check if file exists"""
        return self.fs.file_exists(path)
    
    def directory_exists(self, path: PathLike) -> bool:
        """Check if directory exists"""
        return self.fs.directory_exists(path)
    
    def get_file_info(self, path: PathLike) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            path: Path to file
            
        Returns:
            Dict with file information or None if operation fails
        """
        return self.fs.get_file_info(path)
    
    def copy_file(self, src_path: PathLike, dst_path: PathLike) -> bool:
        """
        Copy file from source to destination
        
        Args:
            src_path: Source path
            dst_path: Destination path
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.copy_file(src_path, dst_path)
    
    def move_file(self, src_path: PathLike, dst_path: PathLike) -> bool:
        """
        Move file from source to destination
        
        Args:
            src_path: Source path
            dst_path: Destination path
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        return self.fs.move_file(src_path, dst_path)
    
    # Permission management
    
    def grant_permission(self, path: PathLike, 
                         operations: List[str], 
                         duration: Optional[int] = None) -> None:
        """
        Grant permission for operations on path
        
        Args:
            path: Target path
            operations: Operations to allow (read, write, execute, delete)
            duration: Duration in seconds (None for permanent)
        """
        self.permission_manager.grant_permission(path, operations, duration)
    
    def revoke_permission(self, path: PathLike, operations: Optional[List[str]] = None) -> None:
        """
        Revoke permission for operations on path
        
        Args:
            path: Target path
            operations: Operations to revoke (None for all)
        """
        self.permission_manager.revoke_permission(path, operations)
    
    def list_permissions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active permissions
        
        Returns:
            Dict: Dictionary of path -> permission record
        """
        return self.permission_manager.list_permissions()


# Create a default instance for easy import
default_file_manager = FileOperationManager()


# Helper functions for easy use
def read_file(path: PathLike, binary: bool = False) -> Optional[FileContent]:
    """Read file content"""
    return default_file_manager.read_file(path, binary)

def write_file(path: PathLike, content: FileContent, binary: bool = False) -> bool:
    """Write content to file"""
    return default_file_manager.write_file(path, content, binary)

def append_file(path: PathLike, content: FileContent, binary: bool = False) -> bool:
    """Append content to file"""
    return default_file_manager.append_file(path, content, binary)

def delete_file(path: PathLike) -> bool:
    """Delete a file"""
    return default_file_manager.delete_file(path)

def create_directory(path: PathLike) -> bool:
    """Create a directory"""
    return default_file_manager.create_directory(path)

def delete_directory(path: PathLike, recursive: bool = False) -> bool:
    """Delete a directory"""
    return default_file_manager.delete_directory(path, recursive)

def list_directory(path: PathLike) -> Optional[List[Path]]:
    """List contents of a directory"""
    return default_file_manager.list_directory(path)

def file_exists(path: PathLike) -> bool:
    """Check if file exists"""
    return default_file_manager.file_exists(path)

def directory_exists(path: PathLike) -> bool:
    """Check if directory exists"""
    return default_file_manager.directory_exists(path)

def get_file_info(path: PathLike) -> Optional[Dict[str, Any]]:
    """Get file information"""
    return default_file_manager.get_file_info(path)

def copy_file(src_path: PathLike, dst_path: PathLike) -> bool:
    """Copy file from source to destination"""
    return default_file_manager.copy_file(src_path, dst_path)

def move_file(src_path: PathLike, dst_path: PathLike) -> bool:
    """Move file from source to destination"""
    return default_file_manager.move_file(src_path, dst_path)

def grant_permission(path: PathLike, operations: List[str], duration: Optional[int] = None) -> None:
    """Grant permission for operations on path"""
    return default_file_manager.grant_permission(path, operations, duration)

def revoke_permission(path: PathLike, operations: Optional[List[str]] = None) -> None:
    """Revoke permission for operations on path"""
    return default_file_manager.revoke_permission(path, operations)

def list_permissions() -> Dict[str, Dict[str, Any]]:
    """List all active permissions"""
    return default_file_manager.list_permissions() 