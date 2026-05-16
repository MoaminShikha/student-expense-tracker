from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import uuid4

from ...domain.models import IncomeEntry, IncomeSourceTag
from ...ports.repositories import IncomeRepository, SessionRepository
from ...shared.exceptions import ApplicationError, ValidationError


class IncomeService:
    """Coordinates income lifecycle operations for an active session."""

    def __init__(self, session_repository: SessionRepository, income_repository: IncomeRepository, logger: logging.Logger | None = None) -> None:
        """
        Initialize the income service.

        :param session_repository: Repository abstraction for session persistence.
        :param income_repository: Repository abstraction for income persistence.
        :param logger: Optional logger for income operations.
        :return: None.
        """
        self._session_repository = session_repository
        self._income_repository = income_repository
        self._logger = logger or logging.getLogger(__name__)

    def add_income(self, amount: Decimal, source_tag: IncomeSourceTag, entry_date: date) -> IncomeEntry:
        """
        Add one income entry to the active session.

        :param amount: Income amount to add.
        :param source_tag: Income source category.
        :param entry_date: Calendar date for the income entry.
        :return: Persisted income entry.
        """
        if amount <= 0:
            raise ValidationError("Income amount must be greater than zero.")

        if not isinstance(source_tag, IncomeSourceTag):
            raise ValidationError("Income source tag is invalid.")

        if not isinstance(entry_date, date):
            raise ValidationError("Income date is invalid.")

        active_session = self._session_repository.get_active()
        if active_session is None:
            raise ApplicationError("No active session. Start a session before adding income.")

        entry = IncomeEntry(income_id=uuid4(), session_id=active_session.session_id, amount=amount, source_tag=source_tag, date=entry_date)
        self._income_repository.add(entry)
        self._logger.info("Added income entry %s for session %s.", entry.income_id, active_session.session_id)
        return entry

    def list_for_month(self, session_id, year: int, month: int) -> list:
        return self._income_repository.list_for_month(session_id, year, month)
