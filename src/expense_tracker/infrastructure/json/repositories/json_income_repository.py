from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import IncomeEntry, IncomeSourceTag
from ..safe_file_io import load_json_safely, save_json_safely

logger: logging.Logger = logging.getLogger(__name__)


class JsonIncomeRepository:
    """JSON-backed income repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, entry: IncomeEntry) -> None:
        """
        Persist one income entry.

        :param entry: Income entry to persist.
        :return: None.
        """
        data = self._load_all()
        data.append({
            "income_id": str(entry.income_id),
            "session_id": str(entry.session_id),
            "amount": str(entry.amount),
            "source_tag": entry.source_tag.value,
            "date": entry.date.isoformat(),
        })
        self._save_all(data)
        logger.info("Income entry added: %s", entry.income_id)

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        """
        List all income entries for a session.

        :param session_id: Session identifier.
        :return: Income entries for the session.
        """
        data = self._load_all()
        entries = []
        for record in data:
            if record["session_id"] == str(session_id):
                entries.append(self._deserialize(record))
        logger.info("Retrieved %d income entries for session %s", len(entries), session_id)
        return entries

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        """
        List income entries for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Income entries for the month.
        """
        data = self._load_all()
        entries = []
        for record in data:
            if record["session_id"] == str(session_id):
                entry_date = date.fromisoformat(record["date"])
                if entry_date.year == year and entry_date.month == month:
                    entries.append(self._deserialize(record))
        logger.info(
            "Retrieved %d income entries for session %s in %d-%02d",
            len(entries), session_id, year, month,
        )
        return entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _deserialize(self, record: dict) -> IncomeEntry:
        """Reconstruct an IncomeEntry from a JSON record."""
        return IncomeEntry(
            income_id=UUID(record["income_id"]),
            session_id=UUID(record["session_id"]),
            amount=Decimal(record["amount"]),
            source_tag=IncomeSourceTag(record["source_tag"]),
            date=date.fromisoformat(record["date"]),
        )

    def _load_all(self) -> list[dict]:
        """Load all records from storage with corruption recovery."""
        return load_json_safely(self._storage_path)

    def _save_all(self, data: list[dict]) -> None:
        """Save all records to storage with atomic write and backup."""
        save_json_safely(self._storage_path, data)
