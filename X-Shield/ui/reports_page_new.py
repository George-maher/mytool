"""
Reports Page for X-Shield MVC Architecture
Analysis and reports generation interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from ui.styles import Colors, Spacing, Typography


class ReportsPage(QWidget):
    """Reports page for analysis and report generation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        self.target_manager = parent.get_target_manager() if parent else None
        
        self.setup_ui()
        self.setup_connections()
        self.load_reports()
    
    def setup_ui(self):
        """Setup reports UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)

        # Report Generation
        self.setup_report_generation(layout)
        
        # Reports Table
        self.setup_reports_table(layout)
        
        # Report Details
        self.setup_report_details(layout)
        
        layout.addStretch()
    
    def setup_report_generation(self, parent_layout):
        """Setup report generation section with modern minimal style"""
        gen_frame = QFrame()
        gen_frame.setObjectName("card")
        gen_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        gen_layout = QVBoxLayout(gen_frame)
        gen_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        gen_layout.setSpacing(Spacing.XL)
        
        # Section title
        section_title = QLabel("Generate Audit Report")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        gen_layout.addWidget(section_title)
        
        # Report options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(Spacing.XL)
        
        # Report type
        type_layout = QVBoxLayout()
        type_layout.setSpacing(Spacing.SM)
        type_label = QLabel("Report Type")
        type_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        type_layout.addWidget(type_label)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Executive Summary", "Technical Report", "Vulnerability Report", "Compliance Report"
        ])
        type_layout.addWidget(self.report_type_combo)
        options_layout.addLayout(type_layout)
        
        # Format
        format_layout = QVBoxLayout()
        format_layout.setSpacing(Spacing.SM)
        format_label = QLabel("Format")
        format_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "HTML", "JSON", "CSV"])
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        options_layout.addStretch()
        gen_layout.addLayout(options_layout)
        
        # Generate button
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setObjectName("primary_btn")
        self.generate_btn.setMinimumWidth(160)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addStretch()
        gen_layout.addLayout(btn_layout)
        
        parent_layout.addWidget(gen_frame)
    
    def setup_reports_table(self, parent_layout):
        """Setup reports table with modern minimal style"""
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        table_layout.setSpacing(Spacing.XL)
        
        # Section title
        section_title = QLabel("Archived Audits")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        table_layout.addWidget(section_title)
        
        # Reports table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels([
            "Report Name", "Type", "Target", "Generated", "Actions"
        ])
        
        # Set column widths
        header = self.reports_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 120)
        
        self.reports_table.verticalHeader().setDefaultSectionSize(50)
        self.reports_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.reports_table)
        parent_layout.addWidget(table_frame)
    
    def setup_report_details(self, parent_layout):
        """Setup report details section with modern minimal style"""
        details_frame = QFrame()
        details_frame.setObjectName("card")
        details_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        details_layout.setSpacing(Spacing.MD)
        
        # Section title
        section_title = QLabel("Report Content Preview")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        details_layout.addWidget(section_title)
        
        # Report preview
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setMinimumHeight(300)
        self.report_preview.setStyleSheet(f"""
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
        
        self.report_preview.append("Select a report from the table to preview its contents...")
        
        details_layout.addWidget(self.report_preview)
        parent_layout.addWidget(details_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.generate_btn.clicked.connect(self.generate_report)
        self.reports_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def generate_report(self):
        """Generate a new report"""
        report_type = self.report_type_combo.currentText()
        format_type = self.format_combo.currentText()
        
        if not self.target_manager:
            QMessageBox.warning(self, "Warning", "Target manager not available")
            return
        
        try:
            # Get all targets and their scan results
            targets = self.target_manager.get_all_targets()
            
            if not targets:
                QMessageBox.warning(self, "No Data", "No targets found. Please add targets and run scans first.")
                return
            
            # Generate mock report data
            from datetime import datetime
            report_data = {
                'report_name': f"{report_type}_{len(self.reports_table) + 1}",
                'report_type': report_type,
                'format': format_type,
                'targets': len(targets),
                'vulnerabilities': 0,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Count vulnerabilities
            for target in targets:
                for scan_results in target.scan_results.values():
                    if isinstance(scan_results, dict) and 'vulnerabilities' in scan_results:
                        report_data['vulnerabilities'] += len(scan_results['vulnerabilities'])
            
            # Add to table
            self.add_report_to_table(report_data)
            
            QMessageBox.information(self, "Success", f"Report generated successfully: {report_data['report_name']}")
            
            if self.logger:
                self.logger.info(f"Generated {report_type} report in {format_type} format")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def add_report_to_table(self, report_data):
        """Add report to table"""
        row = self.reports_table.rowCount()
        self.reports_table.insertRow(row)
        
        # Report name
        self.reports_table.setItem(row, 0, QTableWidgetItem(report_data['report_name']))
        
        # Type
        self.reports_table.setItem(row, 1, QTableWidgetItem(report_data['report_type']))
        
        # Target
        target_text = f"{report_data['targets']} target(s)"
        self.reports_table.setItem(row, 2, QTableWidgetItem(target_text))
        
        # Generated
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.reports_table.setItem(row, 3, QTableWidgetItem(timestamp))
        
        # Actions
        actions_widget = self.create_report_actions_widget(report_data)
        self.reports_table.setCellWidget(row, 4, actions_widget)
    
    def create_report_actions_widget(self, report_data):
        """Create actions widget for report row with modern minimal style"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
        layout.setSpacing(Spacing.SM)
        
        # View button
        view_btn = QPushButton("👁️")
        view_btn.setToolTip("View")
        view_btn.setFixedSize(28, 28)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.PRIMARY};
            }}
        """)
        view_btn.clicked.connect(lambda: self.view_report(report_data))
        layout.addWidget(view_btn)
        
        # Download button
        download_btn = QPushButton("💾")
        download_btn.setToolTip("Download")
        download_btn.setFixedSize(28, 28)
        download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.SUCCESS};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.SUCCESS};
            }}
        """)
        download_btn.clicked.connect(lambda: self.download_report(report_data))
        layout.addWidget(download_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.DANGER};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.DANGER};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_report(report_data))
        layout.addWidget(delete_btn)
        
        return widget
    
    def view_report(self, report_data):
        """View report content"""
        # Generate mock report content
        content = f"""
