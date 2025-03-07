"""
Tests for the UI module
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    """Test cases for the MainWindow class"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        # Create QApplication instance
        cls.app = QApplication(sys.argv)
        
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'app': {
                'name': 'Agentic AI',
                'version': '1.0.0',
                'site_url': 'https://test.example.com'
            },
            'api': {
                'openrouter': {
                    'models': ['google/gemini-pro', 'google/gemini-pro-vision']
                }
            },
            'ai': {
                'temperature': 0.7,
                'max_tokens': 2048
            },
            'desktop': {
                'startup': True
            }
        }
        self.api_client = MagicMock()
        self.window = MainWindow(self.config, self.api_client)
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.window.close()
        
    def test_initialization(self):
        """Test window initialization"""
        self.assertTrue(self.window.initialize())
        self.assertEqual(self.window.windowTitle(), "Agentic AI v1.0.0")
        
    def test_model_selection(self):
        """Test model selection dropdown"""
        self.assertEqual(self.window.model_combo.count(), 2)
        self.assertEqual(self.window.model_combo.currentText(), "google/gemini-pro")
        
    def test_temperature_control(self):
        """Test temperature control"""
        self.assertEqual(self.window.temp_spin.value(), 0.7)
        self.assertEqual(self.window.temp_spin.minimum(), 0.0)
        self.assertEqual(self.window.temp_spin.maximum(), 1.0)
        
    def test_max_tokens_control(self):
        """Test max tokens control"""
        self.assertEqual(self.window.tokens_spin.value(), 2048)
        self.assertEqual(self.window.tokens_spin.minimum(), 1)
        self.assertEqual(self.window.tokens_spin.maximum(), 4096)
        
    def test_prompt_input(self):
        """Test prompt input field"""
        test_prompt = "Test prompt"
        self.window.prompt_input.setText(test_prompt)
        self.assertEqual(self.window.prompt_input.toPlainText(), test_prompt)
        
    def test_clear_prompt(self):
        """Test clearing prompt"""
        self.window.prompt_input.setText("Test prompt")
        self.window.clear_prompt()
        self.assertEqual(self.window.prompt_input.toPlainText(), "")
        
    @patch('PyQt6.QtWidgets.QMessageBox')
    def test_send_prompt_empty(self, mock_message_box):
        """Test sending empty prompt"""
        self.window.send_prompt()
        mock_message_box.warning.assert_called_once()
        
    @patch('PyQt6.QtWidgets.QMessageBox')
    def test_send_prompt_success(self, mock_message_box):
        """Test successful prompt sending"""
        # Setup mock response
        self.api_client.get_completion.return_value = "Test response"
        
        # Send prompt
        self.window.prompt_input.setText("Test prompt")
        self.window.send_prompt()
        
        # Verify response
        self.assertEqual(self.window.response_output.toPlainText(), "AI: Test response")
        mock_message_box.critical.assert_not_called()
        
    @patch('PyQt6.QtWidgets.QMessageBox')
    def test_send_prompt_error(self, mock_message_box):
        """Test error handling in prompt sending"""
        # Setup mock error
        self.api_client.get_completion.return_value = None
        
        # Send prompt
        self.window.prompt_input.setText("Test prompt")
        self.window.send_prompt()
        
        # Verify error message
        mock_message_box.critical.assert_called_once()
        
    def test_system_tray(self):
        """Test system tray functionality"""
        self.assertIsNotNone(self.window.tray_icon)
        self.assertTrue(self.window.tray_icon.isVisible())
        
    def test_shortcuts(self):
        """Test keyboard shortcuts"""
        # Test send shortcut
        self.window.prompt_input.setText("Test prompt")
        QTest.keySequence(self.window, Qt.KeySequence("Ctrl+Return"))
        self.api_client.get_completion.assert_called_once()
        
        # Test clear shortcut
        QTest.keySequence(self.window, Qt.KeySequence("Ctrl+L"))
        self.assertEqual(self.window.prompt_input.toPlainText(), "")
        
    def test_close_event(self):
        """Test window close event"""
        # Mock system tray show message
        with patch.object(self.window.tray_icon, 'showMessage') as mock_show_message:
            # Trigger close event
            self.window.close()
            
            # Verify window is hidden
            self.assertFalse(self.window.isVisible())
            
            # Verify tray message
            mock_show_message.assert_called_once()
            
    def test_run(self):
        """Test application run"""
        with patch('PyQt6.QtWidgets.QApplication.exec') as mock_exec:
            mock_exec.return_value = 0
            self.assertEqual(self.window.run(), 0)

if __name__ == '__main__':
    unittest.main() 