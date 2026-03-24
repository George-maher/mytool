"""
OSINT Page for X-Shield MVC Architecture
Refactored to use ModuleManager and modern design system
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QProgressBar, QFrame, QComboBox
)
from PySide6.QtCore import Qt, Slot
from ui.components.styles import Colors, Spacing, Typography


class OSINTPage(QWidget):
    """OSINT page with threading and terminal output"""

    def __init__(self, target_manager, module_manager, logger, parent=None):
        super().__init__(parent)
        self.target_manager = target_manager
        self.module_manager = module_manager
        self.logger = logger

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup OSINT UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)

        # OSINT Configuration
        self.setup_osint_config(layout)

        # Terminal Output
        self.setup_terminal_output(layout)

        # Progress Section
        self.setup_progress_section(layout)

        layout.addStretch()

    def setup_osint_config(self, parent_layout):
        """Setup modern OSINT configuration section"""
        config_frame = QFrame()
        config_frame.setObjectName("card")

        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        config_layout.setSpacing(Spacing.SM)

        # Modern Section Title
        section_title = QLabel("Reconnaissance Parameters")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        config_layout.addWidget(section_title)

        # Target selection
        target_layout = QHBoxLayout()
        target_layout.setSpacing(Spacing.SM)

        target_label = QLabel("Target")
        target_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        target_layout.addWidget(target_label)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Domain, company, or email...")
        target_layout.addWidget(self.target_input)

        self.get_active_btn = QPushButton("Use Active")
        self.get_active_btn.setProperty("class", "small")
        target_layout.addWidget(self.get_active_btn)

        config_layout.addLayout(target_layout)

        # Modern OSINT Type Selection
        osint_type_layout = QHBoxLayout()
        osint_type_layout.setSpacing(Spacing.SM)

        osint_type_label = QLabel("OSINT Type")
        osint_type_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        osint_type_layout.addWidget(osint_type_label)

        self.osint_type_combo = QComboBox()
        self.osint_type_combo.addItems([
            "whois", "dns", "shodan", "subdomain", "email", "social", "metadata"
        ])
        osint_type_layout.addWidget(self.osint_type_combo)

        config_layout.addLayout(osint_type_layout)

        # Modern Control Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.XL)

        self.start_btn = QPushButton("Start OSINT")
        self.start_btn.setObjectName("primary_btn")
        self.start_btn.setMinimumWidth(160)
        buttons_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumWidth(100)
        buttons_layout.addWidget(self.stop_btn)

        buttons_layout.addStretch()
        config_layout.addLayout(buttons_layout)

        parent_layout.addWidget(config_frame)

    def setup_terminal_output(self, parent_layout):
        """Setup modern terminal output section"""
        terminal_frame = QFrame()
        terminal_frame.setObjectName("card")

        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        terminal_layout.setSpacing(Spacing.SM)

        # Modern Section Title
        section_title = QLabel("Intelligence Harvest")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        terminal_layout.addWidget(section_title)

        # Modern Terminal Widget
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(300)
        self.terminal.setProperty("class", "Terminal")

        # Add initial message
        self.add_terminal_message("INFO", "Ready for intelligence gathering")

        terminal_layout.addWidget(self.terminal)
        parent_layout.addWidget(terminal_frame)

    def setup_progress_section(self, parent_layout):
        """Setup modern progress section"""
        progress_frame = QFrame()
        progress_frame.setObjectName("card")

        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        progress_layout.setSpacing(Spacing.SM)

        # Modern Status Label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        progress_layout.addWidget(self.status_label)

        # Modern Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        parent_layout.addWidget(progress_frame)

    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.start_btn.clicked.connect(self.start_scan)
        self.stop_btn.clicked.connect(self.stop_scan)
        self.get_active_btn.clicked.connect(self.get_active_target)

    def get_active_target(self):
        """Get active target from target manager"""
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target:
                self.target_input.setText(active_target.value)
                self.add_terminal_message("INFO", f"Loaded active target: {active_target.value}")
            else:
                self.add_terminal_message("WARNING", "No active target set")

    def start_scan(self):
        """Start OSINT scan via ModuleManager"""
        target = self.target_input.text().strip()

        if not target:
            self.add_terminal_message("ERROR", "Please enter a target for OSINT")
            return

        if not self.module_manager:
            self.add_terminal_message("ERROR", "Module Manager not available")
            return

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.target_input.setEnabled(False)
        self.osint_type_combo.setEnabled(False)

        # Clear terminal
        self.terminal.clear()
        self.add_terminal_message("INFO", f"Starting OSINT harvest on {target}...")

        # Connect signals and run module
        self.module_manager.module_finished.connect(self.on_result)
        self.module_manager.module_error.connect(self.on_error)
        self.module_manager.progress_updated.connect(self.on_progress)

        success = self.module_manager.run_module("osint", target, {
            'osint_type': self.osint_type_combo.currentText()
        })

        if not success:
            self.add_terminal_message("ERROR", "Failed to start OSINT module")
            self.on_finished()

    def stop_scan(self):
        """Stop OSINT scan"""
        if self.module_manager:
            self.module_manager.stop_module("osint")
            self.add_terminal_message("WARNING", "Stopping OSINT harvest...")

    def on_progress(self, module_name, current, total):
        """Handle progress updates"""
        if module_name == "osint":
            self.progress_bar.setValue(current)
            percentage = int((current / total) * 100) if total > 0 else 0
            self.status_label.setText(f"Status: Harvesting... {percentage}%")

    def on_result(self, module_name, result):
        """Handle scan result"""
        if module_name == "osint":
            self.add_terminal_message("SUCCESS", "OSINT gathering completed!")

            # Display results
            self.add_terminal_message("RESULT", f"Target: {result['target']}")
            self.add_terminal_message("RESULT", f"Information gathered: {len(result.get('findings', []))}")

            for finding in result.get('findings', []):
                self.add_terminal_message("INTEL", f"{finding['type']}: {finding['details']}")

            self.on_finished()

    def on_error(self, module_name, error):
        """Handle scan error"""
        if module_name == "osint":
            self.add_terminal_message("ERROR", error)
            self.on_finished()

    def on_finished(self):
        """Reset UI after scan"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.target_input.setEnabled(True)
        self.osint_type_combo.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Ready")

    def add_terminal_message(self, msg_type, message):
        """Add message to terminal with Modern Minimal color coding"""
        colors = {
            "INFO": Colors.TEXT_SECONDARY,
            "SUCCESS": Colors.SUCCESS,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.DANGER,
            "RESULT": Colors.INFO,
            "INTEL": Colors.PRIMARY
        }

        color = colors.get(msg_type, Colors.TEXT_PRIMARY)

        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")

        formatted_message = f'<span style="color: {Colors.TEXT_MUTED};">[{timestamp}]</span> <span style="color: {color}; font-weight: 600;">[{msg_type}]</span> <span style="color: {Colors.TEXT_PRIMARY};">{message}</span>'

        self.terminal.append(formatted_message)
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_enter(self):
        """Called when page is entered"""
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target:
                self.target_input.setText(active_target.value)
