#!/usr/bin/env python3
"""
Windows System Manipulation Demo

This script demonstrates the advanced Windows system manipulation capabilities
of Agentic AI, including registry management, service control, firewall rules,
scheduled tasks, and privilege elevation.
"""

import os
import sys
import time
import platform
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import system operations module
from src.core.system_operations import (
    get_system_manager,
    execute_command,
    manage_service,
    modify_registry,
    create_firewall_rule,
    create_scheduled_task,
    elevate_privileges
)

def print_section(title):
    """Print a section title"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_result(operation, success, message=""):
    """Print operation result"""
    if success:
        status = "✅ SUCCESS"
    else:
        status = "❌ FAILED"
    
    print(f"{operation}: {status}")
    if message:
        print(f"  {message}")
    print()

def check_windows():
    """Check if running on Windows"""
    if platform.system() != "Windows":
        print("This demo requires Windows. Exiting.")
        sys.exit(1)
    
    print("Running on Windows:", platform.version())
    print("Python version:", platform.python_version())
    print()

def registry_demo():
    """Demonstrate registry operations"""
    print_section("Registry Operations")
    
    # Test registry key path
    test_key = r"HKEY_CURRENT_USER\Software\AgenticAIDemo"
    
    # Create a test string value
    print("Creating string registry value...")
    success = modify_registry(
        test_key,
        "DemoString",
        "Hello from Agentic AI",
        "REG_SZ"
    )
    print_result("Create string value", success)
    
    # Create a test DWORD value
    print("Creating DWORD registry value...")
    success = modify_registry(
        test_key,
        "DemoNumber",
        42,
        "REG_DWORD"
    )
    print_result("Create DWORD value", success)
    
    # Read registry values
    print("Reading registry values...")
    exit_code, stdout, stderr = execute_command(f'reg query "{test_key}"')
    print_result("Read registry", exit_code == 0, stdout)
    
    # Demonstrate rollback
    print("Modifying registry value (will be rolled back)...")
    system_manager = get_system_manager()
    success = system_manager.modify_registry(
        test_key,
        "DemoString",
        "This will be rolled back",
        "REG_SZ"
    )
    
    if success:
        print("Value modified, now rolling back...")
        rollback_success = system_manager.rollback_last_operation()
        print_result("Registry rollback", rollback_success)
        
        # Verify rollback
        exit_code, stdout, stderr = execute_command(f'reg query "{test_key}" /v DemoString')
        print_result("Verify rollback", exit_code == 0, stdout)
    else:
        print_result("Modify for rollback", False)
    
    # Clean up
    print("Cleaning up registry keys...")
    exit_code, stdout, stderr = execute_command(f'reg delete "{test_key}" /f')
    print_result("Registry cleanup", exit_code == 0)

def service_demo():
    """Demonstrate Windows service operations"""
    print_section("Windows Service Management")
    
    # We'll use Windows Update service for demonstration
    # It's generally present on all Windows systems
    service_name = "wuauserv"  # Windows Update service
    
    # Query service status
    print(f"Querying status of {service_name} service...")
    success, output = manage_service(service_name, "query")
    print_result("Query service", success, output)
    
    # Note: Starting/stopping services requires elevation and confirmation
    # Only attempt if explicitly approved
    print("\nNote: Starting/stopping services requires administrator privileges.")
    print("      and will prompt for confirmation.")
    print("      This part of the demo is optional.")
    
    user_input = input("\nDo you want to attempt service control operations? (y/n): ")
    if user_input.lower() != 'y':
        print("Skipping service control operations.")
        return
    
    # Attempt to stop the service
    print(f"\nAttempting to stop {service_name} service...")
    print("(This will prompt for confirmation and may request elevation)")
    success, output = manage_service(service_name, "stop")
    print_result("Stop service", success, output)
    
    # Wait a moment
    time.sleep(2)
    
    # Restart the service
    print(f"Attempting to start {service_name} service again...")
    success, output = manage_service(service_name, "start")
    print_result("Start service", success, output)

def firewall_demo():
    """Demonstrate Windows Firewall operations"""
    print_section("Windows Firewall Management")
    
    # Create a test rule name with timestamp to avoid conflicts
    timestamp = int(time.time())
    rule_name = f"AgenticAIDemo_{timestamp}"
    
    print("Note: Creating firewall rules requires administrator privileges")
    print("      and will prompt for confirmation.")
    print("      This part of the demo is optional.")
    
    user_input = input("\nDo you want to attempt firewall operations? (y/n): ")
    if user_input.lower() != 'y':
        print("Skipping firewall operations.")
        return
    
    # Create a test inbound rule
    print(f"\nCreating firewall rule: {rule_name}...")
    success = create_firewall_rule(
        rule_name,
        "allow",
        "in",
        "TCP",
        8080
    )
    print_result("Create firewall rule", success)
    
    # Verify rule was created
    print("Verifying firewall rule...")
    exit_code, stdout, stderr = execute_command(f'netsh advfirewall firewall show rule name="{rule_name}"')
    print_result("Verify firewall rule", exit_code == 0, stdout)
    
    # Clean up - delete the rule
    print("Cleaning up firewall rule...")
    exit_code, stdout, stderr = execute_command(f'netsh advfirewall firewall delete rule name="{rule_name}"')
    print_result("Delete firewall rule", exit_code == 0)

def scheduled_task_demo():
    """Demonstrate scheduled task operations"""
    print_section("Scheduled Tasks Management")
    
    # Create a test task name with timestamp to avoid conflicts
    timestamp = int(time.time())
    task_name = f"AgenticAIDemo_{timestamp}"
    
    # Create a harmless command for the task (just echo a message)
    task_command = f'cmd /c echo "This is a test task from Agentic AI"'
    
    print("Note: Creating scheduled tasks requires confirmation.")
    print("      This part of the demo is optional.")
    
    user_input = input("\nDo you want to attempt scheduled task operations? (y/n): ")
    if user_input.lower() != 'y':
        print("Skipping scheduled task operations.")
        return
    
    # Create a test scheduled task
    print(f"\nCreating scheduled task: {task_name}...")
    success = create_scheduled_task(
        task_name,
        task_command,
        "ONCE /ST 23:59"  # Schedule once at 11:59 PM
    )
    print_result("Create scheduled task", success)
    
    # Verify task was created
    print("Verifying scheduled task...")
    exit_code, stdout, stderr = execute_command(f'schtasks /query /tn "{task_name}"')
    print_result("Verify scheduled task", exit_code == 0, stdout)
    
    # Clean up - delete the task
    print("Cleaning up scheduled task...")
    exit_code, stdout, stderr = execute_command(f'schtasks /delete /tn "{task_name}" /f')
    print_result("Delete scheduled task", exit_code == 0)

def background_process_demo():
    """Demonstrate background process management"""
    print_section("Background Process Management")
    
    print("Starting a background process (ping with 10 count)...")
    system_manager = get_system_manager()
    
    # Start a ping command in the background
    exit_code, stdout, stderr = system_manager.execute_command(
        "ping -n 10 127.0.0.1",
        background=True
    )
    
    if exit_code != 0:
        print_result("Start background process", False, stderr)
        return
    
    # Get process ID from stdout
    process_id = int(stdout.split("Process ID: ")[1].strip())
    print(f"Process started with ID: {process_id}")
    
    # Check status immediately
    print("\nChecking status immediately...")
    status = system_manager.get_process_status(process_id)
    print(f"Process running: {not status.get('completed', True)}")
    
    # Wait a moment and check again
    print("\nWaiting for 2 seconds...")
    time.sleep(2)
    
    # Check status again
    print("Checking status again...")
    status = system_manager.get_process_status(process_id)
    print(f"Process running: {not status.get('completed', True)}")
    
    if not status.get("completed", True):
        # Demonstrate process termination
        print("\nTerminating the process...")
        kill_success = system_manager.kill_process(process_id)
        print_result("Terminate process", kill_success)
    else:
        # Show the output if process completed
        print("\nProcess completed. Output:")
        print(status.get("stdout", ""))
    
    # Final status check
    print("\nFinal status check...")
    status = system_manager.get_process_status(process_id)
    print(f"Process completed: {status.get('completed', False)}")
    print_result("Background process demo", True)

def privilege_elevation_demo():
    """Demonstrate privilege elevation"""
    print_section("Privilege Elevation")
    
    # Check current elevation status
    system_manager = get_system_manager()
    current_status = system_manager.is_elevated
    print(f"Current process elevated: {current_status}")
    
    if current_status:
        print("\nProcess is already running with elevated privileges.")
        print("No need to demonstrate elevation.")
        return
    
    print("\nNote: This will attempt to restart the script with elevated privileges.")
    print("      The current process will exit if elevation is approved.")
    print("      This part of the demo is optional.")
    
    user_input = input("\nDo you want to attempt privilege elevation? (y/n): ")
    if user_input.lower() != 'y':
        print("Skipping privilege elevation.")
        return
    
    print("\nAttempting to elevate privileges...")
    print("(This will prompt for confirmation)")
    
    # This will restart the script with elevated privileges if confirmed
    elevated = elevate_privileges("Windows System Demo")
    
    # The code below will only execute if elevation was denied or failed
    print_result("Privilege elevation", elevated, 
                 "If you approved elevation, a new elevated process should have started.")

def main():
    """Main demo function"""
    print_section("Agentic AI - Windows System Manipulation Demo")
    
    # Check if running on Windows
    check_windows()
    
    # Show menu
    print("This demo will showcase the Windows system manipulation capabilities of Agentic AI.")
    print("Choose the demonstrations you want to run:\n")
    print("1. Registry management")
    print("2. Windows service control")
    print("3. Firewall rules")
    print("4. Scheduled tasks")
    print("5. Background process management")
    print("6. Privilege elevation")
    print("7. Run all demos")
    print("0. Exit\n")
    
    choice = input("Enter your choice (0-7): ")
    
    if choice == '1':
        registry_demo()
    elif choice == '2':
        service_demo()
    elif choice == '3':
        firewall_demo()
    elif choice == '4':
        scheduled_task_demo()
    elif choice == '5':
        background_process_demo()
    elif choice == '6':
        privilege_elevation_demo()
    elif choice == '7':
        registry_demo()
        background_process_demo()
        service_demo()
        firewall_demo()
        scheduled_task_demo()
        privilege_elevation_demo()
    elif choice == '0':
        print("Exiting demo.")
        return
    else:
        print("Invalid choice. Exiting.")
        return
    
    print_section("Demo Completed")
    print("Thank you for trying the Agentic AI Windows System Manipulation Demo!")

if __name__ == "__main__":
    main() 