#!/usr/bin/env python3
"""
Agentic AI - Interactive Application Launcher

This enhanced launcher script provides a fully interactive experience with
the Agentic AI assistant. It handles proper path setup, module initialization,
and provides both GUI and CLI interfaces.
"""

import os
import sys
import json
import logging
import datetime
import traceback
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

def setup_environment():
    """Set up the application environment"""
    # Determine if we're running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            if hasattr(sys, '_MEIPASS'):  # type: ignore
                root_dir = Path(sys._MEIPASS)  # type: ignore
            else:
                root_dir = Path(os.path.dirname(sys.executable))
        except Exception:
            root_dir = Path(os.path.dirname(sys.executable))
        script_dir = Path(os.path.dirname(sys.executable))
    else:
        # Running from script
        root_dir = Path(__file__).resolve().parent
        script_dir = root_dir

    # Ensure the logs directory exists
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Set up logging with timestamp - FILE ONLY, no console output
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(logs_dir, f"agentic_ai_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file)
            # Removed console handler to clean up the interface
        ]
    )

    # Add root dir to Python path if needed
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    return root_dir, script_dir

class Message:
    """Represents a message in the conversation"""
    
    def __init__(self, role: str, content: Any):
        """
        Initialize a message
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The content of the message (string or structured content)
        """
        self.role = role
        self.content = content
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format for API"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    @staticmethod
    def from_text(role: str, text: str) -> 'Message':
        """Create a message from text"""
        return Message(role, text)
    
    @staticmethod
    def from_multimodal(role: str, text: str, image_url: Optional[str] = None) -> 'Message':
        """Create a multimodal message with text and optional image"""
        content = [{"type": "text", "text": text}]
        
        if image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
            
        return Message(role, content)

