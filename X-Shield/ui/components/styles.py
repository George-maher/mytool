"""
X-Shield Modern Minimal Design System
Centralized styles, colors, and QSS templates for the entire application.
"""

import os

# --- Color Palette (Vibrant Cyberpunk Theme) ---
class Colors:
    BACKGROUND = "#0a0e1a"      # Deep Dark Blue
    SURFACE = "#1a1f2e"         # Dark Blue-Gray
    SURFACE_LIGHT = "#2a3f5f"   # Medium Blue
    BORDER = "#3a4f6f"          # Light Blue
    BORDER_HOVER = "#4a5f7f"    # Lighter Blue

    TEXT_PRIMARY = "#ffffff"    # Pure White
    TEXT_SECONDARY = "#b8c5d6"  # Light Blue-Gray
    TEXT_MUTED = "#6b7c93"      # Muted Blue

    PRIMARY = "#ff00ff"         # Bright Magenta
    PRIMARY_HOVER = "#ff33ff"   # Lighter Magenta
    PRIMARY_MUTED = "rgba(255, 0, 255, 0.1)"

    SUCCESS = "#00ff88"         # Neon Green
    WARNING = "#ffaa00"         # Golden Amber
    DANGER = "#ff0066"          # Hot Pink
    INFO = "#00ddff"            # Cyan
    ACCENT = "#ff6b35"          # Orange Coral
    TERMINAL_BG = "#0f172a"     # Dark Blue
    
    # Additional vibrant colors
    PURPLE = "#8b5cf6"          # Violet
    PINK = "#ec4899"            # Hot Pink
    LIME = "#84cc16"            # Lime Green
    TEAL = "#14b8a6"            # Teal
    INDIGO = "#6366f1"          # Indigo
    ROSE = "#f43f5e"            # Rose

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

# Get the absolute path to the assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CHECK_SVG_PATH = os.path.join(ASSETS_DIR, "check.svg").replace("\\", "/")

