# Agentic AI

A powerful AI assistant platform that seamlessly integrates across Windows, macOS, VS Code, and Chrome with reliable API connectivity and robust error handling.

## Features

- **Cross-Platform Support**
  - Windows desktop application with improved build process
  - macOS desktop application
  - VS Code extension
  - Chrome extension with proper validation and packaging

- **AI Capabilities**
  - Text generation and analysis through OpenRouter API
  - Code completion and explanation with improved reliability
  - Image analysis capabilities
  - Natural language processing
  - Multi-model support (Gemini, GPT, Claude, and more)

- **Enhanced Reliability**
  - Robust error handling and user-friendly error messages
  - Network retry logic with exponential backoff
  - API key validation and verification
  - Comprehensive logging for troubleshooting

- **Integration Features**
  - Seamless cross-platform synchronization
  - Global hotkeys
  - Context-aware assistance
  - Customizable settings with proper validation

## Installation

### Desktop Applications

#### Windows
1. Download the latest Windows installer from the releases page
2. Run the installer and follow the setup wizard
3. Launch Agentic AI from the Start menu or desktop shortcut
4. On first run, copy config.example.json to config.json and add your API key

#### macOS
1. Download the latest DMG file from the releases page
2. Open the DMG file and drag Agentic AI to Applications
3. Launch Agentic AI from Applications or Spotlight
4. On first run, copy config.example.json to config.json and add your API key

### Extensions

#### VS Code
1. Open VS Code
2. Go to the Extensions view (Ctrl+Shift+X)
3. Search for "Agentic AI"
4. Click Install
5. Configure your API key in the extension settings

#### Chrome
1. Download the latest Chrome extension ZIP from the releases page
2. Extract the ZIP file to a folder
3. Open Chrome and go to chrome://extensions/
4. Enable Developer mode (toggle in top right)
5. Click "Load unpacked" and select the extracted folder
6. Configure your API key in the extension options

## Configuration

### API Keys
1. Get your API keys from:
   - OpenRouter: https://openrouter.ai/
   - Direct API: Configure in settings
2. Add your API key to the configuration file or environment variables
3. API keys should start with "sk-or-v1-" for OpenRouter

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
├── app_launcher.py       # Application launcher
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Error Handling

Agentic AI includes comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **API Errors**: Clear, user-friendly messages for common API errors
- **Configuration Problems**: Validation and clear guidance for fixes
- **Detailed Logging**: Comprehensive logs for troubleshooting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with descriptive commit messages
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Powered by various AI models and APIs via OpenRouter 