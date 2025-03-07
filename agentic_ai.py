# agentic_ai.py
import requests
import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agentic_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories() -> None:
    """Create necessary directories if they don't exist."""
    directories = ['logs', 'cache', 'assets']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def validate_config(config: Dict[str, Any]) -> Optional[str]:
    """Validate configuration values."""
    if not config.get("OPENROUTER_API_KEY"):
        return "OPENROUTER_API_KEY is required"
    if not config.get("MODEL"):
        return "MODEL is required"
    if not config.get("SITE_URL"):
        return "SITE_URL is required"
    if not config.get("SITE_NAME"):
        return "SITE_NAME is required"
    return None

def load_config(config_file: str = "config.json") -> Optional[Dict[str, Any]]:
    """Loads configuration from a JSON file."""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            
            # Validate configuration
            error = validate_config(config)
            if error:
                logger.error(f"Configuration validation failed: {error}")
                print(f"Error: {error}")
                print("Please check your config.json file and ensure all required fields are set.")
                return None
                
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_file}' not found")
        print(f"Error: Configuration file '{config_file}' not found.")
        print("Please copy config.example.json to config.json and update the settings.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in '{config_file}': {e}")
        print(f"Error: Invalid JSON format in '{config_file}'.")
        print("Please ensure your config.json file contains valid JSON.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        print(f"Error: Unexpected error loading configuration: {e}")
        return None

def get_gemini_response(prompt: str, image_url: Optional[str] = None) -> str:
    """Gets a response from Gemini via OpenRouter."""
    config = load_config()
    if not config:
        return "Configuration error. Please check the logs for details."

    headers = {
        "Authorization": f"Bearer {config['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.get("SITE_URL", ""),
        "X-Title": config.get("SITE_NAME", ""),
    }

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if image_url:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    data = {
        "model": config["MODEL"],
        "messages": messages,
        "max_tokens": config.get("MAX_TOKENS", 1000),
        "temperature": config.get("TEMPERATURE", 0.7),
        "stream": False,
        "headers": {
            "HTTP-Referer": config.get("SITE_URL", ""),
            "X-Title": config.get("SITE_NAME", "")
        }
    }

    try:
        logger.info(f"Sending request to Gemini API with prompt: {prompt[:50]}...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            data=json.dumps(data),
            timeout=30  # Add timeout
        )
        
        if response.status_code == 401:
            logger.error("Authentication failed. Please check your OpenRouter API key.")
            return "Error: Authentication failed. Please check your OpenRouter API key in config.json"
        elif response.status_code == 403:
            logger.error("Access forbidden. Please check your API key permissions.")
            return "Error: Access forbidden. Please check your API key permissions."
        elif response.status_code == 429:
            logger.error("Rate limit exceeded. Please try again later.")
            return "Error: Rate limit exceeded. Please try again later."
        
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        logger.info("Successfully received response from Gemini API")
        return result
    except requests.exceptions.Timeout:
        logger.error("Request to Gemini API timed out")
        return "Error: Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'status_code'):
            return f"Error: API request failed with status code {e.response.status_code}. Please check your configuration and try again."
        return f"Request error: {e}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Response parsing error: {e}")
        return f"Error: Failed to parse API response. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Unexpected error: {e}"

def main():
    """Main entry point for the application."""
    try:
        setup_directories()
        logger.info("Starting Agentic AI application")

        # Check if config.json exists
        if not os.path.exists("config.json"):
            print("Error: config.json not found!")
            print("Please copy config.example.json to config.json and update the settings.")
            return

        # Test 0: Basic Greeting
        print("\n=== Test 0: Basic Greeting ===")
        greeting_prompt = "Hello! How are you today?"
        logger.info(f"Processing greeting: {greeting_prompt}")
        ai_response = get_gemini_response(greeting_prompt)
        print("\nAgentic AI:", ai_response)

        # Test 1: Basic text query
        print("\n=== Test 1: Basic Text Query ===")
        user_prompt = "What is the capital of France?"
        logger.info(f"Processing text prompt: {user_prompt}")
        ai_response = get_gemini_response(user_prompt)
        print("\nAgentic AI:", ai_response)

        # Test 2: Complex text query
        print("\n=== Test 2: Complex Text Query ===")
        complex_prompt = "Write a Python function to calculate the Fibonacci sequence recursively."
        logger.info(f"Processing complex prompt: {complex_prompt}")
        ai_response = get_gemini_response(complex_prompt)
        print("\nAgentic AI:", ai_response)

        # Test 3: Code explanation
        print("\n=== Test 3: Code Explanation ===")
        code_prompt = "Explain this code:\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        logger.info(f"Processing code explanation: {code_prompt}")
        ai_response = get_gemini_response(code_prompt)
        print("\nAgentic AI:", ai_response)

        # Test 4: Image analysis (using a different model)
        print("\n=== Test 4: Image Analysis ===")
        # Temporarily switch to a model that supports image analysis
        config = load_config()
        if config:
            original_model = config["MODEL"]
            config["MODEL"] = "google/gemini-pro-vision"
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/JPEG_example_flower.jpg/800px-JPEG_example_flower.jpg"
            image_prompt = "What is in this image? Describe it in detail."
            logger.info(f"Processing image prompt: {image_prompt}")
            ai_response_image = get_gemini_response(image_prompt, image_url)
            print("\nAgentic AI (Image):", ai_response_image)
            
            # Restore original model
            config["MODEL"] = original_model
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()