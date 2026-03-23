"""
Dashboard Widget for X-Shield Framework
Provides overview of scan results and system status with comprehensive tabs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar, QScrollArea, QTabWidget,
    QListWidget, QListWidgetItem, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QLineEdit, QComboBox, QPushButton, QStyledItemDelegate
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QBrush, QColor, QPen
from ui.styles import Colors, Spacing, Typography


class StatusDelegate(QStyledItemDelegate):
    """Custom delegate for coloring status items"""
    
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        if index.column() == 2:  # Status column
            text = index.data()
            color = None
            
            if text == "Active":
                color = QColor("#10b981")
            elif text == "Scanned":
                color = QColor("#3b82f6")
            elif text == "Scanning":
                color = QColor("#f59e0b")
            elif text == "Queued":
                color = QColor("#6b7280")
            
            if color:
                painter.save()
                painter.setPen(QPen(color))
                painter.setBrush(QBrush(color))
                painter.setFont(QFont("Inter", 10, QFont.Bold))
                
                # Draw the text
                rect = option.rect
                painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
                painter.restore()


class DashboardWidget(QWidget):
    """Dashboard widget with comprehensive tabs for different aspects"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup dashboard UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_overview_tab()
        self.create_modules_tab()
        self.create_targets_tab()
        self.create_vulnerabilities_tab()
        self.create_network_tab()
        self.create_reports_tab()
        self.create_system_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_overview_tab(self):
        """Create overview tab with main statistics and modern design"""
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        overview_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        overview_layout.setSpacing(Spacing.XL)
        
        # Statistics cards
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(Spacing.LG)
        
        # Create stat cards
        self.scans_completed_card = self.create_stat_card("Scans Completed", "0", Colors.SUCCESS, "✓")
        stats_layout.addWidget(self.scans_completed_card, 0, 0)
        
        self.vulnerabilities_found_card = self.create_stat_card("Vulnerabilities", "0", Colors.DANGER, "⚠")
        stats_layout.addWidget(self.vulnerabilities_found_card, 0, 1)
        
        self.modules_active_card = self.create_stat_card("Active Modules", "0", Colors.WARNING, "⚙")
        stats_layout.addWidget(self.modules_active_card, 0, 2)
        
        self.risk_score_card = self.create_stat_card("Risk Score", "0", Colors.PRIMARY, "🛡")
        stats_layout.addWidget(self.risk_score_card, 1, 0)
        
        self.targets_scanned_card = self.create_stat_card("Targets", "0", Colors.INFO, "🎯")
        stats_layout.addWidget(self.targets_scanned_card, 1, 1)
        
        self.reports_generated_card = self.create_stat_card("Reports", "0", Colors.SUCCESS, "📄")
        stats_layout.addWidget(self.reports_generated_card, 1, 2)
        
        overview_layout.addWidget(stats_frame)
        overview_layout.addStretch()
        
        self.tab_widget.addTab(overview_widget, "Overview")
    
    def create_modules_tab(self):
        """Create modules tab with module status and controls"""
        modules_widget = QWidget()
        modules_layout = QHBoxLayout(modules_widget)
        
        # Left side - Module list
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        
        modules_title = QLabel("Available Modules")
        modules_title.setFont(QFont("Inter", 16, QFont.Bold))
        modules_title.setStyleSheet("color: #8b5cf6;")
        left_layout.addWidget(modules_title)
        
        self.modules_list = QListWidget()
        self.modules_list.setStyleSheet("""
            QListWidget {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
                background-color: #4b5563;
                color: #e5e7eb;
            }
            QListWidget::item:hover {
                background-color: #6b7280;
            }
        """)
        
        # Add sample modules
        sample_modules = [
            "Network Scanner - ARP/TCP scanning",
            "Web Scanner - XSS/SQLi detection",
            "Brute Force - Password cracking",
            "Exploitation - Payload execution",
            "OSINT - Open source intelligence",
            "MITM - Man-in-the-middle attacks",
            "DoS Testing - Stress testing",
            "Threat Intel - CVE feeds"
        ]
        
        for module in sample_modules:
            item = QListWidgetItem(module)
            self.modules_list.addItem(item)
        
        left_layout.addWidget(self.modules_list)
        
        # Right side - Module status
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        
        status_title = QLabel("Module Status")
        status_title.setFont(QFont("Inter", 16, QFont.Bold))
        status_title.setStyleSheet("color: #8b5cf6;")
        right_layout.addWidget(status_title)
        
        self.module_status_text = QTextEdit()
        self.module_status_text.setMaximumHeight(200)
        self.module_status_text.setReadOnly(True)
        self.module_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.module_status_text.setText("No modules currently running")
        right_layout.addWidget(self.module_status_text)
        
        # Module controls
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        
        self.start_module_btn = QLabel("🚀 Start Module")
        self.start_module_btn.setStyleSheet("""
            QLabel {
                background-color: #10b981;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                text-align: center;
            }
        """)
        controls_layout.addWidget(self.start_module_btn)
        
        self.stop_module_btn = QLabel("🛑 Stop Module")
        self.stop_module_btn.setStyleSheet("""
            QLabel {
                background-color: #ef4444;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                text-align: center;
            }
        """)
        controls_layout.addWidget(self.stop_module_btn)
        
        right_layout.addWidget(controls_frame)
        right_layout.addStretch()
        
        modules_layout.addWidget(left_frame)
        modules_layout.addWidget(right_frame)
        
        self.tab_widget.addTab(modules_widget, "🔧 Modules")
    
    def create_targets_tab(self):
        """Create targets tab with target management"""
        targets_widget = QWidget()
        targets_layout = QVBoxLayout(targets_widget)
        
        # Target input section
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        
        input_title = QLabel("Target Management")
        input_title.setFont(QFont("Inter", 16, QFont.Bold))
        input_title.setStyleSheet("color: #8b5cf6;")
        input_layout.addWidget(input_title)
        
        # Quick add target section
        quick_add_frame = QFrame()
        quick_add_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1f2937, stop:1 #374151);
                border-radius: 12px;
                padding: 20px;
                border: 2px solid #374151;
                margin: 8px;
            }
        """)
        quick_add_layout = QHBoxLayout(quick_add_frame)
        quick_add_layout.setSpacing(16)
        
        target_label = QLabel("Add Target:")
        target_label.setStyleSheet("""
            color: #e5e7eb; 
            font-weight: bold; 
            font-size: 15px;
            margin-right: 16px;
        """)
        quick_add_layout.addWidget(target_label)
        
        self.target_input = QLineEdit()
        self.target_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                color: #e5e7eb;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #8b5cf6;
                background-color: #4b5563;
            }
        """)
        self.target_input.setPlaceholderText("Enter IP, domain, or URL...")
        quick_add_layout.addWidget(self.target_input)
        
        # Target type dropdown
        self.target_type_combo = QComboBox()
        self.target_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #374151;
                color: #e5e7eb;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                min-width: 140px;
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
        self.target_type_combo.addItems(["Network", "Web", "Range", "Custom"])
        quick_add_layout.addWidget(self.target_type_combo)
        
        # Add button
        self.add_target_btn = QPushButton("➕ Add Target")
        self.add_target_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin-left: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #059669, stop:1 #047857);

            }
            QPushButton:pressed {
                background: #047857;
            }
        """)
        quick_add_layout.addWidget(self.add_target_btn)
        
        quick_add_layout.addStretch()
        input_layout.addWidget(quick_add_frame)
        
        # Quick target templates
        templates_frame = QFrame()
        templates_layout = QHBoxLayout(templates_frame)
        
        templates_label = QLabel("Quick Templates:")
        templates_label.setStyleSheet("color: #9ca3af; font-size: 12px; margin-right: 10px;")
        templates_layout.addWidget(templates_label)
        
        # Quick template buttons
        self.local_network_btn = QPushButton("🏠 Local Network")
        self.local_network_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #6b7280;
            }
        """)
        templates_layout.addWidget(self.local_network_btn)
        
        self.web_app_btn = QPushButton("🌐 Web App")
        self.web_app_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #6b7280;
            }
        """)
        templates_layout.addWidget(self.web_app_btn)
        
        self.range_scan_btn = QPushButton("📡 Range Scan")
        self.range_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #6b7280;
            }
        """)
        templates_layout.addWidget(self.range_scan_btn)
        
        templates_layout.addStretch()
        input_layout.addWidget(templates_frame)
        
        # Target list
        targets_list_frame = QFrame()
        targets_list_layout = QVBoxLayout(targets_list_frame)
        
        list_title = QLabel("Active Targets")
        list_title.setFont(QFont("Inter", 14, QFont.Bold))
        list_title.setStyleSheet("color: #8b5cf6; margin-bottom: 10px;")
        targets_list_layout.addWidget(list_title)
        
        # Create scrollable table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #374151;
                border-radius: 6px;
                background-color: #1f2937;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #1f2937;
            }
        """)
        
        self.targets_table = QTableWidget()
        self.targets_table.setColumnCount(5)
        self.targets_table.setHorizontalHeaderLabels(["Target", "Type", "Status", "Last Scan", "Actions"])
        self.targets_table.setStyleSheet("""
            QTableWidget {
                background-color: #374151;
                color: #e5e7eb;
                border: none;
                gridline-color: #4b5563;
                selection-background-color: #8b5cf6;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #4b5563;
            }
            QTableWidget::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
            QHeaderView::section {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        # Set column widths
        header = self.targets_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Target
        header.setSectionResizeMode(1, QHeaderView.Fixed)      # Type
        header.setSectionResizeMode(2, QHeaderView.Fixed)      # Status
        header.setSectionResizeMode(3, QHeaderView.Fixed)      # Last Scan
        header.setSectionResizeMode(4, QHeaderView.Stretch)     # Actions
        
        header.resizeSection(0, 250)
        header.resizeSection(1, 80)
        header.resizeSection(2, 100)
        header.resizeSection(3, 150)
        
        # Add sample targets
        sample_targets = [
            ["192.168.1.1", "Network", "Active", "2024-03-23 10:30", "🗑️ 🔄 📊"],
            ["https://example.com", "Web", "Scanned", "2024-03-23 09:15", "🗑️ 🔄 📊"],
            ["10.0.0.0/24", "Network", "Queued", "Never", "🗑️ ▶️ 📊"],
            ["192.168.1.0/28", "Network", "Scanning", "2024-03-23 08:00", "⏹️ 📊"]
        ]
        
        self.targets_table.setRowCount(len(sample_targets))
        for row, target_data in enumerate(sample_targets):
            for col, data in enumerate(target_data):
                item = QTableWidgetItem(data)
                # Store status info for coloring
                if col == 2:  # Status column
                    if data == "Active":
                        item.setData(Qt.UserRole, "#10b981")
                    elif data == "Scanned":
                        item.setData(Qt.UserRole, "#3b82f6")
                    elif data == "Scanning":
                        item.setData(Qt.UserRole, "#f59e0b")
                    elif data == "Queued":
                        item.setData(Qt.UserRole, "#6b7280")
                self.targets_table.setItem(row, col, item)
        
        # Set custom delegate for status column
        self.targets_table.setItemDelegateForColumn(2, StatusDelegate(self.targets_table))
        
        # Set row height and hide header
        self.targets_table.verticalHeader().setDefaultSectionSize(40)
        self.targets_table.verticalHeader().setVisible(False)
        
        scroll_area.setWidget(self.targets_table)
        targets_list_layout.addWidget(scroll_area)
        
        # Summary stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_targets_label = QLabel("📊 Total Targets: 4")
        self.total_targets_label.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(self.total_targets_label)
        
        stats_layout.addStretch()
        
        self.active_targets_label = QLabel("🟢 Active: 1")
        self.active_targets_label.setStyleSheet("color: #10b981; font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(self.active_targets_label)
        
        self.scanning_targets_label = QLabel("🟡 Scanning: 1")
        self.scanning_targets_label.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 14px; margin-left: 20px;")
        stats_layout.addWidget(self.scanning_targets_label)
        
        targets_list_layout.addWidget(stats_frame)
        targets_layout.addWidget(targets_list_frame)
        
        self.tab_widget.addTab(targets_widget, "🎯 Targets")
    
    def create_vulnerabilities_tab(self):
        """Create vulnerabilities tab with vulnerability management"""
        vulns_widget = QWidget()
        vulns_layout = QVBoxLayout(vulns_widget)
        
        # Vulnerabilities summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        vuln_title = QLabel("Vulnerability Assessment")
        vuln_title.setFont(QFont("Inter", 16, QFont.Bold))
        vuln_title.setStyleSheet("color: #8b5cf6;")
        summary_layout.addWidget(vuln_title)
        
        summary_layout.addStretch()
        
        # Severity distribution
        severity_layout = QHBoxLayout()
        
        critical_label = QLabel("🔴 Critical: 0")
        critical_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        severity_layout.addWidget(critical_label)
        
        high_label = QLabel("🟠 High: 0")
        high_label.setStyleSheet("color: #ea580c; font-weight: bold;")
        severity_layout.addWidget(high_label)
        
        medium_label = QLabel("🟡 Medium: 0")
        medium_label.setStyleSheet("color: #ca8a04; font-weight: bold;")
        severity_layout.addWidget(medium_label)
        
        low_label = QLabel("🟢 Low: 0")
        low_label.setStyleSheet("color: #16a34a; font-weight: bold;")
        severity_layout.addWidget(low_label)
        
        summary_layout.addLayout(severity_layout)
        vulns_layout.addWidget(summary_frame)
        
        # Vulnerabilities list
        self.vulns_table = QTableWidget()
        self.vulns_table.setColumnCount(5)
        self.vulns_table.setHorizontalHeaderLabels(["Title", "Severity", "Target", "Module", "Discovered"])
        self.vulns_table.setStyleSheet("""
            QTableWidget {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                gridline-color: #4b5563;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Set column widths
        header = self.vulns_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 250)
        header.resizeSection(1, 80)
        header.resizeSection(2, 150)
        header.resizeSection(3, 100)
        
        # Add sample vulnerabilities
        sample_vulns = [
            ["SQL Injection in login form", "High", "https://example.com", "Web Scanner", "2024-03-23 10:30"],
            ["Open FTP port 21", "Medium", "192.168.1.1", "Network Scanner", "2024-03-23 09:15"],
            ["Weak SSL Configuration", "Low", "https://test.com", "Web Scanner", "2024-03-23 08:45"]
        ]
        
        self.vulns_table.setRowCount(len(sample_vulns))
        for row, vuln_data in enumerate(sample_vulns):
            for col, data in enumerate(vuln_data):
                item = QTableWidgetItem(data)
                self.vulns_table.setItem(row, col, item)
        
        vulns_layout.addWidget(self.vulns_table)
        
        self.tab_widget.addTab(vulns_widget, "⚠️ Vulnerabilities")
    
    def create_network_tab(self):
        """Create network tab with network status and topology"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)
        
        # Network status
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        
        network_title = QLabel("Network Status")
        network_title.setFont(QFont("Inter", 16, QFont.Bold))
        network_title.setStyleSheet("color: #8b5cf6;")
        status_layout.addWidget(network_title)
        
        # Network stats
        stats_grid = QGridLayout()
        
        self.interfaces_label = self.create_status_item("Network Interfaces", "eth0, wlan0")
        stats_grid.addWidget(self.interfaces_label, 0, 0)
        
        self.traffic_label = self.create_status_item("Network Traffic", "1.2 MB/s")
        stats_grid.addWidget(self.traffic_label, 0, 1)
        
        self.connections_label = self.create_status_item("Active Connections", "24")
        stats_grid.addWidget(self.connections_label, 1, 0)
        
        self.packets_label = self.create_status_item("Packets Captured", "1,247")
        stats_grid.addWidget(self.packets_label, 1, 1)
        
        status_layout.addLayout(stats_grid)
        network_layout.addWidget(status_frame)
        
        # Network activity log
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("Network Activity")
        activity_title.setFont(QFont("Inter", 14, QFont.Bold))
        activity_title.setStyleSheet("color: #8b5cf6;")
        activity_layout.addWidget(activity_title)
        
        self.network_log = QTextEdit()
        self.network_log.setMaximumHeight(150)
        self.network_log.setReadOnly(True)
        self.network_log.setStyleSheet("""
            QTextEdit {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.network_log.setText("[10:30:15] ARP Request: 192.168.1.1 → 192.168.1.255\n"
                              "[10:30:16] TCP SYN: 192.168.1.100:12345 → 8.8.8.8:53\n"
                              "[10:30:17] ICMP Echo: 192.168.1.1 → 192.168.1.100")
        
        activity_layout.addWidget(self.network_log)
        network_layout.addWidget(activity_frame)
        
        self.tab_widget.addTab(network_widget, "🌐 Network")
    
    def create_reports_tab(self):
        """Create reports tab with report management"""
        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)
        
        # Reports header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        reports_title = QLabel("Report Management")
        reports_title.setFont(QFont("Inter", 16, QFont.Bold))
        reports_title.setStyleSheet("color: #8b5cf6;")
        header_layout.addWidget(reports_title)
        
        header_layout.addStretch()
        
        generate_btn = QLabel("📊 Generate Report")
        generate_btn.setStyleSheet("""
            QLabel {
                background-color: #8b5cf6;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(generate_btn)
        
        reports_layout.addWidget(header_frame)
        
        # Reports list
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels(["Report Name", "Date", "Type", "Size"])
        self.reports_table.setStyleSheet("""
            QTableWidget {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                gridline-color: #4b5563;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #4b5563;
                color: #e5e7eb;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Set column widths
        header = self.reports_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 200)
        header.resizeSection(1, 120)
        header.resizeSection(2, 100)
        
        # Add sample reports
        sample_reports = [
            ["Network Scan Report", "2024-03-23 10:30", "Network", "2.4 MB"],
            ["Web Vulnerability Assessment", "2024-03-23 09:15", "Web", "1.8 MB"],
            ["Comprehensive Security Audit", "2024-03-22 16:45", "Full", "5.2 MB"]
        ]
        
        self.reports_table.setRowCount(len(sample_reports))
        for row, report_data in enumerate(sample_reports):
            for col, data in enumerate(report_data):
                item = QTableWidgetItem(data)
                self.reports_table.setItem(row, col, item)
        
        reports_layout.addWidget(self.reports_table)
        
        self.tab_widget.addTab(reports_widget, "📄 Reports")
    
    def create_system_tab(self):
        """Create system tab with system monitoring"""
        system_widget = QWidget()
        system_layout = QVBoxLayout(system_widget)
        
        # System resources
        resources_frame = QFrame()
        resources_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        resources_layout = QVBoxLayout(resources_frame)
        
        system_title = QLabel("System Resources")
        system_title.setFont(QFont("Inter", 16, QFont.Bold))
        system_title.setStyleSheet("color: #8b5cf6;")
        resources_layout.addWidget(system_title)
        
        # Resource meters
        resources_grid = QGridLayout()
        
        # CPU
        cpu_label = QLabel("CPU Usage")
        cpu_label.setStyleSheet("color: #e5e7eb; font-weight: bold;")
        resources_grid.addWidget(cpu_label, 0, 0)
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4b5563;
                border-radius: 6px;
                text-align: center;
                color: #e5e7eb;
                background-color: #374151;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 4px;
            }
        """)
        self.cpu_progress.setValue(35)
        resources_grid.addWidget(self.cpu_progress, 0, 1)
        
        # Memory
        memory_label = QLabel("Memory Usage")
        memory_label.setStyleSheet("color: #e5e7eb; font-weight: bold;")
        resources_grid.addWidget(memory_label, 1, 0)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4b5563;
                border-radius: 6px;
                text-align: center;
                color: #e5e7eb;
                background-color: #374151;
            }
            QProgressBar::chunk {
                background-color: #f59e0b;
                border-radius: 4px;
            }
        """)
        self.memory_progress.setValue(62)
        resources_grid.addWidget(self.memory_progress, 1, 1)
        
        # Disk
        disk_label = QLabel("Disk Usage")
        disk_label.setStyleSheet("color: #e5e7eb; font-weight: bold;")
        resources_grid.addWidget(disk_label, 2, 0)
        
        self.disk_progress = QProgressBar()
        self.disk_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4b5563;
                border-radius: 6px;
                text-align: center;
                color: #e5e7eb;
                background-color: #374151;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 4px;
            }
        """)
        self.disk_progress.setValue(45)
        resources_grid.addWidget(self.disk_progress, 2, 1)
        
        resources_layout.addLayout(resources_grid)
        system_layout.addWidget(resources_frame)
        
        # System information
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #374151;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("System Information")
        info_title.setFont(QFont("Inter", 14, QFont.Bold))
        info_title.setStyleSheet("color: #8b5cf6;")
        info_layout.addWidget(info_title)
        
        self.system_info = QTextEdit()
        self.system_info.setMaximumHeight(120)
        self.system_info.setReadOnly(True)
        self.system_info.setStyleSheet("""
            QTextEdit {
                background-color: #374151;
                color: #e5e7eb;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.system_info.setText("OS: Windows 10\n"
                              "Python: 3.10.0\n"
                              "X-Shield: v1.0.0\n"
                              "Uptime: 2h 34m\n"
                              "User: Administrator")
        
        info_layout.addWidget(self.system_info)
        system_layout.addWidget(info_frame)
        
        self.tab_widget.addTab(system_widget, "⚙️ System")
    
    def create_stat_card(self, title, value, color, icon):
        """Create a single statistics card with modern minimal style"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(120)
        card.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-color: {color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        card_layout.setSpacing(Spacing.SM)
        
        header = QHBoxLayout()
        header.setSpacing(Spacing.MD)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        header.addWidget(icon_label)
        
        title_label = QLabel(title.upper())
        title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px; letter-spacing: 0.05em;")
        header.addWidget(title_label)
        header.addStretch()
        card_layout.addLayout(header)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont(Typography.FAMILY_MONO, 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        card_layout.addWidget(value_label)
        
        card.value_label = value_label
        return card
    
    def create_status_item(self, label_text, value_text):
        """Create a single status item with design system style"""
        item_frame = QFrame()
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(0, Spacing.XS, 0, Spacing.XS)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        item_layout.addWidget(label)
        
        item_layout.addStretch()
        
        value = QLabel(value_text)
        value.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 600; font-family: {Typography.FAMILY_MONO};")
        item_layout.addWidget(value)
        
        item_frame.value_label = value
        return item_frame
    
    def setup_timer(self):
        """Setup update timer for dashboard"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def update_dashboard(self):
        """Update dashboard with current data"""
        # This would be connected to actual data from modules
        # For now, just update system status
        self.update_system_status()
    
    def update_system_status(self):
        """Update system status information"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_progress.setValue(int(cpu_percent))
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.setValue(int(memory_percent))
            
            # Network status (simplified)
            self.connections_label.value_label.setText(f"{len(psutil.net_connections())}")
            
        except ImportError:
            # psutil not available, use placeholder values
            pass
    
    def update_stats(self, stats_data):
        """Update statistics cards with new data"""
        if 'scans_completed' in stats_data:
            self.scans_completed_card.value_label.setText(str(stats_data['scans_completed']))
        
        if 'vulnerabilities_found' in stats_data:
            self.vulnerabilities_found_card.value_label.setText(str(stats_data['vulnerabilities_found']))
        
        if 'modules_active' in stats_data:
            self.modules_active_card.value_label.setText(str(stats_data['modules_active']))
        
        if 'risk_score' in stats_data:
            self.risk_score_card.value_label.setText(str(stats_data['risk_score']))
        
        if 'targets_scanned' in stats_data:
            self.targets_scanned_card.value_label.setText(str(stats_data['targets_scanned']))
        
        if 'reports_generated' in stats_data:
            self.reports_generated_card.value_label.setText(str(stats_data['reports_generated']))
    
    def add_activity_item(self, activity_text, activity_type="info"):
        """Add an item to recent activity"""
        # This would update the activity log
        pass
    
    def reset(self):
        """Reset dashboard to initial state"""
        # Reset stats
        self.update_stats({
            'scans_completed': 0,
            'vulnerabilities_found': 0,
            'modules_active': 0,
            'risk_score': 0,
            'targets_scanned': 0,
            'reports_generated': 0
        })
        
        # Clear tables and logs
        self.module_status_text.setText("No modules currently running")
        self.network_log.clear()
