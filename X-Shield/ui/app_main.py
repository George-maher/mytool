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
        self.setGeometry(100, 100, 1000, 1000)
        self.setMinimumSize(1000, 800)
        
        # Apply qt-material dark_teal theme
        self.apply_theme()
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Setup update timer
        self.setup_timers()
        
        self.logger.info("X-Shield Professional Application initialized")
    
    def apply_theme(self):
        """Apply SOC Command Center Midnight Neon theme"""
        # Midnight Neon Palette: Indigo: #0f172a, Cyan: #22d3ee, Amber: #fbbf24, Rose: #f43f5e
        try:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #020617;
                }

                QWidget {
                    background-color: transparent;
                    color: #94a3b8;
                    font-family: 'DejaVu Sans';
                }
                
                #sidebar {
                    background-color: #0f172a;
                    border-right: 1px solid #1e293b;
                }
                
                #content_area {
                    background-color: #020617;
                }
                
                /* Cyber Cyan Buttons */
                QPushButton {
                    background-color: #0891b2;
                    color: #f8fafc;
                    border: 1px solid #22d3ee;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 38px;
                    text-transform: uppercase;
                }
                
                QPushButton:hover {
                    background-color: #0e7490;
                    border: 1px solid #67e8f9;
                    color: #ffffff;
                }
                
                QPushButton:pressed {
                    background-color: #155e75;
                }
                
                /* Enhanced Input Styling */
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 4px;
                    padding: 10px 14px;
                    color: #22d3ee;
                    font-family: 'DejaVu Sans Mono';
                    font-size: 14px;
                    selection-background-color: #155e75;
                }
                
                QLineEdit:focus {
                    border: 1px solid #22d3ee;
                    background-color: #020617;
                }
                
                /* ComboBox */
                QComboBox {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 4px;
                    padding: 8px 12px;
                    color: #f8fafc;
                }
                
                /* Frame Styling - Command Center Cards */
                .QFrame {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 2px;
                    padding: 15px;
                }
                
                /* Table Styling */
                QTableWidget {
                    background-color: #020617;
                    border: 1px solid #1e293b;
                    gridline-color: #1e293b;
                    color: #94a3b8;
                }
                
                QHeaderView::section {
                    background-color: #0f172a;
                    color: #22d3ee;
                    padding: 10px;
                    border: 1px solid #1e293b;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                
                /* Labels */
                QLabel {
                    color: #94a3b8;
                }
                
                QLabel#title {
                    font-size: 24px;
                    font-weight: 800;
                    color: #f8fafc;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                }
                
                /* Progress Bar */
                QProgressBar {
                    border: 1px solid #1e293b;
                    border-radius: 2px;
                    text-align: center;
                    background-color: #020617;
                    height: 10px;
                    color: transparent;
                }
                
                QProgressBar::chunk {
                    background-color: #22d3ee;
                }
                
                /* Tab Widget */
                QTabWidget::pane {
                    border: 1px solid #1e293b;
                    background-color: #0f172a;
                }
                
                QTabBar::tab {
                    background-color: #020617;
                    color: #64748b;
                    padding: 10px 20px;
                    border: 1px solid #1e293b;
                    border-bottom: none;
                    margin-right: 2px;
                }
                
                QTabBar::tab:selected {
                    background-color: #0f172a;
                    color: #22d3ee;
                    border-bottom: 2px solid #22d3ee;
                }
            """)
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
            self.setStyleSheet("QMainWindow { background-color: #121212; color: white; }")
    
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
