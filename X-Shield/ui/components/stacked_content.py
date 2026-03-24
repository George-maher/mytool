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
        """Setup main UI layout with improved spacing"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # Add proper margins
        layout.setSpacing(12)  # Space between header and content
        
        # Header bar with better styling
        header = self.create_header()
        layout.addWidget(header)
        
        # Stacked widget for pages with proper spacing
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {Colors.BACKGROUND}; 
                border: none;
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.stacked_widget)
    
    def create_header(self):
        """Create header bar with improved styling"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)  # Reduced from 80
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {Colors.BACKGROUND}, stop:0.5 {Colors.SURFACE}, stop:1 {Colors.BACKGROUND});
                border-bottom: 2px solid {Colors.PRIMARY};
                border-radius: 8px 8px 0 0;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)  # Better padding
        header_layout.setSpacing(16)
        
        # Page title
        self.page_title = QLabel("DASHBOARD")
        self.page_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.PRIMARY};
                font-weight: 800;
                font-size: 18px;
                letter-spacing: 2px;
                text-transform: uppercase;
                font-family: {Typography.FAMILY_SANS};
                text-shadow: 0 0 10px rgba(255, 0, 255, 0.3);
            }}
        """)
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # Status indicator
        status_label = QLabel("● ONLINE")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.SUCCESS};
                font-weight: 700;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-family: {Typography.FAMILY_SANS};
                text-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
            }}
        """)
        header_layout.addWidget(status_label)
        
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
