from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import uuid4

from ...domain.models import AppSession
from ...ports.repositories import SessionRepository
from ...shared.exceptions import ApplicationError, ValidationError


class SessionService:
    """Coordinates session-related application operations."""

    def __init__(self, session_repository: SessionRepository, logger: logging.Logger | None = None) -> None:
        """
        Initialize the session service.

        :param session_repository: Repository abstraction for session persistence.
        :param logger: Optional logger for session operations.
        :return: None.
        """
        self._session_repository = session_repository
        self._logger = logger or logging.getLogger(__name__)

    def init_session(self, opening_balance: Decimal) -> None:
        """
        Start a new budgeting session.

        :param opening_balance: Opening balance for the session.
        :return: None.
        """
        # Guard independently — services must not rely on callers having validated.
        if opening_balance < 0:
            raise ValidationError("Opening balance cannot be negative.")

        if self._session_repository.get_active() is not None:
            raise ApplicationError("An active session already exists.")

        session = AppSession(session_id=uuid4(), start_date=date.today(), opening_balance=opening_balance)
        self._session_repository.create(session)
        self._logger.info("Created session with opening balance %s.", opening_balance)
