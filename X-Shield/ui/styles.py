"""
X-Shield Modern Minimal Design System
Centralized styles, colors, and QSS templates for the entire application.
"""

import os
from PySide6.QtGui import QColor

# Get the absolute path to the assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CHECK_SVG_PATH = os.path.join(ASSETS_DIR, "check.svg").replace("\\", "/")

# --- Color Palette (Modern Minimal / Slate & Sky) ---
class Colors:
    BACKGROUND = "#09090b"      # Zinc 950
    SURFACE = "#18181b"         # Zinc 900
    SURFACE_LIGHT = "#27272a"   # Zinc 800
    BORDER = "#27272a"          # Zinc 800
    BORDER_HOVER = "#3f3f46"    # Zinc 700

    TEXT_PRIMARY = "#fafafa"    # Zinc 50
    TEXT_SECONDARY = "#a1a1aa"  # Zinc 400
    TEXT_MUTED = "#52525b"      # Zinc 600

    PRIMARY = "#0ea5e9"         # Sky 500
    PRIMARY_HOVER = "#38bdf8"   # Sky 400
    PRIMARY_MUTED = "rgba(14, 165, 233, 0.1)"

    SUCCESS = "#10b981"         # Emerald 500
    WARNING = "#f59e0b"         # Amber 500
    DANGER = "#ef4444"          # Red 500
    INFO = "#3b82f6"            # Blue 500

# --- Spacing System ---
class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    PAGE_MARGIN = 32

# --- Typography ---
class Typography:
    FAMILY_SANS = "'Inter', 'DejaVu Sans', sans-serif"
    FAMILY_MONO = "'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', monospace"

    H1_SIZE = "24px"
    H2_SIZE = "20px"
    H3_SIZE = "16px"
    BODY_SIZE = "14px"
    SMALL_SIZE = "12px"

