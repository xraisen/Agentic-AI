import pytest
import asyncio
from pathlib import Path
import json
import shutil
from src.core.ai_engine import AIEngine
from src.gui.main_window import MainWindow
from src.plugins.weather_plugin import WeatherPlugin
from src.plugins.plugin_manager import PluginManager
from src.utils.logger import log_action, log_error, log_debug

class TestScenarios:
    """Test scenarios for Agentic AI system."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        self.config_path = Path("tests/test_config.json")
        self.test_data_dir = Path("tests/test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create test configuration
        config = {
            "api_key": "test_key",
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.7,
            "plugins": ["weather"]
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f)
        
        # Initialize components
        self.ai_engine = AIEngine(self.config_path)
        self.plugin_manager = PluginManager()
        self.main_window = MainWindow(self.ai_engine)
        
        yield
        
        # Cleanup
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
        self.config_path.unlink(missing_ok=True)
        await self.ai_engine.close()
        self.main_window.close()

    async def test_basic_conversation(self):
        """Test basic conversation flow."""
        # Test simple query
        response = await self.ai_engine.get_response("Hello, how are you?")
        assert response is not None
        assert len(response) > 0
        
        # Test context retention
        response = await self.ai_engine.get_response("What was my previous message?")
        assert "Hello" in response.lower()
        
        # Test conversation history
        history = self.ai_engine.get_history()
        assert len(history) >= 2

    async def test_plugin_integration(self):
        """Test plugin system integration."""
        # Register weather plugin
        weather_plugin = WeatherPlugin()
        self.plugin_manager.register_plugin(weather_plugin)
        
        # Test plugin command
        response = await self.ai_engine.get_response("What's the weather in London?")
        assert response is not None
        assert "weather" in response.lower()
        
        # Test plugin error handling
        response = await self.ai_engine.get_response("What's the weather in InvalidCity123?")
        assert "error" in response.lower() or "unavailable" in response.lower()

    async def test_error_handling(self):
        """Test error handling and recovery."""
        # Test invalid API key
        invalid_config = {
            "api_key": "invalid_key",
            "model": "gpt-4"
        }
        with open(self.config_path, "w") as f:
            json.dump(invalid_config, f)
        
        try:
            await self.ai_engine.get_response("Test message")
            assert False, "Should have raised an error"
        except Exception as e:
            assert "api" in str(e).lower()
        
        # Test network error simulation
        self.ai_engine.api_url = "https://invalid-url.com"
        try:
            await self.ai_engine.get_response("Test message")
            assert False, "Should have raised a network error"
        except Exception as e:
            assert "network" in str(e).lower() or "connection" in str(e).lower()

    async def test_memory_management(self):
        """Test memory and resource management."""
        # Generate long conversation
        for i in range(20):
            await self.ai_engine.get_response(f"Message {i}")
        
        # Check history size limit
        history = self.ai_engine.get_history()
        assert len(history) <= 10  # Assuming max history is 10
        
        # Test memory cleanup
        self.ai_engine.clear_history()
        assert len(self.ai_engine.get_history()) == 0

    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        async def make_request(i):
            return await self.ai_engine.get_response(f"Concurrent request {i}")
        
        # Make multiple concurrent requests
        tasks = [make_request(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests completed
        assert len(responses) == 5
        assert all(r is not None for r in responses)

    async def test_gui_interaction(self):
        """Test GUI interaction and responsiveness."""
        # Test message display
        test_message = "Test GUI message"
        self.main_window.display_message(test_message)
        
        # Test response handling
        response = await self.ai_engine.get_response(test_message)
        self.main_window.handle_response(response)
        
        # Test error display
        self.main_window.handle_error(Exception("Test error"))

    async def test_configuration_management(self):
        """Test configuration loading and validation."""
        # Test invalid configuration
        invalid_config = {
            "api_key": "test_key",
            "model": "invalid_model"
        }
        with open(self.config_path, "w") as f:
            json.dump(invalid_config, f)
        
        try:
            AIEngine(self.config_path)
            assert False, "Should have raised a configuration error"
        except Exception as e:
            assert "configuration" in str(e).lower() or "invalid" in str(e).lower()

    async def test_logging_system(self):
        """Test logging functionality."""
        # Test action logging
        log_action("Test action", "Test description")
        
        # Test error logging
        log_error(Exception("Test error"), "Test error description")
        
        # Test debug logging
        log_debug("Test debug message")
        
        # Verify log files exist
        assert (Path("logs/app.log")).exists()
        assert (Path("logs/error.log")).exists()
        assert (Path("logs/history.log")).exists()

    async def test_performance(self):
        """Test system performance under load."""
        start_time = asyncio.get_event_loop().time()
        
        # Generate multiple requests
        for i in range(10):
            await self.ai_engine.get_response(f"Performance test {i}")
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Verify reasonable response time
        assert duration < 30  # Assuming max 3 seconds per request

    async def test_security(self):
        """Test security features."""
        # Test API key protection
        config = self.ai_engine._load_config()
        assert config["api_key"] != "test_key"  # Should be masked
        
        # Test input sanitization
        malicious_input = "'; DROP TABLE users; --"
        response = await self.ai_engine.get_response(malicious_input)
        assert "drop table" not in response.lower()

    async def test_recovery(self):
        """Test system recovery from failures."""
        # Simulate crash
        self.ai_engine.clear_history()
        
        # Test recovery
        response = await self.ai_engine.get_response("Recovery test")
        assert response is not None
        
        # Verify state is maintained
        history = self.ai_engine.get_history()
        assert len(history) > 0 