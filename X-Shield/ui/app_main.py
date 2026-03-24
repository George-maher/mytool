"""
X-Shield Professional MVC Application
Main Application with Modern Minimal design system and modular architecture
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.sidebar import Sidebar
from ui.components.stacked_content import StackedContent
from ui.pages.dashboard_page import DashboardPage
from ui.pages.target_manager_page import TargetManagerPage
from ui.pages.network_scanner_page import NetworkScannerPage
from ui.pages.web_scanner_page import WebScannerPage
from ui.pages.osint_page import OSINTPage
from ui.pages.reports_page_new import ReportsPage
from ui.pages.settings_page_new import SettingsPage
from core.target_manager import TargetManager
from core.module_manager import ModuleManager
from core.logger_new import XShieldLogger
from ui.components.styles import get_main_stylesheet


class XShieldApp(QMainWindow):
    """Main Application Window with Professional MVC Architecture"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.logger = XShieldLogger()
        self.target_manager = TargetManager(self.logger)
        self.module_manager = ModuleManager(self.logger)
        
        # Window setup
        self.setWindowTitle("X-Shield Cybersecurity Framework")
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(900, 800)
        
        # Apply Modern Minimal design system
        self.apply_theme()
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Setup update timer
        self.setup_timers()
        
        self.logger.info("X-Shield Professional Application initialized")
    
    def apply_theme(self):
        """Apply Modern Minimal design system"""
        try:
            self.setStyleSheet(get_main_stylesheet())
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
            self.setStyleSheet("QMainWindow { background-color: #09090b; color: white; }")
    
    def setup_ui(self):
        """Setup main UI layout with improved spacing"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with proper margins and spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)  # Add breathing room around edges
        main_layout.setSpacing(12)  # Space between sidebar and content
        
        # Create sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.setObjectName("sidebar")
        main_layout.addWidget(self.sidebar)
        
        # Create content container with proper margins
        content_container = QFrame()
        content_container.setObjectName("content_area")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create stacked content area
        self.stacked_content = StackedContent(
            self.target_manager,
            self.module_manager,
            self.logger,
            self
        )
        self.stacked_content.setObjectName("content_area")
        content_layout.addWidget(self.stacked_content)
        
        # Add content container to main layout
        main_layout.addWidget(content_container)
        
        # Set layout proportions (25% sidebar, 75% content for better balance)
        main_layout.setStretchFactor(self.sidebar, 1)
        main_layout.setStretchFactor(content_container, 3)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect sidebar navigation to content switching
        self.sidebar.navigation_requested.connect(self.stacked_content.switch_page)
        
        # Connect target manager signals
        self.target_manager.target_added.connect(self.on_target_added)
        self.target_manager.target_removed.connect(self.on_target_removed)
        self.target_manager.target_updated.connect(self.on_target_updated)
    
    def setup_timers(self):
        """Setup update timers"""
        # Dashboard update timer
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.update_dashboard_stats)
        self.dashboard_timer.start(5000)  # Update every 5 seconds
    
    def get_active_target(self):
        """Get the currently active target from target manager"""
        return self.target_manager.get_active_target()
    
    def get_logger(self):
        """Get the application logger"""
        return self.logger
    
    def get_target_manager(self):
        """Get the target manager instance"""
        return self.target_manager
    
    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        try:
            dashboard_page = self.stacked_content.get_page("dashboard")
            if dashboard_page:
                dashboard_page.update_statistics()
        except Exception as e:
            self.logger.error(f"Failed to update dashboard stats: {e}")
    
    @Slot(str, dict)
    def on_target_added(self, target_id, target_data):
        """Handle target addition"""
        self.logger.info(f"Target added: {target_id}")
        # Update any pages that need to know about new targets
        dashboard_page = self.stacked_content.get_page("dashboard")
        if dashboard_page:
            dashboard_page.update_target_count()
    
    @Slot(str)
    def on_target_removed(self, target_id):
        """Handle target removal"""
        self.logger.info(f"Target removed: {target_id}")
        # Update any pages that need to know about removed targets
        dashboard_page = self.stacked_content.get_page("dashboard")
        if dashboard_page:
            dashboard_page.update_target_count()
    
    @Slot(str, dict)
    def on_target_updated(self, target_id, target_data):
        """Handle target updates"""
        self.logger.info(f"Target updated: {target_id}")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.logger.info("X-Shield Application closing")
        
        # Cleanup resources
        self.target_manager.cleanup()
        
        # Accept close event
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("X-Shield")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("X-Shield Security")
    
    # Create and show main window
    window = XShieldApp()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
