#!/usr/bin/env python3
"""
Build script for Agentic AI
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json
import zipfile
import tarfile
import platform
import argparse

class Builder:
    """Build system for Agentic AI"""
    
    def __init__(self):
        """Initialize the builder"""
        self.root_dir = Path(__file__).resolve().parent
        self.dist_dir = self.root_dir / 'dist'
        self.build_dir = self.root_dir / 'build'
        self.version = self._get_version()
        self.system = platform.system().lower()
        
    def _get_version(self) -> str:
        """Get version from package.json"""
        try:
            with open(self.root_dir / 'package.json', 'r') as f:
                return json.load(f)['version']
        except:
            return '1.0.0'
            
    def clean(self) -> None:
        """Clean build directories"""
        print("Cleaning build directories...")
        
        # Remove build and dist directories
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Warning: Could not remove directory {dir_path}: {e}")
                    
        # Remove Python cache files
        for pattern in ['*.pyc', '__pycache__', '*.egg-info']:
            for path in self.root_dir.rglob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                except Exception as e:
                    print(f"Warning: Could not remove {path}: {e}")
                    
    def install_dependencies(self) -> None:
        """Install Python dependencies"""
        print("Installing Python dependencies...")
        
        # Install development dependencies
        subprocess.run([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            'requirements-dev.txt'
        ], check=True)
        
        # Install package in development mode
        subprocess.run([
            sys.executable,
            'setup.py',
            'develop'
        ], check=True)
        
    def run_tests(self) -> None:
        """Run tests"""
        print("Running tests...")
        
        # Run Python tests
        subprocess.run([
            sys.executable,
            '-m',
            'pytest',
            'tests/'
        ], check=True)
        
    def build_python_package(self) -> None:
        """Build Python package"""
        print("Building Python package...")
        
        # Build package
        subprocess.run([
            sys.executable,
            'setup.py',
            'sdist',
            'bdist_wheel'
        ], check=True)
        
    def build_vscode_extension(self) -> None:
        """Build VS Code extension"""
        print("Building VS Code extension...")
        
        try:
            # Check if Node.js and npm are installed
            try:
                subprocess.run(['npm', '--version'], check=True, capture_output=True, text=True)
                print("npm is installed, proceeding with VS Code extension build")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("npm is not installed or not in PATH. Cannot build VS Code extension.")
                return

            # Install vsce globally if not already installed
            try:
                subprocess.run(['vsce', '--version'], check=True, capture_output=True, text=True)
                print("vsce is already installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Installing vsce globally...")
                subprocess.run(['npm', 'install', '-g', '@vscode/vsce'], check=True)
            
            # Install VS Code extension dependencies
            print("Installing VS Code extension dependencies...")
            subprocess.run([
                'npm',
                'install',
                '--prefix',
                '.vscode'
            ], check=True)
            
            # Build extension
            print("Compiling TypeScript...")
            subprocess.run([
                'npm',
                'run',
                'compile',
                '--prefix',
                '.vscode'
            ], check=True)
            
            # Package extension
            print("Packaging VS Code extension...")
            # Create dist directory if it doesn't exist
            os.makedirs(self.dist_dir, exist_ok=True)
            
            subprocess.run([
                'vsce',
                'package',
                '--out',
                str(self.dist_dir / f'agentic-ai-{self.version}.vsix'),
                '--baseContentUrl',
                'https://github.com/xraisen/agentic-ai/releases/download',
                '--baseImagesUrl',
                'https://github.com/xraisen/agentic-ai/releases/download'
            ], check=True)
            
            print("VS Code extension successfully built!")
            
        except Exception as e:
            print(f"Warning: Could not build VS Code extension: {e}")
            print("Skipping VS Code extension build.")
        
    def build_chrome_extension(self) -> None:
        """Build Chrome extension"""
        print("Building Chrome extension...")
        
        try:
            # Create Chrome extension directory
            chrome_dir = self.dist_dir / 'chrome'
            chrome_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if source Chrome directory exists
            source_chrome_dir = self.root_dir / 'chrome'
            if not source_chrome_dir.exists():
                print(f"Warning: Chrome extension source directory '{source_chrome_dir}' not found.")
                return
                
            print(f"Copying files from {source_chrome_dir} to {chrome_dir}...")
            
            # Copy extension files
            for file in source_chrome_dir.glob('*'):
                try:
                    if file.is_file():
                        shutil.copy2(file, chrome_dir)
                        print(f"Copied {file.name}")
                    else:
                        if chrome_dir / file.name and (chrome_dir / file.name).exists():
                            shutil.rmtree(chrome_dir / file.name)
                        shutil.copytree(file, chrome_dir / file.name)
                        print(f"Copied directory {file.name}")
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")
            
            # Check if manifest.json exists
            manifest_file = chrome_dir / 'manifest.json'
            if not manifest_file.exists():
                print("Warning: manifest.json not found in Chrome extension directory.")
                return
                
            # Create ZIP archive
            print("Creating Chrome extension ZIP archive...")
            zip_file = self.dist_dir / f'agentic-ai-chrome-{self.version}.zip'
            
            # Remove existing zip file if it exists
            if zip_file.exists():
                zip_file.unlink()
                
            with zipfile.ZipFile(
                zip_file,
                'w',
                zipfile.ZIP_DEFLATED
            ) as zipf:
                for file in chrome_dir.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(chrome_dir))
                        print(f"Added {file.relative_to(chrome_dir)} to ZIP")
                        
            print(f"Chrome extension successfully built: {zip_file}")
            
        except Exception as e:
            print(f"Warning: Could not build Chrome extension: {e}")
            print("Skipping Chrome extension build.")
        
    def build_desktop_app(self) -> None:
        """Build desktop application"""
        print("Building desktop application...")
        
        if self.system == 'windows':
            self._build_windows_app()
        elif self.system == 'darwin':
            self._build_macos_app()
        else:
            print(f"Unsupported system: {self.system}")
            
    def _build_windows_app(self) -> None:
        """Build Windows application"""
        # Create Windows executable with debugging enabled 
        print("Building Windows application with debug information...")
        subprocess.run([
            'pyinstaller',
            '--name=AgenticAI',
            # Skip windowed mode and icon for now to avoid build issues
            # '--windowed',
            # '--icon=assets/icon.ico',
            '--debug=all',  # Enable all debugging information
            '--add-data=assets;assets',
            # Add paths to help PyInstaller find modules
            '--paths=src',
            'src/main.py'
        ], check=True)
        
        # Create installer - skipping for now as innosetup is not installed
        # subprocess.run([
        #     'innosetup',
        #     'installer.iss'
        # ], check=True)
        
    def _build_macos_app(self) -> None:
        """Build macOS application"""
        # Create macOS application bundle
        subprocess.run([
            'pyinstaller',
            '--name=AgenticAI',
            '--windowed',
            '--icon=assets/icon.icns',
            '--add-data=assets:assets',
            'src/main.py'
        ], check=True)
        
        # Create DMG
        subprocess.run([
            'create-dmg',
            '--volname=AgenticAI',
            '--window-pos=200,120',
            '--window-size=800,400',
            '--icon-size=100',
            '--icon=AgenticAI.app=200,190',
            '--hide-extension=AgenticAI.app',
            '--app-drop-link=600,185',
            str(self.dist_dir / f'AgenticAI-{self.version}.dmg'),
            str(self.build_dir / 'AgenticAI.app')
        ], check=True)
        
    def build_platform(self, platform_name=None):
        """Build for a specific platform"""
        print(f"Building for platform: {platform_name or self.system}")
        
        # Clean
        self.clean()
        
        # Create dist directory
        os.makedirs(self.dist_dir, exist_ok=True)
        
        if platform_name == 'windows' or (platform_name is None and self.system == 'windows'):
            self._build_windows_app()
        elif platform_name == 'mac' or (platform_name is None and self.system == 'darwin'):
            self._build_macos_app()
        elif platform_name == 'vscode':
            self.build_vscode_extension()
        elif platform_name == 'chrome':
            self.build_chrome_extension()
        else:
            print(f"Unsupported platform: {platform_name}")
        
    def build_all(self) -> None:
        """Build all components"""
        try:
            # Clean
            self.clean()
            
            # Install dependencies
            self.install_dependencies()
            
            # Run tests
            self.run_tests()
            
            # Build components
            self.build_python_package()
            self.build_vscode_extension()
            self.build_chrome_extension()
            self.build_desktop_app()
            
            print("Build completed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Agentic AI')
    parser.add_argument('--platform', choices=['windows', 'mac', 'vscode', 'chrome'], help='Platform to build for')
    args = parser.parse_args()
    
    builder = Builder()
    if args.platform:
        builder.build_platform(args.platform)
    else:
        builder.build_all() 