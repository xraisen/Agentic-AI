import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from utils.logger import log_action, log_error, log_debug

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

async def run_tests():
    """Run all test scenarios."""
    try:
        log_action("Starting test suite", "Initializing test environment")
        
        # Create test results directory
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Create timestamp for this test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = results_dir / f"test_run_{timestamp}.log"
        
        # Configure pytest
        pytest_args = [
            "tests/test_scenarios.py",
            "-v",
            "--tb=short",
            f"--log-file={log_file}",
            "--log-file-level=DEBUG"
        ]
        
        # Run tests
        log_action("Running test scenarios", "Executing test suite")
        result = pytest.main(pytest_args)
        
        # Log results
        if result == 0:
            log_action("Test suite completed", "All tests passed")
        else:
            log_error(Exception("Test suite failed"), f"Tests failed with exit code {result}")
        
        return result == 0
        
    except Exception as e:
        log_error(e, "Test suite execution failed")
        return False

def main():
    """Main test runner entry point."""
    try:
        # Run tests
        success = asyncio.run(run_tests())
        
        # Exit with appropriate status code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        log_action("Test suite interrupted", "User interrupted test execution")
        sys.exit(1)
    except Exception as e:
        log_error(e, "Test runner failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 