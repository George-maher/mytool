"""
X-Shield Cybersecurity Framework - Professional MVC Architecture
Main entry point using the new modular MVC design
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import warnings

# Suppress Qt warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the new MVC application
from ui.app_main import XShieldApp


def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def main():
    """Main entry point for X-Shield Framework"""
    
    # Check for administrator privileges
    if not check_admin_privileges():
        print("WARNING: Administrator privileges recommended for full functionality")
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("X-Shield")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("X-Shield Security")
        
        # Create and show main window
        window = XShieldApp()
        window.show()
        
        print("X-Shield Professional MVC Framework started successfully!")
        print("Features:")
        print("  - Professional qt-material dark_teal theme")
        print("  - Modular MVC architecture")
        print("  - Central target management")
        print("  - Background threading for scanners")
        print("  - Professional dashboard and UI")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Failed to start X-Shield: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
