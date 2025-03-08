#!/usr/bin/env python3
"""
Advanced build script for Windows version of Agentic AI
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
import datetime

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Build Agentic AI for Windows")
    parser.add_argument("--console", action="store_true", help="Build with console window (for debugging)")
    parser.add_argument("--onefile", action="store_true", help="Build as a single executable file")
    parser.add_argument("--installer", action="store_true", help="Create an installer")
    parser.add_argument("--version", help="Override version number")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    return parser.parse_args()

def get_version():
    """Get current version from VERSION file"""
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Default version if file not found
        return "1.0.0"

def clean_build_dirs(root_dir):
    """Clean build directories"""
    print("Cleaning build directories...")
    
    # Directories to clean
    dirs_to_clean = [
        root_dir / "build",
        root_dir / "dist"
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"Removing {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)

def create_inno_script(root_dir, version, output_dir):
    """Create Inno Setup script for installer"""
    inno_script = f"""
#define MyAppName "Agentic AI"
#define MyAppVersion "{version}"
#define MyAppPublisher "Agentic AI Team"
#define MyAppURL "https://example.com/agentic-ai"
#define MyAppExeName "agentic-ai.exe"

[Setup]
AppId={{{{3F1A412C-B30E-4F5A-8A24-9B5E99725E0D}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile={root_dir}\\LICENSE
OutputDir={output_dir}
OutputBaseFilename=agentic-ai-setup-{version}
Compression=lzma
SolidCompression=yes
PrivilegesRequiredOverridesAllowed=dialog
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{root_dir}\\dist\\agentic-ai\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{root_dir}\\dist\\agentic-ai\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#MyAppName}}}}"; Flags: nowait postinstall skipifsilent
"""
    
    # Write Inno Setup script file
    script_path = root_dir / "installer.iss"
    with open(script_path, "w") as f:
        f.write(inno_script)
    
    return script_path

def build_executable(args, root_dir, version):
    """Build the Windows executable"""
    print(f"Building Windows application v{version}...")
    
    # Ensure the release directory exists
    release_dir = root_dir / 'release' / 'windows'
    release_dir.mkdir(parents=True, exist_ok=True)
    
    # Base PyInstaller command
    pyinstaller_args = [
        sys.executable,  # Use the same Python interpreter
        '-m',
        'PyInstaller',
        '--clean',  # Clean PyInstaller cache
        '--name=agentic-ai',  # Name of the output file
        '--add-data=assets;assets',  # Include assets folder
        '--add-data=config;config',  # Include config folder
    ]
    
    # Add icon if it exists
    icon_path = root_dir / 'assets' / 'icon.ico'
    if icon_path.exists():
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # Add version info if available
    version_info = root_dir / 'version_info.txt'
    if version_info.exists():
        pyinstaller_args.append(f'--version-file={version_info}')
    
    # Check for onefile mode
    if args.onefile:
        pyinstaller_args.append('--onefile')
    else:
        pyinstaller_args.append('--onedir')
    
    # Check for console mode
    if args.console:
        pyinstaller_args.append('--console')
    else:
        pyinstaller_args.append('--windowed')
    
    # Add the main script
    pyinstaller_args.append('src/main.py')
    
    try:
        # Run PyInstaller
        print("Running PyInstaller with arguments:", " ".join(pyinstaller_args))
        subprocess.run(pyinstaller_args, check=True)
        
        # Copy the executable to the release directory
        if args.onefile:
            # For --onefile mode
            exe_path = root_dir / 'dist' / 'agentic-ai.exe'
            if exe_path.exists():
                shutil.copy2(exe_path, release_dir / 'agentic-ai.exe')
                print(f"Copied executable to {release_dir / 'agentic-ai.exe'}")
            else:
                print(f"Warning: Executable not found at {exe_path}")
        else:
            # For --onedir mode, copy the entire directory
            dist_dir = root_dir / 'dist' / 'agentic-ai'
            if dist_dir.exists():
                # Remove existing release directory if it exists
                release_exe_dir = release_dir / 'agentic-ai'
                if release_exe_dir.exists():
                    shutil.rmtree(release_exe_dir)
                
                # Copy the entire directory
                shutil.copytree(dist_dir, release_exe_dir)
                print(f"Copied application folder to {release_exe_dir}")
            else:
                print(f"Warning: Application directory not found at {dist_dir}")
        
        # Create a launcher batch file
        with open(release_dir / 'run.bat', 'w') as f:
            f.write('@echo off\r\n')
            f.write('echo Starting Agentic AI...\r\n')
            if args.onefile:
                f.write('start "" "%~dp0agentic-ai.exe"\r\n')
            else:
                f.write('start "" "%~dp0agentic-ai\\agentic-ai.exe"\r\n')
                
        print(f"Created launcher: {release_dir / 'run.bat'}")
        
        # Create readme with build information
        with open(release_dir / 'README.txt', 'w') as f:
            f.write(f"Agentic AI v{version}\r\n")
            f.write(f"Built on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\r\n\r\n")
            f.write(f"Build configuration:\r\n")
            f.write(f"- One file mode: {'Yes' if args.onefile else 'No'}\r\n")
            f.write(f"- Console mode: {'Yes' if args.console else 'No'}\r\n\r\n")
            f.write(f"To run the application, use run.bat or directly execute agentic-ai.exe\r\n")
        
        print(f"Created README: {release_dir / 'README.txt'}")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def build_installer(root_dir, version, release_dir):
    """Build Windows installer using Inno Setup"""
    print("Building Windows installer...")
    
    # Check if Inno Setup is installed
    inno_setup_path = None
    possible_paths = [
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files (x86)/Inno Setup 5/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 5/ISCC.exe")
    ]
    
    for path in possible_paths:
        if path.exists():
            inno_setup_path = path
            break
    
    if inno_setup_path is None:
        print("Error: Inno Setup not found. Please install Inno Setup or specify the path manually.")
        return False
    
    # Create Inno Setup script
    script_path = create_inno_script(root_dir, version, release_dir)
    
    try:
        # Run Inno Setup compiler
        subprocess.run([str(inno_setup_path), str(script_path)], check=True)
        print(f"Installer created successfully in {release_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installer build failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error building installer: {e}")
        return False

def main():
    """Main build function"""
    # Check if running on Windows
    if platform.system() != "Windows":
        print("Error: This build script is intended to be run on Windows.")
        return 1
    
    # Parse arguments
    args = parse_args()
    
    # Get project root directory
    root_dir = Path(__file__).resolve().parent
    
    # Get version
    version = args.version if args.version else get_version()
    print(f"Building Agentic AI v{version}")
    
    # Clean build directories if requested
    if args.clean:
        clean_build_dirs(root_dir)
    
    # Build the executable
    if not build_executable(args, root_dir, version):
        return 1
    
    # Create installer if requested
    if args.installer:
        release_dir = str(root_dir / 'release' / 'windows')
        if not build_installer(root_dir, version, release_dir):
            print("Warning: Installer creation failed, but executable was built successfully.")
    
    print("\nWindows application build completed!")
    print(f"Artifacts can be found in: {root_dir / 'release' / 'windows'}")
    return 0

if __name__ == '__main__':
    sys.exit(main()) 