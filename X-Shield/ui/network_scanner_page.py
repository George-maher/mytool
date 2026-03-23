"""
Network Scanner Page for X-Shield MVC Architecture
Template for scanner pages with background threading
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QProgressBar, QFrame, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer
from PySide6.QtGui import QFont, QTextCursor


class NetworkScannerWorker(QThread):
    """Background worker for network scanning"""
    
    # Signals
    progress = Signal(int, int)  # current, total
    status = Signal(str)        # status message
    result = Signal(dict)       # scan result
    error = Signal(str)         # error message
    finished = Signal()         # scan finished
    
    def __init__(self, target, parameters=None):
        super().__init__()
        self.target = target
        self.parameters = parameters or {}
        self.is_running = False
        self.should_stop = False
    
    def run(self):
        """Run the network scan in background"""
        self.is_running = True
        self.should_stop = False
        
        try:
            self.status.emit(f"Starting network scan on {self.target}")
            
            # Simulate network scan with different phases
            phases = [
                ("Host Discovery", 20),
                ("Port Scanning", 40),
                ("Service Detection", 30),
                ("OS Fingerprinting", 10)
            ]
            
            results = {
                'target': self.target,
                'scan_type': 'network',
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
                
                # Simulate work with progress updates
                phase_steps = 10
                for step in range(phase_steps):
                    if self.should_stop:
                        break
                    
                    # Simulate scanning work
                    self.msleep(200)  # 200ms delay
                    
                    # Emit progress
                    phase_progress = (step + 1) / phase_steps
                    current_progress = total_progress + (phase_progress * phase_weight)
                    self.progress.emit(int(current_progress), 100)
                
                total_progress += phase_weight
                
                # Add mock findings
                if phase_name == "Host Discovery":
                    results['findings'].append({
                        'type': 'host_alive',
                        'details': f"Host {self.target} is responding to ping"
                    })
                elif phase_name == "Port Scanning":
                    open_ports = [22, 80, 443, 8080]
                    for port in open_ports:
                        results['findings'].append({
                            'type': 'open_port',
                            'details': f"Port {port} is open"
                        })
                elif phase_name == "Service Detection":
                    services = {
                        22: "SSH",
                        80: "HTTP",
                        443: "HTTPS",
                        8080: "HTTP-Alt"
                    }
                    for port, service in services.items():
                        results['findings'].append({
                            'type': 'service',
                            'details': f"Port {port}: {service}"
                        })
                elif phase_name == "OS Fingerprinting":
                    results['findings'].append({
                        'type': 'os_info',
                        'details': "OS fingerprint: Linux (likely Ubuntu)"
                    })
            
            # Add mock vulnerabilities
            if not self.should_stop:
                results['vulnerabilities'] = [
                    {
                        'severity': 'Medium',
                        'title': 'SSH Version 7.4',
                        'description': 'SSH server version may have known vulnerabilities'
                    },
                    {
                        'severity': 'Low',
                        'title': 'HTTP Server Header',
                        'description': 'Server header exposes server information'
                    }
                ]
                
                results['summary'] = f"Network scan completed for {self.target}. Found {len(results['findings'])} findings and {len(results['vulnerabilities'])} potential vulnerabilities."
            
            if not self.should_stop:
                self.result.emit(results)
            
        except Exception as e:
            self.error.emit(f"Scan error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()
    
    def stop(self):
        """Stop the scan"""
        self.should_stop = True


class NetworkScannerPage(QWidget):
    """Network Scanner page with threading and terminal output"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        self.target_manager = parent.get_target_manager() if parent else None
        
        self.worker = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup network scanner UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Network Scanner")
        title_label.setFont(QFont("Roboto", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title_label)
        
        # Scanner Configuration
        self.setup_scanner_config(layout)
        
        # Terminal Output
        self.setup_terminal_output(layout)
        
        # Progress Section
        self.setup_progress_section(layout)
        
        layout.addStretch()
    
    def setup_scanner_config(self, parent_layout):
        """Setup scanner configuration section"""
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        config_layout = QVBoxLayout(config_frame)
        config_layout.setSpacing(16)
        
        # Section title
        section_title = QLabel("Scanner Configuration")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        config_layout.addWidget(section_title)
        
        # Target selection
        target_layout = QHBoxLayout()
        target_layout.setSpacing(12)
        
        target_label = QLabel("Target:")
        target_label.setFont(QFont("Roboto", 12))
        target_label.setStyleSheet("color: #b0b0b0;")
        target_layout.addWidget(target_label)
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target IP or hostname...")
        self.target_input.setStyleSheet("""
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
        target_layout.addWidget(self.target_input)
        
        # Get active target button
        self.get_active_btn = QPushButton("🎯 Use Active")
        self.get_active_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        target_layout.addWidget(self.get_active_btn)
        
        target_layout.addStretch()
        config_layout.addLayout(target_layout)
        
        # Scan type
        scan_type_layout = QHBoxLayout()
        scan_type_layout.setSpacing(12)
        
        scan_type_label = QLabel("Scan Type:")
        scan_type_label.setFont(QFont("Roboto", 12))
        scan_type_label.setStyleSheet("color: #b0b0b0;")
        scan_type_layout.addWidget(scan_type_label)
        
        self.scan_type_combo = QComboBox()
        self.scan_type_combo.addItems([
            "Quick Scan", "Full Scan", "Port Scan", "Service Scan", "OS Detection"
        ])
        self.scan_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 14px;
                min-width: 200px;
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
        scan_type_layout.addWidget(self.scan_type_combo)
        
        scan_type_layout.addStretch()
        config_layout.addLayout(scan_type_layout)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.start_btn = QPushButton("🚀 Start Scan")
        self.start_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop Scan")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #da190b;

            }
            QPushButton:pressed {
                background-color: #b71c1c;

            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;

            }
        """)
        buttons_layout.addWidget(self.stop_btn)
        
        buttons_layout.addStretch()
        config_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(config_frame)
    
    def setup_terminal_output(self, parent_layout):
        """Setup terminal output section"""
        terminal_frame = QFrame()
        terminal_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setSpacing(16)
        
        # Section title
        section_title = QLabel("Terminal Output")
        section_title.setFont(QFont("Roboto", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        terminal_layout.addWidget(section_title)
        
        # Terminal widget
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(300)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                border: 2px solid #404040;
                border-radius: 8px;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 16px;
            }
        """)
        
        # Add initial message
        self.terminal.append('<span style="color: #2196F3;">[NETWORK SCANNER]</span> <span style="color: #ffffff;">Ready to scan targets</span>')
        
        terminal_layout.addWidget(self.terminal)
        
        parent_layout.addWidget(terminal_frame)
    
    def setup_progress_section(self, parent_layout):
        """Setup progress section"""
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
            }
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(12)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Roboto", 12))
        self.status_label.setStyleSheet("color: #b0b0b0;")
        progress_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                text-align: center;
                color: white;
                font-weight: bold;
                background-color: #2d2d2d;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2e7d32;
                border-radius: 6px;
            }
        """)
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
        """Start network scan"""
        target = self.target_input.text().strip()
        
        if not target:
            self.add_terminal_message("ERROR", "Please enter a target")
            return
        
        # Get active target from target manager if not specified
        if not target and self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target:
                target = active_target.value
                self.target_input.setText(target)
            else:
                self.add_terminal_message("ERROR", "No target specified and no active target set")
                return
        
        # Create and start worker
        self.worker = NetworkScannerWorker(target, {
            'scan_type': self.scan_type_combo.currentText()
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
        self.scan_type_combo.setEnabled(False)
        
        # Clear terminal
        self.terminal.clear()
        self.add_terminal_message("INFO", f"Starting network scan on {target}")
        
        # Start worker
        self.worker.start()
        
        if self.logger:
            self.logger.info(f"Network scan started on target: {target}")
    
    def stop_scan(self):
        """Stop network scan"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.add_terminal_message("WARNING", "Stopping scan...")
            
            if self.logger:
                self.logger.info("Network scan stopped by user")
    
    def on_progress(self, current, total):
        """Handle progress updates"""
        self.progress_bar.setValue(current)
        percentage = int((current / total) * 100) if total > 0 else 0
        self.add_terminal_message("PROGRESS", f"Scan progress: {percentage}%")
    
    def on_status(self, status):
        """Handle status updates"""
        self.status_label.setText(f"Status: {status}")
        self.add_terminal_message("STATUS", status)
    
    def on_result(self, result):
        """Handle scan result"""
        self.add_terminal_message("SUCCESS", "Scan completed successfully!")
        
        # Display results
        self.add_terminal_message("RESULT", f"Target: {result['target']}")
        self.add_terminal_message("RESULT", f"Findings: {len(result['findings'])}")
        self.add_terminal_message("RESULT", f"Vulnerabilities: {len(result['vulnerabilities'])}")
        
        for finding in result['findings']:
            self.add_terminal_message("FINDING", f"{finding['type']}: {finding['details']}")
        
        for vuln in result['vulnerabilities']:
            self.add_terminal_message("VULNERABILITY", f"[{vuln['severity']}] {vuln['title']}")
        
        # Update target with scan results
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target and active_target.value == result['target']:
                active_target.add_scan_result('network_scanner', result)
                self.target_manager.target_updated.emit(active_target.id, active_target.to_dict())
        
        if self.logger:
            self.logger.info(f"Network scan completed for {result['target']}")
    
    def on_error(self, error):
        """Handle scan error"""
        self.add_terminal_message("ERROR", error)
        
        if self.logger:
            self.logger.error(f"Network scan error: {error}")
    
    def on_finished(self):
        """Handle scan finished"""
        # Reset UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.target_input.setEnabled(True)
        self.scan_type_combo.setEnabled(True)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Ready")
        
        self.add_terminal_message("INFO", "Scan finished. Ready for next scan.")
        
        # Cleanup worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def add_terminal_message(self, msg_type, message):
        """Add message to terminal with color coding"""
        colors = {
            "INFO": "#2196F3",
            "SUCCESS": "#4CAF50",
            "WARNING": "#FF9800",
            "ERROR": "#f44336",
            "RESULT": "#9C27B0",
            "FINDING": "#FFC107",
            "VULNERABILITY": "#f44336",
            "STATUS": "#00BCD4",
            "PROGRESS": "#607D8B"
        }
        
        color = colors.get(msg_type, "#ffffff")
        
        # Move cursor to end
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Add message with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted_message = f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">[{msg_type}]</span> <span style="color: #ffffff;">{message}</span>'
        
        self.terminal.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_enter(self):
        """Called when page is entered"""
        # Get active target if available
        if self.target_manager:
            active_target = self.target_manager.get_active_target()
            if active_target:
                self.target_input.setText(active_target.value)
                self.add_terminal_message("INFO", f"Active target loaded: {active_target.value}")
        
        if self.logger:
            self.logger.info("Network Scanner page entered")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
