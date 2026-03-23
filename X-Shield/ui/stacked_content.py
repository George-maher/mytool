"""
Stacked Content Widget for X-Shield MVC Architecture
Dynamic area that switches pages based on sidebar selection
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

# Import all page components
from ui.dashboard_page import DashboardPage
from ui.target_manager_page import TargetManagerPage
from ui.network_scanner_page import NetworkScannerPage
from ui.web_scanner_page import WebScannerPage
from ui.osint_page import OSINTPage
from ui.reports_page_new import ReportsPage
from ui.settings_page_new import SettingsPage


class StackedContent(QWidget):
    """Dynamic content area with QStackedWidget for page switching"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pages = {}
        
        self.setup_ui()
        self.setup_pages()
    
    def setup_ui(self):
        """Setup main UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header bar
        header = self.create_header()
        layout.addWidget(header)
        
        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        layout.addWidget(self.stacked_widget)
    
    def create_header(self):
        """Create header bar with page title"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-bottom: 2px solid #2d2d2d;
            }
            QLabel {
                border: none;
                background: transparent;
                padding: 0px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Roboto", 20, QFont.Bold))
        self.page_title.setStyleSheet("color: #2e7d32;")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("🟢 System Ready")
        self.status_indicator.setFont(QFont("Roboto", 12))
        self.status_indicator.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(self.status_indicator)
        
        return header_frame
    
    def setup_pages(self):
        """Setup all pages and add to stacked widget"""
        # Get parent application for dependencies
        app = self.parent()
        
        # Dashboard Page
        dashboard_page = DashboardPage(app)
        self.stacked_widget.addWidget(dashboard_page)
        self.pages["dashboard"] = dashboard_page
        
        # Target Manager Page
        target_manager_page = TargetManagerPage(app)
        self.stacked_widget.addWidget(target_manager_page)
        self.pages["target_manager"] = target_manager_page
        
        # Network Scanner Page
        network_scanner_page = NetworkScannerPage(app)
        self.stacked_widget.addWidget(network_scanner_page)
        self.pages["network_scanner"] = network_scanner_page
        
        # Web Scanner Page
        web_scanner_page = WebScannerPage(app)
        self.stacked_widget.addWidget(web_scanner_page)
        self.pages["web_scanner"] = web_scanner_page
        
        # OSINT Page
        osint_page = OSINTPage(app)
        self.stacked_widget.addWidget(osint_page)
        self.pages["osint"] = osint_page
        
        # Reports Page
        reports_page = ReportsPage(app)
        self.stacked_widget.addWidget(reports_page)
        self.pages["reports"] = reports_page
        
        # Settings Page
        settings_page = SettingsPage(app)
        self.stacked_widget.addWidget(settings_page)
        self.pages["settings"] = settings_page
        
        # Set default page
        self.stacked_widget.setCurrentWidget(dashboard_page)
    
    @Slot(str)
    def switch_page(self, page_name):
        """Switch to specified page"""
        if page_name in self.pages:
            page = self.pages[page_name]
            self.stacked_widget.setCurrentWidget(page)
            
            # Update header title
            page_titles = {
                "dashboard": "Dashboard",
                "target_manager": "Target Manager",
                "network_scanner": "Network Scanner",
                "web_scanner": "Web Scanner",
                "osint": "OSINT",
                "reports": "Reports",
                "settings": "Settings"
            }
            
            title = page_titles.get(page_name, "Unknown")
            self.page_title.setText(title)
            
            # Call page's on_enter method if it exists
            if hasattr(page, 'on_enter'):
                page.on_enter()
            
            print(f"Switched to page: {page_name}")
        else:
            print(f"Page not found: {page_name}")
    
    def get_page(self, page_name):
        """Get page instance by name"""
        return self.pages.get(page_name)
    
    def get_current_page(self):
        """Get current active page"""
        return self.stacked_widget.currentWidget()
    
    def get_current_page_name(self):
        """Get current page name"""
        current_widget = self.stacked_widget.currentWidget()
        for name, page in self.pages.items():
            if page == current_widget:
                return name
        return "unknown"
