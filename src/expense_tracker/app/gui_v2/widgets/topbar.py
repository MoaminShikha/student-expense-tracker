from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens


class _PulseDot(QWidget):
    """7×7 pulsing dot driven by an external float (0→1)."""

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
        if self._pulse > 0.0:
            glow = QColor(self._color)
            glow.setAlpha(int(80 * self._pulse))
            p.setBrush(glow)
            r = 3.5 + self._pulse * 2.5
            p.drawEllipse(QPointF(3.5, 3.5), r, r)
        p.setBrush(self._color)
        p.drawEllipse(QPointF(3.5, 3.5), 3.0, 3.0)
        p.end()


class StatusPill(QFrame):
    """Animated status pill with pulsing dot and state text."""

    _STATES = {
        "green":       {"text": "On track",    "color": tokens.GREEN,   "bg": tokens.GREEN_BG},
        "yellow":      {"text": "Caution",     "color": tokens.AMBER,   "bg": tokens.AMBER_BG},
        "red":         {"text": "Over budget", "color": tokens.RED,     "bg": "#fce8e8"},
        "tight_month": {"text": "Tight month", "color": tokens.MUTED_FG, "bg": tokens.BG},
    }

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("statusPill")
        self.setFixedHeight(26)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 12, 0)
        layout.setSpacing(6)
        self._dot = _PulseDot(tokens.GREEN)
        self._label = QLabel("On track")
        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(1200)
        anim.setLoopCount(-1)
        anim.setEasingCurve(QEasingCurve.Type.SineCurve)
        anim.valueChanged.connect(self._dot.set_pulse)
        anim.start()
        self.set_status("green")

    def set_status(self, state: str) -> None:
        """Update the pill for the given state key."""
        cfg = self._STATES.get(state, self._STATES["green"])
        self._label.setText(cfg["text"])
        self._dot.set_color(cfg["color"])
        self.setStyleSheet(
            f"QFrame#statusPill {{ background: {cfg['bg']}; border: none; border-radius: 13px; }}"
        )
        self._label.setStyleSheet(
            f"color: {cfg['color']}; font-size: {tokens.T_XS}px; font-weight: 500;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )


class Topbar(QWidget):
    """
    Application topbar: breadcrumb | stretch | status pill | sync button | bell.

    Signals:
        refresh_requested — sync button clicked
    """

    refresh_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(tokens.TOPBAR_H)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._crumb  = QLabel("DASHBOARD / 01")
        self._date   = QLabel(date.today().strftime("%A, %B %d, %Y"))
        self._pill   = StatusPill()
        self._sync   = QPushButton("↻  —")
        self._sync.setObjectName("tbSyncBtn")
        self._sync.clicked.connect(self.refresh_requested.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(14)
        layout.addWidget(self._build_breadcrumb(), alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()
        layout.addWidget(self._pill)
        layout.addWidget(self._sync)

        self.setStyleSheet(f"""
            QWidget#topbar {{
                background: {tokens.SURFACE};
                border-bottom: 1px solid {tokens.HAIRLINE};
                font-family: "DM Mono", Consolas, monospace;
            }}
            QWidget {{ background: transparent; }}
            QLabel#tbBreadcrumb {{
                font-size: {tokens.T_MINI}px; letter-spacing: 2px; color: {tokens.MUTED};
            }}
            QLabel#tbDate {{
                font-size: {tokens.T_MD}px; font-weight: 500; color: {tokens.FG};
            }}
            QPushButton#tbSyncBtn {{
                background: transparent; border: 1px solid {tokens.HAIRLINE};
                border-radius: 6px; padding: 4px 9px; font-size: {tokens.T_XS}px;
                color: {tokens.MUTED_FG};
            }}
            QPushButton#tbSyncBtn:hover {{
                background: {tokens.PAPER_WARM}; color: {tokens.FG};
            }}
        """)

    def set_status(self, state: str) -> None:
        """Update the status pill for the given on-track state key."""
        self._pill.set_status(state)

    def set_on_track_state(self, state: str) -> None:
        """Alias for set_status for compatibility."""
        self._pill.set_status(state)

    def set_last_sync(self, text: str) -> None:
        """Update the sync button timestamp label."""
        self._sync.setText(f"↻  {text}" if text else "↻  —")

    def set_breadcrumb(self, text: str) -> None:
        """Update the page breadcrumb label."""
        self._crumb.setText(text)

    def _build_breadcrumb(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(42)
        stack = QVBoxLayout(w)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(0)
        self._crumb.setObjectName("tbBreadcrumb")
        self._date.setObjectName("tbDate")
        stack.addWidget(self._crumb)
        stack.addWidget(self._date)
        return w
