"""
Heads-up alert strip — shown when an upcoming charge is due within 7 days.
Matches the HTML .alert block: amber background, badge left, body center, amount right.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens


class HeadsUpAlert(QWidget):
    """
    Amber alert strip.

    Public API:
        set_data(body_html, amount_str)   — update text and amount
        set_visible(bool)                 — show/hide the whole widget
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._frame = QFrame()
        self._frame.setObjectName("alertFrame")
        self._frame.setStyleSheet(f"""
            QFrame#alertFrame {{
                background: {tokens.AMBER_BG};
                border: 1px solid {tokens.AMBER_BD};
                border-radius: 10px;
            }}
        """)

        inner = QHBoxLayout(self._frame)
        inner.setContentsMargins(16, 9, 16, 9)
        inner.setSpacing(12)

        # Left badge
        self._badge = QLabel("▲  HEADS-UP")
        self._badge.setStyleSheet(f"""
            background: rgba(160,87,18,0.15);
            color: {tokens.AMBER};
            font-size: {tokens.T_MINI}px;
            letter-spacing: 1px;
            font-family: "DM Mono", Consolas, monospace;
            font-weight: 500;
            padding: 3px 8px;
            border-radius: 4px;
        """)
        self._badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Body
        self._body = QLabel("")
        self._body.setStyleSheet(f"""
            color: {tokens.FG};
            font-size: {tokens.T_SM}px;
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        """)
        self._body.setTextFormat(Qt.TextFormat.RichText)
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Right amount
        self._amount = QLabel("")
        self._amount.setStyleSheet(f"""
            color: {tokens.RED};
            font-family: "Playfair Display";
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        """)
        self._amount.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        inner.addWidget(self._badge)
        inner.addWidget(self._body, stretch=1)
        inner.addWidget(self._amount)

        outer.addWidget(self._frame)

        self.setVisible(False)

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def set_data(self, body_html: str, amount_str: str) -> None:
        """Update body text (may include <b> tags) and right-side amount."""
        self._body.setText(body_html)
        self._amount.setText(amount_str)

    def set_visible(self, visible: bool) -> None:  # type: ignore[override]
        self.setVisible(visible)
