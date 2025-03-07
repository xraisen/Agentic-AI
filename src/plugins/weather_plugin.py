import requests
from typing import Dict, Any
from .base_plugin import BasePlugin

class WeatherPlugin(BasePlugin):
    """A plugin that provides weather information."""
    
    def __init__(self):
        super().__init__()
        self.name = "Weather Plugin"
        self.version = "1.0.0"
        self.description = "Provides weather information for specified locations"
        self.api_key = None
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def initialize(self) -> bool:
        """Initialize the weather plugin."""
        self.api_key = self.get_setting("api_key")
        return self.api_key is not None
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.api_key = None
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Get weather information for a city."""
        if not self.is_enabled():
            return {"error": "Plugin is disabled"}
            
        if not self.api_key:
            return {"error": "API key not configured"}
            
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except (KeyError, IndexError) as e:
            return {"error": f"Invalid response format: {str(e)}"}
    
    def format_weather(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data into a readable string."""
        if "error" in weather_data:
            return f"Error: {weather_data['error']}"
            
        return (
            f"Temperature: {weather_data['temperature']}°C\n"
            f"Humidity: {weather_data['humidity']}%\n"
            f"Conditions: {weather_data['description']}\n"
            f"Wind Speed: {weather_data['wind_speed']} m/s"
        ) 