"""
Base View for X-Shield Framework
MVC View base class with common UI functionality
"""

from typing import Any, Dict, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from ui.styles import Colors, Spacing, Typography

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
            'primary': Colors.PRIMARY,
            'secondary': Colors.WARNING,
            'success': Colors.SUCCESS,
            'warning': Colors.WARNING,
            'danger': Colors.DANGER,
            'info': Colors.INFO,
            'dark': Colors.BACKGROUND,
            'light': Colors.TEXT_PRIMARY,
            'gray': Colors.TEXT_MUTED
        }
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup basic UI structure"""
        self._main_widget = QWidget()
        self._layout = QVBoxLayout(self._main_widget)
        self._layout.setContentsMargins(Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN, Spacing.PAGE_MARGIN)
        self._layout.setSpacing(Spacing.XL)
        
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
    
    def create_label(self, text: str, style: str = 'normal', size: int = 14) -> QLabel:
        """Create a styled label using the design system"""
        label = QLabel(text)
        
        if style == 'header':
            label.setObjectName("title")
            label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 700; font-size: {Typography.H1_SIZE};")
        elif style == 'title':
            label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600; font-size: {Typography.H2_SIZE};")
        elif style == 'subtitle':
            label.setObjectName("subtitle")
            label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.BODY_SIZE};")
        elif style == 'error':
            label.setStyleSheet(f"color: {Colors.DANGER}; font-weight: 500;")
        elif style == 'success':
            label.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 500;")
        elif style == 'warning':
            label.setStyleSheet(f"color: {Colors.WARNING}; font-weight: 500;")
        elif style == 'info':
            label.setStyleSheet(f"color: {Colors.INFO}; font-weight: 500;")
        
        return label
    
    def create_button(self, text: str, style: str = 'primary') -> QWidget:
        """Create a styled button using the design system"""
        from PySide6.QtWidgets import QPushButton
        
        button = QPushButton(text)
        
        if style == 'primary':
            button.setObjectName("primary_btn")
        elif style == 'secondary':
            pass # Uses default button style
        elif style == 'success':
            button.setStyleSheet(f"QPushButton {{ background-color: {Colors.SUCCESS}; color: {Colors.BACKGROUND}; border-color: {Colors.SUCCESS}; }}")
        elif style == 'danger':
            button.setStyleSheet(f"QPushButton {{ background-color: {Colors.DANGER}; color: white; border-color: {Colors.DANGER}; }}")
        elif style == 'outline':
            button.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {Colors.PRIMARY}; border-color: {Colors.PRIMARY}; }}")
        
        return button
    
    def create_input_field(self, placeholder: str = "", input_type: str = 'text') -> QWidget:
        """Create an input field using the design system"""
        from PySide6.QtWidgets import QLineEdit, QSpinBox, QDoubleSpinBox
        
        if input_type == 'text':
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            return field
        elif input_type == 'number':
            field = QSpinBox()
            field.setRange(0, 999999)
            return field
        elif input_type == 'decimal':
            field = QDoubleSpinBox()
            field.setRange(0.0, 999999.0)
            return field
    
    def create_combo_box(self, items: list = None) -> QWidget:
        """Create a combo box using the design system"""
        from PySide6.QtWidgets import QComboBox
        
        combo = QComboBox()
        if items:
            combo.addItems(items)
        
        return combo
    
    def create_progress_bar(self) -> QWidget:
        """Create a progress bar using the design system"""
        from PySide6.QtWidgets import QProgressBar
        
        progress = QProgressBar()
        progress.setTextVisible(False)
        return progress
    
    def create_status_indicator(self, status: str = 'normal') -> QWidget:
        """Create a status indicator using the design system"""
        from PySide6.QtWidgets import QWidget
        
        indicator = QWidget()
        indicator.setFixedSize(12, 12)
        
        colors = {
            'normal': Colors.SUCCESS,
            'warning': Colors.WARNING,
            'error': Colors.DANGER,
            'info': Colors.INFO,
            'disabled': Colors.TEXT_MUTED
        }
        
        color = colors.get(status, Colors.TEXT_MUTED)
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
