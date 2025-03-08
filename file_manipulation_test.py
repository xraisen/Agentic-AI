#!/usr/bin/env python3
"""
File Manipulation Test for Agentic AI

This script tests whether the Agentic AI can perform various file system operations
including creating, reading, writing, and deleting files and directories.
"""

import os
import sys
import time
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

# Import required modules
from core.file_operations import FileOperationManager
from core.system_operations import SystemOperationManager
from utils.permission_manager import PermissionManager

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_file_manipulation():
    """Test if Agentic AI can perform file manipulation operations"""
    print_section("TESTING FILE MANIPULATION CAPABILITIES")
    
    # Get current directory
    project_root = Path(__file__).resolve().parent
    
    # Create a test directory
    test_dir = project_root / "test_manipulation"
    if not test_dir.exists():
        test_dir.mkdir(parents=True)
    
    print(f"Testing in directory: {test_dir}")
    
    # Initialize file manager
    file_manager = FileOperationManager(workspace_path=project_root)
    
    # Test file creation
    test_file = test_dir / "test_file.txt"
    content = "This is a test file created by Agentic AI.\nTesting file manipulation capabilities."
    
    print("\n1. Creating a text file...")
    success = file_manager.write_file(str(test_file), content)
    print(f"   Success: {success}")
    
    # Test file reading
    print("\n2. Reading the file content...")
    read_content = file_manager.read_file(str(test_file))
    print(f"   Content: {read_content}")
    print(f"   Match: {read_content == content}")
    
    # Test file appending
    print("\n3. Appending to the file...")
    append_content = "\nThis line was appended by the test."
    success = file_manager.append_file(str(test_file), append_content)
    print(f"   Success: {success}")
    
    # Test reading updated file
    print("\n4. Reading the updated file...")
    read_updated = file_manager.read_file(str(test_file))
    print(f"   Content: {read_updated}")
    print(f"   Match: {read_updated == content + append_content}")
    
    # Test file copying
    copy_file = test_dir / "test_file_copy.txt"
    print("\n5. Copying the file...")
    success = file_manager.copy_file(str(test_file), str(copy_file))
    print(f"   Success: {success}")
    
    # Test reading copied file
    print("\n6. Reading the copied file...")
    copy_content = file_manager.read_file(str(copy_file))
    print(f"   Content matches original: {copy_content == read_updated}")
    
    # Test creating a subdirectory
    subdir = test_dir / "subdir"
    print("\n7. Creating a subdirectory...")
    success = file_manager.create_directory(str(subdir))
    print(f"   Success: {success}")
    
    # Test creating a file in the subdirectory
    subdir_file = subdir / "subfile.txt"
    print("\n8. Creating a file in the subdirectory...")
    success = file_manager.write_file(str(subdir_file), "File in subdirectory")
    print(f"   Success: {success}")
    
    # Test listing directory contents
    print("\n9. Listing directory contents...")
    dir_contents = file_manager.list_directory(str(test_dir))
    if dir_contents:
        print(f"   Found {len(dir_contents)} items:")
        for item in dir_contents:
            item_type = "Directory" if item.is_dir() else "File"
            item_size = 0 if item.is_dir() else item.stat().st_size
            print(f"   - {item.name} ({item_type}, {item_size} bytes)")
    else:
        print("   Failed to list directory contents")
    
    # Test deleting a file
    print("\n10. Deleting the copied file...")
    success = file_manager.delete_file(str(copy_file))
    print(f"   Success: {success}")
    print(f"   File still exists: {copy_file.exists()}")
    
    # Test deleting directory with contents
    print("\n11. Deleting subdirectory with contents...")
    success = file_manager.delete_directory(str(subdir), recursive=True)
    print(f"   Success: {success}")
    print(f"   Directory still exists: {subdir.exists()}")
    
    # Clean up
    print("\n12. Cleaning up test directory...")
    
    # Delete test file if it exists
    if test_file.exists():
        file_manager.delete_file(str(test_file))
    
    # Delete test directory if it exists
    if test_dir.exists():
        file_manager.delete_directory(str(test_dir), recursive=True)
    
    print(f"   Test directory still exists: {test_dir.exists()}")
    
    print("\nFile manipulation tests completed successfully!")

if __name__ == "__main__":
    try:
        test_file_manipulation()
    except Exception as e:
        print(f"Error during testing: {e}")
        print(f"Traceback: {sys.exc_info()}") 