from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens
from expense_tracker.app.gui_v2.view_models.ledger_view_model import LedgerEntryVM

_TYPE_COLORS = {
    "income":  tokens.GREEN,
    "spend":   tokens.RED,
    "charge":  tokens.AMBER,
}

_FILTER_KEYS = ["all", "income", "spend", "charge"]


class _LedgerRow(QFrame):
    """Single row in the activity ledger."""

    def __init__(self, entry: LedgerEntryVM) -> None:
        super().__init__()
        self.setObjectName("ledgerRow")
        color = _TYPE_COLORS.get(entry.entry_type, tokens.MUTED)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(12)

        stripe = QFrame()
        stripe.setFixedWidth(4)
        stripe.setSizePolicy(stripe.sizePolicy().horizontalPolicy(), stripe.sizePolicy().verticalPolicy())
        stripe.setMinimumHeight(28)
        stripe.setStyleSheet(f"background: {color}; border-radius: 2px;")

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(1)
        name = QLabel(entry.description)
        name.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.FG};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        meta = QLabel(f"{entry.date.strftime('%d %b')} · {entry.category_str or entry.entry_type.capitalize()}")
        meta.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        body_layout.addWidget(name)
        body_layout.addWidget(meta)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(1)
        sign = "+" if entry.entry_type == "income" else "-"
        amt = QLabel(f"{sign}{entry.amount_str}")
        amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px; font-weight: 700;"
            f"color: {color}; background: transparent;"
        )
        bal = QLabel(entry.running_balance_str)
        bal.setAlignment(Qt.AlignmentFlag.AlignRight)
        bal.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        right_layout.addWidget(amt)
        right_layout.addWidget(bal)

        layout.addWidget(stripe)
        layout.addWidget(body, stretch=1)
        layout.addWidget(right)

        self.setStyleSheet(f"""
            QFrame#ledgerRow {{
                background: transparent; border: none;
                border-bottom: 1px solid {tokens.HAIRLINE};
            }}
        """)


class ActivityPage(QWidget):
    """Activity ledger page with filter pills."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("activityPage")
        self._all_entries: list[LedgerEntryVM] = []
        self._opening: Decimal = Decimal("0")
        self._filter = "all"
        self._filter_btns: dict[str, QPushButton] = {}
        self._rows_container: QWidget | None = None
        self._scroll: QScrollArea | None = None
        self._build()

    def set_ledger(self, entries: Iterable[LedgerEntryVM], opening_balance: Decimal = Decimal("0")) -> None:
        """Populate the ledger with entries and the opening balance."""
        self._all_entries = list(entries)
        self._opening = opening_balance
        self._render()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(tokens.CONTENT_PAD, tokens.CONTENT_PAD, tokens.CONTENT_PAD, 0)
        outer.setSpacing(tokens.SPACE_MD)

        header = QHBoxLayout()
        title = QLabel("Activity")
        title.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_XL}px; font-weight: 700;"
            f"color: {tokens.FG}; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()
        outer.addLayout(header)

        pills_row = QHBoxLayout()
        pills_row.setSpacing(6)
        for key in _FILTER_KEYS:
            btn = QPushButton(key.capitalize())
            btn.setObjectName("filterPill")
            btn.setCheckable(True)
            btn.setChecked(key == "all")
            btn.clicked.connect(lambda _checked, k=key: self._set_filter(k))
            self._filter_btns[key] = btn
            pills_row.addWidget(btn)
        pills_row.addStretch()
        outer.addLayout(pills_row)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)
        self._rows_layout.addStretch()
        self._scroll.setWidget(self._rows_container)
        outer.addWidget(self._scroll, stretch=1)

        self.setStyleSheet(f"""
            QWidget#activityPage {{ background: {tokens.BG}; }}
            QPushButton#filterPill {{
                background: {tokens.SURFACE}; border: 1px solid {tokens.HAIRLINE};
                border-radius: 14px; padding: 4px 12px;
                font-size: {tokens.T_SM}px; font-family: "DM Mono", Consolas, monospace;
                color: {tokens.MUTED_FG};
            }}
            QPushButton#filterPill:checked {{
                background: {tokens.NAVY}; border-color: {tokens.NAVY};
                color: {tokens.GOLD};
            }}
        """)

    def _set_filter(self, key: str) -> None:
        self._filter = key
        for k, btn in self._filter_btns.items():
            btn.setChecked(k == key)
        self._render()

    def _render(self) -> None:
        if self._rows_container is None:
            return
        layout = self._rows_layout
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self._filter == "all":
            visible = self._all_entries
        else:
            visible = [e for e in self._all_entries if e.entry_type == self._filter]
        if not visible:
            placeholder = QLabel("No entries match the selected filter.")
            placeholder.setStyleSheet(
                f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; padding: 24px 0;"
                "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
            )
            layout.insertWidget(0, placeholder)
        else:
            for entry in reversed(visible):
                layout.insertWidget(0, _LedgerRow(entry))
