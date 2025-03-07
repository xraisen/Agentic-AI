"""
Configuration management for Agentic AI
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load configuration from environment and config file"""
    # Load environment variables
    load_dotenv()
    
    # Default configuration
    config = {
        'version': '1.0.0',
        'api': {
            'openrouter': {
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'models': ['google/gemini-pro', 'google/gemini-pro-vision']
            },
            'direct': {
                'api_key': os.getenv('DIRECT_API_KEY'),
                'models': ['google/gemini-pro']
            }
        },
        'app': {
            'name': 'Agentic AI',
            'version': '1.0.0',
            'site_url': os.getenv('AGENTIC_AI_SITE_URL', 'https://agentic-ai.example.com'),
            'log_level': os.getenv('AGENTIC_AI_LOG_LEVEL', 'INFO'),
            'cache_dir': os.getenv('AGENTIC_AI_CACHE_DIR', 'cache'),
            'assets_dir': os.getenv('AGENTIC_AI_ASSETS_DIR', 'assets')
        },
        'ai': {
            'max_tokens': int(os.getenv('AGENTIC_AI_MAX_TOKENS', '2048')),
            'temperature': float(os.getenv('AGENTIC_AI_TEMPERATURE', '0.7')),
            'top_p': float(os.getenv('AGENTIC_AI_TOP_P', '0.9')),
            'frequency_penalty': float(os.getenv('AGENTIC_AI_FREQUENCY_PENALTY', '0.0')),
            'presence_penalty': float(os.getenv('AGENTIC_AI_PRESENCE_PENALTY', '0.0')),
            'timeout': int(os.getenv('AGENTIC_AI_TIMEOUT', '30'))
        },
        'security': {
            'encryption_key': os.getenv('AGENTIC_AI_ENCRYPTION_KEY'),
            'api_key_encryption': os.getenv('AGENTIC_AI_API_KEY_ENCRYPTION', 'true').lower() == 'true',
            'save_history': os.getenv('AGENTIC_AI_SAVE_HISTORY', 'true').lower() == 'true',
            'encrypt_history': os.getenv('AGENTIC_AI_ENCRYPT_HISTORY', 'true').lower() == 'true',
            'max_history_items': int(os.getenv('AGENTIC_AI_MAX_HISTORY_ITEMS', '1000'))
        },
        'monitoring': {
            'activity_tracking': os.getenv('AGENTIC_AI_ACTIVITY_TRACKING', 'true').lower() == 'true',
            'performance_metrics': os.getenv('AGENTIC_AI_PERFORMANCE_METRICS', 'true').lower() == 'true',
            'api_errors_threshold': int(os.getenv('AGENTIC_AI_API_ERRORS_THRESHOLD', '5')),
            'response_time_threshold': int(os.getenv('AGENTIC_AI_RESPONSE_TIME_THRESHOLD', '5000')),
            'memory_usage_threshold': int(os.getenv('AGENTIC_AI_MEMORY_USAGE_THRESHOLD', '500'))
        },
        'desktop': {
            'startup': os.getenv('AGENTIC_AI_STARTUP', 'true').lower() == 'true',
            'global_hotkey': os.getenv('AGENTIC_AI_GLOBAL_HOTKEY', 'Ctrl+Shift+A'),
            'theme': os.getenv('AGENTIC_AI_THEME', 'light')
        },
        'extensions': {
            'vscode': {
                'enabled': os.getenv('AGENTIC_AI_VSCODE_ENABLED', 'true').lower() == 'true',
                'code_completion': os.getenv('AGENTIC_AI_VSCODE_CODE_COMPLETION', 'true').lower() == 'true',
                'code_explanation': os.getenv('AGENTIC_AI_VSCODE_CODE_EXPLANATION', 'true').lower() == 'true',
                'refactoring': os.getenv('AGENTIC_AI_VSCODE_REFACTORING', 'true').lower() == 'true'
            },
            'chrome': {
                'enabled': os.getenv('AGENTIC_AI_CHROME_ENABLED', 'true').lower() == 'true',
                'page_analysis': os.getenv('AGENTIC_AI_CHROME_PAGE_ANALYSIS', 'true').lower() == 'true',
                'text_selection': os.getenv('AGENTIC_AI_CHROME_TEXT_SELECTION', 'true').lower() == 'true',
                'screenshot_analysis': os.getenv('AGENTIC_AI_CHROME_SCREENSHOT_ANALYSIS', 'true').lower() == 'true'
            }
        },
        'logging': {
            'file': os.getenv('AGENTIC_AI_LOG_FILE', 'logs/agentic_ai.log'),
            'max_size': int(os.getenv('AGENTIC_AI_LOG_MAX_SIZE', '10485760')),
            'backup_count': int(os.getenv('AGENTIC_AI_LOG_BACKUP_COUNT', '5')),
            'types': os.getenv('AGENTIC_AI_LOG_TYPES', 'error,info,debug,warning').split(',')
        },
        'development': {
            'dev_mode': os.getenv('AGENTIC_AI_DEV_MODE', 'false').lower() == 'true',
            'debug': os.getenv('AGENTIC_AI_DEBUG', 'false').lower() == 'true',
            'test_mode': os.getenv('AGENTIC_AI_TEST_MODE', 'false').lower() == 'true'
        }
    }
    
    # Load config file if exists
    config_file = Path('config.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file: {str(e)}")
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration settings"""
    try:
        # Validate required API keys
        if not config['api']['openrouter']['api_key']:
            print("Error: OPENROUTER_API_KEY is required")
            return False
            
        if not config['api']['direct']['api_key']:
            print("Error: DIRECT_API_KEY is required")
            return False
            
        # Validate encryption key if encryption is enabled
        if config['security']['api_key_encryption'] and not config['security']['encryption_key']:
            print("Error: AGENTIC_AI_ENCRYPTION_KEY is required when API key encryption is enabled")
            return False
            
        # Validate numeric ranges
        if not 0 <= config['ai']['temperature'] <= 1:
            print("Error: Temperature must be between 0 and 1")
            return False
            
        if not 0 <= config['ai']['top_p'] <= 1:
            print("Error: Top P must be between 0 and 1")
            return False
            
        if config['ai']['max_tokens'] <= 0:
            print("Error: Max tokens must be positive")
            return False
            
        if config['ai']['timeout'] <= 0:
            print("Error: Timeout must be positive")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error validating config: {str(e)}")
        return False 