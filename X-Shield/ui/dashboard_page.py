"""
Dashboard Page for X-Shield MVC Architecture
Visual overview with status cards and recent activity
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QScrollArea, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont
from ui.styles import Colors, Spacing, Typography


class StatusCard(QFrame):
    """Status card widget for dashboard with Modern Minimal aesthetic"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 color: str = Colors.PRIMARY, icon: str = "📊"):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(120)
        self.setup_ui(title, value, subtitle, color, icon)
    
    def setup_ui(self, title, value, subtitle, color, icon):
        """Setup card UI"""
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
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(Spacing.MD)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setFixedSize(20, 20)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title.upper())
        title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px; letter-spacing: 0.05em;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont(Typography.FAMILY_MONO, 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 10px; font-weight: 500;")
            layout.addWidget(subtitle_label)
    
    def update_value(self, value: str, subtitle: str = ""):
        """Update card values"""
        # Find and update value label
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.font().bold():
                widget.setText(value)
                if subtitle:
                    # Update subtitle if exists
                    for j in range(self.layout().count()):
                        sub_widget = self.layout().itemAt(j).widget()
                        if isinstance(sub_widget, QLabel) and not sub_widget.font().bold() and not sub_widget.font().pointSize() == 24:
                            sub_widget.setText(subtitle)
                            break
                break


class DashboardPage(QWidget):
    """Dashboard page with overview and statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        self.target_manager = parent.get_target_manager() if parent else None
        
        self.setup_ui()
        self.setup_connections()
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(3000)  # Update every 3 seconds
        
        # Initial update
        self.update_statistics()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Overview Section Title
        overview_title = QLabel("Overview")
        overview_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H2_SIZE};")
        layout.addWidget(overview_title)
        
        # Status Cards
        self.setup_status_cards(layout)
        
        # Recent Activity and System Health
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Recent Activity
        self.setup_recent_activity(content_layout)
        
        # System Health
        self.setup_system_health(content_layout)
        
        layout.addLayout(content_layout)
        
        layout.addStretch()
    
    def setup_status_cards(self, parent_layout):
        """Setup status cards grid"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(Spacing.LG)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create status cards
        self.cards = {}
        
        # Total Targets
        self.cards['targets'] = StatusCard("Targets", "0", "ACTIVE NODES", Colors.PRIMARY, "🎯")
        cards_layout.addWidget(self.cards['targets'], 0, 0)
        
        # Active Scans
        self.cards['scans'] = StatusCard("Threads", "0", "SCAN OPERATIONS", Colors.WARNING, "🔍")
        cards_layout.addWidget(self.cards['scans'], 0, 1)
        
        # Vulnerabilities Found
        self.cards['vulnerabilities'] = StatusCard("Breaches", "0", "THREAT FINDINGS", Colors.DANGER, "⚠️")
        cards_layout.addWidget(self.cards['vulnerabilities'], 0, 2)
        
        # System Health
        self.cards['health'] = StatusCard("Integrity", "100%", "CORE STATUS", Colors.SUCCESS, "💚")
        cards_layout.addWidget(self.cards['health'], 0, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def setup_recent_activity(self, parent_layout):
        """Setup recent activity section"""
        activity_frame = QFrame()
        activity_frame.setObjectName("card")
        activity_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        activity_layout.setSpacing(Spacing.LG)
        
        # Title
        title_label = QLabel("LIVE TELEMETRY")
        title_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: 600; font-size: 12px; letter-spacing: 0.05em;")
        activity_layout.addWidget(title_label)
        
        # Activity log
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(300)
        self.activity_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                color: {Colors.TEXT_PRIMARY};
                font-family: {Typography.FAMILY_MONO};
                font-size: 11px;
                padding: {Spacing.MD}px;
            }}
        """)
        
        # Add initial log entries
        self.add_activity_entry("System", "X-Shield Framework initialized", "system")
        self.add_activity_entry("Target Manager", "Ready to manage targets", "info")
        
        activity_layout.addWidget(self.activity_log)
        
        parent_layout.addWidget(activity_frame)
    
    def setup_system_health(self, parent_layout):
        """Setup system health section"""
        health_frame = QFrame()
        health_frame.setObjectName("card")
        health_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        health_layout = QVBoxLayout(health_frame)
        health_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        health_layout.setSpacing(Spacing.LG)
        
        # Title
        title_label = QLabel("SYSTEM HEALTH")
        title_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: 600; font-size: 12px; letter-spacing: 0.05em;")
        health_layout.addWidget(title_label)
        
        # Health indicators
        self.health_indicators = {}
        
        indicators = [
            ("CPU LOAD", "15%", Colors.SUCCESS),
            ("MEMORY ADDR", "42%", Colors.PRIMARY),
            ("STORAGE", "78%", Colors.WARNING),
            ("UPLINK", "ACTIVE", Colors.SUCCESS)
        ]
        
        for label_text, value, color in indicators:
            indicator_layout = QHBoxLayout()
            
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 10px; font-weight: 600;")
            indicator_layout.addWidget(label)
            
            indicator_layout.addStretch()
            
            if "%" in value:
                # Progress bar for percentage values
                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(int(value.replace("%", "")))
                progress.setFixedWidth(120)
                progress.setFixedHeight(6)
                progress.setTextVisible(False)
                progress.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Colors.BACKGROUND};
                        border: 1px solid {Colors.BORDER};
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 2px;
                    }}
                """)
                indicator_layout.addWidget(progress)
                self.health_indicators[label_text] = progress
            else:
                # Label for status values
                value_label = QLabel(value)
                value_label.setStyleSheet(f"color: {color}; font-weight: 600; font-family: {Typography.FAMILY_MONO}; font-size: 11px;")
                indicator_layout.addWidget(value_label)
                self.health_indicators[label_text] = value_label
            
            health_layout.addLayout(indicator_layout)
        
        parent_layout.addWidget(health_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        if self.target_manager:
            # Connect to target manager signals
            self.target_manager.target_added.connect(self.on_target_added)
            self.target_manager.target_removed.connect(self.on_target_removed)
            self.target_manager.target_updated.connect(self.on_target_updated)
    
    def update_statistics(self):
        """Update dashboard statistics"""
        try:
            if self.target_manager:
                stats = self.target_manager.get_target_statistics()
                
                # Update cards
                self.cards['targets'].update_value(str(stats['total']), "Active targets")
                self.cards['scans'].update_value(str(stats.get('active', 0)), "Running scans")
                
                # Update vulnerabilities (placeholder for now)
                total_vulns = 0
                for target in self.target_manager.get_all_targets():
                    total_vulns += len(target.scan_results.get('vulnerabilities', []))
                self.cards['vulnerabilities'].update_value(str(total_vulns), "Total findings")
                
                # Update system health (mock data for now)
                import random
                cpu_usage = random.randint(10, 30)
                memory_usage = random.randint(35, 55)
                disk_usage = random.randint(70, 85)
                
                if 'CPU Usage' in self.health_indicators:
                    self.health_indicators['CPU Usage'].setValue(cpu_usage)
                if 'Memory Usage' in self.health_indicators:
                    self.health_indicators['Memory Usage'].setValue(memory_usage)
                if 'Disk Space' in self.health_indicators:
                    self.health_indicators['Disk Space'].setValue(disk_usage)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to update dashboard statistics: {e}")
    
    def update_target_count(self):
        """Update target count specifically"""
        if self.target_manager:
            stats = self.target_manager.get_target_statistics()
            self.cards['targets'].update_value(str(stats['total']), "Active targets")
    
    @Slot(str, dict)
    def on_target_added(self, target_id, target_data):
        """Handle target addition"""
        self.add_activity_entry("Target Added", f"{target_data['value']} ({target_data['type']})", "success")
        self.update_target_count()
    
    @Slot(str)
    def on_target_removed(self, target_id):
        """Handle target removal"""
        self.add_activity_entry("Target Removed", f"Target {target_id}", "warning")
        self.update_target_count()
    
    @Slot(str, dict)
    def on_target_updated(self, target_id, target_data):
        """Handle target update"""
        self.add_activity_entry("Target Updated", f"{target_data['value']} status: {target_data['status']}", "info")
    
    def add_activity_entry(self, source: str, message: str, entry_type: str = "info"):
        """Add entry to activity log with Modern Minimal styling"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different types
        colors = {
            "system": Colors.PRIMARY,
            "info": Colors.TEXT_SECONDARY,
            "warning": Colors.WARNING,
            "error": Colors.DANGER,
            "success": Colors.SUCCESS
        }
        
        color = colors.get(entry_type, Colors.TEXT_PRIMARY)
        
        entry = f'<span style="color: {Colors.TEXT_MUTED};">[{timestamp}]</span> <span style="color: {Colors.PRIMARY}; font-weight: 600;">{source.upper()}:</span> <span style="color: {color};">{message}</span>'
        
        self.activity_log.append(entry)
        
        # Limit log size
        if self.activity_log.document().blockCount() > 100:
            cursor = self.activity_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
    
    def on_enter(self):
        """Called when page is entered"""
        self.update_statistics()
        if self.logger:
            self.logger.info("Dashboard page entered")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
