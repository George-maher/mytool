"""
Terminal Widget for X-Shield Framework
Real-time log display with terminal-like interface
"""

from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat
from datetime import datetime


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
        """Setup terminal UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Terminal display
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 10))
        layout.addWidget(self.terminal)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_terminal)
        button_layout.addWidget(self.clear_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_btn)
        
        layout.addLayout(button_layout)
        
        # State
        self.paused = False
        self.max_lines = 1000
    
    def setup_styles(self):
        """Setup terminal styles"""
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:checked {
                background-color: #dc2626;
            }
        """)
    
    def append_log(self, level, message, timestamp):
        """Append log message to terminal"""
        if self.paused:
            return
        
        # Format message
        formatted_time = timestamp.split()[1]  # Get time part only
        formatted_message = f"[{formatted_time}] {level}: {message}"
        
        # Move cursor to end
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Apply color based on level
        char_format = QTextCharFormat()
        
        if level == "DEBUG":
            char_format.setForeground(QColor("#00ffff"))  # Cyan
        elif level == "INFO":
            char_format.setForeground(QColor("#00ff00"))  # Green
        elif level == "WARNING":
            char_format.setForeground(QColor("#ffff00"))  # Yellow
        elif level == "ERROR":
            char_format.setForeground(QColor("#ff0000"))  # Red
        elif level == "CRITICAL":
            char_format.setForeground(QColor("#ff00ff"))  # Magenta
        elif level == "SUCCESS":
            char_format.setForeground(QColor("#00ff88"))  # Light green
        else:
            char_format.setForeground(QColor("#ffffff"))  # White
        
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
