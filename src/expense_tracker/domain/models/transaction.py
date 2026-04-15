from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID


class TransactionCategory(str, Enum):
    """Supported spend categories."""

    FOOD = "food"
    TRANSPORT = "transport"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


@dataclass(frozen=True)
class Transaction:
    """Represents one spend transaction."""

    transaction_id: UUID
    session_id: UUID
    amount: Decimal
    description: str
    category: TransactionCategory | None
    date: date
