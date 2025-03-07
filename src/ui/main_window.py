"""
Main Window UI for Agentic AI
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QPushButton, QLabel,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from ..api.client import APIClient

class MainWindow(QMainWindow):
    """Main window for the Agentic AI application"""
    
    def __init__(self, config: Dict[str, Any], api_client: APIClient):
        """Initialize the main window"""
        super().__init__()
        self.config = config
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Setup the user interface"""
        # Set window properties
        self.setWindowTitle(f"{self.config['app']['name']} v{self.config['app']['version']}")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        # Model selection
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.config['api']['openrouter']['models'])
        input_layout.addWidget(model_label)
        input_layout.addWidget(self.model_combo)
        
        # Temperature control
        temp_label = QLabel("Temperature:")
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setValue(self.config['ai']['temperature'])
        self.temp_spin.setSingleStep(0.1)
        input_layout.addWidget(temp_label)
        input_layout.addWidget(self.temp_spin)
        
        # Max tokens control
        tokens_label = QLabel("Max Tokens:")
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(1, 4096)
        self.tokens_spin.setValue(self.config['ai']['max_tokens'])
        input_layout.addWidget(tokens_label)
        input_layout.addWidget(self.tokens_spin)
        
        layout.addLayout(input_layout)
        
        # Create prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        layout.addWidget(self.prompt_input)
        
        # Create button area
        button_layout = QHBoxLayout()
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_prompt)
        button_layout.addWidget(self.send_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_prompt)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Create response area
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        layout.addWidget(self.response_output)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Setup system tray
        self.setup_system_tray()
        
        # Setup shortcuts
        self.setup_shortcuts()
        
    def setup_system_tray(self) -> None:
        """Setup the system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icon.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts"""
        send_shortcut = QAction("Send", self)
        send_shortcut.setShortcut(QKeySequence("Ctrl+Return"))
        send_shortcut.triggered.connect(self.send_prompt)
        self.addAction(send_shortcut)
        
        clear_shortcut = QAction("Clear", self)
        clear_shortcut.setShortcut(QKeySequence("Ctrl+L"))
        clear_shortcut.triggered.connect(self.clear_prompt)
        self.addAction(clear_shortcut)
        
    def send_prompt(self) -> None:
        """Send the prompt to the AI"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt")
            return
            
        try:
            # Update status
            self.statusBar().showMessage("Processing...")
            self.send_button.setEnabled(False)
            
            # Get completion
            model = self.model_combo.currentText()
            response = self.api_client.get_completion(prompt, model)
            
            if response:
                self.response_output.append(f"AI: {response}")
            else:
                QMessageBox.critical(self, "Error", "Failed to get AI response")
                
        except Exception as e:
            self.logger.error(f"Error sending prompt: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            
        finally:
            self.statusBar().showMessage("Ready")
            self.send_button.setEnabled(True)
            
    def clear_prompt(self) -> None:
        """Clear the prompt input"""
        self.prompt_input.clear()
        
    def closeEvent(self, event) -> None:
        """Handle window close event"""
        if self.config['desktop']['startup']:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Agentic AI",
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()
            
    def initialize(self) -> bool:
        """Initialize the main window"""
        try:
            # Check for required assets
            if not os.path.exists("assets/icon.png"):
                self.logger.warning("Icon file not found")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize main window: {str(e)}")
            return False
            
    def run(self) -> int:
        """Run the application"""
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
                
            self.show()
            return app.exec()
            
        except Exception as e:
            self.logger.error(f"Failed to run application: {str(e)}")
            return 1 