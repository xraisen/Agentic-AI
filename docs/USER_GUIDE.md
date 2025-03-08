# Agentic AI User Guide

## Introduction

Welcome to Agentic AI, a powerful assistant that can help you perform file operations and system tasks using natural language commands. This guide will help you understand how to use the application, its features, and how to troubleshoot common issues.

## Installation

### Windows

1. Download the latest release from [GitHub](https://github.com/xraisen/agentic-ai/releases)
2. Extract the ZIP file to a directory of your choice
3. Run `agentic-ai.exe` from the extracted folder or use the `run.bat` file

### From Source (All Platforms)

1. Clone the repository:
   ```bash
   git clone https://github.com/xraisen/agentic-ai.git
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

4. Run the application:
   ```bash
   python src/agentic_ai/main.py
   ```

## Getting Started

When you first start Agentic AI, you'll see the main interface:

```
==================================================
             Agentic AI
==================================================
Type 'exit' or 'quit' to exit.
Type 'help' for commands.
==================================================
```

You can interact with the AI by typing commands after the "You:" prompt.

## Using Natural Language Commands

Agentic AI understands natural language commands for file operations. Here are some examples:

### Creating Files

```
You: create file named example.txt with Hello, World!

Processing: create file named example.txt with Hello, World!
Generating and executing code...

Result:
File 'example.txt' created successfully
```

This will create a file named `example.txt` with the content "Hello, World!"

### Reading Files

```
You: read file example.txt

Processing: read file example.txt
Generating and executing code...

Result:
Hello, World!
```

This will display the contents of `example.txt`.

### Listing Files

```
You: list files in .

Processing: list files in .
Generating and executing code...

Result:
Files in '.':
1. example.txt
2. README.md
3. config.json
...
```

This will list all files in the current directory.

### Searching Files

```
search files containing import
```

This will search for files containing the word "import".

### Deleting Files

```
delete file example.txt
```

This will delete the file `example.txt`.

### Creating Directories

```
create directory docs
```

This will create a directory named `docs`.

## How It Works

Agentic AI uses a self-aware code generation system:

1. **Natural Language Processing**: Your command is interpreted to understand your intent
2. **Code Generation**: Python code is dynamically generated to perform the requested operation
3. **Security Analysis**: The generated code is analyzed for safety
4. **Execution**: The code is executed in a secure environment
5. **Result Presentation**: The results are presented in a user-friendly way

## Security Features

Agentic AI is designed with security in mind:

- **Workspace Confinement**: By default, operations are limited to the workspace directory
- **Code Analysis**: All generated code is analyzed for potential security issues
- **Transparency**: You can see the code that will be executed before it runs
- **Permission System**: Sensitive operations require explicit permission
- **Rollback Capability**: Some operations (like registry changes) can be rolled back if necessary

## Advanced Features

### Changing Workspace

You can change the workspace directory (where file operations will be performed):

1. Click the "Change Workspace" button in the toolbar
2. Select the desired directory
3. The new workspace path will be displayed in the output area

### Command-Line Interface

For advanced users, Agentic AI also provides a command-line interface:

```bash
# Start in interactive mode
python src/agentic_ai/main.py

# Execute a single command
python src/agentic_ai/main.py create file named test.txt with Hello World

# Specify a workspace directory
python src/agentic_ai/main.py --workspace /path/to/workspace
```

## Troubleshooting

### Application Doesn't Start

- Ensure you have extracted all files from the ZIP archive
- Check that the `assets` and `config` directories are present
- Verify that you have the required permissions to run the application

### Commands Not Working

- Check that you're using the correct command format
- Try rephrasing your command
- Verify that you have the necessary permissions for the file operations
- Check the error message for specific issues

### File Operations Failing

- Ensure the workspace directory is accessible
- Check if the file already exists (for creation) or doesn't exist (for reading/deletion)
- Verify that you have the necessary permissions for the file operations

## Getting Help

If you need additional help:

- Click the "Help" button in the toolbar for in-app assistance
- Type `help` in the command input for a list of example commands
- Visit [GitHub Issues](https://github.com/xraisen/agentic-ai/issues) for known issues and solutions

## Contributing

We welcome contributions to Agentic AI! If you'd like to contribute:

1. Fork the repository on GitHub
2. Create a new branch for your feature or fix
3. Make your changes and add tests
4. Submit a pull request

## License

Agentic AI is released under the MIT License. See the LICENSE file for details. 