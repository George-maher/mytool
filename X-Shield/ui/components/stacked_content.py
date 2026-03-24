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
from ui.components.styles import Colors, Spacing, Typography

# Import all page components
from ui.pages.dashboard_page import DashboardPage
from ui.pages.target_manager_page import TargetManagerPage
from ui.pages.network_scanner_page import NetworkScannerPage
from ui.pages.web_scanner_page import WebScannerPage
from ui.pages.osint_page import OSINTPage
from ui.pages.reports_page_new import ReportsPage
from ui.pages.settings_page_new import SettingsPage


class StackedContent(QWidget):
    """Dynamic content area with QStackedWidget for page switching"""
    
    def __init__(self, target_manager, module_manager, logger, parent=None):
        super().__init__(parent)
        self.target_manager = target_manager
        self.module_manager = module_manager
        self.logger = logger
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
        self.stacked_widget.setStyleSheet(f"background-color: {Colors.BACKGROUND}; border: none;")
        layout.addWidget(self.stacked_widget)
    
    def create_header(self):
        """Create header bar with page title"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BACKGROUND};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(Spacing.XXL, 0, Spacing.XXL, 0)
        
        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("title")
        self.page_title.setStyleSheet(f"color: {Colors.PRIMARY}; font-size: {Typography.H1_SIZE}; font-weight: 800; letter-spacing: -0.5px;")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("● System Operational")
        self.status_indicator.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 13px; font-weight: 500;")
        header_layout.addWidget(self.status_indicator)
        
        return header_frame
    
    def setup_pages(self):
        """Setup all pages and add to stacked widget"""
        # Common dependencies
        deps = {
            'target_manager': self.target_manager,
            'module_manager': self.module_manager,
            'logger': self.logger,
            'parent': self.parent()
        }
        
        # Dashboard Page
        dashboard_page = DashboardPage(**deps)
        self.stacked_widget.addWidget(dashboard_page)
        self.pages["dashboard"] = dashboard_page
        
        # Target Manager Page
        target_manager_page = TargetManagerPage(**deps)
        self.stacked_widget.addWidget(target_manager_page)
        self.pages["target_manager"] = target_manager_page
        
        # Network Scanner Page
        network_scanner_page = NetworkScannerPage(**deps)
        self.stacked_widget.addWidget(network_scanner_page)
        self.pages["network_scanner"] = network_scanner_page
        
        # Web Scanner Page
        web_scanner_page = WebScannerPage(**deps)
        self.stacked_widget.addWidget(web_scanner_page)
        self.pages["web_scanner"] = web_scanner_page
        
        # OSINT Page
        osint_page = OSINTPage(**deps)
        self.stacked_widget.addWidget(osint_page)
        self.pages["osint"] = osint_page
        
        # Reports Page
        reports_page = ReportsPage(**deps)
        self.stacked_widget.addWidget(reports_page)
        self.pages["reports"] = reports_page
        
        # Settings Page
        settings_page = SettingsPage(**deps)
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
