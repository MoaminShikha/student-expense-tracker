from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.ledger_view_model import LedgerEntryVM


class _FilterPill(QPushButton):
    def __init__(self, text: str, active: bool = False) -> None:
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_XS}px;
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 999px;
                padding: 4px 14px;
                background: transparent;
                color: {tokens.MUTED_FG};
            }}
            QPushButton:checked {{
                background: {tokens.NAVY};
                color: {tokens.GOLD};
                border-color: {tokens.NAVY};
                font-weight: 500;
            }}
            QPushButton:hover:!checked {{
                background: {tokens.PAPER_WARM};
            }}
        """)


class _LedgerRow(QWidget):
    def __init__(self, entry: LedgerEntryVM, even: bool) -> None:
        super().__init__()
        self.setObjectName("ledgerRow")
        bg = "transparent" if even else "rgba(36,28,10,0.03)"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 8, 24, 8)
        layout.setSpacing(12)

        date_lbl = QLabel(entry.date.strftime("%d %b"))
        date_lbl.setFixedWidth(60)
        date_lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            f"font-family: 'DM Mono', Consolas, monospace; background: transparent;")

        desc_lbl = QLabel(entry.description)
        desc_lbl.setStyleSheet(
            f"font-size: {tokens.T_BASE}px; color: {tokens.FG};"
            f"font-family: 'DM Mono', Consolas, monospace; font-weight: 500; background: transparent;")
        desc_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        badge_colors = {
            "income": (tokens.GREEN, tokens.GREEN_BG, "+"),
            "spend": (tokens.RED, "#fce8e8", "−"),
            "charge": (tokens.AMBER, tokens.AMBER_BG, "•"),
        }
        fg, bg_color, symbol = badge_colors.get(entry.entry_type, (tokens.MUTED_FG, tokens.BG, "?"))
        badge = QLabel(f" {symbol} ")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedWidth(28)
        badge.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {fg}; background: {bg_color};"
            f"border-radius: 4px; font-weight: 700; font-family: 'DM Mono', Consolas, monospace;")

        amt_color = tokens.GREEN if entry.entry_type == "income" else tokens.RED
        amt_lbl = QLabel(entry.amount_str)
        amt_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt_lbl.setFixedWidth(100)
        amt_lbl.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px;"
            f"font-weight: 700; color: {amt_color}; background: transparent;")

        bal_lbl = QLabel(entry.running_balance_str)
        bal_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        bal_lbl.setFixedWidth(100)
        bal_lbl.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px;"
            f"font-weight: 700; color: {tokens.FG}; background: transparent;")

        layout.addWidget(date_lbl)
        layout.addWidget(desc_lbl, stretch=1)
        layout.addWidget(badge)
        layout.addWidget(amt_lbl)
        layout.addWidget(bal_lbl)
        self.setStyleSheet(f"QWidget#ledgerRow {{ background: {bg}; border-bottom: 1px solid {tokens.HAIRLINE}; }}"
                           f"QWidget#ledgerRow:hover {{ background: rgba(199,154,57,0.06); }}")


class ActivityPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("activityPage")
        self._filter = "all"
        self._all_entries: list[LedgerEntryVM] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._build_summary(outer)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {tokens.BG}; border: none; }}")
        self._content = PaperWidget()
        self._content.setObjectName("activityContent")
        self._ledger_layout = QVBoxLayout(self._content)
        self._ledger_layout.setContentsMargins(0, 0, 0, 0)
        self._ledger_layout.setSpacing(0)
        scroll.setWidget(self._content)
        outer.addWidget(scroll, stretch=1)

    def _build_summary(self, outer: QVBoxLayout) -> None:
        summary = QWidget()
        summary.setObjectName("activitySummary")
        summary.setStyleSheet(f"QWidget#activitySummary {{ background: {tokens.SURFACE}; border-bottom: 1px solid {tokens.HAIRLINE}; }}")
        layout = QHBoxLayout(summary)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(20)

        from datetime import date
        month_name = date.today().strftime("%B %Y")
        period_lbl = QLabel(month_name)
        period_lbl.setStyleSheet(f"font-size: {tokens.T_MD}px; font-weight: 700; color: {tokens.FG}; font-family: 'Playfair Display'; background: transparent;")
        self._net_lbl = QLabel("Net: —")
        self._net_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")

        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)
        self._filter_btns: dict[str, QPushButton] = {}
        for f in ["All", "Income", "Spend", "Charges"]:
            key = f.lower()
            btn = _FilterPill(f, active=(key == self._filter))
            btn.clicked.connect(lambda _c, k=key: self._on_filter(k))
            self._filter_btns[key] = btn
            filter_row.addWidget(btn)

        layout.addWidget(period_lbl)
        layout.addWidget(self._net_lbl)
        layout.addStretch()
        layout.addLayout(filter_row)
        outer.addWidget(summary)

    def _on_filter(self, key: str) -> None:
        self._filter = key
        for k, btn in self._filter_btns.items():
            btn.setChecked(k == key)
        self._render_ledger()

    def set_ledger(self, entries: list[LedgerEntryVM], opening_balance: Decimal) -> None:
        self._all_entries = entries
        if entries:
            net = entries[-1].running_balance - opening_balance
            sign = "+" if net >= 0 else "−"
            color = tokens.GREEN if net >= 0 else tokens.RED
            self._net_lbl.setText(f"Net this month: {sign}₪{abs(net):,.0f}  ·  Opening: ₪{opening_balance:,.0f}  ·  Current: ₪{entries[-1].running_balance:,.0f}")
            self._net_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {color}; font-family: 'DM Mono', Consolas, monospace; font-weight: 500; background: transparent;")
        else:
            self._net_lbl.setText("Net this month: ₪0  ·  No entries yet")
        self._render_ledger()

    def _render_ledger(self) -> None:
        while self._ledger_layout.count():
            item = self._ledger_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = QWidget()
        header.setObjectName("ledgerHeader")
        header.setStyleSheet(f"QWidget#ledgerHeader {{ background: {tokens.PAPER_WARM}; border-bottom: 2px solid {tokens.HAIRLINE}; }}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 8, 24, 8)
        hl.setSpacing(12)
        for text, w in [("Date", 60), ("Description", 1), ("", 28), ("Amount", 100), ("Balance", 100)]:
            lbl = QLabel(text)
            if w == 1:
                lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            else:
                lbl.setFixedWidth(w)
            lbl.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 2px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
            if text in ("Amount", "Balance"):
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            hl.addWidget(lbl)
        self._ledger_layout.addWidget(header)

        filtered = self._all_entries
        if self._filter == "income":
            filtered = [e for e in filtered if e.entry_type == "income"]
        elif self._filter == "spend":
            filtered = [e for e in filtered if e.entry_type == "spend"]
        elif self._filter == "charges":
            filtered = [e for e in filtered if e.entry_type == "charge"]

        if not filtered:
            empty = QLabel("No entries found for this filter.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"font-size: {tokens.T_BASE}px; color: {tokens.MUTED}; padding: 40px; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
            self._ledger_layout.addWidget(empty)
            self._ledger_layout.addStretch()
            return

        for i, entry in enumerate(filtered):
            self._ledger_layout.addWidget(_LedgerRow(entry, even=(i % 2 == 0)))
        self._ledger_layout.addStretch()
