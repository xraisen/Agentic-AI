"""
File System Interface for Agentic AI

This module provides an abstraction layer for file system operations,
ensuring editor-agnostic file access and manipulation capabilities.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Union, Optional, BinaryIO, TextIO, Any
import logging

# Get logger
logger = logging.getLogger("agentic_ai")

# Type hints
PathLike = Union[str, Path]
FileContent = Union[str, bytes]


class FileSystemPermission:
    """Class to represent file system permissions"""
    
    def __init__(self, path: PathLike, allowed_operations: List[str]):
        self.path = str(Path(path).resolve())
        self.allowed_operations = allowed_operations
    
    def can_read(self) -> bool:
        """Check if read operations are allowed"""
        return "read" in self.allowed_operations
    
    def can_write(self) -> bool:
        """Check if write operations are allowed"""
        return "write" in self.allowed_operations
    
    def can_execute(self) -> bool:
        """Check if execute operations are allowed"""
        return "execute" in self.allowed_operations
    
    def can_delete(self) -> bool:
        """Check if delete operations are allowed"""
        return "delete" in self.allowed_operations


class FileSystemInterface:
    """Interface for file system operations"""
    
    def __init__(self, workspace_path: Optional[PathLike] = None, permission_manager=None):
        """
        Initialize the file system interface
        
        Args:
            workspace_path: Root path for workspace operations
            permission_manager: Permission manager instance to verify operations
        """
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.permission_manager = permission_manager
        self.logger = logging.getLogger("agentic_ai.file_system")
    
    def _check_permission(self, path: PathLike, operation: str) -> bool:
        """
        Check if operation is permitted on the path
        
        Args:
            path: Path to check
            operation: Operation to check (read, write, execute, delete)
            
        Returns:
            bool: True if operation is permitted, False otherwise
        """
        if self.permission_manager is None:
            # Default to allowing operations within workspace
            absolute_path = Path(path).resolve()
            workspace_path = self.workspace_path.resolve()
            return str(absolute_path).startswith(str(workspace_path))
            
        return self.permission_manager.check_permission(path, operation)
    
    def _log_operation(self, operation: str, path: PathLike, success: bool = True) -> None:
        """Log file operation"""
        status = "succeeded" if success else "failed"
        self.logger.info(f"File operation {operation} on {path} {status}")
    
    def read_file(self, path: PathLike, binary: bool = False) -> Optional[FileContent]:
        """
        Read file content
        
        Args:
            path: Path to file
            binary: Whether to read in binary mode
            
        Returns:
            File content as string or bytes, None if operation fails
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "read"):
                self.logger.warning(f"Permission denied: Cannot read {path}")
                return None
                
            mode = "rb" if binary else "r"
            with open(path_obj, mode) as f:
                content = f.read()
                
            self._log_operation("read", path)
            return content
        except Exception as e:
            self.logger.error(f"Error reading file {path}: {str(e)}")
            self._log_operation("read", path, False)
            return None
    
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
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "write"):
                self.logger.warning(f"Permission denied: Cannot write to {path}")
                return False
            
            if create_dirs:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                
            mode = "wb" if binary else "w"
            with open(path_obj, mode) as f:
                f.write(content)
                
            self._log_operation("write", path)
            return True
        except Exception as e:
            self.logger.error(f"Error writing to file {path}: {str(e)}")
            self._log_operation("write", path, False)
            return False
    
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
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "write"):
                self.logger.warning(f"Permission denied: Cannot append to {path}")
                return False
            
            if create_dirs:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                
            mode = "ab" if binary else "a"
            with open(path_obj, mode) as f:
                f.write(content)
                
            self._log_operation("append", path)
            return True
        except Exception as e:
            self.logger.error(f"Error appending to file {path}: {str(e)}")
            self._log_operation("append", path, False)
            return False
    
    def delete_file(self, path: PathLike) -> bool:
        """
        Delete a file
        
        Args:
            path: Path to file
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "delete"):
                self.logger.warning(f"Permission denied: Cannot delete {path}")
                return False
                
            if path_obj.is_file():
                os.remove(path_obj)
                self._log_operation("delete", path)
                return True
            else:
                self.logger.warning(f"Not a file: {path}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting file {path}: {str(e)}")
            self._log_operation("delete", path, False)
            return False
    
    def create_directory(self, path: PathLike) -> bool:
        """
        Create a directory
        
        Args:
            path: Path to directory
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "write"):
                self.logger.warning(f"Permission denied: Cannot create directory {path}")
                return False
                
            path_obj.mkdir(parents=True, exist_ok=True)
            self._log_operation("create_dir", path)
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory {path}: {str(e)}")
            self._log_operation("create_dir", path, False)
            return False
    
    def delete_directory(self, path: PathLike, recursive: bool = False) -> bool:
        """
        Delete a directory
        
        Args:
            path: Path to directory
            recursive: Whether to delete recursively
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "delete"):
                self.logger.warning(f"Permission denied: Cannot delete directory {path}")
                return False
                
            if path_obj.is_dir():
                if recursive:
                    shutil.rmtree(path_obj)
                else:
                    os.rmdir(path_obj)
                self._log_operation("delete_dir", path)
                return True
            else:
                self.logger.warning(f"Not a directory: {path}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting directory {path}: {str(e)}")
            self._log_operation("delete_dir", path, False)
            return False
    
    def list_directory(self, path: PathLike) -> Optional[List[Path]]:
        """
        List contents of a directory
        
        Args:
            path: Path to directory
            
        Returns:
            List of paths, None if operation fails
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "read"):
                self.logger.warning(f"Permission denied: Cannot list directory {path}")
                return None
                
            if path_obj.is_dir():
                contents = list(path_obj.iterdir())
                self._log_operation("list_dir", path)
                return contents
            else:
                self.logger.warning(f"Not a directory: {path}")
                return None
        except Exception as e:
            self.logger.error(f"Error listing directory {path}: {str(e)}")
            self._log_operation("list_dir", path, False)
            return None
    
    def file_exists(self, path: PathLike) -> bool:
        """Check if file exists"""
        return Path(path).is_file()
    
    def directory_exists(self, path: PathLike) -> bool:
        """Check if directory exists"""
        return Path(path).is_dir()
    
    def get_file_info(self, path: PathLike) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            path: Path to file
            
        Returns:
            Dict with file information, None if operation fails
        """
        try:
            path_obj = Path(path)
            if not self._check_permission(path_obj, "read"):
                self.logger.warning(f"Permission denied: Cannot get info for {path}")
                return None
                
            if path_obj.exists():
                stat = path_obj.stat()
                info = {
                    "name": path_obj.name,
                    "path": str(path_obj),
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "is_file": path_obj.is_file(),
                    "is_dir": path_obj.is_dir(),
                }
                self._log_operation("get_info", path)
                return info
            else:
                self.logger.warning(f"Path does not exist: {path}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting info for {path}: {str(e)}")
            self._log_operation("get_info", path, False)
            return None
    
    def copy_file(self, src_path: PathLike, dst_path: PathLike) -> bool:
        """
        Copy file from source to destination
        
        Args:
            src_path: Source path
            dst_path: Destination path
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        try:
            src_obj = Path(src_path)
            dst_obj = Path(dst_path)
            
            if not self._check_permission(src_obj, "read"):
                self.logger.warning(f"Permission denied: Cannot read {src_path}")
                return False
                
            if not self._check_permission(dst_obj, "write"):
                self.logger.warning(f"Permission denied: Cannot write to {dst_path}")
                return False
                
            if src_obj.is_file():
                dst_obj.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_obj, dst_obj)
                self._log_operation("copy", f"{src_path} to {dst_path}")
                return True
            else:
                self.logger.warning(f"Not a file: {src_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error copying {src_path} to {dst_path}: {str(e)}")
            self._log_operation("copy", f"{src_path} to {dst_path}", False)
            return False
    
    def move_file(self, src_path: PathLike, dst_path: PathLike) -> bool:
        """
        Move file from source to destination
        
        Args:
            src_path: Source path
            dst_path: Destination path
            
        Returns:
            bool: True if operation succeeds, False otherwise
        """
        try:
            src_obj = Path(src_path)
            dst_obj = Path(dst_path)
            
            if not self._check_permission(src_obj, "read") or not self._check_permission(src_obj, "delete"):
                self.logger.warning(f"Permission denied: Cannot read/delete {src_path}")
                return False
                
            if not self._check_permission(dst_obj, "write"):
                self.logger.warning(f"Permission denied: Cannot write to {dst_path}")
                return False
                
            if src_obj.exists():
                dst_obj.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src_obj, dst_obj)
                self._log_operation("move", f"{src_path} to {dst_path}")
                return True
            else:
                self.logger.warning(f"Path does not exist: {src_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error moving {src_path} to {dst_path}: {str(e)}")
            self._log_operation("move", f"{src_path} to {dst_path}", False)
            return False


