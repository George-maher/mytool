"""
Reports Page for X-Shield Framework
Report generation and viewing with Material Design
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QGroupBox, QFormLayout, QComboBox, QFileDialog, QMessageBox,
    QFrame, QProgressBar
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont


class ReportsPage(QWidget):
    """Reports page for generating and viewing security reports"""
    
    # Signals
    report_generated = Signal(str)  # report path
    
    def __init__(self, report_generator):
        super().__init__()
        self.report_generator = report_generator
        self.current_reports = []
        self.setup_ui()
        self.setup_connections()
        self.refresh_reports()
    
    def setup_ui(self):
        """Setup reports page UI with Midnight Neon aesthetic"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Header Section
        header_layout = QHBoxLayout()
        header = QLabel("REPORTING ENGINE")
        header.setStyleSheet("color: #f8fafc; font-weight: 900; font-size: 24px; letter-spacing: 4px;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        status_tag = QLabel("READY")
        status_tag.setStyleSheet("""
            color: #22d3ee;
            font-weight: bold;
            font-size: 10px;
            background-color: rgba(34, 211, 238, 0.1);
            border: 1px solid #22d3ee;
            padding: 4px 12px;
            border-radius: 4px;
        """)
        header_layout.addWidget(status_tag)
        layout.addLayout(header_layout)
        
        # Report generation section
        self.setup_report_generation(layout)
        
        # Report list section
        self.setup_report_list(layout)
        
        # Report preview section
        self.setup_report_preview(layout)
    
    def setup_report_generation(self, parent_layout):
        """Setup report generation section"""
        gen_frame = QFrame()
        gen_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 20px;
            }
        """)
        
        gen_layout = QVBoxLayout(gen_frame)
        
        # Title
        title = QLabel("GENERATE AUDIT")
        title.setStyleSheet("color: #22d3ee; font-weight: bold; font-size: 12px; letter-spacing: 2px; margin-bottom: 10px;")
        gen_layout.addWidget(title)
        
        # Report options
        options_layout = QHBoxLayout()
        
        # Report type
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Report Type:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Comprehensive Security Report",
            "Vulnerability Summary", 
            "Network Scan Report",
            "Web Application Report",
            "Executive Summary"
        ])
        self.report_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 8px;
                color: #f8fafc;
                font-size: 12px;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 1px solid #22d3ee;
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
        type_layout.addWidget(self.report_type_combo)
        options_layout.addLayout(type_layout)
        
        # Date range
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems([
            "Last 24 Hours",
            "Last 7 Days",
            "Last 30 Days",
            "All Time"
        ])
        self.date_range_combo.setStyleSheet("""
            QComboBox {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 8px;
                color: #f8fafc;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 1px solid #22d3ee;
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
        date_layout.addWidget(self.date_range_combo)
        options_layout.addLayout(date_layout)
        
        # Format
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "PDF", "JSON", "CSV"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 8px;
                color: #f8fafc;
                font-size: 12px;
                min-width: 100px;
            }
            QComboBox:focus {
                border: 1px solid #22d3ee;
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
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        options_layout.addStretch()
        gen_layout.addLayout(options_layout)
        
        # Generate button
        self.generate_btn = QPushButton("EXECUTE REPORT GENERATION")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #22d3ee;
                color: #020617;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-weight: 900;
                font-size: 13px;
                letter-spacing: 1px;
                min-width: 200px;
                min-height: 48px;
            }
            QPushButton:hover {
                background-color: #67e8f9;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #475569;
            }
        """)
        gen_layout.addWidget(self.generate_btn)
        
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
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)
        gen_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(gen_frame)
    
    def setup_report_list(self, parent_layout):
        """Setup report list section"""
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 20px;
            }
        """)
        
        list_layout = QVBoxLayout(list_frame)
        
        # Title
        title = QLabel("ARCHIVED AUDITS")
        title.setStyleSheet("color: #22d3ee; font-weight: bold; font-size: 12px; letter-spacing: 2px; margin-bottom: 10px;")
        list_layout.addWidget(title)
        
        # Reports table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels([
            "Name", "Type", "Created", "Size", "Actions"
        ])
        
        self.reports_table.setStyleSheet("""
            QTableWidget {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 4px;
                gridline-color: #1e293b;
                color: #f8fafc;
                selection-background-color: rgba(34, 211, 238, 0.2);
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #1e293b;
            }
            QHeaderView::section {
                background-color: #0f172a;
                color: #64748b;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 10px;
                letter-spacing: 1px;
            }
        """)
        
        header = self.reports_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        
        self.reports_table.setAlternatingRowColors(True)
        self.reports_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        list_layout.addWidget(self.reports_table)
        
        parent_layout.addWidget(list_frame)
    
    def setup_report_preview(self, parent_layout):
        """Setup report preview section"""
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 4px;
                padding: 20px;
            }
        """)
        
        preview_layout = QVBoxLayout(preview_frame)
        
        # Title
        title = QLabel("CONTENT INSPECTION")
        title.setStyleSheet("color: #22d3ee; font-weight: bold; font-size: 12px; letter-spacing: 2px; margin-bottom: 10px;")
        preview_layout.addWidget(title)
        
        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #020617;
                border: 1px solid #1e293b;
                border-radius: 4px;
                color: #f8fafc;
                padding: 12px;
                font-family: 'DejaVu Sans Mono', monospace;
                font-size: 11px;
            }
        """)
        self.preview_text.setText("Select a report to preview...")
        preview_layout.addWidget(self.preview_text)
        
        # Preview actions
        actions_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("OPEN")
        self.open_btn.setEnabled(False)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #22d3ee;
                color: #020617;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 120px;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: #67e8f9;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #475569;
            }
        """)
        actions_layout.addWidget(self.open_btn)
        
        self.export_btn = QPushButton("EXPORT")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: #020617;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 120px;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: #fbbf24;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #475569;
            }
        """)
        actions_layout.addWidget(self.export_btn)
        
        self.delete_btn = QPushButton("PURGE")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f43f5e;
                color: #f8fafc;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 120px;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: #fb7185;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #475569;
            }
        """)
        actions_layout.addWidget(self.delete_btn)
        
        actions_layout.addStretch()
        preview_layout.addLayout(actions_layout)
        
        parent_layout.addWidget(preview_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Generate report
        self.generate_btn.clicked.connect(self.generate_report)
        
        # Table selection
        self.reports_table.itemSelectionChanged.connect(self.on_report_selected)
        
        # Report actions
        self.open_btn.clicked.connect(self.open_report)
        self.export_btn.clicked.connect(self.export_report)
        self.delete_btn.clicked.connect(self.delete_report)
    
    @Slot()
    def generate_report(self):
        """Generate new report"""
        # Update UI
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Get report options
        report_type = self.report_type_combo.currentText()
        date_range = self.date_range_combo.currentText()
        format_type = self.format_combo.currentText()
        
        # Simulate report generation
        QTimer.singleShot(2000, lambda: self.complete_report_generation(
            report_type, date_range, format_type
        ))
    
    def complete_report_generation(self, report_type, date_range, format_type):
        """Complete report generation"""
        try:
            # Generate report using report generator
            scan_data = {
                'report_type': report_type,
                'date_range': date_range,
                'format': format_type,
                'primary_target': 'Sample Target',
                'target_description': f'Generated {report_type.lower()} for {date_range.lower()}',
                'modules': [
                    {
                        'name': 'Network Scanner',
                        'status': 'completed',
                        'duration': 120.5,
                        'items_scanned': 1000,
                        'issues_found': 5,
                        'summary': 'Network scan completed successfully'
                    }
                ],
                'vulnerabilities': [
                    {
                        'title': 'Sample Vulnerability',
                        'severity': 'Medium',
                        'description': 'This is a sample vulnerability for demonstration',
                        'target': 'Sample Target',
                        'cvss_score': 5.5,
                        'recommendation': 'Apply security patches and update configurations'
                    }
                ]
            }
            
            # Generate report
            if hasattr(self.report_generator, 'generate_report'):
                report_path = self.report_generator.generate_report(scan_data)
            else:
                # Fallback: create simple report
                report_path = self.create_simple_report(scan_data)
            
            # Add to reports list
            self.add_report_to_list(report_path, report_type, format_type)
            
            # Update UI
            self.generate_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            
            # Emit signal
            self.report_generated.emit(report_path)
            
        except Exception as e:
            self.generate_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Report Error", f"Failed to generate report:\n{str(e)}")
    
    def create_simple_report(self, scan_data):
        """Create simple report as fallback"""
        reports_dir = "data/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"
        report_path = os.path.join(reports_dir, filename)
        
        # Simple HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>X-Shield Security Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
                .header {{ background: #2196F3; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #2d2d2d; border-radius: 8px; }}
                .vulnerability {{ margin: 10px 0; padding: 10px; background: #404040; border-radius: 4px; }}
                .severity-high {{ border-left: 4px solid #f44336; }}
                .severity-medium {{ border-left: 4px solid #FF9800; }}
                .severity-low {{ border-left: 4px solid #4CAF50; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>X-Shield Security Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Report Type: {scan_data.get('report_type', 'Unknown')}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{scan_data.get('target_description', 'No description available')}</p>
            </div>
            
            <div class="section">
                <h2>Scan Results</h2>
                <p>Total vulnerabilities found: {len(scan_data.get('vulnerabilities', []))}</p>
            </div>
            
            <div class="section">
                <h2>Vulnerabilities</h2>
        """
        
        for vuln in scan_data.get('vulnerabilities', []):
            severity = vuln.get('severity', 'Low').lower()
            html_content += f"""
                <div class="vulnerability severity-{severity}">
                    <h3>{vuln.get('title', 'Unknown')}</h3>
                    <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown')}</p>
                    <p><strong>Target:</strong> {vuln.get('target', 'Unknown')}</p>
                    <p><strong>Description:</strong> {vuln.get('description', 'No description')}</p>
                    <p><strong>Recommendation:</strong> {vuln.get('recommendation', 'No recommendation')}</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def add_report_to_list(self, report_path, report_type, format_type):
        """Add report to the list"""
        try:
            # Get file size
            file_size = os.path.getsize(report_path)
            size_str = self.format_file_size(file_size)
            
            # Get creation time
            created_time = datetime.fromtimestamp(os.path.getctime(report_path))
            created_str = created_time.strftime('%Y-%m-%d %H:%M')
            
            # Add to table
            row = self.reports_table.rowCount()
            self.reports_table.insertRow(row)
            
            # Name
            name = os.path.basename(report_path)
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, report_path)
            self.reports_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(report_type)
            self.reports_table.setItem(row, 1, type_item)
            
            # Created
            created_item = QTableWidgetItem(created_str)
            self.reports_table.setItem(row, 2, created_item)
            
            # Size
            size_item = QTableWidgetItem(size_str)
            self.reports_table.setItem(row, 3, size_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            view_btn = QPushButton("👁️")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            view_btn.clicked.connect(lambda checked, path=report_path: self.view_report(path))
            
            actions_layout.addWidget(view_btn)
            self.reports_table.setCellWidget(row, 4, actions_widget)
            
        except Exception as e:
            print(f"Error adding report to list: {e}")
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    @Slot()
    def on_report_selected(self):
        """Handle report selection"""
        current_row = self.reports_table.currentRow()
        has_selection = current_row >= 0
        
        self.open_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
        if has_selection:
            report_path = self.reports_table.item(current_row, 0).data(Qt.UserRole)
            self.preview_report(report_path)
        else:
            self.preview_text.setText("Select a report to preview...")
    
    def preview_report(self, report_path):
        """Preview report content"""
        try:
            if report_path.endswith('.html'):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Extract text content (simplified)
                import re
                text_content = re.sub('<[^<]+?>', '', content)
                self.preview_text.setText(text_content[:1000] + "..." if len(text_content) > 1000 else text_content)
            else:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.preview_text.setText(content[:1000] + "..." if len(content) > 1000 else content)
        except Exception as e:
            self.preview_text.setText(f"Error previewing report: {str(e)}")
    
    @Slot()
    def open_report(self):
        """Open selected report"""
        current_row = self.reports_table.currentRow()
        if current_row >= 0:
            report_path = self.reports_table.item(current_row, 0).data(Qt.UserRole)
            self.view_report(report_path)
    
    def view_report(self, report_path):
        """View report in external application"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(report_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", report_path])
            else:  # Linux
                subprocess.run(["xdg-open", report_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open report:\n{str(e)}")
    
    @Slot()
    def export_report(self):
        """Export selected report"""
        current_row = self.reports_table.currentRow()
        if current_row >= 0:
            report_path = self.reports_table.item(current_row, 0).data(Qt.UserRole)
            
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Export Report", 
                os.path.basename(report_path),
                "All Files (*)"
            )
            
            if save_path:
                try:
                    import shutil
                    shutil.copy2(report_path, save_path)
                    QMessageBox.information(self, "Success", "Report exported successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export report:\n{str(e)}")
    
    @Slot()
    def delete_report(self):
        """Delete selected report"""
        current_row = self.reports_table.currentRow()
        if current_row >= 0:
            report_path = self.reports_table.item(current_row, 0).data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Delete Report",
                f"Are you sure you want to delete this report?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(report_path)
                    self.reports_table.removeRow(current_row)
                    self.preview_text.setText("Select a report to preview...")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete report:\n{str(e)}")
    
    @Slot()
    def refresh_reports(self):
        """Refresh reports list"""
        # Load existing reports from data/reports directory
        reports_dir = "data/reports"
        if os.path.exists(reports_dir):
            self.reports_table.setRowCount(0)
            
            for filename in os.listdir(reports_dir):
                if filename.endswith('.html') or filename.endswith('.pdf') or filename.endswith('.json'):
                    report_path = os.path.join(reports_dir, filename)
                    self.add_report_to_list(report_path, "Existing Report", filename.split('.')[-1].upper())
