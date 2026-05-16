from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class BalanceViewModel:
    """
    UI-shaped display representation of a balance snapshot.

    Contains pre-formatted strings and timeline percentages for direct consumption by views.
    Built by controller from domain BalanceSnapshot; never manipulates domain state.
    """

    free_money: Decimal
    free_money_str: str
    balance_state_value: str  # "normal" | "caution" | "crisis"
    monthly_budget: Decimal
    monthly_budget_str: str
    monthly_spent: Decimal
    monthly_spent_str: str
    monthly_committed: Decimal
    monthly_committed_str: str
    monthly_fuzzy_estimated: Decimal
    monthly_fuzzy_estimated_str: str
    monthly_left: Decimal
    monthly_left_str: str
    on_track_state_value: str  # "green" | "yellow" | "red" | "tight_month"
    timeline_spent_pct: float
    timeline_committed_pct: float
    timeline_fuzzy_left_pct: float
    timeline_fuzzy_width_pct: float
    today_pct: float
    committed_due_pcts: list[float] = field(default_factory=list)
    spend_day_pcts: list[float] = field(default_factory=list)

