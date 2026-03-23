"""
Base View for X-Shield Framework
MVC View base class with common UI functionality
"""

from typing import Any, Dict, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

from mvc.base import BaseView as MVCBaseView


class BaseView(MVCBaseView):
    """Base class for all UI views in X-Shield"""
    
    # Additional signals specific to UI
    ui_ready = Signal()
    ui_error = Signal(str)
    ui_warning = Signal(str)
    ui_info = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._main_widget = None
        self._layout = None
        self._components = {}
        self._styles = {
            'primary': '#2196F3',
            'secondary': '#FF9800',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'danger': '#F44336',
            'info': '#00BCD4',
            'dark': '#212121',
            'light': '#FFFFFF',
            'gray': '#9E9E9E'
        }
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup basic UI structure"""
        self._main_widget = QWidget()
        self._layout = QVBoxLayout(self._main_widget)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)
        
        # Setup the specific view
        self.setup_view()
        
        # Emit ready signal
        self.ui_ready.emit()
    
    def setup_view(self):
        """Setup the specific view UI (to be implemented by subclasses)"""
        pass
    
    def get_widget(self) -> QWidget:
        """Get the main widget for this view"""
        return self._main_widget
    
    def add_component(self, name: str, component: QWidget) -> None:
        """Add a component to the view"""
        self._components[name] = component
    
    def get_component(self, name: str) -> Optional[QWidget]:
        """Get a component by name"""
        return self._components.get(name)
    
    def remove_component(self, name: str) -> bool:
        """Remove a component"""
        if name in self._components:
            component = self._components.pop(name)
            if component and hasattr(component, 'deleteLater'):
                component.deleteLater()
            return True
        return False
    
    def clear_components(self) -> None:
        """Clear all components"""
        for component in self._components.values():
            if hasattr(component, 'deleteLater'):
                component.deleteLater()
        self._components.clear()
    
    # Styling utilities
    def get_style(self, style_name: str) -> str:
        """Get a style color by name"""
        return self._styles.get(style_name, '#000000')
    
    def create_label(self, text: str, style: str = 'normal', size: int = 12) -> QLabel:
        """Create a styled label"""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(size)
        
        if style == 'header':
            font.setBold(True)
            label.setStyleSheet(f"color: {self.get_style('primary')};")
        elif style == 'title':
            font.setBold(True)
            font.setPointSize(size + 2)
            label.setStyleSheet(f"color: {self.get_style('dark')};")
        elif style == 'subtitle':
            font.setBold(True)
            label.setStyleSheet(f"color: {self.get_style('gray')};")
        elif style == 'error':
            label.setStyleSheet(f"color: {self.get_style('danger')};")
        elif style == 'success':
            label.setStyleSheet(f"color: {self.get_style('success')};")
        elif style == 'warning':
            label.setStyleSheet(f"color: {self.get_style('warning')};")
        elif style == 'info':
            label.setStyleSheet(f"color: {self.get_style('info')};")
        
        label.setFont(font)
        return label
    
    def create_button(self, text: str, style: str = 'primary') -> QWidget:
        """Create a styled button"""
        from PySide6.QtWidgets import QPushButton
        
        button = QPushButton(text)
        button.setMinimumHeight(32)
        
        if style == 'primary':
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.get_style('primary')};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                QPushButton:pressed {{
                    background-color: #0D47A1;
                }}
                QPushButton:disabled {{
                    background-color: {self.get_style('gray')};
                    color: white;
                }}
            """)
        elif style == 'secondary':
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.get_style('secondary')};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #F57C00;
                }}
                QPushButton:pressed {{
                    background-color: #E65100;
                }}
                QPushButton:disabled {{
                    background-color: {self.get_style('gray')};
                    color: white;
                }}
            """)
        elif style == 'success':
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.get_style('success')};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #388E3C;
                }}
                QPushButton:pressed {{
                    background-color: #1B5E20;
                }}
                QPushButton:disabled {{
                    background-color: {self.get_style('gray')};
                    color: white;
                }}
            """)
        elif style == 'danger':
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.get_style('danger')};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #D32F2F;
                }}
                QPushButton:pressed {{
                    background-color: #B71C1C;
                }}
                QPushButton:disabled {{
                    background-color: {self.get_style('gray')};
                    color: white;
                }}
            """)
        elif style == 'outline':
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.get_style('primary')};
                    border: 2px solid {self.get_style('primary')};
                    border-radius: 4px;
                    padding: 6px 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.get_style('primary')};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: #1976D2;
                    color: white;
                }}
                QPushButton:disabled {{
                    border-color: {self.get_style('gray')};
                    color: {self.get_style('gray')};
                }}
            """)
        
        return button
    
    def create_input_field(self, placeholder: str = "", input_type: str = 'text') -> QWidget:
        """Create an input field"""
        from PySide6.QtWidgets import QLineEdit, QSpinBox, QDoubleSpinBox
        
        if input_type == 'text':
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: white;
                    border: 1px solid #DDDDDD;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {self.get_style('primary')};
                }}
            """)
            return field
        elif input_type == 'number':
            field = QSpinBox()
            field.setRange(0, 999999)
            field.setStyleSheet(f"""
                QSpinBox {{
                    background-color: white;
                    border: 1px solid #DDDDDD;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
                QSpinBox:focus {{
                    border: 2px solid {self.get_style('primary')};
                }}
            """)
            return field
        elif input_type == 'decimal':
            field = QDoubleSpinBox()
            field.setRange(0.0, 999999.0)
            field.setStyleSheet(f"""
                QDoubleSpinBox {{
                    background-color: white;
                    border: 1px solid #DDDDDD;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                }}
                QDoubleSpinBox:focus {{
                    border: 2px solid {self.get_style('primary')};
                }}
            """)
            return field
    
    def create_combo_box(self, items: list = None) -> QWidget:
        """Create a combo box"""
        from PySide6.QtWidgets import QComboBox
        
        combo = QComboBox()
        if items:
            combo.addItems(items)
        
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                min-width: 150px;
            }}
            QComboBox:focus {{
                border: 2px solid {self.get_style('primary')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {self.get_style('gray')};
                margin-right: 4px;
            }}
        """)
        
        return combo
    
    def create_progress_bar(self) -> QWidget:
        """Create a progress bar"""
        from PySide6.QtWidgets import QProgressBar
        
        progress = QProgressBar()
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {self.get_style('primary')};
                border-radius: 4px;
            }}
        """)
        
        return progress
    
    def create_status_indicator(self, status: str = 'normal') -> QWidget:
        """Create a status indicator"""
        from PySide6.QtWidgets import QWidget
        
        indicator = QWidget()
        indicator.setFixedSize(12, 12)
        
        colors = {
            'normal': self.get_style('success'),
            'warning': self.get_style('warning'),
            'error': self.get_style('danger'),
            'info': self.get_style('info'),
            'disabled': self.get_style('gray')
        }
        
        color = colors.get(status, self.get_style('gray'))
        indicator.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        
        return indicator
    
    def show_message(self, message: str, message_type: str = 'info') -> None:
        """Show a message to the user"""
        if message_type == 'error':
            self.ui_error.emit(message)
        elif message_type == 'warning':
            self.ui_warning.emit(message)
        elif message_type == 'info':
            self.ui_info.emit(message)
        else:
            self.ui_info.emit(message)
    
    def set_loading(self, loading: bool) -> None:
        """Set loading state"""
        # Disable/enable components during loading
        for component in self._components.values():
            if hasattr(component, 'setEnabled'):
                component.setEnabled(not loading)
    
    def refresh_view(self) -> None:
        """Refresh the view with current data"""
        # Update all components with current data
        if self._data:
            self.update_components_with_data()
    
    def update_components_with_data(self) -> None:
        """Update components with current data (to be implemented by subclasses)"""
        pass
    
    def validate_input(self) -> tuple[bool, str]:
        """Validate user input (to be implemented by subclasses)"""
        return True, ""
    
    def collect_user_input(self) -> Any:
        """Collect user input from components (to be implemented by subclasses)"""
        return {}
    
    # Layout utilities
    def add_to_layout(self, widget: QWidget, stretch: int = 0) -> None:
        """Add widget to main layout"""
        if self._layout:
            self._layout.addWidget(widget, stretch)
    
    def add_spacing(self, spacing: int) -> None:
        """Add spacing to layout"""
        if self._layout:
            self._layout.addSpacing(spacing)
    
    def add_stretch(self, stretch: int = 1) -> None:
        """Add stretch to layout"""
        if self._layout:
            self._layout.addStretch(stretch)
    
    def clear_layout(self) -> None:
        """Clear all widgets from layout"""
        if self._layout:
            while self._layout.count():
                item = self._layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
