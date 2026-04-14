from __future__ import annotations

from decimal import Decimal

from ..ports.repositories import SessionRepository


class SessionService:
    """Coordinates session-related application operations."""

    def __init__(self, session_repository: SessionRepository) -> None:
        """
        Initialize the session service.

        :param session_repository: Repository abstraction for session persistence.
        :return: None.
        """
        pass

    def init_session(self, opening_balance: Decimal, period_name: str | None = None) -> None:
        """
        Start a new budgeting session.

        :param opening_balance: Opening balance for the session.
        :param period_name: Optional label for the session.
        :return: None.
        """
        pass
