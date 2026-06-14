from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget

# settings_page.py lives at src/expense_tracker/app/gui/views/settings_page.py
# parents[5] is the project root; data/ sits beside src/
_DATA_DIR = Path(__file__).resolve().parents[5] / "data"


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

        # Light mode is the default. A runtime toggle requires re-importing ~180 token
        # references frozen at startup — deferred to a future refactor.
        appearance_info = QLabel("Mizān uses a light theme.\nA dark theme is coming in a future update.")
        appearance_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG};"
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

        data_info = QLabel(f"Session data is stored in the data/ directory.\nLocation: {_DATA_DIR}")
        data_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        data_info.setWordWrap(True)
        layout.addWidget(data_info)

        open_btn = QPushButton("Open data folder")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setAccessibleName("Open data folder in file manager")
        open_btn.setFixedWidth(180)
        open_btn.setStyleSheet(f"""
            QPushButton {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_SM}px;
                padding: 7px 14px;
                border-radius: 6px;
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                color: {tokens.FG};
            }}
            QPushButton:hover {{
                background: {tokens.PAPER_WARM};
            }}
        """)
        open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(_DATA_DIR))))
        layout.addWidget(open_btn)

        # About section
        about_title = QLabel("About")
        about_title.setStyleSheet(
            f"font-size: {tokens.T_LG}px; font-weight: 600; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(about_title)

        about_info = QLabel("Mizān — Student Budget Tracker\nVersion 0.2.0\n\nBuilt with PyQt6 · data stored as JSON")
        about_info.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        about_info.setWordWrap(True)
        layout.addWidget(about_info)

        layout.addStretch()
