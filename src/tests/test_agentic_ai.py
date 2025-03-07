import pytest
import json
import os
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock
from agentic_ai import load_config, get_gemini_response, setup_directories

@pytest.fixture
def mock_config():
    return {
        "OPENROUTER_API_KEY": "test-key",
        "MODEL": "test-model",
        "SITE_URL": "http://test.com",
        "SITE_NAME": "Test Site",
        "MAX_TOKENS": 100,
        "TEMPERATURE": 0.5
    }

@pytest.fixture
def mock_response():
    return {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }

def test_setup_directories():
    """Test directory creation"""
    setup_directories()
    assert Path("logs").exists()
    assert Path("cache").exists()
    assert Path("assets").exists()

def test_load_config_success(tmp_path, mock_config):
    """Test successful config loading"""
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(mock_config, f)
    
    config = load_config(str(config_file))
    assert config == mock_config

def test_load_config_not_found():
    """Test config file not found"""
    config = load_config("nonexistent.json")
    assert config is None

def test_load_config_invalid_json(tmp_path):
    """Test invalid JSON config"""
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        f.write("invalid json")
    
    config = load_config(str(config_file))
    assert config is None

@patch("requests.post")
def test_get_gemini_response_success(mock_post, mock_config, mock_response):
    """Test successful API response"""
    mock_post.return_value = MagicMock(
        json=lambda: mock_response,
        raise_for_status=lambda: None
    )
    
    with patch("agentic_ai.load_config", return_value=mock_config):
        response = get_gemini_response("test prompt")
        assert response == "Test response"

@patch("requests.post")
def test_get_gemini_response_timeout(mock_post, mock_config):
    """Test API timeout"""
    mock_post.side_effect = requests.exceptions.Timeout()
    
    with patch("agentic_ai.load_config", return_value=mock_config):
        response = get_gemini_response("test prompt")
        assert "timed out" in response.lower()

@patch("requests.post")
def test_get_gemini_response_error(mock_post, mock_config):
    """Test API error"""
    mock_post.side_effect = requests.exceptions.RequestException("API Error")
    
    with patch("agentic_ai.load_config", return_value=mock_config):
        response = get_gemini_response("test prompt")
        assert "api error" in response.lower() 