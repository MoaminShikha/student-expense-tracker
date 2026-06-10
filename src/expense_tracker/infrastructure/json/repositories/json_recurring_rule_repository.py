from __future__ import annotations

import logging
from uuid import UUID

from ....domain.models import RecurringRule
from ..mappers import RecurringRuleMapper
from .base import JsonStore

logger: logging.Logger = logging.getLogger(__name__)


class JsonRecurringRuleRepository(JsonStore[RecurringRule]):
    """JSON-backed recurring-rule repository adapter for Stage 1."""

    def __init__(self, storage_path) -> None:
        super().__init__(storage_path, RecurringRuleMapper())

    def add(self, rule: RecurringRule) -> None:
        """Persist one recurring rule."""
        self._append(rule)
        logger.info("Recurring rule added: %s", rule.rule_id)

    def get_by_id(self, rule_id: UUID) -> RecurringRule | None:
        """Fetch one recurring rule by identifier."""
        for rule in self._all():
            if rule.rule_id == rule_id:
                logger.debug("Recurring rule retrieved: %s", rule_id)
                return rule
        return None

    def list_for_session(self, session_id: UUID) -> list[RecurringRule]:
        """List recurring rules for one session."""
        rules = [r for r in self._all() if r.session_id == session_id]
        logger.debug("Retrieved %d recurring rules for session %s", len(rules), session_id)
        return rules
