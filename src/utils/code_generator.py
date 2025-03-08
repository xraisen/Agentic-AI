"""
Code Generator Utility for Agentic AI

This module implements the selfaware rules for file manipulation through
self-generated code. It allows the AI to create and execute code based on
natural language instructions, with appropriate security checks and error handling.
"""

import os
import sys
import subprocess
import tempfile
import logging
import inspect
from typing import Optional, Dict, Any, Tuple, List
import re
import ast
from pathlib import Path

# Get logger
logger = logging.getLogger("agentic_ai.utils.code_generator")

class CodeGenerator:
    """
    Generator for creating and executing Python code based on natural language instructions.
    Follows the selfaware rules for file manipulation.
    """
    
    def __init__(self, workspace_path: Optional[Path] = None):
        """
        Initialize the code generator
        
        Args:
            workspace_path: Path to workspace (default: current directory)
        """
        self.workspace_path = workspace_path or Path.cwd()
        self.last_code: Optional[str] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self.execution_count = 0
        self.max_attempts = 3
        self.safe_imports = {
            "os", "sys", "pathlib", "re", "json", "csv", "datetime", 
            "shutil", "glob", "tempfile", "time", "logging"
        }
        self.unsafe_modules = {
            "subprocess", "socket", "requests", "urllib", "http", "ftp",
            "pickle", "marshal", "shelve", "_winreg", "winreg", "ctypes"
        }
        self.unsafe_functions = {
            "exec", "eval", "compile", "getattr", "setattr", "delattr",
            "globals", "locals", "__import__"
        }
        
    def is_safe_code(self, code: str) -> Tuple[bool, str]:
        """
        Check if the generated code is safe to execute.
        
        Args:
            code: The Python code to check
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Check for unsafe modules
        for module in self.unsafe_modules:
            if re.search(fr'\b{re.escape(module)}\b', code):
                return False, f"Using unsafe module: {module}"
        
        # Check for unsafe functions
        for func in self.unsafe_functions:
            if re.search(fr'\b{re.escape(func)}\b', code):
                return False, f"Using unsafe function: {func}"
        
        # Parse the code and check for unsafe operations
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Check for exec or eval
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in self.unsafe_functions:
                        return False, f"Using unsafe function: {node.func.id}"
                
                # Check for imports
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name.split('.')[0] in self.unsafe_modules:
                            return False, f"Importing unsafe module: {name.name}"
                
                # Check for from ... import
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split('.')[0] in self.unsafe_modules:
                        return False, f"Importing from unsafe module: {node.module}"
            
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error in code: {e}"
            
    def generate_file_manipulation_code(self, instruction: str) -> str:
        """
        Generate Python code to manipulate files based on natural language instruction.
        
        Args:
            instruction: Natural language instruction for file manipulation
            
        Returns:
            Generated Python code
        """
        # Basic template for file manipulation
        code = f"""
# Generated code for: {instruction}
import os
import pathlib
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generated_code")

def main():
    \"\"\"
    Execute the file manipulation based on instruction:
    {instruction}
    \"\"\"
    try:
        # Get workspace path
        workspace_path = Path({repr(str(self.workspace_path))})
        logger.info(f"Working in: {{workspace_path}}")
        
        # Ensure we're working within the workspace
        os.chdir(workspace_path)
        
        # File manipulation logic based on instruction
"""
        
        # Add specific file operation code based on the instruction
        if "create" in instruction.lower() and "file" in instruction.lower():
            # Extract filename using better pattern matching
            # Match 'named filename.txt with content' or 'called filename.txt with content'
            filename_match = re.search(r'(?:named|called)\s+([^\s]+)(?:\s+with\s+|\s+containing\s+)(.*)', instruction)
            
            if filename_match:
                filename = filename_match.group(1)
                content = filename_match.group(2)
                
                code += f"""
        # Create a new file
        file_path = workspace_path / "{filename}"
        logger.info(f"Creating file: {{file_path}}")
        with open(file_path, 'w') as f:
            f.write({repr(content)})
        logger.info(f"Successfully created file: {{file_path}}")
        return {{"success": True, "message": f"File created: {{file_path}}", "path": str(file_path)}}
