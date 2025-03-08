# Agentic AI: Quick Start Guide

This guide will help you get started with Agentic AI quickly.

## Installation

### Windows

1. Download the latest release from [GitHub](https://github.com/xraisen/agentic-ai/releases)
2. Extract the ZIP file to a directory of your choice
3. Run `agentic-ai.exe` from the extracted folder or use the `run.bat` file

### From Source

```bash
git clone https://github.com/xraisen/agentic-ai.git
cd agentic-ai
python -m venv .venv
.\.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
python src/agentic_ai/main.py
```

## User Interface

When you start Agentic AI, you'll see this interface:

```
==================================================
             Agentic AI
==================================================
Type 'exit' or 'quit' to exit.
Type 'help' for commands.
==================================================

You: 
```

Type your commands after the "You:" prompt.

## Basic Commands

Once the application is running, you can use these example commands:

### Create a file

```
You: create file named example.txt with Hello, World!

Processing: create file named example.txt with Hello, World!
Generating and executing code...

Result:
File 'example.txt' created successfully
```

### Read a file

```
You: read file example.txt

Processing: read file example.txt
Generating and executing code...

Result:
Hello, World!
```

### List files in a directory

```
list files in .
```

### Search for files containing text

```
search files containing import
```

### Delete a file

```
delete file example.txt
```

### Create a directory

```
create directory docs
```

## Tips

- Type `help` to see available commands
- Type `exit` or `quit` to exit the application
- Type `clear` to clear the screen

## Next Steps

- Read the full [User Guide](USER_GUIDE.md) for detailed information
- Explore the [GitHub repository](https://github.com/xraisen/agentic-ai) for the latest updates
- Report issues on the [GitHub Issues page](https://github.com/xraisen/agentic-ai/issues) 
