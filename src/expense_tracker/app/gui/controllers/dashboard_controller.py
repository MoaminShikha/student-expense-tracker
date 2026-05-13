from __future__ import annotations

import calendar
import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense_tracker.application.services import (
        BalanceService,
        ChargeService,
        FuzzyChargeService,
        IncomeService,
        SessionService,
        SpendService,
    )
    from expense_tracker.domain.models.balance import BalanceSnapshot
    from expense_tracker.app.gui.views.main_window import MainWindow

from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class DashboardController:
    """
    Thin orchestrator connecting MainWindow signals with application services.

    Owns no domain state. Receives signals from the view, calls services,
    converts results into view models, and calls the view's public setters.
    """

    def __init__(
        self,
        view: MainWindow,
        session_service: SessionService | None = None,
        balance_service: BalanceService | None = None,
        income_service: IncomeService | None = None,
        charge_service: ChargeService | None = None,
        fuzzy_charge_service: FuzzyChargeService | None = None,
        spend_service: SpendService | None = None,
        caution_threshold: Decimal | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._view                 = view
        self._session_service      = session_service
        self._balance_service      = balance_service
        self._income_service       = income_service
        self._charge_service       = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._spend_service        = spend_service
        self._caution_threshold    = Decimal("100") if caution_threshold is None else caution_threshold
        self._logger               = logger or logging.getLogger(__name__)

        self._view.refresh_requested.connect(self._on_refresh_requested)
        self._view.add_income_requested.connect(self._on_add_income_requested)
        self._view.add_spend_requested.connect(self._on_add_spend_requested)
        self._view.add_charge_requested.connect(self._on_add_charge_requested)

    def refresh(self) -> None:
        """Fetch latest data from services and push it into the view."""
        if not self._balance_service or not self._session_service:
            self._logger.debug("Skipping refresh: missing services")
            return

        session = self._session_service.get_active()
        if session is None:
            self._logger.debug("No active session — dashboard refresh skipped")
            return

        try:
            snapshot = self._balance_service.aggregate_and_build_snapshot(
                session.session_id,
                self._caution_threshold,
                session.opening_balance,
            )
            view_model = self._build_view_model(snapshot)
            self._view.set_snapshot(view_model, last_sync=None)
            self._logger.debug("Dashboard refreshed")
        except Exception:
            self._logger.exception("Failed to refresh dashboard")

    # ── Signal handlers ───────────────────────────────────────────────────────

    def _on_refresh_requested(self) -> None:
        self.refresh()

    def _on_add_income_requested(self) -> None:
        self._logger.debug("Add income requested — dialog not yet implemented")

    def _on_add_spend_requested(self) -> None:
        self._logger.debug("Add spend requested — dialog not yet implemented")

    def _on_add_charge_requested(self) -> None:
        self._logger.debug("Add charge requested — dialog not yet implemented")

    # ── Presentation mapping ──────────────────────────────────────────────────

    def _build_view_model(self, snapshot: BalanceSnapshot) -> BalanceViewModel:
        """Convert a domain BalanceSnapshot into a UI-shaped BalanceViewModel."""

        def fmt(amount: Decimal) -> str:
            return f"₪{amount:,.0f}"

        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        today_pct = float(today.day / days_in_month * 100)

        budget = snapshot.monthly_budget
        if budget > Decimal("0"):
            spent_pct = float(
                min(Decimal("100"), snapshot.monthly_spent / budget * Decimal("100"))
            )
        else:
            spent_pct = 0.0

        # committed_pct and fuzzy zones require data not yet in BalanceSnapshot.
        # Will be populated in Phase 7 when snapshot is extended or a second
        # service call retrieves charges-this-month separately.
        committed_pct    = 0.0
        fuzzy_left_pct   = 0.0
        fuzzy_width_pct  = 0.0

        return BalanceViewModel(
            free_money=snapshot.free_money,
            free_money_str=fmt(snapshot.free_money),
            balance_state_value=snapshot.balance_state.value,
            monthly_budget=snapshot.monthly_budget,
            monthly_budget_str=fmt(snapshot.monthly_budget),
            monthly_spent=snapshot.monthly_spent,
            monthly_spent_str=fmt(snapshot.monthly_spent),
            monthly_left=snapshot.monthly_left,
            monthly_left_str=fmt(snapshot.monthly_left),
            on_track_state_value=snapshot.on_track_state.value,
            timeline_spent_pct=spent_pct,
            timeline_committed_pct=committed_pct,
            timeline_fuzzy_left_pct=fuzzy_left_pct,
            timeline_fuzzy_width_pct=fuzzy_width_pct,
            today_pct=today_pct,
        )