# --- QSS Template ---
def get_main_stylesheet():
    return f"""
    QMainWindow {{
        background-color: {Colors.BACKGROUND};
    }}

    QWidget {{
        background-color: transparent;
        color: {Colors.TEXT_PRIMARY};
        font-family: {Typography.FAMILY_SANS};
        font-size: {Typography.BODY_SIZE};
    }}

    /* --- ScrollBars --- */
    QScrollBar:vertical {{
        border: none;
        background: {Colors.BACKGROUND};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.SURFACE_LIGHT};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: {Colors.BACKGROUND};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.SURFACE_LIGHT};
        min-width: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* --- Buttons --- */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.SURFACE}, stop:1 {Colors.SURFACE_LIGHT});
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        min-height: 36px;
        transition: all 0.3s ease;
    }}

    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.PRIMARY_MUTED}, stop:1 rgba(255, 0, 255, 0.2));
        border-color: {Colors.PRIMARY};
        color: {Colors.PRIMARY_HOVER};
        transform: translateY(-1px);
    }}

    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_HOVER});
        color: {Colors.TEXT_PRIMARY};
    }}

    QPushButton:disabled {{
        color: {Colors.TEXT_MUTED};
        background-color: {Colors.SURFACE};
        border-color: {Colors.BORDER};
    }}

    /* Primary Action Buttons */
    QPushButton#primary_btn, QPushButton.large {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_HOVER});
        color: {Colors.TEXT_PRIMARY};
        border: 2px solid {Colors.PRIMARY};
        font-weight: 700;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(255, 0, 255, 0.3);
    }}

    QPushButton#primary_btn:hover, QPushButton.large:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.PRIMARY_HOVER}, stop:1 #ff66ff);
        border-color: {Colors.PRIMARY_HOVER};
        box-shadow: 0 6px 20px rgba(255, 0, 255, 0.5);
    }}

    /* Success Buttons */
    QPushButton#success_btn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.SUCCESS}, stop:1 #00ffaa);
        color: {Colors.BACKGROUND};
        border: 2px solid {Colors.SUCCESS};
        font-weight: 700;
    }}

    QPushButton#success_btn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 #00ffaa, stop:1 #00ffcc);
        box-shadow: 0 6px 20px rgba(0, 255, 136, 0.5);
    }}

    /* Warning Buttons */
    QPushButton#warning_btn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.WARNING}, stop:1 #ffcc00);
        color: {Colors.BACKGROUND};
        border: 2px solid {Colors.WARNING};
        font-weight: 700;
    }}

    QPushButton#warning_btn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 #ffcc00, stop:0 #ffdd33);
        box-shadow: 0 6px 20px rgba(255, 170, 0, 0.5);
    }}

    /* Danger Buttons */
    QPushButton#danger_btn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.DANGER}, stop:1 #ff3388);
        color: {Colors.TEXT_PRIMARY};
        border: 2px solid {Colors.DANGER};
        font-weight: 700;
    }}

    QPushButton#danger_btn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 #ff3388, stop:1 #ff66aa);
        box-shadow: 0 6px 20px rgba(255, 0, 102, 0.5);
    }}

    /* Small/Secondary Buttons */
    QPushButton.small {{
        padding: 4px 12px;
        min-height: 28px;
        font-size: {Typography.SMALL_SIZE};
        border-radius: 6px;
    }}

    /* --- Inputs --- */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {{
        background-color: {Colors.SURFACE};
        border: 1px solid {Colors.BORDER};
        border-radius: 6px;
        padding: 8px 12px;
        color: {Colors.TEXT_PRIMARY};
        font-family: {Typography.FAMILY_MONO};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
        border: 1px solid {Colors.PRIMARY};
        background-color: {Colors.BACKGROUND};
    }}

    QLineEdit::placeholder {{
        color: {Colors.TEXT_MUTED};
    }}

    /* --- Combo Box --- */
    QComboBox {{
        background-color: {Colors.SURFACE};
        border: 1px solid {Colors.BORDER};
        border-radius: 6px;
        padding: 8px 12px;
        min-height: 36px;
    }}

    QComboBox:hover {{
        border-color: {Colors.BORDER_HOVER};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {Colors.TEXT_SECONDARY};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {Colors.SURFACE};
        border: 1px solid {Colors.BORDER};
        selection-background-color: {Colors.PRIMARY_MUTED};
        selection-color: {Colors.PRIMARY};
        outline: none;
    }}

    /* --- Labels --- */
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
    }}

    QLabel#title {{
        font-size: {Typography.H1_SIZE};
        font-weight: 700;
        letter-spacing: -0.5px;
    }}

    QLabel#subtitle {{
        color: {Colors.TEXT_SECONDARY};
        font-size: {Typography.BODY_SIZE};
    }}

    QLabel#label_heading {{
        color: {Colors.TEXT_SECONDARY};
        font-weight: 600;
        font-size: {Typography.SMALL_SIZE};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* --- Frames & Containers --- */
    #card {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.SURFACE}, stop:1 {Colors.SURFACE_LIGHT});
        border: 1px solid {Colors.BORDER};
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }}

    #card:hover {{
        border-color: {Colors.PRIMARY};
        box-shadow: 0 6px 20px rgba(255, 0, 255, 0.2);
    }}

    #sidebar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 {Colors.SURFACE}, stop:1 {Colors.SURFACE_LIGHT});
        border-right: 2px solid {Colors.PRIMARY};
        box-shadow: 2px 0 10px rgba(255, 0, 255, 0.1);
    }}

    /* --- Tables --- */
    QTableWidget {{
        background-color: {Colors.SURFACE};
        border: 1px solid {Colors.BORDER};
        border-radius: 8px;
        gridline-color: {Colors.BORDER};
        outline: none;
    }}

    QTableWidget::item {{
        padding: 12px;
        border-bottom: 1px solid {Colors.BORDER};
    }}

    QTableWidget::item:selected {{
        background-color: {Colors.PRIMARY_MUTED};
        color: {Colors.PRIMARY};
    }}

    QHeaderView::section {{
        background-color: {Colors.SURFACE};
        color: {Colors.TEXT_SECONDARY};
        padding: 12px;
        border: none;
        border-bottom: 1px solid {Colors.BORDER};
        font-weight: 600;
        text-align: left;
    }}

    /* --- Tabs --- */
    QTabWidget::pane {{
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.SURFACE};
        top: -1px;
        border-radius: 8px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {Colors.TEXT_SECONDARY};
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        font-weight: 500;
    }}

    QTabBar::tab:selected {{
        color: {Colors.PRIMARY};
        border-bottom: 2px solid {Colors.PRIMARY};
    }}

    QTabBar::tab:hover {{
        color: {Colors.TEXT_PRIMARY};
    }}

    /* --- Progress Bar --- */
    QProgressBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.SURFACE}, stop:1 {Colors.SURFACE_LIGHT});
        border: 1px solid {Colors.BORDER};
        border-radius: 6px;
        text-align: center;
        height: 12px;
        color: {Colors.TEXT_PRIMARY};
        font-weight: 600;
    }}

    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 {Colors.PRIMARY}, stop:0.5 {Colors.INFO}, stop:1 {Colors.PRIMARY_HOVER});
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.3);
    }}

    /* --- CheckBox --- */
    QCheckBox {{
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {Colors.BORDER};
        border-radius: 4px;
        background-color: {Colors.SURFACE};
    }}

    QCheckBox::indicator:checked {{
        background-color: {Colors.PRIMARY};
        border-color: {Colors.PRIMARY};
        image: url({CHECK_SVG_PATH});
    }}

    QCheckBox::indicator:hover {{
        border-color: {Colors.PRIMARY};
    }}

    /* --- Specialized Components --- */
    .Terminal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 {Colors.TERMINAL_BG}, stop:1 #1a2332);
        border: 2px solid {Colors.PRIMARY};
        border-radius: 10px;
        color: {Colors.SUCCESS};
        font-family: {Typography.FAMILY_MONO};
        font-size: 13px;
        padding: {Spacing.MD}px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
    }}

    .StatusIndicator {{
        font-weight: 700;
        font-size: {Typography.SMALL_SIZE};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .StatusIndicator[status="online"] {{
        color: {Colors.SUCCESS};
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }}

    .StatusIndicator[status="warning"] {{
        color: {Colors.WARNING};
        text-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
    }}

    .StatusIndicator[status="error"] {{
        color: {Colors.DANGER};
        text-shadow: 0 0 10px rgba(255, 0, 102, 0.5);
    }}

    .ToolHeader {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 {Colors.BACKGROUND}, stop:0.5 {Colors.SURFACE}, stop:1 {Colors.BACKGROUND});
        border-bottom: 2px solid {Colors.PRIMARY};
        min-height: 60px;
        border-radius: 8px 8px 0 0;
    }}
    """
