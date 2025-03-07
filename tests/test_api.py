"""
Tests for the API client module
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from src.api.client import APIClient

class TestAPIClient(unittest.TestCase):
    """Test cases for the APIClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'api': {
                'openrouter': {
                    'api_key': 'test_openrouter_key',
                    'models': ['google/gemini-pro', 'google/gemini-pro-vision']
                },
                'direct': {
                    'api_key': 'test_direct_key',
                    'models': ['google/gemini-pro']
                }
            },
            'security': {
                'encryption_key': 'test_encryption_key',
                'api_key_encryption': True
            },
            'monitoring': {
                'api_errors_threshold': 5
            }
        }
        self.client = APIClient(self.config)
        
    def test_initialization(self):
        """Test client initialization"""
        self.assertTrue(self.client.initialize())
        self.assertIsNotNone(self.client.fernet)
        self.assertIsNotNone(self.client.session)
        
    def test_encryption(self):
        """Test API key encryption/decryption"""
        test_key = "test_api_key"
        encrypted = self.client._encrypt_api_key(test_key)
        decrypted = self.client._decrypt_api_key(encrypted)
        
        self.assertNotEqual(test_key, encrypted)
        self.assertEqual(test_key, decrypted)
        
    @patch('requests.Session')
    def test_get_completion(self, mock_session):
        """Test getting AI completion"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_session.return_value.request.return_value = mock_response
        
        # Test completion
        response = self.client.get_completion("Test prompt")
        self.assertEqual(response, "Test response")
        
    @patch('requests.Session')
    def test_get_completion_error(self, mock_session):
        """Test error handling in get_completion"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_session.return_value.request.return_value = mock_response
        
        # Test error handling
        response = self.client.get_completion("Test prompt")
        self.assertIsNone(response)
        
    @patch('requests.Session')
    def test_analyze_image(self, mock_session):
        """Test image analysis"""
        # Mock responses
        mock_image_response = MagicMock()
        mock_image_response.status_code = 200
        
        mock_ai_response = MagicMock()
        mock_ai_response.status_code = 200
        mock_ai_response.json.return_value = {
            'choices': [{'message': {'content': 'Test image analysis'}}]
        }
        
        mock_session.return_value.request.side_effect = [
            mock_image_response,
            mock_ai_response
        ]
        
        # Test image analysis
        response = self.client.analyze_image("http://test.com/image.jpg")
        self.assertEqual(response, "Test image analysis")
        
    @patch('requests.Session')
    def test_analyze_image_error(self, mock_session):
        """Test error handling in image analysis"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Image not found"
        mock_session.return_value.request.return_value = mock_response
        
        # Test error handling
        response = self.client.analyze_image("http://test.com/image.jpg")
        self.assertIsNone(response)
        
    def test_rate_limiting(self):
        """Test rate limiting"""
        import time
        
        start_time = time.time()
        self.client._rate_limit()
        self.client._rate_limit()
        end_time = time.time()
        
        # Should have waited at least 1 second
        self.assertGreaterEqual(end_time - start_time, 1.0)
        
    def test_error_handling(self):
        """Test error handling and threshold"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Test error threshold
        for _ in range(self.config['monitoring']['api_errors_threshold']):
            self.client._handle_error(mock_response)
            
        self.assertEqual(self.client.error_count, self.config['monitoring']['api_errors_threshold'])

if __name__ == '__main__':
    unittest.main() 