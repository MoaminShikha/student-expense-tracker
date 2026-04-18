from __future__ import annotations

import json
import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import ChargeStatus, CommittedCharge
from ....infrastructure.logging_config import LoggerFactory

logger: logging.Logger = LoggerFactory.get_logger(__name__)


class JsonChargeRepository:
    """JSON-backed committed-charge repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, charge: CommittedCharge) -> None:
        """
        Persist one committed charge.

        :param charge: Charge to persist.
        :return: None.
        """
        data = self._load_all()
        data.append({
            "charge_id": str(charge.charge_id),
            "session_id": str(charge.session_id),
            "name": charge.name,
            "amount": str(charge.amount),
            "due_date": charge.due_date.isoformat(),
            "status": charge.status.value,
            "recurring_rule_id": str(charge.recurring_rule_id) if charge.recurring_rule_id else None,
        })
        self._save_all(data)
        logger.info("Committed charge added: %s", charge.charge_id)

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        """
        List upcoming charges for one session.

        :param session_id: Session identifier.
        :return: Upcoming committed charges.
        """
        data = self._load_all()
        charges = []
        for record in data:
            if record["session_id"] == str(session_id) and record["status"] == ChargeStatus.UPCOMING.value:
                charges.append(self._deserialize(record))
        logger.info("Retrieved %d upcoming charges for session %s", len(charges), session_id)
        return charges

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        """
        List committed charges for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Committed charges for the month.
        """
        data = self._load_all()
        charges = []
        for record in data:
            if record["session_id"] == str(session_id):
                due_date = date.fromisoformat(record["due_date"])
                if due_date.year == year and due_date.month == month:
                    charges.append(self._deserialize(record))
        logger.info(
            "Retrieved %d committed charges for session %s in %d-%02d",
            len(charges), session_id, year, month,
        )
        return charges

    def mark_paid(self, charge_id: UUID) -> None:
        """
        Mark one committed charge as paid.

        :param charge_id: Charge identifier.
        :return: None.
        """
        data = self._load_all()
        for record in data:
            if record["charge_id"] == str(charge_id):
                record["status"] = ChargeStatus.PAID.value
                break
        self._save_all(data)
        logger.info("Charge marked paid: %s", charge_id)

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        """
        Fetch one committed charge by identifier.

        :param charge_id: Charge identifier.
        :return: Matching charge if found; otherwise None.
        """
        data = self._load_all()
        for record in data:
            if record["charge_id"] == str(charge_id):
                logger.info("Committed charge retrieved: %s", charge_id)
                return self._deserialize(record)
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _deserialize(self, record: dict) -> CommittedCharge:
        """Reconstruct a CommittedCharge from a JSON record."""
        return CommittedCharge(
            charge_id=UUID(record["charge_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            amount=Decimal(record["amount"]),
            due_date=date.fromisoformat(record["due_date"]),
            status=ChargeStatus(record["status"]),
            recurring_rule_id=UUID(record["recurring_rule_id"]) if record["recurring_rule_id"] else None,
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
