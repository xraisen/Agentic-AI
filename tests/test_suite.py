import unittest
import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from src.core.ai_engine import AIEngine
from src.utils.knowledge_manager import KnowledgeManager
from src.utils.logger import log_action, log_error, log_debug

class TestAIEngine(unittest.TestCase):
    """Test suite for AIEngine component."""
    
    def setUp(self):
        """Set up test environment."""
        try:
            self.test_config = {
                "OPENROUTER_API_KEY": "test_key",
                "MODEL": "gemini-pro",
                "SITE_URL": "http://localhost:8000",
                "SITE_NAME": "Agentic AI Test"
            }
            self.config_path = "test_config.json"
            with open(self.config_path, "w") as f:
                json.dump(self.test_config, f)
            
            self.ai_engine = AIEngine(self.config_path)
            log_action("Test environment set up", "AIEngine test suite initialized")
        except Exception as e:
            log_error(e, "Failed to set up test environment")
            raise

    def tearDown(self):
        """Clean up test environment."""
        try:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            log_action("Test environment cleaned up", "AIEngine test suite completed")
        except Exception as e:
            log_error(e, "Failed to clean up test environment")

    def test_config_loading(self):
        """Test configuration loading."""
        try:
            self.assertEqual(self.ai_engine.config["MODEL"], "gemini-pro")
            self.assertEqual(self.ai_engine.config["SITE_NAME"], "Agentic AI Test")
            log_action("Config loading test passed", "Configuration loaded correctly")
        except Exception as e:
            log_error(e, "Config loading test failed")
            raise

    def test_message_preparation(self):
        """Test message preparation."""
        try:
            prompt = "Test message"
            messages = self.ai_engine._prepare_messages(prompt)
            self.assertIsInstance(messages, list)
            self.assertEqual(len(messages), 2)  # System and user messages
            self.assertEqual(messages[1]["content"][0]["text"], prompt)
            log_action("Message preparation test passed", "Messages prepared correctly")
        except Exception as e:
            log_error(e, "Message preparation test failed")
            raise

    def test_history_management(self):
        """Test conversation history management."""
        try:
            # Test adding to history
            self.ai_engine._update_history("Test prompt", "Test response")
            self.assertEqual(len(self.ai_engine.conversation_history), 1)
            
            # Test history limit
            for i in range(150):  # Exceed max_history
                self.ai_engine._update_history(f"Prompt {i}", f"Response {i}")
            self.assertEqual(len(self.ai_engine.conversation_history), 100)
            
            # Test history clearing
            self.ai_engine.clear_history()
            self.assertEqual(len(self.ai_engine.conversation_history), 0)
            
            log_action("History management test passed", "History operations working correctly")
        except Exception as e:
            log_error(e, "History management test failed")
            raise

class TestKnowledgeManager(unittest.TestCase):
    """Test suite for KnowledgeManager component."""
    
    def setUp(self):
        """Set up test environment."""
        try:
            self.test_logs_dir = Path("test_logs")
            self.test_docs_dir = Path("test_docs")
            self.test_logs_dir.mkdir(exist_ok=True)
            self.test_docs_dir.mkdir(exist_ok=True)
            
            # Create test log files
            self._create_test_logs()
            self._create_test_docs()
            
            self.knowledge_manager = KnowledgeManager()
            self.knowledge_manager.logs_dir = self.test_logs_dir
            self.knowledge_manager.docs_dir = self.test_docs_dir
            
            log_action("Test environment set up", "KnowledgeManager test suite initialized")
        except Exception as e:
            log_error(e, "Failed to set up test environment")
            raise

    def tearDown(self):
        """Clean up test environment."""
        try:
            import shutil
            shutil.rmtree(self.test_logs_dir)
            shutil.rmtree(self.test_docs_dir)
            log_action("Test environment cleaned up", "KnowledgeManager test suite completed")
        except Exception as e:
            log_error(e, "Failed to clean up test environment")

    def _create_test_logs(self):
        """Create test log files."""
        try:
            # Create app.log
            with open(self.test_logs_dir / "app.log", "w") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | INFO     | Action: Test action\n")
            
            # Create error.log
            with open(self.test_logs_dir / "error.log", "w") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ERROR    | Test error\n")
            
            # Create history.log
            with open(self.test_logs_dir / "history.log", "w") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | INFO     | Action: Message sent\n")
        except Exception as e:
            log_error(e, "Failed to create test logs")
            raise

    def _create_test_docs(self):
        """Create test documentation files."""
        try:
            # Create README.md
            with open(self.test_docs_dir / "README.md", "w") as f:
                f.write("Test README\nThis is a test documentation file.\n")
            
            # Create knowledgebase.md
            with open(self.test_docs_dir / "knowledgebase.md", "w") as f:
                f.write("Test Knowledge Base\nThis is a test knowledge base file.\n")
        except Exception as e:
            log_error(e, "Failed to create test docs")
            raise

    def test_log_loading(self):
        """Test log file loading."""
        try:
            self.knowledge_manager.update_knowledge_cache()
            
            # Check app logs
            app_logs = self.knowledge_manager.knowledge_cache["logs"]["app"]
            self.assertGreater(len(app_logs), 0)
            self.assertEqual(app_logs[0]["level"], "INFO")
            
            # Check error logs
            error_logs = self.knowledge_manager.knowledge_cache["logs"]["error"]
            self.assertGreater(len(error_logs), 0)
            self.assertEqual(error_logs[0]["level"], "ERROR")
            
            log_action("Log loading test passed", "Logs loaded correctly")
        except Exception as e:
            log_error(e, "Log loading test failed")
            raise

    def test_documentation_loading(self):
        """Test documentation loading."""
        try:
            self.knowledge_manager.update_knowledge_cache()
            
            docs = self.knowledge_manager.knowledge_cache["docs"]
            self.assertIn("README.md", docs)
            self.assertIn("knowledgebase.md", docs)
            
            log_action("Documentation loading test passed", "Documentation loaded correctly")
        except Exception as e:
            log_error(e, "Documentation loading test failed")
            raise

    def test_search_functionality(self):
        """Test documentation search."""
        try:
            self.knowledge_manager.update_knowledge_cache()
            
            results = self.knowledge_manager.search_documentation("test")
            self.assertGreater(len(results), 0)
            self.assertIn("README.md", results)
            
            log_action("Search functionality test passed", "Documentation search working correctly")
        except Exception as e:
            log_error(e, "Search functionality test failed")
            raise

def run_tests():
    """Run all tests and generate report."""
    try:
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAIEngine)
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestKnowledgeManager))
        
        # Create test results directory
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Run tests and capture output
        with open(results_dir / "test_report.txt", "w") as f:
            runner = unittest.TextTestRunner(stream=f)
            result = runner.run(suite)
            
            # Write summary
            f.write("\nTest Summary:\n")
            f.write(f"Tests run: {result.testsRun}\n")
            f.write(f"Failures: {len(result.failures)}\n")
            f.write(f"Errors: {len(result.errors)}\n")
            
            if result.failures:
                f.write("\nFailures:\n")
                for failure in result.failures:
                    f.write(f"{failure[1]}\n")
            
            if result.errors:
                f.write("\nErrors:\n")
                for error in result.errors:
                    f.write(f"{error[1]}\n")
        
        log_action("Test suite completed", f"Results saved to {results_dir}/test_report.txt")
        return result.wasSuccessful()
    except Exception as e:
        log_error(e, "Test suite execution failed")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 