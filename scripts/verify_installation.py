#!/usr/bin/env python3
"""
Agentic AI - Installation Verification Script
This script checks if all dependencies are installed and the environment is properly configured.
"""

import os
import sys
import importlib
import platform
import subprocess
from pathlib import Path

# Add the project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_status(message, status, details=None):
    """Print a status message with color coding."""
    status_text = {
        "OK": f"{GREEN}OK{RESET}",
        "WARNING": f"{YELLOW}WARNING{RESET}",
        "ERROR": f"{RED}ERROR{RESET}",
        "INFO": f"{BOLD}INFO{RESET}"
    }
    
    print(f"  {message:<40} [{status_text.get(status, status)}]")
    if details:
        for line in details.split('\n'):
            print(f"    {line}")

def check_dependency(module_name, package_name=None):
    """Check if a Python dependency is installed."""
    package_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        return True, None
    except ImportError as e:
        return False, f"Missing package: {package_name}\nInstall with: pip install {package_name}"

def check_command(command, args=None):
    """Check if a command is available."""
    args = args or ["--version"]
    try:
        result = subprocess.run([command] + args, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except FileNotFoundError:
        return False, f"Command '{command}' not found"
        
def check_directory(directory):
    """Check if a directory exists and is writable."""
    if not os.path.exists(directory):
        return False, f"Directory does not exist"
    if not os.path.isdir(directory):
        return False, f"Not a directory"
    if not os.access(directory, os.W_OK):
        return False, f"Directory is not writable"
    return True, None

def main():
    """Run the verification checks."""
    print(f"\n{BOLD}Agentic AI - Installation Verification{RESET}\n")
    
    print(f"{BOLD}System Information:{RESET}")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  Platform: {platform.platform()}")
    print(f"  Installation directory: {ROOT_DIR}")
    
    print(f"\n{BOLD}Checking Core Dependencies:{RESET}")
    core_deps = [
        ("PyQt6", None),
        ("aiohttp", None),
        ("requests", None),
        ("python_dotenv", "python-dotenv"),
        ("transformers", None),
        ("torch", None),
        ("nltk", None),
    ]
    
    for module_name, package_name in core_deps:
        ok, details = check_dependency(module_name, package_name)
        print_status(f"Checking {module_name}", "OK" if ok else "ERROR", None if ok else details)
    
    print(f"\n{BOLD}Checking Build Dependencies:{RESET}")
    build_deps = [
        ("PyInstaller", "pyinstaller"),
        ("wheel", None),
    ]
    
    for module_name, package_name in build_deps:
        ok, details = check_dependency(module_name, package_name)
        print_status(f"Checking {module_name}", "OK" if ok else "WARNING", None if ok else details)
    
    print(f"\n{BOLD}Checking Directories:{RESET}")
    directories = [
        ("assets", ROOT_DIR / "assets"),
        ("logs", ROOT_DIR / "logs"),
        ("cache", ROOT_DIR / "cache"),
    ]
    
    for name, path in directories:
        ok, details = check_directory(path)
        print_status(f"Checking {name} directory", "OK" if ok else "WARNING", None if ok else details)
        
    print(f"\n{BOLD}Checking Configuration:{RESET}")
    config_file = ROOT_DIR / "config.json"
    if os.path.exists(config_file):
        import json
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print_status("Loading config.json", "OK")
            
            # Check API key
            if 'OPENROUTER_API_KEY' in config and config['OPENROUTER_API_KEY'] != 'your-api-key-here':
                print_status("API key configured", "OK")
            else:
                print_status("API key configured", "WARNING", "API key not set or using default value")
                
        except json.JSONDecodeError:
            print_status("Loading config.json", "ERROR", "Invalid JSON format")
    else:
        print_status("Loading config.json", "WARNING", "File not found. Using config.example.json instead.")
    
    # Check package version
    try:
        from src.agentic_ai import __version__
        print_status(f"Package version", "INFO", f"Agentic AI version {__version__}")
    except ImportError:
        print_status("Package version", "WARNING", "Could not determine package version")
    
    print(f"\n{BOLD}Verification Complete{RESET}\n")
    
if __name__ == "__main__":
    main() 