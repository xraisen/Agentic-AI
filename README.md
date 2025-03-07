# Agentic AI

A powerful AI assistant platform that seamlessly integrates across Windows, macOS, VS Code, and Chrome.

## Features

- **Cross-Platform Support**
  - Windows desktop application
  - macOS desktop application
  - VS Code extension
  - Chrome extension

- **AI Capabilities**
  - Text generation and analysis
  - Code completion and explanation
  - Image analysis
  - Natural language processing
  - Multi-model support

- **Integration Features**
  - Seamless cross-platform synchronization
  - Global hotkeys
  - Context-aware assistance
  - Customizable settings

## Installation

### Desktop Applications

#### Windows
1. Download the latest Windows installer from the releases page
2. Run the installer and follow the setup wizard
3. Launch Agentic AI from the Start menu or desktop shortcut

#### macOS
1. Download the latest DMG file from the releases page
2. Open the DMG file and drag Agentic AI to Applications
3. Launch Agentic AI from Applications or Spotlight

### Extensions

#### VS Code
1. Open VS Code
2. Go to the Extensions view (Ctrl+Shift+X)
3. Search for "Agentic AI"
4. Click Install

#### Chrome
1. Download the Chrome extension from the releases page
2. Open Chrome and go to chrome://extensions/
3. Enable Developer mode
4. Click "Load unpacked" and select the extension directory

## Configuration

### API Keys
1. Get your API keys from:
   - OpenRouter: https://openrouter.ai/
   - Direct API: Configure in settings
2. Add your API keys to the configuration file or environment variables

### Settings
The application can be configured through:
- GUI settings panel
- Configuration file (`config.json`)
- Environment variables

See [CONFIGURATION.md](CONFIGURATION.md) for detailed settings documentation.

## Development

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/xraisen/agentic-ai.git
   cd agentic-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Building

#### Desktop Applications
```bash
# Build for current platform
python build.py

# Build for specific platform
python build.py --platform windows
python build.py --platform mac
```

#### Extensions
```bash
# Build VS Code extension
cd .vscode
npm install
npm run compile
vsce package

# Build Chrome extension
python build.py --platform chrome
```

### Testing
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_api.py
pytest tests/test_ui.py
```

### Code Style
```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

## Project Structure

```
agentic-ai/
├── src/                    # Source code
│   ├── main.py            # Main application entry
│   ├── ui/                # UI components
│   ├── api/               # API integration
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── assets/               # Application assets
├── .vscode/              # VS Code extension
├── chrome/               # Chrome extension
├── build.py              # Build script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Powered by various AI models and APIs

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/xraisen/agentic-ai/issues)
- Community: [Discussions](https://github.com/xraisen/agentic-ai/discussions) 