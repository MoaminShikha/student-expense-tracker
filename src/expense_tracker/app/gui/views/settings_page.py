from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget


class SettingsPage(QWidget):
    """Settings page — appearance note, data location, and about info."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("settingsPage")

        w = PaperWidget(self)
        layout = QVBoxLayout(w)
        layout.setContentsMargins(tokens.CONTENT_PAD, 40, tokens.CONTENT_PAD, 40)
        layout.setSpacing(24)

        # Title
        lbl = QLabel("Settings")
        lbl.setStyleSheet(
            f"font-size: 22px; font-family: 'Playfair Display'; font-weight: 700;"
            f"color: {tokens.FG}; background: transparent;"
        )
        layout.addWidget(lbl)

        # Appearance section
        appearance_title = QLabel("Appearance")
        appearance_title.setStyleSheet(
            f"font-size: {tokens.T_LG}px; font-weight: 600; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(appearance_title)

        # Mizān ships dark-first; a light theme is planned. We show a static note
        # rather than a toggle so there's no control that appears to do nothing.
        appearance_info = QLabel("Mizān uses a light theme.\nA dark theme is coming in a future update.")
        appearance_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        appearance_info.setWordWrap(True)
        layout.addWidget(appearance_info)

        # Data section
        data_title = QLabel("Data")
        data_title.setStyleSheet(
            f"font-size: {tokens.T_LG}px; font-weight: 600; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(data_title)

        data_info = QLabel("Session-based data stored in data/ directory.\nExport and backup options coming soon.")
        data_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        data_info.setWordWrap(True)
        layout.addWidget(data_info)

        # About section
        about_title = QLabel("About")
        about_title.setStyleSheet(
            f"font-size: {tokens.T_LG}px; font-weight: 600; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(about_title)

        about_info = QLabel("Mizān — Student Budget Tracker\nVersion 0.9\n\nBuilt with PyQt6\nData in JSON")
        about_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        about_info.setWordWrap(True)
        layout.addWidget(about_info)

        layout.addStretch()
