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
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        
        # Icon label
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(40, 40)
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(label_text)
        text_label.setFont(QFont("Roboto", 16, QFont.Medium))
        layout.addWidget(text_label)
        
        layout.addStretch()
    
    def setup_style(self):
        """Setup button styling"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: #b0b0b0;
                text-align: left;
                padding: 0px;
                margin: 6px 16px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #ffffff;
                transform: translateX(4px);
            }
            QPushButton:checked {
                background-color: rgba(46, 125, 50, 0.4);
                color: #2e7d32;
                border-left: 6px solid #2e7d32;
                font-weight: 600;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
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
        header_frame.setFixedHeight(100)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #0d3b3b;
                border-bottom: 2px solid #1a4a4a;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        # Logo
        logo_label = QLabel("🛡️")
        logo_label.setFont(QFont("Segoe UI Emoji", 36))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(60, 60)
        logo_label.setStyleSheet("""
            QLabel {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.6,
                    fx:0.5, fy:0.5, stop:0 #2e7d32, stop:1 transparent);
                border-radius: 30px;
            }
        """)
        header_layout.addWidget(logo_label)
        
        # App name
        app_label = QLabel("X-Shield")
        app_label.setFont(QFont("Roboto", 22, QFont.Bold))
        app_label.setStyleSheet("color: #2e7d32;")
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
                background-color: #0d3b3b;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #0d3b3b;
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
        footer_frame.setFixedHeight(100)
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #0d3b3b;
                border-top: 2px solid #1a4a4a;
            }
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(24, 20, 24, 20)
        
        # User avatar
        avatar_label = QLabel("👤")
        avatar_label.setFont(QFont("Segoe UI Emoji", 32))
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setFixedSize(50, 50)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #1a4a4a;
                border-radius: 25px;
                border: 2px solid #2e7d32;
            }
        """)
        footer_layout.addWidget(avatar_label)
        
        # User info
        user_info_layout = QVBoxLayout()
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(4)
        
        username_label = QLabel("Administrator")
        username_label.setFont(QFont("Roboto", 14, QFont.Bold))
        username_label.setStyleSheet("color: #ffffff;")
        user_info_layout.addWidget(username_label)
        
        status_label = QLabel("🟢 Online")
        status_label.setFont(QFont("Roboto", 12))
        status_label.setStyleSheet("color: #2e7d32;")
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
