"""
Stat column — three stacked cards to the right of the hero card.

Cards:
  1. SPENT MTD      — gold-leaf, 28px Playfair, delta row
  2. COMMITTED       — red, 28px Playfair, "due in N days" sub
  3. MONTHLY LEFT    — green, 26px Playfair, explanation, QPainter BurnBars

All values pushed via set_snapshot(vm: BalanceViewModel).
"""
from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens

if __name__ != "__main__":
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


# ── BurnBars ──────────────────────────────────────────────────────────────────

class BurnBars(QWidget):
    """
    24px-tall horizontal bar: green (spent portion) + hairline (remaining).
    Each "bar" is a single pixel-wide band drawn by paintEvent.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(24)
        self._spent_pct: float = 0.0

    def set_pcts(self, spent_pct: float) -> None:
        self._spent_pct = max(0.0, min(100.0, spent_pct))
        self.update()

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = 2.0

        from PyQt6.QtCore import QRectF
        # Background track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.HAIRLINE_S))
        p.setOpacity(0.5)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)
        p.setOpacity(1.0)

        # Spent portion
        spent_w = max(0.0, w * self._spent_pct / 100.0)
        if spent_w > 0:
            p.setBrush(QColor(tokens.GREEN))
            p.drawRoundedRect(QRectF(0, 0, spent_w, h), r, r)

        p.end()


# ── Card builder ──────────────────────────────────────────────────────────────

def _stat_card(
    micro_text: str,
    context_text: str,
    value_color: str,
    value_size: int = 28,
) -> tuple[QFrame, QLabel, QLabel]:
    """Return (frame, value_label, sub_label)."""
    frame = QFrame()
    frame.setObjectName("statCard")
    frame.setStyleSheet(f"""
        QFrame#statCard {{
            background: {tokens.SURFACE};
            border: 1px solid {tokens.HAIRLINE};
            border-radius: {tokens.CARD_RADIUS}px;
        }}
        QLabel#sMicro {{
            font-size: {tokens.T_MICRO}px;
            letter-spacing: 3px;
            color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        }}
        QLabel#sCtx {{
            font-size: {tokens.T_SM}px;
            color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        }}
        QLabel#sSub {{
            font-size: {tokens.T_SM}px;
            color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        }}
        QLabel#sDelta {{
            font-size: {tokens.T_SM}px;
            font-family: "DM Mono", Consolas, monospace;
            background: transparent;
        }}
    """)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(3)

    micro = QLabel(micro_text)
    micro.setObjectName("sMicro")
    ctx = QLabel(context_text)
    ctx.setObjectName("sCtx")

    val = QLabel("₪0")
    val.setObjectName("statValue")
    val.setStyleSheet(
        f"color: {value_color};"
        f"font-family: 'Playfair Display';"
        f"font-size: {value_size}px;"
        f"font-weight: 700;"
        f"letter-spacing: -0.01em;"
        f"background: transparent;"
    )
    val.setMinimumHeight(value_size + 14)

    sub = QLabel("")
    sub.setObjectName("sSub")

    layout.addWidget(micro)
    layout.addWidget(ctx)
    layout.addWidget(val)
    layout.addWidget(sub)

    return frame, val, sub


# ── StatColumn ────────────────────────────────────────────────────────────────

class StatColumn(QWidget):
    """
    Fixed 290px right-side column with three stat cards.
    Fed exclusively through set_snapshot(vm).
    """

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(tokens.STAT_COL_W)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Card 1 — SPENT MTD
        spent_card, self._spent_val, self._spent_sub = _stat_card(
            "SPENT · MTD", "this calendar month", tokens.GOLD_LEAF, 28
        )
        # add delta row to spent card
        self._delta_lbl = QLabel("")
        self._delta_lbl.setObjectName("sDelta")
        spent_card.layout().addWidget(self._delta_lbl)

        # Card 2 — COMMITTED
        committed_card, self._committed_val, self._committed_sub = _stat_card(
            "COMMITTED", "charges this month", tokens.RED, 28
        )

        # Card 3 — MONTHLY LEFT
        left_card, self._left_val, self._left_sub = _stat_card(
            "MONTHLY LEFT", "", tokens.GREEN, 26
        )
        self._burn = BurnBars()
        # Labels row under burn bar
        burn_lbls_w = QWidget()
        burn_lbls = QHBoxLayout(burn_lbls_w)
        burn_lbls.setContentsMargins(0, 2, 0, 0)
        burn_lbls.setSpacing(0)
        self._burn_spent_lbl = QLabel("")
        self._burn_left_lbl  = QLabel("")
        for lbl in (self._burn_spent_lbl, self._burn_left_lbl):
            lbl.setStyleSheet(
                f"font-size: {tokens.T_MINI}px; color: {tokens.MUTED};"
                f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
            )
        self._burn_left_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        burn_lbls.addWidget(self._burn_spent_lbl)
        burn_lbls.addStretch()
        burn_lbls.addWidget(self._burn_left_lbl)

        left_layout = left_card.layout()
        left_layout.addWidget(self._burn)
        left_layout.addWidget(burn_lbls_w)

        layout.addWidget(spent_card)
        layout.addWidget(committed_card)
        layout.addWidget(left_card, stretch=1)

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def set_snapshot(self, vm: "BalanceViewModel") -> None:
        from decimal import Decimal
        self._spent_val.setText(vm.monthly_spent_str)
        self._committed_val.setText(vm.monthly_budget_str)
        self._left_val.setText(vm.monthly_left_str)

        # Burn bar
        budget = vm.monthly_budget
        if budget > Decimal("0"):
            pct = float(vm.monthly_spent / budget * 100)
        else:
            pct = 0.0
        self._burn.set_pcts(pct)
        self._burn_spent_lbl.setText(f"{vm.monthly_spent_str} spent")
        self._burn_left_lbl.setText(f"{vm.monthly_left_str} left")

    def set_delta(self, pct: float, direction: str) -> None:
        """direction: 'up' | 'down' | 'flat'"""
        if direction == "down":
            arrow, color = "↓", tokens.GREEN
        elif direction == "up":
            arrow, color = "↑", tokens.RED
        else:
            arrow, color = "→", tokens.MUTED
        text = f"{arrow}  {abs(pct):.0f}% vs last month"
        self._delta_lbl.setText(text)
        self._delta_lbl.setStyleSheet(
            f"color: {color}; font-size: {tokens.T_SM}px;"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )

    def set_due_in(self, text: str) -> None:
        self._committed_sub.setText(text)
