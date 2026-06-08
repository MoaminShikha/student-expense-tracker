from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget


class SettingsPage(QWidget):
    """Settings page with theme and configuration options."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("settingsPage")

        w = PaperWidget(self)
        layout = QVBoxLayout(w)
        layout.setContentsMargins(tokens.CONTENT_PAD, 40, tokens.CONTENT_PAD, 40)

        lbl = QLabel("Settings")
        lbl.setStyleSheet(
            f"font-size: 22px; font-family: 'Playfair Display'; font-weight: 700;"
            f"color: {tokens.FG}; background: transparent;"
        )
        layout.addWidget(lbl)

        # Theme section
        theme_section = QLabel("Theme & Display")
        theme_section.setStyleSheet(
            f"font-size: {tokens.T_SM}px; font-weight: 600; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(theme_section)

        # Dark mode note
        dark_mode_info = QLabel(
            "To enable dark mode, edit src/expense_tracker/app/gui/styles/tokens.py\n"
            "and change: DARK_MODE = False → DARK_MODE = True"
        )
        dark_mode_info.setStyleSheet(
            f"font-size: {tokens.T_XS}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        dark_mode_info.setWordWrap(True)
        layout.addWidget(dark_mode_info)

        layout.addSpacing(20)

        sub = QLabel("Opening balance · Currency · Export · About")
        sub.setStyleSheet(
            f"font-size: {tokens.T_BASE}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(sub)
        layout.addStretch()
