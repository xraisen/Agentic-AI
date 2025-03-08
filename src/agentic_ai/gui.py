"""Graphical user interface for Agentic AI."""

import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import os
from pathlib import Path
import sys
import time

# Import the code generator
from src.utils.code_generator import CodeGenerator

class MainWindow(tk.Tk):
    """Main window of the Agentic AI GUI."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.title("Agentic AI - File Manipulation Assistant")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Set icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass  # Ignore icon errors
        
        # Initialize workspace
        self.workspace_path = Path.cwd()
        
        # Initialize code generator
        self.code_generator = CodeGenerator(workspace_path=self.workspace_path)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create chat/output display
        self.create_output_display()
        
        # Create input frame
        self.create_input_area()
        
        # Create status bar
        self.create_status_bar()
        
        # Task queue for background operations
        self.task_queue = queue.Queue()
        self.after(100, self.process_queue)
        
        # Log window creation
        logger = logging.getLogger(__name__)
        logger.info("Main window initialized")
        
        # Display welcome message
        self.add_system_message("Welcome to Agentic AI File Manipulation Assistant!")
        self.add_system_message(f"Current workspace: {self.workspace_path}")
        self.add_system_message("Type your file operation instructions below or use the toolbar to select options.")
        self.add_system_message("Examples:")
        self.add_system_message("  - create file named example.txt with Hello World")
        self.add_system_message("  - read file config.json")
        self.add_system_message("  - list files in src")
        
        # Add protocol for window closing
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_toolbar(self):
        """Create the toolbar with buttons"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Workspace button
        self.workspace_btn = ttk.Button(toolbar, text="Change Workspace", command=self.change_workspace)
        self.workspace_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        self.help_btn = ttk.Button(toolbar, text="Help", command=self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = ttk.Button(toolbar, text="Clear Display", command=self.clear_display)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Examples dropdown
        self.examples_label = ttk.Label(toolbar, text="Examples:")
        self.examples_label.pack(side=tk.LEFT, padx=(15, 5))
        
        self.examples_var = tk.StringVar()
        examples = [
            "Choose an example...",
            "Create a text file",
            "Read a file",
            "List files in directory",
            "Search for files",
            "Delete a file",
            "Create a directory"
        ]
        self.examples_combo = ttk.Combobox(toolbar, textvariable=self.examples_var, values=examples, width=25)
        self.examples_combo.current(0)
        self.examples_combo.pack(side=tk.LEFT, padx=5)
        self.examples_combo.bind("<<ComboboxSelected>>", self.example_selected)
    
    def create_output_display(self):
        """Create the output display area"""
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Use scrolledtext for better handling of large outputs
        self.output_display = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for different message types
        self.output_display.tag_configure("user", foreground="blue")
        self.output_display.tag_configure("assistant", foreground="green")
        self.output_display.tag_configure("system", foreground="gray")
        self.output_display.tag_configure("error", foreground="red")
        self.output_display.tag_configure("success", foreground="green")
        self.output_display.tag_configure("code", foreground="purple", font=("Courier", 10))
    
    def create_input_area(self):
        """Create the input area with prompt and command entry"""
        input_frame = ttk.LabelFrame(self.main_frame, text="Command Input", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Use multi-line text box for input
        self.input_field = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=3)
        self.input_field.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_command)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Bind Enter key to send
        self.input_field.bind("<Control-Return>", lambda e: self.send_command())
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def process_queue(self):
        """Process tasks in the queue"""
        try:
            while True:
                task = self.task_queue.get_nowait()
                task()
                self.task_queue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.process_queue)
    
    def add_message(self, message: str, message_type: str = "assistant"):
        """Add a message to the output display.
        
        Args:
            message: The message to display.
            message_type: Type of message ("user", "assistant", "system", "error", "success", "code")
        """
        def _add():
            self.output_display.configure(state=tk.NORMAL)
            
            # Add timestamp
            timestamp = time.strftime("[%H:%M:%S] ")
            self.output_display.insert(tk.END, timestamp, "system")
            
            # Add prefix based on message type
            if message_type == "user":
                self.output_display.insert(tk.END, "You: ", "user")
            elif message_type == "assistant":
                self.output_display.insert(tk.END, "AI: ", "assistant")
            elif message_type == "system":
                pass  # No prefix for system messages
            elif message_type == "error":
                self.output_display.insert(tk.END, "Error: ", "error")
            elif message_type == "success":
                self.output_display.insert(tk.END, "Success: ", "success")
            
            # Insert message with appropriate tag
            self.output_display.insert(tk.END, f"{message}\n", message_type)
            
            # Scroll to end
            self.output_display.configure(state=tk.DISABLED)
            self.output_display.see(tk.END)
            
        self.task_queue.put(_add)
    
    def add_user_message(self, message: str):
        """Add a user message to the output display."""
        self.add_message(message, "user")
    
    def add_system_message(self, message: str):
        """Add a system message to the output display."""
        self.add_message(message, "system")
    
    def add_error_message(self, message: str):
        """Add an error message to the output display."""
        self.add_message(message, "error")
    
    def add_success_message(self, message: str):
        """Add a success message to the output display."""
        self.add_message(message, "success")
    
    def add_code_block(self, code: str):
        """Add a code block to the output display."""
        def _add():
            self.output_display.configure(state=tk.NORMAL)
            
            # Add section header
            self.output_display.insert(tk.END, "\nGenerated Code:\n", "system")
            
            # Add code with syntax highlighting
            self.output_display.insert(tk.END, f"{code}\n\n", "code")
            
            # Scroll to end
            self.output_display.configure(state=tk.DISABLED)
            self.output_display.see(tk.END)
            
        self.task_queue.put(_add)
    
    def update_status(self, status: str):
        """Update the status bar text."""
        def _update():
            self.status_bar.config(text=status)
        self.task_queue.put(_update)
    
    def send_command(self):
        """Send the current input to the AI assistant."""
        command = self.input_field.get("1.0", tk.END).strip()
        if not command:
            return
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Add user message to display
        self.add_user_message(command)
        
        # Process command in background thread to avoid freezing GUI
        self.update_status("Processing command...")
        threading.Thread(target=self._process_command, args=(command,), daemon=True).start()
    
    def _process_command(self, command: str):
        """Process a command in a background thread."""
        try:
            # Check for built-in commands
            if command.lower() in ['exit', 'quit']:
                self.add_system_message("Use the window close button to exit the application.")
                self.update_status("Ready")
                return
            elif command.lower() == 'help':
                self._show_help()
                self.update_status("Ready")
                return
            elif command.lower() == 'clear':
                self.clear_display()
                self.update_status("Ready")
                return
            elif command.lower().startswith('workspace'):
                self.change_workspace()
                self.update_status("Ready")
                return
            
            # Handle file operation using the code generator
            self.add_system_message(f"Processing: {command}")
            
            # Generate and execute code
            success, message, result = self.code_generator.generate_and_execute(command)
            
            # Show the generated code
            if 'code' in result:
                self.add_code_block(result['code'])
            
            # Display results
            if success:
                self.add_success_message(message)
                
                # If we have result data to display
                if 'result' in result and isinstance(result['result'], dict):
                    result_data = result['result']
                    
                    # For file read operations, show content
                    if 'content' in result_data:
                        self.add_system_message("File Content:")
                        self.add_system_message("─" * 50)
                        self.add_message(result_data['content'], "assistant")
                        self.add_system_message("─" * 50)
                    
                    # For list operations, show files
                    if 'files' in result_data:
                        self.add_system_message("Files:")
                        files_output = "\n".join([f"{i+1}. {file}" for i, file in enumerate(result_data['files'])])
                        self.add_message(files_output, "assistant")
            else:
                self.add_error_message(message)
                
                # Show error details if available
                if 'stderr' in result and result['stderr']:
                    self.add_system_message("Error details:")
                    self.add_error_message(result['stderr'])
        except Exception as e:
            self.add_error_message(f"Error processing command: {str(e)}")
        finally:
            self.update_status("Ready")
    
    def change_workspace(self):
        """Open a dialog to change the workspace directory."""
        new_workspace = filedialog.askdirectory(
            title="Select Workspace Directory",
            initialdir=self.workspace_path
        )
        
        if new_workspace:
            # Update workspace path
            self.workspace_path = Path(new_workspace)
            
            # Update code generator
            self.code_generator = CodeGenerator(workspace_path=self.workspace_path)
            
            # Display confirmation
            self.add_system_message(f"Workspace changed to: {self.workspace_path}")
    
    def clear_display(self):
        """Clear the output display."""
        def _clear():
            self.output_display.configure(state=tk.NORMAL)
            self.output_display.delete("1.0", tk.END)
            self.output_display.configure(state=tk.DISABLED)
            
            # Show welcome message again
            self.add_system_message("Display cleared.")
            self.add_system_message(f"Current workspace: {self.workspace_path}")
            
        self.task_queue.put(_clear)
    
    def _show_help(self):
        """Show help information."""
        help_text = [
            "Agentic AI File Manipulation Assistant Help",
            "",
            "This application allows you to manipulate files using natural language commands.",
            "",
            "Commands:",
            "  help - Show this help message",
            "  clear - Clear the display",
            "  workspace - Change the workspace directory",
            "",
            "File Operations (examples):",
            "  create file named example.txt with Hello, World!",
            "  read file example.txt",
            "  delete file example.txt",
            "  list files in .",
            "  search files containing example",
            "  create directory docs",
            "",
            "Try using natural language to describe what you want to do!"
        ]
        
        for line in help_text:
            self.add_system_message(line)
    
    def show_help(self):
        """Show the help dialog."""
        messagebox.showinfo(
            "Agentic AI Help",
            "Agentic AI File Manipulation Assistant\n\n"
            "This application allows you to manipulate files using natural language commands.\n\n"
            "Examples:\n"
            "- create file named example.txt with Hello, World!\n"
            "- read file example.txt\n"
            "- list files in .\n"
            "- search files containing example\n"
            "- create directory docs\n\n"
            "Type 'help' in the command input for more information."
        )
    
    def example_selected(self, event):
        """Handle example selection from dropdown."""
        selected = self.examples_var.get()
        
        # Reset dropdown to default
        self.examples_combo.current(0)
        
        if selected == "Choose an example...":
            return
            
        # Set example command based on selection
        if selected == "Create a text file":
            command = "create file named example.txt with Hello from Agentic AI!"
        elif selected == "Read a file":
            command = "read file README.md"
        elif selected == "List files in directory":
            command = "list files in ."
        elif selected == "Search for files":
            command = "search files containing import"
        elif selected == "Delete a file":
            command = "delete file example.txt"
        elif selected == "Create a directory":
            command = "create directory example_dir"
        else:
            return
            
        # Insert command into input field
        self.input_field.delete("1.0", tk.END)
        self.input_field.insert("1.0", command)
    
    def on_close(self):
        """Handle window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit Agentic AI?"):
            self.destroy()

def main(args: list[str]) -> int:
    """Run the Agentic AI GUI.
    
    Args:
        args: Command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create and run the main window
        app = MainWindow()
        
        # Set the window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "assets", "icon.ico")
            if os.path.exists(icon_path):
                app.iconbitmap(icon_path)
        except:
            pass  # Ignore icon errors
        
        # Run the main loop
        app.mainloop()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error in GUI: {e}", exc_info=True)
        messagebox.showerror("Error", f"An error occurred: {str(e)}\n\nCheck logs for details.")
        return 1 