from __future__ import annotations

from collections.abc import Iterable
import calendar
from datetime import datetime
from typing import TYPE_CHECKING, Any

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

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.footer_strip import FooterStrip
from expense_tracker.app.gui.widgets.hero_card import HeroCard
from expense_tracker.app.gui.widgets.panels import CategoryPanel, ChargeRowVM, RecentPanel, TxRowVM, UpcomingPanel, CategoryRowVM
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget
from expense_tracker.app.gui.widgets.stat_column import StatColumn

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class DashboardPage(QWidget):
    """
    Full dashboard page: hero card + stat column + three bottom panels + footer.
    Encapsulates all dashboard-specific state so MainWindow can switch pages cleanly.
    """

    def __init__(
        self,
        add_income_signal,
        add_spend_signal,
        add_charge_signal,
        mark_charge_paid_signal=None,
    ) -> None:
        super().__init__()
        self.setObjectName("dashboardPage")

        # Panels receive signals from MainWindow (not the raw signal).
        # Their "Add" buttons emit these signals → MainWindow re-fires them
        # → DashboardController opens the corresponding dialog.
        self._stat_column = StatColumn()
        self._hero = HeroCard()
        self._cat_panel = CategoryPanel(add_income_signal)
        self._upcoming_panel = UpcomingPanel(add_charge_signal)
        self._recent_panel = RecentPanel(add_spend_signal)
        self._footer = FooterStrip()

        # A charge row's ✓ button emits charge_paid(id); forward it up to
        # MainWindow so the controller can mark the charge paid.
        if mark_charge_paid_signal is not None:
            self._upcoming_panel.charge_paid.connect(mark_charge_paid_signal)

        self._build_layout()

    # ── PUBLIC SETTERS ─────────────────────────────────────────────────────────

    def set_snapshot(
        self,
        snapshot: BalanceViewModel,
        last_sync: datetime | None = None,
        animate: bool = True,
    ) -> None:
        self._hero.set_money_value(snapshot.free_money, animate=animate)
        self._hero.set_state(snapshot.balance_state_value)
        self._hero.set_period_for_today()
        self._hero.set_legend(
            snapshot.monthly_spent_str,
            snapshot.monthly_committed_str,
            snapshot.monthly_fuzzy_estimated_str,
            snapshot.monthly_budget_str,
        )
        self._hero.set_daily_allowance(snapshot.monthly_left_str, "")
        self._hero.timeline.set_percentages(
            snapshot.timeline_spent_pct,
            snapshot.timeline_committed_pct,
            snapshot.timeline_fuzzy_left_pct,
            snapshot.timeline_fuzzy_width_pct,
            snapshot.today_pct,
        )
        self._hero.timeline.set_committed_due_pcts(snapshot.committed_due_pcts)
        self._hero.timeline.set_spend_day_pcts(snapshot.spend_day_pcts)
        today = datetime.now().date()
        last_day = calendar.monthrange(today.year, today.month)[1]
        month_abbr = calendar.month_abbr[today.month]
        self._hero.timeline.set_endpoints(f"1 {month_abbr}", f"{last_day} {month_abbr}")

        self._stat_column.set_snapshot(snapshot, animate=animate)

    def set_upcoming(self, rows: Iterable[ChargeRowVM]) -> None:
        self._upcoming_panel.set_upcoming(list(rows))

    def set_recent(self, rows: Iterable[TxRowVM]) -> None:
        self._recent_panel.set_recent(list(rows))

    def set_categories(self, rows: Iterable[CategoryRowVM]) -> None:
        self._cat_panel.set_categories(list(rows))

    def set_timeline_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        self._hero.timeline.set_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self._hero.set_alert(body_html, amount_str, visible)

    # ── LAYOUT ─────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._build_content())
        outer.addWidget(scroll, stretch=1)

        scroll.setStyleSheet(f"""
            QScrollArea {{ background: {tokens.BG}; border: none; }}
        """)

    def _build_content(self) -> QWidget:
        w = PaperWidget()
        w.setObjectName("dashboardContent")

        layout = QVBoxLayout(w)
        layout.setContentsMargins(tokens.CONTENT_PAD, 18, tokens.CONTENT_PAD, 18)
        layout.setSpacing(14)

        # Hero row
        hero_container = QWidget()
        hero_row = QHBoxLayout(hero_container)
        hero_row.setContentsMargins(0, 0, 0, 0)
        hero_row.setSpacing(12)
        hero_row.addWidget(self._hero, stretch=1)
        hero_row.addWidget(self._stat_column)
        layout.addWidget(hero_container)

        # Panels row
        panels_w = QWidget()
        panels_l = QHBoxLayout(panels_w)
        panels_l.setContentsMargins(0, 0, 0, 0)
        panels_l.setSpacing(10)
        panels_l.addWidget(self._cat_panel, stretch=1)
        panels_l.addWidget(self._upcoming_panel, stretch=1)
        panels_l.addWidget(self._recent_panel, stretch=1)
        layout.addWidget(panels_w)

        # Footer
        layout.addWidget(self._footer)

        w.setStyleSheet(f"""
            QWidget#dashboardContent {{
                background: transparent;
                font-family: "DM Mono", Consolas, monospace;
            }}
            QFrame#card {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: {tokens.CARD_RADIUS}px;
            }}
            QLabel#cardMicro {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 2px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#cardSubtitle {{
                font-size: {tokens.T_SM}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#moneyValue {{
                font-size: 54px;
                font-weight: 900;
                font-family: "Playfair Display";
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#panelTitle {{
                font-size: {tokens.T_BASE}px;
                font-weight: 500;
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#emptyState {{
                font-size: {tokens.T_SM}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#footerText {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 1px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QPushButton#actionBtn {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_SM}px;
                font-weight: 500;
                background: {tokens.NAVY};
                color: {tokens.GOLD};
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                letter-spacing: 1px;
            }}
            QPushButton#actionBtn:hover {{
                background: {tokens.FG};
            }}
        """)
        return w
