"""
Hero card — the main "FREE MONEY" display card.

Custom paintEvent draws:
  - Two radial gradients + one linear gradient background (matches HTML .hero-card)
  - Dot-grain texture overlay
  - 2px state-colored rounded border (animates on state change)

Public API:
    set_state(state: str)
    set_money(value_str: str)
    set_today_changes(text: str)
    timeline → TimelineWidget  (passthrough for controller)
"""
from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,  # type: ignore[attr-defined]
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
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

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.textures import dot_grain
from expense_tracker.app.gui.widgets.heads_up_alert import HeadsUpAlert
from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget

# rgba tint for the hero card radial gradient — kept here (not in tokens.py)
# to avoid breaking the hex-only token test.
_HERO_TINT_RGBA = (252, 247, 234, 62)  # close to HTML tint, softened for Qt's heavier paint


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


class HeroCard(QWidget):
    """Custom-painted hero card with animated state transitions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        self._state       = "normal"
        self._border_color = QColor(tokens.HERO_OUTLINE_GREEN)

        # ── Child widgets ────────────────────────────────────────────────────
        self._micro       = QLabel("FREE MONEY")
        self._subtitle    = QLabel("after spend and committed charges")
        self._line        = QLabel("")
        self._period_lbl  = QLabel("PERIOD")
        self._period_val  = QLabel("")
        self._money_sym   = QLabel("₪")
        self._money_value = QLabel("0")
        self._state_badge = QLabel("ON TRACK")
        self._legend_spent = QLabel("₪0")
        self._legend_committed = QLabel("₪0")
        self._legend_fuzzy = QLabel("₪0")
        self._legend_limit = QLabel("₪0")
        self.timeline     = TimelineWidget()

        self._setup_layout()
        self.set_period_for_today()
        self._apply_state("normal", animate=False)

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    @property
    def current_state(self) -> str:
        return self._state

    def set_state(self, state: str) -> None:
        if state != self._state:
            self._apply_state(state, animate=True)

    def set_money(self, value_str: str) -> None:
        self._money_value.setText(value_str.replace("₪", "").strip())

    def set_period(self, text: str) -> None:
        self._period_val.setText(text)

    def set_period_for_today(self) -> None:
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        self.set_period(f"{today.day} / {days_in_month}")

    def set_legend(self, spent: str, committed: str, fuzzy: str, limit: str) -> None:
        self._legend_spent.setText(spent or "—")
        self._legend_committed.setText(committed or "—")
        self._legend_fuzzy.setText(fuzzy or "—")
        self._legend_limit.setText(limit or "—")
        self._legend_spent.setVisible(True)
        self._legend_committed.setVisible(True)
        self._legend_fuzzy.setVisible(True)
        self._legend_limit.setVisible(True)

    def set_daily_allowance(self, per_day: str, days_left: str) -> None:
        """Show daily remaining budget e.g. set_daily_allowance("₪61", "11 days left")."""
        self._daily_amt.setText(per_day)
        self._daily_sub.setText(f"/ day · {days_left}")

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self._heads_up.set_data(body_html, amount_str)
        self._heads_up.set_visible(visible)

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 16)
        layout.setSpacing(0)

        # Top row: label stack + period counter
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(16)
        self._micro.setObjectName("heroMicro")

        label_stack = QWidget()
        label_layout = QVBoxLayout(label_stack)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(2)

        # Arabic label alongside "FREE MONEY"
        self._arabic = QLabel("ميزان")
        self._arabic.setObjectName("heroArabic")

        label_row = QHBoxLayout()
        label_row.setContentsMargins(0, 0, 0, 0)
        label_row.setSpacing(7)
        label_row.addWidget(self._micro)
        label_row.addWidget(self._arabic)
        label_row.addStretch()

        self._subtitle.setObjectName("heroSub")
        self._line.setObjectName("heroLine")
        self._line.setFixedSize(20, 1)

        label_layout.addLayout(label_row)
        label_layout.addWidget(self._subtitle)
        label_layout.addWidget(self._line)

        period_stack = QWidget()
        period_layout = QVBoxLayout(period_stack)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(1)
        self._period_lbl.setObjectName("heroPeriodLabel")
        self._period_val.setObjectName("heroPeriodValue")
        self._period_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._period_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        period_layout.addWidget(self._period_lbl)
        period_layout.addWidget(self._period_val)

        top.addWidget(label_stack)
        top.addStretch()
        top.addWidget(period_stack)
        layout.addLayout(top)

        layout.addSpacing(6)

        # Big money
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

        # State badge + legend (combined row)
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(14)
        self._state_badge.setObjectName("heroBadge")
        self._state_badge.setFixedHeight(22)
        badge_row.addWidget(self._state_badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        badge_row.addWidget(self._build_legend())
        badge_row.addStretch()
        layout.addLayout(badge_row)

        layout.addSpacing(6)

        # Heads-up alert (always visible, fills space)
        self._heads_up = HeadsUpAlert()
        layout.addWidget(self._heads_up)

        layout.addSpacing(6)

        # Timeline
        layout.addWidget(self.timeline)

        layout.addSpacing(6)

        # Daily allowance row
        da_row = self._build_daily_allowance()
        layout.addWidget(da_row)

        self._apply_styles()

    def _build_daily_allowance(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setObjectName("dailyAllowance")
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.setSpacing(0)
        micro = QLabel("DAILY BUDGET")
        micro.setObjectName("daMicro")
        self._daily_amt = QLabel("—")
        self._daily_amt.setObjectName("daAmt")
        left_l.addWidget(micro)
        left_l.addWidget(self._daily_amt)

        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(2)
        right_l.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._daily_sub = QLabel("")
        self._daily_sub.setObjectName("daSub")
        self._daily_sub.setAlignment(Qt.AlignmentFlag.AlignRight)
        days_bar = QWidget()
        days_bar.setObjectName("daBar")
        days_bar.setFixedHeight(4)

        right_l.addWidget(self._daily_sub)
        right_l.addWidget(days_bar)

        row.addWidget(left)
        row.addWidget(right, stretch=1)
        return wrapper

    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QLabel#heroMicro {{
                color: {tokens.MUTED_FG};
                font-size: {tokens.T_MINI}px;
                letter-spacing: 2px;
                font-family: "DM Mono", Consolas, monospace;
                font-weight: 500;
                background: transparent;
            }}
            QLabel#heroSub {{
                color: {tokens.MUTED};
                font-size: {tokens.T_MINI}px;
                font-family: "DM Mono", Consolas, monospace;
                background: transparent;
            }}
            QLabel#heroPeriodLabel {{
                color: {tokens.MUTED};
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 1px;
                font-family: "DM Mono", Consolas, monospace;
                background: transparent;
            }}
            QLabel#heroPeriodValue {{
                color: {tokens.FG};
                font-family: "Playfair Display";
                font-size: {tokens.T_MD}px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#heroMoneySym {{
                color: rgba(24,26,44,0.38);
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 20px;
                padding-bottom: 8px;
                background: transparent;
            }}
            QLabel#heroMoney {{
                color: {tokens.FG};
                font-family: "Playfair Display";
                font-size: 52px;
                font-weight: 900;
                letter-spacing: -0.03em;
                background: transparent;
            }}
            QWidget#dailyAllowance {{
                background: transparent;
            }}
            QLabel#daMicro {{
                font-size: {tokens.T_MICRO}px; letter-spacing: 0.18em;
                color: {tokens.MUTED}; background: transparent;
            }}
            QLabel#daAmt {{
                font-family: "Playfair Display"; font-size: 22px; font-weight: 700;
                color: {tokens.FG}; background: transparent;
            }}
            QLabel#daSub {{
                font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG};
                font-family: "DM Mono", Consolas, monospace; background: transparent;
            }}
            QWidget#daBar {{
                background: {tokens.TRACK}; border-radius: 2px;
            }}
            QLabel#heroArabic {{
                font-family: "Noto Naskh Arabic"; font-size: 13px;
                color: rgba(168,124,36,0.65); background: transparent;
            }}
            QWidget#heroLine {{
                background: {tokens.GOLD}; border: none;
            }}
        """)

    def _build_legend(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(self._legend_item(tokens.GOLD_LEAF, "Spent", self._legend_spent))
        layout.addWidget(self._legend_item(tokens.RED, "Committed", self._legend_committed))
        layout.addWidget(self._legend_item(tokens.AMBER, "Fuzzy", self._legend_fuzzy, striped=True))
        layout.addWidget(self._legend_item(tokens.MUTED, "Limit", self._legend_limit, outline=True))
        layout.addStretch()
        return w

    def _legend_item(
        self,
        color: str,
        label: str,
        value_label: QLabel,
        striped: bool = False,
        outline: bool = False,
    ) -> QWidget:
        item = QWidget()
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        if striped:
            dot.setStyleSheet(
                f"background: rgba(150,46,46,0.18);"
                f"border: 1px solid {tokens.RED};"
                "border-radius: 4px;"
            )
        elif outline:
            dot.setStyleSheet(
                f"background: transparent; border: 1px solid {color}; border-radius: 4px;"
            )
        else:
            dot.setStyleSheet(f"background: {color}; border: none; border-radius: 4px;")

        text = QLabel(label)
        text.setStyleSheet(
            f"color: {tokens.MUTED_FG}; font-size: {tokens.T_SM}px;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        value_label.setStyleSheet(
            f"color: {color}; font-size: {tokens.T_SM}px; font-weight: 500;"
            "font-family: 'DM Mono', 'Segoe UI', Consolas, monospace; background: transparent;"
        )

        layout.addWidget(dot)
        layout.addWidget(text)
        layout.addWidget(value_label)
        return item

    def _apply_state(self, state: str, animate: bool = True) -> None:
        cfg = _STATES.get(state, _STATES["normal"])
        self._state = state

        # Badge
        self._state_badge.setText(cfg["badge_text"])
        self._state_badge.setStyleSheet(
            f"color: {cfg['badge_color']};"
            f"background: {cfg['badge_bg']};"
            f"border: 1px solid {cfg['badge_border']};"
            f"border-radius: 3px;"
            f"font-size: {tokens.T_MINI}px;"
            f"font-weight: 500;"
            f"letter-spacing: 1px;"
            f"padding: 3px 10px;"
            f"font-family: 'DM Mono', Consolas, monospace;"
        )

        # Border color
        self._border_color = QColor(cfg["border"])
        self.update()

    # ── PAINT ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        r = float(tokens.HERO_RADIUS)
        rect = QRectF(1, 1, w - 2, h - 2)

        # ── Radial tint top-right ─────────────────────────────────────────────
        rg1 = QRadialGradient(QPointF(w * 0.88, 0), w * 0.6) 
        tint_c = QColor(*_HERO_TINT_RGBA)
        rg1.setColorAt(0, tint_c)
        rg1.setColorAt(1, Qt.GlobalColor.transparent)

        # ── Radial warm bottom-left ───────────────────────────────────────────
        warm = QColor(246, 238, 222)
        warm.setAlpha(42)
        rg2 = QRadialGradient(QPointF(w * 0.08, h), w * 0.55)
        rg2.setColorAt(0, warm)
        rg2.setColorAt(1, Qt.GlobalColor.transparent)

        # ── Linear gradient base ──────────────────────────────────────────────
        lg = QLinearGradient(QPointF(0, 0), QPointF(w, h))
        lg.setColorAt(0, QColor(tokens.HERO_BG1))
        lg.setColorAt(1, QColor(tokens.HERO_BG2))

        # Draw base gradient
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(lg)
        p.drawRoundedRect(rect, r, r)

        # Radial overlays
        p.setBrush(rg2)
        p.drawRoundedRect(rect, r, r)
        p.setBrush(rg1)
        p.drawRoundedRect(rect, r, r)

        # ── Dot grain overlay ─────────────────────────────────────────────────
        p.setOpacity(0.18)
        p.setBrush(QBrush(dot_grain()))
        p.drawRoundedRect(rect, r, r)
        p.setOpacity(1.0)

        # ── Border ────────────────────────────────────────────────────────────
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(self._border_color, 2))
        p.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)

        p.end()
