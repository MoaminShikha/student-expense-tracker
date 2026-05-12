from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import date
import calendar

if TYPE_CHECKING:
    # TYPE_CHECKING imports only for type hints — keep runtime deps small
    from expense_tracker.application.services import (
        BalanceService,
        ChargeService,
        SessionService,
        SpendService,
    )
    from expense_tracker.app.gui.views.main_window import MainWindow

from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class DashboardController:
    """Thin orchestrator connecting MainWindow signals with application services.

    Presentation-only controller: it coordinates view signals and delegates
    all business logic to application-layer services. It formats domain
    snapshots into UI view models and calls the view's public setters.
    """

    def __init__(
        self,
        view: "MainWindow",
        session_service: "SessionService" | None = None,
        balance_service: "BalanceService" | None = None,
        charge_service: "ChargeService" | None = None,
        spend_service: "SpendService" | None = None,
        logger: logging.Logger | None = None,
        caution_threshold: Decimal | None = None,
    ) -> None:
        """Initialize the dashboard controller.

        :param view: Presentation layer window (presentation-only).
        :param session_service: Application session service.
        :param balance_service: Application balance service.
        :param caution_threshold: Presentation threshold for caution state.
        """
        self._view = view
        self._session_service = session_service
        self._balance_service = balance_service
        self._charge_service = charge_service
        self._spend_service = spend_service
        self._logger = logger or logging.getLogger(__name__)

        # Connect view signals to controller handlers
        self._view.refresh_requested.connect(self._on_refresh_requested)
        self._view.add_income_requested.connect(self._on_add_income_requested)
        self._view.add_spend_requested.connect(self._on_add_spend_requested)
        self._view.add_charge_requested.connect(self._on_add_charge_requested)

        # Presentation-level threshold (default matches CLI default)
        self._caution_threshold: Decimal = caution_threshold or Decimal("100")

    def refresh(self) -> None:
        """Refresh dashboard by fetching latest data from services and updating the view.

        This method orchestrates application services then maps the resulting
        domain snapshot into a view model for presentation. No domain state is
        modified here.
        """
        if not self._balance_service or not self._session_service:
            self._logger.debug("Skipping refresh: missing services")
            return

        session = self._session_service.get_active()
        if session is None:
            self._logger.debug("No active session — dashboard refresh skipped")
            return

        try:
            snapshot = self._balance_service.aggregate_and_build_snapshot(
                session.session_id, self._caution_threshold, session.opening_balance
            )

            view_model = self._snapshot_to_view_model(snapshot)
            # last_sync is not implemented in Stage 1 — pass None
            self._view.set_snapshot(view_model, last_sync=None)
            self._logger.debug("Dashboard refresh completed and view updated")
        except Exception:
            self._logger.exception("Failed to refresh dashboard")

    def _on_refresh_requested(self) -> None:
        """Handle refresh signal from view."""
        self._logger.debug("Refresh requested from view")
        self.refresh()

    def _on_add_income_requested(self) -> None:
        """Handle add-income signal from view (scaffold).

        For Stage 1 this method logs and triggers a refresh; dialog wiring is
        implemented in later stages.
        """
        self._logger.debug("Add income requested from view")

    def _on_add_spend_requested(self) -> None:
        """Handle add-spend signal from view (scaffold)."""
        self._logger.debug("Add spend requested from view")

    def _on_add_charge_requested(self) -> None:
        """Handle add-charge signal from view (scaffold)."""
        self._logger.debug("Add charge requested from view")

    # /* Presentation mapping helpers (pure formatting) */
    def _snapshot_to_view_model(self, snapshot) -> BalanceViewModel:
        """Convert domain BalanceSnapshot into UI-shaped BalanceViewModel.

        This method performs only formatting and percentage calculations used by
        the view. It does not modify domain state or apply business rules.
        """
        # Currency formatter: two decimals with shekel symbol
        def fmt(amount: Decimal) -> str:
            return f"₪{amount:.2f}"

        # timeline calculations
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        today_pct = float(today.day / days_in_month * 100)

        monthly_budget = snapshot.monthly_budget
        if monthly_budget and monthly_budget > Decimal("0"):
            spent_pct = float(min(Decimal("100"), (snapshot.monthly_spent / monthly_budget) * Decimal("100")))
        else:
            spent_pct = 0.0

        committed_pct = 0.0
        fuzzy_left_pct = 0.0
        fuzzy_width_pct = 0.0

        vm = BalanceViewModel(
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
        return vm

