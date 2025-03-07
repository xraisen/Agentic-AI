from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QSystemTrayIcon, QMenu, QLabel)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QAction
import sys
import asyncio
from ..core.ai_engine import AIEngine
from ..utils.logger import log_action, log_error, log_debug
from pathlib import Path

class KnowledgeDialog(QDialog):
    """Dialog for displaying knowledge management information."""
    
    def __init__(self, ai_engine, parent=None):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.init_ui()
        self.update_content()
        log_action("Knowledge dialog opened", "Displaying knowledge management interface")

    def init_ui(self):
        """Initialize the dialog UI."""
        try:
            self.setWindowTitle('Knowledge Management')
            self.setGeometry(200, 200, 800, 600)

            layout = QVBoxLayout(self)
            
            # Create tab widget
            tabs = QTabWidget()
            
            # Summary tab
            summary_tab = QWidget()
            summary_layout = QVBoxLayout(summary_tab)
            self.summary_text = QTextEdit()
            self.summary_text.setReadOnly(True)
            summary_layout.addWidget(self.summary_text)
            tabs.addTab(summary_tab, "Summary")
            
            # History tab
            history_tab = QWidget()
            history_layout = QVBoxLayout(history_tab)
            self.history_text = QTextEdit()
            self.history_text.setReadOnly(True)
            history_layout.addWidget(self.history_text)
            tabs.addTab(history_tab, "History")
            
            # Actions tab
            actions_tab = QWidget()
            actions_layout = QVBoxLayout(actions_tab)
            self.actions_text = QTextEdit()
            self.actions_text.setReadOnly(True)
            actions_layout.addWidget(self.actions_text)
            tabs.addTab(actions_tab, "Actions")
            
            layout.addWidget(tabs)
            
            # Add refresh button
            refresh_button = QPushButton('Refresh')
            refresh_button.clicked.connect(self.update_content)
            layout.addWidget(refresh_button)
            
            log_debug("Knowledge dialog UI initialized", "All components created")
        except Exception as e:
            log_error(e, "Failed to initialize knowledge dialog UI")
            QMessageBox.critical(self, "Error", "Failed to initialize knowledge dialog")
            raise

    def update_content(self):
        """Update the content of all tabs."""
        try:
            # Update summary
            summary = self.ai_engine.get_knowledge_summary()
            self.summary_text.setText(summary)
            
            # Update history
            history = self.ai_engine.get_history()
            history_text = "Conversation History:\n\n"
            for entry in history:
                history_text += f"[{entry['timestamp']}]\n"
                history_text += f"User: {entry['prompt']}\n"
                history_text += f"AI: {entry['response']}\n\n"
            self.history_text.setText(history_text)
            
            # Update actions
            actions = self.ai_engine.knowledge_manager.get_recent_actions(50)
            actions_text = "Recent Actions:\n\n"
            for action in actions:
                actions_text += f"[{action['timestamp']}] {action['details']}\n"
            self.actions_text.setText(actions_text)
            
            log_action("Knowledge content updated", "All tabs refreshed")
        except Exception as e:
            log_error(e, "Failed to update knowledge content")
            QMessageBox.warning(self, "Warning", "Failed to update knowledge content")
            self.summary_text.setText(f"Error updating content: {str(e)}")

class AIWorker(QThread):
    """Worker thread for AI processing."""
    
    response_ready = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, engine, prompt):
        """Initialize the worker thread."""
        super().__init__()
        self.engine = engine
        self.prompt = prompt
        log_action("Worker initialized", f"Prompt: {prompt[:100]}...")
    
    def run(self):
        """Process the prompt and emit the response."""
        try:
            log_action("Processing started", "Worker thread running")
            response = self.engine.get_response(self.prompt)
            self.response_ready.emit(response)
            log_action("Processing complete", f"Response length: {len(response)}")
        except Exception as e:
            error_msg = f"Error processing prompt: {str(e)}"
            self.error_occurred.emit(error_msg)
            log_error(e, "Worker thread error")

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Agentic AI")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize components
        self.setup_ui()
        self.setup_tray()
        self.ai_engine = AIEngine()
        
        log_action("Window initialized", "Main window setup complete")
    
    def setup_ui(self):
        """Set up the user interface."""
        try:
            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Create chat display
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            layout.addWidget(self.chat_display)
            
            # Create input area
            input_layout = QHBoxLayout()
            self.input_field = QTextEdit()
            self.input_field.setMaximumHeight(100)
            input_layout.addWidget(self.input_field)
            
            # Create send button
            send_button = QPushButton("Send")
            send_button.clicked.connect(self.send_message)
            input_layout.addWidget(send_button)
            
            layout.addLayout(input_layout)
            
            # Create status bar
            self.status_label = QLabel("Ready")
            self.statusBar().addWidget(self.status_label)
            
            log_action("UI setup complete", "Interface components initialized")
            
        except Exception as e:
            log_error(e, "Failed to set up UI")
            raise
    
    def setup_tray(self):
        """Set up the system tray icon."""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("assets/icon.png"))
            
            # Create tray menu
            tray_menu = QMenu()
            show_action = QAction("Show", self)
            quit_action = QAction("Quit", self)
            clear_action = QAction("Clear Chat", self)
            
            show_action.triggered.connect(self.show)
            quit_action.triggered.connect(self.close)
            clear_action.triggered.connect(self.clear_chat)
            
            tray_menu.addAction(show_action)
            tray_menu.addAction(clear_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            log_action("Tray setup complete", "System tray icon initialized")
            
        except Exception as e:
            log_error(e, "Failed to set up system tray")
            raise
    
    def send_message(self):
        """Send a message to the AI engine."""
        try:
            message = self.input_field.toPlainText().strip()
            if not message:
                return
            
            # Display user message
            self.chat_display.append(f"You: {message}")
            self.input_field.clear()
            
            # Process with AI
            self.status_label.setText("Processing...")
            self.worker = AIWorker(self.ai_engine, message)
            self.worker.response_ready.connect(self.handle_response)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.start()
            
            log_action("Message sent", f"User message: {message[:100]}...")
            
        except Exception as e:
            log_error(e, "Failed to send message")
            self.handle_error(str(e))
    
    def handle_response(self, response):
        """Handle the AI response."""
        try:
            self.chat_display.append(f"AI: {response}")
            self.status_label.setText("Ready")
            log_action("Response handled", f"AI response length: {len(response)}")
        except Exception as e:
            log_error(e, "Failed to handle response")
            self.handle_error(str(e))
    
    def handle_error(self, error_message):
        """Handle errors in the application."""
        self.status_label.setText("Error")
        self.chat_display.append(f"Error: {error_message}")
        log_error(Exception(error_message), "Error in main window")
    
    def clear_chat(self):
        """Clear the chat display."""
        try:
            self.chat_display.clear()
            log_action("Chat cleared", "Chat display cleared")
        except Exception as e:
            log_error(e, "Failed to clear chat")
            self.handle_error(str(e))
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            event.ignore()
            self.hide()
            log_action("Window minimized", "Application minimized to tray")
        except Exception as e:
            log_error(e, "Failed to handle close event")
            event.accept() 