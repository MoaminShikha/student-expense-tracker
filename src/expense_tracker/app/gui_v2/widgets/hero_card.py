from __future__ import annotations

import calendar
from datetime import date
from functools import lru_cache
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    Qt,
    QVariantAnimation,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens

# Shared TimelineWidget — geometry-only, no theme coupling.
from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget

_STATES: dict[str, dict] = {
    "normal": {
        "border":       tokens.HERO_OUTLINE_GREEN,
        "badge_text":   "ON TRACK",
        "badge_color":  tokens.GOLD_LEAF,
        "badge_bg":     "rgba(199,154,57,0.12)",
        "badge_border": "rgba(199,154,57,0.28)",
    },
    "caution": {
        "border":       tokens.HERO_OUTLINE_AMBER,
        "badge_text":   "CAUTION",
        "badge_color":  tokens.AMBER,
        "badge_bg":     "rgba(160,87,18,0.12)",
        "badge_border": "rgba(160,87,18,0.28)",
    },
    "crisis": {
        "border":       tokens.HERO_OUTLINE_RED,
        "badge_text":   "CRISIS",
        "badge_color":  tokens.RED,
        "badge_bg":     "rgba(150,46,46,0.12)",
        "badge_border": "rgba(150,46,46,0.28)",
    },
}


@lru_cache(maxsize=1)
def _dot_grain(tile: int = 3) -> QPixmap:
    px = QPixmap(tile, tile)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(158, 148, 116, 35))
    p.drawRect(0, 0, 1, 1)
    p.end()
    return px


