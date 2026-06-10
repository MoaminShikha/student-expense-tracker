from __future__ import annotations

import logging
from dataclasses import replace
from uuid import UUID

from ....domain.models import FuzzyCharge, FuzzyChargeStatus
from ..mappers import FuzzyChargeMapper
from .base import JsonStore

logger: logging.Logger = logging.getLogger(__name__)


class JsonFuzzyChargeRepository(JsonStore[FuzzyCharge]):
    """JSON-backed fuzzy-entry repository adapter for Stage 1."""

    def __init__(self, storage_path) -> None:
        super().__init__(storage_path, FuzzyChargeMapper())

    def add(self, charge: FuzzyCharge) -> None:
        """Persist one fuzzy entry."""
        self._append(charge)
        logger.info("Fuzzy entry added: %s", charge.fuzzy_id)

    def get_by_id(self, fuzzy_id: UUID) -> FuzzyCharge | None:
        """Fetch one fuzzy entry by identifier."""
        for charge in self._all():
            if charge.fuzzy_id == fuzzy_id:
                logger.debug("Fuzzy entry retrieved: %s", fuzzy_id)
                return charge
        return None

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        """List pending fuzzy entries for one session."""
        charges = [
            c for c in self._all()
            if c.session_id == session_id and c.status is FuzzyChargeStatus.PENDING
        ]
        logger.debug("Retrieved %d pending fuzzy entries for session %s", len(charges), session_id)
        return charges

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        """Update the status of one fuzzy entry."""
        self._persist([
            self._mapper.to_dict(replace(c, status=status) if c.fuzzy_id == fuzzy_id else c)
            for c in self._all()
        ])
        logger.info("Fuzzy entry status updated: %s → %s", fuzzy_id, status.value)

    def update(self, charge: FuzzyCharge) -> None:
        """Persist full-state changes to one fuzzy entry."""
        self._persist([
            self._mapper.to_dict(charge if c.fuzzy_id == charge.fuzzy_id else c)
            for c in self._all()
        ])
        logger.info("Fuzzy entry updated: %s", charge.fuzzy_id)
