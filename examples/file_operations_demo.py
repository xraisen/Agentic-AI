#!/usr/bin/env python3
"""
Agentic AI - File Operations Demo

This script demonstrates the file operations capabilities of Agentic AI.
It shows how to use the file system interface and permission management
system to perform various file operations.
"""

import os
import sys
from pathlib import Path
import argparse

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.file_operations import FileOperationManager
from src.core.system_operations import SystemOperationManager
from src.core.conversation_manager import ConversationManager
from src.core.agentic_core import AgenticCore


def create_demo_files(file_manager, base_dir):
    """Create some demo files for testing."""
    print("\n=== Creating Demo Files ===")
    
    # Create demo directory
    demo_dir = os.path.join(base_dir, "demo_files")
    if not file_manager.directory_exists(demo_dir):
        file_manager.create_directory(demo_dir)
        print(f"Created directory: {demo_dir}")
    
    # Create a text file
    text_file = os.path.join(demo_dir, "hello.txt")
    content = "Hello, world!\nThis is a demo file created by Agentic AI."
    file_manager.write_file(text_file, content)
    print(f"Created file: {text_file}")
    
    # Create a JSON file
    json_file = os.path.join(demo_dir, "config.json")
    json_content = '{\n  "name": "Agentic AI",\n  "version": "1.0.0",\n  "description": "AI with file operations capabilities"\n}'
    file_manager.write_file(json_file, json_content)
    print(f"Created file: {json_file}")
    
    # Create a Python file
    py_file = os.path.join(demo_dir, "hello.py")
    py_content = 'print("Hello from Agentic AI!")\nprint("This script was created by the AI.")\n'
    file_manager.write_file(py_file, py_content)
    print(f"Created file: {py_file}")
    
    return demo_dir


def demonstrate_file_operations(file_manager, demo_dir):
    """Demonstrate various file operations."""
    print("\n=== File Operations Demo ===")
    
    # List directory contents
    print("\n1. Listing directory contents:")
    contents = file_manager.list_directory(demo_dir)
    for item in contents:
        info = file_manager.get_file_info(item)
        if info:
            size = info["size"]
            type_str = "File" if info["is_file"] else "Directory"
            print(f"- {item.name} ({type_str}, {size} bytes)")
    
    # Read a file
    print("\n2. Reading a file:")
    text_file = os.path.join(demo_dir, "hello.txt")
    content = file_manager.read_file(text_file)
    print(f"Content of {text_file}:")
    print(f"\"\"\"\n{content}\n\"\"\"")
    
    # Append to a file
    print("\n3. Appending to a file:")
    append_content = "\nThis line was appended by the demo."
    file_manager.append_file(text_file, append_content)
    print(f"Appended to {text_file}")
    
    # Read the file again to see changes
    content = file_manager.read_file(text_file)
    print(f"Updated content of {text_file}:")
    print(f"\"\"\"\n{content}\n\"\"\"")
    
    # Copy a file
    print("\n4. Copying a file:")
    copy_file = os.path.join(demo_dir, "hello_copy.txt")
    file_manager.copy_file(text_file, copy_file)
    print(f"Copied {text_file} to {copy_file}")
    
    # Move a file
    print("\n5. Moving a file:")
    moved_file = os.path.join(demo_dir, "hello_moved.txt")
    file_manager.copy_file(text_file, moved_file)  # Create a file to move
    renamed_file = os.path.join(demo_dir, "hello_renamed.txt")
    file_manager.move_file(moved_file, renamed_file)
    print(f"Moved {moved_file} to {renamed_file}")
    
    # Delete a file
    print("\n6. Deleting a file:")
    file_manager.delete_file(copy_file)
    print(f"Deleted {copy_file}")
    
    # Create a subdirectory
    print("\n7. Creating a subdirectory:")
    subdir = os.path.join(demo_dir, "subdir")
    file_manager.create_directory(subdir)
    print(f"Created directory: {subdir}")
    
    # Create a file in the subdirectory
    subfile = os.path.join(subdir, "subfile.txt")
    file_manager.write_file(subfile, "This is a file in a subdirectory.")
    print(f"Created file: {subfile}")
    
    # List directory contents again
    print("\n8. Updated directory contents:")
    contents = file_manager.list_directory(demo_dir)
    for item in contents:
        info = file_manager.get_file_info(item)
        if info:
            size = info["size"]
            type_str = "File" if info["is_file"] else "Directory"
            print(f"- {item.name} ({type_str}, {size} bytes)")


