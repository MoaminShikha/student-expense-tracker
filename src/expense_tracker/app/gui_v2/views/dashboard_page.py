from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens
from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel
from expense_tracker.app.gui_v2.widgets.alert_banner import AlertBanner
from expense_tracker.app.gui_v2.widgets.hero_card import HeroCard
from expense_tracker.app.gui_v2.widgets.panels import (
    CategoryPanel,
    CategoryRowVM,
    ChargeRowVM,
    RecentPanel,
    TxRowVM,
    UpcomingPanel,
)
from expense_tracker.app.gui_v2.widgets.stat_column import StatColumn


class DashboardPage(QWidget):
    """
    Dashboard page widget.

    Lays out HeroCard (left + bottom) and StatColumn (right) plus the three
    lower panels (Category, Upcoming, Recent).  All signal forwarding is
    intentionally absent — callers drive the view directly.
    """

    # Signals forwarded to the controller
    add_income_requested  = pyqtSignal()
    add_spend_requested   = pyqtSignal()
    add_charge_requested  = pyqtSignal()
    refresh_requested     = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dashboardPage")

        self._hero       = HeroCard()
        self._stat_col   = StatColumn()
        self._cat_panel  = CategoryPanel(self.add_spend_requested)
        self._up_panel   = UpcomingPanel(self.add_charge_requested)
        self._rec_panel  = RecentPanel(self.add_spend_requested)
        self._alert      = AlertBanner()

        self._build_layout()

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    def set_snapshot(self, vm: BalanceViewModel) -> None:
        """Push a BalanceViewModel into both the HeroCard and StatColumn."""
        self._hero.set_state(vm.balance_state_value)
        self._hero.set_money_value(vm.free_money_str)
        self._hero.set_period_for_today()
        self._hero.set_legend(
            vm.monthly_spent_str,
            vm.monthly_committed_str,
            vm.monthly_fuzzy_estimated_str,
            vm.monthly_budget_str,
        )
        self._hero.timeline.set_percentages(
            vm.timeline_spent_pct,
            vm.timeline_committed_pct,
            vm.timeline_fuzzy_left_pct,
            vm.timeline_fuzzy_width_pct,
            vm.today_pct,
        )
        self._stat_col.set_snapshot(vm)

    def set_upcoming(self, rows: Iterable[ChargeRowVM]) -> None:
        """Forward upcoming charge rows to the UpcomingPanel."""
        self._up_panel.set_upcoming(list(rows))

    def set_recent(self, rows: Iterable[TxRowVM]) -> None:
        """Forward recent transaction rows to the RecentPanel."""
        self._rec_panel.set_recent(list(rows))

    def set_categories(self, rows: Iterable[CategoryRowVM]) -> None:
        """Forward category breakdown rows to the CategoryPanel."""
        self._cat_panel.set_categories(list(rows))

    def set_timeline_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Delegate timeline segment percentages to the HeroCard's TimelineWidget."""
        self._hero.timeline.set_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        """Forward alert state to the AlertBanner and HeroCard heads-up strip."""
        self._alert.set_visible(visible)
        if visible and body_html:
            self._alert.set_message(body_html)
        self._hero.set_alert(body_html, amount_str, visible)

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setObjectName("dashboardInner")
        page_layout = QVBoxLayout(inner)
        page_layout.setContentsMargins(
            tokens.CONTENT_PAD, tokens.CONTENT_PAD,
            tokens.CONTENT_PAD, tokens.CONTENT_PAD,
        )
        page_layout.setSpacing(tokens.SPACE_MD)

        page_layout.addWidget(self._alert)

        top_row = QHBoxLayout()
        top_row.setSpacing(tokens.SPACE_MD)
        top_row.addWidget(self._hero, stretch=1)
        top_row.addWidget(self._stat_col)
        page_layout.addLayout(top_row)

        panels_row = QHBoxLayout()
        panels_row.setSpacing(tokens.SPACE_MD)
        panels_row.addWidget(self._cat_panel, stretch=2)
        panels_row.addWidget(self._up_panel, stretch=2)
        panels_row.addWidget(self._rec_panel, stretch=2)
        page_layout.addLayout(panels_row)
        page_layout.addStretch()

        scroll.setWidget(inner)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        self.setStyleSheet(f"QWidget#dashboardPage, QWidget#dashboardInner {{ background: {tokens.BG}; }}")
