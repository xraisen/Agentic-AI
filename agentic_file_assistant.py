#!/usr/bin/env python3
"""
Agentic AI File Assistant

A simple command-line interface for interacting with the Agentic AI file operations capabilities.
This assistant can create, read, write, move, copy, and delete files, as well as execute commands.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import core components
from src.core.file_operations import FileOperationManager
from src.core.system_operations import SystemOperationManager
from src.core.conversation_manager import ConversationManager


def create_text_file(file_manager, path, content=None):
    """Create a text file with optional content."""
    if content is None:
        content = input("Enter file content (press Ctrl+D or Ctrl+Z on a new line to finish):\n")
    
    success = file_manager.write_file(path, content)
    if success:
        print(f"Successfully created file: {path}")
    else:
        print(f"Failed to create file: {path}")


def read_text_file(file_manager, path):
    """Read and display the contents of a text file."""
    content = file_manager.read_file(path)
    if content:
        print(f"\nContents of {path}:")
        print("=" * 40)
        print(content)
        print("=" * 40)
    else:
        print(f"Failed to read file: {path}")


def write_text_file(file_manager, path, content=None, append=False):
    """Write or append to a text file."""
    if content is None:
        content = input("Enter file content (press Ctrl+D or Ctrl+Z on a new line to finish):\n")
    
    if append:
        success = file_manager.append_file(path, content)
        action = "appended to"
    else:
        success = file_manager.write_file(path, content)
        action = "written to"
    
    if success:
        print(f"Successfully {action} file: {path}")
    else:
        print(f"Failed to write to file: {path}")


def list_directory(file_manager, path="."):
    """List the contents of a directory."""
    contents = file_manager.list_directory(path)
    if contents:
        print(f"\nContents of directory: {path}")
        print("=" * 40)
        for item in contents:
            info = file_manager.get_file_info(item)
            if info:
                type_str = "File" if info["is_file"] else "Directory"
                size = info["size"] if "size" in info else 0
                print(f"{item.name} ({type_str}, {size} bytes)")
        print("=" * 40)
    else:
        print(f"Failed to list directory: {path}")


def copy_file(file_manager, source, destination):
    """Copy a file from source to destination."""
    success = file_manager.copy_file(source, destination)
    if success:
        print(f"Successfully copied {source} to {destination}")
    else:
        print(f"Failed to copy {source} to {destination}")


def move_file(file_manager, source, destination):
    """Move a file from source to destination."""
    success = file_manager.move_file(source, destination)
    if success:
        print(f"Successfully moved {source} to {destination}")
    else:
        print(f"Failed to move {source} to {destination}")


def delete_file(file_manager, path):
    """Delete a file."""
    success = file_manager.delete_file(path)
    if success:
        print(f"Successfully deleted file: {path}")
    else:
        print(f"Failed to delete file: {path}")


def create_directory(file_manager, path):
    """Create a directory."""
    success = file_manager.create_directory(path)
    if success:
        print(f"Successfully created directory: {path}")
    else:
        print(f"Failed to create directory: {path}")


def delete_directory(file_manager, path, recursive=False):
    """Delete a directory."""
    success = file_manager.delete_directory(path, recursive)
    if success:
        print(f"Successfully deleted directory: {path}")
    else:
        print(f"Failed to delete directory: {path}")


def execute_command(system_manager, command):
    """Execute a system command."""
    exit_code, stdout, stderr = system_manager.execute_command(command)
    print(f"\nCommand: {command}")
    print(f"Exit code: {exit_code}")
    
    if stdout:
        print("\nStandard output:")
        print("-" * 40)
        print(stdout)
    
    if stderr:
        print("\nStandard error:")
        print("-" * 40)
        print(stderr)


def main():
    """Main function for the file assistant."""
    parser = argparse.ArgumentParser(description="Agentic AI File Assistant")
    parser.add_argument("--workspace", "-w", type=str, default=str(project_root),
                       help="Workspace directory path")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create file
    create_parser = subparsers.add_parser("create", help="Create a text file")
    create_parser.add_argument("path", help="Path to the file")
    create_parser.add_argument("--content", "-c", help="File content (if not provided, will prompt)")
    
    # Read file
    read_parser = subparsers.add_parser("read", help="Read a text file")
    read_parser.add_argument("path", help="Path to the file")
    
    # Write file
    write_parser = subparsers.add_parser("write", help="Write to a text file")
    write_parser.add_argument("path", help="Path to the file")
    write_parser.add_argument("--content", "-c", help="File content (if not provided, will prompt)")
    write_parser.add_argument("--append", "-a", action="store_true", help="Append to the file")
    
    # List directory
    list_parser = subparsers.add_parser("list", help="List directory contents")
    list_parser.add_argument("path", nargs="?", default=".", help="Path to the directory")
    
    # Copy file
    copy_parser = subparsers.add_parser("copy", help="Copy a file")
    copy_parser.add_argument("source", help="Source file")
    copy_parser.add_argument("destination", help="Destination file")
    
    # Move file
    move_parser = subparsers.add_parser("move", help="Move a file")
    move_parser.add_argument("source", help="Source file")
    move_parser.add_argument("destination", help="Destination file")
    
    # Delete file
    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("path", help="Path to the file")
    
    # Create directory
    mkdir_parser = subparsers.add_parser("mkdir", help="Create a directory")
    mkdir_parser.add_argument("path", help="Path to the directory")
    
    # Delete directory
    rmdir_parser = subparsers.add_parser("rmdir", help="Delete a directory")
    rmdir_parser.add_argument("path", help="Path to the directory")
    rmdir_parser.add_argument("--recursive", "-r", action="store_true", help="Delete recursively")
    
    # Execute command
    exec_parser = subparsers.add_parser("exec", help="Execute a command")
    exec_parser.add_argument("command", help="Command to execute")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Initialize managers
    file_manager = FileOperationManager(workspace_path=args.workspace)
    system_manager = SystemOperationManager(workspace_path=args.workspace)
    
    print(f"Using workspace: {args.workspace}")
    
    # Process command
    if args.command == "create":
        create_text_file(file_manager, args.path, args.content)
    elif args.command == "read":
        read_text_file(file_manager, args.path)
    elif args.command == "write":
        write_text_file(file_manager, args.path, args.content, args.append)
    elif args.command == "list":
        list_directory(file_manager, args.path)
    elif args.command == "copy":
        copy_file(file_manager, args.source, args.destination)
    elif args.command == "move":
        move_file(file_manager, args.source, args.destination)
    elif args.command == "delete":
        delete_file(file_manager, args.path)
    elif args.command == "mkdir":
        create_directory(file_manager, args.path)
    elif args.command == "rmdir":
        delete_directory(file_manager, args.path, args.recursive)
    elif args.command == "exec":
        execute_command(system_manager, args.command)
    elif args.command == "interactive":
        # Start interactive mode
        interactive_mode(file_manager, system_manager)
    else:
        parser.print_help()


def interactive_mode(file_manager, system_manager):
    """Run in interactive mode."""
    print("\nAgentic AI File Assistant - Interactive Mode")
    print("Type 'help' for a list of commands, 'exit' to quit")
    
    while True:
        try:
            command = input("\n> ").strip()
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "exit" or cmd == "quit":
                break
            elif cmd == "help":
                print_help()
            elif cmd == "create" and len(parts) >= 2:
                create_text_file(file_manager, parts[1])
            elif cmd == "read" and len(parts) >= 2:
                read_text_file(file_manager, parts[1])
            elif cmd == "write" and len(parts) >= 2:
                write_text_file(file_manager, parts[1])
            elif cmd == "append" and len(parts) >= 2:
                write_text_file(file_manager, parts[1], append=True)
            elif cmd == "list":
                path = parts[1] if len(parts) >= 2 else "."
                list_directory(file_manager, path)
            elif cmd == "copy" and len(parts) >= 3:
                copy_file(file_manager, parts[1], parts[2])
            elif cmd == "move" and len(parts) >= 3:
                move_file(file_manager, parts[1], parts[2])
            elif cmd == "delete" and len(parts) >= 2:
                delete_file(file_manager, parts[1])
            elif cmd == "mkdir" and len(parts) >= 2:
                create_directory(file_manager, parts[1])
            elif cmd == "rmdir" and len(parts) >= 2:
                recursive = "-r" in parts or "--recursive" in parts
                path = parts[1]
                delete_directory(file_manager, path, recursive)
            elif cmd == "exec" and len(parts) >= 2:
                execute_command(system_manager, command[len("exec "):])
            else:
                print("Unknown command or missing arguments. Type 'help' for a list of commands.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"Error: {str(e)}")


def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print("  create <path>        - Create a text file")
    print("  read <path>          - Read a text file")
    print("  write <path>         - Write to a text file")
    print("  append <path>        - Append to a text file")
    print("  list [path]          - List directory contents (default: current directory)")
    print("  copy <src> <dst>     - Copy a file")
    print("  move <src> <dst>     - Move a file")
    print("  delete <path>        - Delete a file")
    print("  mkdir <path>         - Create a directory")
    print("  rmdir <path> [-r]    - Delete a directory (-r for recursive)")
    print("  exec <command>       - Execute a command")
    print("  help                 - Show this help message")
    print("  exit                 - Exit the program")


if __name__ == "__main__":
    main() 