from __future__ import annotations

import logging
from uuid import UUID

from ....domain.models import IncomeEntry
from ..mappers import IncomeMapper
from .base import JsonStore

logger: logging.Logger = logging.getLogger(__name__)


class JsonIncomeRepository(JsonStore[IncomeEntry]):
    """JSON-backed income repository adapter for Stage 1."""

    def __init__(self, storage_path) -> None:
        super().__init__(storage_path, IncomeMapper())

    def add(self, entry: IncomeEntry) -> None:
        """Persist one income entry."""
        self._append(entry)
        logger.info("Income entry added: %s", entry.income_id)

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        """List all income entries for a session."""
        entries = [e for e in self._all() if e.session_id == session_id]
        logger.debug("Retrieved %d income entries for session %s", len(entries), session_id)
        return entries

    def delete(self, income_id: UUID) -> bool:
        """Remove an income entry by ID. Returns True if found and removed."""
        return self._delete_by_id("income_id", str(income_id))

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        """List income entries for one calendar month."""
        entries = [
            e for e in self._all()
            if e.session_id == session_id and e.date.year == year and e.date.month == month
        ]
        logger.info(
            "Retrieved %d income entries for session %s in %d-%02d",
            len(entries), session_id, year, month,
        )
        return entries
