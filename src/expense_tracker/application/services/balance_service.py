from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from ...domain.models import BalanceSnapshot, ChargeStatus
from ...ports.repositories import ChargeRepository, IncomeRepository, TransactionRepository
from ..calculations import BalanceEngine


class BalanceService:
    """Coordinates balance snapshot calculations for dashboard use cases."""

    def __init__(
        self,
        balance_engine: BalanceEngine,
        income_repository: IncomeRepository,
        charge_repository: ChargeRepository,
        transaction_repository: TransactionRepository,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the balance service.

        :param balance_engine: Calculation engine for balance outputs.
        :param income_repository: Repository for income entries.
        :param charge_repository: Repository for committed charges.
        :param transaction_repository: Repository for spend transactions.
        :param logger: Optional logger for balance operations.
        :return: None.
        """
        self._balance_engine = balance_engine
        self._income_repository = income_repository
        self._charge_repository = charge_repository
        self._transaction_repository = transaction_repository
        self._logger = logger or logging.getLogger(__name__)

    def aggregate_and_build_snapshot(self, session_id: UUID, caution_threshold: Decimal, session_opening_balance: Decimal, red_threshold: Decimal = Decimal("130")) -> BalanceSnapshot:
        """
        Fetch all repository data for a session, aggregate totals, and build snapshot.

        :param session_id: Active session identifier.
        :param caution_threshold: Threshold for caution balance state.
        :param session_opening_balance: Session opening balance.
        :param red_threshold: Threshold percentage for red on-track state.
        :return: Computed balance snapshot.
        """
        today = date.today()
        year, month = today.year, today.month

        income_entries = self._income_repository.list_for_session(session_id)
        all_income = sum((entry.amount for entry in income_entries), Decimal("0"))
        income_this_month = sum((entry.amount for entry in self._income_repository.list_for_month(session_id, year, month)), Decimal("0"))

        charges = self._charge_repository.list_upcoming(session_id)
        total_committed = sum((charge.amount for charge in charges), Decimal("0"))
        charges_this_month = sum((charge.amount for charge in self._charge_repository.list_for_month(session_id, year, month) if charge.status == ChargeStatus.UPCOMING), Decimal("0"))

        all_transactions = self._transaction_repository.list_for_session(session_id)
        total_spent = sum((tx.amount for tx in all_transactions), Decimal("0"))
        spent_this_month = sum((tx.amount for tx in self._transaction_repository.list_for_month(session_id, year, month)), Decimal("0"))

        snapshot = self._balance_engine.build_snapshot(session_opening_balance, all_income, total_committed, total_spent, income_this_month, charges_this_month, spent_this_month, caution_threshold, red_threshold)
        self._logger.info("Built balance snapshot with free money %s.", snapshot.free_money)
        return snapshot

