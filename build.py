import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import PyInstaller.__main__
import json
import zipfile
from utils.logger import log_action, log_error, log_debug

class Builder:
    """Handles building and packaging of the application."""
    
    def __init__(self):
        self.version = "1.0.0"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.assets_dir = Path("assets")
        self.test_results_dir = Path("test_results")
        
        # Create necessary directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Check required assets
        self._check_required_assets()
        
        log_action("Builder initialized", "Build environment set up")

    def _check_required_assets(self):
        """Check if all required assets are present."""
        required_assets = {
            'icon.ico': 'Windows application icon',
            'icon.icns': 'macOS application icon',
            'dmg_background.png': 'macOS DMG background',
            'icon16.png': 'Chrome extension icon (16x16)',
            'icon48.png': 'Chrome extension icon (48x48)',
            'icon128.png': 'Chrome extension icon (128x128)',
            'popup.html': 'Chrome extension popup'
        }
        
        missing_assets = []
        for asset, description in required_assets.items():
            if not (self.assets_dir / asset).exists():
                missing_assets.append(f"{asset} ({description})")
        
        if missing_assets:
            log_error(Exception("Missing required assets"), 
                     f"Missing assets: {', '.join(missing_assets)}")
            raise FileNotFoundError(f"Missing required assets: {', '.join(missing_assets)}")

    def run_tests(self):
        """Run the test suite."""
        try:
            log_action("Running tests", "Starting test suite")
            result = subprocess.run([sys.executable, "tests/test_suite.py"], 
                                 capture_output=True, text=True)
            
            # Save test output
            with open(self.test_results_dir / "test_output.txt", "w") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nErrors:\n" + result.stderr)
            
            if result.returncode != 0:
                log_error(Exception("Tests failed"), "Test suite execution failed")
                return False
            
            log_action("Tests completed", "All tests passed")
            return True
        except Exception as e:
            log_error(e, "Failed to run tests")
            return False

    def build_windows(self):
        """Build Windows executable."""
        try:
            log_action("Building Windows package", "Starting PyInstaller build")
            
            PyInstaller.__main__.run([
                'src/main.py',
                '--name=AgenticAI',
                '--onefile',
                '--windowed',
                '--icon=assets/icon.ico',
                '--add-data=assets;assets',
                '--add-data=config.json;.',
                '--hidden-import=PyQt6',
                '--hidden-import=aiohttp',
                '--hidden-import=asyncio',
                '--clean'
            ])
            
            # Create Windows installer
            self._create_windows_installer()
            
            log_action("Windows build completed", "Executable and installer created")
            return True
        except Exception as e:
            log_error(e, "Windows build failed")
            return False

    def build_mac(self):
        """Build macOS application."""
        try:
            log_action("Building macOS package", "Starting PyInstaller build")
            
            PyInstaller.__main__.run([
                'src/main.py',
                '--name=AgenticAI',
                '--onefile',
                '--windowed',
                '--icon=assets/icon.icns',
                '--add-data=assets:assets',
                '--add-data=config.json:.',
                '--hidden-import=PyQt6',
                '--hidden-import=aiohttp',
                '--hidden-import=asyncio',
                '--clean'
            ])
            
            # Create macOS DMG
            self._create_mac_dmg()
            
            log_action("macOS build completed", "Application and DMG created")
            return True
        except Exception as e:
            log_error(e, "macOS build failed")
            return False

    def build_vscode_extension(self):
        """Build VS Code extension."""
        try:
            log_action("Building VS Code extension", "Starting extension build")
            
            # Check for Node.js
            try:
                subprocess.run(['node', '--version'], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                log_error(Exception("Node.js not found"), "Node.js is required for VS Code extension build")
                return False
            
            # Build TypeScript files
            subprocess.run(['npm', 'install'], cwd='.vscode', check=True)
            subprocess.run(['npm', 'run', 'compile'], cwd='.vscode', check=True)
            
            # Install vsce globally if not present
            try:
                subprocess.run(['vsce', '--version'], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                subprocess.run(['npm', 'install', '-g', 'vsce'], check=True)
            
            # Package extension
            subprocess.run(['vsce', 'package'], cwd='.vscode', check=True)
            
            log_action("VS Code extension built", "Extension package created")
            return True
        except Exception as e:
            log_error(e, "VS Code extension build failed")
            return False

    def build_chrome_extension(self):
        """Build Chrome extension."""
        try:
            log_action("Building Chrome extension", "Starting extension build")
            
            # Create manifest
            manifest = {
                "manifest_version": 3,
                "name": "Agentic AI",
                "version": self.version,
                "description": "AI Assistant for Chrome",
                "permissions": ["activeTab", "storage"],
                "action": {
                    "default_popup": "popup.html",
                    "default_icon": {
                        "16": "assets/icon16.png",
                        "48": "assets/icon48.png",
                        "128": "assets/icon128.png"
                    }
                },
                "icons": {
                    "16": "assets/icon16.png",
                    "48": "assets/icon48.png",
                    "128": "assets/icon128.png"
                }
            }
            
            # Create extension directory
            chrome_ext_dir = self.build_dir / "chrome_extension"
            chrome_ext_dir.mkdir(exist_ok=True)
            
            # Write manifest
            with open(chrome_ext_dir / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=4)
            
            # Copy extension files
            shutil.copy("assets/popup.html", chrome_ext_dir)
            shutil.copy("assets/icon16.png", chrome_ext_dir / "assets")
            shutil.copy("assets/icon48.png", chrome_ext_dir / "assets")
            shutil.copy("assets/icon128.png", chrome_ext_dir / "assets")
            
            # Create ZIP file
            self._create_zip(chrome_ext_dir, "chrome_extension.zip")
            
            log_action("Chrome extension built", "Extension package created")
            return True
        except Exception as e:
            log_error(e, "Chrome extension build failed")
            return False

    def _create_windows_installer(self):
        """Create Windows installer using NSIS."""
        try:
            # Check for NSIS
            try:
                subprocess.run(['makensis', '--version'], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                log_error(Exception("NSIS not found"), "NSIS is required for Windows installer creation")
                raise
            
            # Create NSIS script
            nsi_script = f"""
            !include "MUI2.nsh"
            Name "Agentic AI"
            OutFile "dist/AgenticAI-Setup.exe"
            InstallDir "$PROGRAMFILES\\AgenticAI"
            
            !insertmacro MUI_PAGE_WELCOME
            !insertmacro MUI_PAGE_DIRECTORY
            !insertmacro MUI_PAGE_INSTFILES
            !insertmacro MUI_PAGE_FINISH
            
            !insertmacro MUI_LANGUAGE "English"
            
            Section "MainSection" SEC01
                SetOutPath "$INSTDIR"
                File /r "dist\\AgenticAI\\*.*"
                CreateDirectory "$SMPROGRAMS\\AgenticAI"
                CreateShortcut "$SMPROGRAMS\\AgenticAI\\AgenticAI.lnk" "$INSTDIR\\AgenticAI.exe"
                CreateShortcut "$DESKTOP\\AgenticAI.lnk" "$INSTDIR\\AgenticAI.exe"
                WriteUninstaller "$INSTDIR\\uninstall.exe"
            SectionEnd
            
            Section "Uninstall"
                Delete "$SMPROGRAMS\\AgenticAI\\AgenticAI.lnk"
                Delete "$DESKTOP\\AgenticAI.lnk"
                RMDir "$SMPROGRAMS\\AgenticAI"
                RMDir /r "$INSTDIR"
            SectionEnd
            """
            
            # Write NSIS script
            with open(self.build_dir / "installer.nsi", "w") as f:
                f.write(nsi_script)
            
            # Run NSIS compiler
            subprocess.run(['makensis', 'installer.nsi'], cwd=self.build_dir, check=True)
            
        except Exception as e:
            log_error(e, "Failed to create Windows installer")
            raise

    def _create_mac_dmg(self):
        """Create macOS DMG file using dmgbuild."""
        try:
            # Check for dmgbuild
            try:
                subprocess.run([sys.executable, '-m', 'dmgbuild', '--version'], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                log_error(Exception("dmgbuild not found"), "dmgbuild is required for macOS DMG creation")
                raise
            
            # Create DMG settings
            settings = {
                'files': ['dist/AgenticAI.app'],
                'symlinks': {'Applications': '/Applications'},
                'icon': 'assets/icon.icns',
                'background': 'assets/dmg_background.png',
                'window_rect': ((200, 120), (800, 400)),
                'icon_size': 100,
                'text_size': 16,
                'icon_locations': {
                    'AgenticAI.app': (200, 190),
                    'Applications': (600, 185)
                }
            }
            
            # Write settings to file
            settings_path = self.build_dir / "dmg_settings.py"
            with open(settings_path, "w") as f:
                f.write(f"settings = {settings}")
            
            # Run dmgbuild
            subprocess.run([
                sys.executable, '-m', 'dmgbuild',
                '-s', str(settings_path),
                'AgenticAI',
                'dist/AgenticAI.dmg'
            ], check=True)
            
        except Exception as e:
            log_error(e, "Failed to create macOS DMG")
            raise

    def _create_zip(self, source_dir, zip_name):
        """Create ZIP archive of a directory."""
        try:
            zip_path = self.dist_dir / zip_name
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
        except Exception as e:
            log_error(e, f"Failed to create ZIP file: {zip_name}")
            raise

    def build_all(self):
        """Build all packages."""
        try:
            # Run tests first
            if not self.run_tests():
                log_error(Exception("Tests failed"), "Build process stopped due to test failures")
                return False
            
            # Build Windows package
            if sys.platform == "win32":
                if not self.build_windows():
                    return False
            
            # Build macOS package
            if sys.platform == "darwin":
                if not self.build_mac():
                    return False
            
            # Build VS Code extension
            if not self.build_vscode_extension():
                return False
            
            # Build Chrome extension
            if not self.build_chrome_extension():
                return False
            
            log_action("All builds completed", "All packages created successfully")
            return True
        except Exception as e:
            log_error(e, "Build process failed")
            return False

def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description='Build Agentic AI packages')
    parser.add_argument('--platform', choices=['windows', 'mac', 'vscode', 'chrome', 'all'],
                      default='all', help='Platform to build for')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    args = parser.parse_args()
    
    try:
        builder = Builder()
        
        # Run tests unless skipped
        if not args.skip_tests:
            if not builder.run_tests():
                print("\nTests failed. Build process stopped.")
                sys.exit(1)
        
        # Build based on platform
        success = True
        if args.platform in ['windows', 'all'] and sys.platform == "win32":
            success = builder.build_windows()
        if args.platform in ['mac', 'all'] and sys.platform == "darwin":
            success = builder.build_mac()
        if args.platform in ['vscode', 'all']:
            success = builder.build_vscode_extension()
        if args.platform in ['chrome', 'all']:
            success = builder.build_chrome_extension()
        
        if success:
            print("\nBuild completed successfully!")
            print("Packages are available in the 'dist' directory.")
        else:
            print("\nBuild failed. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        log_error(e, "Build process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 