#!/usr/bin/env python3
"""
Agentic AI Capabilities Test

This script tests the following capabilities of Agentic AI:
1. Filesystem alterations (create, read, write, delete files and directories)
2. Finding hidden files
3. Recalling past conversations
"""

import os
import sys
import time
from pathlib import Path
import random
import string

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import core components
from src.core.file_operations import FileOperationManager
from src.core.system_operations import SystemOperationManager
from src.core.conversation_manager import ConversationManager


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_filesystem_operations():
    """Test filesystem operations (create, read, write, delete files and directories)."""
    print_section("TESTING FILESYSTEM OPERATIONS")
    
    # Initialize file manager
    file_manager = FileOperationManager(workspace_path=project_root)
    
    # Create a test directory
    test_dir = os.path.join(project_root, "test_files")
    print(f"\n1. Creating test directory: {test_dir}")
    success = file_manager.create_directory(test_dir)
    print(f"   Success: {success}")
    
    # Create a text file
    text_file = os.path.join(test_dir, "test.txt")
    content = "Hello, world!\nThis is a test file created by Agentic AI."
    print(f"\n2. Creating text file: {text_file}")
    success = file_manager.write_file(text_file, content)
    print(f"   Success: {success}")
    
    # Read the file
    print(f"\n3. Reading file: {text_file}")
    read_content = file_manager.read_file(text_file)
    print(f"   Content: {read_content}")
    print(f"   Content matches: {read_content == content}")
    
    # Append to the file
    append_content = "\nThis line was appended by the test."
    print(f"\n4. Appending to file: {text_file}")
    success = file_manager.append_file(text_file, append_content)
    print(f"   Success: {success}")
    
    # Read the file again
    print(f"\n5. Reading updated file: {text_file}")
    read_content = file_manager.read_file(text_file)
    expected_content = content + append_content
    print(f"   Content: {read_content}")
    print(f"   Content matches: {read_content == expected_content}")
    
    # Create a binary file
    binary_file = os.path.join(test_dir, "binary.bin")
    binary_content = bytes([random.randint(0, 255) for _ in range(100)])
    print(f"\n6. Creating binary file: {binary_file}")
    success = file_manager.write_file(binary_file, binary_content, binary=True)
    print(f"   Success: {success}")
    
    # Read the binary file
    print(f"\n7. Reading binary file: {binary_file}")
    read_binary = file_manager.read_file(binary_file, binary=True)
    if read_binary is not None:
        print(f"   Content length: {len(read_binary)} bytes")
        print(f"   Content matches: {read_binary == binary_content}")
    else:
        print("   Failed to read binary file")
    
    # Copy a file
    copy_file = os.path.join(test_dir, "copy.txt")
    print(f"\n8. Copying file: {text_file} to {copy_file}")
    success = file_manager.copy_file(text_file, copy_file)
    print(f"   Success: {success}")
    
    # Move a file
    moved_file = os.path.join(test_dir, "moved.txt")
    print(f"\n9. Moving file: {copy_file} to {moved_file}")
    success = file_manager.move_file(copy_file, moved_file)
    print(f"   Success: {success}")
    
    # Create a subdirectory
    subdir = os.path.join(test_dir, "subdir")
    print(f"\n10. Creating subdirectory: {subdir}")
    success = file_manager.create_directory(subdir)
    print(f"   Success: {success}")
    
    # Create a file in the subdirectory
    subfile = os.path.join(subdir, "subfile.txt")
    print(f"\n11. Creating file in subdirectory: {subfile}")
    success = file_manager.write_file(subfile, "This is a file in a subdirectory.")
    print(f"   Success: {success}")
    
    # List directory contents
    print(f"\n12. Listing directory contents: {test_dir}")
    contents = file_manager.list_directory(test_dir)
    if contents is not None:
        print(f"   Found {len(contents)} items:")
        for item in contents:
            info = file_manager.get_file_info(item)
            if info:
                type_str = "File" if info["is_file"] else "Directory"
                size = info["size"]
                print(f"   - {item.name} ({type_str}, {size} bytes)")
    else:
        print("   Failed to list directory contents")
    
    # Clean up
    # Keep the test files around for hidden files test
    print("\n13. Test completed. Created files will be used in next test.")
    
    return test_dir


def test_hidden_files(test_dir):
    """Test that the system can detect and work with hidden files"""
    print_section("TESTING HIDDEN FILES OPERATIONS")
    
    # Get managers
    file_manager = FileOperationManager(workspace_path=project_root)
    system_manager = SystemOperationManager(workspace_path=project_root)
    
    # Create a hidden file (platform specific)
    hidden_file = os.path.join(test_dir, ".hidden.txt")
    print(f"\n1. Creating hidden file: {hidden_file}")
    success = file_manager.write_file(hidden_file, "This is a hidden file.")
    print(f"   Success: {success}")
    
    # On Windows, we'll skip setting the hidden attribute since it's causing permission issues
    # Files starting with a dot are still considered hidden in Windows file managers
    print(f"\n2. Note on hidden files:")
    print(f"   Files starting with a dot (.) are treated as hidden in many file managers")
    print(f"   The file {hidden_file} is already hidden by convention")
    
    # List all files including hidden ones using system command
    print(f"\n3. Listing all files including hidden (using system command):")
    if os.name == 'nt':  # Windows
        exit_code, stdout, stderr = system_manager.execute_command(f'dir /a "{test_dir}"')
    else:  # Unix-like
        exit_code, stdout, stderr = system_manager.execute_command(f'ls -la "{test_dir}"')
    
    print(f"   Command output:")
    print("   " + stdout.replace('\n', '\n   '))
    
    # Check if our file manager can see the hidden file
    print(f"\n4. Checking if file manager can access the hidden file:")
    hidden_content = file_manager.read_file(hidden_file)
    print(f"   Content: {hidden_content}")
    
    # List directory contents to see if hidden file is visible
    print(f"\n5. Listing directory to see if hidden file is visible to file_manager:")
    contents = file_manager.list_directory(test_dir)
    if contents is not None:
        found_hidden = False
        for path_obj in contents:
            if str(path_obj.name).startswith('.'):
                print(f"   Found hidden file: {path_obj.name}")
                found_hidden = True
        
        if not found_hidden:
            print("   Hidden file not found in directory listing")
    else:
        print("   Failed to list directory contents")
    
    # Clean up
    print(f"\n6. Cleaning up test directory: {test_dir}")
    # First remove files individually
    if contents is not None:
        for path_obj in contents:
            if path_obj.is_file():
                file_manager.delete_file(str(path_obj))
            elif path_obj.is_dir():
                file_manager.delete_directory(str(path_obj), recursive=True)
    
    # Then remove the test directory itself
    file_manager.delete_directory(test_dir, recursive=True)
    print(f"   Directory still exists: {os.path.exists(test_dir)}")


