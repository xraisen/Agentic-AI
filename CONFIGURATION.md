# Configuration Guide

This document provides detailed information about configuring Agentic AI.

## Configuration File

The main configuration file is `config.json`. Here's a complete example with all available options:

```json
{
    "version": "1.0.0",
    "api": {
        "openrouter": {
            "api_key": "your_openrouter_api_key",
            "models": {
                "text": "google/gemini-pro",
                "code": "google/gemini-pro",
                "image": "google/gemini-pro-vision"
            }
        },
        "direct": {
            "api_key": "your_direct_api_key",
            "endpoint": "https://api.example.com/v1",
            "models": {
                "text": "gpt-4",
                "code": "gpt-4",
                "image": "gpt-4-vision"
            }
        }
    },
    "application": {
        "name": "Agentic AI",
        "version": "1.0.0",
        "site_url": "https://agentic-ai.example.com",
        "log_level": "INFO",
        "cache_dir": "cache",
        "assets_dir": "assets"
    },
    "ai": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop_sequences": [],
        "timeout": 30
    },
    "desktop": {
        "windows": {
            "startup": true,
            "global_hotkey": "Ctrl+Shift+A",
            "theme": "light"
        },
        "mac": {
            "startup": true,
            "global_hotkey": "Cmd+Shift+A",
            "theme": "light"
        }
    },
    "extensions": {
        "vscode": {
            "enabled": true,
            "features": {
                "code_completion": true,
                "code_explanation": true,
                "refactoring": true
            }
        },
        "chrome": {
            "enabled": true,
            "features": {
                "page_analysis": true,
                "text_selection": true,
                "screenshot_analysis": true
            }
        }
    },
    "logging": {
        "file": "logs/agentic_ai.log",
        "max_size": 10485760,
        "backup_count": 5,
        "log_types": ["error", "info", "debug", "warning"]
    },
    "security": {
        "api_key_encryption": true,
        "environment_variables": {
            "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
            "DIRECT_API_KEY": "DIRECT_API_KEY"
        },
        "data_privacy": {
            "save_history": true,
            "encrypt_history": true,
            "max_history_items": 1000
        }
    },
    "monitoring": {
        "activity_tracking": true,
        "performance_metrics": true,
        "alert_thresholds": {
            "api_errors": 5,
            "response_time": 5000,
            "memory_usage": 500
        }
    }
}
```

## Configuration Options

### API Configuration

#### OpenRouter API
- `api_key`: Your OpenRouter API key
- `models`: Model configurations for different tasks
  - `text`: Model for text generation
  - `code`: Model for code-related tasks
  - `image`: Model for image analysis

#### Direct API
- `api_key`: Your direct API key
- `endpoint`: API endpoint URL
- `models`: Model configurations (same as OpenRouter)

### Application Settings

- `name`: Application name
- `version`: Application version
- `site_url`: Website URL
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `cache_dir`: Directory for cached data
- `assets_dir`: Directory for application assets

### AI Settings

- `max_tokens`: Maximum tokens in response
- `temperature`: Response randomness (0.0-1.0)
- `top_p`: Nucleus sampling parameter
- `frequency_penalty`: Penalty for frequent tokens
- `presence_penalty`: Penalty for new tokens
- `stop_sequences`: Sequences to stop generation
- `timeout`: API request timeout in seconds

### Desktop Settings

#### Windows
- `startup`: Launch on system startup
- `global_hotkey`: Global shortcut key
- `theme`: UI theme (light/dark)

#### macOS
- Same options as Windows

### Extension Settings

#### VS Code
- `enabled`: Enable/disable extension
- `features`: Available features
  - `code_completion`: Enable code completion
  - `code_explanation`: Enable code explanation
  - `refactoring`: Enable code refactoring

#### Chrome
- `enabled`: Enable/disable extension
- `features`: Available features
  - `page_analysis`: Enable page analysis
  - `text_selection`: Enable text selection
  - `screenshot_analysis`: Enable screenshot analysis

### Logging Settings

- `file`: Log file path
- `max_size`: Maximum log file size
- `backup_count`: Number of backup files
- `log_types`: Types of logs to record

### Security Settings

- `api_key_encryption`: Enable API key encryption
- `environment_variables`: Environment variable names
- `data_privacy`: Privacy settings
  - `save_history`: Save conversation history
  - `encrypt_history`: Encrypt history
  - `max_history_items`: Maximum history items

### Monitoring Settings

- `activity_tracking`: Enable activity tracking
- `performance_metrics`: Enable performance metrics
- `alert_thresholds`: Alert thresholds
  - `api_errors`: Maximum API errors
  - `response_time`: Maximum response time
  - `memory_usage`: Maximum memory usage

## Environment Variables

You can override configuration settings using environment variables:

```bash
# API Keys
OPENROUTER_API_KEY=your_key
DIRECT_API_KEY=your_key

# Application Settings
AGENTIC_AI_LOG_LEVEL=DEBUG
AGENTIC_AI_CACHE_DIR=/path/to/cache

# Security
AGENTIC_AI_ENCRYPTION_KEY=your_key
```

## Configuration Validation

The application validates the configuration file on startup. Invalid configurations will be logged and may prevent the application from starting.

## Updating Configuration

1. Stop the application
2. Edit `config.json`
3. Restart the application

For runtime changes:
1. Use the settings panel in the application
2. Changes are saved automatically
3. Some changes require restart

## Troubleshooting

### Common Issues

1. **Invalid API Key**
   - Check API key format
   - Verify API key permissions
   - Check environment variables

2. **Configuration File Not Found**
   - Verify file path
   - Check file permissions
   - Create from example if missing

3. **Invalid Configuration**
   - Check JSON syntax
   - Verify required fields
   - Check value types

### Logging

Check the log file for detailed error messages:
```bash
tail -f logs/agentic_ai.log
```

## Best Practices

1. **API Keys**
   - Use environment variables
   - Enable encryption
   - Rotate keys regularly

2. **Logging**
   - Set appropriate log level
   - Monitor log size
   - Regular log rotation

3. **Security**
   - Enable encryption
   - Use secure storage
   - Regular security audits

4. **Performance**
   - Monitor resource usage
   - Set appropriate timeouts
   - Cache when possible 