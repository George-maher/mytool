"""
Dashboard Overview Page for X-Shield Framework
Statistics and overview with Material Design
"""

from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QScrollArea, QProgressBar, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont
from core.target_store import TargetStore


class StatCard(QFrame):
    """Statistics card with Material Design"""
    
    def __init__(self, title, value, color, icon="📊"):
        super().__init__()
        self.setup_ui(title, value, color, icon)
    
    def setup_ui(self, title, value, color, icon):
        """Setup stat card UI"""
        self.setFixedSize(150, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e1e;
                border: 2px solid {color};
                border-radius: 12px;
                margin: 5px;
            }}
            QFrame:hover {{
                background-color: #2d2d2d;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Roboto", 28, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Roboto", 12))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(title_label)
    
    def update_value(self, value):
        """Update card value"""
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.font().bold():
                widget.setText(str(value))


class DashboardOverview(QWidget):
    """Dashboard overview page with statistics"""
    
    def __init__(self, target_store: TargetStore):
        super().__init__()
        self.target_store = target_store
        self.scan_results = []
        self.setup_ui()
        self.setup_connections()
        self.refresh_stats()
    
    def setup_ui(self):
        """Setup dashboard overview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard Overview")
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        header.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Statistics cards
        self.setup_stats_cards(layout)
        
        # Recent activity
        self.setup_recent_activity(layout)
        
        # Quick actions
        self.setup_quick_actions(layout)
    
    def setup_stats_cards(self, parent_layout):
        """Setup statistics cards"""
        cards_frame = QFrame()
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setSpacing(10)
        
        # Create stat cards
        self.targets_card = StatCard("Active Targets", 0, "#2196F3", "🎯")
        self.scans_card = StatCard("Total Scans", 0, "#4CAF50", "🔍")
        self.vulns_card = StatCard("Vulnerabilities", 0, "#f44336", "⚠️")
        self.score_card = StatCard("Security Score", "85", "#FF9800", "📊")
        
        cards_layout.addWidget(self.targets_card)
        cards_layout.addWidget(self.scans_card)
        cards_layout.addWidget(self.vulns_card)
        cards_layout.addWidget(self.score_card)
        cards_layout.addStretch()
        
        parent_layout.addWidget(cards_frame)
    
    def setup_recent_activity(self, parent_layout):
        """Setup recent activity section"""
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        activity_layout = QVBoxLayout(activity_frame)
        
        # Title
        title = QLabel("Recent Activity")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        activity_layout.addWidget(title)
        
        # Activity list
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setMaximumHeight(200)
        self.activity_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #c9d1d9;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.activity_text.setText("No recent activity...")
        activity_layout.addWidget(self.activity_text)
        
        parent_layout.addWidget(activity_frame)
    
    def setup_quick_actions(self, parent_layout):
        """Setup quick actions section"""
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        actions_layout = QVBoxLayout(actions_frame)
        
        # Title
        title = QLabel("Quick Actions")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        actions_layout.addWidget(title)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        from PySide6.QtWidgets import QPushButton
        
        # Quick scan button
        quick_scan_btn = QPushButton("🚀 Quick Scan")
        quick_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        buttons_layout.addWidget(quick_scan_btn)
        
        # Add target button
        add_target_btn = QPushButton("➕ Add Target")
        add_target_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(add_target_btn)
        
        # Generate report button
        report_btn = QPushButton("📋 Generate Report")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        buttons_layout.addWidget(report_btn)
        
        buttons_layout.addStretch()
        actions_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(actions_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Target store signals
        self.target_store.targets_updated.connect(self.refresh_stats)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_stats)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    @Slot()
    def refresh_stats(self):
        """Refresh dashboard statistics"""
        # Update target count
        target_count = self.target_store.get_target_count()
        self.targets_card.update_value(target_count)
        
        # Update scan count
        scan_count = len(self.scan_results)
        self.scans_card.update_value(scan_count)
        
        # Update vulnerability count
        vuln_count = sum(len(result.get('vulnerabilities', [])) for result in self.scan_results)
        self.vulns_card.update_value(vuln_count)
        
        # Update security score (simplified calculation)
        if target_count > 0:
            score = max(0, 100 - (vuln_count * 5))
            self.score_card.update_value(f"{score}")
        else:
            self.score_card.update_value("N/A")
        
        # Update recent activity
        self.update_recent_activity()
    
    def update_recent_activity(self):
        """Update recent activity display"""
        activities = []
        
        # Add target activities
        targets = self.target_store.get_all_targets()
        recent_targets = sorted(targets, key=lambda t: t.created_at, reverse=True)[:5]
        
        for target in recent_targets:
            activities.append(f"[{target.created_at[:19]}] Added target: {target.name}")
        
        # Add scan activities
        recent_scans = sorted(self.scan_results, key=lambda s: s.get('timestamp', ''), reverse=True)[:5]
        
        for scan in recent_scans:
            timestamp = scan.get('timestamp', datetime.now().isoformat())[:19]
            scanner = scan.get('scanner', 'Unknown')
            target = scan.get('target', 'Unknown')
            vuln_count = len(scan.get('vulnerabilities', []))
            activities.append(f"[{timestamp}] {scanner} scan on {target} - {vuln_count} issues")
        
        # Update display
        if activities:
            activity_text = "\n".join(activities)
        else:
            activity_text = "No recent activity..."
        
        self.activity_text.setText(activity_text)
    
    @Slot(str, dict)
    def add_scan_result(self, scanner_name, results):
        """Add scan result to dashboard"""
        scan_data = {
            'scanner': scanner_name,
            'target': results.get('target', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': results.get('vulnerabilities', []),
            'summary': results.get('summary', '')
        }
        
        self.scan_results.append(scan_data)
        
        # Keep only last 50 scans
        if len(self.scan_results) > 50:
            self.scan_results = self.scan_results[-50:]
        
        self.refresh_stats()
    
    def get_statistics(self):
        """Get dashboard statistics"""
        target_count = self.target_store.get_target_count()
        scan_count = len(self.scan_results)
        vuln_count = sum(len(result.get('vulnerabilities', [])) for result in self.scan_results)
        
        if target_count > 0:
            score = max(0, 100 - (vuln_count * 5))
        else:
            score = 0
        
        return {
            'targets': target_count,
            'scans': scan_count,
            'vulnerabilities': vuln_count,
            'security_score': score
        }
