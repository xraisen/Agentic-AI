import requests
import json
import os
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..utils.logger import log_action, log_error, log_debug
from ..utils.knowledge_manager import KnowledgeManager

class AIEngine:
    def __init__(self, config_path: str = "config.json"):
        try:
            self.config = self._load_config(config_path)
            self.conversation_history = []
            self.max_history = 100
            self.knowledge_manager = KnowledgeManager()
            log_action("AIEngine initialized", f"Config path: {config_path}")
        except Exception as e:
            log_error(e, "Failed to initialize AIEngine")
            raise

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads configuration from a JSON file."""
        try:
            if not os.path.exists(config_path):
                # Create default config if it doesn't exist
                default_config = {
                    "OPENROUTER_API_KEY": "",
                    "MODEL": "gemini-pro",
                    "SITE_URL": "http://localhost:8000",
                    "SITE_NAME": "Agentic AI"
                }
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                log_action("Created default config", f"File: {config_path}")
                return default_config

            with open(config_path, "r") as f:
                config = json.load(f)
                
            # Validate required fields
            required_fields = ["OPENROUTER_API_KEY", "MODEL"]
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise ValueError(f"Missing required config fields: {', '.join(missing_fields)}")
                
            log_debug("Configuration loaded", f"From: {config_path}")
            return config
        except FileNotFoundError:
            error = FileNotFoundError(f"Configuration file '{config_path}' not found.")
            log_error(error, "Configuration loading")
            raise error
        except json.JSONDecodeError:
            error = ValueError(f"Invalid JSON format in '{config_path}'.")
            log_error(error, "Configuration loading")
            raise error

    def _get_headers(self) -> Dict[str, str]:
        """Generates headers for API requests."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.config.get("SITE_URL", ""),
                "X-Title": self.config.get("SITE_NAME", ""),
            }
            log_debug("Generated API headers", "Headers prepared for request")
            return headers
        except Exception as e:
            log_error(e, "Failed to generate API headers")
            raise

    def _prepare_messages(self, prompt: str, image_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Prepares messages for the API request with context from knowledge manager."""
        try:
            # Update knowledge cache
            self.knowledge_manager.update_knowledge_cache()
            
            # Get relevant context
            recent_conversations = self.knowledge_manager.get_conversation_history(5)
            recent_actions = self.knowledge_manager.get_recent_actions(3)
            relevant_docs = self.knowledge_manager.search_documentation(prompt)
            
            # Prepare context message
            context = ["Previous context:"]
            for conv in recent_conversations:
                context.append(f"- {conv['details']}")
            for action in recent_actions:
                context.append(f"- {action['details']}")
            if relevant_docs:
                context.append("\nRelevant documentation:")
                for doc_name, matches in relevant_docs.items():
                    context.append(f"\nFrom {doc_name}:")
                    for match in matches[:3]:  # Limit to 3 matches per doc
                        context.append(f"- {match}")
            
            context_str = "\n".join(context)
            
            # Prepare messages with context
            messages = [
                {"role": "system", "content": context_str},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]

            if image_url:
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
                log_debug("Image URL added to message", f"URL: {image_url}")

            log_debug("Messages prepared", f"Prompt: {prompt[:50]}...")
            return messages
        except Exception as e:
            log_error(e, "Failed to prepare messages")
            # Fallback to simple message if context preparation fails
            return [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    async def get_response(self, prompt: str, image_url: Optional[str] = None) -> str:
        """Gets a response from Gemini via OpenRouter with context awareness."""
        try:
            log_action("API request initiated", f"Prompt: {prompt[:50]}...")
            messages = self._prepare_messages(prompt, image_url)
            
            data = {
                "model": self.config["MODEL"],
                "messages": messages,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=self._get_headers(),
                    json=data,
                    timeout=30  # Add timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                        
                    result = await response.json()
                    
                    if "choices" not in result or not result["choices"]:
                        raise Exception("Invalid API response format")
                        
                    response_text = result["choices"][0]["message"]["content"]
                    
                    # Update conversation history
                    self._update_history(prompt, response_text)
                    
                    log_action("API response received", "Response processed successfully")
                    return response_text

        except aiohttp.ClientError as e:
            error_msg = f"Network error: {str(e)}"
            log_error(e, "API request failed")
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            log_error(e, "API request failed")
            return error_msg

    def _update_history(self, prompt: str, response: str):
        """Updates the conversation history with new interaction."""
        try:
            timestamp = datetime.now().isoformat()
            self.conversation_history.append({
                "timestamp": timestamp,
                "prompt": prompt,
                "response": response
            })
            
            # Maintain history size limit
            if len(self.conversation_history) > self.max_history:
                self.conversation_history.pop(0)
                log_debug("History limit reached", "Oldest entry removed")

            log_action("Conversation history updated", f"Current size: {len(self.conversation_history)}")
        except Exception as e:
            log_error(e, "Failed to update conversation history")

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the current conversation history."""
        try:
            log_debug("History retrieved", f"Size: {len(self.conversation_history)}")
            return self.conversation_history
        except Exception as e:
            log_error(e, "Failed to get conversation history")
            return []

    def clear_history(self):
        """Clears the conversation history."""
        try:
            self.conversation_history = []
            log_action("History cleared", "Conversation history reset")
        except Exception as e:
            log_error(e, "Failed to clear conversation history")

    def get_knowledge_summary(self) -> str:
        """Get a summary of the current knowledge state."""
        try:
            return self.knowledge_manager.get_knowledge_summary()
        except Exception as e:
            log_error(e, "Failed to get knowledge summary")
            return "Error: Failed to get knowledge summary" 