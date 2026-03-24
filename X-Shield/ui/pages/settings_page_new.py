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
from ui.components.styles import Colors, Spacing, Typography


class SettingsPage(QWidget):
    """Settings page for configuration management"""
    
    def __init__(self, target_manager, module_manager, logger, parent=None):
        super().__init__(parent)
        self.target_manager = target_manager
        self.module_manager = module_manager
        self.logger = logger
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
    
    def setup_ui(self):
        """Setup settings UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Tab widget for different settings categories
        self.settings_tabs = QTabWidget()
        
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
        general_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        general_layout.setSpacing(Spacing.XL)
        
        # Application settings
        app_layout = QVBoxLayout()
        app_layout.setSpacing(Spacing.LG)
        
        section_title = QLabel("Application Settings")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        app_layout.addWidget(section_title)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(Spacing.MD)
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Modern Minimal (Slate)", "Cyber Dark", "High Contrast"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        app_layout.addLayout(theme_layout)
        
        # Auto-save
        self.autosave_checkbox = QCheckBox("Auto-save scan results")
        app_layout.addWidget(self.autosave_checkbox)
        
        # Log level
        log_layout = QHBoxLayout()
        log_layout.setSpacing(Spacing.MD)
        log_label = QLabel("Log Level")
        log_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        log_layout.addWidget(log_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addWidget(self.log_level_combo)
        log_layout.addStretch()
        app_layout.addLayout(log_layout)
        
        general_layout.addLayout(app_layout)
        general_layout.addStretch()
        
        self.settings_tabs.addTab(general_widget, "General")
    
    def setup_scanner_tab(self):
        """Setup scanner settings tab"""
        scanner_widget = QWidget()
        scanner_layout = QVBoxLayout(scanner_widget)
        scanner_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        scanner_layout.setSpacing(Spacing.XL)
        
        # Scanner configuration
        config_layout = QVBoxLayout()
        config_layout.setSpacing(Spacing.LG)
        
        section_title = QLabel("Scanner Configuration")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        config_layout.addWidget(section_title)
        
        # Max concurrent scans
        concurrent_layout = QHBoxLayout()
        concurrent_layout.setSpacing(Spacing.MD)
        concurrent_label = QLabel("Max Concurrent Scans")
        concurrent_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        concurrent_layout.addWidget(concurrent_label)
        
        self.concurrent_scans_spin = QSpinBox()
        self.concurrent_scans_spin.setRange(1, 10)
        self.concurrent_scans_spin.setValue(3)
        concurrent_layout.addWidget(self.concurrent_scans_spin)
        concurrent_layout.addStretch()
        config_layout.addLayout(concurrent_layout)
        
        # Default timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.setSpacing(Spacing.MD)
        timeout_label = QLabel("Default Timeout (s)")
        timeout_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        timeout_layout.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        config_layout.addLayout(timeout_layout)
        
        # Enable verbose logging
        self.verbose_checkbox = QCheckBox("Enable verbose scanner output")
        config_layout.addWidget(self.verbose_checkbox)
        
        scanner_layout.addLayout(config_layout)
        scanner_layout.addStretch()
        
        self.settings_tabs.addTab(scanner_widget, "Scanners")
    
    def setup_network_tab(self):
        """Setup network settings tab"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        network_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        network_layout.setSpacing(Spacing.XL)
        
        # Network configuration
        config_layout = QVBoxLayout()
        config_layout.setSpacing(Spacing.LG)
        
        section_title = QLabel("Network Configuration")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        config_layout.addWidget(section_title)
        
        # Proxy settings
        proxy_layout = QHBoxLayout()
        proxy_layout.setSpacing(Spacing.MD)
        proxy_label = QLabel("HTTP Proxy")
        proxy_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        proxy_layout.addWidget(proxy_label)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://proxy:port")
        proxy_layout.addWidget(self.proxy_input)
        proxy_layout.addStretch()
        config_layout.addLayout(proxy_layout)
        
        # User agent
        user_agent_layout = QHBoxLayout()
        user_agent_layout.setSpacing(Spacing.MD)
        ua_label = QLabel("User Agent")
        ua_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        user_agent_layout.addWidget(ua_label)
        
        self.user_agent_input = QLineEdit()
        self.user_agent_input.setPlaceholderText("X-Shield/2.0.0")
        user_agent_layout.addWidget(self.user_agent_input)
        user_agent_layout.addStretch()
        config_layout.addLayout(user_agent_layout)
        
        # Enable proxy
        self.enable_proxy_checkbox = QCheckBox("Enable HTTP proxy")
        config_layout.addWidget(self.enable_proxy_checkbox)
        
        network_layout.addLayout(config_layout)
        network_layout.addStretch()
        
        self.settings_tabs.addTab(network_widget, "Network")
    
    def setup_security_tab(self):
        """Setup security settings tab"""
        security_widget = QWidget()
        security_layout = QVBoxLayout(security_widget)
        security_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        security_layout.setSpacing(Spacing.XL)
        
        # Security configuration
        config_layout = QVBoxLayout()
        config_layout.setSpacing(Spacing.LG)
        
        section_title = QLabel("Security Settings")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        config_layout.addWidget(section_title)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.setSpacing(Spacing.MD)
        api_key_label = QLabel("API Key")
        api_key_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        api_key_layout.addWidget(api_key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addStretch()
        config_layout.addLayout(api_key_layout)
        
        # Security checkboxes
        self.encryption_checkbox = QCheckBox("Enable data encryption")
        config_layout.addWidget(self.encryption_checkbox)
        
        self.secure_storage_checkbox = QCheckBox("Secure storage for sensitive data")
        config_layout.addWidget(self.secure_storage_checkbox)
        
        security_layout.addLayout(config_layout)
        security_layout.addStretch()
        
        self.settings_tabs.addTab(security_widget, "Security")
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons with modern minimal style"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.MD)
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.setMinimumWidth(140)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setMinimumWidth(140)
        buttons_layout.addWidget(self.reset_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setMinimumWidth(100)
        buttons_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("Import")
        self.import_btn.setMinimumWidth(100)
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
