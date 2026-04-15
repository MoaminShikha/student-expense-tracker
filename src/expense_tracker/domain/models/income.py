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


@dataclass(frozen=True)
class IncomeEntry:
    """Represents one income entry for a session."""

    income_id: UUID
    session_id: UUID
    amount: Decimal
    source_tag: IncomeSourceTag
    date: date
