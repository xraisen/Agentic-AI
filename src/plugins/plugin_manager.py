import os
import importlib
import json
from typing import Dict, List, Type, Optional
from .base_plugin import BasePlugin

class PluginManager:
    """Manages the loading and lifecycle of plugins."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.settings_file = "plugin_settings.json"
        self.load_settings()
        
    def load_settings(self) -> None:
        """Load plugin settings from file."""
        try:
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
        except json.JSONDecodeError:
            self.settings = {}
    
    def save_settings(self) -> None:
        """Save plugin settings to file."""
        settings = {
            name: plugin.get_settings()
            for name, plugin in self.plugins.items()
        }
        with open(self.settings_file, "w") as f:
            json.dump(settings, f, indent=4)
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directory."""
        plugins = []
        for item in os.listdir(self.plugin_dir):
            if os.path.isdir(os.path.join(self.plugin_dir, item)):
                if os.path.exists(os.path.join(self.plugin_dir, item, "__init__.py")):
                    plugins.append(item)
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name."""
        try:
            # Import the plugin module
            module = importlib.import_module(f"plugins.{plugin_name}.plugin")
            
            # Find the plugin class (should be the first class that inherits from BasePlugin)
            plugin_class = None
            for item in dir(module):
                obj = getattr(module, item)
                if (isinstance(obj, type) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                print(f"No valid plugin class found in {plugin_name}")
                return False
            
            # Create and initialize the plugin
            plugin = plugin_class()
            if plugin_name in self.settings:
                plugin.set_settings(self.settings[plugin_name])
            
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                return True
            else:
                print(f"Failed to initialize plugin {plugin_name}")
                return False
                
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {str(e)}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin by name."""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].cleanup()
                del self.plugins[plugin_name]
                return True
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {str(e)}")
                return False
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Get all loaded plugins."""
        return self.plugins.copy()
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enable()
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].disable()
            return True
        return False
    
    def load_all_plugins(self) -> None:
        """Load all discovered plugins."""
        for plugin_name in self.discover_plugins():
            self.load_plugin(plugin_name)
    
    def unload_all_plugins(self) -> None:
        """Unload all plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
    
    def __del__(self):
        """Clean up when the plugin manager is destroyed."""
        self.unload_all_plugins()
        self.save_settings() 