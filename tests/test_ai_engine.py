import pytest
import json
import os
from src.core.ai_engine import AIEngine

@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file for testing."""
    config = {
        "OPENROUTER_API_KEY": "test-api-key",
        "SITE_URL": "https://test-site.com",
        "SITE_NAME": "Test Agentic AI",
        "MODEL": "google/gemini-2.0-flash-thinking-exp:free"
    }
    
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path

@pytest.fixture
def ai_engine(config_file):
    """Create an AI engine instance for testing."""
    return AIEngine(str(config_file))

def test_ai_engine_initialization(ai_engine):
    """Test AI engine initialization."""
    assert ai_engine.config is not None
    assert "OPENROUTER_API_KEY" in ai_engine.config
    assert "MODEL" in ai_engine.config
    assert len(ai_engine.conversation_history) == 0

def test_conversation_history(ai_engine):
    """Test conversation history management."""
    # Add a test conversation
    ai_engine._update_history("Test prompt", "Test response")
    
    # Check history
    assert len(ai_engine.conversation_history) == 1
    assert ai_engine.conversation_history[0]["prompt"] == "Test prompt"
    assert ai_engine.conversation_history[0]["response"] == "Test response"
    
    # Test history limit
    for i in range(ai_engine.max_history + 1):
        ai_engine._update_history(f"Prompt {i}", f"Response {i}")
    
    assert len(ai_engine.conversation_history) == ai_engine.max_history

def test_clear_history(ai_engine):
    """Test clearing conversation history."""
    # Add some test conversations
    ai_engine._update_history("Test prompt 1", "Test response 1")
    ai_engine._update_history("Test prompt 2", "Test response 2")
    
    # Clear history
    ai_engine.clear_history()
    
    # Verify history is cleared
    assert len(ai_engine.conversation_history) == 0

def test_invalid_config_file():
    """Test handling of invalid config file."""
    with pytest.raises(FileNotFoundError):
        AIEngine("nonexistent_config.json")

def test_invalid_json_config(tmp_path):
    """Test handling of invalid JSON in config file."""
    config_path = tmp_path / "invalid_config.json"
    with open(config_path, "w") as f:
        f.write("invalid json")
    
    with pytest.raises(ValueError):
        AIEngine(str(config_path))

@pytest.mark.asyncio
async def test_get_response(ai_engine):
    """Test getting a response from the AI engine."""
    # Note: This test requires a valid API key to work
    # In a real test environment, you might want to mock the API call
    response = await ai_engine.get_response("Hello, how are you?")
    assert response is not None
    assert isinstance(response, str) 