========================================
{report_data['report_name'].upper()}
========================================

Report Type: {report_data['report_type']}
Format: {report_data['format']}
Generated: {report_data.get('generated_at', 'Unknown')}
Targets Scanned: {report_data['targets']}
Vulnerabilities Found: {report_data['vulnerabilities']}

EXECUTIVE SUMMARY:
==================
This security assessment was conducted on {report_data['targets']} target(s).
A total of {report_data['vulnerabilities']} potential vulnerabilities were identified.

FINDINGS:
=========
High Severity: {report_data['vulnerabilities'] // 3}
Medium Severity: {report_data['vulnerabilities'] // 2}
Low Severity: {report_data['vulnerabilities'] - (report_data['vulnerabilities'] // 3 + report_data['vulnerabilities'] // 2)}

RECOMMENDATIONS:
================
1. Address all high and medium severity vulnerabilities immediately
2. Implement regular security scanning and monitoring
3. Update and patch systems regularly
4. Conduct security awareness training for staff

CONCLUSION:
==========
The security posture requires improvement. Implement the recommended actions to enhance security.
        """
        
        self.report_preview.setText(content)
    
    def download_report(self, report_data):
        """Download report"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"{report_data['report_name']}.{report_data['format'].lower()}", 
            f"{report_data['format']} Files (*.{report_data['format'].lower()})"
        )
        
        if file_path:
            try:
                # Mock file creation
                with open(file_path, 'w') as f:
                    f.write(f"Report: {report_data['report_name']}\n")
                    f.write(f"Type: {report_data['report_type']}\n")
                    f.write(f"Format: {report_data['format']}\n")
                    f.write(f"Targets: {report_data['targets']}\n")
                    f.write(f"Vulnerabilities: {report_data['vulnerabilities']}\n")
                
                QMessageBox.information(self, "Success", f"Report saved to {file_path}")
                
                if self.logger:
                    self.logger.info(f"Report downloaded: {file_path}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
    
    def delete_report(self, report_data):
        """Delete report"""
        reply = QMessageBox.question(
            self, "Delete Report", 
            f"Are you sure you want to delete report '{report_data['report_name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Find and remove row
            for row in range(self.reports_table.rowCount()):
                item = self.reports_table.item(row, 0)
                if item and item.text() == report_data['report_name']:
                    self.reports_table.removeRow(row)
                    break
            
            QMessageBox.information(self, "Success", "Report deleted successfully")
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.reports_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            report_name = self.reports_table.item(row, 0).text()
            
            # Find report data and view it
            for i in range(self.reports_table.rowCount()):
                if self.reports_table.item(i, 0).text() == report_name:
                    report_data = {
                        'report_name': report_name,
                        'report_type': self.reports_table.item(i, 1).text(),
                        'format': 'HTML',
                        'targets': int(self.reports_table.item(i, 2).text().split()[0]),
                        'vulnerabilities': 5  # Mock data
                    }
                    self.view_report(report_data)
                    break
    
    def load_reports(self):
        """Load existing reports (mock data)"""
        # Clear existing reports first
        self.reports_table.setRowCount(0)
        
        # Add some mock reports for demonstration
        from datetime import datetime
        mock_reports = [
            {
                'report_name': 'Security_Assessment_1',
                'report_type': 'Executive Summary',
                'format': 'PDF',
                'targets': 3,
                'vulnerabilities': 12,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'report_name': 'Vulnerability_Report_1',
                'report_type': 'Vulnerability Report',
                'format': 'HTML',
                'targets': 1,
                'vulnerabilities': 8,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        for report_data in mock_reports:
            self.add_report_to_table(report_data)
    
    def on_enter(self):
        """Called when page is entered"""
        self.load_reports()
        if self.logger:
            self.logger.info("Reports page entered")
