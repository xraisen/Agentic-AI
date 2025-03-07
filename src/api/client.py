"""
API Client for Agentic AI
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
import requests
from cryptography.fernet import Fernet
from ..config import validate_config

class APIClient:
    """Client for interacting with AI APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the API client"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fernet = None
        self.session = requests.Session()
        self.last_request_time = 0
        self.error_count = 0
        
    def initialize(self) -> bool:
        """Initialize the API client"""
        try:
            # Validate configuration
            if not validate_config(self.config):
                return False
                
            # Setup encryption if enabled
            if self.config['security']['api_key_encryption']:
                key = self.config['security']['encryption_key'].encode()
                self.fernet = Fernet(key)
                
            # Setup session headers
            self.session.headers.update({
                'User-Agent': f"{self.config['app']['name']}/{self.config['app']['version']}",
                'Content-Type': 'application/json'
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {str(e)}")
            return False
            
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key if encryption is enabled"""
        if self.fernet:
            return self.fernet.encrypt(api_key.encode()).decode()
        return api_key
        
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key if encryption is enabled"""
        if self.fernet:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        return encrypted_key
        
    def _rate_limit(self) -> None:
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1:  # Minimum 1 second between requests
            time.sleep(1 - time_since_last)
        self.last_request_time = time.time()
        
    def _handle_error(self, response: requests.Response) -> None:
        """Handle API errors"""
        self.error_count += 1
        if self.error_count >= self.config['monitoring']['api_errors_threshold']:
            self.logger.error("API error threshold exceeded")
            
        try:
            error_data = response.json()
            self.logger.error(f"API error: {error_data}")
        except:
            self.logger.error(f"API error: {response.text}")
            
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make an API request with error handling"""
        try:
            self._rate_limit()
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 200:
                self.error_count = 0
                return response
                
            self._handle_error(response)
            return None
            
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            return None
            
    def get_completion(self, prompt: str, model: str = None) -> Optional[str]:
        """Get AI completion for a prompt"""
        try:
            # Select model
            if not model:
                model = self.config['api']['openrouter']['models'][0]
                
            # Prepare request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                'Authorization': f"Bearer {self._decrypt_api_key(self.config['api']['openrouter']['api_key'])}",
                'HTTP-Referer': self.config['app']['site_url']
            }
            
            data = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': self.config['ai']['max_tokens'],
                'temperature': self.config['ai']['temperature'],
                'top_p': self.config['ai']['top_p'],
                'frequency_penalty': self.config['ai']['frequency_penalty'],
                'presence_penalty': self.config['ai']['presence_penalty']
            }
            
            # Make request
            response = self._make_request('POST', url, headers=headers, json=data)
            if not response:
                return None
                
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            self.logger.error(f"Failed to get completion: {str(e)}")
            return None
            
    def analyze_image(self, image_url: str, prompt: str = None) -> Optional[str]:
        """Analyze an image using AI"""
        try:
            # Use vision model
            model = "google/gemini-pro-vision"
            
            # Prepare request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                'Authorization': f"Bearer {self._decrypt_api_key(self.config['api']['openrouter']['api_key'])}",
                'HTTP-Referer': self.config['app']['site_url']
            }
            
            # Get image data
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                self.logger.error(f"Failed to fetch image: {image_url}")
                return None
                
            # Prepare messages
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt or "Please analyze this image and provide a detailed description."
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': image_url
                            }
                        }
                    ]
                }
            ]
            
            data = {
                'model': model,
                'messages': messages,
                'max_tokens': self.config['ai']['max_tokens'],
                'temperature': self.config['ai']['temperature']
            }
            
            # Make request
            response = self._make_request('POST', url, headers=headers, json=data)
            if not response:
                return None
                
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            self.logger.error(f"Failed to analyze image: {str(e)}")
            return None 