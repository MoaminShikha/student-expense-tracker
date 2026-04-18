from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from expense_tracker.application.services import SpendService
from expense_tracker.domain.models import AppSession, Transaction, TransactionCategory
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class _InMemorySessionRepository:

    def __init__(self, active_session: AppSession | None = None) -> None:
        self._active_session = active_session

    def create(self, session: AppSession) -> None:
        self._active_session = session

    def get_active(self) -> AppSession | None:
        return self._active_session


class _InMemoryTransactionRepository:

    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        return [transaction for transaction in self.transactions if transaction.session_id == session_id and transaction.date.year == year and transaction.date.month == month]


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for spend service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestSpendServiceAddTransaction:

    def test_add_transaction_persists_transaction(self, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one spend transaction
        session_repository = _InMemorySessionRepository(active_session=active_session)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        transaction = service.add_transaction(amount=Decimal("25.50"), description="Coffee and notes", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 11))

        assert len(transaction_repository.transactions) == 1
        assert transaction_repository.transactions[0] == transaction
        assert transaction.session_id == active_session.session_id
        assert transaction.amount == Decimal("25.50")
        assert transaction.description == "Coffee and notes"
        assert transaction.category is TransactionCategory.FOOD
        assert transaction.date == date(2026, 4, 11)

    def test_add_transaction_rejects_without_active_session(self) -> None:
        # service must fail fast if spend is logged before a session is started
        session_repository = _InMemorySessionRepository(active_session=None)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        with pytest.raises(ApplicationError):
            service.add_transaction(amount=Decimal("12.00"), description="Bus", category=TransactionCategory.TRANSPORT, spent_on=date(2026, 4, 12))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount — validation error",),  # zero spend is not a valid outflow amount
            pytest.param(Decimal("-1.00"), id="negative amount — validation error",),  # spend values are stored as positive numbers by convention
        ],
    )
    def test_add_transaction_rejects_non_positive_amount(self, active_session: AppSession, amount: Decimal) -> None:
        # spend entries must always be positive amounts by project money convention
        session_repository = _InMemorySessionRepository(active_session=active_session)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=amount, description="Lunch", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 12))

    def test_add_transaction_rejects_blank_description(self, active_session: AppSession) -> None:
        # blank descriptions create unusable spend records and are not allowed
        session_repository = _InMemorySessionRepository(active_session=active_session)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="   ", category=TransactionCategory.FOOD, spent_on=date(2026, 4, 12))

    def test_add_transaction_rejects_invalid_category_type(self, active_session: AppSession) -> None:
        # category must be a TransactionCategory enum or None
        session_repository = _InMemorySessionRepository(active_session=active_session)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="Snacks", category="food", spent_on=date(2026, 4, 12))  # type: ignore[arg-type]

    def test_add_transaction_rejects_invalid_date_type(self, active_session: AppSession) -> None:
        # transaction date must be a real date object so monthly filtering remains correct
        session_repository = _InMemorySessionRepository(active_session=active_session)
        transaction_repository = _InMemoryTransactionRepository()
        service = SpendService(session_repository=session_repository, transaction_repository=transaction_repository)

        with pytest.raises(ValidationError):
            service.add_transaction(amount=Decimal("8.50"), description="Snacks", category=TransactionCategory.FOOD, spent_on="2026-04-12")  # type: ignore[arg-type]

