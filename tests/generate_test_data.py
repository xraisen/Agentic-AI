import json
import random
import string
from pathlib import Path
from datetime import datetime, timedelta
from utils.logger import log_action, log_error, log_debug

class TestDataGenerator:
    """Generates test data for the Agentic AI test suite."""
    
    def __init__(self):
        self.test_data_dir = Path("tests/test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Test data categories
        self.categories = {
            "conversations": [],
            "configurations": [],
            "errors": [],
            "performance": [],
            "security": []
        }
    
    def generate_conversations(self, count=100):
        """Generate test conversations."""
        try:
            log_action("Generating conversations", f"Creating {count} test conversations")
            
            # Sample conversation templates
            templates = [
                "Hello, how are you?",
                "What's the weather like?",
                "Can you help me with {task}?",
                "Tell me about {topic}",
                "How do I {action}?",
                "What's the meaning of {word}?",
                "Translate {text} to {language}",
                "Summarize {content}",
                "Analyze {data}",
                "Generate {output}"
            ]
            
            # Sample tasks, topics, etc.
            tasks = ["writing code", "debugging", "testing", "deploying", "optimizing"]
            topics = ["AI", "machine learning", "programming", "data science", "robotics"]
            actions = ["write tests", "optimize code", "deploy application", "debug issues"]
            words = ["algorithm", "neural network", "deep learning", "reinforcement learning"]
            languages = ["Python", "JavaScript", "Java", "C++", "Rust"]
            
            conversations = []
            for _ in range(count):
                template = random.choice(templates)
                conversation = {
                    "id": self._generate_id(),
                    "timestamp": datetime.now().isoformat(),
                    "template": template,
                    "variables": self._generate_variables(template, locals()),
                    "expected_response": self._generate_expected_response(template)
                }
                conversations.append(conversation)
            
            self.categories["conversations"] = conversations
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate conversations")
            return False
    
    def generate_configurations(self, count=50):
        """Generate test configurations."""
        try:
            log_action("Generating configurations", f"Creating {count} test configurations")
            
            configurations = []
            for _ in range(count):
                config = {
                    "id": self._generate_id(),
                    "api_key": self._generate_api_key(),
                    "model": random.choice(["gpt-4", "gpt-3.5-turbo", "claude-2"]),
                    "max_tokens": random.randint(100, 4000),
                    "temperature": round(random.uniform(0.1, 1.0), 2),
                    "plugins": random.sample(["weather", "calculator", "translator", "summarizer"], 
                                         random.randint(0, 3)),
                    "history_size": random.randint(5, 20),
                    "timeout": random.randint(10, 60),
                    "retry_attempts": random.randint(1, 5)
                }
                configurations.append(config)
            
            self.categories["configurations"] = configurations
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate configurations")
            return False
    
    def generate_errors(self, count=50):
        """Generate test error scenarios."""
        try:
            log_action("Generating errors", f"Creating {count} test error scenarios")
            
            error_types = [
                "APIError",
                "NetworkError",
                "TimeoutError",
                "ValidationError",
                "AuthenticationError",
                "RateLimitError",
                "ResourceNotFoundError",
                "InvalidInputError",
                "PluginError",
                "SystemError"
            ]
            
            errors = []
            for _ in range(count):
                error = {
                    "id": self._generate_id(),
                    "type": random.choice(error_types),
                    "message": self._generate_error_message(),
                    "context": self._generate_error_context(),
                    "recovery_steps": self._generate_recovery_steps()
                }
                errors.append(error)
            
            self.categories["errors"] = errors
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate errors")
            return False
    
    def generate_performance_data(self, count=50):
        """Generate performance test data."""
        try:
            log_action("Generating performance data", f"Creating {count} performance test scenarios")
            
            performance_data = []
            for _ in range(count):
                data = {
                    "id": self._generate_id(),
                    "timestamp": datetime.now().isoformat(),
                    "request_size": random.randint(100, 10000),
                    "response_time": round(random.uniform(0.1, 5.0), 2),
                    "memory_usage": random.randint(100, 1000),
                    "cpu_usage": round(random.uniform(0.1, 100.0), 2),
                    "concurrent_requests": random.randint(1, 10),
                    "error_rate": round(random.uniform(0.0, 0.1), 3)
                }
                performance_data.append(data)
            
            self.categories["performance"] = performance_data
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate performance data")
            return False
    
    def generate_security_data(self, count=50):
        """Generate security test data."""
        try:
            log_action("Generating security data", f"Creating {count} security test scenarios")
            
            security_data = []
            for _ in range(count):
                data = {
                    "id": self._generate_id(),
                    "timestamp": datetime.now().isoformat(),
                    "input": self._generate_malicious_input(),
                    "expected_behavior": self._generate_expected_behavior(),
                    "risk_level": random.choice(["low", "medium", "high", "critical"]),
                    "mitigation": self._generate_mitigation_steps()
                }
                security_data.append(data)
            
            self.categories["security"] = security_data
            return True
            
        except Exception as e:
            log_error(e, "Failed to generate security data")
            return False
    
    def save_test_data(self):
        """Save generated test data to files."""
        try:
            log_action("Saving test data", "Writing test data to files")
            
            for category, data in self.categories.items():
                if data:
                    file_path = self.test_data_dir / f"{category}.json"
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                    log_action(f"Saved {category} data", f"Written to {file_path}")
            
            return True
            
        except Exception as e:
            log_error(e, "Failed to save test data")
            return False
    
    def _generate_id(self):
        """Generate a unique ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def _generate_api_key(self):
        """Generate a test API key."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _generate_variables(self, template, variables):
        """Generate variables for template."""
        result = {}
        for var in variables:
            if "{" + var + "}" in template:
                result[var] = random.choice(variables[var])
        return result
    
    def _generate_expected_response(self, template):
        """Generate expected response for template."""
        return f"Response for: {template}"
    
    def _generate_error_message(self):
        """Generate error message."""
        messages = [
            "Invalid input provided",
            "Network connection failed",
            "API request timed out",
            "Authentication failed",
            "Resource not found",
            "Rate limit exceeded",
            "Invalid configuration",
            "Plugin initialization failed",
            "System error occurred",
            "Validation failed"
        ]
        return random.choice(messages)
    
    def _generate_error_context(self):
        """Generate error context."""
        return {
            "timestamp": datetime.now().isoformat(),
            "component": random.choice(["API", "Network", "Plugin", "System"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "traceback": "Traceback (most recent call last):\n  ..."
        }
    
    def _generate_recovery_steps(self):
        """Generate recovery steps."""
        steps = [
            "Check network connection",
            "Verify API credentials",
            "Validate input data",
            "Check system resources",
            "Review error logs",
            "Restart service",
            "Clear cache",
            "Update configuration",
            "Check dependencies",
            "Contact support"
        ]
        return random.sample(steps, random.randint(1, 5))
    
    def _generate_malicious_input(self):
        """Generate malicious input for security testing."""
        inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "{{7*7}}",
            "1' OR '1'='1",
            "eval('alert(1)')",
            "data:text/html,<script>alert(1)</script>",
            "javascript:alert(1)",
            "onerror=alert(1)",
            "onload=alert(1)"
        ]
        return random.choice(inputs)
    
    def _generate_expected_behavior(self):
        """Generate expected behavior for security tests."""
        return {
            "sanitization": random.choice([True, False]),
            "validation": random.choice([True, False]),
            "escaping": random.choice([True, False]),
            "blocking": random.choice([True, False]),
            "logging": random.choice([True, False])
        }
    
    def _generate_mitigation_steps(self):
        """Generate mitigation steps for security issues."""
        steps = [
            "Input validation",
            "Output encoding",
            "Access control",
            "Rate limiting",
            "Error handling",
            "Logging",
            "Monitoring",
            "Patching",
            "Configuration review",
            "Security audit"
        ]
        return random.sample(steps, random.randint(1, 5))

def main():
    """Main generator entry point."""
    try:
        generator = TestDataGenerator()
        
        # Generate all test data
        if not all([
            generator.generate_conversations(),
            generator.generate_configurations(),
            generator.generate_errors(),
            generator.generate_performance_data(),
            generator.generate_security_data()
        ]):
            return False
        
        # Save test data
        if not generator.save_test_data():
            return False
        
        log_action("Test data generation completed", "All test data generated and saved")
        return True
        
    except Exception as e:
        log_error(e, "Test data generation failed")
        return False

if __name__ == "__main__":
    main() 