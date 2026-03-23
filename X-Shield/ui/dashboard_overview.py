"""
Dashboard Overview Page for X-Shield Framework
Statistics and overview with Material Design
"""

from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QScrollArea, QProgressBar, QSizePolicy, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont
from core.target_store import TargetStore
from ui.styles import Colors, Spacing, Typography


class StatCard(QFrame):
    """Statistics card with Material Design"""
    
    def __init__(self, title, value, color, icon="📊"):
        super().__init__()
        self.setup_ui(title, value, color, icon)
    
    def setup_ui(self, title, value, color, icon):
        """Setup stat card UI with modern minimal style"""
        self.setObjectName("card")
        self.setMinimumWidth(180)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QFrame#card:hover {{
                border-color: {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.SM)

        # Header (Icon + Title)
        header = QHBoxLayout()
        header.setSpacing(Spacing.MD)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        header.addWidget(icon_label)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px; letter-spacing: 0.05em;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont(Typography.FAMILY_MONO, 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        layout.addStretch()
    
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
        """Setup dashboard overview UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Section Title
        header = QLabel("Global Dashboard")
        header.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H2_SIZE};")
        layout.addWidget(header)
        
        # Statistics cards
        self.setup_stats_cards(layout)
        
        # Recent activity and Quick Actions row
        content_row = QHBoxLayout()
        content_row.setSpacing(Spacing.XL)
        
        self.setup_recent_activity(content_row)
        self.setup_quick_actions(content_row)

        layout.addLayout(content_row)
        layout.addStretch()
    
    def setup_stats_cards(self, parent_layout):
        """Setup statistics cards"""
        cards_frame = QFrame()
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(Spacing.LG)
        
        # Create stat cards
        self.targets_card = StatCard("Active Targets", 0, Colors.PRIMARY, "🎯")
        self.scans_card = StatCard("Total Scans", 0, Colors.SUCCESS, "🔍")
        self.vulns_card = StatCard("Vulnerabilities", 0, Colors.DANGER, "⚠️")
        self.score_card = StatCard("Security Score", "85", Colors.WARNING, "📊")
        
        cards_layout.addWidget(self.targets_card)
        cards_layout.addWidget(self.scans_card)
        cards_layout.addWidget(self.vulns_card)
        cards_layout.addWidget(self.score_card)
        cards_layout.addStretch()
        
        parent_layout.addWidget(cards_frame)
    
    def setup_recent_activity(self, parent_layout):
        """Setup recent activity section with modern minimal style"""
        activity_frame = QFrame()
        activity_frame.setObjectName("card")
        activity_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        activity_layout.setSpacing(Spacing.LG)
        
        # Title
        title = QLabel("Recent Activity")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        activity_layout.addWidget(title)
        
        # Activity list
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setMinimumHeight(200)
        self.activity_text.setStyleSheet(f"""
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
        self.activity_text.setText("No recent activity...")
        activity_layout.addWidget(self.activity_text)
        
        parent_layout.addWidget(activity_frame, 2)  # Stretch factor 2
    
    def setup_quick_actions(self, parent_layout):
        """Setup quick actions section with modern minimal style"""
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        actions_layout.setSpacing(Spacing.LG)
        
        # Title
        title = QLabel("Quick Actions")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        actions_layout.addWidget(title)
        
        # Action buttons stack
        buttons_stack = QVBoxLayout()
        buttons_stack.setSpacing(Spacing.MD)
        
        # Quick scan button
        quick_scan_btn = QPushButton("🚀 Launch Quick Scan")
        quick_scan_btn.setObjectName("primary_btn")
        buttons_stack.addWidget(quick_scan_btn)
        
        # Add target button
        add_target_btn = QPushButton("➕ Enroll New Target")
        buttons_stack.addWidget(add_target_btn)
        
        # Generate report button
        report_btn = QPushButton("📋 Generate New Audit")
        buttons_stack.addWidget(report_btn)
        
        buttons_stack.addStretch()
        actions_layout.addLayout(buttons_stack)
        
        parent_layout.addWidget(actions_frame, 1)  # Stretch factor 1
    
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
