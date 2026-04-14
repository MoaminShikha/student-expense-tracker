from __future__ import annotations

from typing import Protocol

from ..domain.models import AppSession


class SessionRepository(Protocol):
    """Defines storage operations for application sessions."""

    def create(self, session: AppSession) -> None:
        """
        Persist a new active session.

        :param session: The session to persist.
        :return: None.
        """
        pass

    def get_active(self) -> AppSession | None:
        """
        Fetch the currently active session.

        :return: Active session if present; otherwise None.
        """
        pass

