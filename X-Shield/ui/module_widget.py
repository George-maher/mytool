"""
Module Configuration Widget for X-Shield Framework
Provides interface for configuring and running pentesting modules
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QSpinBox, QCheckBox, QComboBox, QGroupBox,
    QFormLayout, QScrollArea, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class ModuleWidget(QWidget):
    """Widget for configuring pentesting modules"""
    
    def __init__(self):
        super().__init__()
        self.current_module = None
        self.current_module_info = None
        self.parameter_widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup module configuration UI"""
        layout = QVBoxLayout(self)
        
        # Scroll area for configuration
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.config_widget = QWidget()
        self.config_layout = QVBoxLayout(self.config_widget)
        scroll_area.setWidget(self.config_widget)
        layout.addWidget(scroll_area)
        
        # Default message
        self.show_default_message()
    
    def show_default_message(self):
        """Show default message when no module is selected"""
        self.clear_config()
        
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        
        message_label = QLabel("Select a module from the left panel to configure and run it.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 16px;
                padding: 40px;
                background-color: #1f2937;
                border-radius: 8px;
                border: 2px dashed #374151;
            }
        """)
        
        message_layout.addWidget(message_label)
        self.config_layout.addWidget(message_frame)
    
    def display_module_config(self, module_name, module_info):
        """Display configuration for selected module"""
        self.current_module = module_name
        self.current_module_info = module_info
        self.parameter_widgets.clear()
        
        # Clear existing config
        self.clear_config()
        
        # Module header
        self.create_module_header(module_info)
        
        # Target configuration
        self.create_target_config()
        
        # Module parameters
        if module_info.get('parameters'):
            self.create_parameters_config(module_info['parameters'])
        
        # Action buttons
        self.create_action_buttons()
    
    def create_module_header(self, module_info):
        """Create module information header"""
        header_group = QGroupBox("Module Information")
        header_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #8b5cf6;
                border: 2px solid #374151;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        header_layout = QFormLayout(header_group)
        
        # Module name
        name_label = QLabel(self.current_module)
        name_label.setStyleSheet("color: #e5e7eb; font-weight: bold;")
        header_layout.addRow("Name:", name_label)
        
        # Description
        desc_label = QLabel(module_info.get('description', 'No description'))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #9ca3af;")
        header_layout.addRow("Description:", desc_label)
        
        # Version
        version_label = QLabel(module_info.get('version', '1.0.0'))
        version_label.setStyleSheet("color: #9ca3af;")
        header_layout.addRow("Version:", version_label)
        
        # Author
        author_label = QLabel(module_info.get('author', 'Unknown'))
        author_label.setStyleSheet("color: #9ca3af;")
        header_layout.addRow("Author:", author_label)
        
        # Category
        category_label = QLabel(module_info.get('category', 'General'))
        category_label.setStyleSheet("color: #9ca3af;")
        header_layout.addRow("Category:", category_label)
        
        self.config_layout.addWidget(header_group)
    
    def create_target_config(self):
        """Create target configuration section"""
        target_group = QGroupBox("Target Configuration")
        target_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #8b5cf6;
                border: 2px solid #374151;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        target_layout = QFormLayout(target_group)
        
        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target (IP address, domain, URL, etc.)")
        self.target_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
            QLineEdit:focus {
                border: 2px solid #8b5cf6;
            }
        """)
        target_layout.addRow("Target:", self.target_input)
        
        self.config_layout.addWidget(target_group)
    
    def create_parameters_config(self, parameters):
        """Create module-specific parameters configuration"""
        params_group = QGroupBox("Module Parameters")
        params_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #8b5cf6;
                border: 2px solid #374151;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        params_layout = QFormLayout(params_group)
        
        for param_name, param_config in parameters.items():
            param_type = param_config.get('type', 'string')
            param_label = param_config.get('label', param_name.title())
            param_default = param_config.get('default', '')
            param_description = param_config.get('description', '')
            
            # Create widget based on type
            if param_type == 'string':
                widget = QLineEdit()
                widget.setText(str(param_default))
                widget.setStyleSheet("""
                    QLineEdit {
                        background-color: #374151;
                        color: #e5e7eb;
                        border: 1px solid #4b5563;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #8b5cf6;
                    }
                """)
            
            elif param_type == 'text':
                widget = QTextEdit()
                widget.setMaximumHeight(100)
                widget.setPlainText(str(param_default))
                widget.setStyleSheet("""
                    QTextEdit {
                        background-color: #374151;
                        color: #e5e7eb;
                        border: 1px solid #4b5563;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QTextEdit:focus {
                        border: 2px solid #8b5cf6;
                    }
                """)
            
            elif param_type == 'integer':
                widget = QSpinBox()
                widget.setMinimum(param_config.get('min', 0))
                widget.setMaximum(param_config.get('max', 999999))
                widget.setValue(int(param_default) if param_default else 0)
                widget.setStyleSheet("""
                    QSpinBox {
                        background-color: #374151;
                        color: #e5e7eb;
                        border: 1px solid #4b5563;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QSpinBox:focus {
                        border: 2px solid #8b5cf6;
                    }
                """)
            
            elif param_type == 'boolean':
                widget = QCheckBox()
                widget.setChecked(bool(param_default))
                widget.setStyleSheet("""
                    QCheckBox {
                        color: #e5e7eb;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid #4b5563;
                        border-radius: 4px;
                        background-color: #374151;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #8b5cf6;
                        border-color: #8b5cf6;
                    }
                """)
            
            elif param_type == 'choice':
                widget = QComboBox()
                widget.addItems(param_config.get('choices', []))
                if param_default:
                    index = widget.findText(param_default)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                widget.setStyleSheet("""
                    QComboBox {
                        background-color: #374151;
                        color: #e5e7eb;
                        border: 1px solid #4b5563;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QComboBox:focus {
                        border: 2px solid #8b5cf6;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #e5e7eb;
                    }
                """)
            
            else:
                # Default to string input
                widget = QLineEdit()
                widget.setText(str(param_default))
                widget.setStyleSheet("""
                    QLineEdit {
                        background-color: #374151;
                        color: #e5e7eb;
                        border: 1px solid #4b5563;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #8b5cf6;
                    }
                """)
            
            # Add tooltip if description available
            if param_description:
                widget.setToolTip(param_description)
            
            # Store widget reference
            self.parameter_widgets[param_name] = widget
            
            # Add to layout
            params_layout.addRow(f"{param_label}:", widget)
        
        self.config_layout.addWidget(params_group)
    
    def create_action_buttons(self):
        """Create action buttons for module execution"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # Validate configuration button
        self.validate_btn = QPushButton("Validate Configuration")
        self.validate_btn.clicked.connect(self.validate_configuration)
        self.validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        button_layout.addWidget(self.validate_btn)
        
        # Save preset button
        self.save_preset_btn = QPushButton("Save Preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.save_preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        button_layout.addWidget(self.save_preset_btn)
        
        button_layout.addStretch()
        
        self.config_layout.addWidget(button_frame)
    
    def clear_config(self):
        """Clear current configuration display"""
        while self.config_layout.count():
            child = self.config_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def get_target(self):
        """Get configured target"""
        return self.target_input.text().strip() if hasattr(self, 'target_input') else ""
    
    def get_parameters(self):
        """Get configured parameters"""
        parameters = {}
        
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                parameters[param_name] = widget.text()
            elif isinstance(widget, QTextEdit):
                parameters[param_name] = widget.toPlainText()
            elif isinstance(widget, QSpinBox):
                parameters[param_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                parameters[param_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                parameters[param_name] = widget.currentText()
        
        return parameters
    
    def validate_configuration(self):
        """Validate current configuration"""
        target = self.get_target()
        if not target:
            return False, "Target is required"
        
        # Additional validation based on module type
        if self.current_module == "network_scanner":
            if not self._validate_ip_or_hostname(target):
                return False, "Invalid IP address or hostname"
        
        elif self.current_module == "web_scanner":
            if not target.startswith(('http://', 'https://')):
                return False, "Web scanner requires a valid URL (http:// or https://)"
        
        return True, "Configuration is valid"
    
    def _validate_ip_or_hostname(self, target):
        """Simple validation for IP address or hostname"""
        import re
        
        # IP address validation
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, target):
            parts = target.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # Hostname validation (simplified)
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(hostname_pattern, target))
    
    def save_preset(self):
        """Save current configuration as preset"""
        # This would save the configuration to a file
        # Implementation depends on requirements
        pass
    
    def load_preset(self, preset_name):
        """Load a saved preset"""
        # This would load configuration from a file
        # Implementation depends on requirements
        pass
