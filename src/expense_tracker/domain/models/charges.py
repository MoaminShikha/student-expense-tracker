from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID


class ChargeStatus(str, Enum):
    """State of a committed charge."""

    UPCOMING = "upcoming"
    PAID = "paid"


class RecurringFrequency(str, Enum):
    """Supported recurring frequencies for Stage 1."""

    MONTHLY = "monthly"


class FuzzyChargeStatus(str, Enum):
    """State of a fuzzy charge."""

    PENDING = "pending"
    OVERDUE = "overdue"
    RESOLVED = "resolved"
    DISCARDED = "discarded"


class FuzzyEntryDirection(str, Enum):
    """Direction of one fuzzy entry."""

    EXPENSE = "expense"
    INCOME = "income"


@dataclass(frozen=True)
class CommittedCharge:
    """Represents one committed charge for a session."""

    charge_id: UUID
    session_id: UUID
    name: str
    amount: Decimal
    due_date: date
    status: ChargeStatus
    recurring_rule_id: UUID | None = None


@dataclass(frozen=True)
class RecurringRule:
    """Represents a recurring charge generation rule."""

    rule_id: UUID
    session_id: UUID
    name: str
    amount: Decimal
    frequency: RecurringFrequency
    day_of_month: int
    reminder_days: int


@dataclass(frozen=True)
class FuzzyCharge:
    """Represents one uncertain entry that may resolve to expense or income."""

    fuzzy_id: UUID
    session_id: UUID
    name: str
    direction: FuzzyEntryDirection
    status: FuzzyChargeStatus
    expected_date: date | None = None
    estimated_amount: Decimal | None = None
    resolved_amount: Decimal | None = None
    resolved_date: date | None = None
