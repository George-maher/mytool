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
from ui.styles import Colors, Spacing, Typography


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for configuration
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.config_widget = QWidget()
        self.config_layout = QVBoxLayout(self.config_widget)
        self.config_layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        self.config_layout.setSpacing(Spacing.XL)

        scroll_area.setWidget(self.config_widget)
        layout.addWidget(scroll_area)
        
        # Default message
        self.show_default_message()
    
    def show_default_message(self):
        """Show default message when no module is selected"""
        self.clear_config()
        
        message_label = QLabel("Select a module from the left panel to configure and run it.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_MUTED};
                font-size: 16px;
                padding: 64px;
                background-color: {Colors.SURFACE};
                border-radius: 12px;
                border: 2px dashed {Colors.BORDER};
            }}
        """)
        
        self.config_layout.addWidget(message_label)
        self.config_layout.addStretch()
    
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
        """Create module information header with modern minimal style"""
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        header_layout.setSpacing(Spacing.LG)
        
        title = QLabel("Module Information")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        header_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(Spacing.MD)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        def add_info_row(label, value):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
            val.setWordWrap(True)
            form_layout.addRow(lbl, val)

        add_info_row("Name", self.current_module)
        add_info_row("Description", module_info.get('description', 'No description'))
        add_info_row("Version", module_info.get('version', '1.0.0'))
        add_info_row("Author", module_info.get('author', 'Unknown'))
        add_info_row("Category", module_info.get('category', 'General'))
        
        header_layout.addLayout(form_layout)
        self.config_layout.addWidget(header_frame)
    
    def create_target_config(self):
        """Create target configuration section with modern minimal style"""
        target_frame = QFrame()
        target_frame.setObjectName("card")
        target_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")

        target_layout = QVBoxLayout(target_frame)
        target_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        target_layout.setSpacing(Spacing.LG)
        
        title = QLabel("Target Configuration")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        target_layout.addWidget(title)
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("IP address, domain, or URL...")
        target_layout.addWidget(self.target_input)
        
        self.config_layout.addWidget(target_frame)
    
    def create_parameters_config(self, parameters):
        """Create module-specific parameters configuration with modern minimal style"""
        params_frame = QFrame()
        params_frame.setObjectName("card")
        params_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        
        params_layout = QVBoxLayout(params_frame)
        params_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        params_layout.setSpacing(Spacing.LG)

        title = QLabel("Module Parameters")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        params_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(Spacing.MD)
        
        for param_name, param_config in parameters.items():
            param_type = param_config.get('type', 'string')
            param_label = param_config.get('label', param_name.title())
            param_default = param_config.get('default', '')
            param_description = param_config.get('description', '')
            
            if param_type == 'string':
                widget = QLineEdit()
                widget.setText(str(param_default))
            elif param_type == 'text':
                widget = QTextEdit()
                widget.setMaximumHeight(80)
                widget.setPlainText(str(param_default))
            elif param_type == 'integer':
                widget = QSpinBox()
                widget.setMinimum(param_config.get('min', 0))
                widget.setMaximum(param_config.get('max', 999999))
                widget.setValue(int(param_default) if param_default else 0)
            elif param_type == 'boolean':
                widget = QCheckBox()
                widget.setChecked(bool(param_default))
            elif param_type == 'choice':
                widget = QComboBox()
                widget.addItems(param_config.get('choices', []))
                if param_default:
                    index = widget.findText(param_default)
                    if index >= 0:
                        widget.setCurrentIndex(index)
            else:
                widget = QLineEdit()
                widget.setText(str(param_default))
            
            if param_description:
                widget.setToolTip(param_description)
            
            self.parameter_widgets[param_name] = widget
            
            label_widget = QLabel(f"{param_label}")
            label_widget.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
            form_layout.addRow(label_widget, widget)
        
        params_layout.addLayout(form_layout)
        self.config_layout.addWidget(params_frame)
    
    def create_action_buttons(self):
        """Create action buttons for module execution with modern minimal style"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.MD)
        
        self.validate_btn = QPushButton("Validate Config")
        self.validate_btn.setObjectName("primary_btn")
        self.validate_btn.setMinimumWidth(150)
        self.validate_btn.clicked.connect(self.validate_configuration)
        buttons_layout.addWidget(self.validate_btn)
        
        self.save_preset_btn = QPushButton("Save Preset")
        self.save_preset_btn.setMinimumWidth(120)
        self.save_preset_btn.clicked.connect(self.save_preset)
        buttons_layout.addWidget(self.save_preset_btn)
        
        buttons_layout.addStretch()
        self.config_layout.addLayout(buttons_layout)
    
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
