"""
Footer strip — three-column muted footer at the bottom of the scroll content.
Matches the HTML .page-footer block.

Public API:
    set_left(str)    — "13 MAY  ·  LAST SYNC 09:41"
    set_center(str)  — "MIZĀN  ·  QUIET BY DESIGN"
    set_right(str)   — "FY 2026  ·  MAY CLOSES IN 18 DAYS"
"""
from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens


class FooterStrip(QWidget):
    """Thin three-column footer matching the HTML .page-footer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 0)
        outer.setSpacing(8)

        # Hairline divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {tokens.HAIRLINE}; border: none;")
        outer.addWidget(divider)

        # Three-column row
        row_w = QWidget()
        row = QHBoxLayout(row_w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        self._left   = self._lbl("", Qt.AlignmentFlag.AlignLeft)
        self._center = self._lbl("MIZĀN  ·  QUIET BY DESIGN", Qt.AlignmentFlag.AlignHCenter)
        self._right  = self._lbl("", Qt.AlignmentFlag.AlignRight)

        row.addWidget(self._left)
        row.addWidget(self._center, stretch=1)
        row.addWidget(self._right)

        outer.addWidget(row_w)

        # Populate defaults from today
        today = date.today()
        self.set_left(today.strftime("%d %b").upper() + "  ·  LAST SYNC —")
        self.set_right(f"FY {today.year}")

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def set_left(self, text: str) -> None:
        self._left.setText(text)

    def set_center(self, text: str) -> None:
        self._center.setText(text)

    def set_right(self, text: str) -> None:
        self._right.setText(text)

    # ── HELPER ────────────────────────────────────────────────────────────────

    @staticmethod
    def _lbl(text: str, align: Qt.AlignmentFlag) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(align)
        lbl.setStyleSheet(f"""
            font-size: {tokens.T_MINI}px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: rgba(86,88,108,0.7);
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        """)
        return lbl