# Create a default instance for easy import
default_fs = FileSystemInterface()


# Helper functions for easy use
def read_file(path: PathLike, binary: bool = False) -> Optional[FileContent]:
    """Read file content"""
    return default_fs.read_file(path, binary)

def write_file(path: PathLike, content: FileContent, binary: bool = False) -> bool:
    """Write content to file"""
    return default_fs.write_file(path, content, binary)

def append_file(path: PathLike, content: FileContent, binary: bool = False) -> bool:
    """Append content to file"""
    return default_fs.append_file(path, content, binary)

def delete_file(path: PathLike) -> bool:
    """Delete a file"""
    return default_fs.delete_file(path)

def create_directory(path: PathLike) -> bool:
    """Create a directory"""
    return default_fs.create_directory(path)

def delete_directory(path: PathLike, recursive: bool = False) -> bool:
    """Delete a directory"""
    return default_fs.delete_directory(path, recursive)

def list_directory(path: PathLike) -> Optional[List[Path]]:
    """List contents of a directory"""
    return default_fs.list_directory(path)

def file_exists(path: PathLike) -> bool:
    """Check if file exists"""
    return default_fs.file_exists(path)

def directory_exists(path: PathLike) -> bool:
    """Check if directory exists"""
    return default_fs.directory_exists(path)

def get_file_info(path: PathLike) -> Optional[Dict[str, Any]]:
    """Get file information"""
    return default_fs.get_file_info(path)

def copy_file(src_path: PathLike, dst_path: PathLike) -> bool:
    """Copy file from source to destination"""
    return default_fs.copy_file(src_path, dst_path)

def move_file(src_path: PathLike, dst_path: PathLike) -> bool:
    """Move file from source to destination"""
    return default_fs.move_file(src_path, dst_path) 