"""Command-line interface for Agentic AI."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Import the code generator
from src.utils.code_generator import CodeGenerator

def print_banner():
    """Print the Agentic AI banner"""
    banner = """
    +-+-+-+-+-+-+-+ +-+-+
    |A|g|e|n|t|i|c| |A|I|
    +-+-+-+-+-+-+-+ +-+-+
    File Manipulation Assistant
    Type 'help' for commands, 'exit' to quit
    """
    print(banner)

def print_help():
    """Print help information for the CLI"""
    help_text = """
    Agentic AI CLI Commands:
    -----------------------
    help                       : Show this help message
    exit, quit                 : Exit the application
    
    File Operations (examples):
    create file named example.txt with Hello, World!
    read file example.txt
    delete file example.txt
    list files in .
    search files containing example
    create directory docs
    
    Try using natural language to describe what you want to do!
    """
    print(help_text)

def wait_on_error(seconds=3):
    """Wait a moment on error to show the message"""
    time.sleep(seconds)

def handle_command(code_generator: CodeGenerator, command: str) -> bool:
    """
    Handle a command in the CLI
    
    Args:
        code_generator: The code generator instance
        command: The command to handle
        
    Returns:
        bool: True to continue, False to exit
    """
    # Check for built-in commands first
    if command.lower() in ['exit', 'quit']:
        print("Exiting Agentic AI...")
        return False
    elif command.lower() == 'help':
        print_help()
        return True
    elif command.lower() == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        return True
    
    # Handle file operation commands using the code generator
    print(f"\nProcessing: {command}")
    print("Generating and executing code...")
    
    try:
        success, message, result = code_generator.generate_and_execute(command)
        
        if success:
            print(f"\n✅ Success: {message}")
            
            # If we have result data to display
            if 'result' in result and isinstance(result['result'], dict):
                result_data = result['result']
                
                # For file read operations, show content
                if 'content' in result_data:
                    print("\nFile Content:")
                    print("-" * 50)
                    print(result_data['content'])
                    print("-" * 50)
                
                # For list operations, show files
                if 'files' in result_data:
                    print("\nFiles:")
                    for i, file in enumerate(result_data['files'], 1):
                        print(f"{i}. {file}")
        else:
            print(f"\n❌ Error: {message}")
            
            # Show error details if available
            if 'stderr' in result and result['stderr']:
                print("\nError details:")
                print(result['stderr'])
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    return True

def interactive_mode(code_generator: CodeGenerator) -> int:
    """
    Run the interactive CLI mode
    
    Args:
        code_generator: The code generator instance
        
    Returns:
        int: Exit code
    """
    print_banner()
    print("Current workspace:", code_generator.workspace_path)
    print_help()
    
    try:
        # Main interactive loop
        while True:
            try:
                command = input("\n> ")
                if not command.strip():
                    continue
                
                # Handle the command
                should_continue = handle_command(code_generator, command)
                if not should_continue:
                    break
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error processing command: {e}")
                wait_on_error(1)
        
        return 0
    except Exception as e:
        print(f"Error in interactive mode: {e}")
        wait_on_error()
        return 1

def main(args: list[str]) -> int:
    """Run the Agentic AI CLI.
    
    Args:
        args: Command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Agentic AI Command Line Interface")
    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--workspace", help="Path to workspace directory")
    parser.add_argument("command", nargs="*", help="Command to execute")
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Determine workspace path
        workspace_path = None
        if parsed_args.workspace:
            workspace_path = Path(parsed_args.workspace).resolve()
        else:
            workspace_path = Path.cwd()
        
        # Create code generator
        code_generator = CodeGenerator(workspace_path=workspace_path)
        
        # Process command or start interactive mode
        if parsed_args.command:
            # Join arguments into a single command
            command = " ".join(parsed_args.command)
            logger.info(f"Processing command: {command}")
            
            # Handle the command
            handle_command(code_generator, command)
            return 0
        else:
            # Interactive mode
            logger.info("Starting interactive mode")
            return interactive_mode(code_generator)
            
    except KeyboardInterrupt:
        logger.info("User interrupted")
        return 0
    except Exception as e:
        logger.error(f"Error in CLI: {e}", exc_info=True)
        print(f"Error: {e}")
        wait_on_error()
        return 1 