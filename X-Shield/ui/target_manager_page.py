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
from PySide6.QtGui import QFont


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
        """Setup target manager UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Target Manager")
        title_label.setObjectName("title")
        title_label.setFont(QFont("Roboto", 28, QFont.Bold))
        title_label.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title_label)
        
        # Target Input Section
        self.setup_target_input(layout)
        
        # Target Table Section
        self.setup_target_table(layout)
        
        # Action Buttons Section
        self.setup_action_buttons(layout)
        
        layout.addStretch()
    
    def setup_target_input(self, parent_layout):
        """Setup target input section"""
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(16)
        
        # Section title
        section_title = QLabel("Add New Target")
        section_title.setObjectName("section_title")
        section_title.setFont(QFont("Roboto", 20, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        input_layout.addWidget(section_title)
        
        # Input form
        form_layout = QGridLayout()
        form_layout.setSpacing(16)
        
        # Target IP/URL
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target IP, domain, or URL...")
        self.target_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                selection-background-color: #2e7d32;
                min-height: 28px;
            }
            QLineEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
                box-shadow: 0 0 12px rgba(46, 125, 50, 0.4);
            }
        """)
        form_layout.addWidget(QLabel("Target IP/URL:"), 0, 0)
        form_layout.addWidget(self.target_input, 0, 1)
        
        # Target Type
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems(["IP Address", "Domain", "URL", "IP Range", "File"])
        self.target_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                min-width: 250px;
                min-height: 28px;
            }
            QComboBox:focus {
                border: 2px solid #2e7d32;
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
                selection-background-color: #2e7d32;
                selection-color: white;
                font-size: 15px;
                padding: 8px;
            }
        """)
        form_layout.addWidget(QLabel("Target Type:"), 1, 0)
        form_layout.addWidget(self.target_type_combo, 1, 1)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description...")
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px 20px;
                color: #ffffff;
                font-size: 16px;
                selection-background-color: #2e7d32;
            }
            QTextEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #333333;
                box-shadow: 0 0 12px rgba(46, 125, 50, 0.4);
            }
        """)
        form_layout.addWidget(QLabel("Description:"), 2, 0)
        form_layout.addWidget(self.description_input, 2, 1)
        
        input_layout.addLayout(form_layout)
        
        # Add button
        self.add_target_btn = QPushButton("🎯 Add Target")
        self.add_target_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 18px;
                min-width: 200px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #388e3c;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(46, 125, 50, 0.4);
            }
            QPushButton:pressed {
                background-color: #1b5e20;
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(46, 125, 50, 0.3);
            }
        """)
        input_layout.addWidget(self.add_target_btn)
        
        parent_layout.addWidget(input_frame)
    
    def setup_target_table(self, parent_layout):
        """Setup target table section"""
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 24px;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setSpacing(16)
        
        # Section title
        section_title = QLabel("Managed Targets")
        section_title.setObjectName("section_title")
        section_title.setFont(QFont("Roboto", 20, QFont.Bold))
        section_title.setStyleSheet("color: #2e7d32;")
        table_layout.addWidget(section_title)
        
        # Target table
        self.target_table = QTableWidget()
        self.target_table.setColumnCount(6)
        self.target_table.setHorizontalHeaderLabels([
            "Target", "Type", "Status", "Description", "Created", "Actions"
        ])
        
        # Setup table styling
        self.target_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                gridline-color: #404040;
                color: #ffffff;
                selection-background-color: #2e7d32;
                alternate-background-color: #333333;
                font-size: 15px;
            }
            QTableWidget::item {
                padding: 16px;
                border-bottom: 1px solid #404040;
                min-height: 24px;
            }
            QTableWidget::item:selected {
                background-color: #2e7d32;
                color: white;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 16px;
                border: none;
                font-weight: 600;
                font-size: 16px;
                border-bottom: 3px solid #2e7d32;
            }
        """)
        
        # Set column widths
        header = self.target_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Target
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Actions
        header.resizeSection(5, 140)
        
        # Set row height
        self.target_table.verticalHeader().setDefaultSectionSize(60)
        self.target_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.target_table)
        
        parent_layout.addWidget(table_frame)
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons section"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        # Import/Export buttons
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                min-width: 120px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
            }
        """)
        buttons_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                min-width: 120px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #F57C00;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(255, 152, 0, 0.4);
            }
            QPushButton:pressed {
                background-color: #E65100;
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
            }
        """)
        buttons_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                min-width: 120px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #da190b;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(244, 67, 54, 0.4);
            }
            QPushButton:pressed {
                background-color: #b71c1c;
                transform: translateY(0px);
                box-shadow: 0 2px 4px rgba(244, 67, 54, 0.3);
            }
        """)
        buttons_layout.addWidget(self.clear_btn)
        
        buttons_layout.addStretch()
        
        # Active target indicator
        self.active_target_label = QLabel("No active target")
        self.active_target_label.setObjectName("subtitle")
        self.active_target_label.setFont(QFont("Roboto", 16, QFont.Bold))
        self.active_target_label.setStyleSheet("color: #FF9800;")
        buttons_layout.addWidget(self.active_target_label)
        
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
                status_item.setStyleSheet("color: #4CAF50;")
            elif target.status == "Scanning":
                status_item.setStyleSheet("color: #FF9800;")
            elif target.status == "Completed":
                status_item.setStyleSheet("color: #2196F3;")
            else:
                status_item.setStyleSheet("color: #f44336;")
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
        """Create actions widget for table row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Set Active button
        active_btn = QPushButton("🎯")
        active_btn.setToolTip("Set as Active Target")
        active_btn.setFixedSize(40, 40)
        active_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #388e3c;
                transform: scale(1.1);
            }
        """)
        active_btn.clicked.connect(lambda: self.set_active_target(target_id))
        layout.addWidget(active_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Edit Target")
        edit_btn.setFixedSize(40, 40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: scale(1.1);
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_target(target_id))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete Target")
        delete_btn.setFixedSize(40, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #da190b;
                transform: scale(1.1);
            }
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
            self.active_target_label.setText(f"Active: {target_data['value']}")
            self.active_target_label.setStyleSheet("color: #4CAF50;")
        else:
            self.active_target_label.setText("No active target")
            self.active_target_label.setStyleSheet("color: #FF9800;")
    
    def on_enter(self):
        """Called when page is entered"""
        self.load_targets()
        if self.logger:
            self.logger.info("Target Manager page entered")
