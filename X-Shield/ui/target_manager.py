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
        """Setup target manager UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Target Manager")
        header_label.setFont(QFont("Roboto", 24, QFont.Bold))
        header_label.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Toolbar
        self.setup_toolbar(layout)
        
        # Add target section
        self.setup_add_target_section(layout)
        
        # Targets table
        self.setup_targets_table(layout)
        
        # Target details section
        self.setup_target_details(layout)
    
    def setup_toolbar(self, parent_layout):
        """Setup toolbar for target operations"""
        toolbar_frame = QFrame()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Import/Export buttons
        self.import_btn = QPushButton("Import Targets")
        self.import_btn.setIcon(QIcon("icons/import.png"))
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.export_btn = QPushButton("Export Targets")
        self.export_btn.setIcon(QIcon("icons/export.png"))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Clear all button
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setIcon(QIcon("icons/clear.png"))
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(QIcon("icons/refresh.png"))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        
        toolbar_layout.addWidget(self.import_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.clear_all_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.refresh_btn)
        
        parent_layout.addWidget(toolbar_frame)
    
    def setup_add_target_section(self, parent_layout):
        """Setup add target section"""
        add_group = QGroupBox("Add New Target")
        add_group.setStyleSheet("""
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
        
        add_layout = QFormLayout(add_group)
        
        # Target name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter target name...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                selection-background-color: #2196F3;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #333333;

            }
            QLineEdit:disabled {
                background-color: #1e1e1e;
                color: #666666;
                border-color: #303030;
            }
        """)
        add_layout.addRow("Name:", self.name_input)
        
        # Target type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["IP Address", "Domain", "URL", "IP Range", "File"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                min-width: 250px;
                min-height: 24px;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
                background-color: #333333;

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
                padding: 16px 20px;
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
        add_layout.addRow("Type:", self.type_combo)
        
        # Target value
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter target value (IP, domain, URL, etc.)...")
        self.value_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                selection-background-color: #2196F3;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #333333;

            }
            QLineEdit:disabled {
                background-color: #1e1e1e;
                color: #666666;
                border-color: #303030;
            }
        """)
        add_layout.addRow("Value:", self.value_input)
        
        # Buttonscription
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        add_layout.addRow("Description:", self.description_input)
        
        # Add button
        self.add_target_btn = QPushButton("Add Target")
        self.add_target_btn.setIcon(QIcon("icons/add.png"))
        self.add_target_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        add_layout.addRow("", self.add_target_btn)
        
        parent_layout.addWidget(add_group)
    
    def setup_targets_table(self, parent_layout):
        """Setup targets table"""
        table_group = QGroupBox("Targets")
        table_group.setStyleSheet("""
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
        
        table_layout = QVBoxLayout(table_group)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search targets...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        table_layout.addLayout(search_layout)
        
        # Targets table
        self.targets_table = QTableWidget()
        self.targets_table.setColumnCount(7)
        self.targets_table.setHorizontalHeaderLabels([
            "Name", "Type", "Value", "Description", "Scan Count", "Last Scanned", "Actions"
        ])
        
        # Table styling
        self.targets_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
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
            QHeaderView::section:hover {
                background-color: #505050;
            }
        """)
        
        # Table properties
        header = self.targets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Value
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Scan Count
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Last Scanned
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        self.targets_table.setAlternatingRowColors(True)
        self.targets_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.targets_table.setSortingEnabled(True)
        
        table_layout.addWidget(self.targets_table)
        
        parent_layout.addWidget(table_group)
    
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
        """Populate table with targets"""
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
            desc_item = QTableWidgetItem(target.description[:50] + "..." if len(target.description) > 50 else target.description)
            self.targets_table.setItem(row, 3, desc_item)
            
            # Scan Count
            scan_count_item = QTableWidgetItem(str(target.scan_count))
            self.targets_table.setItem(row, 4, scan_count_item)
            
            # Last Scanned
            last_scanned = target.last_scanned
            if last_scanned:
                # Format date
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(last_scanned)
                    last_scanned_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    last_scanned_str = last_scanned[:16]
            else:
                last_scanned_str = "Never"
            
            last_scanned_item = QTableWidgetItem(last_scanned_str)
            self.targets_table.setItem(row, 5, last_scanned_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            # Scan button
            scan_btn = QPushButton("Scan")
            scan_btn.setStyleSheet("""
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
            scan_btn.clicked.connect(lambda checked, t=target: self.scan_target(t))
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            edit_btn.clicked.connect(lambda checked, t=target: self.edit_target(t))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
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
