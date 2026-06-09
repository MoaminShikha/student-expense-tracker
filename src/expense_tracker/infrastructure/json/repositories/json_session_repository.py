from __future__ import annotations

import json
import logging
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import AppSession
from ..safe_file_io import load_json_safely

logger: logging.Logger = logging.getLogger(__name__)


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
        Persist a session to JSON storage using atomic write.

        :param session: The session to persist.
        :return: None.
        """
        data = {
            "session_id": str(session.session_id),
            "start_date": session.start_date.isoformat(),
            "opening_balance": str(session.opening_balance),
        }

        # Create backup if file exists
        if self._storage_path.exists():
            backup_path = self._storage_path.with_suffix(".json.bak")
            try:
                shutil.copy2(self._storage_path, backup_path)
            except Exception as e:
                logger.warning("Failed to create backup: %s", e)

        # Write to temp file then atomically rename
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._storage_path.with_suffix(".json.tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.replace(self._storage_path)
            logger.info("Session created and persisted: %s", session.session_id)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.error("Failed to persist session: %s", e)
            raise

    def get_active(self) -> AppSession | None:
        """
        Retrieve the current active session from JSON storage with corruption recovery.

        :return: Active session if present; otherwise None.
        """
        # Try primary file first
        if self._storage_path.exists():
            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = AppSession(
                    session_id=UUID(data["session_id"]),
                    start_date=date.fromisoformat(data["start_date"]),
                    opening_balance=Decimal(data["opening_balance"]),
                )
                logger.info("Active session retrieved: %s", session.session_id)
                return session
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Failed to read primary session file: %s", e)
                # Fall through to try backup

        # Try backup file if primary failed
        backup_path = self._storage_path.with_suffix(".json.bak")
        if backup_path.exists():
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = AppSession(
                    session_id=UUID(data["session_id"]),
                    start_date=date.fromisoformat(data["start_date"]),
                    opening_balance=Decimal(data["opening_balance"]),
                )
                logger.info("Active session recovered from backup: %s", session.session_id)
                return session
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Failed to read backup session file: %s", e)

        return None
