"""Stylesheet manager for dynamic theme switching."""
from __future__ import annotations

from PyQt6.QtWidgets import QApplication
from expense_tracker.app.gui.styles import tokens


def get_global_stylesheet(theme: str = "light") -> str:
    """Generate the global application stylesheet based on theme.

    Args:
        theme: "light" or "dark"

    Returns:
        Complete QSS stylesheet string
    """
    # Select color palette based on theme
    if theme == "dark":
        bg = "#1a1a2e"
        paper = "#242442"
        surface = "#2d2d47"
        hairline = "#3d3d57"
        hairline_s = "#4d4d67"
        fg = "#e8e8f0"
        muted_fg = "#a8a8b8"
        muted = "#767686"
        red = "#ff6b6b"
        green = "#51cf66"
        gold = "#ffd93d"
        amber = "#ffb347"
        navy = "#1a1a2e"
    else:
        bg = "#f7f3ec"
        paper = "#f3ede0"
        surface = "#ffffff"
        hairline = "#e2dccd"
        hairline_s = "#cdc4ae"
        fg = "#181a2c"
        muted_fg = "#56586c"
        muted = "#838897"
        red = "#962e2e"
        green = "#1b6a4f"
        gold = "#c79a39"
        amber = "#a05712"
        navy = "#16172a"

    return f"""
    /* Global application stylesheet */
    QWidget {{
        background: {bg};
        color: {fg};
    }}

    /* Main window */
    QMainWindow {{
        background: {bg};
    }}

    /* Dialogs */
    QDialog {{
        background: {surface};
    }}

    QMessageBox {{
        background: {surface};
    }}

    /* Sidebar */
    QWidget#sidebarRoot {{
        background: {surface};
        border-right: 1px solid {hairline_s};
    }}

    QFrame#sbDivider {{
        background: {hairline};
    }}

    QLabel#sbTag {{
        color: {gold};
        background: transparent;
    }}

    QLabel#sbWordmark {{
        color: {gold};
        background: transparent;
    }}

    QLabel#sbSub {{
        color: {muted};
        background: transparent;
    }}

    QLabel#sbSectionLabel {{
        color: {muted};
        background: transparent;
    }}

    QPushButton#sbNavItem {{
        color: {muted_fg};
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
    }}

    QPushButton#sbNavItem:hover {{
        background: rgba(255, 255, 255, 0.05);
        color: {fg};
        border-left: 3px solid {hairline_s};
    }}

    QPushButton#sbNavItem[active="true"] {{
        border-left: 2px solid {gold};
        background: rgba(255, 215, 61, 0.1);
        color: {fg};
    }}

    QFrame#sbStreak {{
        background: {paper};
        border-radius: 8px;
    }}

    QLabel#sbStreakLabel {{
        color: {fg};
        background: transparent;
    }}

    QLabel#sbStreakCount {{
        color: {gold};
        font-family: 'Playfair Display';
        font-size: 14px;
        font-weight: 700;
        background: transparent;
    }}

    QLabel#sbStreakUnit {{
        color: {muted};
        background: transparent;
    }}

    QFrame#sbStreakSegOn {{
        background: {gold};
    }}

    QFrame#sbStreakSegOff {{
        background: {hairline};
    }}

    QLabel#sbUserName {{
        color: {fg};
        background: transparent;
    }}

    QLabel#sbUserSub {{
        color: {muted};
        background: transparent;
    }}

    QFrame#sbUserDivider {{
        background: {hairline};
    }}

    /* Dashboard */
    QWidget#dashboardPage {{
        background: {bg};
    }}

    QScrollArea {{
        background: {bg};
        border: none;
    }}

    QFrame#panelCard {{
        background: {surface};
        border: 1px solid {hairline};
        border-radius: 14px;
    }}

    /* Topbar */
    QWidget#topbarRoot {{
        background: {surface};
        border-bottom: 1px solid {hairline};
    }}

    /* Forms & Inputs */
    QLineEdit {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QLineEdit:focus {{
        border: 1px solid {gold};
    }}

    QComboBox {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QComboBox:focus {{
        border: 1px solid {gold};
    }}

    QComboBox QAbstractItemView {{
        background: {surface};
        color: {fg};
        selection-background-color: {paper};
        selection-color: {fg};
        border: 1px solid {hairline};
    }}

    QDateEdit {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QDateEdit:focus {{
        border: 1px solid {gold};
    }}

    QSpinBox {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QSpinBox:focus {{
        border: 1px solid {gold};
    }}

    QProgressBar {{
        background: {hairline};
        border: none;
        border-radius: 3px;
        height: 6px;
    }}

    QProgressBar::chunk {{
        background: {gold};
        border-radius: 3px;
    }}

    /* Buttons */
    QPushButton {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 12px;
    }}

    QPushButton:hover {{
        background: {paper};
    }}

    QPushButton:pressed {{
        background: {hairline};
    }}

    QDialogButtonBox QPushButton[text="Add"] {{
        background: {gold};
        color: {navy};
        border: none;
        font-weight: 600;
    }}

    QDialogButtonBox QPushButton[text="Add"]:hover {{
        background: {amber};
    }}

    QDialogButtonBox QPushButton[text="Cancel"] {{
        background: transparent;
        border: 1px solid {hairline};
        color: {muted_fg};
    }}

    /* Labels */
    QLabel {{
        color: {fg};
        background: transparent;
    }}

    /* Scrollbar */
    QScrollBar:vertical {{
        background: {bg};
        width: 10px;
    }}

    QScrollBar::handle:vertical {{
        background: {hairline_s};
        border-radius: 5px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {muted};
    }}

    QScrollBar:horizontal {{
        background: {bg};
        height: 10px;
    }}

    QScrollBar::handle:horizontal {{
        background: {hairline_s};
        border-radius: 5px;
        min-width: 20px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {muted};
    }}

    /* Checkboxes */
    QCheckBox {{
        color: {fg};
        background: transparent;
        spacing: 6px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {hairline};
        background: {surface};
    }}

    QCheckBox::indicator:checked {{
        background: {gold};
        border: 1px solid {gold};
    }}

    /* Frames */
    QFrame {{
        background: transparent;
        color: {fg};
    }}

    /* Tooltips */
    QToolTip {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    """


def apply_stylesheet(app: QApplication, theme: str = "light") -> None:
    """Apply the complete stylesheet to the application.

    Args:
        app: QApplication instance
        theme: "light" or "dark"
    """
    stylesheet = get_global_stylesheet(theme)
    app.setStyleSheet(stylesheet)


def apply_theme(theme: str) -> None:
    """Apply theme to the current application.

    Args:
        theme: "light" or "dark"
    """
    app = QApplication.instance()
    if app:
        apply_stylesheet(app, theme)
