from __future__ import annotations

import logging
from uuid import UUID

from ....domain.models import ChargeStatus, CommittedCharge
from ..mappers import ChargeMapper
from .base import JsonStore

logger: logging.Logger = logging.getLogger(__name__)


class JsonChargeRepository(JsonStore[CommittedCharge]):
    """JSON-backed committed-charge repository adapter for Stage 1."""

    def __init__(self, storage_path) -> None:
        super().__init__(storage_path, ChargeMapper())

    def add(self, charge: CommittedCharge) -> None:
        """Persist one committed charge."""
        self._append(charge)
        logger.info("Committed charge added: %s", charge.charge_id)

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        """List upcoming charges for one session."""
        charges = [c for c in self._all() if c.session_id == session_id and c.status is ChargeStatus.UPCOMING]
        logger.debug("Retrieved %d upcoming charges for session %s", len(charges), session_id)
        return charges

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        """List committed charges for one calendar month."""
        charges = [
            c for c in self._all()
            if c.session_id == session_id and c.due_date.year == year and c.due_date.month == month
        ]
        logger.info(
            "Retrieved %d committed charges for session %s in %d-%02d",
            len(charges), session_id, year, month,
        )
        return charges

    def mark_paid(self, charge_id: UUID) -> None:
        """Mark one committed charge as paid."""
        self._persist([
            self._mapper.to_dict(c.mark_paid() if c.charge_id == charge_id else c)
            for c in self._all()
        ])
        logger.info("Charge marked paid: %s", charge_id)

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        """Fetch one committed charge by identifier."""
        for charge in self._all():
            if charge.charge_id == charge_id:
                logger.debug("Committed charge retrieved: %s", charge_id)
                return charge
        return None
