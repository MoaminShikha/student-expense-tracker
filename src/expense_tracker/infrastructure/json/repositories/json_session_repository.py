from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from ....domain.models import AppSession
from ..mappers import SessionMapper

logger: logging.Logger = logging.getLogger(__name__)


class JsonSessionRepository:
    """JSON-backed session repository adapter for Stage 1.

    Stores a single session object (not a list), so it keeps its own atomic
    write rather than extending the list-backed :class:`JsonStore`; field
    mapping is delegated to :class:`SessionMapper`.
    """

    def __init__(self, storage_path: Path | str) -> None:
        """
        :param storage_path: Path to the JSON storage file.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._mapper = SessionMapper()

    def create(self, session: AppSession) -> None:
        """Persist a session to JSON storage using atomic write."""
        data = self._mapper.to_dict(session)

        if self._storage_path.exists():
            backup_path = self._storage_path.with_suffix(".json.bak")
            try:
                shutil.copy2(self._storage_path, backup_path)
            except Exception as e:
                logger.warning("Failed to create backup: %s", e)

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
        """Retrieve the active session, falling back to backup on corruption."""
        for path, recovered in ((self._storage_path, False),
                                (self._storage_path.with_suffix(".json.bak"), True)):
            if not path.exists():
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    session = self._mapper.from_dict(json.load(f))
                if recovered:
                    logger.info("Active session recovered from backup: %s", session.session_id)
                else:
                    logger.debug("Active session retrieved: %s", session.session_id)
                return session
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Failed to read session file %s: %s", path, e)

        return None
