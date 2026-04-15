from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OnTrackState(str, Enum):
    """Monthly on-track classification relative to the monthly budget."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    TIGHT_MONTH = "tight_month"


class BalanceState(str, Enum):
    """Full-session balance classification relative to the caution threshold."""

    NORMAL = "normal"
    CAUTION = "caution"
    CRISIS = "crisis"


@dataclass(frozen=True)
class MonthlyBudgetView:
    """Calculated monthly budget view for the current calendar month."""

    monthly_budget: Decimal
    monthly_spent: Decimal
    monthly_left: Decimal
    on_track_state: OnTrackState


@dataclass(frozen=True)
class BalanceSnapshot:
    """Full balance snapshot combining session-scope and monthly-scope outputs."""

    free_money: Decimal
    monthly_budget: Decimal
    monthly_spent: Decimal
    monthly_left: Decimal
    on_track_state: OnTrackState
    balance_state: BalanceState
