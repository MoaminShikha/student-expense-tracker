from __future__ import annotations

import json
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import Transaction, TransactionCategory

logger: logging.Logger = logging.getLogger(__name__)


class JsonTransactionRepository:
    """JSON-backed spend-transaction repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, transaction: Transaction) -> None:
        """
        Persist one spend transaction.

        :param transaction: Transaction to persist.
        :return: None.
        """
        data = self._load_all()
        data.append({
            "transaction_id": str(transaction.transaction_id),
            "session_id": str(transaction.session_id),
            "amount": str(transaction.amount),
            "description": transaction.description,
            "category": transaction.category.value if transaction.category else None,
            "date": transaction.date.isoformat(),
        })
        self._save_all(data)
        logger.info("Transaction added: %s", transaction.transaction_id)

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        """
        List spend transactions for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Transactions for the month.
        """
        data = self._load_all()
        transactions = []
        for record in data:
            if record["session_id"] == str(session_id):
                transaction_date = date.fromisoformat(record["date"])
                if transaction_date.year == year and transaction_date.month == month:
                    transactions.append(self._deserialize(record))
        logger.info(
            "Retrieved %d transactions for session %s in %d-%02d",
            len(transactions), session_id, year, month,
        )
        return transactions

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _deserialize(self, record: dict) -> Transaction:
        """Reconstruct a Transaction from a JSON record."""
        return Transaction(
            transaction_id=UUID(record["transaction_id"]),
            session_id=UUID(record["session_id"]),
            amount=Decimal(record["amount"]),
            description=record["description"],
            category=TransactionCategory(record["category"]) if record["category"] else None,
            date=date.fromisoformat(record["date"]),
        )

    def _load_all(self) -> list[dict]:
        """Load all records from storage."""
        if not self._storage_path.exists():
            return []
        try:
            with open(self._storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all(self, data: list[dict]) -> None:
        """Save all records to storage."""
        with open(self._storage_path, "w") as f:
            json.dump(data, f, indent=2)
