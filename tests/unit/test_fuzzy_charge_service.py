from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from expense_tracker.application.services import FuzzyChargeService
from expense_tracker.domain.models import AppSession, ChargeStatus, FuzzyChargeStatus, FuzzyEntryDirection, IncomeSourceTag
from expense_tracker.infrastructure.json.repositories import (
    JsonChargeRepository,
    JsonFuzzyChargeRepository,
    JsonIncomeRepository,
    JsonSessionRepository,
)
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


def _build_service(
    tmp_path: Path,
    active_session: AppSession | None = None,
) -> tuple[FuzzyChargeService, JsonFuzzyChargeRepository, JsonChargeRepository, JsonIncomeRepository]:
    session_repo = JsonSessionRepository(tmp_path / "session.json")
    fuzzy_repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
    charge_repo = JsonChargeRepository(tmp_path / "charges.json")
    income_repo = JsonIncomeRepository(tmp_path / "income.json")
    if active_session is not None:
        session_repo.create(active_session)
    service = FuzzyChargeService(
        session_repository=session_repo,
        fuzzy_charge_repository=fuzzy_repo,
        charge_repository=charge_repo,
        income_repository=income_repo,
    )
    return service, fuzzy_repo, charge_repo, income_repo


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for fuzzy service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestFuzzyChargeServiceAdd:

    def test_add_fuzzy_entry_supports_income_or_expense(self, tmp_path, active_session: AppSession) -> None:
        # fuzzy entries can represent either uncertain expense or uncertain income
        service, fuzzy_repo, _, _ = _build_service(tmp_path, active_session=active_session)

        expense_entry = service.add_fuzzy_entry(name="Unknown utility bill", direction=FuzzyEntryDirection.EXPENSE, expected_date=date(2026, 4, 20), estimated_amount=Decimal("90.00"))
        income_entry = service.add_fuzzy_entry(name="Possible refund", direction=FuzzyEntryDirection.INCOME, expected_date=None, estimated_amount=None)

        pending = fuzzy_repo.list_pending(active_session.session_id)
        assert len(pending) == 2
        assert expense_entry.direction is FuzzyEntryDirection.EXPENSE
        assert income_entry.direction is FuzzyEntryDirection.INCOME
        assert income_entry.expected_date is None
        assert income_entry.estimated_amount is None

    def test_add_fuzzy_entry_rejects_non_positive_estimate(self, tmp_path, active_session: AppSession) -> None:
        # when an estimate is provided it must be a strict positive amount
        service, _, _, _ = _build_service(tmp_path, active_session=active_session)

        with pytest.raises(ValidationError):
            service.add_fuzzy_entry(name="Utility", direction=FuzzyEntryDirection.EXPENSE, estimated_amount=Decimal("0"))

    def test_add_fuzzy_entry_rejects_without_active_session(self, tmp_path) -> None:
        # fuzzy entries still require a started session context
        service, _, _, _ = _build_service(tmp_path, active_session=None)

        with pytest.raises(ApplicationError):
            service.add_fuzzy_entry(name="Utility", direction=FuzzyEntryDirection.EXPENSE)


class TestFuzzyChargeServiceResolve:

    def test_resolve_expense_creates_committed_charge_with_confirmed_amount(self, tmp_path, active_session: AppSession) -> None:
        # resolving an expense creates a committed charge and may differ from estimate
        service, fuzzy_repo, charge_repo, _ = _build_service(tmp_path, active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Power bill", direction=FuzzyEntryDirection.EXPENSE, expected_date=date(2026, 4, 20), estimated_amount=Decimal("80.00"))

        resolved_entry = service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("95.50"), resolved_date=date(2026, 4, 22))

        assert resolved_entry.status is FuzzyChargeStatus.RESOLVED
        assert resolved_entry.resolved_amount == Decimal("95.50")
        assert resolved_entry.estimated_amount == Decimal("80.00")
        assert fuzzy_repo.get_by_id(fuzzy_entry.fuzzy_id) == resolved_entry
        charges = charge_repo.list_upcoming(active_session.session_id)
        assert len(charges) == 1
        assert charges[0].status is ChargeStatus.UPCOMING
        assert charges[0].amount == Decimal("95.50")
        assert charges[0].due_date == date(2026, 4, 22)

    def test_resolve_income_creates_income_entry(self, tmp_path, active_session: AppSession) -> None:
        # resolving an income fuzzy entry creates one income record instead of a committed charge
        service, _, charge_repo, income_repo = _build_service(tmp_path, active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Unknown stipend", direction=FuzzyEntryDirection.INCOME)

        resolved_entry = service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("150.00"), resolved_date=date(2026, 4, 25), income_source_tag=IncomeSourceTag.OTHER)

        assert resolved_entry.status is FuzzyChargeStatus.RESOLVED
        assert len(charge_repo.list_upcoming(active_session.session_id)) == 0
        income_entries = income_repo.list_for_session(active_session.session_id)
        assert len(income_entries) == 1
        assert income_entries[0].amount == Decimal("150.00")
        assert income_entries[0].date == date(2026, 4, 25)


class TestFuzzyChargeServiceDiscard:

    def test_discard_sets_discarded_without_creating_concrete_records(self, tmp_path, active_session: AppSession) -> None:
        # discarding a fuzzy entry must not create a committed charge or income entry
        service, _, charge_repo, income_repo = _build_service(tmp_path, active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Maybe fee", direction=FuzzyEntryDirection.EXPENSE)

        discarded_entry = service.discard(fuzzy_id=fuzzy_entry.fuzzy_id)

        assert discarded_entry.status is FuzzyChargeStatus.DISCARDED
        assert len(charge_repo.list_upcoming(active_session.session_id)) == 0
        assert len(income_repo.list_for_session(active_session.session_id)) == 0

    def test_discard_rejects_when_entry_already_resolved(self, tmp_path, active_session: AppSession) -> None:
        # terminal entries cannot be discarded after resolution
        service, _, _, _ = _build_service(tmp_path, active_session=active_session)
        fuzzy_entry = service.add_fuzzy_entry(name="Maybe fee", direction=FuzzyEntryDirection.EXPENSE)
        service.resolve(fuzzy_id=fuzzy_entry.fuzzy_id, resolved_amount=Decimal("55.00"), resolved_date=date(2026, 4, 18))

        with pytest.raises(ApplicationError):
            service.discard(fuzzy_id=fuzzy_entry.fuzzy_id)
