"""
Monthly budget timeline — custom-painted.

Track layout (left → right):
  [spent — gold-leaf]  [committed — red]  [fuzzy — striped red]  |today|  [remaining]

Supports:
  - Animated width transitions (1100 ms OutCubic)
  - Today marker with "TODAY" label above
  - Event ticks with labels below
  - Endpoint labels (left / right)
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,  # type: ignore[attr-defined]
)
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QWidget

from expense_tracker.app.gui.styles import tokens


@lru_cache(maxsize=1)
def _fuzzy_brush() -> QBrush:
    """7×7 diagonal stripe pixmap at 55% red alpha — tiled for the fuzzy zone."""
    pm = QPixmap(7, 7)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    stripe = QColor(tokens.RED)
    stripe.setAlpha(140)
    p.setPen(QPen(stripe, 1.5))
    p.drawLine(0, 7, 7, 0)
    p.end()
    return QBrush(pm)


class TimelineWidget(QWidget):
    """
    Monthly budget timeline — presentation only.
    All percentages are 0–100 of the monthly budget width.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(54)

        # Target values (set externally)
        self._spent_pct:       float = 0.0
        self._committed_pct:   float = 0.0
        self._fuzzy_left_pct:  float = 0.0
        self._fuzzy_width_pct: float = 0.0
        self._today_pct:       float = 0.0

        # Animated "display" spent value (drives paintEvent)
        self._anim_spent: float = 0.0

        self._ticks:       list[tuple[float, str]] = []  # (pct, label)
        self._left_label:  str = ""
        self._right_label: str = ""

        # Property animation for the spent bar width
        self._animation = QPropertyAnimation(self, b"anim_spent", self)
        self._animation.setDuration(1100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── Qt property (drives animation) ───────────────────────────────────────

    @pyqtProperty(float)
    def anim_spent(self) -> float:  # type: ignore[override]
        return self._anim_spent

    @anim_spent.setter  # type: ignore[attr-defined]
    def anim_spent(self, value: float) -> None:
        self._anim_spent = value
        self.update()

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    def set_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Update all timeline zones and trigger an animated repaint."""
        clamp = lambda v: max(0.0, min(100.0, float(v)))
        self._spent_pct       = clamp(spent_pct)
        self._committed_pct   = clamp(committed_pct)
        self._fuzzy_left_pct  = clamp(fuzzy_left_pct)
        self._fuzzy_width_pct = clamp(fuzzy_width_pct)
        self._today_pct       = clamp(today_pct)

        # Animate spent bar
        self._animation.stop()
        self._animation.setStartValue(self._anim_spent)
        self._animation.setEndValue(self._spent_pct)
        self._animation.start()

        self.update()

    def set_ticks(self, ticks: list[tuple[float, str]]) -> None:
        """Set event ticks: list of (pct, label) pairs."""
        self._ticks = ticks
        self.update()

    def set_endpoints(self, left_label: str, right_label: str) -> None:
        """Set the bottom-left and bottom-right labels."""
        self._left_label  = left_label
        self._right_label = right_label
        self.update()

    # ── PAINT ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w  = self.width()
        h  = self.height()
        track_y = 20          # pixels from top to track center
        track_h = 6
        track_r = track_h / 2

        def pct_x(pct: float) -> int:
            return int(w * pct / 100.0)

        # ── Background track ─────────────────────────────────────────────────
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.TRACK))
        p.drawRoundedRect(QRectF(0, track_y, w, track_h), track_r, track_r)

        # ── Spent — gold-leaf, left-rounded only ─────────────────────────────
        spent_w = pct_x(self._anim_spent)
        if spent_w > 0:
            p.setBrush(QColor(tokens.GOLD_LEAF))
            p.drawRoundedRect(
                QRectF(0, track_y, spent_w, track_h), track_r, track_r
            )
            # Cover right rounded corner with a sharp rectangle
            p.drawRect(QRectF(max(0, spent_w - track_r), track_y, track_r, track_h))

        # ── Committed — red, sharp corners ──────────────────────────────────
        committed_x = spent_w
        committed_w = pct_x(self._committed_pct)
        if committed_w > 0:
            p.setBrush(QColor(tokens.RED))
            p.drawRect(QRectF(committed_x, track_y, committed_w, track_h))

        # ── Fuzzy — striped red, right-rounded ───────────────────────────────
        fx = pct_x(self._fuzzy_left_pct)
        fw = pct_x(self._fuzzy_width_pct)
        if fw > 0:
            # Base translucent fill
            base = QColor(tokens.RED)
            base.setAlpha(80)
            p.setBrush(base)
            p.drawRoundedRect(
                QRectF(fx, track_y, fw, track_h), track_r, track_r
            )
            # Cover left rounded corner sharp
            p.drawRect(QRectF(fx, track_y, track_r, track_h))
            # Diagonal stripes on top
            p.save()
            p.setClipRect(QRectF(fx, track_y, fw, track_h))
            p.setBrush(_fuzzy_brush())
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(QRectF(fx, track_y, fw, track_h))
            p.restore()

        # ── Event ticks ──────────────────────────────────────────────────────
        tick_color = QColor(tokens.FG)
        tick_color.setAlpha(60)
        p.setPen(QPen(tick_color, 1.5))
        for tick_pct, tick_lbl in self._ticks:
            tx = pct_x(tick_pct)
            is_rent = "rent" in tick_lbl.lower()
            active_tick_color = QColor(tokens.RED if is_rent else tokens.FG)
            active_tick_color.setAlpha(135 if is_rent else 60)
            p.setPen(QPen(active_tick_color, 1.5))
            p.drawLine(tx, track_y - 4, tx, track_y + track_h + 4)
            if tick_lbl:
                p.setPen(QColor(tokens.RED if is_rent else tokens.MUTED))
                p.setFont(_micro_font(p))
                p.drawText(
                    QRectF(tx - 30, track_y + track_h + 5, 60, 14),
                    Qt.AlignmentFlag.AlignHCenter,
                    tick_lbl,
                )
                p.setPen(QPen(tick_color, 1.5))

        # ── Today marker ─────────────────────────────────────────────────────
        today_x = pct_x(self._today_pct)
        p.setPen(QPen(QColor(tokens.FG), 2))
        p.drawLine(today_x, track_y - 6, today_x, track_y + track_h + 6)

        # "TODAY" label above
        p.setPen(QColor(tokens.FG))
        p.setFont(_micro_font(p))
        p.drawText(
            QRectF(today_x - 30, track_y - 20, 60, 14),
            Qt.AlignmentFlag.AlignHCenter,
            "TODAY",
        )

        # ── Bottom endpoint labels ────────────────────────────────────────────
        if self._left_label or self._right_label:
            bottom_y = track_y + track_h + 20
            p.setPen(QColor(tokens.MUTED))
            p.setFont(_micro_font(p))
            if self._left_label:
                p.drawText(
                    QRectF(0, bottom_y, w / 2, 14),
                    Qt.AlignmentFlag.AlignLeft,
                    self._left_label,
                )
            if self._right_label:
                p.drawText(
                    QRectF(w / 2, bottom_y, w / 2, 14),
                    Qt.AlignmentFlag.AlignRight,
                    self._right_label,
                )

        p.end()


def _micro_font(painter: QPainter):  # type: ignore[return]
    f = painter.font()
    f.setFamily("DM Mono")
    f.setPointSize(tokens.T_MINI)
    f.setLetterSpacing(f.SpacingType.AbsoluteSpacing, 1)
    return f
