from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from expense_tracker.application.services import FuzzyChargeService
from expense_tracker.domain.models import AppSession, ChargeStatus, CommittedCharge, FuzzyCharge, FuzzyChargeStatus, FuzzyEntryDirection, IncomeEntry, IncomeSourceTag
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class _InMemorySessionRepository:

    def __init__(self, active_session: AppSession | None = None) -> None:
        self._active_session = active_session

    def create(self, session: AppSession) -> None:
        self._active_session = session

    def get_active(self) -> AppSession | None:
        return self._active_session


class _InMemoryFuzzyChargeRepository:

    def __init__(self) -> None:
        self.entries: list[FuzzyCharge] = []

    def add(self, charge: FuzzyCharge) -> None:
        self.entries.append(charge)

    def get_by_id(self, fuzzy_id: UUID) -> FuzzyCharge | None:
        for entry in self.entries:
            if entry.fuzzy_id == fuzzy_id:
                return entry
        return None

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        return [entry for entry in self.entries if entry.session_id == session_id and entry.status is FuzzyChargeStatus.PENDING]

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        self.entries = [FuzzyCharge(fuzzy_id=entry.fuzzy_id, session_id=entry.session_id, name=entry.name, direction=entry.direction, status=status, expected_date=entry.expected_date, estimated_amount=entry.estimated_amount, resolved_amount=entry.resolved_amount, resolved_date=entry.resolved_date) if entry.fuzzy_id == fuzzy_id else entry for entry in self.entries]

    def update(self, charge: FuzzyCharge) -> None:
        self.entries = [charge if entry.fuzzy_id == charge.fuzzy_id else entry for entry in self.entries]


class _InMemoryChargeRepository:

    def __init__(self) -> None:
        self.charges: list[CommittedCharge] = []

    def add(self, charge: CommittedCharge) -> None:
        self.charges.append(charge)

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        return [charge for charge in self.charges if charge.session_id == session_id and charge.status is ChargeStatus.UPCOMING]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        return [charge for charge in self.charges if charge.session_id == session_id and charge.due_date.year == year and charge.due_date.month == month]

    def mark_paid(self, charge_id: UUID) -> None:
        self.charges = [CommittedCharge(charge_id=charge.charge_id, session_id=charge.session_id, name=charge.name, amount=charge.amount, due_date=charge.due_date, status=ChargeStatus.PAID, recurring_rule_id=charge.recurring_rule_id) if charge.charge_id == charge_id else charge for charge in self.charges]

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        for charge in self.charges:
            if charge.charge_id == charge_id:
                return charge
        return None


class _InMemoryIncomeRepository:

    def __init__(self) -> None:
        self.entries: list[IncomeEntry] = []

    def add(self, entry: IncomeEntry) -> None:
        self.entries.append(entry)

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        return [entry for entry in self.entries if entry.session_id == session_id]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        return [entry for entry in self.entries if entry.session_id == session_id and entry.date.year == year and entry.date.month == month]


