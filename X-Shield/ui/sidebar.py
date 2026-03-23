"""
Professional Sidebar Component for X-Shield MVC Architecture
Sleek left-hand sidebar with icons for navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QButtonGroup, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon


class SidebarButton(QPushButton):
    """Custom sidebar button with icon and professional styling"""
    
    def __init__(self, icon_text, label_text, page_name):
        super().__init__()
        self.page_name = page_name
        self.is_active = False
        
        self.setup_ui(icon_text, label_text)
        self.setup_style()
    
    def setup_ui(self, icon_text, label_text):
        """Setup button UI"""
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(15)
        
        # Icon label
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(30, 30)
        icon_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(label_text)
        text_label.setFont(QFont("Roboto", 14, QFont.Medium))
        text_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(text_label)
        
        layout.addStretch()
    
    def setup_style(self):
        """Setup button styling with Midnight Neon aesthetic"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #64748b;
                text-align: left;
                padding: 0px;
                margin: 2px 10px;
                min-height: 48px;
            }
            QPushButton:hover {
                background-color: rgba(34, 211, 238, 0.05);
                color: #22d3ee;
            }
            QPushButton:checked {
                background-color: rgba(34, 211, 238, 0.1);
                color: #22d3ee;
                border-left: 3px solid #22d3ee;
            }
        """)


class Sidebar(QWidget):
    """Professional sidebar with Material Design icons and navigation"""
    
    # Signal emitted when navigation is requested
    navigation_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        
        self.setup_ui()
        self.setup_connections()
        
        # Set default active page
        self.set_active_page("dashboard")
    
    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.setup_header(layout)
        
        # Navigation
        self.setup_navigation(layout)
        
        # Footer
        self.setup_footer(layout)
    
    def setup_header(self, parent_layout):
        """Setup sidebar header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-bottom: 1px solid #1e293b;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)
        
        # Logo
        logo_label = QLabel("🛡️")
        logo_label.setFont(QFont("Segoe UI Emoji", 24))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(40, 40)
        logo_label.setStyleSheet("""
            QLabel {
                background-color: rgba(34, 211, 238, 0.1);
                border: 1px solid #22d3ee;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(logo_label)
        
        # App name
        app_label = QLabel("X-SHIELD")
        app_label.setStyleSheet("color: #f8fafc; font-weight: 900; font-size: 18px; letter-spacing: 3px;")
        header_layout.addWidget(app_label)
        
        parent_layout.addWidget(header_frame)
    
    def setup_navigation(self, parent_layout):
        """Setup navigation buttons"""
        # Scroll area for navigation
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f172a;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #0f172a;
            }
        """)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(2)
        
        # Navigation title
        nav_title = QLabel("NAVIGATION")
        nav_title.setFont(QFont("Roboto", 11, QFont.Bold))
        nav_title.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 8px 20px;
                margin-top: 10px;
            }
        """)
        nav_layout.addWidget(nav_title)
        
        # Create navigation buttons
        self.nav_buttons = []
        
        # Dashboard
        dashboard_btn = SidebarButton("📊", "Dashboard", "dashboard")
        self.nav_buttons.append(dashboard_btn)
        nav_layout.addWidget(dashboard_btn)
        
        # Target Manager
        target_btn = SidebarButton("🎯", "Target Manager", "target_manager")
        self.nav_buttons.append(target_btn)
        nav_layout.addWidget(target_btn)
        
        # Network Scanner
        network_btn = SidebarButton("🌐", "Network Scanner", "network_scanner")
        self.nav_buttons.append(network_btn)
        nav_layout.addWidget(network_btn)
        
        # Web Scanner
        web_btn = SidebarButton("🌍", "Web Scanner", "web_scanner")
        self.nav_buttons.append(web_btn)
        nav_layout.addWidget(web_btn)
        
        # OSINT
        osint_btn = SidebarButton("🔍", "OSINT", "osint")
        self.nav_buttons.append(osint_btn)
        nav_layout.addWidget(osint_btn)
        
        # Reports
        reports_btn = SidebarButton("📋", "Reports", "reports")
        self.nav_buttons.append(reports_btn)
        nav_layout.addWidget(reports_btn)
        
        # Settings
        settings_btn = SidebarButton("⚙️", "Settings", "settings")
        self.nav_buttons.append(settings_btn)
        nav_layout.addWidget(settings_btn)
        
        # Add stretch
        nav_layout.addStretch()
        
        scroll_area.setWidget(nav_widget)
        parent_layout.addWidget(scroll_area)
    
    def setup_footer(self, parent_layout):
        """Setup user info footer"""
        footer_frame = QFrame()
        footer_frame.setFixedHeight(80)
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-top: 1px solid #1e293b;
            }
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        footer_layout.setSpacing(12)
        
        # User avatar
        avatar_label = QLabel("👤")
        avatar_label.setFont(QFont("Segoe UI Emoji", 20))
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setFixedSize(36, 36)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                border-radius: 4px;
                border: 1px solid #334155;
            }
        """)
        footer_layout.addWidget(avatar_label)
        
        # User info
        user_info_layout = QVBoxLayout()
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        
        username_label = QLabel("ADMIN")
        username_label.setStyleSheet("color: #f8fafc; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        user_info_layout.addWidget(username_label)
        
        status_label = QLabel("SYSTEM ONLINE")
        status_label.setStyleSheet("color: #10b981; font-size: 10px; font-weight: bold;")
        user_info_layout.addWidget(status_label)
        
        footer_layout.addLayout(user_info_layout)
        footer_layout.addStretch()
        
        parent_layout.addWidget(footer_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect navigation buttons
        button_group = QButtonGroup(self)
        
        for button in self.nav_buttons:
            button_group.addButton(button)
            button.clicked.connect(lambda checked, btn=button: self.on_navigation_clicked(btn))
    
    @Slot()
    def on_navigation_clicked(self, button):
        """Handle navigation button click"""
        page_name = button.page_name
        self.set_active_page(page_name)
        self.navigation_requested.emit(page_name)
    
    def set_active_page(self, page_name):
        """Set active page"""
        for button in self.nav_buttons:
            button.setChecked(button.page_name == page_name)
            button.is_active = (button.page_name == page_name)
    
    def get_current_page(self):
        """Get current active page name"""
        for button in self.nav_buttons:
            if button.is_active:
                return button.page_name
        return "dashboard"
