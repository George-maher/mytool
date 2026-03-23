"""
Settings Page for X-Shield MVC Architecture
Configuration and settings management interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QFrame, QComboBox, QCheckBox, QSpinBox,
    QTabWidget, QScrollArea, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class SettingsPage(QWidget):
    """Settings page for configuration management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
    
    def setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Settings & Configuration")
        title_label.setFont(QFont("Roboto", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title_label)
        
        # Tab widget for different settings categories
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #2e7d32;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
        """)
        
        # General Settings Tab
        self.setup_general_tab()
        
        # Scanner Settings Tab
        self.setup_scanner_tab()
        
        # Network Settings Tab
        self.setup_network_tab()
        
        # Security Settings Tab
        self.setup_security_tab()
        
        layout.addWidget(self.settings_tabs)
        
        # Action buttons
        self.setup_action_buttons(layout)
        
        layout.addStretch()
    
    def setup_general_tab(self):
        """Setup general settings tab"""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.setContentsMargins(30, 30, 30, 30)
        general_layout.setSpacing(20)
        
        # Application settings
        app_frame = QFrame()
        app_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        app_layout = QVBoxLayout(app_frame)
        app_layout.setSpacing(16)
        
        section_title = QLabel("Application Settings")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        app_layout.addWidget(section_title)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(12)
        
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Roboto", 12))
        theme_label.setStyleSheet("color: #b0b0b0;")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Teal", "Dark Blue", "Dark Red", "Light"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 200px;
                min-height: 40px;
            }
            QComboBox:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                color: #ffffff;
                selection-background-color: #2e7d32;
                selection-color: white;
            }
        """)
        theme_layout.addWidget(self.theme_combo)
        
        theme_layout.addStretch()
        app_layout.addLayout(theme_layout)
        
        # Auto-save
        self.autosave_checkbox = QCheckBox("Auto-save scan results")
        self.autosave_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 4px;
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
        app_layout.addWidget(self.autosave_checkbox)
        
        # Log level
        log_layout = QHBoxLayout()
        log_layout.setSpacing(12)
        
        log_label = QLabel("Log Level:")
        log_label.setFont(QFont("Roboto", 12))
        log_label.setStyleSheet("color: #b0b0b0;")
        log_layout.addWidget(log_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 150px;
                min-height: 40px;
            }
            QComboBox:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                color: #ffffff;
                selection-background-color: #2e7d32;
                selection-color: white;
            }
        """)
        log_layout.addWidget(self.log_level_combo)
        
        log_layout.addStretch()
        app_layout.addLayout(log_layout)
        
        general_layout.addWidget(app_frame)
        general_layout.addStretch()
        
        self.settings_tabs.addTab(general_widget, "General")
    
    def setup_scanner_tab(self):
        """Setup scanner settings tab"""
        scanner_widget = QWidget()
        scanner_layout = QVBoxLayout(scanner_widget)
        scanner_layout.setContentsMargins(30, 30, 30, 30)
        scanner_layout.setSpacing(20)
        
        # Scanner configuration
        scanner_frame = QFrame()
        scanner_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        config_layout = QVBoxLayout(scanner_frame)
        config_layout.setSpacing(16)
        
        section_title = QLabel("Scanner Configuration")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        config_layout.addWidget(section_title)
        
        # Max concurrent scans
        concurrent_layout = QHBoxLayout()
        concurrent_layout.setSpacing(12)
        
        concurrent_label = QLabel("Max Concurrent Scans:")
        concurrent_label.setFont(QFont("Roboto", 12))
        concurrent_label.setStyleSheet("color: #b0b0b0;")
        concurrent_layout.addWidget(concurrent_label)
        
        self.concurrent_scans_spin = QSpinBox()
        self.concurrent_scans_spin.setRange(1, 10)
        self.concurrent_scans_spin.setValue(3)
        self.concurrent_scans_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 100px;
                min-height: 40px;
            }
            QSpinBox:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
            }
        """)
        concurrent_layout.addWidget(self.concurrent_scans_spin)
        
        concurrent_layout.addStretch()
        config_layout.addLayout(concurrent_layout)
        
        # Default timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.setSpacing(12)
        
        timeout_label = QLabel("Default Timeout (seconds):")
        timeout_label.setFont(QFont("Roboto", 12))
        timeout_label.setStyleSheet("color: #b0b0b0;")
        timeout_layout.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
            }
        """)
        timeout_layout.addWidget(self.timeout_spin)
        
        timeout_layout.addStretch()
        config_layout.addLayout(timeout_layout)
        
        # Enable verbose logging
        self.verbose_checkbox = QCheckBox("Enable verbose scanner output")
        self.verbose_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 4px;
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
        config_layout.addWidget(self.verbose_checkbox)
        
        scanner_layout.addWidget(scanner_frame)
        scanner_layout.addStretch()
        
        self.settings_tabs.addTab(scanner_widget, "Scanners")
    
    def setup_network_tab(self):
        """Setup network settings tab"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        network_layout.setContentsMargins(30, 30, 30, 30)
        network_layout.setSpacing(20)
        
        # Network configuration
        network_frame = QFrame()
        network_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        config_layout = QVBoxLayout(network_frame)
        config_layout.setSpacing(16)
        
        section_title = QLabel("Network Configuration")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        config_layout.addWidget(section_title)
        
        # Proxy settings
        proxy_layout = QHBoxLayout()
        proxy_layout.setSpacing(12)
        
        proxy_label = QLabel("HTTP Proxy:")
        proxy_label.setFont(QFont("Roboto", 12))
        proxy_label.setStyleSheet("color: #b0b0b0;")
        proxy_layout.addWidget(proxy_label)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://proxy:port")
        self.proxy_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 14px;
                selection-background-color: #2e7d32;
                min-width: 300px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
            }
        """)
        proxy_layout.addWidget(self.proxy_input)
        
        proxy_layout.addStretch()
        config_layout.addLayout(proxy_layout)
        
        # User agent
        user_agent_layout = QHBoxLayout()
        user_agent_layout.setSpacing(12)
        
        ua_label = QLabel("User Agent:")
        ua_label.setFont(QFont("Roboto", 12))
        ua_label.setStyleSheet("color: #b0b0b0;")
        user_agent_layout.addWidget(ua_label)
        
        self.user_agent_input = QLineEdit()
        self.user_agent_input.setPlaceholderText("X-Shield/2.0.0")
        self.user_agent_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 14px;
                selection-background-color: #2e7d32;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;

            }
        """)
        user_agent_layout.addWidget(self.user_agent_input)
        
        user_agent_layout.addStretch()
        config_layout.addLayout(user_agent_layout)
        
        # Enable proxy
        self.enable_proxy_checkbox = QCheckBox("Enable HTTP proxy")
        self.enable_proxy_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 4px;
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
        config_layout.addWidget(self.enable_proxy_checkbox)
        
        network_layout.addWidget(network_frame)
        network_layout.addStretch()
        
        self.settings_tabs.addTab(network_widget, "Network")
    
    def setup_security_tab(self):
        """Setup security settings tab"""
        security_widget = QWidget()
        security_layout = QVBoxLayout(security_widget)
        security_layout.setContentsMargins(30, 30, 30, 30)
        security_layout.setSpacing(20)
        
        # Security configuration
        security_frame = QFrame()
        security_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        config_layout = QVBoxLayout(security_frame)
        config_layout.setSpacing(16)
        
        section_title = QLabel("Security Settings")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        config_layout.addWidget(section_title)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.setSpacing(12)
        
        api_key_label = QLabel("API Key:")
        api_key_label.setFont(QFont("Roboto", 12))
        api_key_label.setStyleSheet("color: #b0b0b0;")
        api_key_layout.addWidget(api_key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 14px;
                selection-background-color: #2e7d32;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;

            }
        """)
        api_key_layout.addWidget(self.api_key_input)
        
        api_key_layout.addStretch()
        config_layout.addLayout(api_key_layout)
        
        # Security checkboxes
        self.encryption_checkbox = QCheckBox("Enable data encryption")
        self.encryption_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 4px;
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
        config_layout.addWidget(self.encryption_checkbox)
        
        self.secure_storage_checkbox = QCheckBox("Secure storage for sensitive data")
        self.secure_storage_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 4px;
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
        config_layout.addWidget(self.secure_storage_checkbox)
        
        security_layout.addWidget(security_frame)
        security_layout.addStretch()
        
        self.settings_tabs.addTab(security_widget, "Security")
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 150px;
                min-height: 48px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
        """)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #F57C00;

            }
            QPushButton:pressed {
                background-color: #E65100;

            }
        """)
        buttons_layout.addWidget(self.reset_btn)
        
        self.export_btn = QPushButton("📤 Export Settings")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;

            }
            QPushButton:pressed {
                background-color: #0D47A1;

            }
        """)
        buttons_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("📥 Import Settings")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;

            }
            QPushButton:pressed {
                background-color: #4A148C;

            }
        """)
        buttons_layout.addWidget(self.import_btn)
        
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.export_btn.clicked.connect(self.export_settings)
        self.import_btn.clicked.connect(self.import_settings)
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Collect all settings
            settings = {
                'theme': self.theme_combo.currentText(),
                'autosave': self.autosave_checkbox.isChecked(),
                'log_level': self.log_level_combo.currentText(),
                'max_concurrent_scans': self.concurrent_scans_spin.value(),
                'default_timeout': self.timeout_spin.value(),
                'verbose_output': self.verbose_checkbox.isChecked(),
                'http_proxy': self.proxy_input.text(),
                'user_agent': self.user_agent_input.text(),
                'enable_proxy': self.enable_proxy_checkbox.isChecked(),
                'api_key': self.api_key_input.text(),
                'encryption': self.encryption_checkbox.isChecked(),
                'secure_storage': self.secure_storage_checkbox.isChecked()
            }
            
            # Mock save operation
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
            if self.logger:
                self.logger.info("Settings saved successfully")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.theme_combo.setCurrentIndex(0)
            self.autosave_checkbox.setChecked(True)
            self.log_level_combo.setCurrentText("INFO")
            self.concurrent_scans_spin.setValue(3)
            self.timeout_spin.setValue(60)
            self.verbose_checkbox.setChecked(False)
            self.proxy_input.clear()
            self.user_agent_input.setText("X-Shield/2.0.0")
            self.enable_proxy_checkbox.setChecked(False)
            self.api_key_input.clear()
            self.encryption_checkbox.setChecked(True)
            self.secure_storage_checkbox.setChecked(True)
            
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
    
    def export_settings(self):
        """Export settings to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "xshield_settings.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                settings = {
                    'theme': self.theme_combo.currentText(),
                    'autosave': self.autosave_checkbox.isChecked(),
                    'log_level': self.log_level_combo.currentText(),
                    'max_concurrent_scans': self.concurrent_scans_spin.value(),
                    'default_timeout': self.timeout_spin.value(),
                    'verbose_output': self.verbose_checkbox.isChecked(),
                    'http_proxy': self.proxy_input.text(),
                    'user_agent': self.user_agent_input.text(),
                    'enable_proxy': self.enable_proxy_checkbox.isChecked(),
                    'api_key': self.api_key_input.text(),
                    'encryption': self.encryption_checkbox.isChecked(),
                    'secure_storage': self.secure_storage_checkbox.isChecked()
                }
                
                import json
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Settings exported to {file_path}")
                
                if self.logger:
                    self.logger.info(f"Settings exported to {file_path}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export settings: {str(e)}")
    
    def import_settings(self):
        """Import settings from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                # Apply imported settings
                self.theme_combo.setCurrentText(settings.get('theme', 'Dark Teal'))
                self.autosave_checkbox.setChecked(settings.get('autosave', True))
                self.log_level_combo.setCurrentText(settings.get('log_level', 'INFO'))
                self.concurrent_scans_spin.setValue(settings.get('max_concurrent_scans', 3))
                self.timeout_spin.setValue(settings.get('default_timeout', 60))
                self.verbose_checkbox.setChecked(settings.get('verbose_output', False))
                self.proxy_input.setText(settings.get('http_proxy', ''))
                self.user_agent_input.setText(settings.get('user_agent', 'X-Shield/2.0.0'))
                self.enable_proxy_checkbox.setChecked(settings.get('enable_proxy', False))
                self.api_key_input.setText(settings.get('api_key', ''))
                self.encryption_checkbox.setChecked(settings.get('encryption', True))
                self.secure_storage_checkbox.setChecked(settings.get('secure_storage', True))
                
                QMessageBox.information(self, "Success", "Settings imported successfully!")
                
                if self.logger:
                    self.logger.info(f"Settings imported from {file_path}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import settings: {str(e)}")
    
    def load_settings(self):
        """Load settings (mock implementation)"""
        # Load default settings for demonstration
        self.theme_combo.setCurrentText("Dark Teal")
        self.autosave_checkbox.setChecked(True)
        self.log_level_combo.setCurrentText("INFO")
        self.concurrent_scans_spin.setValue(3)
        self.timeout_spin.setValue(60)
        self.verbose_checkbox.setChecked(False)
        self.user_agent_input.setText("X-Shield/2.0.0")
        self.encryption_checkbox.setChecked(True)
        self.secure_storage_checkbox.setChecked(True)
    
    def on_enter(self):
        """Called when page is entered"""
        if self.logger:
            self.logger.info("Settings page entered")
