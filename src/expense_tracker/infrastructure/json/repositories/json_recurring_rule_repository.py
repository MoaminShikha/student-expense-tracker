from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import RecurringFrequency, RecurringRule
from ....infrastructure.logging_config import LoggerFactory

logger: logging.Logger = LoggerFactory.get_logger(__name__)


class JsonRecurringRuleRepository:
    """JSON-backed recurring-rule repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, rule: RecurringRule) -> None:
        """
        Persist one recurring rule.

        :param rule: Recurring rule to persist.
        :return: None.
        """
        data = self._load_all()
        data.append({
            "rule_id": str(rule.rule_id),
            "session_id": str(rule.session_id),
            "name": rule.name,
            "amount": str(rule.amount),
            "frequency": rule.frequency.value,
            "day_of_month": rule.day_of_month,
            "reminder_days": rule.reminder_days,
        })
        self._save_all(data)
        logger.info("Recurring rule added: %s", rule.rule_id)

    def get_by_id(self, rule_id: UUID) -> RecurringRule | None:
        """
        Fetch one recurring rule by identifier.

        :param rule_id: Rule identifier.
        :return: Matching rule if found; otherwise None.
        """
        data = self._load_all()
        for record in data:
            if record["rule_id"] == str(rule_id):
                logger.info("Recurring rule retrieved: %s", rule_id)
                return self._deserialize(record)
        return None

    def list_for_session(self, session_id: UUID) -> list[RecurringRule]:
        """
        List recurring rules for one session.

        :param session_id: Session identifier.
        :return: Recurring rules for the session.
        """
        data = self._load_all()
        rules = []
        for record in data:
            if record["session_id"] == str(session_id):
                rules.append(self._deserialize(record))
        logger.info("Retrieved %d recurring rules for session %s", len(rules), session_id)
        return rules

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _deserialize(self, record: dict) -> RecurringRule:
        """Reconstruct a RecurringRule from a JSON record."""
        return RecurringRule(
            rule_id=UUID(record["rule_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            amount=Decimal(record["amount"]),
            frequency=RecurringFrequency(record["frequency"]),
            day_of_month=record["day_of_month"],
            reminder_days=record["reminder_days"],
        )

    def _load_all(self) -> list[dict]:
        """Load all records from storage."""
        if not self._storage_path.exists():
            return []
        try:
            with open(self._storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all(self, data: list[dict]) -> None:
        """Save all records to storage."""
        with open(self._storage_path, "w") as f:
            json.dump(data, f, indent=2)
