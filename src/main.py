import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main entry point for the Agentic AI application."""
    try:
        log_action("Application starting", "Initializing Agentic AI")
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        log_action("Application initialized", "Main window displayed")
        
        # Start the event loop
        sys.exit(app.exec())
    except Exception as e:
        log_error(e, "Application failed to start")
        sys.exit(1)

if __name__ == '__main__':
    main() 