"""
Terminal Widget for X-Shield Framework
Real-time log display with terminal-like interface
"""

from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat
from datetime import datetime
from ui.components.styles import Colors, Spacing, Typography


class TerminalWidget(QWidget):
    """Terminal-like widget for real-time log display"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        
        # Auto-scroll timer
        self.auto_scroll_timer = QTimer()
        self.auto_scroll_timer.timeout.connect(self.auto_scroll)
        self.auto_scroll_timer.start(100)
    
    def setup_ui(self):
        """Setup terminal UI with modern minimal design"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # Terminal display
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont(Typography.FAMILY_MONO, 10))
        layout.addWidget(self.terminal)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Spacing.SM)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setProperty("class", "small")
        self.clear_btn.clicked.connect(self.clear_terminal)
        button_layout.addWidget(self.clear_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setProperty("class", "small")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # State
        self.paused = False
        self.max_lines = 1000
    
    def setup_styles(self):
        """Setup terminal styles with design system"""
        self.terminal.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: {Spacing.MD}px;
            }}
        """)
        
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Colors.BORDER};
                color: {Colors.DANGER};
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.DANGER};
            }}
        """)
        
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Colors.BORDER};
                color: {Colors.INFO};
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_LIGHT};
                border-color: {Colors.INFO};
            }}
            QPushButton:checked {{
                background-color: {Colors.INFO};
                color: {Colors.BACKGROUND};
                border-color: {Colors.INFO};
            }}
        """)
    
    def append_log(self, level, message, timestamp):
        """Append log message to terminal with design system colors"""
        if self.paused:
            return
        
        # Format message
        try:
            formatted_time = timestamp.split()[1]  # Get time part only
        except IndexError:
            formatted_time = timestamp

        formatted_message = f"[{formatted_time}] {level}: {message}"
        
        # Move cursor to end
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Apply color based on level
        char_format = QTextCharFormat()
        
        if level == "DEBUG":
            char_format.setForeground(QColor(Colors.TEXT_MUTED))
        elif level == "INFO":
            char_format.setForeground(QColor(Colors.PRIMARY))
        elif level == "WARNING":
            char_format.setForeground(QColor(Colors.WARNING))
        elif level == "ERROR" or level == "CRITICAL":
            char_format.setForeground(QColor(Colors.DANGER))
        elif level == "SUCCESS":
            char_format.setForeground(QColor(Colors.SUCCESS))
        else:
            char_format.setForeground(QColor(Colors.TEXT_PRIMARY))
        
        cursor.setCharFormat(char_format)
        cursor.insertText(formatted_message + "\n")
        
        # Limit lines to prevent memory issues
        self.limit_lines()
        
        # Auto-scroll to bottom
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()
    
    def limit_lines(self):
        """Limit the number of lines in terminal"""
        document = self.terminal.document()
        if document.blockCount() > self.max_lines:
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 
                              document.blockCount() - self.max_lines)
            cursor.removeSelectedText()
    
    def auto_scroll(self):
        """Auto-scroll to bottom if needed"""
        scrollbar = self.terminal.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 10:
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_terminal(self):
        """Clear terminal content"""
        self.terminal.clear()
    
    def toggle_pause(self, checked):
        """Toggle pause state"""
        self.paused = checked
        self.pause_btn.setText("Resume" if checked else "Pause")
    
    def export_logs(self, file_path):
        """Export terminal content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.terminal.toPlainText())
            return True
        except Exception:
            return False
