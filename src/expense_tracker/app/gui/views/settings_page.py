from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget


class SettingsPage(QWidget):
    """Settings page (stub for now)."""

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

        sub = QLabel("Opening balance · Currency · Export · About")
        sub.setStyleSheet(
            f"font-size: {tokens.T_BASE}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(sub)
        layout.addStretch()
