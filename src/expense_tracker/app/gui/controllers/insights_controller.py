from __future__ import annotations

import calendar
import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense_tracker.application.services import BalanceService, ChargeService, FuzzyChargeService, SessionService, SpendService
    from expense_tracker.app.gui.views.insights_page import InsightsPage

from expense_tracker.app.gui.styles import tokens


class InsightsController:
    """Orchestrates the insights page by computing category breakdowns, daily burn rate, and encumbrance splits from service data."""

    def __init__(
        self,
        view: InsightsPage,
        session_service: SessionService | None = None,
        balance_service: BalanceService | None = None,
        spend_service: SpendService | None = None,
        charge_service: ChargeService | None = None,
        fuzzy_charge_service: FuzzyChargeService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the insights controller.

        :param view: InsightsPage instance to populate with analytics data.
        :param session_service: Service for querying the active budget session.
        :param balance_service: Service for aggregating balance snapshots.
        :param spend_service: Service for fetching spend transactions.
        :param charge_service: Service for fetching committed charges.
        :param fuzzy_charge_service: Service for fetching fuzzy/estimated charges.
        :param logger: Optional logger; defaults to the module logger.
        """
        self._view = view
        self._session_service = session_service
        self._balance_service = balance_service
        self._spend_service = spend_service
        self._charge_service = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._logger = logger or logging.getLogger(__name__)

    def refresh(self) -> None:
        if not self._session_service:
            return
        session = self._session_service.get_active()
        if session is None:
            return

        today = date.today()
        year, month = today.year, today.month
        days_in_month = calendar.monthrange(year, month)[1]
        days_elapsed = today.day

        try:
            # ── Core snapshot from BalanceService ────────────────────────────
            # This gives us monthly_budget, monthly_spent, monthly_left, free_money
            snapshot = None
            if self._balance_service:
                snapshot = self._balance_service.aggregate_and_build_snapshot(session.session_id, Decimal("100"), session.opening_balance)

            budget = snapshot.monthly_budget if snapshot else Decimal("0")
            spent = snapshot.monthly_spent if snapshot else Decimal("0")
            remaining = snapshot.monthly_left if snapshot else Decimal("0")
            free_money = snapshot.free_money if snapshot else Decimal("0")

            # ── Category breakdown ───────────────────────────────────────────
            # Aggregates spend by category for the current month, computes each
            # as a percentage of total monthly budget.
            cat_spend: dict[str, Decimal] = {}
            if self._spend_service:
                for tx in self._spend_service.list_for_month(session.session_id, year, month):
                    key = tx.category.value if tx.category else "other"
                    cat_spend[key] = cat_spend.get(key, Decimal("0")) + tx.amount

            cat_bars: list[dict] = []
            if budget > 0:
                for cat_key, amount in sorted(cat_spend.items(), key=lambda x: -x[1]):
                    pct = float(amount / budget * 100)
                    cat_bars.append({"name": cat_key.capitalize(), "amount_str": f"₪{amount:,.0f}", "pct": min(pct, 100.0), "color": tokens.CATEGORY_COLORS.get(cat_key, tokens.MUTED)})

            total_utilized_pct = float(spent / budget * 100) if budget > 0 else 0.0

            # ── Daily burn rate ──────────────────────────────────────────────
            # Average spend per elapsed day vs budgeted daily allowance.
            # Runway = how many days until remaining budget runs out at current burn.
            daily_burn = spent / Decimal(max(days_elapsed, 1))
            daily_budget = budget / Decimal(max(days_in_month, 1))
            daily_pct = float(daily_burn / daily_budget * 100) if daily_budget > 0 else 0.0
            runway_days = int(remaining / daily_burn) if daily_burn > 0 and remaining > 0 else days_in_month - days_elapsed

            # ── Encumbrance split ────────────────────────────────────────────
            # Committed charges = locked obligations (deduct from free money).
            # Fuzzy charges = estimated liabilities (not yet deducted).
            # Visualized as stacked percentages of total monthly budget:
            # [utilized | encumbered | fuzzy | available]
            committed_total = Decimal("0")
            if self._charge_service:
                committed_total = self._charge_service.get_monthly_committed_total(session.session_id, year, month)

            fuzzy_total = Decimal("0")
            if self._fuzzy_charge_service:
                fuzzy_list = self._fuzzy_charge_service.list_pending_for_month(session.session_id, year, month)
                fuzzy_estimates = [f.estimated_amount for f in fuzzy_list if f.estimated_amount is not None]
                fuzzy_total = sum(fuzzy_estimates, Decimal("0"))

            available = free_money
            encumbered_pct = float(committed_total / budget * 100) if budget > 0 else 0.0
            fuzzy_pct = float(fuzzy_total / budget * 100) if budget > 0 else 0.0
            available_pct = max(0.0, 100.0 - total_utilized_pct - encumbered_pct - fuzzy_pct)

            self._view.set_data(
                cat_bars=cat_bars, cat_total_str=f"₪{spent:,.0f}", cat_budget_str=f"₪{budget:,.0f}",
                total_utilized_pct=total_utilized_pct,
                daily_burn_str=f"₪{daily_burn:,.0f}", daily_budget_str=f"₪{daily_budget:,.0f}",
                daily_pct=daily_pct, runway_days=runway_days, remaining_str=f"₪{remaining:,.0f}",
                committed_str=f"₪{committed_total:,.0f}", fuzzy_str=f"₪{fuzzy_total:,.0f}" if fuzzy_total > 0 else "₪0",
                available_str=f"₪{available:,.0f}", available_pct=available_pct,
                encumbered_pct=encumbered_pct, fuzzy_pct=fuzzy_pct,
            )
        except Exception:
            self._logger.exception("Failed to refresh insights")
