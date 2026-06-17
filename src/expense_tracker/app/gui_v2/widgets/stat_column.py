from __future__ import annotations

from decimal import Decimal
from typing import Any, TYPE_CHECKING

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens

if TYPE_CHECKING:
    from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel


def _split_amount(amount_str: str) -> tuple[str, str]:
    s = amount_str.strip()
    if s.startswith("₪"):
        return "₪", s[1:]
    return "", s


class BurnBars(QWidget):
    """Horizontal bar: green (spent) over hairline track."""

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
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.HAIRLINE_S))
        p.setOpacity(0.5)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)
        p.setOpacity(1.0)
        spent_w = max(0.0, w * self._spent_pct / 100.0)
        if spent_w > 0:
            p.setBrush(QColor(tokens.GREEN))
            p.drawRoundedRect(QRectF(0, 0, spent_w, h), r, r)
        p.end()


def _stat_card(micro: str, context: str, value_color: str, value_size: int = 28) -> tuple[QFrame, QLabel, QLabel]:
    frame = QFrame()
    frame.setObjectName("statCard")
    frame.setStyleSheet(f"""
        QFrame#statCard {{
            background: {tokens.SURFACE}; border: 1px solid {tokens.HAIRLINE};
            border-radius: {tokens.CARD_RADIUS}px;
        }}
        QLabel#sMicro {{ font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace; background: transparent; }}
        QLabel#sCtx {{ font-size: {tokens.T_SM}px; color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace; background: transparent; }}
        QLabel#sSub {{ font-size: {tokens.T_SM}px; color: {tokens.MUTED};
            font-family: "DM Mono", Consolas, monospace; background: transparent; }}
    """)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(3)
    micro_lbl = QLabel(micro)
    micro_lbl.setObjectName("sMicro")
    ctx_lbl = QLabel(context)
    ctx_lbl.setObjectName("sCtx")
    amt_row = QWidget()
    amt_row.setStyleSheet("background: transparent;")
    amt_layout = QHBoxLayout(amt_row)
    amt_layout.setContentsMargins(0, 0, 0, 0)
    amt_layout.setSpacing(2)
    sym = QLabel("₪")
    sym.setStyleSheet(
        "color: rgba(24,26,44,0.38); font-size: 12px;"
        "font-family: 'Segoe UI', 'Arial', sans-serif; background: transparent;"
    )
    val = QLabel("0")
    val.setObjectName("statValue")
    val.setStyleSheet(
        f"color: {value_color}; font-family: 'Playfair Display';"
        f"font-size: {value_size}px; font-weight: 700;"
        f"letter-spacing: -0.01em; background: transparent;"
    )
    val.setMinimumHeight(value_size + 6)
    amt_layout.addWidget(sym, alignment=Qt.AlignmentFlag.AlignBottom)
    amt_layout.addWidget(val, alignment=Qt.AlignmentFlag.AlignBottom)
    amt_layout.addStretch()
    sub = QLabel("")
    sub.setObjectName("sSub")
    layout.addWidget(micro_lbl)
    layout.addWidget(ctx_lbl)
    layout.addWidget(amt_row)
    layout.addWidget(sub)
    return frame, val, sub


class StatColumn(QWidget):
    """Fixed 290px right-side column with three stat cards fed via set_snapshot()."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(tokens.STAT_COL_W)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        spent_card, self._spent_val, self._spent_sub = _stat_card(
            "SPENT · MTD", "this calendar month", tokens.GOLD_LEAF, 28
        )
        self._delta_lbl = QLabel("")
        self._delta_lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; font-family: 'DM Mono', Consolas, monospace;"
            "background: transparent;"
        )
        spent_card.layout().addWidget(self._delta_lbl)

        committed_card, self._committed_val, self._committed_sub = _stat_card(
            "COMMITTED", "charges this month", tokens.RED, 28
        )

        left_card, self._left_val, self._left_sub = _stat_card(
            "MONTHLY LEFT", "income minus charges minus spend", tokens.GREEN, 26
        )
        self._burn = BurnBars()
        burn_lbls_w = QWidget()
        burn_lbls = QHBoxLayout(burn_lbls_w)
        burn_lbls.setContentsMargins(0, 2, 0, 0)
        burn_lbls.setSpacing(0)
        self._burn_spent_lbl = QLabel("")
        self._burn_left_lbl = QLabel("")
        for lbl in (self._burn_spent_lbl, self._burn_left_lbl):
            lbl.setStyleSheet(
                f"font-size: {tokens.T_MINI}px; color: {tokens.MUTED};"
                "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
            )
        self._burn_left_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        burn_lbls.addWidget(self._burn_spent_lbl)
        burn_lbls.addStretch()
        burn_lbls.addWidget(self._burn_left_lbl)
        left_card.layout().addWidget(self._burn)
        left_card.layout().addWidget(burn_lbls_w)

        layout.addWidget(spent_card)
        layout.addWidget(committed_card)
        layout.addWidget(left_card, stretch=1)

    def set_snapshot(self, vm: BalanceViewModel) -> None:
        """Populate all stat card values from the given view model."""
        _, spent_num     = _split_amount(vm.monthly_spent_str)
        _, committed_num = _split_amount(vm.monthly_committed_str)
        _, left_num      = _split_amount(vm.monthly_left_str)
        self._spent_val.setText(spent_num)
        self._committed_val.setText(committed_num)
        self._left_val.setText(left_num)
        budget = vm.monthly_budget
        pct = float(vm.monthly_spent / budget * 100) if budget > Decimal("0") else 0.0
        self._burn.set_pcts(pct)
        self._burn_spent_lbl.setText(f"{vm.monthly_spent_str} spent")
        self._burn_left_lbl.setText(f"{vm.monthly_left_str} left")
