from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.stylesheet import (
    filter_pill_stylesheet,
    ledger_date_label_stylesheet,
    ledger_description_label_stylesheet,
    ledger_badge_stylesheet,
    ledger_amount_label_stylesheet,
    ledger_balance_label_stylesheet,
)
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.ledger_view_model import LedgerEntryVM


class _FilterPill(QPushButton):
    def __init__(self, text: str, active: bool = False) -> None:
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(filter_pill_stylesheet())


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
        date_lbl.setStyleSheet(ledger_date_label_stylesheet())

        desc_lbl = QLabel(entry.description)
        desc_lbl.setStyleSheet(ledger_description_label_stylesheet())
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
        badge.setStyleSheet(ledger_badge_stylesheet(fg, bg_color))

        amt_color = tokens.GREEN if entry.entry_type == "income" else tokens.RED
        amt_lbl = QLabel(entry.amount_str)
        amt_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt_lbl.setFixedWidth(100)
        amt_lbl.setStyleSheet(ledger_amount_label_stylesheet(amt_color))

        bal_lbl = QLabel(entry.running_balance_str)
        bal_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        bal_lbl.setFixedWidth(100)
        bal_lbl.setStyleSheet(ledger_balance_label_stylesheet())

        layout.addWidget(date_lbl)
        layout.addWidget(desc_lbl, stretch=1)
        layout.addWidget(badge)
        layout.addWidget(amt_lbl)
        layout.addWidget(bal_lbl)
        self.setStyleSheet(f"QWidget#ledgerRow {{ background: {bg}; border-bottom: 1px solid {tokens.HAIRLINE}; }}"
                           f"QWidget#ledgerRow:hover {{ background: rgba(199,154,57,0.06); }}")


class ActivityPage(QWidget):
    """
    General ledger view — all transactions for the month with running balance.

    Input comes from ActivityController calling set_ledger().
    Filter pills (All/Income/Spend/Charges) are client-side only.

    Action signals (add_income/spend/charge) are forwarded up to MainWindow
    so DashboardController can open dialogs — same wiring as DashboardPage.
    """

    add_income_requested = pyqtSignal()
    add_spend_requested  = pyqtSignal()
    add_charge_requested = pyqtSignal()

    def __init__(
        self,
        add_income_signal: pyqtSignal | None = None,
        add_spend_signal: pyqtSignal | None = None,
        add_charge_signal: pyqtSignal | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("activityPage")
        self._filter = "all"
        self._all_entries: list[LedgerEntryVM] = []

        if add_income_signal is not None:
            self.add_income_requested = add_income_signal
        if add_spend_signal is not None:
            self.add_spend_requested = add_spend_signal
        if add_charge_signal is not None:
            self.add_charge_requested = add_charge_signal

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

        # Action buttons grouped in a bordered container to visually separate
        # them from the filter pills.
        action_box = QFrame()
        action_box.setObjectName("actionBox")
        action_box.setStyleSheet(f"""
            QFrame#actionBox {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 8px;
                padding: 2px;
            }}
        """)
        action_row = QHBoxLayout(action_box)
        action_row.setContentsMargins(4, 2, 4, 2)
        action_row.setSpacing(2)
        action_row.addWidget(self._action_btn("+ Income", self.add_income_requested))
        action_row.addWidget(self._action_btn("+ Spend", self.add_spend_requested))
        action_row.addWidget(self._action_btn("+ Charge", self.add_charge_requested))
        layout.addWidget(action_box)

        layout.addLayout(filter_row)
        outer.addWidget(summary)

    @staticmethod
    def _action_btn(text: str, signal: pyqtSignal) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_SM}px;
                background: transparent;
                border: none;
                border-radius: 5px;
                padding: 4px 10px;
                color: {tokens.MUTED_FG};
            }}
            QPushButton:hover {{
                background: {tokens.PAPER_WARM};
                color: {tokens.FG};
            }}
        """)
        btn.clicked.connect(signal.emit)
        return btn

    def _on_filter(self, key: str) -> None:
        # Client-side filtering: just re-render with the selected type.
        # No controller call — all data is already in self._all_entries.
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
