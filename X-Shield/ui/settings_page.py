"""
Settings Page for X-Shield Framework
Application configuration with Material Design
"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QGroupBox, QFormLayout, QComboBox, 
    QCheckBox, QSpinBox, QTabWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class SettingsPage(QWidget):
    """Settings page for application configuration"""
    
    # Signals
    settings_changed = Signal(dict)  # settings dictionary
    
    def __init__(self):
        super().__init__()
        self.settings_file = "data/settings.json"
        self.settings = self.load_settings()
        self.setup_ui()
        self.setup_connections()
        self.load_settings_to_ui()
    
    def setup_ui(self):
        """Setup settings page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Settings")
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        header.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #e5e7eb;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # Create tabs
        self.create_general_tab()
        self.create_scanner_tab()
        self.create_api_tab()
        self.create_theme_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Save/Reset buttons
        self.setup_buttons(layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.setContentsMargins(20, 20, 20, 20)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        app_form = QFormLayout(app_group)
        
        # Max console lines
        self.max_console_lines = QSpinBox()
        self.max_console_lines.setRange(100, 10000)
        self.max_console_lines.setValue(1000)
        self.max_console_lines.setSingleStep(100)
        self.max_console_lines.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        app_form.addRow("Max Console Lines:", self.max_console_lines)
        
        # Auto-save reports
        self.auto_save_reports = QCheckBox("Automatically save reports after generation")
        self.auto_save_reports.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """)
        app_form.addRow("", self.auto_save_reports)
        
        # Report directory
        report_layout = QHBoxLayout()
        self.report_dir = QLineEdit()
        self.report_dir.setText("data/reports")
        self.report_dir.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        report_layout.addWidget(self.report_dir)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        browse_btn.clicked.connect(self.browse_report_dir)
        report_layout.addWidget(browse_btn)
        
        app_form.addRow("Report Directory:", report_layout)
        
        general_layout.addWidget(app_group)
        general_layout.addStretch()
        
        self.tab_widget.addTab(general_widget, "General")
    
    def create_scanner_tab(self):
        """Create scanner settings tab"""
        scanner_widget = QWidget()
        scanner_layout = QVBoxLayout(scanner_widget)
        scanner_layout.setContentsMargins(20, 20, 20, 20)
        
        # Scanner defaults
        scanner_group = QGroupBox("Scanner Defaults")
        scanner_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        scanner_form = QFormLayout(scanner_group)
        
        # Default threads
        self.default_threads = QSpinBox()
        self.default_threads.setRange(1, 100)
        self.default_threads.setValue(5)
        self.default_threads.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        scanner_form.addRow("Default Threads:", self.default_threads)
        
        # Default timeout
        self.default_timeout = QSpinBox()
        self.default_timeout.setRange(1, 300)
        self.default_timeout.setValue(30)
        self.default_timeout.setSuffix(" sec")
        self.default_timeout.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        scanner_form.addRow("Default Timeout:", self.default_timeout)
        
        # Enable auto-chain
        self.auto_chain = QCheckBox("Enable automatic module chaining")
        self.auto_chain.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """)
        scanner_form.addRow("", self.auto_chain)
        
        scanner_layout.addWidget(scanner_group)
        scanner_layout.addStretch()
        
        self.tab_widget.addTab(scanner_widget, "Scanners")
    
    def create_api_tab(self):
        """Create API settings tab"""
        api_widget = QWidget()
        api_layout = QVBoxLayout(api_widget)
        api_layout.setContentsMargins(20, 20, 20, 20)
        
        # API Keys
        api_group = QGroupBox("API Keys")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        api_form = QFormLayout(api_group)
        
        # Shodan API key
        self.shodan_key = QLineEdit()
        self.shodan_key.setPlaceholderText("Enter Shodan API key...")
        self.shodan_key.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        api_form.addRow("Shodan API Key:", self.shodan_key)
        
        # VirusTotal API key
        self.virustotal_key = QLineEdit()
        self.virustotal_key.setPlaceholderText("Enter VirusTotal API key...")
        self.virustotal_key.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        api_form.addRow("VirusTotal API Key:", self.virustotal_key)
        
        # Custom API endpoints
        self.custom_endpoints = QTextEdit()
        self.custom_endpoints.setPlaceholderText("Enter custom API endpoints (JSON format)...")
        self.custom_endpoints.setMaximumHeight(100)
        self.custom_endpoints.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        api_form.addRow("Custom Endpoints:", self.custom_endpoints)
        
        api_layout.addWidget(api_group)
        api_layout.addStretch()
        
        self.tab_widget.addTab(api_widget, "API Keys")
    
    def create_theme_tab(self):
        """Create theme settings tab"""
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme settings
        theme_group = QGroupBox("Theme Settings")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        theme_form = QFormLayout(theme_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "dark_cyan",
            "dark_teal", 
            "dark_amber",
            "dark_pink",
            "dark_light"
        ])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                margin-right: 4px;
            }
        """)
        theme_form.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        theme_form.addRow("Font Size:", self.font_size)
        
        # Enable animations
        self.enable_animations = QCheckBox("Enable UI animations")
        self.enable_animations.setChecked(True)
        self.enable_animations.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """)
        theme_form.addRow("", self.enable_animations)
        
        theme_layout.addWidget(theme_group)
        theme_layout.addStretch()
        
        self.tab_widget.addTab(theme_widget, "Theme")
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        advanced_form = QFormLayout(advanced_group)
        
        # Debug mode
        self.debug_mode = QCheckBox("Enable debug mode")
        self.debug_mode.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #FF9800;
                border-color: #FF9800;
            }
        """)
        advanced_form.addRow("", self.debug_mode)
        
        # Log level
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText("INFO")
        self.log_level.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                margin-right: 4px;
            }
        """)
        advanced_form.addRow("Log Level:", self.log_level)
        
        # Database path
        db_layout = QHBoxLayout()
        self.db_path = QLineEdit()
        self.db_path.setText("data/xshield.db")
        self.db_path.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        db_layout.addWidget(self.db_path)
        
        browse_db_btn = QPushButton("Browse")
        browse_db_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        browse_db_btn.clicked.connect(self.browse_db_path)
        db_layout.addWidget(browse_db_btn)
        
        advanced_form.addRow("Database Path:", db_layout)
        
        advanced_layout.addWidget(advanced_group)
        advanced_layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "Advanced")
    
    def setup_buttons(self, parent_layout):
        """Setup save/reset buttons"""
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        buttons_layout.addWidget(self.reset_btn)
        
        buttons_layout.addStretch()
        
        self.export_btn = QPushButton("📤 Export Settings")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        buttons_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("📥 Import Settings")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        buttons_layout.addWidget(self.import_btn)
        
        parent_layout.addWidget(buttons_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.export_btn.clicked.connect(self.export_settings)
        self.import_btn.clicked.connect(self.import_settings)
    
    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            'general': {
                'max_console_lines': 1000,
                'auto_save_reports': True,
                'report_directory': 'data/reports'
            },
            'scanner': {
                'default_threads': 5,
                'default_timeout': 30,
                'auto_chain': True
            },
            'api': {
                'shodan_key': '',
                'virustotal_key': '',
                'custom_endpoints': '{}'
            },
            'theme': {
                'theme': 'dark_cyan',
                'font_size': 12,
                'enable_animations': True
            },
            'advanced': {
                'debug_mode': False,
                'log_level': 'INFO',
                'database_path': 'data/xshield.db'
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults
                for category in default_settings:
                    if category in loaded_settings:
                        default_settings[category].update(loaded_settings[category])
        except Exception:
            pass  # Use defaults if loading fails
        
        return default_settings
    
    def load_settings_to_ui(self):
        """Load settings into UI controls"""
        # General settings
        self.max_console_lines.setValue(self.settings['general']['max_console_lines'])
        self.auto_save_reports.setChecked(self.settings['general']['auto_save_reports'])
        self.report_dir.setText(self.settings['general']['report_directory'])
        
        # Scanner settings
        self.default_threads.setValue(self.settings['scanner']['default_threads'])
        self.default_timeout.setValue(self.settings['scanner']['default_timeout'])
        self.auto_chain.setChecked(self.settings['scanner']['auto_chain'])
        
        # API settings
        self.shodan_key.setText(self.settings['api']['shodan_key'])
        self.virustotal_key.setText(self.settings['api']['virustotal_key'])
        self.custom_endpoints.setText(self.settings['api']['custom_endpoints'])
        
        # Theme settings
        self.theme_combo.setCurrentText(self.settings['theme']['theme'])
        self.font_size.setValue(self.settings['theme']['font_size'])
        self.enable_animations.setChecked(self.settings['theme']['enable_animations'])
        
        # Advanced settings
        self.debug_mode.setChecked(self.settings['advanced']['debug_mode'])
        self.log_level.setCurrentText(self.settings['advanced']['log_level'])
        self.db_path.setText(self.settings['advanced']['database_path'])
    
    @Slot()
    def save_settings(self):
        """Save current settings"""
        try:
            # Collect settings from UI
            self.settings = {
                'general': {
                    'max_console_lines': self.max_console_lines.value(),
                    'auto_save_reports': self.auto_save_reports.isChecked(),
                    'report_directory': self.report_dir.text()
                },
                'scanner': {
                    'default_threads': self.default_threads.value(),
                    'default_timeout': self.default_timeout.value(),
                    'auto_chain': self.auto_chain.isChecked()
                },
                'api': {
                    'shodan_key': self.shodan_key.text(),
                    'virustotal_key': self.virustotal_key.text(),
                    'custom_endpoints': self.custom_endpoints.toPlainText()
                },
                'theme': {
                    'theme': self.theme_combo.currentText(),
                    'font_size': self.font_size.value(),
                    'enable_animations': self.enable_animations.isChecked()
                },
                'advanced': {
                    'debug_mode': self.debug_mode.isChecked(),
                    'log_level': self.log_level.currentText(),
                    'database_path': self.db_path.text()
                }
            }
            
            # Save to file
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            # Emit signal
            self.settings_changed.emit(self.settings)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{str(e)}")
    
    @Slot()
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings = self.load_settings()  # Load defaults
            self.load_settings_to_ui()
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
    
    @Slot()
    def export_settings(self):
        """Export settings to file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "xshield_settings.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                QMessageBox.information(self, "Success", "Settings exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export settings:\n{str(e)}")
    
    @Slot()
    def import_settings(self):
        """Import settings from file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)
                
                self.settings = imported_settings
                self.load_settings_to_ui()
                self.save_settings()  # Save imported settings
                
                QMessageBox.information(self, "Success", "Settings imported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import settings:\n{str(e)}")
    
    @Slot()
    def browse_report_dir(self):
        """Browse for report directory"""
        from PySide6.QtWidgets import QFileDialog
        
        dir_path = QFileDialog.getExistingDirectory(self, "Select Report Directory")
        if dir_path:
            self.report_dir.setText(dir_path)
    
    @Slot()
    def browse_db_path(self):
        """Browse for database file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Database File", "", "SQLite Database (*.db)"
        )
        
        if file_path:
            self.db_path.setText(file_path)
    
    def get_setting(self, category, key, default=None):
        """Get specific setting value"""
        return self.settings.get(category, {}).get(key, default)
    
    def set_setting(self, category, key, value):
        """Set specific setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