# --- QSS Template ---
def get_main_stylesheet():
    return f\"\"\"
    QMainWindow {{
        background-color: {{Colors.BACKGROUND}};
    }}

    QWidget {{
        background-color: transparent;
        color: {{Colors.TEXT_PRIMARY}};
        font-family: {{Typography.FAMILY_SANS}};
        font-size: {{Typography.BODY_SIZE}};
    }}

    /* --- ScrollBars --- */
    QScrollBar:vertical {{
        border: none;
        background: {{Colors.BACKGROUND}};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {{Colors.SURFACE_LIGHT}};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {{Colors.TEXT_MUTED}};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: {{Colors.BACKGROUND}};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {{Colors.SURFACE_LIGHT}};
        min-width: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* --- Buttons --- */
    QPushButton {{
        background-color: {{Colors.SURFACE_LIGHT}};
        color: {{Colors.TEXT_PRIMARY}};
        border: 1px solid {{Colors.BORDER}};
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        min-height: 36px;
    }}

    QPushButton:hover {{
        background-color: {{Colors.BORDER_HOVER}};
        border-color: {{Colors.TEXT_MUTED}};
    }}

    QPushButton:pressed {{
        background-color: {{Colors.SURFACE}};
    }}

    QPushButton:disabled {{
        color: {{Colors.TEXT_MUTED}};
        background-color: {{Colors.SURFACE}};
        border-color: {{Colors.BORDER}};
    }}

    /* Primary Action Buttons */
    QPushButton#primary_btn, QPushButton.large {{
        background-color: {{Colors.PRIMARY}};
        color: {{Colors.BACKGROUND}};
        border: 1px solid {{Colors.PRIMARY}};
        font-weight: 600;
    }}

    QPushButton#primary_btn:hover, QPushButton.large:hover {{
        background-color: {{Colors.PRIMARY_HOVER}};
        border-color: {{Colors.PRIMARY_HOVER}};
    }}

    /* Small/Secondary Buttons */
    QPushButton.small {{
        padding: 4px 12px;
        min-height: 28px;
        font-size: {{Typography.SMALL_SIZE}};
    }}

    /* --- Inputs --- */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {{
        background-color: {{Colors.SURFACE}};
        border: 1px solid {{Colors.BORDER}};
        border-radius: 6px;
        padding: 8px 12px;
        color: {{Colors.TEXT_PRIMARY}};
        font-family: {{Typography.FAMILY_MONO}};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
        border: 1px solid {{Colors.PRIMARY}};
        background-color: {{Colors.BACKGROUND}};
    }}

    QLineEdit::placeholder {{
        color: {{Colors.TEXT_MUTED}};
    }}

    /* --- Combo Box --- */
    QComboBox {{
        background-color: {{Colors.SURFACE}};
        border: 1px solid {{Colors.BORDER}};
        border-radius: 6px;
        padding: 8px 12px;
        min-height: 36px;
    }}

    QComboBox:hover {{
        border-color: {{Colors.BORDER_HOVER}};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {{Colors.TEXT_SECONDARY}};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {{Colors.SURFACE}};
        border: 1px solid {{Colors.BORDER}};
        selection-background-color: {{Colors.PRIMARY_MUTED}};
        selection-color: {{Colors.PRIMARY}};
        outline: none;
    }}

    /* --- Labels --- */
    QLabel {{
        color: {{Colors.TEXT_PRIMARY}};
    }}

    QLabel#title {{
        font-size: {{Typography.H1_SIZE}};
        font-weight: 700;
        letter-spacing: -0.5px;
    }}

    QLabel#subtitle {{
        color: {{Colors.TEXT_SECONDARY}};
        font-size: {{Typography.BODY_SIZE}};
    }}

    QLabel#label_heading {{
        color: {{Colors.TEXT_SECONDARY}};
        font-weight: 600;
        font-size: {{Typography.SMALL_SIZE}};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* --- Frames & Containers --- */
    .QFrame#card {{
        background-color: {{Colors.SURFACE}};
        border: 1px solid {{Colors.BORDER}};
        border-radius: 12px;
    }}

    .QFrame#sidebar {{
        background-color: {{Colors.SURFACE}};
        border-right: 1px solid {{Colors.BORDER}};
    }}

    /* --- Tables --- */
    QTableWidget {{
        background-color: {{Colors.SURFACE}};
        border: 1px solid {{Colors.BORDER}};
        border-radius: 8px;
        gridline-color: {{Colors.BORDER}};
        outline: none;
    }}

    QTableWidget::item {{
        padding: 12px;
        border-bottom: 1px solid {{Colors.BORDER}};
    }}

    QTableWidget::item:selected {{
        background-color: {{Colors.PRIMARY_MUTED}};
        color: {{Colors.PRIMARY}};
    }}

    QHeaderView::section {{
        background-color: {{Colors.SURFACE}};
        color: {{Colors.TEXT_SECONDARY}};
        padding: 12px;
        border: none;
        border-bottom: 1px solid {{Colors.BORDER}};
        font-weight: 600;
        text-align: left;
    }}

    /* --- Tabs --- */
    QTabWidget::pane {{
        border: 1px solid {{Colors.BORDER}};
        background-color: {{Colors.SURFACE}};
        top: -1px;
        border-radius: 8px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {{Colors.TEXT_SECONDARY}};
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        font-weight: 500;
    }}

    QTabBar::tab:selected {{
        color: {{Colors.PRIMARY}};
        border-bottom: 2px solid {{Colors.PRIMARY}};
    }}

    QTabBar::tab:hover {{
        color: {{Colors.TEXT_PRIMARY}};
    }}

    /* --- Progress Bar --- */
    QProgressBar {{
        background-color: {{Colors.SURFACE_LIGHT}};
        border: none;
        border-radius: 4px;
        text-align: center;
        height: 8px;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background-color: {{Colors.PRIMARY}};
        border-radius: 4px;
    }}

    /* --- CheckBox --- */
    QCheckBox {{
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {{Colors.BORDER}};
        border-radius: 4px;
        background-color: {{Colors.SURFACE}};
    }}

    QCheckBox::indicator:checked {{
        background-color: {{Colors.PRIMARY}};
        border-color: {{Colors.PRIMARY}};
        image: url({{CHECK_SVG_PATH}});
    }}

    QCheckBox::indicator:hover {{
        border-color: {{Colors.PRIMARY}};
    }}
    \"\"\"
