"""
Tests for the utility modules
"""

import os
import logging
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.utils.logger import (
    setup_logger,
    log_action,
    log_error,
    log_warning,
    log_debug
)

class TestLogger(unittest.TestCase):
    """Test cases for the logger module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_log_file = "test.log"
        self.logger = setup_logger(
            log_file=self.test_log_file,
            max_size=1024,  # 1KB
            backup_count=2,
            log_level="DEBUG"
        )
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove test log file
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
            
        # Remove backup files
        for i in range(1, 3):
            backup_file = f"{self.test_log_file}.{i}"
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
    def test_logger_setup(self):
        """Test logger setup"""
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.level, logging.DEBUG)
        self.assertEqual(len(self.logger.handlers), 2)  # File and console handlers
        
    def test_log_file_creation(self):
        """Test log file creation"""
        self.assertTrue(os.path.exists(self.test_log_file))
        
    def test_log_rotation(self):
        """Test log file rotation"""
        # Write enough logs to trigger rotation
        for i in range(100):
            self.logger.info(f"Test log {i}")
            
        # Check if backup files were created
        self.assertTrue(os.path.exists(f"{self.test_log_file}.1"))
        
    def test_log_action(self):
        """Test action logging"""
        with patch.object(self.logger, 'info') as mock_info:
            log_action(self.logger, "Test Action", "Test Details")
            mock_info.assert_called_once_with("Test Action: Test Details")
            
    def test_log_error(self):
        """Test error logging"""
        test_error = ValueError("Test error")
        with patch.object(self.logger, 'error') as mock_error:
            log_error(self.logger, test_error, "Test Context")
            mock_error.assert_called_once_with(
                "Test Context: Test error",
                exc_info=True
            )
            
    def test_log_warning(self):
        """Test warning logging"""
        with patch.object(self.logger, 'warning') as mock_warning:
            log_warning(self.logger, "Test Warning", "Test Context")
            mock_warning.assert_called_once_with("Test Context: Test Warning")
            
    def test_log_debug(self):
        """Test debug logging"""
        with patch.object(self.logger, 'debug') as mock_debug:
            log_debug(self.logger, "Test Debug", "Test Context")
            mock_debug.assert_called_once_with("Test Context: Test Debug")
            
    def test_log_types_filtering(self):
        """Test log type filtering"""
        # Create logger with specific log types
        filtered_logger = setup_logger(
            log_file="filtered.log",
            log_types=["error", "warning"]
        )
        
        # Write different types of logs
        filtered_logger.error("Test error")
        filtered_logger.warning("Test warning")
        filtered_logger.info("Test info")
        filtered_logger.debug("Test debug")
        
        # Read log file
        with open("filtered.log", "r") as f:
            log_content = f.read()
            
        # Verify only error and warning logs are present
        self.assertIn("Test error", log_content)
        self.assertIn("Test warning", log_content)
        self.assertNotIn("Test info", log_content)
        self.assertNotIn("Test debug", log_content)
        
        # Clean up
        os.remove("filtered.log")
        
    def test_log_directory_creation(self):
        """Test log directory creation"""
        # Create logger with nested directory
        nested_logger = setup_logger(
            log_file="nested/dir/test.log"
        )
        
        # Verify directory was created
        self.assertTrue(os.path.exists("nested/dir"))
        
        # Clean up
        os.remove("nested/dir/test.log")
        os.rmdir("nested/dir")
        os.rmdir("nested")

if __name__ == '__main__':
    unittest.main() 