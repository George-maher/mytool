"""
X-Shield Professional MVC Application
Main Application with qt-material dark_teal theme and modular architecture
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.sidebar import Sidebar
from ui.stacked_content import StackedContent
from ui.dashboard_page import DashboardPage
from ui.target_manager_page import TargetManagerPage
from ui.network_scanner_page import NetworkScannerPage
from ui.web_scanner_page import WebScannerPage
from ui.osint_page import OSINTPage
from ui.reports_page_new import ReportsPage
from ui.settings_page_new import SettingsPage
from core.target_manager import TargetManager
from core.logger_new import XShieldLogger


class XShieldApp(QMainWindow):
    """Main Application Window with Professional MVC Architecture"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.logger = XShieldLogger()
        self.target_manager = TargetManager(self.logger)
        
        # Window setup
        self.setWindowTitle("X-Shield Cybersecurity Framework")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1200, 800)
        
        # Apply qt-material dark_teal theme
        self.apply_theme()
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Setup update timer
        self.setup_timers()
        
        self.logger.info("X-Shield Professional Application initialized")
    
    def apply_theme(self):
        """Apply qt-material dark_teal theme"""
        try:
            apply_stylesheet(self, theme='dark_teal.xml', invert_secondary=False)
            
            # Additional custom styling for professional look
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                }
                
                /* Enhanced Sidebar Styling */
                #sidebar {
                    background-color: #0d3b3b;
                    border-right: 2px solid #1a4a4a;
                }
                
                /* Enhanced Content Area */
                #content_area {
                    background-color: #1a1a1a;
                }
                
                /* Professional Button Styling - LARGER */
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    border: none;
                    padding: 16px 32px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 16px;
                    min-height: 24px;
                    min-width: 120px;
                }
                
                QPushButton:hover {
                    background-color: #388e3c;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(46, 125, 50, 0.4);
                }
                
                QPushButton:pressed {
                    background-color: #1b5e20;
                    transform: translateY(0px);
                    box-shadow: 0 2px 4px rgba(46, 125, 50, 0.3);
                }
                
                QPushButton:disabled {
                    background-color: #404040;
                    color: #888888;
                    transform: none;
                    box-shadow: none;
                }
                
                /* Enhanced Input Styling - LARGER */
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #2d2d2d;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #ffffff;
                    font-size: 16px;
                    selection-background-color: #2e7d32;
                    min-height: 28px;
                }
                
                QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                    border: 2px solid #2e7d32;
                    background-color: #333333;
                    box-shadow: 0 0 12px rgba(46, 125, 50, 0.4);
                }
                
                /* Enhanced ComboBox - LARGER */
                QComboBox {
                    background-color: #2d2d2d;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #ffffff;
                    font-size: 16px;
                    min-width: 250px;
                    min-height: 28px;
                }
                
                QComboBox:focus {
                    border: 2px solid #2e7d32;
                    background-color: #333333;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 40px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border-left: 6px solid transparent;
                    border-right: 6px solid transparent;
                    border-top: 6px solid #ffffff;
                    margin-right: 8px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    border: 2px solid #404040;
                    color: #ffffff;
                    selection-background-color: #2e7d32;
                    selection-color: white;
                    font-size: 15px;
                    padding: 8px;
                }
                
                /* Enhanced Table Styling - LARGER */
                QTableWidget {
                    background-color: #2d2d2d;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    gridline-color: #404040;
                    color: #ffffff;
                    selection-background-color: #2e7d32;
                    alternate-background-color: #333333;
                    font-size: 15px;
                }
                
                QTableWidget::item {
                    padding: 16px;
                    border-bottom: 1px solid #404040;
                    min-height: 24px;
                }
                
                QTableWidget::item:selected {
                    background-color: #2e7d32;
                    color: white;
                }
                
                QHeaderView::section {
                    background-color: #404040;
                    color: #ffffff;
                    padding: 16px;
                    border: none;
                    font-weight: 600;
                    font-size: 16px;
                    border-bottom: 3px solid #2e7d32;
                }
                
                /* Enhanced Status Cards - LARGER */
                #status_card {
                    background-color: #1e1e1e;
                    border: 2px solid #404040;
                    border-radius: 16px;
                    padding: 24px;
                }
                
                /* Enhanced Labels - LARGER */
                QLabel {
                    color: #ffffff;
                    font-size: 15px;
                }
                
                QLabel#title {
                    font-size: 28px;
                    font-weight: 700;
                    color: #2e7d32;
                    padding: 8px 0px;
                }
                
                QLabel#section_title {
                    font-size: 20px;
                    font-weight: 600;
                    color: #2e7d32;
                    padding: 12px 0px;
                }
                
                QLabel#subtitle {
                    font-size: 17px;
                    font-weight: 500;
                    color: #b0b0b0;
                    padding: 6px 0px;
                }
                
                QLabel#info {
                    font-size: 14px;
                    color: #888888;
                    padding: 4px 0px;
                }
                
                /* Terminal Styling - LARGER */
                #terminal {
                    background-color: #0d0d0d;
                    color: #00ff00;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 15px;
                    padding: 20px;
                }
                
                /* Progress Bar - LARGER */
                QProgressBar {
                    border: 2px solid #404040;
                    border-radius: 8px;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    background-color: #2d2d2d;
                    height: 24px;
                    font-size: 15px;
                }
                
                QProgressBar::chunk {
                    background-color: #2e7d32;
                    border-radius: 6px;
                }
                
                /* Tab Widget - LARGER */
                QTabWidget::pane {
                    border: 2px solid #404040;
                    background-color: #1e1e1e;
                    border-radius: 12px;
                }
                
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 12px 24px;
                    margin-right: 2px;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    font-weight: 600;
                    font-size: 15px;
                }
                
                QTabBar::tab:selected {
                    background-color: #2e7d32;
                    color: white;
                }
                
                QTabBar::tab:hover {
                    background-color: #404040;
                }
                
                /* Frame Styling - LARGER */
                QFrame {
                    background-color: #1e1e1e;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    padding: 24px;
                }
                
                /* SpinBox - LARGER */
                QSpinBox {
                    background-color: #2d2d2d;
                    border: 2px solid #404040;
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #ffffff;
                    font-size: 16px;
                    min-width: 120px;
                    min-height: 28px;
                }
                
                QSpinBox:focus {
                    border: 2px solid #2e7d32;
                    background-color: #333333;
                }
                
                /* CheckBox - LARGER */
                QCheckBox {
                    color: #ffffff;
                    font-size: 16px;
                    spacing: 16px;
                    padding: 8px 0px;
                }
                
                QCheckBox::indicator {
                    width: 24px;
                    height: 24px;
                    border: 2px solid #404040;
                    border-radius: 6px;
                    background-color: #2d2d2d;
                }
                
                QCheckBox::indicator:hover {
                    border: 2px solid #2e7d32;
                    background-color: #333333;
                }
                
                QCheckBox::indicator:checked {
                    background-color: #2e7d32;
                    border: 2px solid #2e7d32;
                    image: none;
                }
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply qt-material theme: {e}")
            # Fallback to basic dark theme
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: white; }
                QWidget { background-color: #1e1e1e; color: white; }
            """)
    
    def setup_ui(self):
        """Setup main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.setObjectName("sidebar")
        main_layout.addWidget(self.sidebar)
        
        # Create stacked content area
        self.stacked_content = StackedContent(self)
        self.stacked_content.setObjectName("content_area")
        main_layout.addWidget(self.stacked_content)
        
        # Set layout proportions (20% sidebar, 80% content)
        main_layout.setStretchFactor(self.sidebar, 1)
        main_layout.setStretchFactor(self.stacked_content, 4)
    
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
