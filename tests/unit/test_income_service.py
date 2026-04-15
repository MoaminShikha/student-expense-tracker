from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from expense_tracker.application.services import IncomeService
from expense_tracker.domain.models import AppSession, IncomeEntry, IncomeSourceTag
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class _InMemorySessionRepository:

    def __init__(self, active_session: AppSession | None = None) -> None:
        self._active_session = active_session

    def create(self, session: AppSession) -> None:
        self._active_session = session

    def get_active(self) -> AppSession | None:
        return self._active_session


class _InMemoryIncomeRepository:

    def __init__(self) -> None:
        self.entries: list[IncomeEntry] = []

    def add(self, entry: IncomeEntry) -> None:
        self.entries.append(entry)

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        return [entry for entry in self.entries if entry.session_id == session_id]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        return [entry for entry in self.entries if entry.session_id == session_id and entry.date.year == year and entry.date.month == month]


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for income service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestIncomeServiceAddIncome:

    def test_add_income_persists_income_entry(self, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one income entry
        session_repository = _InMemorySessionRepository(active_session=active_session)
        income_repository = _InMemoryIncomeRepository()
        service = IncomeService(session_repository=session_repository, income_repository=income_repository)

        entry = service.add_income(amount=Decimal("250.00"), source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))

        assert len(income_repository.entries) == 1
        assert income_repository.entries[0] == entry
        assert entry.session_id == active_session.session_id
        assert entry.amount == Decimal("250.00")
        assert entry.source_tag is IncomeSourceTag.WORK
        assert entry.date == date(2026, 4, 15)

    def test_add_income_rejects_when_no_active_session(self) -> None:
        # service must fail fast if the caller tries to add income before starting a session
        session_repository = _InMemorySessionRepository(active_session=None)
        income_repository = _InMemoryIncomeRepository()
        service = IncomeService(session_repository=session_repository, income_repository=income_repository)

        with pytest.raises(ApplicationError):
            service.add_income(amount=Decimal("250.00"), source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount",),
            pytest.param(Decimal("-1.00"), id="negative amount",),
        ],
    )
    def test_add_income_rejects_non_positive_amount(self, active_session: AppSession, amount: Decimal) -> None:
        # income must always increase available funds; zero/negative values are invalid
        session_repository = _InMemorySessionRepository(active_session=active_session)
        income_repository = _InMemoryIncomeRepository()
        service = IncomeService(session_repository=session_repository, income_repository=income_repository)

        with pytest.raises(ValidationError):
            service.add_income(amount=amount, source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))

