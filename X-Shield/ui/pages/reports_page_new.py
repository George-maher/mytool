"""
Reports Page for X-Shield MVC Architecture
Analysis and reports generation interface
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from ui.components.styles import Colors, Spacing, Typography
from reports.advanced_report_generator import AdvancedReportGenerator


class ReportsPage(QWidget):
    """Reports page for analysis and report generation"""
    
    def __init__(self, target_manager, module_manager, logger, parent=None):
        super().__init__(parent)
        self.target_manager = target_manager
        self.module_manager = module_manager
        self.logger = logger
        self.report_generator = AdvancedReportGenerator()
        
        self.setup_ui()
        self.setup_connections()
        self.load_reports()
    
    def setup_ui(self):
        """Setup reports UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.SM)

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
        gen_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        gen_layout.setSpacing(Spacing.SM)
        
        # Section title
        section_title = QLabel("Generate Audit Report")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        gen_layout.addWidget(section_title)
        
        # Report options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(Spacing.SM)
        
        # Target Selection
        target_layout = QVBoxLayout()
        target_layout.setSpacing(Spacing.SM)
        target_label = QLabel("Select Target")
        target_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        target_layout.addWidget(target_label)

        self.target_combo = QComboBox()
        self.target_combo.addItem("All Targets", "all")
        target_layout.addWidget(self.target_combo)
        options_layout.addLayout(target_layout)

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
        self.format_combo.addItems(["HTML", "PDF", "JSON", "CSV"])
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
        table_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        table_layout.setSpacing(Spacing.SM)
        
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
        details_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        details_layout.setSpacing(Spacing.SM)
        
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
    
    def refresh_targets(self):
        """Refresh target selection combo box"""
        if not self.target_manager:
            return

        current_id = self.target_combo.currentData()
        self.target_combo.clear()
        self.target_combo.addItem("All Targets", "all")

        for target in self.target_manager.get_all_targets():
            self.target_combo.addItem(f"{target.value} ({target.type})", target.id)

        # Try to restore selection
        index = self.target_combo.findData(current_id)
        if index >= 0:
            self.target_combo.setCurrentIndex(index)

    def generate_report(self):
        """Generate a new report using actual scan data"""
        report_type = self.report_type_combo.currentText()
        format_type = self.format_combo.currentText()
        target_id = self.target_combo.currentData()
        
        if not self.target_manager:
            QMessageBox.warning(self, "Warning", "Target manager not available")
            return
        
        try:
            # Prepare scan data for the generator
            if target_id == "all":
                targets = self.target_manager.get_all_targets()
                primary_target = "Multiple Targets"
            else:
                target = self.target_manager.get_target(target_id)
                if not target:
                    QMessageBox.warning(self, "Error", "Selected target not found")
                    return
                targets = [target]
                primary_target = target.value

            if not targets:
                QMessageBox.warning(self, "No Data", "No targets found. Please add targets and run scans first.")
                return

            # Consolidate vulnerabilities and modules from targets
            all_vulnerabilities = []
            all_modules = []
            
            for t in targets:
                for scanner, results in t.scan_results.items():
                    if isinstance(results, dict):
                        vulns = results.get('vulnerabilities', [])
                        for v in vulns:
                            v_copy = v.copy()
                            if 'target' not in v_copy:
                                v_copy['target'] = t.value
                            all_vulnerabilities.append(v_copy)

                        # Add module info
                        all_modules.append({
                            'name': scanner,
                            'status': 'completed',
                            'duration': results.get('duration', 0),
                            'items_scanned': results.get('items_scanned', 0),
                            'issues_found': len(vulns),
                            'summary': results.get('summary', f'Scan of {t.value} completed')
                        })

            scan_data = {
                'primary_target': primary_target,
                'vulnerabilities': all_vulnerabilities,
                'modules': all_modules,
                'scan_scope': [report_type]
            }

            # Use the actual generator
            report_path = self.report_generator.generate_report(scan_data, report_title=f"{report_type} - {primary_target}")
            
            self.load_reports() # Refresh table
            QMessageBox.information(self, "Success", f"Report generated successfully: {os.path.basename(report_path)}")
            
            if self.logger:
                self.logger.info(f"Generated {report_type} report for {primary_target}")
                
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
        self.reports_table.setItem(row, 2, QTableWidgetItem(report_data['target']))
        
        # Generated
        self.reports_table.setItem(row, 3, QTableWidgetItem(report_data['generated_at']))
        
        # Actions
        actions_widget = self.create_report_actions_widget(report_data)
        self.reports_table.setCellWidget(row, 4, actions_widget)
    
    def create_report_actions_widget(self, report_data):
        """Create actions widget for report row with modern minimal style"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.XL)
        
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
        view_btn.clicked.connect(lambda: self.view_report_file(report_data['path']))
        layout.addWidget(view_btn)
        
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
        delete_btn.clicked.connect(lambda: self.delete_report_file(report_data))
        layout.addWidget(delete_btn)
        
        return widget
    
    def view_report_file(self, report_path):
        """Open report in system browser"""
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(report_path)}")

    def delete_report_file(self, report_data):
        """Delete report file"""
        reply = QMessageBox.question(
            self, "Delete Report", 
            f"Are you sure you want to delete report '{report_data['report_name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(report_data['path']):
                    os.remove(report_data['path'])

                # Also delete JSON summary if it exists
                json_path = report_data['path'].replace('.html', '.json')
                if os.path.exists(json_path):
                    os.remove(json_path)

                self.load_reports()
                QMessageBox.information(self, "Success", "Report deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete report: {str(e)}")

    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.reports_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            report_name = self.reports_table.item(row, 0).text()
            
            # Find report file and preview it
            reports_dir = "data/reports"
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    if filename == report_name:
                        report_path = os.path.join(reports_dir, filename)
                        self.preview_report(report_path)
                        break
    
    def preview_report(self, report_path):
        """Preview report content in text edit"""
        try:
            if report_path.endswith('.html'):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple HTML to text conversion for preview
                import re
                text = re.sub('<[^<]+?>', '', content)
                self.report_preview.setText(text[:2000] + ("..." if len(text) > 2000 else ""))
            elif report_path.endswith('.json'):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.report_preview.setText(content)
            else:
                self.report_preview.setText(f"Preview not available for this format. Use the 👁️ icon to view.")
        except Exception as e:
            self.report_preview.setText(f"Error previewing report: {str(e)}")

    def load_reports(self):
        """Load existing reports from data/reports"""
        self.reports_table.setRowCount(0)
        
        reports_dir = "data/reports"
        if not os.path.exists(reports_dir):
            return

        for filename in os.listdir(reports_dir):
            if filename.endswith('.html'):
                report_path = os.path.join(reports_dir, filename)
                stat = os.stat(report_path)

                # Try to get info from JSON summary if available
                json_path = report_path.replace('.html', '.json')
                report_type = "Security Report"
                target = "Unknown"

                if os.path.exists(json_path):
                    try:
                        import json
                        with open(json_path, 'r') as f:
                            data = json.load(f)
                            report_type = data.get('metadata', {}).get('report_title', report_type).split(' - ')[0]
                            target = data.get('target', {}).get('primary_target', target)
                    except:
                        pass

                report_data = {
                    'report_name': filename,
                    'report_type': report_type,
                    'target': target,
                    'path': report_path,
                    'generated_at': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                }
                self.add_report_to_table(report_data)

    def on_enter(self):
        """Called when page is entered"""
        self.refresh_targets()
        self.load_reports()
        if self.logger:
            self.logger.info("Reports page entered")
