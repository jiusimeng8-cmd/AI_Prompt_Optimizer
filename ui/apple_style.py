"""
Apple-style light design system for the PyQt6 desktop UI.

This reconstructs the original clean, light, minimal interface style used by
the app before the later Liquid Glass / Neumorphism experiments.
"""

from PyQt6.QtWidgets import QApplication, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QPalette, QColor


class Colors:
    """Clean light Apple-style palette."""

    ACCENT = "#007AFF"
    ACCENT_HOVER = "#0066D6"
    ACCENT_PRESSED = "#0051A8"
    ACCENT_LIGHT = "#E8F2FF"

    TEXT_PRIMARY = "#1D1D1F"
    TEXT_SECONDARY = "#6E6E73"
    TEXT_TERTIARY = "#A1A1A6"
    TEXT_ON_ACCENT = "#FFFFFF"

    BG_WINDOW = "#F5F5F7"
    BG_CARD = "#FFFFFF"
    BG_HOVER = "#F2F2F7"
    BG_INPUT = "#FFFFFF"

    BORDER = "#D2D2D7"
    BORDER_FOCUS = "#007AFF"
    BORDER_HOVER = "#B8B8BD"

    SUCCESS = "#34C759"
    WARNING = "#FF9500"
    ERROR = "#FF3B30"


class GlassColors:
    """Compatibility tokens kept for custom-painted widgets."""

    WINDOW_TOP = BG_WINDOW = Colors.BG_WINDOW
    WINDOW_MID = Colors.BG_WINDOW
    WINDOW_BOTTOM = Colors.BG_WINDOW
    SURFACE = Colors.BG_CARD
    SURFACE_STRONG = Colors.BG_HOVER
    SURFACE_SOFT = "#FAFAFC"
    BORDER = Colors.BORDER
    BORDER_STRONG = Colors.BORDER_HOVER
    HIGHLIGHT = "#FFFFFF"
    SHADOW = "rgba(0, 0, 0, 0.08)"
    LOADING_BG = (245, 245, 245, 230)
    LOADING_BORDER = (220, 220, 225, 180)
    LOADING_DOT_ACTIVE = (255, 255, 255, 255)
    LOADING_DOT_IDLE = (160, 160, 160, 180)


class Spacing:
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


class Radius:
    XS = 6
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24


def create_card_shadow(opacity=0.04, radius=8, y_offset=1):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(0, 0, 0, int(opacity * 255)))
    return shadow


def create_glass_shadow(opacity=0.04, radius=8, y_offset=1):
    """Compatibility alias for UI files created during later style passes."""
    return create_card_shadow(opacity=opacity, radius=radius, y_offset=y_offset)


def create_button_shadow():
    return create_card_shadow(opacity=0.06, radius=10, y_offset=2)


class Fonts:
    FAMILY = "Segoe UI Variable Display"
    FALLBACK = "Segoe UI"
    MONO = "Cascadia Code, Consolas, monospace"

    @staticmethod
    def get_font(size=14, weight="normal"):
        font = QFont(Fonts.FAMILY, size)
        if weight in ("semibold", "bold"):
            font.setWeight(QFont.Weight.DemiBold)
        return font


APPLE_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {Colors.BG_WINDOW};
    font-family: "{Fonts.FAMILY}", "{Fonts.FALLBACK}";
    font-size: 14px;
    color: {Colors.TEXT_PRIMARY};
}}

QWidget {{
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 14px;
    background: transparent;
    border: none;
}}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {Colors.BG_INPUT};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD}px;
    padding: 10px 12px;
    font-size: 14px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QTextEdit {{
    border-radius: {Radius.LG}px;
    padding: 14px 16px;
}}

QLineEdit:hover, QTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: {Colors.BORDER_HOVER};
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QLineEdit:disabled, QTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: #F2F2F7;
    color: {Colors.TEXT_TERTIARY};
}}

QComboBox {{
    background-color: {Colors.BG_INPUT};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD}px;
    padding: 8px 12px;
    min-height: 26px;
    font-size: 14px;
    color: {Colors.TEXT_PRIMARY};
}}

QComboBox:hover {{
    background-color: {Colors.BG_HOVER};
    border-color: {Colors.BORDER_HOVER};
}}

QComboBox:focus {{ border-color: {Colors.BORDER_FOCUS}; }}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {Colors.TEXT_SECONDARY};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD}px;
    padding: 4px;
    outline: none;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QPushButton {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD}px;
    padding: 8px 16px;
    min-height: 28px;
    font-size: 14px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    border-color: {Colors.BORDER_HOVER};
}}

QPushButton:pressed {{
    background-color: #E5E5EA;
}}

