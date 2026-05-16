from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import uuid4

from ...domain.models import Transaction, TransactionCategory
from ...ports.repositories import SessionRepository, TransactionRepository
from ...shared.exceptions import ApplicationError, ValidationError


class SpendService:
    """Coordinates spend transaction lifecycle operations for an active session."""

    def __init__(self, session_repository: SessionRepository, transaction_repository: TransactionRepository,
                 logger: logging.Logger | None = None) -> None:
        """
        Initialize the spend service.

        :param session_repository: Repository abstraction for session persistence.
        :param transaction_repository: Repository abstraction for spend persistence.
        :param logger: Optional logger for spend operations.
        :return: None.
        """
        self._session_repository = session_repository
        self._transaction_repository = transaction_repository
        self._logger = logger or logging.getLogger(__name__)

    def add_transaction(self, amount: Decimal, description: str, category: TransactionCategory | None,
                        spent_on: date) -> Transaction:
        """
        Add one spend transaction to the active session.

        :param amount: Positive spend amount.
        :param description: Human-readable spend description.
        :param category: Optional spend category.
        :param spent_on: Calendar date of the transaction.
        :return: Persisted transaction.
        """
        if amount <= 0:
            raise ValidationError("Transaction amount must be greater than zero.")

        normalized_description = description.strip()
        if not normalized_description:
            raise ValidationError("Transaction description cannot be empty.")

        if category is not None and not isinstance(category, TransactionCategory):
            raise ValidationError("Transaction category is invalid.")

        if not isinstance(spent_on, date):
            raise ValidationError("Transaction date is invalid.")

        active_session = self._session_repository.get_active()
        if active_session is None:
            raise ApplicationError("No active session. Start a session before adding transactions.")

        transaction = Transaction(transaction_id=uuid4(), session_id=active_session.session_id, amount=amount,
                                  description=normalized_description, category=category, date=spent_on)
        self._transaction_repository.add(transaction)
        self._logger.info("Added transaction %s for session %s.", transaction.transaction_id, active_session.session_id)
        return transaction

    def list_for_month(self, session_id, year: int, month: int) -> list:
        return self._transaction_repository.list_for_month(session_id, year, month)
