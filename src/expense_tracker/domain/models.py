from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class AppSession:
    """Represents the active student budgeting session."""

    session_id: UUID
    start_date: date
    opening_balance: Decimal
    period_name: Optional[str] = None


