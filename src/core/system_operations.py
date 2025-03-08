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
import platform
import ctypes
import tempfile
import winreg
from typing import Optional, Dict, List, Any, Union, Tuple, Callable
from pathlib import Path
import threading

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
        
        # Track running background processes
        self.running_processes = {}
        self.process_lock = threading.Lock()
        
        # List of safe commands that don't require permissions
        self.safe_commands = [
            "dir", "ls", "echo", "cd", "pwd", "type", "cat", "more", "date", "time",
            "whoami", "hostname", "ver", "python --version", "pip --version"
        ]
        
        # Track elevated privileges
        self.is_elevated = self._check_if_elevated()
        
        # Last operation status for rollback
        self.last_operation = {
            "type": None,
            "original_state": None,
            "target": None,
            "rollback_possible": False
        }
    
    def _check_if_elevated(self) -> bool:
        """
        Check if the current process has administrative privileges
        
        Returns:
            bool: True if elevated, False otherwise
        """
        if platform.system() == 'Windows':
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            # For non-Windows systems, we'll take a platform-specific approach
            try:
                if platform.system() == 'Darwin':  # macOS
                    # On macOS, try to check using the id command
                    result = subprocess.run(['id', '-u'], capture_output=True, text=True)
                    return result.stdout.strip() == '0'  # UID 0 is root
                elif platform.system() == 'Linux':
                    # On Linux, check effective user ID through subprocess
                    # to avoid linter issues with os.geteuid
                    result = subprocess.run(['id', '-u'], capture_output=True, text=True)
                    return result.stdout.strip() == '0'  # UID 0 is root
                else:
                    # Unknown platform, assume not elevated
                    return False
            except Exception:
                # If any error occurs, assume not elevated
                return False
    
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
    
    def _elevation_request_callback(self, operation: str, details: str) -> bool:
        """
        Request permission to elevate privileges
        
        Args:
            operation: Operation description
            details: Additional details about the operation
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Create root window if needed
        self._create_root_if_needed()
        
        # Show elevation request dialog
        response = messagebox.askyesno(
            title="Administrator Permission Request",
            message=f"The following operation requires administrator privileges:\n\n{operation}",
            detail=f"{details}\n\nDo you want to continue with elevated privileges?",
            icon="warning"
        )
        
        if response:
            logger.info(f"User granted elevation for operation: {operation}")
            return True
        else:
            logger.info(f"User denied elevation for operation: {operation}")
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
    
    def elevate_privileges(self, operation: str = "Perform privileged operation") -> bool:
        """
        Attempt to elevate the process privileges (for Windows)
        
        Args:
            operation: Description of the operation requiring elevation
            
        Returns:
            bool: True if successfully elevated, False otherwise
        """
        if self.is_elevated:
            logger.info("Process already has elevated privileges")
            return True
            
        if platform.system() != 'Windows':
            logger.warning("Privilege elevation only supported on Windows")
            return False
            
        # Request user permission for elevation
        if not self._elevation_request_callback(
            operation, 
            "This will restart the application with Administrator privileges."
        ):
            return False
            
        try:
            # Create a temporary batch file to elevate the current process
            with tempfile.NamedTemporaryFile(suffix='.bat', delete=False) as f:
                batch_path = f.name
                
            with open(batch_path, 'w') as f:
                script_path = sys.argv[0]
                args = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
                
                f.write('@echo off\n')
                f.write(f'powershell -Command "Start-Process -FilePath \'{sys.executable}\' ')
                f.write(f'-ArgumentList \'{script_path} {args}\' -Verb RunAs"\n')
                f.write('del "%~f0"\n')  # Self-delete the batch file
                
            # Execute the batch file
            subprocess.Popen(batch_path, shell=True)
            
            # Exit the current non-elevated process
            logger.info("Restarting with elevated privileges...")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Failed to elevate privileges: {e}")
            return False
            
        return True  # Should never reach here
    
    def execute_command(self, command: str, cwd: Optional[Union[str, Path]] = None, shell: bool = True, 
                       capture_output: bool = True, timeout: Optional[int] = None, 
                       context: Optional[Dict[str, Any]] = None,
                       background: bool = False,
                       callback: Optional[Callable] = None) -> Tuple[int, str, str]:
        """
        Execute a system command
        
        Args:
            command: Command to execute
            cwd: Current working directory
            shell: Whether to use shell
            capture_output: Whether to capture output
            timeout: Timeout in seconds
            context: Additional context information
            background: Run in background
            callback: Callback function when background task completes
            
        Returns:
            Tuple: (exit_code, stdout, stderr)
        """
        # Use workspace path as default working directory
        if cwd is None:
            cwd = self.workspace_path
        
        # Check if safe command or get permission
        if not self._is_safe_command(command):
            # For permission checking, we need to handle command differently
            # Extract the executable part for permission checking
            command_parts = command.split(None, 1)
            executable = command_parts[0] if command_parts else command
            
            if not self.permission_manager.has_permission(executable, "execute"):
                if not self._permission_request_callback(command, "execute"):
                    logger.warning(f"Permission denied for command: {command}")
                    return 1, "", "Permission denied"
                # Grant permission for this command
                self.permission_manager.grant_permission(executable, ["execute"])
        
        # Log command execution
        logger.info(f"Executing command: {command}")
        
        # For background execution
        if background:
            process_id = id(command)
            
            def background_task():
                try:
                    result = subprocess.run(
                        command,
                        cwd=cwd,
                        shell=shell,
                        capture_output=capture_output,
                        text=True,
                        timeout=timeout
                    )
                    
                    # Store result
                    with self.process_lock:
                        self.running_processes[process_id] = {
                            "returncode": result.returncode,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "completed": True
                        }
                    
                    # Call callback if provided
                    if callback:
                        callback(result.returncode, result.stdout, result.stderr)
                        
                except subprocess.TimeoutExpired:
                    with self.process_lock:
                        self.running_processes[process_id] = {
                            "returncode": 1,
                            "stdout": "",
                            "stderr": "Command timed out",
                            "completed": True
                        }
                except Exception as e:
                    with self.process_lock:
                        self.running_processes[process_id] = {
                            "returncode": 1,
                            "stdout": "",
                            "stderr": f"Error: {str(e)}",
                            "completed": True
                        }
            
            # Start background thread
            thread = threading.Thread(target=background_task)
            thread.daemon = True
            thread.start()
            
            # Store process information
            with self.process_lock:
                self.running_processes[process_id] = {
                    "thread": thread,
                    "command": command,
                    "cwd": cwd,
                    "completed": False
                }
            
            return 0, f"Command started in background. Process ID: {process_id}", ""
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            # Save last command for potential rollback
            self.last_operation = {
                "type": "command",
                "original_state": None,  # Not applicable for general commands
                "target": command,
                "rollback_possible": False
            }
            
            # Return results
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return 1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return 1, "", f"Error: {str(e)}"
    
    def get_process_status(self, process_id: int) -> Dict[str, Any]:
        """
        Get status of a background process
        
        Args:
            process_id: Process ID
            
        Returns:
            Dict: Process status information
        """
        with self.process_lock:
            if process_id not in self.running_processes:
                return {
                    "exists": False,
                    "message": "Process not found"
                }
            
            process = self.running_processes[process_id]
            
            if not process["completed"]:
                return {
                    "exists": True,
                    "completed": False,
                    "command": process["command"]
                }
            else:
                return {
                    "exists": True,
                    "completed": True,
                    "command": process["command"] if "command" in process else "Unknown",
                    "returncode": process["returncode"],
                    "stdout": process["stdout"],
                    "stderr": process["stderr"]
                }
    
    def kill_process(self, process_id: int) -> bool:
        """
        Kill a running background process
        
        Args:
            process_id: Process ID
            
        Returns:
            bool: True if successfully killed, False otherwise
        """
        with self.process_lock:
            if process_id not in self.running_processes:
                return False
            
            process = self.running_processes[process_id]
            
            if process["completed"]:
                return True  # Already completed
            
            # Cannot directly kill a thread in Python
            # Mark as completed with an error
            process["completed"] = True
            process["returncode"] = 1
            process["stdout"] = ""
            process["stderr"] = "Process was killed"
            
            return True
    
    def execute_python_script(self, 
                             script_path: Union[str, Path],
                             args: Optional[List[str]] = None,
                             cwd: Optional[Union[str, Path]] = None,
                             background: bool = False) -> Tuple[int, str, str]:
        """
        Execute a Python script
        
        Args:
            script_path: Path to script
            args: Command line arguments
            cwd: Working directory
            background: Run in background
            
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
        
        if background:
            # Convert command args to string for background execution
            command_str = f'"{python_exe}" "{script_path_obj}"'
            if args:
                command_str += ' ' + ' '.join([f'"{arg}"' for arg in args])
            
            return self.execute_command(
                command=command_str,
                cwd=cwd if cwd else self.workspace_path,
                background=True
            )
        
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
            
            # Save last operation for potential rollback
            self.last_operation = {
                "type": "python_script",
                "original_state": None,  # Not applicable for scripts
                "target": str(script_path_obj),
                "rollback_possible": False
            }
            
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
        # Get pip executable (same directory as Python)
        python_dir = Path(sys.executable).parent
        pip_exe = python_dir / "pip.exe" if platform.system() == "Windows" else python_dir / "pip"
        
        if not pip_exe.exists():
            pip_exe = python_dir / "pip3.exe" if platform.system() == "Windows" else python_dir / "pip3"
            
        if not pip_exe.exists():
            # Fall back to using Python's pip module
            pip_exe = [sys.executable, "-m", "pip"]
        else:
            pip_exe = [str(pip_exe)]
        
        # Build command
        command = pip_exe + ["install"]
        
        if upgrade:
            command.append("--upgrade")
            
        if user:
            command.append("--user")
            
        # Add package name
        command.append(package_name)
        
        # Log what we're about to do
        logger.info(f"Installing package: {package_name}")
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=False,  # Set to False for security
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Save last operation for potential rollback
            self.last_operation = {
                "type": "package_install",
                "original_state": None,  # Not applicable for package install
                "target": package_name,
                "rollback_possible": False
            }
            
            # Return results
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Package installation timed out: {package_name}")
            return 1, "", f"Package installation timed out: {package_name}"
        except Exception as e:
            logger.error(f"Error installing package {package_name}: {e}")
            return 1, "", f"Error: {str(e)}"
    
    def modify_registry(self, key_path: str, value_name: str, value_data: Any, value_type: str) -> bool:
        """
        Modify Windows registry
        
        Args:
            key_path: Registry key path
            value_name: Name of the value to set
            value_data: Data to set
            value_type: Registry value type (REG_SZ, REG_DWORD, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if platform.system() != "Windows":
            logger.error("Registry modification is only available on Windows")
            return False
            
        # Request permission
        if not self._permission_request_callback(
            f"Modify registry key: {key_path}\\{value_name}", 
            "registry_write"
        ):
            return False
            
        # Map value types to winreg constants
        type_map = {
            "REG_SZ": winreg.REG_SZ,
            "REG_DWORD": winreg.REG_DWORD,
            "REG_BINARY": winreg.REG_BINARY,
            "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
            "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ
        }
        
        if value_type not in type_map:
            logger.error(f"Unsupported registry value type: {value_type}")
            return False
            
        # Parse registry key path
        parts = key_path.split('\\', 1)
        if len(parts) != 2:
            logger.error(f"Invalid registry key path: {key_path}")
            return False
            
        hkey_map = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }
        
        if parts[0] not in hkey_map:
            logger.error(f"Unsupported registry hive: {parts[0]}")
            return False
            
        hkey = hkey_map[parts[0]]
        subkey = parts[1]
        
        # Backup current value for potential rollback
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            try:
                old_value, old_type = winreg.QueryValueEx(key, value_name)
                backup_exists = True
            except WindowsError:
                backup_exists = False
            winreg.CloseKey(key)
        except WindowsError:
            backup_exists = False
            
        if backup_exists:
            self.last_operation = {
                "type": "registry",
                "original_state": {
                    "key_path": key_path,
                    "value_name": value_name,
                    "value_data": old_value,
                    "value_type": old_type
                },
                "target": f"{key_path}\\{value_name}",
                "rollback_possible": True
            }
            
        # Modify registry
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, type_map[value_type], value_data)
            winreg.CloseKey(key)
            logger.info(f"Registry value modified: {key_path}\\{value_name}")
            return True
        except WindowsError as e:
            logger.error(f"Failed to modify registry: {e}")
            return False
    
    def manage_service(self, service_name: str, action: str) -> Tuple[bool, str]:
        """
        Manage Windows services
        
        Args:
            service_name: Name of the service
            action: Action to perform (start, stop, restart, query)
            
        Returns:
            Tuple[bool, str]: (success, status/error message)
        """
        if platform.system() != "Windows":
            logger.error("Service management is only available on Windows")
            return False, "Service management is only available on Windows"
            
        # Check if action requires elevation
        requires_elevation = action in ["start", "stop", "restart"]
            
        # Request permission
        if not self._permission_request_callback(
            f"{action.capitalize()} service: {service_name}", 
            "service_management"
        ):
            return False, "Permission denied"
            
        # Check for elevation if needed
        if requires_elevation and not self.is_elevated:
            # Offer to elevate
            if self._elevation_request_callback(
                f"{action.capitalize()} service: {service_name}",
                "This operation requires administrative privileges."
            ):
                if not self.elevate_privileges(f"{action.capitalize()} service: {service_name}"):
                    return False, "Failed to elevate privileges"
            else:
                return False, "Elevation required but denied"
                
        # Build command based on action
        if action == "query":
            command = f'sc query "{service_name}"'
        elif action == "start":
            command = f'sc start "{service_name}"'
        elif action == "stop":
            command = f'sc stop "{service_name}"'
        elif action == "restart":
            command = f'sc stop "{service_name}" && sc start "{service_name}"'
        else:
            return False, f"Unsupported service action: {action}"
            
        # Execute command
        exit_code, stdout, stderr = self.execute_command(command)
        
        if exit_code == 0:
            logger.info(f"Service {action} successful: {service_name}")
            return True, stdout
        else:
            logger.error(f"Service {action} failed: {service_name}")
            return False, stderr if stderr else "Service operation failed"
    
    def rollback_last_operation(self) -> bool:
        """
        Attempt to rollback the last operation
        
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        if not self.last_operation["rollback_possible"]:
            logger.warning("No valid operation to rollback")
            return False
            
        op_type = self.last_operation["type"]
        
        if op_type == "registry":
            # Rollback registry change
            orig = self.last_operation["original_state"]
            return self.modify_registry(
                orig["key_path"],
                orig["value_name"],
                orig["value_data"],
                orig["value_type"]
            )
        # Add other operation types as needed
            
        return False
    
    def open_file(self, file_path: Union[str, Path]) -> bool:
        """
        Open a file with the default application
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path).resolve()
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Request permission
        if not self.permission_manager.has_permission(file_path, "execute"):
            if not self._permission_request_callback(f"Open file: {file_path}", "execute"):
                logger.warning(f"Permission denied to open file: {file_path}")
                return False
            self.permission_manager.grant_permission(file_path, ["execute"])
        
        try:
            if platform.system() == "Windows":
                os.startfile(str(file_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", str(file_path)], check=True)
                
            logger.info(f"File opened: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    def create_scheduled_task(self, name: str, command: str, schedule: str) -> bool:
        """
        Create a scheduled task (Windows only)
        
        Args:
            name: Task name
            command: Command to execute
            schedule: Schedule expression (e.g. "DAILY", "ONCE /ST 12:00")
            
        Returns:
            bool: True if successful, False otherwise
        """
        if platform.system() != "Windows":
            logger.error("Scheduled tasks are only available on Windows")
            return False
            
        # Request permission
        if not self._permission_request_callback(
            f"Create scheduled task: {name}", 
            "task_scheduling"
        ):
            return False
            
        # Build command
        schtasks_cmd = f'schtasks /Create /TN "{name}" /TR "{command}" /SC {schedule} /F'
        
        # Execute command
        exit_code, stdout, stderr = self.execute_command(schtasks_cmd)
        
        if exit_code == 0:
            logger.info(f"Scheduled task created: {name}")
            return True
        else:
            logger.error(f"Failed to create scheduled task: {stderr}")
            return False

    def create_firewall_rule(self, name: str, action: str, direction: str, 
                           protocol: str = "TCP", port: Optional[int] = None) -> bool:
        """
        Create a Windows firewall rule
        
        Args:
            name: Rule name
            action: "allow" or "block"
            direction: "in" or "out"
            protocol: Protocol (TCP, UDP, etc.)
            port: Port number (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if platform.system() != "Windows":
            logger.error("Firewall management is only available on Windows")
            return False
            
        # Request permission
        if not self._permission_request_callback(
            f"Create firewall rule: {name}", 
            "firewall_management"
        ):
            return False
            
        # Check for elevation
        if not self.is_elevated:
            if self._elevation_request_callback(
                f"Create firewall rule: {name}",
                "This operation requires administrative privileges."
            ):
                if not self.elevate_privileges(f"Create firewall rule: {name}"):
                    return False
            else:
                return False
                
        # Build command
        action_param = "allow" if action.lower() == "allow" else "block"
        dir_param = "in" if direction.lower() == "in" else "out"
        
        netsh_cmd = f'netsh advfirewall firewall add rule name="{name}" dir={dir_param} action={action_param} protocol={protocol}'
        
        if port is not None:
            netsh_cmd += f' localport={port}'
        
        # Execute command
        exit_code, stdout, stderr = self.execute_command(netsh_cmd)
        
        if exit_code == 0:
            logger.info(f"Firewall rule created: {name}")
            return True
        else:
            logger.error(f"Failed to create firewall rule: {stderr}")
            return False


# Global instance for convenience functions
_system_manager = None

def get_system_manager():
    """Get or create a global system manager instance"""
    global _system_manager
    if _system_manager is None:
        _system_manager = SystemOperationManager()
    return _system_manager

def execute_command(command: str, 
                   cwd: Optional[Union[str, Path]] = None,
                   shell: bool = True,
                   capture_output: bool = True,
                   timeout: Optional[int] = None,
                   context: Optional[Dict[str, Any]] = None) -> Tuple[int, str, str]:
    """Convenience function to execute a command"""
    return get_system_manager().execute_command(
        command, cwd, shell, capture_output, timeout, context
    )

def execute_python_script(script_path: Union[str, Path],
                         args: Optional[List[str]] = None,
                         cwd: Optional[Union[str, Path]] = None) -> Tuple[int, str, str]:
    """Convenience function to execute a Python script"""
    return get_system_manager().execute_python_script(script_path, args, cwd)

def install_package(package_name: str,
                   upgrade: bool = False,
                   user: bool = True) -> Tuple[int, str, str]:
    """Convenience function to install a Python package"""
    return get_system_manager().install_package(package_name, upgrade, user)

def open_file(file_path: Union[str, Path]) -> bool:
    """Convenience function to open a file"""
    return get_system_manager().open_file(file_path)

def elevate_privileges(operation: str = "Perform privileged operation") -> bool:
    """Convenience function to elevate privileges"""
    return get_system_manager().elevate_privileges(operation)

def modify_registry(key_path: str, value_name: str, value_data: Any, value_type: str) -> bool:
    """Convenience function to modify registry"""
    return get_system_manager().modify_registry(key_path, value_name, value_data, value_type)

def manage_service(service_name: str, action: str) -> Tuple[bool, str]:
    """Convenience function to manage services"""
    return get_system_manager().manage_service(service_name, action)

def create_scheduled_task(name: str, command: str, schedule: str) -> bool:
    """Convenience function to create a scheduled task"""
    return get_system_manager().create_scheduled_task(name, command, schedule)

def create_firewall_rule(name: str, action: str, direction: str, protocol: str = "TCP", port: Optional[int] = None) -> bool:
    """Convenience function to create a firewall rule"""
    return get_system_manager().create_firewall_rule(name, action, direction, protocol, port) 