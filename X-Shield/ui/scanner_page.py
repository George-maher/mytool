"""
Scanner Page for X-Shield Framework
Scanner selection and execution with Material Design
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QScrollArea,
    QSpinBox, QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont
from core.target_store import TargetStore


class ScannerPage(QWidget):
    """Scanner selection and execution page"""
    
    # Signals
    scanner_started = Signal(str, str)  # scanner, target
    scanner_finished = Signal(str, dict)  # scanner, results
    scanner_error = Signal(str, str)  # scanner, error
    
    def __init__(self, module_manager, target_store: TargetStore):
        super().__init__()
        self.module_manager = module_manager
        self.target_store = target_store
        self.current_scanner = None
        self.scanner_thread = None
        self.setup_ui()
        self.setup_connections()
        self.refresh_targets()
    
    def setup_ui(self):
        """Setup scanner page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Security Scanners")
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        header.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Scanner configuration
        self.setup_scanner_config(layout)
        
        # Scanner output
        self.setup_scanner_output(layout)
        
        # Scanner results
        self.setup_scanner_results(layout)
    
    def setup_scanner_config(self, parent_layout):
        """Setup scanner configuration section"""
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        config_layout = QVBoxLayout(config_frame)
        
        # Title
        title = QLabel("Scanner Configuration")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 15px;")
        config_layout.addWidget(title)
        
        # Scanner selection form
        form_layout = QFormLayout()
        
        # Target selection
        self.target_combo = QComboBox()
        self.target_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 16px;
                min-width: 350px;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
                background-color: #333333;
                box-shadow: 0 0 8px rgba(33, 150, 243, 0.3);
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ffffff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                color: #ffffff;
                selection-background-color: #2196F3;
                selection-color: white;
                border-radius: 8px;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 12px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #404040;
            }
        """)
        form_layout.addRow("Target:", self.target_combo)
        
        # Scanner type
        self.scanner_combo = QComboBox()
        self.scanner_combo.addItems([
            "Network Scanner",
            "Web Scanner",
            "OSINT Scanner", 
            "Brute Force",
            "Attack/Stress",
            "Threat Intelligence"
        ])
        self.scanner_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
                min-width: 300px;
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
        form_layout.addRow("Scanner Type:", self.scanner_combo)
        
        # Scanner parameters (dynamic)
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout(self.params_widget)
        form_layout.addRow("Parameters:", self.params_widget)
        
        config_layout.addLayout(form_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Start Scan")
        self.start_btn.setProperty("class", "success")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 18px;
                min-height: 30px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #45a049;
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                transform: translateY(0px);
                box-shadow: 0 3px 10px rgba(76, 175, 80, 0.4);
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
                transform: none;
                box-shadow: none;
            }
        """)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop Scan")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 18px;
                min-height: 30px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #da190b;
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
            }
            QPushButton:pressed {
                background-color: #b71c1c;
                transform: translateY(0px);
                box-shadow: 0 3px 10px rgba(244, 67, 54, 0.4);
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
                transform: none;
                box-shadow: none;
            }
        """)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        config_layout.addLayout(button_layout)
        
        parent_layout.addWidget(config_frame)
    
    def setup_scanner_output(self, parent_layout):
        """Setup scanner output section"""
        output_frame = QFrame()
        output_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        output_layout = QVBoxLayout(output_frame)
        
        # Title
        title = QLabel("Scanner Output")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 15px;")
        output_layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #2d2d2d;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 6px;
            }
        """)
        output_layout.addWidget(self.progress_bar)
        
        # Output text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #c9d1d9;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.output_text.setText("Scanner output will appear here...")
        output_layout.addWidget(self.output_text)
        
        parent_layout.addWidget(output_frame)
    
    def setup_scanner_results(self, parent_layout):
        """Setup scanner results section"""
        results_frame = QFrame()
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        results_layout = QVBoxLayout(results_frame)
        
        # Title
        title = QLabel("Scan Results")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 15px;")
        results_layout.addWidget(title)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Type", "Severity", "Description", "Target"])
        
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                gridline-color: #404040;
                color: #ffffff;
                selection-background-color: #2196F3;
                alternate-background-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Severity
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Target
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        results_layout.addWidget(self.results_table)
        
        parent_layout.addWidget(results_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Scanner controls
        self.start_btn.clicked.connect(self.start_scanner)
        self.stop_btn.clicked.connect(self.stop_scanner)
        
        # Scanner selection
        self.scanner_combo.currentTextChanged.connect(self.on_scanner_changed)
        
        # Target store
        self.target_store.targets_updated.connect(self.refresh_targets)
    
    @Slot()
    def refresh_targets(self):
        """Refresh target combo box"""
        self.target_combo.clear()
        targets = self.target_store.get_all_targets()
        
        for target in targets:
            display_text = f"{target.name} ({target.value})"
            self.target_combo.addItem(display_text, target.value)
        
        if targets:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
    
    @Slot(str)
    def on_scanner_changed(self, scanner_name):
        """Handle scanner type change"""
        # Update parameters based on scanner type
        self.update_scanner_parameters(scanner_name)
    
    def update_scanner_parameters(self, scanner_name):
        """Update scanner parameters based on type"""
        # Clear existing parameters
        for i in reversed(range(self.params_layout.count())):
            child = self.params_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add scanner-specific parameters
        if scanner_name == "Network Scanner":
            self.add_network_params()
        elif scanner_name == "Web Scanner":
            self.add_web_params()
        elif scanner_name == "OSINT Scanner":
            self.add_osint_params()
        elif scanner_name == "Brute Force":
            self.add_brute_params()
        elif scanner_name == "Attack/Stress":
            self.add_attack_params()
        elif scanner_name == "Threat Intelligence":
            self.add_threat_params()
    
    def add_network_params(self):
        """Add network scanner parameters"""
        from PySide6.QtWidgets import QSpinBox, QCheckBox, QLineEdit
        
        # Port range
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        
        self.start_port = QSpinBox()
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        self.start_port.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        port_layout.addWidget(self.start_port)
        
        port_layout.addWidget(QLabel("to"))
        
        self.end_port = QSpinBox()
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1000)
        self.end_port.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        port_layout.addWidget(self.end_port)
        
        port_layout.addStretch()
        self.params_layout.addLayout(port_layout)
        
        # Scan type
        self.tcp_scan = QCheckBox("TCP Scan")
        self.tcp_scan.setChecked(True)
        self.tcp_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.tcp_scan)
        
        self.arp_scan = QCheckBox("ARP Discovery")
        self.arp_scan.setChecked(True)
        self.arp_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.arp_scan)
    
    def add_web_params(self):
        """Add web scanner parameters"""
        from PySide6.QtWidgets import QSpinBox, QCheckBox, QLineEdit
        
        # Maximum pages
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Max Pages:"))
        
        self.max_pages = QSpinBox()
        self.max_pages.setRange(1, 1000)
        self.max_pages.setValue(50)
        self.max_pages.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        pages_layout.addWidget(self.max_pages)
        pages_layout.addStretch()
        self.params_layout.addLayout(pages_layout)
        
        # Scan types
        self.xss_scan = QCheckBox("XSS Scan")
        self.xss_scan.setChecked(True)
        self.xss_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.xss_scan)
        
        self.sqli_scan = QCheckBox("SQL Injection Scan")
        self.sqli_scan.setChecked(True)
        self.sqli_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.sqli_scan)
    
    def add_osint_params(self):
        """Add OSINT scanner parameters"""
        from PySide6.QtWidgets import QCheckBox, QLineEdit
        
        # OSINT types
        self.whois_scan = QCheckBox("WHOIS Lookup")
        self.whois_scan.setChecked(True)
        self.whois_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.whois_scan)
        
        self.dns_scan = QCheckBox("DNS Enumeration")
        self.dns_scan.setChecked(True)
        self.dns_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.dns_scan)
        
        self.shodan_scan = QCheckBox("Shodan Search")
        self.shodan_scan.setChecked(False)
        self.shodan_scan.setStyleSheet("""
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
        self.params_layout.addWidget(self.shodan_scan)
    
    def add_brute_params(self):
        """Add brute force parameters"""
        from PySide6.QtWidgets import QSpinBox, QLineEdit
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username or leave blank for wordlist")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        username_layout.addWidget(self.username_input)
        username_layout.addStretch()
        self.params_layout.addLayout(username_layout)
        
        # Thread count
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Threads:"))
        
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 50)
        self.thread_count.setValue(5)
        self.thread_count.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        threads_layout.addWidget(self.thread_count)
        threads_layout.addStretch()
        self.params_layout.addLayout(threads_layout)
    
    def add_attack_params(self):
        """Add attack/stress parameters"""
        from PySide6.QtWidgets import QSpinBox, QCheckBox
        
        # Attack type
        self.arp_spoof = QCheckBox("ARP Spoofing")
        self.arp_spoof.setChecked(False)
        self.arp_spoof.setStyleSheet("""
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
                background-color: #f44336;
                border-color: #f44336;
            }
        """)
        self.params_layout.addWidget(self.arp_spoof)
        
        self.syn_flood = QCheckBox("SYN Flood")
        self.syn_flood.setChecked(False)
        self.syn_flood.setStyleSheet("""
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
                background-color: #f44336;
                border-color: #f44336;
            }
        """)
        self.params_layout.addWidget(self.syn_flood)
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        
        self.attack_duration = QSpinBox()
        self.attack_duration.setRange(1, 300)
        self.attack_duration.setValue(30)
        self.attack_duration.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        duration_layout.addWidget(self.attack_duration)
        duration_layout.addStretch()
        self.params_layout.addLayout(duration_layout)
    
    def add_threat_params(self):
        """Add threat intelligence parameters"""
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        
        # Intelligence sources
        self.cve_feed = QCheckBox("CVE Feed")
        self.cve_feed.setChecked(True)
        self.cve_feed.setStyleSheet("""
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
        self.params_layout.addWidget(self.cve_feed)
        
        self.exploitdb = QCheckBox("ExploitDB")
        self.exploitdb.setChecked(True)
        self.exploitdb.setStyleSheet("""
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
        self.params_layout.addWidget(self.exploitdb)
        
        # Days to look back
        days_layout = QHBoxLayout()
        days_layout.addWidget(QLabel("Days to look back:"))
        
        self.threat_days = QSpinBox()
        self.threat_days.setRange(1, 365)
        self.threat_days.setValue(30)
        self.threat_days.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
            }
        """)
        days_layout.addWidget(self.threat_days)
        days_layout.addStretch()
        self.params_layout.addLayout(days_layout)
    
    @Slot()
    def start_scanner(self):
        """Start selected scanner"""
        if self.target_combo.currentIndex() < 0:
            return
        
        target_value = self.target_combo.currentData()
        scanner_name = self.scanner_combo.currentText()
        
        # Get scanner parameters
        params = self.get_scanner_parameters()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.output_text.clear()
        
        # Emit signal
        self.scanner_started.emit(scanner_name, target_value)
        
        # Log start
        self.output_text.append(f"🚀 Starting {scanner_name} on {target_value}")
        self.output_text.append(f"Parameters: {params}")
        
        # Simulate scanner execution (replace with actual scanner logic)
        self.simulate_scanner(scanner_name, target_value, params)
    
    @Slot()
    def stop_scanner(self):
        """Stop current scanner"""
        self.current_scanner = None
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.output_text.append("⏹️ Scanner stopped")
    
    def get_scanner_parameters(self):
        """Get current scanner parameters"""
        params = {}
        
        scanner_name = self.scanner_combo.currentText()
        
        if scanner_name == "Network Scanner":
            params['start_port'] = self.start_port.value()
            params['end_port'] = self.end_port.value()
            params['tcp_scan'] = self.tcp_scan.isChecked()
            params['arp_scan'] = self.arp_scan.isChecked()
        
        elif scanner_name == "Web Scanner":
            params['max_pages'] = self.max_pages.value()
            params['xss_scan'] = self.xss_scan.isChecked()
            params['sqli_scan'] = self.sqli_scan.isChecked()
        
        elif scanner_name == "OSINT Scanner":
            params['whois_scan'] = self.whois_scan.isChecked()
            params['dns_scan'] = self.dns_scan.isChecked()
            params['shodan_scan'] = self.shodan_scan.isChecked()
        
        elif scanner_name == "Brute Force":
            params['username'] = self.username_input.text()
            params['threads'] = self.thread_count.value()
        
        elif scanner_name == "Attack/Stress":
            params['arp_spoof'] = self.arp_spoof.isChecked()
            params['syn_flood'] = self.syn_flood.isChecked()
            params['duration'] = self.attack_duration.value()
        
        elif scanner_name == "Threat Intelligence":
            params['cve_feed'] = self.cve_feed.isChecked()
            params['exploitdb'] = self.exploitdb.isChecked()
            params['days'] = self.threat_days.value()
        
        return params
    
    def simulate_scanner(self, scanner_name, target, params):
        """Simulate scanner execution (replace with actual logic)"""
        self.current_scanner = scanner_name
        
        # Simulate progress
        progress = 0
        self.progress_timer = QTimer()
        
        def update_progress():
            nonlocal progress
            progress += 10
            self.progress_bar.setValue(progress)
            self.output_text.append(f"Progress: {progress}%")
            
            if progress >= 100:
                self.progress_timer.stop()
                self.complete_scanner(scanner_name, target)
        
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(500)
    
    def complete_scanner(self, scanner_name, target):
        """Complete scanner execution"""
        # Generate mock results
        results = {
            'scanner': scanner_name,
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [
                {
                    'type': 'Information',
                    'severity': 'Low',
                    'description': f'Sample vulnerability found during {scanner_name}',
                    'target': target
                }
            ],
            'summary': f'{scanner_name} completed successfully'
        }
        
        # Update results table
        self.add_results(results['vulnerabilities'])
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.output_text.append(f"✅ {scanner_name} completed successfully")
        
        # Emit signal
        self.scanner_finished.emit(scanner_name, results)
    
    def add_results(self, vulnerabilities):
        """Add vulnerabilities to results table"""
        self.results_table.setRowCount(0)
        
        for row, vuln in enumerate(vulnerabilities):
            self.results_table.insertRow(row)
            
            # Type
            type_item = QTableWidgetItem(vuln.get('type', 'Unknown'))
            self.results_table.setItem(row, 0, type_item)
            
            # Severity
            severity_item = QTableWidgetItem(vuln.get('severity', 'Unknown'))
            self.results_table.setItem(row, 1, severity_item)
            
            # Description
            desc_item = QTableWidgetItem(vuln.get('description', ''))
            self.results_table.setItem(row, 2, desc_item)
            
            # Target
            target_item = QTableWidgetItem(vuln.get('target', ''))
            self.results_table.setItem(row, 3, target_item)
    
    @Slot(str, str)
    def start_scanner(self, scanner_type, target_value):
        """Start scanner from external request"""
        # Find scanner in combo box
        index = self.scanner_combo.findText(scanner_type)
        if index >= 0:
            self.scanner_combo.setCurrentIndex(index)
        
        # Find target in combo box
        for i in range(self.target_combo.count()):
            if self.target_combo.itemData(i) == target_value:
                self.target_combo.setCurrentIndex(i)
                break
        
        # Start scanner
        self.start_scanner()
    
    def stop_all_scanners(self):
        """Stop all running scanners"""
        if self.current_scanner:
            self.stop_scanner()
