from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from expense_tracker.application.services import SpendService
from expense_tracker.domain.models import AppSession, TransactionCategory
from expense_tracker.infrastructure.json.repositories import JsonSessionRepository, JsonTransactionRepository
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for spend service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestSpendServiceAddTransaction:

    def test_add_transaction_persists_transaction(self, tmp_path, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one spend transaction
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        session_repo.create(active_session)
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        transaction = service.add_transaction(amount=Decimal("25.50"), description="Coffee and notes", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 11))

        stored = tx_repo.list_for_month(active_session.session_id, 2026, 4)
        assert len(stored) == 1
        assert stored[0] == transaction
        assert transaction.session_id == active_session.session_id
        assert transaction.amount == Decimal("25.50")
        assert transaction.description == "Coffee and notes"
        assert transaction.category is TransactionCategory.FOOD
        assert transaction.date == date(2026, 4, 11)

    def test_add_transaction_rejects_without_active_session(self, tmp_path) -> None:
        # service must fail fast if spend is logged before a session is started
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        with pytest.raises(ApplicationError):
            service.add_transaction(amount=Decimal("12.00"), description="Bus", category=TransactionCategory.TRANSPORT, spent_on=date(2026, 4, 12))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount — validation error"),
            pytest.param(Decimal("-1.00"), id="negative amount — validation error"),
        ],
    )
    def test_add_transaction_rejects_non_positive_amount(self, tmp_path, active_session: AppSession, amount: Decimal) -> None:
        # spend entries must always be positive amounts by project money convention
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        session_repo.create(active_session)
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=amount, description="Lunch", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 12))

    def test_add_transaction_rejects_blank_description(self, tmp_path, active_session: AppSession) -> None:
        # blank descriptions create unusable spend records and are not allowed
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        session_repo.create(active_session)
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="   ", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 12))

    def test_add_transaction_rejects_invalid_category_type(self, tmp_path, active_session: AppSession) -> None:
        # category must be a TransactionCategory enum or None
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        session_repo.create(active_session)
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="Snacks", category="food", spent_on=date(2026, 4, 12))  # type: ignore[arg-type]

    def test_add_transaction_rejects_invalid_date_type(self, tmp_path, active_session: AppSession) -> None:
        # transaction date must be a real date object so monthly filtering remains correct
        session_repo = JsonSessionRepository(tmp_path / "session.json")
        tx_repo = JsonTransactionRepository(tmp_path / "transactions.json")
        session_repo.create(active_session)
        service = SpendService(session_repository=session_repo, transaction_repository=tx_repo)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="Snacks", category=TransactionCategory.FOOD, spent_on="2026-04-12")  # type: ignore[arg-type]