def _build_service(active_session: AppSession | None = None) -> tuple[FuzzyChargeService, _InMemoryFuzzyChargeRepository, _InMemoryChargeRepository, _InMemoryIncomeRepository]:
    session_repository = _InMemorySessionRepository(active_session=active_session)
    fuzzy_repository = _InMemoryFuzzyChargeRepository()
    charge_repository = _InMemoryChargeRepository()
    income_repository = _InMemoryIncomeRepository()
    service = FuzzyChargeService(session_repository=session_repository, fuzzy_charge_repository=fuzzy_repository, charge_repository=charge_repository, income_repository=income_repository)
    return service, fuzzy_repository, charge_repository, income_repository


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for fuzzy service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestFuzzyChargeServiceAdd:

    def test_add_fuzzy_entry_supports_income_or_expense(self, active_session: AppSession) -> None:
        # fuzzy entries can represent either uncertain expense or uncertain income
        service, fuzzy_repository, _, _ = _build_service(active_session=active_session)

        expense_entry = service.add_fuzzy_entry(name="Unknown utility bill", direction=FuzzyEntryDirection.EXPENSE, expected_date=date(2026, 4, 20), estimated_amount=Decimal("90.00"))
        income_entry = service.add_fuzzy_entry(name="Possible refund", direction=FuzzyEntryDirection.INCOME, expected_date=None, estimated_amount=None)

        assert len(fuzzy_repository.entries) == 2
        assert expense_entry.direction is FuzzyEntryDirection.EXPENSE
        assert income_entry.direction is FuzzyEntryDirection.INCOME
        assert income_entry.expected_date is None
        assert income_entry.estimated_amount is None

    def test_add_fuzzy_entry_rejects_non_positive_estimate(self, active_session: AppSession) -> None:
        # when an estimate is provided it must be a strict positive amount
        service, _, _, _ = _build_service(active_session=active_session)

        with pytest.raises(ValidationError):
            service.add_fuzzy_entry(name="Utility", direction=FuzzyEntryDirection.EXPENSE, estimated_amount=Decimal("0"))

    def test_add_fuzzy_entry_rejects_without_active_session(self) -> None:
        # fuzzy entries still require a started session context
        service, _, _, _ = _build_service(active_session=None)

        with pytest.raises(ApplicationError):
            service.add_fuzzy_entry(name="Utility", direction=FuzzyEntryDirection.EXPENSE)


class TestFuzzyChargeServiceResolve:

    def test_resolve_expense_creates_committed_charge_with_confirmed_amount(self, active_session: AppSession) -> None:
        # resolving an expense creates a committed charge and may differ from estimate
        service, fuzzy_repository, charge_repository, _ = _build_service(active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Power bill", direction=FuzzyEntryDirection.EXPENSE, expected_date=date(2026, 4, 20), estimated_amount=Decimal("80.00"))

        resolved_entry = service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("95.50"), resolved_date=date(2026, 4, 22))

        assert resolved_entry.status is FuzzyChargeStatus.RESOLVED
        assert resolved_entry.resolved_amount == Decimal("95.50")
        assert resolved_entry.estimated_amount == Decimal("80.00")
        assert fuzzy_repository.get_by_id(fuzzy_entry.fuzzy_id) == resolved_entry
        assert len(charge_repository.charges) == 1
        assert charge_repository.charges[0].status is ChargeStatus.UPCOMING
        assert charge_repository.charges[0].amount == Decimal("95.50")
        assert charge_repository.charges[0].due_date == date(2026, 4, 22)

    def test_resolve_income_creates_income_entry(self, active_session: AppSession) -> None:
        # resolving an income fuzzy entry creates one income record instead of a committed charge
        service, _, charge_repository, income_repository = _build_service(active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Unknown stipend", direction=FuzzyEntryDirection.INCOME)

        resolved_entry = service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("150.00"), resolved_date=date(2026, 4, 25), income_source_tag=IncomeSourceTag.OTHER)

        assert resolved_entry.status is FuzzyChargeStatus.RESOLVED
        assert len(charge_repository.charges) == 0
        assert len(income_repository.entries) == 1
        assert income_repository.entries[0].amount == Decimal("150.00")
        assert income_repository.entries[0].date == date(2026, 4, 25)


class TestFuzzyChargeServiceDiscard:

    def test_discard_sets_discarded_without_creating_concrete_records(self, active_session: AppSession) -> None:
        # discarding a fuzzy entry must not create a committed charge or income entry
        service, _, charge_repository, income_repository = _build_service(active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Maybe fee", direction=FuzzyEntryDirection.EXPENSE)

        discarded_entry = service.discard(fuzzy_id=fuzzy_entry.fuzzy_id)

        assert discarded_entry.status is FuzzyChargeStatus.DISCARDED
        assert len(charge_repository.charges) == 0
        assert len(income_repository.entries) == 0

    def test_discard_rejects_when_entry_already_resolved(self, active_session: AppSession) -> None:
        # terminal entries cannot be discarded after resolution
        service, _, _, _ = _build_service(active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Maybe fee", direction=FuzzyEntryDirection.EXPENSE)
        service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("55.00"), resolved_date=date(2026, 4, 18))

        with pytest.raises(ApplicationError):
            service.discard(fuzzy_id=fuzzy_entry.fuzzy_id)
