"""Graphical user interface for Agentic AI."""

import logging
import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Tk):
    """Main window of the Agentic AI GUI."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.title("Agentic AI")
        self.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create chat display
        self.chat_display = tk.Text(self.main_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create input frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create input field
        self.input_field = ttk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to send
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
    def send_message(self):
        """Send the current input to the AI assistant."""
        message = self.input_field.get().strip()
        if message:
            # TODO: Implement message sending
            self.input_field.delete(0, tk.END)
            
    def add_message(self, message: str, is_user: bool = False):
        """Add a message to the chat display.
        
        Args:
            message: The message to display.
            is_user: Whether the message is from the user.
        """
        self.chat_display.configure(state=tk.NORMAL)
        prefix = "You: " if is_user else "AI: "
        self.chat_display.insert(tk.END, f"{prefix}{message}\n")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

def main(args: list[str]) -> int:
    """Run the Agentic AI GUI.
    
    Args:
        args: Command line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    logger = logging.getLogger(__name__)
    
    try:
        app = MainWindow()
        app.mainloop()
        return 0
        
    except Exception as e:
        logger.error(f"Error in GUI: {e}", exc_info=True)
        return 1 