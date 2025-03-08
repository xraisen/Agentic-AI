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
        self.options = {
            'onefile': True,  # Whether to build as a single executable file
            'windowed': True,  # Whether to build a windowed application (no console)
            'debug': False,   # Whether to include debug information
        }
        
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
            if chrome_dir.exists():
                print(f"Removing existing Chrome extension directory...")
                shutil.rmtree(chrome_dir)
            chrome_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if source Chrome directory exists
            source_chrome_dir = self.root_dir / 'chrome'
            if not source_chrome_dir.exists():
                raise FileNotFoundError(f"Chrome extension source directory '{source_chrome_dir}' not found.")
            
            # Ensure icons directory exists
            icons_dir = chrome_dir / 'icons'
            icons_dir.mkdir(exist_ok=True)
            
            # Copy icon files from assets
            assets_dir = self.root_dir / 'assets'
            icon_files = {
                'icon16.png': '16',
                'icon32.png': '32',
                'icon48.png': '48',
                'icon128.png': '128'
            }
            
            for icon_file, size in icon_files.items():
                source_icon = assets_dir / icon_file
                if not source_icon.exists():
                    print(f"Warning: Icon {icon_file} not found. Creating placeholder {size}x{size} icon...")
                    # Could use PIL to create placeholder icons here if needed
                    # For now we'll just create empty files
                    with open(icons_dir / icon_file, 'w') as f:
                        f.write(f"/* Placeholder {size}x{size} icon */")
                else:
                    shutil.copy2(source_icon, icons_dir / icon_file)
                    print(f"Copied {icon_file} to extension icons directory")
            
            print(f"Copying files from {source_chrome_dir} to {chrome_dir}...")
            
            # Copy all files from chrome directory
            for file in source_chrome_dir.glob('*'):
                if file.is_file():
                    shutil.copy2(file, chrome_dir)
                    print(f"Copied {file.name}")
                elif file.is_dir() and file.name != 'node_modules':  # Skip node_modules
                    if (chrome_dir / file.name).exists():
                        shutil.rmtree(chrome_dir / file.name)
                    shutil.copytree(file, chrome_dir / file.name)
                    print(f"Copied directory {file.name}")
            
            # Verify all required files exist
            required_files = ['manifest.json', 'popup.html', 'background.js', 'content.js']
            missing_files = [file for file in required_files if not (chrome_dir / file).exists()]
            
            if missing_files:
                raise FileNotFoundError(f"Missing required Chrome extension files: {', '.join(missing_files)}")
            
            # Update the manifest.json with the correct version
            manifest_file = chrome_dir / 'manifest.json'
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                
                manifest_data['version'] = self.version
                
                with open(manifest_file, 'w') as f:
                    json.dump(manifest_data, f, indent=4)
                
                print(f"Updated manifest.json version to {self.version}")
            else:
                raise FileNotFoundError("manifest.json not found in Chrome extension directory.")
            
            # Create distribution ZIP file
            print("Creating Chrome extension ZIP archive...")
            zip_file = self.dist_dir / f'agentic-ai-chrome-{self.version}.zip'
            
            if zip_file.exists():
                zip_file.unlink()
            
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in chrome_dir.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(chrome_dir))
                        print(f"Added {file.relative_to(chrome_dir)} to ZIP")
            
            print(f"Chrome extension successfully built: {zip_file}")
            
            # Copy to release directory
            release_dir = self.root_dir / 'release' / 'chrome'
            release_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(zip_file, release_dir / f'agentic-ai-chrome-{self.version}.zip')
            print(f"Copied Chrome extension to release directory: {release_dir}")
            
            # Add a README.txt with installation instructions
            with open(release_dir / 'README.txt', 'w') as f:
                f.write("Agentic AI - Chrome Extension\n")
                f.write("==========================\n\n")
                f.write("Installation Instructions:\n\n")
                f.write("1. Extract the ZIP file contents to a folder\n")
                f.write("2. Open Chrome and navigate to chrome://extensions/\n")
                f.write("3. Enable Developer Mode (toggle switch in top right)\n")
                f.write("4. Click 'Load unpacked' and select the extracted folder\n")
                f.write("5. The extension should now appear in your Chrome toolbar\n\n")
                f.write("For support, visit: https://github.com/xraisen/agentic-ai\n")
            
            print("Chrome extension build completed!")
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Skipping Chrome extension build.")
        except Exception as e:
            print(f"Unexpected error building Chrome extension: {e}")
            import traceback
            traceback.print_exc()
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
        print("Building Windows application...")
        
        # 1. Setup release directory
        release_dir = self.root_dir / 'release' / 'windows'
        os.makedirs(release_dir, exist_ok=True)
        
        # 2. Ensure the icon exists, if not create a fallback
        icon_path = self.root_dir / 'assets' / 'icon.ico'
        if not icon_path.exists():
            print(f"Warning: Icon file not found at {icon_path}")
            print("Creating fallback icon from PyInstaller resources...")
            fallback_icon = Path(sys.prefix) / 'Lib' / 'site-packages' / 'PyInstaller' / 'bootloader' / 'images' / 'icon-console.ico'
            if fallback_icon.exists():
                shutil.copy2(fallback_icon, icon_path)
                print(f"Created fallback icon at {icon_path}")
            else:
                print("Fallback icon not found. Building without icon.")
                icon_path = None
        
        # 3. Build directly with PyInstaller command line arguments instead of spec file
        # This avoids path escaping issues with the spec file
        icon_arg = f"--icon={icon_path}" if icon_path and icon_path.exists() else ""
        
        try:
            # Run PyInstaller command
            build_cmd = [
                'pyinstaller',
                '--clean',  # Clean PyInstaller cache
                '--onefile' if self.options.get('onefile', False) else '--windowed',
                f'--name=agentic-ai',
                '--add-data=assets;assets',  # Use semicolon for Windows
                '--distpath=dist',
                icon_arg,
                'app_launcher.py'  # Use the app launcher as the main entry point
            ]
            
            # Filter out empty arguments
            build_cmd = [arg for arg in build_cmd if arg]
            
            print(f"Running build command: {' '.join(build_cmd)}")
            subprocess.run(build_cmd, check=True)
            
            # 4. Copy the executable and required files to the release directory
            dist_exe = self.dist_dir / 'agentic-ai.exe'
            if dist_exe.exists():
                shutil.copy2(dist_exe, release_dir / 'AgenticAI.exe')
                print(f"Copied executable to {release_dir / 'AgenticAI.exe'}")
                
                # Copy config.example.json
                config_example = self.root_dir / 'config.example.json'
                if config_example.exists():
                    shutil.copy2(config_example, release_dir / 'config.example.json')
                    print(f"Copied config example to {release_dir}")
                
                # Create a README.txt file with usage instructions
                with open(release_dir / 'README.txt', 'w') as f:
                    f.write("Agentic AI - Windows Application\n")
                    f.write("===============================\n\n")
                    f.write("1. Before first use, copy config.example.json to config.json\n")
                    f.write("2. Edit config.json to add your API key\n")
                    f.write("3. Run AgenticAI.exe\n\n")
                    f.write("For more information, visit: https://github.com/xraisen/agentic-ai\n")
                
                print(f"Created README.txt at {release_dir}")
            else:
                print(f"Error: Build did not produce expected executable at {dist_exe}")
                return
                
            print("Windows application build completed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"Error during Windows build: {e}")
            print(f"Command failed with return code {e.returncode}")
            print("See the logs for more details")
            return
        except Exception as e:
            print(f"Unexpected error during Windows build: {e}")
            import traceback
            traceback.print_exc()
            return
        
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