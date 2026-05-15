"""
Two-track timeline widget.

Track 1 (top) — Calendar: day 1 → end of month.
  · Red dots above track = committed charge due dates.
  · Gold dots above track = days where spending occurred.
  · Vertical TODAY line.

Track 2 (bottom) — Budget bar: left→right = committed | fuzzy | spent.
  · Full width = monthly budget.
  · Red fill   = committed charges (fixed bills).
  · Amber fill  = fuzzy charges (uncertain amount).
  · Gold fill   = money already spent.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from PyQt6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QWidget

from expense_tracker.app.gui.styles import tokens


@dataclass(frozen=True)
class TimelineEvent:
    """One real event positioned on the month timeline (kept for API compat)."""
    pct: float
    label: str
    kind: str  # "spent" | "committed" | "fuzzy" | "generic"


@lru_cache(maxsize=1)
def _fuzzy_brush() -> QBrush:
    pm = QPixmap(7, 7)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    stripe = QColor(tokens.AMBER)
    stripe.setAlpha(145)
    p.setPen(QPen(stripe, 1.5))
    p.drawLine(0, 7, 7, 0)
    p.end()
    return QBrush(pm)


def _micro_font(painter: QPainter):  # type: ignore[return]
    f = painter.font()
    f.setFamily("Segoe UI")
    f.setPixelSize(10)
    f.setLetterSpacing(f.SpacingType.AbsoluteSpacing, 1)
    return f


class TimelineWidget(QWidget):
    """
    Two-track timeline.

    Track 1: calendar month with committed/spend event dots and TODAY marker.
    Track 2: budget bar — committed | fuzzy | spent (left → right).
    """

    # Layout constants (pixels)
    _TRACK_H   = 6
    _TRACK1_Y  = 28   # calendar track top edge (leaves room for dots above)
    _TRACK2_Y  = 64   # budget bar top edge
    _MIN_H     = 90

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(self._MIN_H)

        # Budget bar percentages (0-100, as % of monthly budget)
        self._spent_pct:     float = 0.0
        self._committed_pct: float = 0.0
        self._fuzzy_pct:     float = 0.0  # width of fuzzy zone

        # Calendar track
        self._today_pct:          float       = 0.0   # day position 0-100
        self._committed_due_pcts: list[float] = []    # due-date calendar positions
        self._spend_day_pcts:     list[float] = []    # spending-date calendar positions

        # Month labels
        self._left_label:  str = ""
        self._right_label: str = ""

        # Animated spent fill
        self._anim_spent: float = 0.0
        self._animation = QPropertyAnimation(self, b"anim_spent_prop", self)
        self._animation.setDuration(1100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── Animated property ─────────────────────────────────────────────────────

    @pyqtProperty(float)
    def anim_spent_prop(self) -> float:  # type: ignore[override]
        return self._anim_spent

    @anim_spent_prop.setter  # type: ignore[attr-defined]
    def anim_spent_prop(self, value: float) -> None:
        self._anim_spent = value
        self.update()

    # ── Public setters ────────────────────────────────────────────────────────

    def set_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        clamp = lambda v: max(0.0, min(100.0, float(v)))
        self._spent_pct     = clamp(spent_pct)
        self._committed_pct = clamp(committed_pct)
        self._fuzzy_pct     = clamp(fuzzy_width_pct)
        self._today_pct     = clamp(today_pct)

        self._animation.stop()
        self._animation.setStartValue(self._anim_spent)
        self._animation.setEndValue(self._spent_pct)
        self._animation.start()
        self.update()

    def set_committed_due_pcts(self, pcts: list[float]) -> None:
        """Calendar positions (0-100) of committed charge due dates."""
        self._committed_due_pcts = [max(0.0, min(100.0, p)) for p in pcts]
        self.update()

    def set_spend_day_pcts(self, pcts: list[float]) -> None:
        """Calendar positions (0-100) of days where spending occurred."""
        self._spend_day_pcts = [max(0.0, min(100.0, p)) for p in pcts]
        self.update()

    def set_endpoints(self, left_label: str, right_label: str) -> None:
        self._left_label  = left_label
        self._right_label = right_label
        self.update()

    # Legacy stubs kept so existing call-sites don't break
    def set_ticks(self, ticks: list[tuple[float, str]]) -> None:
        pass

    def set_events(self, events: list[TimelineEvent]) -> None:
        pass

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        total_w = self.width()
        pad = 4
        w = max(1, total_w - pad * 2)
        r = self._TRACK_H / 2

        t1y = self._TRACK1_Y
        t2y = self._TRACK2_Y
        th  = self._TRACK_H

        def px(pct: float) -> float:
            return pad + w * max(0.0, min(100.0, pct)) / 100.0

        # ── TRACK 1: Calendar ─────────────────────────────────────────────────

        # Background track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.TRACK))
        p.drawRoundedRect(QRectF(pad, t1y, w, th), r, r)

        # Spend day dots (gold, above track)
        for sp in self._spend_day_pcts:
            dx = px(sp)
            p.setBrush(QColor(tokens.GOLD_LEAF))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(dx, t1y - 6), 3.5, 3.5)

        # Committed due-date dots (red, above track — drawn on top of gold)
        for cp in self._committed_due_pcts:
            dx = px(cp)
            p.setBrush(QColor(tokens.RED))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(dx, t1y - 6), 3.5, 3.5)
            # short stem to track
            p.setPen(QPen(QColor(tokens.RED), 1.0))
            p.drawLine(QPointF(dx, t1y - 2.5), QPointF(dx, t1y))
            p.setPen(Qt.PenStyle.NoPen)

        # TODAY line
        tx = px(self._today_pct)
        p.setPen(QPen(QColor(tokens.FG), 2))
        p.drawLine(QPointF(tx, t1y - 10), QPointF(tx, t1y + th + 4))

        # "TODAY" label
        p.setPen(QColor(tokens.FG))
        p.setFont(_micro_font(p))
        p.drawText(
            QRectF(tx - 28, t1y - 22, 56, 12),
            Qt.AlignmentFlag.AlignHCenter,
            "TODAY",
        )

        # Month labels below track 1
        lbl_y = t1y + th + 6
        p.setPen(QColor(tokens.MUTED))
        p.setFont(_micro_font(p))
        if self._left_label:
            p.drawText(QRectF(pad, lbl_y, w / 2, 12), Qt.AlignmentFlag.AlignLeft, self._left_label)
        if self._right_label:
            p.drawText(QRectF(pad + w / 2, lbl_y, w / 2, 12), Qt.AlignmentFlag.AlignRight, self._right_label)

        # ── TRACK 2: Budget bar ───────────────────────────────────────────────

        # "BUDGET" micro label above bar
        p.setPen(QColor(tokens.MUTED))
        p.setFont(_micro_font(p))
        p.drawText(
            QRectF(pad, t2y - 14, w, 12),
            Qt.AlignmentFlag.AlignLeft,
            "BUDGET",
        )

        # Background
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.TRACK))
        p.drawRoundedRect(QRectF(pad, t2y, w, th), r, r)

        cursor = float(pad)

        # Committed fill (red, left-most)
        comm_w = w * self._committed_pct / 100.0
        if comm_w > 0:
            p.setBrush(QColor(tokens.RED))
            p.drawRoundedRect(QRectF(cursor, t2y, comm_w, th), r, r)
            cursor += comm_w

        # Fuzzy fill (hatched amber, after committed)
        fuzzy_w = w * self._fuzzy_pct / 100.0
        if fuzzy_w > 0:
            p.setBrush(_fuzzy_brush())
            p.drawRoundedRect(QRectF(cursor, t2y, fuzzy_w, th), 0, 0)
            cursor += fuzzy_w

        # Spent fill (gold, after fuzzy)
        spent_w = w * self._anim_spent / 100.0
        if spent_w > 0:
            p.setBrush(QColor(tokens.GOLD_LEAF))
            p.drawRoundedRect(QRectF(cursor, t2y, spent_w, th), 0, 0)

        p.end()
