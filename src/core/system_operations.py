"""
System Operations Core Module for Agentic AI

This module provides a secure interface for system-level operations
with proper permission handling and logging.
"""

import os
import sys
import subprocess
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, List, Any, Union, Tuple
from pathlib import Path

# Import permission manager
from src.utils.permission_manager import PermissionManager

# Get logger
logger = logging.getLogger("agentic_ai.core.system_operations")


class SystemOperationManager:
    """
    Manager for system operations with permission handling
    
    This class provides a secure interface for executing system commands
    with appropriate permission checks and logging.
    """
    
    def __init__(self, workspace_path: Optional[Union[str, Path]] = None):
        """
        Initialize system operation manager
        
        Args:
            workspace_path: Path to the workspace (project root)
        """
        # Set workspace path
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        logger.info(f"Initializing system operation manager with workspace: {self.workspace_path}")
        
        # Create permission manager
        self.permission_manager = PermissionManager(
            config_path="config/permissions.json",
            auto_save=True,
            workspace_path=self.workspace_path
        )
        
        # Set UI callback for permission requests
        self.permission_manager.set_ui_callback(self._permission_request_callback)
        
        # Root window for dialogs
        self.root = None
        
        # List of safe commands that don't require permissions
        self.safe_commands = [
            "dir", "ls", "echo", "cd", "pwd", "type", "cat", "more", "date", "time",
            "whoami", "hostname", "ver", "python --version", "pip --version"
        ]
    
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
    
    def _permission_request_callback(self, command: str, operation: str) -> bool:
        """
        Callback for permission requests
        
        Args:
            command: Command to execute
            operation: Operation type (execute)
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Create root window if needed
        self._create_root_if_needed()
        
        # Show permission request dialog
        response = messagebox.askyesno(
            title="System Command Permission Request",
            message=f"Allow Agentic AI to execute the following command?\n\n{command}",
            detail="Click Yes to allow this operation, No to deny.",
            icon="question"
        )
        
        if response:
            logger.info(f"User granted execute permission for command: {command}")
            return True
        else:
            logger.info(f"User denied execute permission for command: {command}")
            return False
    
    def _is_safe_command(self, command: str) -> bool:
        """
        Check if a command is in the safe list
        
        Args:
            command: Command to check
            
        Returns:
            bool: True if the command is safe, False otherwise
        """
        command_base = command.split()[0].lower()
        
        # Check against safe commands list
        for safe_cmd in self.safe_commands:
            safe_cmd_base = safe_cmd.split()[0].lower()
            if command_base == safe_cmd_base:
                return True
        
        return False
    
    def execute_command(self, 
                       command: str, 
                       cwd: Optional[Union[str, Path]] = None,
                       shell: bool = True,
                       capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute a system command
        
        Args:
            command: Command to execute
            cwd: Working directory (defaults to workspace path)
            shell: Whether to execute in shell
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Tuple: (exit_code, stdout, stderr)
        """
        # Use workspace path as default working directory
        if cwd is None:
            cwd = self.workspace_path
        
        # Check if safe command or get permission
        if not self._is_safe_command(command):
            # For permission checking, we only need the command name, not the path
            # This avoids issues with trying to resolve a command string as a path
            command_str = command
            if not self.permission_manager.has_permission(command_str, "execute"):
                if not self._permission_request_callback(command_str, "execute"):
                    logger.warning(f"Permission denied for command: {command}")
                    return 1, "", "Permission denied"
                # Grant permission for this command
                self.permission_manager.grant_permission(command_str, ["execute"])
        
        # Log command execution
        logger.info(f"Executing command: {command}")
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Return results
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return 1, "", "Command timed out after 5 minutes"
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return 1, "", f"Error: {str(e)}"
    
    def execute_python_script(self, 
                             script_path: Union[str, Path],
                             args: Optional[List[str]] = None,
                             cwd: Optional[Union[str, Path]] = None) -> Tuple[int, str, str]:
        """
        Execute a Python script
        
        Args:
            script_path: Path to script
            args: Command line arguments
            cwd: Working directory
            
        Returns:
            Tuple: (exit_code, stdout, stderr)
        """
        # Convert to Path object for validation
        script_path_obj = Path(script_path)
        
        # Check if script exists
        if not script_path_obj.exists():
            logger.error(f"Script not found: {script_path}")
            return 1, "", f"Script not found: {script_path}"
        
        # Get Python executable
        python_exe = sys.executable
        
        # Build command - using separate arguments instead of a command string
        command_args = [python_exe, str(script_path_obj)]
        if args:
            command_args.extend(args)
        
        # Log what we're about to do
        command_str = f"Executing Python script: {script_path}"
        logger.info(command_str)
        
        try:
            # Execute command using args instead of a shell string
            result = subprocess.run(
                command_args,
                cwd=cwd if cwd else self.workspace_path,
                shell=False,  # Set to False when using args
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Return results
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Script execution timed out: {script_path}")
            return 1, "", "Script execution timed out after 5 minutes"
        except Exception as e:
            logger.error(f"Error executing script {script_path}: {e}")
            return 1, "", f"Error: {str(e)}"
    
    def install_package(self, 
                       package_name: str,
                       upgrade: bool = False,
                       user: bool = True) -> Tuple[int, str, str]:
        """
        Install a Python package
        
        Args:
            package_name: Name of the package
            upgrade: Whether to upgrade if already installed
            user: Whether to install in user site-packages
            
        Returns:
            Tuple: (exit_code, stdout, stderr)
        """
        # Get Python executable
        python_exe = sys.executable
        
        # Build command arguments as list
        command_args = [python_exe, "-m", "pip", "install", package_name]
        if upgrade:
            command_args.append("--upgrade")
        if user:
            command_args.append("--user")
        
        # Execute using subprocess directly with args
        try:
            result = subprocess.run(
                command_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Error installing package {package_name}: {e}")
            return 1, "", f"Error: {str(e)}"
    
    def open_file(self, file_path: Union[str, Path]) -> bool:
        """
        Open a file with the default system application
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Check permission
        if not self.permission_manager.check_permission(str(file_path), "execute"):
            logger.warning(f"Permission denied to open file: {file_path}")
            return False
        
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
                return True
            elif sys.platform == 'darwin':  # macOS
                returncode, _, _ = self.execute_command(f'open "{file_path}"')
                return returncode == 0
            else:  # Linux
                returncode, _, _ = self.execute_command(f'xdg-open "{file_path}"')
                return returncode == 0
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False


# Create a default instance for easy import
default_system_manager = SystemOperationManager()


# Helper functions for easy use
def execute_command(command: str, 
                   cwd: Optional[Union[str, Path]] = None,
                   shell: bool = True,
                   capture_output: bool = True) -> Tuple[int, str, str]:
    """Execute a system command"""
    return default_system_manager.execute_command(command, cwd, shell, capture_output)

def execute_python_script(script_path: Union[str, Path],
                         args: Optional[List[str]] = None,
                         cwd: Optional[Union[str, Path]] = None) -> Tuple[int, str, str]:
    """Execute a Python script"""
    return default_system_manager.execute_python_script(script_path, args, cwd)

def install_package(package_name: str,
                   upgrade: bool = False,
                   user: bool = True) -> Tuple[int, str, str]:
    """Install a Python package"""
    return default_system_manager.install_package(package_name, upgrade, user)

def open_file(file_path: Union[str, Path]) -> bool:
    """Open a file with the default system application"""
    return default_system_manager.open_file(file_path) 