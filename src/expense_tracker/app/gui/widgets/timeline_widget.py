from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from expense_tracker.app.gui.styles import tokens


class TimelineWidget(QWidget):
    """
    Monthly budget timeline — presentation only.

    Track layout (left to right):
      [spent — gold]  [committed — red]  [fuzzy — hatched red]  |today|  [remaining]

    All inputs are percentages (0–100) of the monthly budget width.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(44)
        self._spent_pct: float = 0.0
        self._committed_pct: float = 0.0
        self._fuzzy_left_pct: float = 0.0
        self._fuzzy_width_pct: float = 0.0
        self._today_pct: float = 0.0

    def set_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Update all timeline zones and trigger a repaint."""
        self._spent_pct = max(0.0, min(100.0, spent_pct))
        self._committed_pct = max(0.0, min(100.0, committed_pct))
        self._fuzzy_left_pct = max(0.0, min(100.0, fuzzy_left_pct))
        self._fuzzy_width_pct = max(0.0, min(100.0, fuzzy_width_pct))
        self._today_pct = max(0.0, min(100.0, today_pct))
        self.update()

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        track_y = h // 2 - 3
        track_h = 6

        def pct_to_x(pct: float) -> int:
            return int(w * pct / 100.0)

        # ── Background track ──────────────────────────────────────────────────
        painter.fillRect(0, track_y, w, track_h, QColor(tokens.TRACK_BG))

        # ── Spent — gold-leaf ─────────────────────────────────────────────────
        spent_w = pct_to_x(self._spent_pct)
        if spent_w > 0:
            painter.fillRect(0, track_y, spent_w, track_h, QColor(tokens.GOLD_LEAF))

        # ── Committed — red ───────────────────────────────────────────────────
        committed_x = spent_w
        committed_w = pct_to_x(self._committed_pct)
        if committed_w > 0:
            painter.fillRect(committed_x, track_y, committed_w, track_h, QColor(tokens.RED))

        # ── Fuzzy — hatched red (diagonal stripes at ~55% opacity) ───────────
        fuzzy_x = pct_to_x(self._fuzzy_left_pct)
        fuzzy_w = pct_to_x(self._fuzzy_width_pct)
        if fuzzy_w > 0:
            base = QColor(tokens.RED)
            base.setAlpha(80)
            painter.fillRect(fuzzy_x, track_y, fuzzy_w, track_h, base)

            stripe = QColor(tokens.RED)
            stripe.setAlpha(140)
            pen = QPen(stripe, 1.0)
            painter.setPen(pen)
            step = 4
            for offset in range(-track_h, fuzzy_w + track_h, step):
                x1 = fuzzy_x + offset
                y1 = track_y + track_h
                x2 = fuzzy_x + offset + track_h
                y2 = track_y
                x1 = max(fuzzy_x, x1)
                x2 = min(fuzzy_x + fuzzy_w, x2)
                if x1 < x2:
                    painter.drawLine(x1, y1, x2, y2)

        # ── Today marker — dark vertical line ─────────────────────────────────
        today_x = pct_to_x(self._today_pct)
        marker_color = QColor(tokens.FG)
        painter.setPen(QPen(marker_color, 2))
        painter.drawLine(today_x, track_y - 6, today_x, track_y + track_h + 6)

        painter.end()
