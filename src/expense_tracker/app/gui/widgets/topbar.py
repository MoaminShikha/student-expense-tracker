from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from PyQt6.QtCore import QRectF, Qt, QVariantAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens


# ── Sparkline ─────────────────────────────────────────────────────────────────

class Sparkline(QWidget):
    """
    60×22 mini polyline chart showing last-7-days spend.
    Call set_values(list[Decimal]) to update.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(80, 22)
        self._values: list[float] = [0.0] * 7

    def set_values(self, values: list[Decimal]) -> None:
        self._values = [float(v) for v in values]
        self.update()

    def paintEvent(self, _event: Any) -> None:
        if not self._values:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        mx = max(self._values) or 1.0
        n = len(self._values)
        pts = QPolygonF()
        for i, v in enumerate(self._values):
            x = i / max(n - 1, 1) * w
            y = h - 2 - (v / mx) * (h - 6)
            pts.append(QPointF(x, y))
        pen = QPen(QColor(tokens.GOLD), 1.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(pts)
        # terminal dot
        last = pts[pts.count() - 1]
        p.setBrush(QColor(tokens.GOLD))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(last, 2.5, 2.5)
        p.end()


# ── Period segmented control ──────────────────────────────────────────────────

class PeriodSegmented(QWidget):
    """W / M / Y pill group. Emits period_changed(str) on click."""

    period_changed = pyqtSignal(str)

    _PERIODS = ["W", "M", "Y"]

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("periodSegmented")
        self._active = "M"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._btns: dict[str, QPushButton] = {}

        for p in self._PERIODS:
            btn = QPushButton(p)
            btn.setFixedHeight(24)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setFixedWidth(28)
            btn.setProperty("active", "true" if p == self._active else "false")
            btn.clicked.connect(lambda _c, period=p: self._on_click(period))
            self._btns[p] = btn
            layout.addWidget(btn)

        self.setStyleSheet(f"""
            QWidget#periodSegmented {{
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 999px;
                background: transparent;
            }}
            QPushButton {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_XS}px;
                border: none;
                border-radius: 0;
                background: transparent;
                color: {tokens.MUTED_FG};
                padding: 3px 10px;
                margin: 0;
            }}
            QPushButton[active="true"] {{
                background: {tokens.PAPER_WARM};
                color: {tokens.FG};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {tokens.PAPER_WARM};
                color: {tokens.FG};
            }}
        """)

    def _on_click(self, period: str) -> None:
        self._active = period
        for p, btn in self._btns.items():
            btn.setProperty("active", "true" if p == period else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.period_changed.emit(period)


# ── Pulsing status pill ───────────────────────────────────────────────────────

class StatusPill(QFrame):
    """
    Animated status pill: rounded bg + pulsing dot + text label.
    Pulse driven by QVariantAnimation (0→1→0, 2400 ms).
    """

    _STATES = {
        "green": {
            "text": "On track",
            "color": tokens.GREEN,
            "bg":    tokens.GREEN_BG,
        },
        "yellow": {
            "text": "Caution",
            "color": tokens.AMBER,
            "bg":    tokens.AMBER_BG,
        },
        "red": {
            "text": "Over budget",
            "color": tokens.RED,
            "bg":    "#fce8e8",
        },
        "tight_month": {
            "text": "Tight month",
            "color": tokens.MUTED_FG,
            "bg":    tokens.BG,
        },
    }

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("statusPill")
        self.setFixedHeight(26)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._state = "green"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 12, 0)
        layout.setSpacing(6)

        self._dot_w = _PulseDot(tokens.GREEN)
        self._label = QLabel("On track")
        self._label.setObjectName("pillLabel")
        layout.addWidget(self._dot_w)
        layout.addWidget(self._label)

        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setDuration(2400)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.SineCurve)
        self._anim.valueChanged.connect(self._dot_w.set_pulse)
        self._anim.start()

        self.set_state("green")

    def set_state(self, state: str) -> None:
        cfg = self._STATES.get(state, self._STATES["green"])
        self._state = state
        self._label.setText(cfg["text"])
        self._dot_w.set_color(cfg["color"])
        self.setStyleSheet(
            f"QFrame#statusPill {{"
            f"    background: {cfg['bg']};"
            f"    border: none;"
            f"    border-radius: 13px;"
            f"}}"
        )
        self._label.setStyleSheet(
            f"color: {cfg['color']};"
            f"font-size: {tokens.T_XS}px;"
            f"font-weight: 500;"
            f"letter-spacing: 0.07em;"
            f"font-family: 'DM Mono', Consolas, monospace;"
            f"background: transparent;"
        )


class _PulseDot(QWidget):
    """7×7 pulsing circle used inside StatusPill."""

    def __init__(self, color_hex: str) -> None:
        super().__init__()
        self.setFixedSize(7, 7)
        self._color = QColor(color_hex)
        self._pulse: float = 0.0

    def set_color(self, color_hex: str) -> None:
        self._color = QColor(color_hex)
        self.update()

    def set_pulse(self, val: float) -> None:
        self._pulse = float(val)
        self.update()

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        # outer glow
        if self._pulse > 0.0:
            glow = QColor(self._color)
            glow.setAlpha(int(80 * self._pulse))
            p.setBrush(glow)
            r = 3.5 + self._pulse * 2.5
            cx, cy = 3.5, 3.5
            p.drawEllipse(QPointF(cx, cy), r, r)
        # solid core
        p.setBrush(self._color)
        p.drawEllipse(QPointF(3.5, 3.5), 3.0, 3.0)
        p.end()


# ── Bell button ───────────────────────────────────────────────────────────────

class BellButton(QWidget):
    """28×28 bell icon button with optional gold unread dot."""

    clicked = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(28, 28)
        self._has_unread = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_has_unread(self, value: bool) -> None:
        self._has_unread = value
        self.update()

    def mousePressEvent(self, _event: Any) -> None:
        self.clicked.emit()

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer box
        p.setPen(QPen(QColor(tokens.HAIRLINE), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, 27, 27), 7, 7)

        pen = QPen(QColor(tokens.MUTED_FG), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # Bell dome + sides — smooth bezier silhouette
        path = QPainterPath()
        path.moveTo(7.5, 19.5)
        path.cubicTo(7.5, 10.5, 9.5, 7.0, 14.0, 7.0)
        path.cubicTo(18.5, 7.0, 20.5, 10.5, 20.5, 19.5)
        p.drawPath(path)

        # Rim
        p.drawLine(QPointF(5.5, 19.5), QPointF(22.5, 19.5))

        # Stem
        p.drawLine(QPointF(14.0, 5.0), QPointF(14.0, 7.0))

        # Clapper
        p.setBrush(QColor(tokens.MUTED_FG))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(14.0, 22.0), 1.8, 1.8)

        # Unread gold dot
        if self._has_unread:
            p.setPen(QPen(QColor(tokens.SURFACE), 1.5))
            p.setBrush(QColor(tokens.GOLD))
            p.drawEllipse(QPointF(20.5, 7.5), 3.0, 3.0)

        p.end()


# ── Topbar ────────────────────────────────────────────────────────────────────

class Topbar(QWidget):
    """
    Top navigation bar.

    Layout (left→right): breadcrumb | sparkline group | stretch |
    period control | status pill | sync button | bell.

    Signals:
        refresh_requested — sync button clicked
        period_changed(str) — W/M/Y selector changed
    """

    refresh_requested = pyqtSignal()
    period_changed    = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(tokens.TOPBAR_H)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._date_label   = QLabel(self._today_str())
        self._status_pill  = StatusPill()
        self._sync_btn     = QPushButton("↻  —")
        self._sparkline    = Sparkline()
        self._period_seg   = PeriodSegmented()
        self._bell         = BellButton()
        self._crumb_label  = QLabel("DASHBOARD / 01")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(14)

        layout.addWidget(self._build_breadcrumb(), alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addSpacing(8)
        layout.addWidget(self._build_sparkline_group())
        layout.addStretch()
        layout.addWidget(self._period_seg)
        layout.addWidget(self._status_pill)
        layout.addWidget(self._build_sync_area())
        layout.addWidget(self._bell)

        self._period_seg.period_changed.connect(self.period_changed.emit)

        self.setStyleSheet(f"""
            QWidget#topbar {{
                background: {tokens.SURFACE};
                border-bottom: 1px solid {tokens.HAIRLINE};
                font-family: "DM Mono", Consolas, monospace;
            }}
            QWidget {{
                background: transparent;
                font-family: "DM Mono", Consolas, monospace;
            }}
            QLabel#tbBreadcrumb {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 2px;
                color: {tokens.MUTED};
            }}
            QLabel#tbDate {{
                font-size: {tokens.T_MD}px;
                font-weight: 500;
                color: {tokens.FG};
            }}
            QLabel#tbSparkLbl {{
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 1px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#tbSparkVal {{
                font-size: {tokens.T_MD}px;
                font-weight: 700;
                font-family: "Playfair Display";
                color: {tokens.FG};
                background: transparent;
            }}
            QPushButton#tbSyncBtn {{
                background: transparent;
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 6px;
                padding: 4px 9px;
                font-size: {tokens.T_XS}px;
                color: {tokens.MUTED_FG};
                font-family: "DM Mono", Consolas, monospace;
            }}
            QPushButton#tbSyncBtn:hover {{
                background: {tokens.PAPER_WARM};
                color: {tokens.FG};
            }}
        """)

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def set_on_track_state(self, state: str) -> None:
        self._status_pill.set_state(state)

    def set_last_sync(self, text: str) -> None:
        self._sync_btn.setText(f"↻  {text}" if text else "↻  —")

    def set_sparkline(self, values: list[Decimal]) -> None:
        self._sparkline.set_values(values)

    def set_sparkline_total(self, text: str) -> None:
        self._spark_val_label.setText(text)

    def set_bell_unread(self, value: bool) -> None:
        self._bell.set_has_unread(value)

    def set_breadcrumb(self, text: str) -> None:
        self._crumb_label.setText(text)

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _build_breadcrumb(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(42)
        stack = QVBoxLayout(w)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(0)
        self._crumb_label.setObjectName("tbBreadcrumb")
        self._date_label.setObjectName("tbDate")
        stack.addWidget(self._crumb_label)
        stack.addWidget(self._date_label)
        return w

    def _build_sparkline_group(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        cap = QWidget()
        cap_l = QVBoxLayout(cap)
        cap_l.setContentsMargins(0, 0, 0, 0)
        cap_l.setSpacing(1)
        lbl = QLabel("LAST 7 DAYS")
        lbl.setObjectName("tbSparkLbl")
        self._spark_val_label = QLabel("—")
        self._spark_val_label.setObjectName("tbSparkVal")
        cap_l.addWidget(lbl)
        cap_l.addWidget(self._spark_val_label)

        layout.addWidget(self._sparkline)
        layout.addWidget(cap)
        return w

    def _build_sync_area(self) -> QPushButton:
        self._sync_btn.setObjectName("tbSyncBtn")
        self._sync_btn.clicked.connect(self.refresh_requested.emit)
        return self._sync_btn

    @staticmethod
    def _today_str() -> str:
        return date.today().strftime("%A, %B %d, %Y")
