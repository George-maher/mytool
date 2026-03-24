"""
Target Manager Page for X-Shield MVC Architecture
Central page to manage targets with modern design
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTextEdit, QMessageBox, QFileDialog, QStyledItemDelegate
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPen, QBrush
from ui.components.styles import Colors, Spacing, Typography


class StatusDelegate(QStyledItemDelegate):
    """Custom delegate for coloring status items in Target Table"""

    def paint(self, painter, option, index):
        if index.column() == 2:  # Status column
            text = index.data()
            color = QColor(Colors.TEXT_MUTED)

            if text == "Active":
                color = QColor(Colors.SUCCESS)
            elif text == "Scanning":
                color = QColor(Colors.WARNING)
            elif text == "Completed":
                color = QColor(Colors.PRIMARY)
            elif text == "Failed":
                color = QColor(Colors.DANGER)

            painter.save()
            painter.setPen(QPen(color))
            painter.setFont(QFont(Typography.FAMILY_SANS, 10, QFont.Bold))
            painter.drawText(option.rect, Qt.AlignCenter, text)
            painter.restore()
        else:
            super().paint(painter, option, index)


class TargetManagerPage(QWidget):
    """Target Manager page with modern input forms and node inventory"""

    def __init__(self, target_manager, module_manager, logger, parent=None):
        super().__init__(parent)
        self.target_manager = target_manager
        self.module_manager = module_manager
        self.logger = logger

        self.setup_ui()
        self.setup_connections()
        self.load_targets()

    def setup_ui(self):
        """Setup target manager UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        layout.setSpacing(Spacing.XL)

        # Tool Header
        header = QFrame()
        header.setProperty("class", "ToolHeader")
        header_layout = QHBoxLayout(header)
        header_title = QLabel("Target Management")
        header_title.setStyleSheet(f"font-size: {Typography.H2_SIZE}; font-weight: 700; color: {Colors.PRIMARY};")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.active_status = QLabel("● NO ACTIVE NODE")
        self.active_status.setStyleSheet(f"color: {Colors.WARNING}; font-weight: 600; font-size: 12px;")
        header_layout.addWidget(self.active_status)
        layout.addWidget(header)

        # Main Content - Split into Form and Table
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Spacing.XL)

        # Left Side - Enrollment Form
        self.setup_enrollment_form(content_layout)

        # Right Side - Inventory Table
        self.setup_inventory_table(content_layout)

        layout.addLayout(content_layout)
        layout.addStretch()

    def setup_enrollment_form(self, parent_layout):
        """Setup enrollment form on left side"""
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_frame.setFixedWidth(320)

        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        form_layout.setSpacing(Spacing.LG)

        title = QLabel("ENROLL NODE")
        title.setStyleSheet(f"color: {Colors.ACCENT}; font-weight: 700; font-size: 12px; letter-spacing: 0.1em;")
        form_layout.addWidget(title)

        # Inputs
        v_layout = QVBoxLayout()
        v_layout.setSpacing(Spacing.MD)

        v_layout.addWidget(QLabel("TARGET ADDRESS"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g. 192.168.1.1 or example.com")
        v_layout.addWidget(self.target_input)

        v_layout.addWidget(QLabel("NODE TYPE"))
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems(["IP Address", "Domain", "URL", "IP Range"])
        v_layout.addWidget(self.target_type_combo)

        v_layout.addWidget(QLabel("DESCRIPTION"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Notes about this node...")
        self.description_input.setMaximumHeight(100)
        v_layout.addWidget(self.description_input)

        form_layout.addLayout(v_layout)

        self.add_target_btn = QPushButton("ENROLL TARGET")
        self.add_target_btn.setObjectName("primary_btn")
        form_layout.addWidget(self.add_target_btn)

        parent_layout.addWidget(form_frame)

        form_layout.addStretch()
        parent_layout.addWidget(form_frame)

    def setup_inventory_table(self, parent_layout):
        """Setup inventory table on right side"""
        table_frame = QFrame()
        table_frame.setObjectName("card")

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        table_layout.setSpacing(Spacing.LG)

        title_row = QHBoxLayout()
        title = QLabel("NODE INVENTORY")
        title.setStyleSheet(f"color: {Colors.ACCENT}; font-weight: 700; font-size: 12px; letter-spacing: 0.1em;")
        title_row.addWidget(title)
        title_row.addStretch()

        self.import_btn = QPushButton("IMPORT")
        self.import_btn.setProperty("class", "small")
        title_row.addWidget(self.import_btn)

        self.export_btn = QPushButton("EXPORT")
        self.export_btn.setProperty("class", "small")
        title_row.addWidget(self.export_btn)

        table_layout.addLayout(title_row)

        self.target_table = QTableWidget()
        self.target_table.setColumnCount(5)
        self.target_table.setHorizontalHeaderLabels([
            "ADDRESS", "TYPE", "STATUS", "DESCRIPTION", "ACTIONS"
        ])
        self.target_table.setItemDelegateForColumn(2, StatusDelegate(self.target_table))

        header = self.target_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.target_table.setColumnWidth(4, 120)

        self.target_table.verticalHeader().setVisible(False)
        self.target_table.setShowGrid(False)

        table_layout.addWidget(self.target_table)
        parent_layout.addWidget(table_frame)

    def setup_connections(self):
        """Setup signal connections"""
        self.add_target_btn.clicked.connect(self.add_target)
        self.import_btn.clicked.connect(self.import_targets)
        self.export_btn.clicked.connect(self.export_targets)

        if self.target_manager:
            self.target_manager.target_added.connect(self.on_target_added)
            self.target_manager.target_removed.connect(self.on_target_removed)
            self.target_manager.target_updated.connect(self.on_target_updated)
            self.target_manager.active_target_changed.connect(self.on_active_target_changed)

    def add_target(self):
        """Add new target"""
        value = self.target_input.text().strip()
        t_type = self.target_type_combo.currentText()
        desc = self.description_input.toPlainText().strip()

        if not value:
            QMessageBox.warning(self, "Invalid Input", "Target address is required.")
            return

        if self.target_manager:
            try:
                self.target_manager.add_target(t_type, value, desc)
                self.target_input.clear()
                self.description_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add target: {e}")

    def load_targets(self):
        """Populate table with targets"""
        if not self.target_manager: return
        targets = self.target_manager.get_all_targets()
        self.target_table.setRowCount(len(targets))
        for row, target in enumerate(targets):
            self.target_table.setItem(row, 0, QTableWidgetItem(target.value))
            self.target_table.setItem(row, 1, QTableWidgetItem(target.type))
            self.target_table.setItem(row, 2, QTableWidgetItem(target.status))
            self.target_table.setItem(row, 3, QTableWidgetItem(target.description or "No notes"))

            actions = QWidget()
            al = QHBoxLayout(actions); al.setContentsMargins(4,4,4,4); al.setSpacing(4)
            btn_act = QPushButton("🎯"); btn_act.setFixedSize(24,24); btn_act.setToolTip("Set Active")
            btn_act.clicked.connect(lambda chk, tid=target.id: self.target_manager.set_active_target(tid))
            btn_del = QPushButton("🗑️"); btn_del.setFixedSize(24,24); btn_del.setToolTip("Delete")
            btn_del.clicked.connect(lambda chk, tid=target.id: self.target_manager.remove_target(tid))
            al.addWidget(btn_act); al.addWidget(btn_del)
            self.target_table.setCellWidget(row, 4, actions)

    def import_targets(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Targets", "", "JSON Files (*.json)")
        if path and self.target_manager: self.target_manager.import_targets(path)

    def export_targets(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Targets", "targets.json", "JSON Files (*.json)")
        if path and self.target_manager: self.target_manager.export_targets(path)

    @Slot(str, dict)
    def on_target_added(self, tid, data): self.load_targets()
    @Slot(str)
    def on_target_removed(self, tid): self.load_targets()
    @Slot(str, dict)
    def on_target_updated(self, tid, data): self.load_targets()
    @Slot(str, dict)
    def on_active_target_changed(self, tid, data):
        if data:
            self.active_status.setText(f"● ACTIVE NODE: {data['value']}")
            self.active_status.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 600; font-size: 12px;")
        else:
            self.active_status.setText("● NO ACTIVE NODE")
            self.active_status.setStyleSheet(f"color: {Colors.WARNING}; font-weight: 600; font-size: 12px;")

    def on_enter(self):
        self.load_targets()
        if self.target_manager:
            at = self.target_manager.get_active_target()
            if at: self.on_active_target_changed(at.id, at.to_dict())
