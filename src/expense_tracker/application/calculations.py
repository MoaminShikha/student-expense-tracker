from __future__ import annotations

from decimal import Decimal

from ..domain.models import BalanceSnapshot, BalanceState, MonthlyBudgetView, OnTrackState


class BalanceEngine:
    """Defines deterministic balance calculations for Stage 1."""

    def calculate_free_money(
        self,
        opening_balance: Decimal,
        total_income: Decimal,
        total_committed: Decimal,
        total_spent: Decimal,
    ) -> Decimal:
        """
        Calculate free money for the full session scope.

        :param opening_balance: Session opening balance.
        :param total_income: Sum of all logged income.
        :param total_committed: Sum of all committed charges.
        :param total_spent: Sum of all spend transactions.
        :return: Calculated free money.
        """
        return opening_balance + total_income - total_committed - total_spent

    def calculate_monthly_budget(
        self,
        income_this_month: Decimal,
        charges_this_month: Decimal,
        spent_this_month: Decimal,
        red_threshold: Decimal = Decimal("130"),
    ) -> MonthlyBudgetView:
        """
        Calculate monthly budget outputs and on-track state.

        :param income_this_month: Sum of income entries in the current month.
        :param charges_this_month: Sum of committed charges due in the current month.
        :param spent_this_month: Sum of spend transactions in the current month.
        :param red_threshold: Red-state threshold percentage.
        :return: Calculated monthly budget view.
        """
        monthly_budget = income_this_month - charges_this_month
        monthly_spent = spent_this_month
        monthly_left = monthly_budget - monthly_spent
        on_track_state = self.classify_on_track_state(monthly_budget, monthly_spent, red_threshold)
        return MonthlyBudgetView(
            monthly_budget=monthly_budget,
            monthly_spent=monthly_spent,
            monthly_left=monthly_left,
            on_track_state=on_track_state,
        )

    def classify_on_track_state(
        self,
        monthly_budget: Decimal,
        monthly_spent: Decimal,
        red_threshold: Decimal = Decimal("130"),
    ) -> OnTrackState:
        """
        Classify monthly on-track status from monthly budget usage.

        :param monthly_budget: Current month budget.
        :param monthly_spent: Current month spent amount.
        :param red_threshold: Red-state threshold percentage.
        :return: Classified on-track state.
        """
        if monthly_budget <= Decimal("0"):
            return OnTrackState.TIGHT_MONTH

        on_track_pct = monthly_spent / monthly_budget * Decimal("100")

        if on_track_pct < Decimal("100"):
            return OnTrackState.GREEN

        if on_track_pct < red_threshold:
            return OnTrackState.YELLOW

        return OnTrackState.RED

    def classify_balance_state(self, free_money: Decimal, caution_threshold: Decimal) -> BalanceState:
        """
        Classify full-session balance state.

        :param free_money: Current free money value.
        :param caution_threshold: Caution-state threshold.
        :return: Classified balance state.
        """
        if free_money > caution_threshold:
            return BalanceState.NORMAL

        if free_money > Decimal("0"):
            return BalanceState.CAUTION

        return BalanceState.CRISIS

    def build_snapshot(
        self,
        opening_balance: Decimal,
        total_income: Decimal,
        total_committed: Decimal,
        total_spent: Decimal,
        income_this_month: Decimal,
        charges_this_month: Decimal,
        spent_this_month: Decimal,
        caution_threshold: Decimal,
        red_threshold: Decimal = Decimal("130"),
    ) -> BalanceSnapshot:
        """
        Build the complete Stage 1 balance snapshot.

        :param opening_balance: Session opening balance.
        :param total_income: Sum of all logged income.
        :param total_committed: Sum of all committed charges.
        :param total_spent: Sum of all spend transactions.
        :param income_this_month: Sum of income entries in current month.
        :param charges_this_month: Sum of committed charges due in current month.
        :param spent_this_month: Sum of spend transactions in current month.
        :param caution_threshold: Caution-state threshold.
        :param red_threshold: Red-state threshold percentage.
        :return: Calculated balance snapshot.
        """
        free_money = self.calculate_free_money(opening_balance, total_income, total_committed, total_spent)
        monthly_view = self.calculate_monthly_budget(income_this_month, charges_this_month, spent_this_month, red_threshold)
        balance_state = self.classify_balance_state(free_money, caution_threshold)
        return BalanceSnapshot(
            free_money=free_money,
            monthly_budget=monthly_view.monthly_budget,
            monthly_spent=monthly_view.monthly_spent,
            monthly_left=monthly_view.monthly_left,
            on_track_state=monthly_view.on_track_state,
            balance_state=balance_state,
        )
