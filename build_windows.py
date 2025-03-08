#!/usr/bin/env python3
"""
Simplified build script for Windows version of Agentic AI
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Build the Windows executable"""
    print("Building Windows application...")
    
    # Get project root directory
    root_dir = Path(__file__).resolve().parent
    
    # Ensure the release directory exists
    release_dir = root_dir / 'release' / 'windows'
    release_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run PyInstaller directly with command line arguments
        subprocess.run([
            sys.executable,  # Use the same Python interpreter
            '-m',
            'PyInstaller',
            '--clean',  # Clean PyInstaller cache
            '--onefile',  # Create a single executable
            '--console',  # Create a console app (for debugging)
            '--name=agentic-ai',  # Name of the output file
            '--add-data=assets;assets',  # Include assets folder
            'src/main.py'  # Main script to execute
        ], check=True)
        
        # Copy the executable to the release directory
        dist_path = root_dir / 'dist'
        if dist_path.exists():
            exe_path = dist_path / 'agentic-ai.exe'
            if exe_path.exists():
                shutil.copy2(exe_path, release_dir / 'agentic-ai.exe')
                print(f"Copied executable to {release_dir / 'agentic-ai.exe'}")
            else:
                print(f"Warning: Executable not found at {exe_path}")
                
            # Create a simple launcher batch file
            with open(release_dir / 'run.bat', 'w') as f:
                f.write('@echo off\r\n')
                f.write('echo Starting Agentic AI...\r\n')
                f.write('start "" "%~dp0agentic-ai.exe"\r\n')
                
            print(f"Created launcher: {release_dir / 'run.bat'}")
        else:
            print(f"Warning: Dist directory not found at {dist_path}")
            
        print("Windows application build completed!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 