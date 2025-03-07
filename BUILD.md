# Building Agentic AI

This document describes how to build and package Agentic AI for different platforms.

## Prerequisites

### Windows
- Python 3.8 or higher
- NSIS (Nullsoft Scriptable Install System)
- Git

### macOS
- Python 3.8 or higher
- Xcode Command Line Tools
- Git

### VS Code Extension
- Node.js 14 or higher
- npm
- vsce (will be installed automatically)

### Chrome Extension
- Chrome browser
- Git

## Required Assets

Before building, ensure the following assets are present in the `assets` directory:
- `icon.ico` - Windows application icon
- `icon.icns` - macOS application icon
- `dmg_background.png` - macOS DMG background
- `icon16.png` - Chrome extension icon (16x16)
- `icon48.png` - Chrome extension icon (48x48)
- `icon128.png` - Chrome extension icon (128x128)
- `popup.html` - Chrome extension popup

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-ai.git
cd agentic-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install build requirements:
```bash
pip install -r build_requirements.txt
```

4. Install VS Code extension dependencies:
```bash
cd .vscode
npm install
cd ..
```

## Building

### Running Tests

Before building, run the test suite:
```bash
python tests/test_suite.py
```

### Building All Packages

To build all packages for your platform:
```bash
python build.py
```

This will:
1. Run the test suite
2. Build the standalone application
3. Build the VS Code extension
4. Build the Chrome extension
5. Create installers/packages

### Platform-Specific Builds

You can build for specific platforms using the `--platform` argument:

```bash
# Build Windows package
python build.py --platform windows

# Build macOS package
python build.py --platform mac

# Build VS Code extension
python build.py --platform vscode

# Build Chrome extension
python build.py --platform chrome

# Build all packages (default)
python build.py --platform all
```

### Skipping Tests

To skip running tests during the build:
```bash
python build.py --skip-tests
```

### Output Files

#### Windows
- `dist/AgenticAI.exe` (standalone executable)
- `dist/AgenticAI-Setup.exe` (installer)

#### macOS
- `dist/AgenticAI.app` (application bundle)
- `dist/AgenticAI.dmg` (disk image)

#### VS Code Extension
- `.vscode/agentic-ai-1.0.0.vsix` (VS Code extension package)

#### Chrome Extension
- `dist/chrome_extension.zip` (Chrome extension package)

## Testing the Builds

### Windows
1. Run `dist/AgenticAI-Setup.exe`
2. Follow the installation wizard
3. Launch from Start Menu or Desktop shortcut

### macOS
1. Open `dist/AgenticAI.dmg`
2. Drag AgenticAI.app to Applications
3. Launch from Applications folder

### VS Code Extension
1. Open VS Code
2. Go to Extensions view
3. Click "..." and select "Install from VSIX"
4. Choose `agentic-ai-1.0.0.vsix`

### Chrome Extension
1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable Developer mode
4. Click "Load unpacked"
5. Select the extracted chrome_extension folder

## Troubleshooting

### Common Issues

1. **Build fails with PyInstaller error**
   - Ensure all dependencies are installed
   - Check for missing imports in the code
   - Try cleaning the build directory: `rm -rf build dist`

2. **VS Code extension build fails**
   - Check Node.js version: `node --version`
   - Reinstall dependencies: `cd .vscode && npm install`
   - Check TypeScript compilation: `npm run compile`

3. **Chrome extension not loading**
   - Check manifest.json for errors
   - Verify all assets are present
   - Check Chrome console for errors

4. **Tests failing**
   - Check test logs in `test_results/`
   - Ensure test environment is properly set up
   - Verify test dependencies are installed

5. **macOS DMG creation fails**
   - Ensure Xcode Command Line Tools are installed
   - Check for required assets (icon.icns, dmg_background.png)
   - Verify dmgbuild is installed: `pip install dmgbuild`

6. **Windows installer creation fails**
   - Ensure NSIS is installed and in PATH
   - Check NSIS version: `makensis --version`
   - Verify all required assets are present

### Getting Help

1. Check the logs in `logs/` directory
2. Review test results in `test_results/`
3. Check the [GitHub Issues](https://github.com/yourusername/agentic-ai/issues)
4. Join the [Discord community](https://discord.gg/your-server)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_suite.py`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 