"""
            else:
                # Fallback to simpler pattern if the first one doesn't match
                filename_match = re.search(r'(?:named|called)\s+([^\s]+)', instruction)
                if filename_match:
                    filename = filename_match.group(1)
                    
                    # Look for content separately
                    content_match = re.search(r'(?:with|containing)\s+(.*)', instruction)
                    content = content_match.group(1) if content_match else "This is a new file."
                    
                    code += f"""
        # Create a new file
        file_path = workspace_path / "{filename}"
        logger.info(f"Creating file: {{file_path}}")
        with open(file_path, 'w') as f:
            f.write({repr(content)})
        logger.info(f"Successfully created file: {{file_path}}")
        return {{"success": True, "message": f"File created: {{file_path}}", "path": str(file_path)}}
"""
        elif "read" in instruction.lower() and "file" in instruction.lower():
            # Extract filename
            filename_match = re.search(r'(?:named|called|from)\s+["\']?([^"\']+)["\']?', instruction)
            if filename_match:
                filename = filename_match.group(1)
                
                code += f"""
        # Read a file
        file_path = workspace_path / "{filename}"
        logger.info(f"Reading file: {{file_path}}")
        if not file_path.exists():
            logger.error(f"File not found: {{file_path}}")
            return {{"success": False, "message": f"File not found: {{file_path}}"}}
        
        with open(file_path, 'r') as f:
            content = f.read()
        logger.info(f"Successfully read file: {{file_path}}")
        return {{"success": True, "message": f"File read: {{file_path}}", "content": content, "path": str(file_path)}}
"""
        elif "list" in instruction.lower() and ("files" in instruction.lower() or "directory" in instruction.lower()):
            # Extract directory path if specified
            dir_match = re.search(r'(?:in|from)\s+["\']?([^"\']+)["\']?', instruction)
            directory = dir_match.group(1) if dir_match else "."
            
            code += f"""
        # List files in a directory
        dir_path = workspace_path / "{directory}"
        logger.info(f"Listing files in: {{dir_path}}")
        if not dir_path.exists():
            logger.error(f"Directory not found: {{dir_path}}")
            return {{"success": False, "message": f"Directory not found: {{dir_path}}"}}
        
        files = os.listdir(dir_path)
        logger.info(f"Found {{len(files)}} items in {{dir_path}}")
        return {{"success": True, "message": f"Listed {{len(files)}} files in {{dir_path}}", "files": files, "path": str(dir_path)}}
"""
        elif "delete" in instruction.lower() and "file" in instruction.lower():
            # Extract filename
            filename_match = re.search(r'(?:named|called)\s+["\']?([^"\']+)["\']?', instruction)
            if filename_match:
                filename = filename_match.group(1)
                
                code += f"""
        # Delete a file
        file_path = workspace_path / "{filename}"
        logger.info(f"Deleting file: {{file_path}}")
        if not file_path.exists():
            logger.error(f"File not found: {{file_path}}")
            return {{"success": False, "message": f"File not found: {{file_path}}"}}
        
        os.remove(file_path)
        logger.info(f"Successfully deleted file: {{file_path}}")
        return {{"success": True, "message": f"File deleted: {{file_path}}", "path": str(file_path)}}
"""
        elif "create" in instruction.lower() and "directory" in instruction.lower():
            # Extract directory name
            dirname_match = re.search(r'(?:named|called)\s+["\']?([^"\']+)["\']?', instruction)
            if dirname_match:
                dirname = dirname_match.group(1)
                
                code += f"""
        # Create a directory
        dir_path = workspace_path / "{dirname}"
        logger.info(f"Creating directory: {{dir_path}}")
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Successfully created directory: {{dir_path}}")
        return {{"success": True, "message": f"Directory created: {{dir_path}}", "path": str(dir_path)}}