class InteractiveAI:
    """Interactive AI interface for OpenRouter API"""
    
    def __init__(self, root_dir):
        """Initialize the AI interface"""
        self.logger = logging.getLogger(__name__)
        self.root_dir = root_dir
        self.config = self._load_config()
        self.history: List[Message] = []
        
        # Check if requests module is available
        if importlib.util.find_spec("requests") is None:
            self.logger.error("Required module 'requests' is not installed")
            print("Error: Required module 'requests' is not installed. Please install it with:")
            print("pip install requests")
        
    def _load_config(self):
        """Load configuration or use defaults"""
        config = {
            "model": "google/gemini-2.0-flash-thinking-exp:free",
            "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
            "max_tokens": 1000,
            "temperature": 0.7,
            "site_url": "https://github.com/xraisen/Agentic-AI",
            "site_name": "Agentic AI"
        }
        
        # Try multiple locations for config.json
        config_locations = [
            os.path.join(self.root_dir, "config.json"),  # PyInstaller temp directory
            "config.json",  # Current working directory
            os.path.join(os.path.dirname(sys.executable), "config.json"),  # Executable directory
            os.path.join(Path(__file__).resolve().parent, "config.json")  # Script directory
        ]
        
        # Try each location
        for config_file in config_locations:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        config.update(file_config)
                    self.logger.info(f"Loaded configuration from {config_file}")
                    break  # Stop after finding first valid config
                except Exception as e:
                    self.logger.error(f"Error loading config from {config_file}: {e}")
        
        # Check if API key is valid format (starts with sk-or-v1-)
        api_key = config.get("api_key", "")
        if api_key and not api_key.startswith("sk-or-v1-"):
            self.logger.warning(f"API key has incorrect format. Should start with 'sk-or-v1-'")
        
        return config
    
    def process_query(self, query: str, image_url: Optional[str] = None) -> str:
        """
        Process a user query and return a response
        
        Args:
            query: The text query from the user
            image_url: Optional URL to an image to include with the query
            
        Returns:
            The response text from the AI
        """
        self.logger.info(f"Processing query: {query}")
        
        # Keep track of conversation history
        if image_url:
            self.history.append(Message.from_multimodal("user", query, image_url))
        else:
            self.history.append(Message.from_text("user", query))
        
        try:
            # Check if OpenRouter API key is set
            if not self.config.get("api_key"):
                response_text = (
                    "API key not configured. Please set your OPENROUTER_API_KEY environment variable "
                    "or add it to config.json.\n\n"
                    "To get an API key:\n"
                    "1. Visit https://openrouter.ai/\n"
                    "2. Sign up or log in\n"
                    "3. Go to https://openrouter.ai/settings/keys\n"
                    "4. Create a new API key\n"
                    "5. Copy the key and add it to config.json"
                )
                self.logger.warning("API key not configured")
                return response_text
            
            # Validate API key format
            api_key = self.config['api_key']
            if not api_key.startswith("sk-or-v1-"):
                self.logger.warning(f"API key has incorrect format. Should start with 'sk-or-v1-'")
                return f"Error: API key has incorrect format. Should start with 'sk-or-v1-'"
                
            # Debug info
            key_preview = f"{api_key[:8]}...{api_key[-8:]}" if len(api_key) > 16 else "[invalid key format]"
            self.logger.info(f"Using API key: {key_preview}")
            self.logger.info(f"Using model: {self.config['model']}")
            
            # Try to use the AI API
            max_retries = 3
            retry_count = 0
            backoff_time = 1  # Starting backoff time in seconds
            
            while retry_count < max_retries:
                try:
                    # Import requests for API calls
                    import requests
                    import json
                    
                    # Format exactly like the example code
                    api_key = self.config['api_key']
                    
                    # Prepare messages for the API
                    api_messages = []
                    for msg in self.history[-5:]:  # Limit to last 5 messages
                        api_messages.append(msg.to_dict())
                    
                    # Following the exact format from the documentation
                    # https://openrouter.ai/docs/api-reference/authentication
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Add optional headers for rankings if provided
                    if self.config.get("site_url"):
                        headers["HTTP-Referer"] = self.config["site_url"]
                    if self.config.get("site_name"):
                        headers["X-Title"] = self.config["site_name"]
                    
                    # Prepare request payload - exact format as example
                    payload = {
                        "model": self.config["model"],
                        "messages": api_messages
                    }
                    
                    # Add optional parameters if present
                    if "max_tokens" in self.config:
                        payload["max_tokens"] = self.config["max_tokens"]
                    if "temperature" in self.config:
                        payload["temperature"] = self.config["temperature"]
                    
                    # Print exactly what we're sending for debugging
                    self.logger.info(f"Request URL: https://openrouter.ai/api/v1/chat/completions")
                    
                    # Make the API request
                    self.logger.info(f"Sending request to OpenRouter API (attempt {retry_count + 1}/{max_retries})")
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    # Check response status and body
                    self.logger.info(f"Response status code: {response.status_code}")
                    
                    # Handle common error status codes with specific messages
                    if response.status_code == 401:
                        self.logger.error("Authentication failed. API key is invalid or expired.")
                        return "Error: Authentication failed. The API key appears to be invalid or expired. Please check your API key in config.json."
                    elif response.status_code == 403:
                        self.logger.error("Access forbidden. Insufficient permissions.")
                        return "Error: Access forbidden. Your API key doesn't have permission to access this model. Please check your OpenRouter account."
                    elif response.status_code == 429:
                        self.logger.error("Rate limit exceeded.")
                        if retry_count < max_retries - 1:
                            # Implement exponential backoff
                            sleep_time = backoff_time * (2 ** retry_count)
                            self.logger.info(f"Retrying in {sleep_time} seconds...")
                            import time
                            time.sleep(sleep_time)
                            retry_count += 1
                            continue
                        else:
                            return "Error: Rate limit exceeded. Please try again later."
                    elif response.status_code >= 500:
                        self.logger.error(f"Server error: {response.status_code}")
                        if retry_count < max_retries - 1:
                            # Implement exponential backoff
                            sleep_time = backoff_time * (2 ** retry_count)
                            self.logger.info(f"Retrying in {sleep_time} seconds...")
                            import time
                            time.sleep(sleep_time)
                            retry_count += 1
                            continue
                        else:
                            return f"Error: Server error (HTTP {response.status_code}). The AI service might be experiencing issues. Please try again later."
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Parse the JSON response
                        response_json = response.json()
                        
                        # Get the actual text response from the JSON
                        if 'choices' in response_json and len(response_json['choices']) > 0:
                            ai_message = response_json['choices'][0]['message']
                            content = ai_message.get('content', '')
                            
                            # Add the response to the conversation history
                            role = ai_message.get('role', 'assistant')
                            # Use from_text even if it's a complex content structure 
                            # - we'll just store it as a string for history purposes
                            self.history.append(Message.from_text(role, str(content)))
                            
                            self.logger.info("Successfully received response from API")
                            return content
                        else:
                            self.logger.error(f"Unexpected response format: {response_json}")
                            return "Error: Received an unexpected response format from the AI service."
                    else:
                        # If we get here, it's another error we didn't handle above
                        self.logger.error(f"Request failed with status code: {response.status_code}")
                        try:
                            error_data = response.json()
                            error_message = error_data.get('error', {}).get('message', f"Unknown error (HTTP {response.status_code})")
                            self.logger.error(f"Error message: {error_message}")
                            return f"Error: {error_message}"
                        except:
                            return f"Error: Request failed with status code {response.status_code}"
                
                except requests.exceptions.Timeout:
                    self.logger.error("Request timed out")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        self.logger.info(f"Retrying (attempt {retry_count + 1}/{max_retries})...")
                        continue
                    else:
                        return "Error: Request timed out after multiple attempts. The service might be experiencing high load."
                        
                except requests.exceptions.ConnectionError:
                    self.logger.error("Connection error")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        self.logger.info(f"Retrying (attempt {retry_count + 1}/{max_retries})...")
                        continue
                    else:
                        return "Error: Could not connect to the AI service. Please check your internet connection and try again."
                        
                except Exception as e:
                    self.logger.error(f"Unexpected error during API request: {e}", exc_info=True)
                    return f"Error: An unexpected problem occurred: {str(e)}"
                
                # If we reach here without returning or continuing, break the loop
                break
                
            # If we've exhausted all retries, return a generic error
            if retry_count >= max_retries:
                return "Error: Failed to get a response after multiple attempts. Please try again later."
            
            # This should never be reached, but adding a fallback return value for type checking
            return "Error: Unknown issue occurred. Please try again."
                
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return f"Error: {str(e)}"

