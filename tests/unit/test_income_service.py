from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from expense_tracker.application.services import IncomeService
from expense_tracker.domain.models import AppSession, IncomeSourceTag
from expense_tracker.infrastructure.json.repositories import JsonIncomeRepository, JsonSessionRepository
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for income service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestIncomeServiceAddIncome:

    def test_add_income_persists_income_entry(self, tmp_path, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one income entry
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        income_repo = JsonIncomeRepository(tmp_path / "income.json")
        session_repo.create(active_session)
        service = IncomeService(session_repository=session_repo, income_repository=income_repo)

        entry = service.add_income(amount=Decimal("250.00"), source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))

        entries = income_repo.list_for_session(active_session.session_id)
        assert len(entries) == 1
        assert entries[0] == entry
        assert entry.session_id == active_session.session_id
        assert entry.amount == Decimal("250.00")
        assert entry.source_tag is IncomeSourceTag.WORK
        assert entry.date == date(2026, 4, 15)

    def test_add_income_rejects_when_no_active_session(self, tmp_path) -> None:
        # service must fail fast if the caller tries to add income before starting a session
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        income_repo = JsonIncomeRepository(tmp_path / "income.json")
        service = IncomeService(session_repository=session_repo, income_repository=income_repo)

        with pytest.raises(ApplicationError):
            service.add_income(amount=Decimal("250.00"), source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount"),
            pytest.param(Decimal("-1.00"), id="negative amount"),
        ],
    )
    def test_add_income_rejects_non_positive_amount(self, tmp_path, active_session: AppSession, amount: Decimal) -> None:
        # income must always increase available funds; zero/negative values are invalid
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        income_repo = JsonIncomeRepository(tmp_path / "income.json")
        session_repo.create(active_session)
        service = IncomeService(session_repository=session_repo, income_repository=income_repo)

        with pytest.raises(ValidationError):
            service.add_income(amount=amount, source_tag=IncomeSourceTag.WORK, entry_date=date(2026, 4, 15))
