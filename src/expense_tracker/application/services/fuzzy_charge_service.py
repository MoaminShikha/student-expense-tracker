from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from ...domain.models import ChargeStatus, CommittedCharge, FuzzyCharge, FuzzyChargeStatus, FuzzyEntryDirection, \
    IncomeEntry, IncomeSourceTag
from ...ports.repositories import ChargeRepository, FuzzyChargeRepository, IncomeRepository, SessionRepository
from ...shared.exceptions import ApplicationError, ValidationError


class FuzzyChargeService:
    """Coordinates fuzzy entry lifecycle operations for an active session."""

    def __init__(self, session_repository: SessionRepository, fuzzy_charge_repository: FuzzyChargeRepository,
                 charge_repository: ChargeRepository, income_repository: IncomeRepository,
                 logger: logging.Logger | None = None) -> None:
        """
        Initialize the fuzzy service.

        :param session_repository: Repository abstraction for session persistence.
        :param fuzzy_charge_repository: Repository abstraction for fuzzy-entry persistence.
        :param charge_repository: Repository abstraction for committed-charge persistence.
        :param income_repository: Repository abstraction for income persistence.
        :param logger: Optional logger for fuzzy-entry operations.
        :return: None.
        """
        self._session_repository = session_repository
        self._fuzzy_charge_repository = fuzzy_charge_repository
        self._charge_repository = charge_repository
        self._income_repository = income_repository
        self._logger = logger or logging.getLogger(__name__)

    def add_fuzzy_entry(self, name: str, direction: FuzzyEntryDirection, expected_date: date | None = None,
                        estimated_amount: Decimal | None = None) -> FuzzyCharge:
        """
        Add one fuzzy entry to the active session.

        :param name: Human-readable fuzzy entry name.
        :param direction: Financial direction the entry resolves to.
        :param expected_date: Optional expected date.
        :param estimated_amount: Optional positive estimated amount.
        :return: Persisted fuzzy entry.
        """
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Fuzzy entry name cannot be empty.")

        if not isinstance(direction, FuzzyEntryDirection):
            raise ValidationError("Fuzzy entry direction is invalid.")

        if expected_date is not None and not isinstance(expected_date, date):
            raise ValidationError("Fuzzy entry expected date is invalid.")

        if estimated_amount is not None and estimated_amount <= 0:
            raise ValidationError("Fuzzy entry estimate must be greater than zero when provided.")

        active_session = self._session_repository.get_active()
        if active_session is None:
            raise ApplicationError("No active session. Start a session before adding fuzzy entries.")

        fuzzy_entry = FuzzyCharge(fuzzy_id=uuid4(), session_id=active_session.session_id, name=normalized_name,
                                  direction=direction, status=FuzzyChargeStatus.PENDING, expected_date=expected_date,
                                  estimated_amount=estimated_amount)
        self._fuzzy_charge_repository.add(fuzzy_entry)
        self._logger.info("Added fuzzy entry %s for session %s.", fuzzy_entry.fuzzy_id, active_session.session_id)
        return fuzzy_entry

    def add_fuzzy_charge(self, name: str, expected_date: date | None = None,
                         estimated_amount: Decimal | None = None) -> FuzzyCharge:
        """
        Add one fuzzy expense entry to the active session.

        :param name: Human-readable fuzzy entry name.
        :param expected_date: Optional expected date.
        :param estimated_amount: Optional positive estimated amount.
        :return: Persisted fuzzy entry.
        """
        return self.add_fuzzy_entry(name=name, direction=FuzzyEntryDirection.EXPENSE, expected_date=expected_date,
                                    estimated_amount=estimated_amount)

    def resolve(self, fuzzy_id: UUID, resolved_amount: Decimal, resolved_date: date | None = None,
                income_source_tag: IncomeSourceTag = IncomeSourceTag.OTHER) -> FuzzyCharge:
        """
        Resolve one fuzzy entry to a concrete expense or income record.

        :param fuzzy_id: Identifier of the fuzzy entry to resolve.
        :param resolved_amount: Confirmed positive amount.
        :param resolved_date: Optional resolved date override.
        :param income_source_tag: Source tag used when resolving to income.
        :return: Updated resolved fuzzy entry.
        """
        if not isinstance(fuzzy_id, UUID):
            raise ValidationError("Fuzzy entry identifier is invalid.")

        if resolved_amount <= 0:
            raise ValidationError("Resolved amount must be greater than zero.")

        if resolved_date is not None and not isinstance(resolved_date, date):
            raise ValidationError("Resolved date is invalid.")

        fuzzy_entry = self._fuzzy_charge_repository.get_by_id(fuzzy_id)
        if fuzzy_entry is None:
            raise ApplicationError("Fuzzy entry not found.")

        if fuzzy_entry.status in {FuzzyChargeStatus.RESOLVED, FuzzyChargeStatus.DISCARDED}:
            raise ApplicationError("Only pending or overdue fuzzy entries can be resolved.")

        applied_date = resolved_date or fuzzy_entry.expected_date or date.today()
        updated_entry = FuzzyCharge(fuzzy_id=fuzzy_entry.fuzzy_id, session_id=fuzzy_entry.session_id,
                                    name=fuzzy_entry.name, direction=fuzzy_entry.direction,
                                    status=FuzzyChargeStatus.RESOLVED, expected_date=fuzzy_entry.expected_date,
                                    estimated_amount=fuzzy_entry.estimated_amount, resolved_amount=resolved_amount,
                                    resolved_date=applied_date)
        self._fuzzy_charge_repository.update(updated_entry)

        if updated_entry.direction is FuzzyEntryDirection.EXPENSE:
            committed_charge = CommittedCharge(charge_id=uuid4(), session_id=updated_entry.session_id,
                                               name=updated_entry.name, amount=resolved_amount, due_date=applied_date,
                                               status=ChargeStatus.UPCOMING)
            self._charge_repository.add(committed_charge)
            self._logger.info("Resolved fuzzy entry %s into committed charge %s.", updated_entry.fuzzy_id,
                              committed_charge.charge_id)
            return updated_entry

        if not isinstance(income_source_tag, IncomeSourceTag):
            raise ValidationError("Income source tag is invalid.")

        income_entry = IncomeEntry(income_id=uuid4(), session_id=updated_entry.session_id, amount=resolved_amount,
                                   source_tag=income_source_tag, date=applied_date)
        self._income_repository.add(income_entry)
        self._logger.info("Resolved fuzzy entry %s into income entry %s.", updated_entry.fuzzy_id,
                          income_entry.income_id)
        return updated_entry

    def discard(self, fuzzy_id: UUID) -> FuzzyCharge:
        """
        Discard one fuzzy entry without creating a concrete record.

        :param fuzzy_id: Identifier of the fuzzy entry to discard.
        :return: Updated discarded fuzzy entry.
        """
        if not isinstance(fuzzy_id, UUID):
            raise ValidationError("Fuzzy entry identifier is invalid.")

        fuzzy_entry = self._fuzzy_charge_repository.get_by_id(fuzzy_id)
        if fuzzy_entry is None:
            raise ApplicationError("Fuzzy entry not found.")

        if fuzzy_entry.status in {FuzzyChargeStatus.RESOLVED, FuzzyChargeStatus.DISCARDED}:
            raise ApplicationError("Only pending or overdue fuzzy entries can be discarded.")

        updated_entry = FuzzyCharge(fuzzy_id=fuzzy_entry.fuzzy_id, session_id=fuzzy_entry.session_id,
                                    name=fuzzy_entry.name, direction=fuzzy_entry.direction,
                                    status=FuzzyChargeStatus.DISCARDED, expected_date=fuzzy_entry.expected_date,
                                    estimated_amount=fuzzy_entry.estimated_amount,
                                    resolved_amount=fuzzy_entry.resolved_amount,
                                    resolved_date=fuzzy_entry.resolved_date)
        self._fuzzy_charge_repository.update(updated_entry)
        self._logger.info("Discarded fuzzy entry %s.", updated_entry.fuzzy_id)
        return updated_entry
