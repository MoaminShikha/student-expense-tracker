from __future__ import annotations

import logging
from uuid import UUID

from ....domain.models import Transaction
from ..mappers import TransactionMapper
from .base import JsonStore

logger: logging.Logger = logging.getLogger(__name__)


class JsonTransactionRepository(JsonStore[Transaction]):
    """JSON-backed spend-transaction repository adapter for Stage 1."""

    def __init__(self, storage_path) -> None:
        super().__init__(storage_path, TransactionMapper())

    def add(self, transaction: Transaction) -> None:
        """Persist one spend transaction."""
        self._append(transaction)
        logger.info("Transaction added: %s", transaction.transaction_id)

    def list_for_session(self, session_id: UUID) -> list[Transaction]:
        """List all spend transactions for one session."""
        transactions = [t for t in self._all() if t.session_id == session_id]
        logger.debug("Retrieved %d transactions for session %s", len(transactions), session_id)
        return transactions

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        """List spend transactions for one calendar month."""
        transactions = [
            t for t in self._all()
            if t.session_id == session_id and t.date.year == year and t.date.month == month
        ]
        logger.info(
            "Retrieved %d transactions for session %s in %d-%02d",
            len(transactions), session_id, year, month,
        )
        return transactions
