"""
Target Manager Page for X-Shield Framework
Professional target management with Material Design
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QComboBox, QLineEdit, QLabel, QFrame,
    QGroupBox, QFormLayout, QTextEdit, QFileDialog, QMessageBox,
    QSpinBox, QCheckBox, QToolBar, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, Slot
from PySide6.QtGui import QIcon, QFont, QAction
from core.target_store import Target
from ui.styles import Colors, Spacing, Typography


class TargetManager(QWidget):
    """Target Manager page with full CRUD operations"""
    
    # Signals
    target_added = Signal(str, str, str)  # name, type, value
    target_removed = Signal(str)  # target value
    scan_requested = Signal(str, str)  # scanner, target
    
    def __init__(self, target_store):
        super().__init__()
        self.target_store = target_store
        self.setup_ui()
        self.setup_connections()
        self.refresh_targets()
    
    def setup_ui(self):
        """Setup target manager UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)
        
        # Header
        header_label = QLabel("Target Manager")
        header_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H2_SIZE};")
        layout.addWidget(header_label)
        
        # Toolbar
        self.setup_toolbar(layout)
        
        # Add target section
        self.setup_add_target_section(layout)
        
        # Targets table
        self.setup_targets_table(layout)
    
    def setup_toolbar(self, parent_layout):
        """Setup toolbar for target operations with modern style"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(Spacing.MD)
        
        # Import/Export buttons
        self.import_btn = QPushButton("Import")
        self.import_btn.setProperty("class", "small")
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setProperty("class", "small")
        
        # Clear all button
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setProperty("class", "small")
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "small")
        
        toolbar_layout.addWidget(self.import_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.clear_all_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_btn)
        
        parent_layout.addLayout(toolbar_layout)
    
    def setup_add_target_section(self, parent_layout):
        """Setup add target section with modern minimal style"""
        add_frame = QFrame()
        add_frame.setObjectName("card")
        add_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")

        add_layout = QVBoxLayout(add_frame)
        add_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        add_layout.setSpacing(Spacing.XL)
        
        title = QLabel("Enroll New Node")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        add_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(Spacing.LG)
        
        # Target name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Primary Database")
        name_label = QLabel("Label")
        name_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
        form_layout.addRow(name_label, self.name_input)
        
        # Target type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["IP Address", "Domain", "URL", "IP Range", "File"])
        type_label = QLabel("Type")
        type_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
        form_layout.addRow(type_label, self.type_combo)
        
        # Target value
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("e.g., 192.168.1.1")
        value_label = QLabel("Address")
        value_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
        form_layout.addRow(value_label, self.value_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional notes...")
        self.description_input.setMaximumHeight(80)
        desc_label = QLabel("Notes")
        desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 500;")
        form_layout.addRow(desc_label, self.description_input)

        add_layout.addLayout(form_layout)
        
        # Add button
        btn_layout = QHBoxLayout()
        self.add_target_btn = QPushButton("Enroll Target")
        self.add_target_btn.setObjectName("primary_btn")
        self.add_target_btn.setMinimumWidth(140)
        btn_layout.addWidget(self.add_target_btn)
        btn_layout.addStretch()
        add_layout.addLayout(btn_layout)
        
        parent_layout.addWidget(add_frame)
    
    def setup_targets_table(self, parent_layout):
        """Setup targets table with modern minimal style"""
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_frame.setStyleSheet(f"QFrame#card {{ background-color: {Colors.SURFACE}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        table_layout.setSpacing(Spacing.XL)

        # Header Row (Title + Search)
        header_row = QHBoxLayout()
        title = QLabel("Target Inventory")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H3_SIZE};")
        header_row.addWidget(title)

        header_row.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter targets...")
        self.search_input.setFixedWidth(200)
        header_row.addWidget(self.search_input)
        table_layout.addLayout(header_row)
        
        # Targets table
        self.targets_table = QTableWidget()
        self.targets_table.setColumnCount(7)
        self.targets_table.setHorizontalHeaderLabels([
            "Name", "Type", "Value", "Description", "Scans", "Last Active", "Actions"
        ])
        
        header = self.targets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.targets_table.verticalHeader().setDefaultSectionSize(50)
        self.targets_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.targets_table)
        parent_layout.addWidget(table_frame)
    
    def setup_target_details(self, parent_layout):
        """Setup target details section"""
        details_group = QGroupBox("Target Details")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
        """)
        
        details_layout = QVBoxLayout(details_group)
        
        # Details display
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
        """)
        self.details_text.setText("Select a target to view details...")
        details_layout.addWidget(self.details_text)
        
        parent_layout.addWidget(details_group)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Add target
        self.add_target_btn.clicked.connect(self.add_target)
        
        # Table selection
        self.targets_table.itemSelectionChanged.connect(self.on_target_selected)
        
        # Search
        self.search_input.textChanged.connect(self.search_targets)
        
        # Toolbar actions
        self.import_btn.clicked.connect(self.import_targets)
        self.export_btn.clicked.connect(self.export_targets)
        self.clear_all_btn.clicked.connect(self.clear_all_targets)
        self.refresh_btn.clicked.connect(self.refresh_targets)
        
        # Target store signals
        self.target_store.target_added.connect(self.on_target_added_to_store)
        self.target_store.target_removed.connect(self.on_target_removed_from_store)
        self.target_store.target_updated.connect(self.on_target_updated_in_store)
        self.target_store.targets_updated.connect(self.refresh_targets)
    
    def add_target(self):
        """Add new target"""
        name = self.name_input.text().strip()
        target_type = self.type_combo.currentText().lower().replace(" ", "_")
        value = self.value_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        # Validation
        if not name or not value:
            QMessageBox.warning(self, "Input Error", "Name and value are required!")
            return
        
        # Validate target
        if not self.target_store.validate_target(target_type, value):
            QMessageBox.warning(self, "Validation Error", f"Invalid {target_type} format!")
            return
        
        # Add target
        if self.target_store.add_target(name, target_type, value, description):
            # Clear inputs
            self.name_input.clear()
            self.value_input.clear()
            self.description_input.clear()
            
            # Emit signal
            self.target_added.emit(name, target_type, value)
        else:
            QMessageBox.warning(self, "Duplicate Target", "Target already exists!")
    
    def on_target_selected(self):
        """Handle target selection in table"""
        current_row = self.targets_table.currentRow()
        if current_row >= 0:
            target_id = self.targets_table.item(current_row, 0).data(Qt.UserRole)
            target = self.target_store.get_target_by_id(target_id)
            
            if target:
                self.display_target_details(target)
    
    def display_target_details(self, target: Target):
        """Display target details"""
        details = f"""
        <b>Name:</b> {target.name}<br>
        <b>Type:</b> {target.type.title()}<br>
        <b>Value:</b> {target.value}<br>
        <b>Description:</b> {target.description or 'N/A'}<br>
        <b>Created:</b> {target.created_at}<br>
        <b>Scan Count:</b> {target.scan_count}<br>
        <b>Last Scanned:</b> {target.last_scanned or 'Never'}<br>
        <b>Tags:</b> {', '.join(target.tags) if target.tags else 'None'}
        """
        
        self.details_text.setHtml(details)
    
    def search_targets(self):
        """Search targets"""
        query = self.search_input.text().strip()
        
        if not query:
            self.refresh_targets()
            return
        
        targets = self.target_store.search_targets(query)
        self.populate_table(targets)
    
    def populate_table(self, targets):
        """Populate table with targets with modern action buttons"""
        self.targets_table.setRowCount(0)
        
        for row, target in enumerate(targets):
            self.targets_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(target.name)
            name_item.setData(Qt.UserRole, target.id)
            self.targets_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(target.type.title())
            self.targets_table.setItem(row, 1, type_item)
            
            # Value
            value_item = QTableWidgetItem(target.value)
            self.targets_table.setItem(row, 2, value_item)
            
            # Description
            desc = target.description or ""
            desc_item = QTableWidgetItem(desc[:50] + "..." if len(desc) > 50 else desc)
            self.targets_table.setItem(row, 3, desc_item)
            
            # Scan Count
            scan_count_item = QTableWidgetItem(str(target.scan_count))
            self.targets_table.setItem(row, 4, scan_count_item)
            
            # Last Scanned
            last_scanned = target.last_scanned or "Never"
            last_scanned_item = QTableWidgetItem(last_scanned[:16] if len(last_scanned) > 16 else last_scanned)
            self.targets_table.setItem(row, 5, last_scanned_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
            actions_layout.setSpacing(Spacing.SM)
            
            # Scan button
            scan_btn = QPushButton("🚀")
            scan_btn.setToolTip("Scan")
            scan_btn.setFixedSize(28, 28)
            scan_btn.setStyleSheet(f"""
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
            scan_btn.clicked.connect(lambda checked, t=target: self.scan_target(t))
            
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
            edit_btn.clicked.connect(lambda checked, t=target: self.edit_target(t))
            
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
            delete_btn.clicked.connect(lambda checked, t=target: self.delete_target(t))
            
            actions_layout.addWidget(scan_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.targets_table.setCellWidget(row, 6, actions_widget)
    
    def refresh_targets(self):
        """Refresh targets table"""
        targets = self.target_store.get_all_targets()
        self.populate_table(targets)
    
    def scan_target(self, target: Target):
        """Scan selected target"""
        # Show scanner selection dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Scanner")
        dialog.setFixedSize(300, 150)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select scanner type:"))
        
        scanner_combo = QComboBox()
        scanner_combo.addItems([
            "Network Scanner",
            "Web Scanner", 
            "OSINT Scanner",
            "Brute Force",
            "Attack/Stress"
        ])
        layout.addWidget(scanner_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        scan_btn = QPushButton("Start Scan")
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(scan_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def start_scan():
            scanner_type = scanner_combo.currentText().lower().replace(" ", "_")
            self.scan_requested.emit(scanner_type, target.value)
            dialog.accept()
        
        scan_btn.clicked.connect(start_scan)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def edit_target(self, target: Target):
        """Edit target"""
        # Create edit dialog
        from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Target")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Name
        name_input = QLineEdit(target.name)
        layout.addRow("Name:", name_input)
        
        # Type
        type_combo = QComboBox()
        type_combo.addItems(["IP Address", "Domain", "URL", "IP Range", "File"])
        type_combo.setCurrentText(target.type.title())
        layout.addRow("Type:", type_combo)
        
        # Value
        value_input = QLineEdit(target.value)
        layout.addRow("Value:", value_input)
        
        # Description
        desc_input = QTextEdit(target.description)
        desc_input.setMaximumHeight(100)
        layout.addRow("Description:", desc_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        def save_changes():
            new_name = name_input.text().strip()
            new_type = type_combo.currentText().lower().replace(" ", "_")
            new_value = value_input.text().strip()
            new_desc = desc_input.toPlainText().strip()
            
            if not new_name or not new_value:
                QMessageBox.warning(dialog, "Input Error", "Name and value are required!")
                return
            
            if not self.target_store.validate_target(new_type, new_value):
                QMessageBox.warning(dialog, "Validation Error", f"Invalid {new_type} format!")
                return
            
            self.target_store.update_target(
                target.id,
                name=new_name,
                type=new_type,
                value=new_value,
                description=new_desc
            )
            
            dialog.accept()
        
        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def delete_target(self, target: Target):
        """Delete target"""
        reply = QMessageBox.question(
            self, "Delete Target",
            f"Are you sure you want to delete '{target.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.target_store.remove_target_by_id(target.id)
            self.target_removed.emit(target.value)
    
    def import_targets(self):
        """Import targets from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Targets", "", "JSON Files (*.json)"
        )
        
        if file_path:
            count = self.target_store.import_targets(file_path)
            QMessageBox.information(self, "Import Complete", f"Imported {count} targets")
    
    def export_targets(self):
        """Export targets to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Targets", "targets.json", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.target_store.export_targets(file_path):
                QMessageBox.information(self, "Export Complete", f"Targets exported to {file_path}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export targets")
    
    def clear_all_targets(self):
        """Clear all targets"""
        reply = QMessageBox.question(
            self, "Clear All Targets",
            "Are you sure you want to delete all targets?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.target_store.clear_all_targets()
    
    # Signal handlers
    @Slot(Target)
    def on_target_added_to_store(self, target: Target):
        """Handle target added to store"""
        self.refresh_targets()
    
    @Slot(str)
    def on_target_removed_from_store(self, target_id: str):
        """Handle target removed from store"""
        self.refresh_targets()
        self.details_text.setText("Select a target to view details...")
    
    @Slot(Target)
    def on_target_updated_in_store(self, target: Target):
        """Handle target updated in store"""
        self.refresh_targets()
        # Update details if currently selected
        current_row = self.targets_table.currentRow()
        if current_row >= 0:
            selected_id = self.targets_table.item(current_row, 0).data(Qt.UserRole)
            if selected_id == target.id:
                self.display_target_details(target)