"""
        elif any(word in instruction.lower() for word in ["search", "find"]) and "file" in instruction.lower():
            # Extract search pattern
            pattern_match = re.search(r'(?:containing|with)\s+["\']?([^"\']+)["\']?', instruction)
            pattern = pattern_match.group(1) if pattern_match else ""
            
            code += f"""
        # Search for files
        logger.info(f"Searching for files with pattern: {pattern}")
        results = []
        
        for root, dirs, files in os.walk(workspace_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        if "{pattern}" in content:
                            results.append(file_path)
                except Exception as e:
                    logger.error(f"Error reading {{file_path}}: {{e}}")
        
        logger.info(f"Found {{len(results)}} matching files")
        return {{"success": True, "message": f"Found {{len(results)}} files containing '{pattern}'", "files": results}}
"""
        else:
            # Generic file manipulation if no specific pattern is matched
            code += f"""
        # Generic file manipulation
        logger.info("Analyzing instruction: {instruction}")
        # No specific operation matched
        return {{"success": False, "message": "Could not determine specific file operation from instruction"}}
"""
        
        # Close the functions and add the execution logic
        code += """
    except Exception as e:
        logger.error(f"Error during file manipulation: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Error: {str(e)}"}

if __name__ == "__main__":
    result = main()
    # Return result in a format that can be parsed
    print("RESULT_START")
    import json
    print(json.dumps(result))
    print("RESULT_END")
"""
        
        return code
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute the generated Python code safely
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results
        """
        self.last_code = code
        self.execution_count += 1
        
        # Check if code is safe
        is_safe, reason = self.is_safe_code(code)
        if not is_safe:
            logger.warning(f"Unsafe code detected: {reason}")
            return {
                "success": False,
                "message": f"Code execution failed: {reason}",
                "code": code
            }
        
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            temp_path = f.name
            f.write(code)
        
        try:
            # Execute code in subprocess
            logger.info(f"Executing generated code from {temp_path}")
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Parse the output
            output = result.stdout
            error = result.stderr
            
            # Extract structured result if available
            if "RESULT_START" in output and "RESULT_END" in output:
                try:
                    result_json = output.split("RESULT_START")[1].split("RESULT_END")[0].strip()
                    import json
                    parsed_result = json.loads(result_json)  # Use json.loads instead of eval
                    execution_result = {
                        "success": parsed_result.get("success", False),
                        "message": parsed_result.get("message", ""),
                        "result": parsed_result,
                        "stdout": output,
                        "stderr": error,
                        "code": code
                    }
                except Exception as e:
                    logger.error(f"Error parsing result: {e}")
                    execution_result = {
                        "success": False,
                        "message": f"Error parsing result: {str(e)}",
                        "stdout": output,
                        "stderr": error,
                        "code": code
                    }
            else:
                # No structured result, return raw output
                execution_result = {
                    "success": result.returncode == 0,
                    "message": "Code execution completed",
                    "stdout": output,
                    "stderr": error,
                    "code": code
                }
                
            logger.info(f"Code execution result: {execution_result['success']}")
            self.last_result = execution_result
            return execution_result
        
        except subprocess.TimeoutExpired:
            logger.error("Code execution timed out")
            return {
                "success": False,
                "message": "Code execution timed out (30 seconds)",
                "code": code
            }
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "success": False,
                "message": f"Error executing code: {str(e)}",
                "code": code
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def execute_file_operation(self, instruction: str) -> Dict[str, Any]:
        """
        Generate and execute code to perform a file operation based on natural language instruction
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Dictionary with operation results
        """
        # Generate code from instruction
        code = self.generate_file_manipulation_code(instruction)
        
        # Execute the generated code
        result = self.execute_code(code)
        
        # If first attempt failed, try to refine the code
        attempts = 1
        while (not result.get("success", False) and 
               attempts < self.max_attempts):
            logger.info(f"Retry attempt {attempts} for instruction: {instruction}")
            
            # Refine the code based on previous error
            error_msg = result.get("stderr", "")
            refined_code = self._refine_code_from_error(code, error_msg)
            
            # Only retry if code was refined
            if refined_code != code:
                code = refined_code
                result = self.execute_code(code)
                attempts += 1
            else:
                break
                
        return result
    
    def _refine_code_from_error(self, code: str, error_msg: str) -> str:
        """
        Refine code based on error message
        
        Args:
            code: Original code
            error_msg: Error message from execution
            
        Returns:
            Refined code
        """
        # Extract error information
        error_type_match = re.search(r'([A-Za-z]+Error):', error_msg)
        line_num_match = re.search(r'line (\d+)', error_msg)
        
        if not error_type_match or not line_num_match:
            return code
            
        error_type = error_type_match.group(1)
        line_num = int(line_num_match.group(1))
        
        # Get code lines
        code_lines = code.splitlines()
        
        # Adjust for offset between temp file and our code
        if line_num >= len(code_lines):
            # Can't fix this specific error
            return code
            
        # Check for common errors and fix them
        if error_type == "FileNotFoundError":
            # Add directory creation
            for i, line in enumerate(code_lines):
                if "open(" in line and "w" in line:
                    indent = line[:len(line) - len(line.lstrip())]
                    code_lines.insert(i, f"{indent}os.makedirs(os.path.dirname(file_path), exist_ok=True)")
                    break
        elif error_type == "PermissionError":
            # Try to use a more permissive approach
            for i, line in enumerate(code_lines):
                if "open(" in line:
                    code_lines[i] = code_lines[i].replace("open(", "open(")
                    break
        elif error_type == "SyntaxError":
            # Try to fix syntax errors
            problem_line = code_lines[line_num - 1]
            if problem_line.strip().endswith(":"):
                # Missing indented block
                code_lines[line_num - 1] += "\n    pass"
            elif "(" in problem_line and ")" not in problem_line:
                # Missing closing parenthesis
                code_lines[line_num - 1] += ")"
        
        return "\n".join(code_lines)
    
    def generate_and_execute(self, instruction: str) -> str:
        """
        High-level function to generate code and execute it based on instruction
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            str: Result of the execution
        """
        try:
            # Check if this is a file operation
            operation_type, params = self.parse_instruction(instruction)
            
            # If it's a known file operation, handle it directly
            if operation_type != "unknown":
                # Generate and execute the appropriate code
                if operation_type == "create_file":
                    return self.create_file(params.get("filename"), params.get("content", ""))
                elif operation_type == "read_file":
                    return self.read_file(params.get("filename"))
                elif operation_type == "delete_file":
                    return self.delete_file(params.get("filename"))
                elif operation_type == "list_files":
                    return self.list_files(params.get("directory", "."))
                elif operation_type == "search_files":
                    return self.search_files(params.get("pattern"), params.get("directory", "."))
                elif operation_type == "create_directory":
                    return self.create_directory(params.get("directory"))
            
            # If it's not a file operation, treat it as a general query to the AI
            return self.get_ai_response(instruction)
            
        except Exception as e:
            self.logger.error(f"Error executing operation: {e}", exc_info=True)
            return f"Error: {str(e)}"
            
    def get_ai_response(self, query: str) -> str:
        """
        Get a response from the AI for a general query
        
        Args:
            query: The user's query
            
        Returns:
            str: The AI's response
        """
        try:
            # For general queries, provide a helpful response
            if "hello" in query.lower() or "hi" in query.lower():
                return "Hello there! 👋 How can I help you today?"
                
            elif "how are you" in query.lower():
                return "I'm doing well, thank you for asking! How can I assist you with file operations today?"
                
            elif "what can you do" in query.lower() or "help" in query.lower():
                return """I can help you with various file operations, such as:
                
1. Creating files: "create file named example.txt with Hello, World!"
2. Reading files: "read file example.txt"
3. Deleting files: "delete file example.txt"
4. Listing files: "list files in ."
5. Searching files: "search files containing example"
6. Creating directories: "create directory docs"

Just let me know what you'd like to do!"""
                
            else:
                return f"I'm an AI assistant that can help with file operations. If you want to work with files, try commands like 'create file', 'read file', etc. Type 'help' for more information."
                
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}", exc_info=True)
            return f"Error generating response: {str(e)}"

    def create_file(self, filename: str, content: str) -> str:
        """Create a file with the given content"""
        if not filename:
            return "Error: No filename provided"
        
        try:
            filepath = self.workspace_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            return f"File '{filename}' created successfully"
        except Exception as e:
            self.logger.error(f"Error creating file: {e}", exc_info=True)
            return f"Error creating file: {str(e)}"

    def read_file(self, filename: str) -> str:
        """Read the contents of a file"""
        if not filename:
            return "Error: No filename provided"
        
        try:
            filepath = self.workspace_path / filename
            with open(filepath, 'r') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"Error: File '{filename}' not found"
        except Exception as e:
            self.logger.error(f"Error reading file: {e}", exc_info=True)
            return f"Error reading file: {str(e)}"

    def delete_file(self, filename: str) -> str:
        """Delete a file"""
        if not filename:
            return "Error: No filename provided"
        
        try:
            filepath = self.workspace_path / filename
            if not filepath.exists():
                return f"Error: File '{filename}' not found"
            
            filepath.unlink()
            return f"File '{filename}' deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}", exc_info=True)
            return f"Error deleting file: {str(e)}"

    def list_files(self, directory: str = ".") -> str:
        """List files in a directory"""
        try:
            dirpath = self.workspace_path / directory
            if not dirpath.exists():
                return f"Error: Directory '{directory}' not found"
            
            files = [f.name for f in dirpath.iterdir()]
            if not files:
                return f"No files found in '{directory}'"
            
            result = f"Files in '{directory}':\n"
            for i, file in enumerate(files, 1):
                result += f"{i}. {file}\n"
            return result
        except Exception as e:
            self.logger.error(f"Error listing files: {e}", exc_info=True)
            return f"Error listing files: {str(e)}"

    def search_files(self, pattern: str, directory: str = ".") -> str:
        """Search for files containing a pattern"""
        if not pattern:
            return "Error: No search pattern provided"
        
        try:
            dirpath = self.workspace_path / directory
            if not dirpath.exists():
                return f"Error: Directory '{directory}' not found"
            
            matching_files = []
            for filepath in dirpath.glob("**/*"):
                if filepath.is_file():
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            if pattern in content:
                                matching_files.append(str(filepath.relative_to(self.workspace_path)))
                    except:
                        # Skip files that can't be read as text
                        pass
            
            if not matching_files:
                return f"No files containing '{pattern}' found in '{directory}'"
            
            result = f"Files containing '{pattern}':\n"
            for i, file in enumerate(matching_files, 1):
                result += f"{i}. {file}\n"
            return result
        except Exception as e:
            self.logger.error(f"Error searching files: {e}", exc_info=True)
            return f"Error searching files: {str(e)}"

    def create_directory(self, directory: str) -> str:
        """Create a directory"""
        if not directory:
            return "Error: No directory name provided"
        
        try:
            dirpath = self.workspace_path / directory
            dirpath.mkdir(parents=True, exist_ok=True)
            return f"Directory '{directory}' created successfully"
        except Exception as e:
            self.logger.error(f"Error creating directory: {e}", exc_info=True)
            return f"Error creating directory: {str(e)}"

    def parse_instruction(self, instruction: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse a natural language instruction to determine the operation and parameters
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Tuple of (operation_type, parameters)
        """
        instruction = instruction.lower()
        params = {}
        
        # Create file
        if "create file" in instruction:
            # Extract filename
            filename_match = re.search(r"create file (?:named|called)? ([^\s]+)", instruction)
            if filename_match:
                params["filename"] = filename_match.group(1)
            
            # Extract content
            content_match = re.search(r"with (.*?)$", instruction)
            if content_match:
                params["content"] = content_match.group(1)
            
            return "create_file", params
        
        # Read file
        elif "read file" in instruction:
            filename_match = re.search(r"read file ([^\s]+)", instruction)
            if filename_match:
                params["filename"] = filename_match.group(1)
            
            return "read_file", params
        
        # Delete file
        elif "delete file" in instruction:
            filename_match = re.search(r"delete file ([^\s]+)", instruction)
            if filename_match:
                params["filename"] = filename_match.group(1)
            
            return "delete_file", params
        
        # List files
        elif "list files" in instruction:
            dir_match = re.search(r"list files (?:in|from) ([^\s]+)", instruction)
            if dir_match:
                params["directory"] = dir_match.group(1)
            
            return "list_files", params
        
        # Search files
        elif "search files" in instruction:
            pattern_match = re.search(r"search files (?:containing|with) ([^\s]+)", instruction)
            if pattern_match:
                params["pattern"] = pattern_match.group(1)
            
            dir_match = re.search(r"in ([^\s]+)", instruction)
            if dir_match:
                params["directory"] = dir_match.group(1)
            
            return "search_files", params
        
        # Create directory
        elif "create directory" in instruction or "create folder" in instruction:
            dir_match = re.search(r"create (?:directory|folder) ([^\s]+)", instruction)
            if dir_match:
                params["directory"] = dir_match.group(1)
            
            return "create_directory", params
        
        # Default to unknown operation
        return "unknown", params 