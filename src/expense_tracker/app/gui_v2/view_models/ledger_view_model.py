from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class LedgerEntryVM:
    """Per-row entry for the activity ledger view."""

    date: date
    description: str
    entry_type: str       # "income" | "spend" | "charge"
    amount: Decimal
    amount_str: str
    running_balance: Decimal
    running_balance_str: str
    category_str: str