def demonstrate_system_operations(system_manager, demo_dir):
    """Demonstrate system operations."""
    print("\n=== System Operations Demo ===")
    
    # Execute a simple command
    print("\n1. Executing a simple command:")
    exit_code, stdout, stderr = system_manager.execute_command("echo Hello from Agentic AI")
    print(f"Exit code: {exit_code}")
    print(f"Output: {stdout}")
    
    # List directory contents using system command
    print("\n2. Listing directory contents using system command:")
    if os.name == "nt":  # Windows
        exit_code, stdout, stderr = system_manager.execute_command(f"dir \"{demo_dir}\"")
    else:  # Unix-like
        exit_code, stdout, stderr = system_manager.execute_command(f"ls -la \"{demo_dir}\"")
    print(f"Exit code: {exit_code}")
    print(f"Output: {stdout}")
    
    # Execute a Python script
    print("\n3. Executing a Python script:")
    script_path = os.path.join(demo_dir, "hello.py")
    exit_code, stdout, stderr = system_manager.execute_python_script(script_path)
    print(f"Exit code: {exit_code}")
    print(f"Output: {stdout}")


def demonstrate_conversation_history(conversation_manager):
    """Demonstrate conversation history logging and retrieval."""
    print("\n=== Conversation History Demo ===")
    
    # Start a new conversation
    print("\n1. Starting a new conversation:")
    conversation_id = conversation_manager.start_conversation("Demo Conversation")
    print(f"Created conversation with ID: {conversation_id}")
    
    # Add some messages
    print("\n2. Adding messages to the conversation:")
    conversation_manager.add_user_message("Hello, AI assistant!")
    print("Added user message: 'Hello, AI assistant!'")
    
    conversation_manager.add_assistant_message("Hello! How can I help you today?")
    print("Added assistant message: 'Hello! How can I help you today?'")
    
    conversation_manager.add_user_message("Can you help me understand how file operations work in Agentic AI?")
    print("Added user message: 'Can you help me understand how file operations work in Agentic AI?'")
    
    conversation_manager.add_assistant_message("Of course! Agentic AI provides a secure abstraction layer for file operations...")
    print("Added assistant message: 'Of course! Agentic AI provides a secure abstraction layer for file operations...'")
    
    # Get conversation history
    print("\n3. Retrieving conversation history:")
    history = conversation_manager.get_conversation_history(conversation_id)
    if history:
        for i, message in enumerate(history):
            print(f"[{i+1}] {message['role']}: {message['content'][:50]}...")
    
    # Generate a summary
    print("\n4. Generating conversation summary:")
    summary = conversation_manager.summarize_conversation(conversation_id)
    print(summary)
    
    # Export the conversation
    print("\n5. Exporting conversation to file:")
    output_file = "exports/demo_conversation.md"
    conversation_manager.export_conversation_to_file(
        conversation_id=conversation_id,
        output_file=output_file,
        format="markdown"
    )
    print(f"Exported conversation to {output_file}")


def main():
    """Main function for the demo application."""
    parser = argparse.ArgumentParser(description="Agentic AI File Operations Demo")
    parser.add_argument("--workspace", "-w", type=str, default=str(project_root),
                      help="Workspace directory path")
    args = parser.parse_args()
    
    workspace_path = args.workspace
    
    print(f"Using workspace: {workspace_path}")
    
    # Initialize managers
    file_manager = FileOperationManager(workspace_path=workspace_path)
    system_manager = SystemOperationManager(workspace_path=workspace_path)
    conversation_manager = ConversationManager(db_path="logs/conversations.db")
    
    # Create exports directory if it doesn't exist
    exports_dir = os.path.join(workspace_path, "exports")
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    
    try:
        # Create demo files
        demo_dir = create_demo_files(file_manager, workspace_path)
        
        # Demonstrate file operations
        demonstrate_file_operations(file_manager, demo_dir)
        
        # Demonstrate system operations
        demonstrate_system_operations(system_manager, demo_dir)
        
        # Demonstrate conversation history
        demonstrate_conversation_history(conversation_manager)
        
        print("\nDemo completed successfully!")
    except Exception as e:
        print(f"Error during demo: {str(e)}")
        import traceback
        print(traceback.format_exc())
    

if __name__ == "__main__":
    main() 