def run_cli(ai: InteractiveAI):
    """Run the command-line interface"""
    logger = logging.getLogger(__name__)
    logger.info("Starting CLI mode")
    
    # Clear the screen for a clean interface
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
    
    print("\n" + "=" * 50)
    print("             Agentic AI")
    print("=" * 50)
    print("Type 'exit' or 'quit' to exit.")
    print("Type 'image URL' to include an image in your query.")
    print("=" * 50 + "\n")
    
    while True:
        try:
            # Get user input
            query = input("\nYou: ")
            
            # Check for exit command
            if query.lower() in ('exit', 'quit', 'q'):
                print("\nExiting Agentic AI. Goodbye!")
                break
            
            # Show a "thinking" indicator
            print("\nAgentic AI: ", end="", flush=True)
            
            # Check for image command
            image_url = None
            if query.lower().startswith('image '):
                parts = query.split(' ', 1)
                if len(parts) > 1:
                    image_url = parts[1].strip()
                    query = input("\nNow enter your question about the image: ")
                    # Clear previous line and show new thinking indicator
                    print("\nAgentic AI: ", end="", flush=True)
                    
            # Process the query - silently logging to file only
            response = ai.process_query(query, image_url)
            
            # Display just the response without any log messages
            print(f"{response}")
            
        except KeyboardInterrupt:
            print("\n\nExiting Agentic AI. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            logger.error(f"CLI error: {e}", exc_info=True)

def main():
    """Main entry point for the application"""
    # Set up environment
    root_dir, script_dir = setup_environment()
    
    # Create logger
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Agentic AI application")
        logger.info(f"Root directory: {root_dir}")
        logger.info(f"Script directory: {script_dir}")
        
        # Initialize the AI interface
        ai = InteractiveAI(root_dir)
        
        # Determine mode (CLI for now, could add GUI later)
        mode = "cli"
        
        if mode == "cli":
            run_cli(ai)
        else:
            # Default to CLI if mode not recognized
            run_cli(ai)
            
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: {e}")
        print("This could be due to missing dependencies.")
        if sys.platform == 'win32':
            input("Press Enter to exit...")
        return 1
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"Error: {e}")
        print("An unexpected error occurred. Check the logs for details.")
        print(traceback.format_exc())
        if sys.platform == 'win32':
            input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 