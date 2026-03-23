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
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(900, 800)
        
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
                
                /* Modern Design System - Clean & Consistent */
                QPushButton {
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    color: #f8fafc;
                    border: 2px solid #475569;
                    padding: 16px 32px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 14px;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    min-height: 48px;
                    min-width: 140px;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                QPushButton:hover {
                    background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
                    border-color: #22d3ee;
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(34, 211, 238, 0.15);
                }
                
                QPushButton:pressed {
                    transform: translateY(0px);
                    box-shadow: 0 4px 12px rgba(34, 211, 238, 0.2);
                }
                
                QPushButton:disabled {
                    background: #1e293b;
                    color: #64748b;
                    border-color: #334155;
                    transform: none;
                    box-shadow: none;
                }
                
                /* Large Primary Buttons */
                QPushButton.large {
                    background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
                    color: #020617;
                    border: 2px solid #22d3ee;
                    padding: 20px 40px;
                    border-radius: 16px;
                    font-weight: 700;
                    font-size: 16px;
                    letter-spacing: 0.5px;
                    min-width: 240px;
                    min-height: 56px;
                    text-transform: uppercase;
                }
                
                QPushButton.large:hover {
                    background: linear-gradient(135deg, #67e8f9 0%, #22d3ee 100%);
                    border-color: #67e8f9;
                    box-shadow: 0 12px 35px rgba(34, 211, 238, 0.25);
                }
                
                /* Small Action Buttons */
                QPushButton.small {
                    background: transparent;
                    color: #22d3ee;
                    border: 2px solid #22d3ee;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-weight: 500;
                    font-size: 13px;
                    min-width: 120px;
                    min-height: 40px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                QPushButton.small:hover {
                    background: rgba(34, 211, 238, 0.1);
                    border-color: #67e8f9;
                    color: #67e8f9;
                    transform: translateY(-1px);
                    box-shadow: 0 6px 20px rgba(34, 211, 238, 0.1);
                }
                
                QPushButton:pressed {
                    background-color: #155e75;
                }
                
                /* Modern Input Design System */
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background: linear-gradient(135deg, #020617 0%, #1e293b 100%);
                    border: 2px solid #334155;
                    border-radius: 12px;
                    padding: 20px 24px;
                    color: #f8fafc;
                    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                    font-size: 15px;
                    selection-background-color: #22d3ee;
                    selection-color: #020617;
                    min-height: 24px;
                    transition: all 0.3s ease;
                }
                
                QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                    border: 2px solid #22d3ee;
                    background: #020617;
                    outline: none;
                    box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.1), inset 0 0 0 1px rgba(34, 211, 238, 0.1);
                }
                
                QLineEdit::placeholder {
                    color: #64748b;
                    font-style: italic;
                    opacity: 0.7;
                }
                
                /* Modern ComboBox Design */
                QComboBox {
                    background: linear-gradient(135deg, #020617 0%, #1e293b 100%);
                    border: 2px solid #334155;
                    border-radius: 12px;
                    padding: 16px 20px;
                    color: #f8fafc;
                    font-size: 15px;
                    font-family: 'Inter', -apple-system, sans-serif;
                    min-height: 24px;
                    min-width: 200px;
                    transition: all 0.3s ease;
                }
                
                QComboBox:focus {
                    border: 2px solid #22d3ee;
                    background: #020617;
                    box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.1);
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 32px;
                    background-color: transparent;
                    padding-right: 8px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border-left: 6px solid transparent;
                    border-right: 6px solid transparent;
                    border-top: 6px solid #22d3ee;
                    margin-right: 12px;
                }
                
                QComboBox QAbstractItemView {
                    background: #0f172a;
                    border: 2px solid #22d3ee;
                    border-radius: 8px;
                    color: #f8fafc;
                    selection-background-color: #22d3ee;
                    selection-color: #020617;
                    padding: 12px;
                    font-size: 14px;
                    font-family: 'Inter', -apple-system, sans-serif;
                }
                
                /* Modern Frame Design */
                .QFrame {
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    border: 2px solid #334155;
                    border-radius: 16px;
                    padding: 32px;
                    margin: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                
                QFrame[frameShape="0"] {
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    background: transparent;
                    box-shadow: none;
                }
                
                /* Modern Table Design */
                QTableWidget {
                    background: #020617;
                    border: 2px solid #334155;
                    border-radius: 12px;
                    gridline-color: #1e293b;
                    color: #f8fafc;
                    font-size: 14px;
                    font-family: 'Inter', -apple-system, sans-serif;
                    selection-background-color: rgba(34, 211, 238, 0.2);
                    outline: none;
                }
                
                QTableWidget::item {
                    padding: 20px 16px;
                    border-bottom: 1px solid #1e293b;
                    min-height: 24px;
                    transition: background-color 0.2s ease;
                }
                
                QTableWidget::item:selected {
                    background: linear-gradient(135deg, rgba(34, 211, 238, 0.3) 0%, rgba(8, 145, 178, 0.3) 100%);
                    color: #020617;
                    font-weight: 600;
                }
                
                QTableWidget::item:hover {
                    background: rgba(34, 211, 238, 0.1);
                }
                
                QHeaderView::section {
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    color: #22d3ee;
                    padding: 20px 16px;
                    border: none;
                    border-bottom: 3px solid #22d3ee;
                    font-weight: 700;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    font-family: 'Inter', -apple-system, sans-serif;
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
