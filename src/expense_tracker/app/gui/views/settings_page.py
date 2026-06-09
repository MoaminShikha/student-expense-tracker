from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QFrame, QSizePolicy
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.theme_manager import get_theme_manager
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget


class SettingsPage(QWidget):
    """Settings page with theme toggle and other options."""

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

        # Dark mode toggle
        dark_mode_row = QHBoxLayout()
        dark_mode_row.setContentsMargins(0, 0, 0, 0)
        dark_mode_row.setSpacing(12)

        dark_mode_lbl = QLabel("Dark Mode")
        dark_mode_lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )

        dark_mode_checkbox = QCheckBox()
        dark_mode_checkbox.setMinimumSize(44, 44)
        dark_mode_checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {tokens.HAIRLINE};
                background: {tokens.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background: {tokens.GOLD};
                border: 1px solid {tokens.GOLD};
            }}
        """)

        theme_mgr = get_theme_manager()
        dark_mode_checkbox.setChecked(theme_mgr.is_dark())
        dark_mode_checkbox.stateChanged.connect(self._on_dark_mode_toggled)

        dark_mode_row.addWidget(dark_mode_lbl)
        dark_mode_row.addStretch()
        dark_mode_row.addWidget(dark_mode_checkbox)

        dark_mode_container = QWidget()
        dark_mode_container.setLayout(dark_mode_row)
        dark_mode_container.setStyleSheet(f"""
            QWidget {{
                background: {tokens.PAPER_WARM};
                border-radius: 8px;
                padding: 12px 16px;
                border: 1px solid {tokens.HAIRLINE};
            }}
        """)
        layout.addWidget(dark_mode_container)

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

    def _on_dark_mode_toggled(self, state: int) -> None:
        """Handle dark mode toggle."""
        theme_mgr = get_theme_manager()
        theme_mgr.set_theme("dark" if state else "light")
