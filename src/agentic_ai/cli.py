"""Command-line interface for Agentic AI."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Import the code generator
from src.utils.code_generator import CodeGenerator

# Set up logging
logger = logging.getLogger(__name__)

def print_banner():
    """Print the Agentic AI banner"""
    banner = """
==================================================
             Agentic AI
==================================================
Type 'exit' or 'quit' to exit.
Type 'help' for commands.
==================================================
"""
    print(banner)

def print_help():
    """Print help information for the CLI"""
    help_text = """
Agentic AI CLI Commands:
-----------------------
help                       : Show this help message
exit, quit                 : Exit the application
clear                      : Clear the screen

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
        # Generate and execute code based on the command
        result = code_generator.generate_and_execute(command)
        
        # Display the result
        if result:
            print("\nResult:")
            print(result)
        else:
            print("\nCommand executed successfully.")
            
        return True
    except Exception as e:
        print(f"\nError: {e}")
        logger.error(f"Error executing command: {e}", exc_info=True)
        return True

def interactive_mode(code_generator: CodeGenerator) -> int:
    """
    Run the interactive CLI mode

    Args:
        code_generator: The code generator instance

    Returns:
        int: Exit code
    """
    # Clear the screen first
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print the banner
    print_banner()
    print("Current workspace:", code_generator.workspace_path)
    print("Type 'help' for available commands.")

    try:
        # Main interactive loop
        while True:
            try:
                # Flush stdout to ensure prompt is displayed
                sys.stdout.flush()
                command = input("\nYou: ")
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
        logger.error(f"Error in interactive mode: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1

def main(args=None) -> int:
    """
    Main entry point for the CLI
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    # Create argument parser
    parser = argparse.ArgumentParser(description="Agentic AI CLI")
    parser.add_argument("command", nargs="*", help="Command to execute")
    parser.add_argument("-w", "--workspace", help="Set the workspace directory")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
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

if __name__ == "__main__":
    sys.exit(main()) 