import os
import sys
import subprocess
import venv
from pathlib import Path
from utils.logger import log_action, log_error, log_debug

def setup_test_environment():
    """Set up the test environment."""
    try:
        log_action("Setting up test environment", "Initializing test setup")
        
        # Create test directories
        test_dirs = [
            "tests/test_data",
            "test_results",
            "logs"
        ]
        
        for dir_path in test_dirs:
            Path(dir_path).mkdir(exist_ok=True)
            log_action(f"Created directory", f"Created {dir_path}")
        
        # Create virtual environment if it doesn't exist
        venv_path = Path("venv")
        if not venv_path.exists():
            log_action("Creating virtual environment", "Setting up Python virtual environment")
            venv.create("venv", with_pip=True)
        
        # Activate virtual environment
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "activate"
        else:
            activate_script = venv_path / "bin" / "activate"
        
        # Install test requirements
        log_action("Installing test requirements", "Installing Python dependencies")
        pip_cmd = [str(activate_script), "-c", "pip install -r tests/requirements.txt"]
        subprocess.run(pip_cmd, check=True)
        
        # Install development requirements
        log_action("Installing development requirements", "Installing development dependencies")
        pip_cmd = [str(activate_script), "-c", "pip install -r build_requirements.txt"]
        subprocess.run(pip_cmd, check=True)
        
        # Set up environment variables
        os.environ["TEST_MODE"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        log_action("Test environment setup completed", "Environment ready for testing")
        return True
        
    except Exception as e:
        log_error(e, "Failed to set up test environment")
        return False

def cleanup_test_environment():
    """Clean up the test environment."""
    try:
        log_action("Cleaning up test environment", "Starting cleanup")
        
        # Remove test directories
        test_dirs = [
            "tests/test_data",
            "test_results",
            "logs"
        ]
        
        for dir_path in test_dirs:
            if Path(dir_path).exists():
                for item in Path(dir_path).glob("*"):
                    if item.is_file():
                        item.unlink()
                    else:
                        for subitem in item.glob("*"):
                            subitem.unlink()
                        item.rmdir()
                Path(dir_path).rmdir()
                log_action(f"Removed directory", f"Removed {dir_path}")
        
        # Remove virtual environment
        venv_path = Path("venv")
        if venv_path.exists():
            if sys.platform == "win32":
                subprocess.run(["rmdir", "/s", "/q", "venv"], check=True)
            else:
                subprocess.run(["rm", "-rf", "venv"], check=True)
            log_action("Removed virtual environment", "Cleaned up Python virtual environment")
        
        log_action("Test environment cleanup completed", "Environment cleaned up")
        return True
        
    except Exception as e:
        log_error(e, "Failed to clean up test environment")
        return False

def main():
    """Main setup script entry point."""
    try:
        # Set up environment
        if not setup_test_environment():
            sys.exit(1)
        
        # Run tests
        subprocess.run([sys.executable, "tests/test_runner.py"], check=True)
        
        # Clean up environment
        if not cleanup_test_environment():
            sys.exit(1)
        
    except KeyboardInterrupt:
        log_action("Setup interrupted", "User interrupted setup process")
        cleanup_test_environment()
        sys.exit(1)
    except Exception as e:
        log_error(e, "Setup process failed")
        cleanup_test_environment()
        sys.exit(1)

if __name__ == "__main__":
    main() 