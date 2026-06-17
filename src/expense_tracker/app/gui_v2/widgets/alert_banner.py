from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from expense_tracker.app.gui_v2 import tokens


class AlertBanner(QFrame):
    """Amber strip shown between the topbar and hero card when fuzzy charges are pending.

    The controller calls set_visible(True/False) based on
    FuzzyChargeService.list_pending_for_month() results.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("alertBanner")
        self.setFixedHeight(36)
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        icon = QLabel("⚠")
        icon.setStyleSheet(
            f"color: #ffffff; font-size: {tokens.T_BASE}px;"
            "background: transparent;"
        )

        self._msg = QLabel("You have pending fuzzy charges this month.")
        self._msg.setStyleSheet(
            f"color: #ffffff; font-size: {tokens.T_SM}px;"
            "font-family: 'DM Mono', Consolas, monospace;"
            "background: transparent;"
        )

        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._msg, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()

        self.setStyleSheet(f"""
            QFrame#alertBanner {{
                background: {tokens.AMBER};
                border-radius: 6px;
            }}
        """)

    def set_visible(self, visible: bool) -> None:
        """Show or hide the banner."""
        self.setVisible(visible)

    def set_message(self, text: str) -> None:
        """Update the banner message text."""
        self._msg.setText(text)
