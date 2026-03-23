"""
Target Manager Page for X-Shield MVC Architecture
Central page to manage targets with input fields and table display
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QScrollArea, QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor
from ui.styles import Colors, Spacing, Typography


class TargetManagerPage(QWidget):
    """Target Manager page with input fields and target table"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.logger = parent.get_logger() if parent else None
        self.target_manager = parent.get_target_manager() if parent else None
        
        self.setup_ui()
        self.setup_connections()
        self.load_targets()
    
    def setup_ui(self):
        """Setup target manager UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Target Input Section
        self.setup_target_input(layout)
        
        # Target Table Section
        self.setup_target_table(layout)
        
        # Action Buttons Section
        self.setup_action_buttons(layout)
        
        layout.addStretch()
    
    def setup_target_input(self, parent_layout):
        """Setup modern target input section"""
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        input_layout.setSpacing(Spacing.XL)
        
        # Modern Section Title
        section_title = QLabel("Enroll New Node")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        input_layout.addWidget(section_title)
        
        # Modern Input Form
        form_layout = QGridLayout()
        form_layout.setSpacing(Spacing.LG)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern Target IP/URL Input
        target_label = QLabel("Target Address")
        target_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        form_layout.addWidget(target_label, 0, 0)
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g., 192.168.1.1 or example.com")
        form_layout.addWidget(self.target_input, 0, 1)
        
        # Modern Target Type Selection
        type_label = QLabel("Target Type")
        type_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        form_layout.addWidget(type_label, 1, 0)
        
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems(["IP Address", "Domain", "URL", "IP Range", "File"])
        form_layout.addWidget(self.target_type_combo, 1, 1)
        
        # Modern Description Input
        desc_label = QLabel("Description")
        desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        form_layout.addWidget(desc_label, 2, 0)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional notes about this target...")
        self.description_input.setMaximumHeight(80)
        form_layout.addWidget(self.description_input, 2, 1)
        
        input_layout.addLayout(form_layout)
        
        # Modern Add Target Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_target_btn = QPushButton("Add Target")
        self.add_target_btn.setObjectName("primary_btn")
        self.add_target_btn.setMinimumWidth(120)
        button_layout.addWidget(self.add_target_btn)
        input_layout.addLayout(button_layout)
        
        parent_layout.addWidget(input_frame)
    
    def setup_target_table(self, parent_layout):
        """Setup modern target table section"""
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
        
        # Modern Section Title
        section_title = QLabel("Target Inventory")
        section_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        table_layout.addWidget(section_title)
        
        # Modern Target Table
        self.target_table = QTableWidget()
        self.target_table.setColumnCount(6)
        self.target_table.setHorizontalHeaderLabels([
            "Target", "Type", "Status", "Description", "Created", "Actions"
        ])
        
        # Set column widths
        header = self.target_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 140)
        
        self.target_table.verticalHeader().setDefaultSectionSize(50)
        self.target_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.target_table)
        parent_layout.addWidget(table_frame)
    
    def setup_action_buttons(self, parent_layout):
        """Setup modern action buttons section"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(Spacing.MD)
        
        # Modern Action Buttons
        self.import_btn = QPushButton("Import")
        self.import_btn.setProperty("class", "small")
        buttons_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setProperty("class", "small")
        buttons_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setProperty("class", "small")
        buttons_layout.addWidget(self.clear_btn)
        
        buttons_layout.addStretch()
        
        # Modern Status Indicator
        status_layout = QHBoxLayout()
        status_layout.setSpacing(Spacing.SM)
        
        status_label = QLabel("Active Target:")
        status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500; font-size: 13px;")
        status_layout.addWidget(status_label)
        
        self.active_target_label = QLabel("None")
        self.active_target_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: 600; font-size: 13px;")
        status_layout.addWidget(self.active_target_label)
        
        buttons_layout.addLayout(status_layout)
        parent_layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.add_target_btn.clicked.connect(self.add_target)
        self.import_btn.clicked.connect(self.import_targets)
        self.export_btn.clicked.connect(self.export_targets)
        self.clear_btn.clicked.connect(self.clear_all_targets)
        
        # Table connections
        self.target_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Target manager connections
        if self.target_manager:
            self.target_manager.target_added.connect(self.on_target_added)
            self.target_manager.target_removed.connect(self.on_target_removed)
            self.target_manager.target_updated.connect(self.on_target_updated)
            self.target_manager.active_target_changed.connect(self.on_active_target_changed)
    
    def add_target(self):
        """Add new target"""
        target_value = self.target_input.text().strip()
        target_type = self.target_type_combo.currentText()
        description = self.description_input.toPlainText().strip()
        
        if not target_value:
            QMessageBox.warning(self, "Invalid Input", "Please enter a target value.")
            return
        
        if self.target_manager:
            try:
                target_id = self.target_manager.add_target(
                    target_type, target_value, description
                )
                
                # Clear inputs
                self.target_input.clear()
                self.description_input.clear()
                
                # Set as active target
                self.target_manager.set_active_target(target_id)
                
                QMessageBox.information(self, "Success", "Target added successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add target: {str(e)}")
    
    def load_targets(self):
        """Load targets into table"""
        if not self.target_manager:
            return
        
        targets = self.target_manager.get_all_targets()
        self.target_table.setRowCount(len(targets))
        
        for row, target in enumerate(targets):
            # Target value
            self.target_table.setItem(row, 0, QTableWidgetItem(target.value))
            
            # Type
            self.target_table.setItem(row, 1, QTableWidgetItem(target.type))
            
            # Status
            status_item = QTableWidgetItem(target.status)
            if target.status == "Active":
                status_item.setForeground(QColor('#4CAF50'))
            elif target.status == "Scanning":
                status_item.setForeground(QColor('#FF9800'))
            elif target.status == "Completed":
                status_item.setForeground(QColor('#2196F3'))
            else:
                status_item.setForeground(QColor('#f44336'))
            self.target_table.setItem(row, 2, status_item)
            
            # Description
            desc = target.description if target.description else "No description"
            self.target_table.setItem(row, 3, QTableWidgetItem(desc))
            
            # Created date
            created = target.created_at[:10] if target.created_at else "Unknown"
            self.target_table.setItem(row, 4, QTableWidgetItem(created))
            
            # Actions
            actions_widget = self.create_actions_widget(target.id)
            self.target_table.setCellWidget(row, 5, actions_widget)
    
    def create_actions_widget(self, target_id):
        """Create actions widget for table row with modern minimal style"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
        layout.setSpacing(Spacing.SM)
        
        # Set Active button
        active_btn = QPushButton("🎯")
        active_btn.setToolTip("Set as Active")
        active_btn.setFixedSize(28, 28)
        active_btn.setStyleSheet(f"""
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
        active_btn.clicked.connect(lambda: self.set_active_target(target_id))
        layout.addWidget(active_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Edit")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.INFO};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.INFO};
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_target(target_id))
        layout.addWidget(edit_btn)
        
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
        delete_btn.clicked.connect(lambda: self.delete_target(target_id))
        layout.addWidget(delete_btn)
        
        return widget
    
    def set_active_target(self, target_id):
        """Set active target"""
        if self.target_manager:
            self.target_manager.set_active_target(target_id)
    
    def edit_target(self, target_id):
        """Edit target (placeholder for now)"""
        QMessageBox.information(self, "Edit Target", f"Edit functionality for target {target_id} coming soon!")
    
    def delete_target(self, target_id):
        """Delete target"""
        reply = QMessageBox.question(
            self, "Delete Target", 
            "Are you sure you want to delete this target?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.target_manager:
            self.target_manager.remove_target(target_id)
    
    def import_targets(self):
        """Import targets from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Targets", "", "JSON Files (*.json)"
        )
        
        if file_path and self.target_manager:
            try:
                count = self.target_manager.import_targets(file_path)
                QMessageBox.information(self, "Import Complete", f"Imported {count} targets!")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")
    
    def export_targets(self):
        """Export targets to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Targets", "targets.json", "JSON Files (*.json)"
        )
        
        if file_path and self.target_manager:
            try:
                success = self.target_manager.export_targets(file_path)
                if success:
                    QMessageBox.information(self, "Export Complete", f"Targets exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def clear_all_targets(self):
        """Clear all targets"""
        reply = QMessageBox.question(
            self, "Clear All Targets", 
            "Are you sure you want to delete all targets? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.target_manager:
            # Remove all targets
            target_ids = list(self.target_manager.targets.keys())
            for target_id in target_ids:
                self.target_manager.remove_target(target_id)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.target_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # You can add selection-specific logic here
    
    @Slot(str, dict)
    def on_target_added(self, target_id, target_data):
        """Handle target addition"""
        self.load_targets()
    
    @Slot(str)
    def on_target_removed(self, target_id):
        """Handle target removal"""
        self.load_targets()
    
    @Slot(str, dict)
    def on_target_updated(self, target_id, target_data):
        """Handle target update"""
        self.load_targets()
    
    @Slot(str, dict)
    def on_active_target_changed(self, target_id, target_data):
        """Handle active target change"""
        if target_data:
            self.active_target_label.setText(target_data['value'])
            self.active_target_label.setStyleSheet(f"color: {Colors.SUCCESS};")
        else:
            self.active_target_label.setText("None")
            self.active_target_label.setStyleSheet(f"color: {Colors.WARNING};")
    
    def on_enter(self):
        """Called when page is entered"""
        self.load_targets()
        if self.logger:
            self.logger.info("Target Manager page entered")
