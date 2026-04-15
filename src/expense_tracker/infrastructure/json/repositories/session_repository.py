from __future__ import annotations

from ....domain.models import AppSession


class JsonSessionRepository:
    """JSON-backed session repository adapter for Stage 1."""

    def create(self, session: AppSession) -> None:
        """
        Persist a session to JSON storage.

        :param session: The session to persist.
        :return: None.
        """
        ...

    def get_active(self) -> AppSession | None:
        """
        Retrieve the current active session from JSON storage.

        :return: Active session if present; otherwise None.
        """
        ...
