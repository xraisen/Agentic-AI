from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """Base class for all Agentic AI plugins."""
    
    def __init__(self):
        self.name: str = "Base Plugin"
        self.version: str = "1.0.0"
        self.description: str = "Base plugin description"
        self.enabled: bool = True
        self.settings: Dict[str, Any] = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when the plugin is unloaded."""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }
    
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a plugin setting."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a plugin setting."""
        self.settings[key] = value
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all plugin settings."""
        return self.settings.copy()
    
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set all plugin settings."""
        self.settings = settings.copy() 