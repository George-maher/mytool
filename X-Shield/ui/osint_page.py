"""
OSINT Page for X-Shield MVC Architecture
Open Source Intelligence gathering interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QProgressBar, QFrame, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont, QTextCursor
from ui.styles import Colors, Spacing, Typography


class OSINTWorker(QThread):
    """Background worker for OSINT operations"""
    
    # Signals
    progress = Signal(int, int)
    status = Signal(str)
    result = Signal(dict)
    error = Signal(str)
    finished = Signal()
    
    def __init__(self, target, parameters=None):
        super().__init__()
        self.target = target
        self.parameters = parameters or {}
        self.is_running = False
        self.should_stop = False
    
    def run(self):
        """Run OSINT gathering in background"""
        self.is_running = True
        self.should_stop = False
        
        try:
            self.status.emit(f"Starting OSINT on {self.target}")
            
            # Simulate OSINT phases
            phases = [
                ("Domain Information", 25),
                ("DNS Records", 20),
                ("Subdomain Discovery", 25),
                ("Email Harvesting", 15),
                ("Social Media Search", 15)
            ]
            
            results = {
                'target': self.target,
                'scan_type': 'osint',
                'timestamp': None,
                'findings': [],
                'vulnerabilities': [],
                'summary': ''
            }
            
            total_progress = 0
            for phase_name, phase_weight in phases:
                if self.should_stop:
                    break
                
                self.status.emit(f"Phase: {phase_name}")
                
                # Simulate work
                phase_steps = 6
                for step in range(phase_steps):
                    if self.should_stop:
                        break
                    
                    self.msleep(400)
                    phase_progress = (step + 1) / phase_steps
                    current_progress = total_progress + (phase_progress * phase_weight)
                    self.progress.emit(int(current_progress), 100)
                
                total_progress += phase_weight
                
                # Add mock findings
                if phase_name == "Domain Information":
                    results['findings'].append({
                        'type': 'domain_info',
                        'details': f"Domain registered: 2019-01-15, Expires: 2024-01-15"
                    })
                elif phase_name == "DNS Records":
                    results['findings'].append({
                        'type': 'dns_record',
                        'details': "A: 192.168.1.1, MX: mail.example.com"
                    })
                elif phase_name == "Subdomain Discovery":
                    subdomains = ["api.example.com", "blog.example.com", "dev.example.com"]
                    for subdomain in subdomains:
                        results['findings'].append({
                            'type': 'subdomain',
                            'details': f"Found subdomain: {subdomain}"
                        })
                elif phase_name == "Email Harvesting":
                    results['findings'].append({
                        'type': 'email',
                        'details': "Found emails: admin@example.com, support@example.com"
                    })
                elif phase_name == "Social Media Search":
                    results['findings'].append({
                        'type': 'social_media',
                        'details': "LinkedIn: Example Corp, Twitter: @examplecorp"
                    })
            
            if not self.should_stop:
                results['summary'] = f"OSINT completed for {self.target}. Found {len(results['findings'])} pieces of information."
                self.result.emit(results)
            
        except Exception as e:
            self.error.emit(f"OSINT error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()
    
    def stop(self):
        """Stop the OSINT operation"""
        self.should_stop = True


class OSINTPage(QWidget):
    """OSINT page for open source intelligence gathering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        self.target_manager = parent.get_target_manager() if parent else None
        
        self.worker = None
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
        """Setup OSINT configuration with modern minimal style"""
        config_frame = QFrame()
        config_frame.setObjectName("card")
        config_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        config_layout.setSpacing(Spacing.XL)
        
        # Section title
        section_title = QLabel("Reconnaissance Parameters")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        config_layout.addWidget(section_title)
        
        # Target input
        target_layout = QHBoxLayout()
        target_layout.setSpacing(Spacing.MD)
        
        target_label = QLabel("Target")
        target_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        target_layout.addWidget(target_label)
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Domain, company, or email...")
        target_layout.addWidget(self.target_input)
        
        # Get active target button
        self.get_active_btn = QPushButton("Use Active")
        self.get_active_btn.setProperty("class", "small")
        target_layout.addWidget(self.get_active_btn)
        
        config_layout.addLayout(target_layout)
        
        # OSINT type
        osint_type_layout = QHBoxLayout()
        osint_type_layout.setSpacing(Spacing.MD)
        
        osint_type_label = QLabel("OSINT Type")
        osint_type_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        osint_type_layout.addWidget(osint_type_label)
        
        self.osint_type_combo = QComboBox()
        self.osint_type_combo.addItems([
            "Domain Analysis", "Email Investigation", "Company Research", "Username Search", "Comprehensive"
        ])
        osint_type_layout.addWidget(self.osint_type_combo)
        
        osint_type_layout.addStretch()
        config_layout.addLayout(osint_type_layout)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.MD)
        
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
        """Setup terminal output with modern minimal style"""
        terminal_frame = QFrame()
        terminal_frame.setObjectName("card")
        terminal_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        terminal_layout.setSpacing(Spacing.MD)
        
        # Section title
        section_title = QLabel("Intelligence Harvest")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        terminal_layout.addWidget(section_title)
        
        # Terminal widget
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(300)
        self.terminal.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FAMILY_MONO};
                font-size: 12px;
                padding: {Spacing.MD}px;
            }}
        """)
        
        self.terminal.append(f'<span style="color: {Colors.PRIMARY}; font-weight: 600;">[OSINT]</span> <span style="color: {Colors.TEXT_PRIMARY};">Ready for intelligence gathering</span>')
        
        terminal_layout.addWidget(self.terminal)
        
        parent_layout.addWidget(terminal_frame)
    
    def setup_progress_section(self, parent_layout):
        """Setup progress section with modern minimal style"""
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        progress_layout.setSpacing(Spacing.MD)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        progress_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(progress_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.start_btn.clicked.connect(self.start_osint)
        self.stop_btn.clicked.connect(self.stop_osint)
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
    
    def start_osint(self):
        """Start OSINT gathering"""
        target = self.target_input.text().strip()
        
        if not target:
            self.add_terminal_message("ERROR", "Please enter a target for OSINT")
            return
        
        # Create and start worker
        self.worker = OSINTWorker(target, {
            'osint_type': self.osint_type_combo.currentText()
        })
        
        # Connect worker signals
        self.worker.progress.connect(self.on_progress)
        self.worker.status.connect(self.on_status)
        self.worker.result.connect(self.on_result)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.target_input.setEnabled(False)
        self.osint_type_combo.setEnabled(False)
        
        # Clear terminal
        self.terminal.clear()
        self.add_terminal_message("INFO", f"Starting OSINT on {target}")
        
        # Start worker
        self.worker.start()
        
        if self.logger:
            self.logger.info(f"OSINT started on target: {target}")
    
    def stop_osint(self):
        """Stop OSINT gathering"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.add_terminal_message("WARNING", "Stopping OSINT...")
            
            if self.logger:
                self.logger.info("OSINT stopped by user")
    
    def on_progress(self, current, total):
        """Handle progress updates"""
        self.progress_bar.setValue(current)
        percentage = int((current / total) * 100) if total > 0 else 0
        self.add_terminal_message("PROGRESS", f"OSINT progress: {percentage}%")
    
    def on_status(self, status):
        """Handle status updates"""
        self.status_label.setText(f"Status: {status}")
        self.add_terminal_message("STATUS", status)
    
    def on_result(self, result):
        """Handle OSINT result"""
        self.add_terminal_message("SUCCESS", "OSINT gathering completed!")
        
        # Display results
        self.add_terminal_message("RESULT", f"Target: {result['target']}")
        self.add_terminal_message("RESULT", f"Information gathered: {len(result['findings'])}")
        
        for finding in result['findings']:
            self.add_terminal_message("INTEL", f"{finding['type']}: {finding['details']}")
        
        # Update target with OSINT results
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target and active_target.value == result['target']:
                active_target.add_scan_result('osint', result)
                self.target_manager.target_updated.emit(active_target.id, active_target.to_dict())
        
        if self.logger:
            self.logger.info(f"OSINT completed for {result['target']}")
    
    def on_error(self, error):
        """Handle OSINT error"""
        self.add_terminal_message("ERROR", error)
        
        if self.logger:
            self.logger.error(f"OSINT error: {error}")
    
    def on_finished(self):
        """Handle OSINT finished"""
        # Reset UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.target_input.setEnabled(True)
        self.osint_type_combo.setEnabled(True)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Ready")
        
        self.add_terminal_message("INFO", "OSINT finished. Ready for next operation.")
        
        # Cleanup worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def add_terminal_message(self, msg_type, message):
        """Add message to terminal with Modern Minimal color coding"""
        colors = {
            "INFO": Colors.TEXT_SECONDARY,
            "SUCCESS": Colors.SUCCESS,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.DANGER,
            "RESULT": Colors.INFO,
            "INTEL": Colors.PRIMARY,
            "STATUS": Colors.TEXT_MUTED,
            "PROGRESS": Colors.BORDER_HOVER
        }
        
        color = colors.get(msg_type, Colors.TEXT_PRIMARY)
        
        # Move cursor to end
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Add message with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted_message = f'<span style="color: {Colors.TEXT_MUTED};">[{timestamp}]</span> <span style="color: {color}; font-weight: 600;">[{msg_type}]</span> <span style="color: {Colors.TEXT_PRIMARY};">{message}</span>'
        
        self.terminal.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_enter(self):
        """Called when page is entered"""
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target:
                self.target_input.setText(active_target.value)
                self.add_terminal_message("INFO", f"Active target loaded: {active_target.value}")
        
        if self.logger:
            self.logger.info("OSINT page entered")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
