from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ....domain.models import FuzzyCharge, FuzzyChargeStatus, FuzzyEntryDirection
from ..safe_file_io import load_json_safely, save_json_safely

logger: logging.Logger = logging.getLogger(__name__)


class JsonFuzzyChargeRepository:
    """JSON-backed fuzzy-entry repository adapter for Stage 1."""

    def __init__(self, storage_path: Path | str) -> None:
        """
        Initialize the repository with storage path.

        :param storage_path: Path to the JSON storage file.
        :return: None.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, charge: FuzzyCharge) -> None:
        """
        Persist one fuzzy entry.

        :param charge: Fuzzy entry to persist.
        :return: None.
        """
        data = self._load_all()
        data.append(self._serialize(charge))
        self._save_all(data)
        logger.info("Fuzzy entry added: %s", charge.fuzzy_id)

    def get_by_id(self, fuzzy_id: UUID) -> FuzzyCharge | None:
        """
        Fetch one fuzzy entry by identifier.

        :param fuzzy_id: Entry identifier.
        :return: Matching fuzzy entry if found; otherwise None.
        """
        data = self._load_all()
        for record in data:
            if record["fuzzy_id"] == str(fuzzy_id):
                logger.info("Fuzzy entry retrieved: %s", fuzzy_id)
                return self._deserialize(record)
        return None

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        """
        List pending fuzzy entries for one session.

        :param session_id: Session identifier.
        :return: Pending fuzzy entries for the session.
        """
        data = self._load_all()
        charges = []
        for record in data:
            if record["session_id"] == str(session_id) and record["status"] == FuzzyChargeStatus.PENDING.value:
                charges.append(self._deserialize(record))
        logger.info("Retrieved %d pending fuzzy entries for session %s", len(charges), session_id)
        return charges

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        """
        Update the status of one fuzzy entry.

        :param fuzzy_id: Entry identifier.
        :param status: New fuzzy entry status.
        :return: None.
        """
        data = self._load_all()
        for record in data:
            if record["fuzzy_id"] == str(fuzzy_id):
                record["status"] = status.value
                break
        self._save_all(data)
        logger.info("Fuzzy entry status updated: %s → %s", fuzzy_id, status.value)

    def update(self, charge: FuzzyCharge) -> None:
        """
        Persist full-state changes to one fuzzy entry.

        :param charge: Updated fuzzy entry.
        :return: None.
        """
        data = self._load_all()
        for i, record in enumerate(data):
            if record["fuzzy_id"] == str(charge.fuzzy_id):
                data[i] = self._serialize(charge)
                break
        self._save_all(data)
        logger.info("Fuzzy entry updated: %s", charge.fuzzy_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _serialize(self, charge: FuzzyCharge) -> dict:
        """Serialize a FuzzyCharge to a JSON-safe dict."""
        return {
            "fuzzy_id": str(charge.fuzzy_id),
            "session_id": str(charge.session_id),
            "name": charge.name,
            "direction": charge.direction.value,
            "status": charge.status.value,
            "expected_date": charge.expected_date.isoformat() if charge.expected_date else None,
            "estimated_amount": str(charge.estimated_amount) if charge.estimated_amount else None,
            "resolved_amount": str(charge.resolved_amount) if charge.resolved_amount else None,
            "resolved_date": charge.resolved_date.isoformat() if charge.resolved_date else None,
        }

    def _deserialize(self, record: dict) -> FuzzyCharge:
        """Reconstruct a FuzzyCharge from a JSON record."""
        return FuzzyCharge(
            fuzzy_id=UUID(record["fuzzy_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            direction=FuzzyEntryDirection(record["direction"]),
            status=FuzzyChargeStatus(record["status"]),
            expected_date=date.fromisoformat(record["expected_date"]) if record["expected_date"] else None,
            estimated_amount=Decimal(record["estimated_amount"]) if record["estimated_amount"] else None,
            resolved_amount=Decimal(record["resolved_amount"]) if record["resolved_amount"] else None,
            resolved_date=date.fromisoformat(record["resolved_date"]) if record["resolved_date"] else None,
        )

    def _load_all(self) -> list[dict]:
        """Load all records from storage with corruption recovery."""
        return load_json_safely(self._storage_path)

    def _save_all(self, data: list[dict]) -> None:
        """Save all records to storage with atomic write and backup."""
        save_json_safely(self._storage_path, data)
