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
from ui.components.styles import Colors, Spacing, Typography


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
        layout.setContentsMargins(Spacing.LG, Spacing.SM, Spacing.LG, Spacing.SM)
        layout.setSpacing(Spacing.MD)
        
        # Icon label
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet("border: none; background: transparent; color: inherit;")
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(label_text)
        text_label.setFont(QFont(Typography.FAMILY_SANS, 10, QFont.Medium))
        text_label.setStyleSheet("border: none; background: transparent; color: inherit;")
        layout.addWidget(text_label)
        
        layout.addStretch()
    
    def setup_style(self):
        """Setup button styling with Modern Minimal aesthetic"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: {Colors.TEXT_SECONDARY};
                text-align: left;
                padding: 0px;
                margin: 4px {Spacing.MD}px;
                min-height: 44px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {Colors.PRIMARY_MUTED};
                color: {Colors.PRIMARY};
                border-left: 3px solid {Colors.PRIMARY};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                font-weight: 600;
            }}
        """)


class Sidebar(QFrame):
    """Professional sidebar with Material Design icons and navigation"""
    
    # Signal emitted when navigation is requested
    navigation_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        
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
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)
        header_layout.setSpacing(Spacing.MD)
        
        # Logo
        logo_label = QLabel("🛡️")
        logo_label.setFont(QFont("Segoe UI Emoji", 18))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(36, 36)
        logo_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SURFACE_LIGHT};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
            }}
        """)
        header_layout.addWidget(logo_label)
        
        # App name
        app_label = QLabel("X-SHIELD")
        app_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 800; font-size: 18px; letter-spacing: 1px;")
        header_layout.addWidget(app_label)
        
        parent_layout.addWidget(header_frame)
    
    def setup_navigation(self, parent_layout):
        """Setup navigation buttons"""
        # Scroll area for navigation
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, Spacing.XL, 0, Spacing.XL)
        nav_layout.setSpacing(Spacing.XS)
        
        # Navigation title
        nav_title = QLabel("Main Menu")
        nav_title.setFont(QFont(Typography.FAMILY_SANS, 9, QFont.Bold))
        nav_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_MUTED};
                padding: 8px {Spacing.XL}px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
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
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-top: 1px solid {Colors.BORDER};
            }}
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)
        footer_layout.setSpacing(Spacing.MD)
        
        # User avatar
        avatar_label = QLabel("👤")
        avatar_label.setFont(QFont("Segoe UI Emoji", 16))
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setFixedSize(32, 32)
        avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SURFACE_LIGHT};
                border-radius: 16px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        footer_layout.addWidget(avatar_label)
        
        # User info
        user_info_layout = QVBoxLayout()
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(0)
        
        username_label = QLabel("Administrator")
        username_label.setStyleSheet(f"border: none; background: transparent; color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: 13px;")
        user_info_layout.addWidget(username_label)
        
        status_label = QLabel("System Online")
        status_label.setStyleSheet(f"border: none; background: transparent; color: {Colors.SUCCESS}; font-size: 11px; font-weight: 500;")
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
