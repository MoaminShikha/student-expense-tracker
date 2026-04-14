from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OnTrackState(str, Enum):
    """Supported monthly on-track states."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    TIGHT_MONTH = "tight_month"


class BalanceState(str, Enum):
    """Supported full-session balance states."""

    NORMAL = "normal"
    CAUTION = "caution"
    CRISIS = "crisis"


@dataclass(frozen=True)
class MonthlyBudgetView:
    """Represents one calculated monthly budget view."""

    monthly_budget: Decimal
    monthly_spent: Decimal
    monthly_left: Decimal
    on_track_state: OnTrackState


@dataclass(frozen=True)
class BalanceSnapshot:
    """Represents one calculated balance snapshot."""

    free_money: Decimal
    monthly_budget: Decimal
    monthly_spent: Decimal
    monthly_left: Decimal
    on_track_state: OnTrackState
    balance_state: BalanceState


class BalanceEngine:
    """Defines deterministic balance calculations for Stage 1."""

    def calculate_free_money(self, opening_balance: Decimal, total_income: Decimal, total_committed: Decimal, total_spent: Decimal) -> Decimal:
        """
        Calculate free money for the full session scope.

        :param opening_balance: Session opening balance.
        :param total_income: Sum of all logged income.
        :param total_committed: Sum of all committed charges.
        :param total_spent: Sum of all spend transactions.
        :return: Calculated free money.
        """
        pass

    def calculate_monthly_budget(self, income_this_month: Decimal, charges_this_month: Decimal, spent_this_month: Decimal, red_threshold: Decimal = Decimal("130")) -> MonthlyBudgetView:
        """
        Calculate monthly budget outputs and ozn-track state.

        :param income_this_month: Sum of income entries in the current month.
        :param charges_this_month: Sum of committed charges due in the current month.
        :param spent_this_month: Sum of spend transactions in the current month.
        :param red_threshold: Red-state threshold percentage.
        :return: Calculated monthly budget view.
        """
        pass

    def classify_on_track_state(self, monthly_budget: Decimal, monthly_spent: Decimal, red_threshold: Decimal = Decimal("130")) -> OnTrackState:
        """
        Classify monthly on-track status from monthly budget usage.

        :param monthly_budget: Current month budget.
        :param monthly_spent: Current month spent amount.
        :param red_threshold: Red-state threshold percentage.
        :return: Classified on-track state.
        """
        pass

    def classify_balance_state(self, free_money: Decimal, caution_threshold: Decimal) -> BalanceState:
        """
        Classify full-session balance state.

        :param free_money: Current free money value.
        :param caution_threshold: Caution-state threshold.
        :return: Classified balance state.
        """
        pass

    def build_snapshot(self, opening_balance: Decimal, total_income: Decimal, total_committed: Decimal, total_spent: Decimal, income_this_month: Decimal, charges_this_month: Decimal, spent_this_month: Decimal, caution_threshold: Decimal, red_threshold: Decimal = Decimal("130")) -> BalanceSnapshot:
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
        pass

