"""
Output Console Component for X-Shield Framework
Terminal-like console for live logs with Material Design
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QComboBox, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat


class OutputConsole(QWidget):
    """Terminal-like output console with Material Design styling"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.max_lines = 1000  # Maximum lines to keep in console
        
    def setup_ui(self):
        """Setup output console UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Console header
        self.setup_header(layout)
        
        # Console output area
        self.setup_console_area(layout)
        
        # Console controls
        self.setup_controls(layout)
    
    def setup_header(self, parent_layout):
        """Setup console header"""
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2d2d2d;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        # Title
        title = QLabel("Output Console")
        title.setFont(QFont("Roboto", 12, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Roboto", 16))
        self.status_indicator.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(self.status_indicator)
        
        header_layout.addStretch()
        
        # Line count
        self.line_count_label = QLabel("0 lines")
        self.line_count_label.setFont(QFont("Roboto", 10))
        self.line_count_label.setStyleSheet("color: #888888;")
        header_layout.addWidget(self.line_count_label)
        
        parent_layout.addWidget(header)
    
    def setup_console_area(self, parent_layout):
        """Setup console output area"""
        # Console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                padding: 8px;
                selection-background-color: #264f78;
            }
            QTextEdit:focus {
                border: none;
            }
        """)
        
        parent_layout.addWidget(self.console)
    
    def setup_controls(self, parent_layout):
        """Setup console controls"""
        controls_frame = QFrame()
        controls_frame.setFixedHeight(40)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-top: 1px solid #2d2d2d;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(12, 8, 12, 8)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Info", "Success", "Warning", "Error"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
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
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addStretch()
        
        # Control buttons
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        controls_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("Save Log")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        controls_layout.addWidget(self.save_btn)
        
        parent_layout.addWidget(controls_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.clear_btn.clicked.connect(self.clear)
        self.save_btn.clicked.connect(self.save_log)
        self.filter_combo.currentTextChanged.connect(self.filter_messages)
    
    def append_message(self, message, level="info", timestamp=None):
        """Append message to console
        
        Args:
            message: Message text
            level: Message level ('info', 'success', 'warning', 'error')
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format timestamp
        timestamp_str = timestamp.strftime("%H:%M:%S")
        
        # Create formatted message
        formatted_message = f"[{timestamp_str}] {message}"
        
        # Move cursor to end
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set text color based on level
        char_format = cursor.charFormat()
        
        if level == "info":
            char_format.setForeground(QColor("#58a6ff"))  # Blue
        elif level == "success":
            char_format.setForeground(QColor("#3fb950"))  # Green
        elif level == "warning":
            char_format.setForeground(QColor("#d29922"))  # Yellow
        elif level == "error":
            char_format.setForeground(QColor("#f85149"))  # Red
        else:
            char_format.setForeground(QColor("#c9d1d9"))  # Default gray
        
        cursor.setCharFormat(char_format)
        cursor.insertText(formatted_message + "\n")
        
        # Auto-scroll to bottom
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()
        
        # Limit number of lines
        self.limit_lines()
        
        # Update line count
        self.update_line_count()
    
    def limit_lines(self):
        """Limit console to max_lines"""
        document = self.console.document()
        if document.blockCount() > self.max_lines:
            # Remove oldest lines
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.Start)
            
            lines_to_remove = document.blockCount() - self.max_lines
            for _ in range(lines_to_remove):
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Remove newline
    
    def update_line_count(self):
        """Update line count display"""
        line_count = self.console.document().blockCount()
        self.line_count_label.setText(f"{line_count} lines")
    
    def filter_messages(self, filter_level):
        """Filter messages by level"""
        # This is a simplified filter - in a real implementation,
        # you would store messages separately and rebuild the display
        pass
    
    def clear(self):
        """Clear console"""
        self.console.clear()
        self.update_line_count()
    
    def save_log(self):
        """Save console log to file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Console Log", f"xshield_console_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.console.toPlainText())
                self.append_message(f"Log saved to {file_path}", "success")
            except Exception as e:
                self.append_message(f"Failed to save log: {str(e)}", "error")
    
    # Convenience methods for different log levels
    @Slot(str)
    def log_info(self, message):
        """Log info message"""
        self.append_message(message, "info")
    
    @Slot(str)
    def log_success(self, message):
        """Log success message"""
        self.append_message(message, "success")
        self.status_indicator.setStyleSheet("color: #3fb950;")
        # Reset status indicator after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_indicator.setStyleSheet("color: #4CAF50;"))
    
    @Slot(str)
    def log_warning(self, message):
        """Log warning message"""
        self.append_message(message, "warning")
        self.status_indicator.setStyleSheet("color: #d29922;")
        # Reset status indicator after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_indicator.setStyleSheet("color: #4CAF50;"))
    
    @Slot(str)
    def log_error(self, message):
        """Log error message"""
        self.append_message(message, "error")
        self.status_indicator.setStyleSheet("color: #f85149;")
        # Reset status indicator after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_indicator.setStyleSheet("color: #4CAF50;"))
    
    @Slot(str)
    def log_debug(self, message):
        """Log debug message"""
        self.append_message(f"[DEBUG] {message}", "info")
    
    @Slot(str, str)
    def log_scanner_start(self, scanner_name, target):
        """Log scanner start"""
        self.append_message(f"🚀 Starting {scanner_name} scan on {target}", "info")
    
    @Slot(str, str, str)
    def log_scanner_progress(self, scanner_name, target, progress):
        """Log scanner progress"""
        self.append_message(f"📊 {scanner_name} on {target}: {progress}", "info")
    
    @Slot(str, str, dict)
    def log_scanner_complete(self, scanner_name, target, results):
        """Log scanner completion"""
        vuln_count = len(results.get('vulnerabilities', []))
        self.append_message(
            f"✅ {scanner_name} on {target} completed - {vuln_count} issues found", 
            "success"
        )
    
    @Slot(str, str, str)
    def log_scanner_error(self, scanner_name, target, error):
        """Log scanner error"""
        self.append_message(f"❌ {scanner_name} on {target} failed: {error}", "error")
    
    @Slot(str)
    def log_target_added(self, target_name):
        """Log target addition"""
        self.append_message(f"➕ Target added: {target_name}", "success")
    
    @Slot(str)
    def log_target_removed(self, target_name):
        """Log target removal"""
        self.append_message(f"➖ Target removed: {target_name}", "warning")
    
    @Slot(str)
    def log_report_generated(self, report_path):
        """Log report generation"""
        self.append_message(f"📋 Report generated: {report_path}", "success")
    
    @Slot(str)
    def log_module_loaded(self, module_name):
        """Log module loading"""
        self.append_message(f"🔧 Module loaded: {module_name}", "info")
    
    @Slot(str)
    def log_settings_updated(self, setting_name):
        """Log settings update"""
        self.append_message(f"⚙️ Settings updated: {setting_name}", "info")
    
    def get_log_text(self):
        """Get all log text"""
        return self.console.toPlainText()
    
    def set_max_lines(self, max_lines):
        """Set maximum number of lines"""
        self.max_lines = max_lines
        self.limit_lines()
