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
python src/main.py
```

## Basic Commands

Once the application is running, you can use these example commands:

### Create a file

```
create file named example.txt with Hello, World!
```

### Read a file

```
read file example.txt
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

- Type `help` in the command input for a list of example commands
- Use the "Change Workspace" button to select where files will be created/modified
- Check the generated code to understand what's happening behind the scenes

## Next Steps

- Read the full [User Guide](USER_GUIDE.md) for detailed information
- Explore the [GitHub repository](https://github.com/xraisen/agentic-ai) for the latest updates
- Report issues on the [GitHub Issues page](https://github.com/xraisen/agentic-ai/issues) 