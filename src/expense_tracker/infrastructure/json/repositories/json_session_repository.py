from __future__ import annotations

import json
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import AppSession
from ....infrastructure.logging_config import LoggerFactory

logger: logging.Logger = LoggerFactory.get_logger(__name__)


class JsonSessionRepository:
    """JSON-backed session repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def create(self, session: AppSession) -> None:
        """
        Persist a session to JSON storage.

        :param session: The session to persist.
        :return: None.
        """
        data = {
            "session_id": str(session.session_id),
            "start_date": session.start_date.isoformat(),
            "opening_balance": str(session.opening_balance),
        }
        with open(self._storage_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Session created and persisted: %s", session.session_id)

    def get_active(self) -> AppSession | None:
        """
        Retrieve the current active session from JSON storage.

        :return: Active session if present; otherwise None.
        """
        if not self._storage_path.exists():
            return None
        try:
            with open(self._storage_path, "r") as f:
                data = json.load(f)
            session = AppSession(
                session_id=UUID(data["session_id"]),
                start_date=date.fromisoformat(data["start_date"]),
                opening_balance=Decimal(data["opening_balance"]),
            )
            logger.info("Active session retrieved: %s", session.session_id)
            return session
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error("Failed to deserialize session: %s", e)
            return None