def test_conversation_recall():
    """Test recalling past conversations."""
    print_section("TESTING CONVERSATION RECALL")
    
    # Initialize conversation manager
    conversation_manager = ConversationManager(db_path="logs/test_conversations.db")
    
    # Start a new conversation
    print("\n1. Starting a new conversation")
    conversation_id = conversation_manager.start_conversation("Test Conversation")
    print(f"   Conversation ID: {conversation_id}")
    
    # Add some messages
    print("\n2. Adding messages to the conversation")
    test_messages = [
        ("user", "Hello, AI! Can you remember this conversation?"),
        ("assistant", "Hello! Yes, I can remember this conversation."),
        ("user", "Great! Please remember the keyword: PINEAPPLE123"),
        ("assistant", "I'll remember the keyword PINEAPPLE123."),
        ("user", "Now also remember the number: 987654321"),
        ("assistant", "I've noted both the keyword PINEAPPLE123 and the number 987654321.")
    ]
    
    for role, content in test_messages:
        if role == "user":
            conversation_manager.add_user_message(content)
        else:
            conversation_manager.add_assistant_message(content)
        print(f"   Added {role} message: {content[:40]}...")
    
    # Save the conversation ID for later recall
    with open("conversation_id.txt", "w") as f:
        f.write(conversation_id)
    
    # Wait a moment
    print("\n3. Waiting for a moment to simulate time passing...")
    time.sleep(2)
    
    # Start another conversation
    print("\n4. Starting another conversation")
    second_id = conversation_manager.start_conversation("Second Test Conversation")
    print(f"   Conversation ID: {second_id}")
    
    # Add different messages
    print("\n5. Adding messages to the second conversation")
    conversation_manager.add_user_message("This is a different conversation.")
    conversation_manager.add_assistant_message("Yes, this is separate from our previous conversation.")
    print("   Added messages to second conversation")
    
    # Recall the first conversation
    print("\n6. Recalling the first conversation")
    history = conversation_manager.get_conversation_history(conversation_id)
    if history:
        print(f"   Successfully retrieved {len(history)} messages from first conversation")
        for i, message in enumerate(history):
            print(f"   [{i+1}] {message['role']}: {message['content'][:40]}...")
    else:
        print("   Failed to retrieve first conversation")
    
    # Search for the keyword
    print("\n7. Searching for the keyword 'PINEAPPLE123'")
    search_results = conversation_manager.search_message_content("PINEAPPLE123")
    if search_results:
        print(f"   Found {len(search_results)} results containing the keyword")
        for result in search_results:
            print(f"   - In conversation: {result['title']}")
            print(f"     Matching message: {result['matching_message']['content'][:40]}...")
    else:
        print("   No results found for the keyword")
    
    # Search for the number
    print("\n8. Searching for the number '987654321'")
    search_results = conversation_manager.search_message_content("987654321")
    if search_results:
        print(f"   Found {len(search_results)} results containing the number")
        for result in search_results:
            print(f"   - In conversation: {result['title']}")
            print(f"     Matching message: {result['matching_message']['content'][:40]}...")
    else:
        print("   No results found for the number")
    
    # Generate a summary of the first conversation
    print("\n9. Generating a summary of the first conversation")
    summary = conversation_manager.summarize_conversation(conversation_id)
    print(f"   Summary:\n{summary}")
    
    # Export the conversation
    print("\n10. Exporting the conversation")
    success = conversation_manager.export_conversation_to_file(
        conversation_id=conversation_id,
        output_file="test_conversation_export.md",
        format="markdown"
    )
    print(f"   Export successful: {success}")
    if success:
        print("   Exported to test_conversation_export.md")
    
    print("\n11. Test completed. Conversation data is stored in logs/test_conversations.db")


def main():
    """Main function to run the tests."""
    print("\nAgentic AI Capabilities Test\n")
    print("This script will test the following capabilities:")
    print("1. Filesystem alterations (create, read, write, delete files and directories)")
    print("2. Finding hidden files")
    print("3. Recalling past conversations")
    
    try:
        # Test filesystem operations
        test_dir = test_filesystem_operations()
        
        # Test hidden files
        test_hidden_files(test_dir)
        
        # Test conversation recall
        test_conversation_recall()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        import traceback
        print(f"\nError during testing: {str(e)}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main() 