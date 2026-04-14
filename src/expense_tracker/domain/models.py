from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID


class IncomeSourceTag(str, Enum):
    """Supported income source tags."""

    SCHOLARSHIP = "scholarship"
    FAMILY = "family"
    WORK = "work"
    OTHER = "other"


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


class TransactionCategory(str, Enum):
    """Supported spend categories."""

    FOOD = "food"
    TRANSPORT = "transport"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    CLOTHING = "clothing"
    HEALTH = "health"
    BILLS = "bills"
    INVESTMENTS = "investments"
    LOANS = "loans"
    SAVINGS = "savings"
    CASH = "cash"
    DEBT = "debt"
    INVESTMENT_RETURNS = "investment_returns"
    OTHER = "other"


@dataclass(frozen=True)
class AppSession:
    """Represents the active student budgeting session."""

    session_id: UUID
    start_date: date
    opening_balance: Decimal


@dataclass(frozen=True)
class IncomeEntry:
    """Represents one income entry for a session."""

    income_id: UUID
    session_id: UUID
    amount: Decimal
    source_tag: IncomeSourceTag
    date: date


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
    """Represents a date-known, amount-unknown charge."""

    fuzzy_id: UUID
    session_id: UUID
    name: str
    due_date: date
    estimated_amount: Decimal | None
    status: FuzzyChargeStatus


@dataclass(frozen=True)
class Transaction:
    """Represents one spend transaction."""

    transaction_id: UUID
    session_id: UUID
    amount: Decimal
    description: str
    category: TransactionCategory | None
    date: date


