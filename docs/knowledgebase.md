# Agentic AI Knowledge Base

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Configuration](#configuration)
4. [API Integration](#api-integration)
5. [Plugin System](#plugin-system)
6. [Troubleshooting](#troubleshooting)
7. [Development Guidelines](#development-guidelines)

## Architecture Overview

Agentic AI is built with a modular architecture that separates concerns into distinct components:

- **Core Engine**: Handles AI model integration and conversation management
- **GUI Layer**: Provides the user interface using PyQt6
- **Plugin System**: Allows for extensibility and customization
- **System Integration**: Manages OS-level interactions

### Key Design Principles

1. **Modularity**: Each component is self-contained and communicates through well-defined interfaces
2. **Asynchronous Operation**: Uses `asyncio` for non-blocking operations
3. **Event-Driven**: GUI updates are handled through signals and slots
4. **Extensible**: Plugin system allows for easy addition of new features

## Core Components

### AI Engine (`src/core/ai_engine.py`)

The AI engine is responsible for:
- Managing API communication with OpenRouter
- Handling conversation history
- Processing user input
- Managing context and state

### Main Window (`src/gui/main_window.py`)

The GUI component provides:
- Chat interface
- System tray integration
- Input handling
- Response display

## Configuration

### Configuration File (`config.json`)

```json
{
    "OPENROUTER_API_KEY": "your-api-key",
    "SITE_URL": "https://your-site.com",
    "SITE_NAME": "Agentic AI",
    "MODEL": "google/gemini-2.0-flash-thinking-exp:free"
}
```

### Environment Variables

- `AGENTIC_DEBUG`: Enable debug logging
- `AGENTIC_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## API Integration

### OpenRouter API

The application uses OpenRouter's API to access the Gemini model. Key features:
- Asynchronous API calls
- Error handling and retries
- Rate limiting management
- Response caching

### API Usage Example

```python
from core.ai_engine import AIEngine

ai = AIEngine()
response = await ai.get_response("Your prompt here")
```

## Plugin System

### Plugin Structure

Plugins should follow this structure:
```
plugins/
└── your_plugin/
    ├── __init__.py
    ├── plugin.py
    └── requirements.txt
```

### Plugin Interface

```python
class BasePlugin:
    def __init__(self):
        self.name = "Plugin Name"
        self.version = "1.0.0"
        self.description = "Plugin description"

    def initialize(self):
        """Called when the plugin is loaded"""
        pass

    def cleanup(self):
        """Called when the plugin is unloaded"""
        pass
```

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Check your internet connection
   - Verify API key is valid
   - Check OpenRouter service status

2. **GUI Freezing**
   - Check system resources
   - Verify no infinite loops in plugins
   - Check for memory leaks

3. **Plugin Loading Failures**
   - Verify plugin structure
   - Check dependencies
   - Review plugin logs

### Logging

Logs are stored in the `logs` directory:
- `app.log`: Main application log
- `error.log`: Error-specific log
- `debug.log`: Debug information

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all public APIs
- Write unit tests for new features

### Testing

Run tests with:
```bash
pytest tests/
```

### Building

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python src/main.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Version Control

- Use semantic versioning
- Write clear commit messages
- Keep commits focused and atomic
- Review changes before committing 