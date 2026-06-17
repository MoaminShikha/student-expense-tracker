from __future__ import annotations

from expense_tracker.app.gui_v2 import tokens as t


def build_stylesheet(theme: str = "light") -> str:
    """Build and return the complete QSS application stylesheet.

    :param theme: "light" or "dark"
    :return: Complete QSS string ready to pass to QApplication.setStyleSheet().
    """
    if theme == "dark":
        bg        = "#1a1a2e"
        paper     = "#242442"
        surface   = "#2d2d47"
        hairline  = "#3d3d57"
        hairline_s = "#4d4d67"
        fg        = "#e8e8f0"
        muted_fg  = "#a8a8b8"
        muted     = "#767686"
        red       = "#ff6b6b"
        green     = "#51cf66"
        gold      = "#ffd93d"
        amber     = "#ffb347"
        navy      = "#1a1a2e"
        focus     = "#ffd93d"
        paper_warm = "#242442"
    else:
        bg        = t.BG
        paper     = t.PAPER_WARM
        surface   = t.SURFACE
        hairline  = t.HAIRLINE
        hairline_s = t.HAIRLINE_S
        fg        = t.FG
        muted_fg  = t.MUTED_FG
        muted     = t.MUTED
        red       = t.RED
        green     = t.GREEN
        gold      = t.GOLD
        amber     = t.AMBER
        navy      = t.NAVY
        focus     = t.FOCUS
        paper_warm = t.PAPER_WARM

    return f"""
    QWidget {{
        background: {bg};
        color: {fg};
        font-family: "DM Mono", Consolas, monospace;
    }}
    QMainWindow {{
        background: {bg};
    }}
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
        text-align: left;
        padding-left: 44px;
        height: 33px;
        border-radius: 0px;
    }}
    QPushButton#sbNavItem:hover {{
        background: rgba(36,28,10,0.08);
        color: {fg};
        border-left: 3px solid {hairline_s};
    }}
    QPushButton#sbNavItem[active="true"] {{
        border-left: 2px solid {gold};
        background: rgba(199,154,57,0.16);
        color: {fg};
        font-weight: 500;
    }}
    QFrame#sbStreak {{
        background: {paper};
        border-radius: 10px;
    }}
    QLabel#sbStreakLabel {{
        color: {muted};
        background: transparent;
    }}
    QLabel#sbStreakCount {{
        color: {fg};
        background: transparent;
    }}
    QLabel#sbStreakUnit {{
        color: {muted};
        background: transparent;
    }}
    QFrame#sbStreakSegOn {{
        background: {gold};
        border-radius: 3px;
    }}
    QFrame#sbStreakSegOff {{
        background: {hairline};
        border-radius: 3px;
    }}
    QFrame#sbUserDivider {{
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

    /* Topbar */
    QWidget#topbar {{
        background: {surface};
        border-bottom: 1px solid {hairline};
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

    /* Alert banner */
    QFrame#alertBanner {{
        background: {amber};
        border-radius: 6px;
    }}

    /* Inputs */
    QLineEdit {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    QLineEdit:focus {{
        border: 1px solid {focus};
    }}
    QComboBox {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    QComboBox:focus {{
        border: 1px solid {focus};
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
        border: 1px solid {focus};
    }}
    QSpinBox {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    QSpinBox:focus {{
        border: 1px solid {focus};
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
        background: {navy};
        color: {gold};
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

    /* Checkbox */
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

    /* Tooltips */
    QToolTip {{
        background: {surface};
        color: {fg};
        border: 1px solid {hairline};
        border-radius: 4px;
        padding: 4px 8px;
    }}

    /* Stat cards */
    QFrame#statCard {{
        background: {surface};
        border: 1px solid {hairline};
        border-radius: 14px;
    }}
    """
