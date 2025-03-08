# Agentic AI

An AI-powered application with secure file system access, advanced system manipulation capabilities, permission management, and conversation history capabilities.

## Overview

Agentic AI is a powerful AI assistant that can interact with your file system, execute system commands, manipulate Windows system components, and maintain conversation history - all with robust permission handling and security measures. It provides a reliable, secure way for AI to assist with tasks that require access to your local environment.

## Key Features

- **File System Operations**: Secure, permission-based file read/write/create/delete capabilities
- **System Command Execution**: Controlled execution of system commands with user authorization
- **Advanced Windows System Manipulation**:
  - Registry management with rollback capability
  - Windows service control
  - Firewall rule creation
  - Scheduled task management
  - Administrative privilege elevation
- **Background Process Management**: Run and monitor long-running tasks in the background
- **Robust Error Handling & Rollback**: Safely attempt operations with automatic rollback
- **Conversation History**: Persistent conversation logging with search and retrieval
- **Permission Management**: Granular permission control for all operations
- **AI Integration**: Connects to large language models for intelligent assistance
- **Secure by Design**: All operations require explicit permissions

## Architecture

Agentic AI is built around several core components:

1. **File System Interface**: A secure abstraction layer for file operations
2. **Permission Manager**: Tracks and enforces user-granted permissions
3. **Conversation Logger**: Records and maintains conversation history
4. **System Operations Manager**: Controls execution of system commands and Windows system manipulation
5. **Agentic Core**: Integrates all components with the AI model

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/agentic-ai.git
cd agentic-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your API key:
```bash
cp config.example.json config.json
# Edit config.json to add your API key
```

## Usage

### Basic Usage

```bash
python src/main.py
```

### Running the Demo

```bash
python examples/file_operations_demo.py
```

### Building Windows Application

```bash
# Build a standard windowed application
python build_windows.py

# Build with console for debugging
python build_windows.py --console

# Build a single executable file
python build_windows.py --onefile

# Create an installer
python build_windows.py --installer
```

## Windows System Manipulation Features

Agentic AI provides advanced Windows system manipulation capabilities with robust security controls:

### Registry Management

```python
# Modify registry values with automatic rollback capability
from src.core.system_operations import modify_registry

# Create or modify a registry value
success = modify_registry(
    "HKEY_CURRENT_USER\\Software\\MyApp",
    "Setting1",
    "My Value",
    "REG_SZ"
)

# Rollback a registry change if needed
from src.core.system_operations import get_system_manager
system_manager = get_system_manager()
system_manager.rollback_last_operation()
```

### Service Management

```python
# Control Windows services
from src.core.system_operations import manage_service

# Start, stop, restart, or query service status
success, output = manage_service("wuauserv", "query")  # Windows Update service
success, output = manage_service("wuauserv", "start")
```

### Privilege Elevation

```python
# Elevate to administrator privileges when needed
from src.core.system_operations import elevate_privileges

# Prompt user and elevate if approved
elevated = elevate_privileges("Install system driver")
```

### Firewall Management

```python
# Create Windows Firewall rules
from src.core.system_operations import create_firewall_rule

# Create an allow rule for inbound TCP traffic on port 8080
success = create_firewall_rule(
    "MyApp Server",
    "allow",
    "in",
    "TCP",
    8080
)
```

### Scheduled Tasks

```python
# Create Windows scheduled tasks
from src.core.system_operations import create_scheduled_task

# Create a daily task
success = create_scheduled_task(
    "MyAppDailyBackup",
    "C:\\path\\to\\backup.exe",
    "DAILY"
)
```

### Background Process Management

```python
# Run commands in the background
from src.core.system_operations import get_system_manager
system_manager = get_system_manager()

# Start a long-running process
exit_code, stdout, stderr = system_manager.execute_command(
    "long_running_command.exe",
    background=True
)

# Get process ID from stdout
process_id = int(stdout.split()[-1])

# Check status later
status = system_manager.get_process_status(process_id)

# Optionally terminate the process
if status["exists"] and not status["completed"]:
    system_manager.kill_process(process_id)
```

## Security

Agentic AI takes security seriously with multiple layers of protection:

1. **Workspace Confinement**: By default, operations are limited to the specified workspace
2. **Explicit Permissions**: All sensitive operations require explicit user permission
3. **Permission Expiry**: Permissions can be limited by time
4. **Operation Logging**: All operations are logged for auditing
5. **Safe Command Filtering**: System commands are filtered for safety
6. **Rollback Capability**: System changes can be rolled back when possible
7. **Privilege Management**: Administrative tasks require explicit elevation
8. **UI Confirmation**: All sensitive operations prompt the user through the UI

## Development

### Project Structure

```
agentic-ai/
├── src/
│   ├── core/                 # Core components
│   │   ├── ai_engine.py      # AI model integration
│   │   ├── agentic_core.py   # Main integration layer
│   │   ├── file_operations.py # File operations manager
│   │   └── system_operations.py # System command and Windows manipulation manager
│   ├── utils/                # Utility modules
│   │   ├── file_system_interface.py # File system abstraction
│   │   ├── permission_manager.py # Permission management
│   │   ├── conversation_logger.py # Conversation history
│   │   └── logger.py         # Logging utility
│   └── main.py               # Application entry point
├── tests/                    # Unit tests
├── examples/                 # Example applications
├── logs/                     # Log directory
├── build_windows.py          # Windows build script
└── config.json               # Configuration file
```

### Running Tests

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 