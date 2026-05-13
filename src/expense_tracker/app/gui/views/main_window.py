from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class MainWindow(QMainWindow):
    """
    Presentation-only main dashboard window.

    Displays balance snapshot, monthly stats, and upcoming/recent transactions.
    Emits signals for user actions — no business logic, no repository access.
    """

    # ── SIGNALS ───────────────────────────────────────────────────────────────
    refresh_requested    = pyqtSignal()
    add_income_requested = pyqtSignal()
    add_spend_requested  = pyqtSignal()
    add_charge_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mizān")
        self.setMinimumSize(1000, 680)

        # Display widgets — created before layout so layout methods can reference them
        self._free_money_value   = QLabel("₪0")
        self._state_value        = QLabel("normal")
        self._monthly_budget_value = QLabel("₪0")
        self._monthly_spent_value  = QLabel("₪0")
        self._monthly_left_value   = QLabel("₪0")
        self._last_sync_label    = QLabel("Never synced")
        self._timeline_widget    = TimelineWidget()

        self.setCentralWidget(self._build_central_widget())

    # ── PUBLIC SETTERS ─────────────────────────────────────────────────────────

    def set_snapshot(
        self,
        snapshot: BalanceViewModel,
        last_sync: datetime | None = None,
        animate: bool = True,
    ) -> None:
        """Push a balance snapshot into the view."""
        self._free_money_value.setText(snapshot.free_money_str)
        self._state_value.setText(snapshot.balance_state_value)
        self._monthly_budget_value.setText(snapshot.monthly_budget_str)
        self._monthly_spent_value.setText(snapshot.monthly_spent_str)
        self._monthly_left_value.setText(snapshot.monthly_left_str)

        if last_sync:
            self._last_sync_label.setText(f"Last synced: {last_sync.strftime('%Y-%m-%d %H:%M')}")

        self._timeline_widget.set_percentages(
            snapshot.timeline_spent_pct,
            snapshot.timeline_committed_pct,
            snapshot.timeline_fuzzy_left_pct,
            snapshot.timeline_fuzzy_width_pct,
            snapshot.today_pct,
        )

    def set_upcoming(self, charges: Iterable[Any]) -> None:
        """Update upcoming charges list (placeholder — implemented in Phase 5)."""
        pass

    def set_recent(self, transactions: Iterable[Any]) -> None:
        """Update recent transactions list (placeholder — implemented in Phase 5)."""
        pass

    def set_categories(self, categories: Iterable[Any]) -> None:
        """Update category breakdown (placeholder — implemented in Phase 5)."""
        pass

    def update_timeline(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Update timeline directly without a full snapshot push."""
        self._timeline_widget.set_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    def set_last_sync(self, dt: datetime | None) -> None:
        """Update the last-sync label."""
        self._last_sync_label.setText(
            f"Last synced: {dt.strftime('%Y-%m-%d %H:%M')}" if dt else "Never synced"
        )

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _build_central_widget(self) -> QWidget:
        root = QWidget()
        root.setObjectName("dashboardRoot")

        layout = QVBoxLayout(root)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_money_panel())
        layout.addWidget(self._timeline_widget)
        layout.addLayout(self._build_stat_row())
        layout.addLayout(self._build_detail_grid(), stretch=1)
        layout.addLayout(self._build_action_row())

        root.setStyleSheet(f"""
            QWidget#dashboardRoot {{
                background: {tokens.BG};
                color: {tokens.FG};
                font-family: "Segoe UI", "DM Mono", Consolas, monospace;
            }}
            QLabel#eyebrow {{
                color: {tokens.MUTED};
                font-size: 10px;
                letter-spacing: 1px;
            }}
            QLabel#dashTitle {{
                font-size: 28px;
                font-weight: 700;
                color: {tokens.FG};
            }}
            QFrame#card {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 8px;
            }}
            QLabel#cardLabel {{
                color: {tokens.MUTED_FG};
                font-size: 11px;
            }}
            QLabel#panelTitle {{
                font-size: 13px;
                font-weight: 600;
                color: {tokens.FG};
            }}
            QLabel#moneyValue {{
                font-size: 54px;
                font-weight: 700;
                color: {tokens.FG};
            }}
            QLabel#stateValue {{
                background: {tokens.GREEN_BG};
                color: {tokens.GREEN};
                border: 1px solid #b9decf;
                border-radius: 4px;
                padding: 4px 10px;
            }}
            QLabel#statValue {{
                font-size: 24px;
                font-weight: 700;
                color: {tokens.FG};
            }}
            QPushButton {{
                background: {tokens.NAVY};
                color: {tokens.GOLD};
                border: none;
                border-radius: 6px;
                padding: 9px 14px;
            }}
            QPushButton:hover {{
                background: {tokens.FG};
            }}
        """)
        return root

    def _build_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        title_stack = QVBoxLayout()
        eyebrow = QLabel("Stage 2 / PyQt6")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Mizān Dashboard")
        title.setObjectName("dashTitle")
        title_stack.addWidget(eyebrow)
        title_stack.addWidget(title)

        layout.addLayout(title_stack)
        layout.addWidget(self._last_sync_label)
        layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

        return layout

    def _build_money_panel(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        lbl = QLabel("Free Money")
        lbl.setObjectName("cardLabel")
        self._state_value.setObjectName("stateValue")
        top_row.addWidget(lbl)
        top_row.addStretch()
        top_row.addWidget(self._state_value)

        self._free_money_value.setObjectName("moneyValue")
        subtitle = QLabel("after spend and committed charges")
        subtitle.setObjectName("cardLabel")

        layout.addLayout(top_row)
        layout.addWidget(self._free_money_value)
        layout.addWidget(subtitle)
        return card

    def _build_stat_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(self._build_stat_card("Monthly Budget", self._monthly_budget_value))
        layout.addWidget(self._build_stat_card("Monthly Spent",  self._monthly_spent_value))
        layout.addWidget(self._build_stat_card("Monthly Left",   self._monthly_left_value))
        return layout

    def _build_detail_grid(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setSpacing(14)
        layout.addWidget(
            self._build_placeholder_panel("Upcoming Charges", "No upcoming charges loaded yet."),
            0, 0,
        )
        layout.addWidget(
            self._build_placeholder_panel("Recent Transactions", "No recent transactions loaded yet."),
            0, 1,
        )
        layout.addWidget(
            self._build_placeholder_panel("By Category", "Category breakdown will appear here."),
            1, 0, 1, 2,
        )
        return layout

    def _build_action_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addStretch()

        for label, signal in [
            ("Add Income", self.add_income_requested),
            ("Add Spend",  self.add_spend_requested),
            ("Add Charge", self.add_charge_requested),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)

        return layout

    def _build_stat_card(self, label_text: str, value_label: QLabel) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setObjectName("cardLabel")
        value_label.setObjectName("statValue")

        layout.addWidget(lbl)
        layout.addWidget(value_label)
        layout.addStretch()
        return card

    def _build_placeholder_panel(self, title_text: str, empty_text: str) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("panelTitle")   # fixed: was "title", caused 28px font collision

        empty = QLabel(empty_text)
        empty.setObjectName("cardLabel")
        empty.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(title)
        layout.addWidget(empty)
        layout.addStretch()
        return card

    @staticmethod
    def _card() -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        return card
