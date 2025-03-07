# Agentic AI

A fully functional, free, and open-source AI assistant application designed for local execution and comprehensive system integration.

## Overview

Agentic AI is a cross-platform AI assistant that runs locally on your system, providing natural language processing capabilities, system integration, task automation, and voice interaction features.

## Features

- Natural Language Processing (NLP) with multilingual support
- System integration and resource control
- Task automation with customizable scripts
- Conversation management with intelligent caching
- Performance optimization with async/await
- Customizable interface and settings
- Voice interaction capabilities
- Cross-platform support (Windows, macOS, VS Code Extension)

## Installation

### Prerequisites

- Python 3.9 or higher
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-ai.git
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

4. Configure the application:
- Copy `config.example.json` to `config.json`
- Update the configuration with your settings

## Usage

1. Start the application:
```bash
python src/main.py
```

2. For VS Code extension:
- Install the extension from the VS Code marketplace
- Use the command palette (Ctrl+Shift+P) and type "Agentic AI"

## Development

### Project Structure

```
agentic-ai/
├── src/
│   ├── core/           # Core functionality
│   ├── gui/            # GUI components
│   ├── plugins/        # Plugin system
│   └── utils/          # Utility functions
├── docs/              # Documentation
├── tests/             # Test files
├── logs/              # Application logs
└── requirements.txt   # Python dependencies
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Gemini 2.0 Flash Thinking Experimental 01-21 (free) from OpenRouter
- PyQt6 for the GUI framework
- All contributors and maintainers 