QPushButton:disabled {{
    color: {Colors.TEXT_TERTIARY};
    background-color: #F2F2F7;
    border-color: #E5E5EA;
}}

QPushButton[class="primary"] {{
    background-color: {Colors.ACCENT};
    color: {Colors.TEXT_ON_ACCENT};
    border: 1px solid {Colors.ACCENT};
    font-weight: 600;
    min-height: 36px;
    font-size: 15px;
    border-radius: {Radius.LG}px;
    padding: 10px 24px;
}}

QPushButton[class="primary"]:hover {{
    background-color: {Colors.ACCENT_HOVER};
    border-color: {Colors.ACCENT_HOVER};
}}

QPushButton[class="primary"]:pressed {{
    background-color: {Colors.ACCENT_PRESSED};
    border-color: {Colors.ACCENT_PRESSED};
}}

QPushButton[class="danger"] {{
    color: {Colors.ERROR};
}}

QPushButton[class="danger"]:hover {{
    background-color: #FFEDEC;
    border-color: #FFD3D0;
}}

QSplitter::handle {{ background-color: #E5E5EA; }}
QSplitter::handle:vertical {{ height: 1px; }}
QSplitter::handle:horizontal {{ width: 1px; }}

QTabWidget::pane {{
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG}px;
    background-color: {Colors.BG_CARD};
    padding: 10px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    border: 1px solid transparent;
    padding: 8px 20px;
    font-size: 14px;
    color: {Colors.TEXT_SECONDARY};
    border-radius: {Radius.MD}px;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    color: {Colors.ACCENT};
    background-color: {Colors.ACCENT_LIGHT};
}}

QTabBar::tab:hover:!selected {{
    color: {Colors.TEXT_PRIMARY};
    background-color: {Colors.BG_HOVER};
}}

QListWidget {{
    background-color: {Colors.BG_INPUT};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG}px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 9px 12px;
    border-radius: {Radius.MD}px;
    margin: 2px 0;
    color: {Colors.TEXT_PRIMARY};
}}

QListWidget::item:selected {{
    background-color: {Colors.ACCENT_LIGHT};
    color: {Colors.ACCENT};
}}

QListWidget::item:hover:!selected {{ background-color: {Colors.BG_HOVER}; }}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 0;
}}

QScrollBar::handle:vertical {{
    background: #D2D2D7;
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{ background: #B8B8BD; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0 4px;
}}

QScrollBar::handle:horizontal {{
    background: #D2D2D7;
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{ background: #B8B8BD; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QStatusBar {{
    background-color: {Colors.BG_WINDOW};
    color: {Colors.TEXT_SECONDARY};
    font-size: 12px;
    border-top: 1px solid {Colors.BORDER};
    padding: 6px 10px;
}}

QMessageBox {{ background-color: {Colors.BG_WINDOW}; }}

QMessageBox QLabel {{
    font-size: 14px;
    min-width: 280px;
    color: {Colors.TEXT_PRIMARY};
}}

QFormLayout {{ spacing: 14px; }}

QLabel[class="secondary"] {{
    color: {Colors.TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 500;
}}

QLabel[class="secondary-lg"] {{
    color: {Colors.TEXT_SECONDARY};
    font-size: 14px;
    font-weight: 500;
}}

QLabel[class="caption"] {{
    color: {Colors.TEXT_TERTIARY};
    font-size: 12px;
}}

QPushButton[class="ghost"] {{
    background: transparent;
    border: none;
    color: {Colors.ACCENT};
    font-size: 13px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: {Radius.XS}px;
}}

QPushButton[class="ghost"]:hover {{ background-color: {Colors.ACCENT_LIGHT}; }}

QFrame[class="separator"] {{
    background-color: {Colors.BORDER};
    max-height: 1px;
    margin: 2px 0;
}}

QLabel[class="hotkey-display"] {{
    font-size: 18px;
    font-weight: 600;
    padding: 12px 20px;
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG}px;
    background-color: {Colors.BG_CARD};
    color: {Colors.TEXT_PRIMARY};
}}

QLabel[class="info"] {{
    color: {Colors.TEXT_SECONDARY};
    font-size: 13px;
}}

QLabel[class="status"] {{
    color: {Colors.TEXT_TERTIARY};
    font-size: 12px;
}}
"""


def apply_apple_style(app: QApplication):
    """Apply the reconstructed light Apple style to the whole app."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BG_WINDOW))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(Colors.BG_INPUT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.BG_HOVER))
    palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(Colors.BG_CARD))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255, 55))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(Colors.TEXT_TERTIARY))
    app.setPalette(palette)

    app.setStyleSheet(APPLE_STYLE)

    font = QFont(Fonts.FAMILY, 14)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