class CountingLabel(QLabel):
    """QLabel that animates a numeric value change with a 600 ms roll-up."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("0", parent)
        self._current_value: float = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_value)

    def set_value(self, target: float) -> None:
        """Animate from the current display value to target."""
        self._anim.stop()
        self._anim.setStartValue(self._current_value)
        self._anim.setEndValue(target)
        self._anim.start()

    def _on_value(self, val: float) -> None:
        self._current_value = float(val)
        self.setText(f"{self._current_value:,.0f}")


class _HeadsUpAlert(QWidget):
    """Amber alert strip — self-contained, uses gui_v2 tokens only."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._frame = QFrame()
        self._frame.setObjectName("huAlert")
        self._frame.setStyleSheet(f"""
            QFrame#huAlert {{
                background: {tokens.AMBER_BG};
                border: 1px solid {tokens.AMBER_BD};
                border-radius: 10px;
            }}
        """)
        inner = QHBoxLayout(self._frame)
        inner.setContentsMargins(14, 8, 14, 8)
        inner.setSpacing(10)
        self._badge = QLabel("▲  HEADS-UP")
        self._badge.setStyleSheet(
            f"background: rgba(160,87,18,0.15); color: {tokens.AMBER};"
            f"font-size: {tokens.T_MINI}px; letter-spacing: 1px;"
            "font-family: 'DM Mono', Consolas, monospace; font-weight: 500;"
            "padding: 3px 8px; border-radius: 4px;"
        )
        self._badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._body = QLabel("")
        self._body.setStyleSheet(
            f"color: {tokens.FG}; font-size: {tokens.T_SM}px;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        self._body.setTextFormat(Qt.TextFormat.PlainText)
        self._body.setWordWrap(True)
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._amount = QLabel("")
        self._amount.setStyleSheet(
            f"color: {tokens.RED}; font-family: 'Playfair Display';"
            "font-size: 14px; font-weight: 700; background: transparent;"
        )
        self._amount.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        inner.addWidget(self._badge)
        inner.addWidget(self._body, stretch=1)
        inner.addWidget(self._amount)
        outer.addWidget(self._frame)
        self.setVisible(False)

    def set_data(self, body_text: str, amount_str: str) -> None:
        self._body.setText(body_text)
        self._amount.setText(amount_str)

    def set_visible(self, visible: bool) -> None:  # type: ignore[override]
        self.setVisible(visible)


class HeroCard(QWidget):
    """Custom-painted hero card with animated state transitions and CountingLabel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        self._state        = "normal"
        self._border_color = QColor(tokens.HERO_OUTLINE_GREEN)

        self._micro       = QLabel("FREE MONEY")
        self._subtitle    = QLabel("after spend and committed charges")
        self._period_lbl  = QLabel("PERIOD")
        self._period_val  = QLabel("")
        self._money_sym   = QLabel("₪")
        self._money_value = CountingLabel()
        self._badge       = QLabel("ON TRACK")
        self._legend_spent     = QLabel("₪0")
        self._legend_committed = QLabel("₪0")
        self._legend_fuzzy     = QLabel("₪0")
        self._legend_limit     = QLabel("₪0")
        self.timeline     = TimelineWidget()
        self._heads_up    = _HeadsUpAlert()

        self._setup_layout()
        self.set_period_for_today()
        self._apply_state("normal", animate=False)

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    @property
    def current_state(self) -> str:
        """Return the current state key ('normal', 'caution', or 'crisis')."""
        return self._state

    def set_state(self, state: str) -> None:
        """Transition the card to a new state, animating the border if it changes."""
        if state != self._state:
            self._apply_state(state, animate=True)

    def set_money_value(self, value_str: str) -> None:
        """Animate the free-money display to the numeric value encoded in value_str."""
        clean = value_str.replace("₪", "").replace(",", "").strip()
        try:
            self._money_value.set_value(float(clean))
        except ValueError:
            self._money_value.setText(clean)

    def set_money(self, value_str: str) -> None:
        """Alias for set_money_value."""
        self.set_money_value(value_str)

    def set_period(self, text: str) -> None:
        """Set the period counter label (e.g. '17 / 30')."""
        self._period_val.setText(text)

    def set_period_for_today(self) -> None:
        """Update the period counter to today's day / days-in-month."""
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        self.set_period(f"{today.day} / {days_in_month}")

    def set_legend(self, spent: str, committed: str, fuzzy: str, limit: str) -> None:
        """Populate the four legend value labels."""
        self._legend_spent.setText(spent or "—")
        self._legend_committed.setText(committed or "—")
        self._legend_fuzzy.setText(fuzzy or "—")
        self._legend_limit.setText(limit or "—")

    def set_alert(self, body_text: str, amount_str: str, visible: bool) -> None:
        """Show or hide the heads-up alert strip."""
        self._heads_up.set_data(body_text, amount_str)
        self._heads_up.set_visible(visible)

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 16)
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        self._micro.setObjectName("heroMicro")
        self._subtitle.setObjectName("heroSub")
        lstack = QVBoxLayout()
        lstack.setContentsMargins(0, 0, 0, 0)
        lstack.setSpacing(2)
        lstack.addWidget(self._micro)
        lstack.addWidget(self._subtitle)
        self._period_lbl.setObjectName("heroPeriodLabel")
        self._period_val.setObjectName("heroPeriodValue")
        self._period_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._period_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        rstack = QVBoxLayout()
        rstack.setContentsMargins(0, 0, 0, 0)
        rstack.setSpacing(1)
        rstack.addWidget(self._period_lbl)
        rstack.addWidget(self._period_val)
        top.addLayout(lstack)
        top.addStretch()
        top.addLayout(rstack)
        layout.addLayout(top)
        layout.addSpacing(6)

        money_row = QHBoxLayout()
        money_row.setContentsMargins(0, 0, 0, 0)
        money_row.setSpacing(2)
        self._money_sym.setObjectName("heroMoneySym")
        self._money_value.setObjectName("heroMoney")
        money_row.addWidget(self._money_sym, alignment=Qt.AlignmentFlag.AlignBottom)
        money_row.addWidget(self._money_value, alignment=Qt.AlignmentFlag.AlignBaseline)
        money_row.addStretch()
        layout.addLayout(money_row)
        layout.addSpacing(4)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(14)
        self._badge.setObjectName("heroBadge")
        self._badge.setFixedHeight(22)
        badge_row.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        badge_row.addWidget(self._build_legend())
        badge_row.addStretch()
        layout.addLayout(badge_row)
        layout.addSpacing(8)

        layout.addWidget(self._heads_up)
        layout.addSpacing(4)
        layout.addWidget(self.timeline)

        self._apply_styles()

    def _build_legend(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._legend_item(tokens.GOLD_LEAF,  "Spent",     self._legend_spent))
        layout.addWidget(self._legend_item(tokens.RED,        "Committed", self._legend_committed))
        layout.addWidget(self._legend_item(tokens.AMBER,      "Fuzzy",     self._legend_fuzzy))
        layout.addWidget(self._legend_item(tokens.MUTED,      "Limit",     self._legend_limit))
        return w

    def _legend_item(self, color: str, label: str, value_label: QLabel) -> QWidget:
        item = QWidget()
        item.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        dot = QFrame()
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(f"background: {color}; border: none; border-radius: 3px;")
        text = QLabel(label)
        text.setStyleSheet(
            f"color: {tokens.MUTED_FG}; font-size: {tokens.T_SM}px;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        value_label.setStyleSheet(
            f"color: {color}; font-size: {tokens.T_SM}px; font-weight: 500;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(dot)
        layout.addWidget(text)
        layout.addWidget(value_label)
        return item

    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QLabel#heroMicro {{
                color: {tokens.MUTED_FG}; font-size: {tokens.T_MINI}px;
                letter-spacing: 2px; font-family: "DM Mono", Consolas, monospace;
                font-weight: 500; background: transparent;
            }}
            QLabel#heroSub {{
                color: {tokens.MUTED}; font-size: {tokens.T_MINI}px;
                font-family: "DM Mono", Consolas, monospace; background: transparent;
            }}
            QLabel#heroPeriodLabel {{
                color: {tokens.MUTED}; font-size: {tokens.T_MICRO}px;
                letter-spacing: 1px; font-family: "DM Mono", Consolas, monospace;
                background: transparent;
            }}
            QLabel#heroPeriodValue {{
                color: {tokens.FG}; font-family: "Playfair Display";
                font-size: {tokens.T_MD}px; font-weight: 700; background: transparent;
            }}
            QLabel#heroMoneySym {{
                color: rgba(24,26,44,0.38); font-size: 20px;
                font-family: "Segoe UI", "Arial", sans-serif;
                padding-bottom: 6px; background: transparent;
            }}
            QLabel#heroMoney {{
                color: {tokens.FG}; font-family: "Playfair Display";
                font-size: 52px; font-weight: 900;
                letter-spacing: -0.03em; background: transparent;
            }}
        """)

    def _apply_state(self, state: str, animate: bool = True) -> None:
        cfg = _STATES.get(state, _STATES["normal"])
        self._state = state
        self._badge.setText(cfg["badge_text"])
        self._badge.setStyleSheet(
            f"color: {cfg['badge_color']}; background: {cfg['badge_bg']};"
            f"border: 1px solid {cfg['badge_border']}; border-radius: 3px;"
            f"font-size: {tokens.T_MINI}px; font-weight: 500; letter-spacing: 1px;"
            f"padding: 3px 10px; font-family: 'DM Mono', Consolas, monospace;"
        )
        self._border_color = QColor(cfg["border"])
        self.update()

    # ── PAINT ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        r = float(tokens.HERO_RADIUS)
        rect = QRectF(1, 1, w - 2, h - 2)

        # Warm parchment gradient (always light in gui_v2)
        lg = QLinearGradient(QPointF(0, 0), QPointF(w, h))
        lg.setColorAt(0, QColor(tokens.HERO_BG1))
        lg.setColorAt(1, QColor(tokens.HERO_BG2))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(lg)
        p.drawRoundedRect(rect, r, r)

        # Radial warm tint (top-right)
        rg = QRadialGradient(QPointF(w * 0.88, 0), w * 0.6)
        rg.setColorAt(0, QColor(252, 247, 234, 62))
        rg.setColorAt(1, Qt.GlobalColor.transparent)
        p.setBrush(rg)
        p.drawRoundedRect(rect, r, r)

        # Dot grain texture
        p.setOpacity(0.18)
        p.setBrush(QBrush(_dot_grain()))
        p.drawRoundedRect(rect, r, r)
        p.setOpacity(1.0)

        # State border
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(self._border_color, 2))
        p.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)
        p.end()
