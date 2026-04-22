from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ...domain.models import BalanceSnapshot
from ..calculations import BalanceEngine


class BalanceService:
    """Coordinates balance snapshot calculations for dashboard use cases."""

    def __init__(self, balance_engine: BalanceEngine, logger: logging.Logger | None = None) -> None:
        """
        Initialize the balance service.

        :param balance_engine: Calculation engine for balance outputs.
        :param logger: Optional logger for balance operations.
        :return: None.
        """
        self._balance_engine = balance_engine
        self._logger = logger or logging.getLogger(__name__)

    def build_snapshot(
        self,
        opening_balance: Decimal,
        total_income: Decimal,
        total_committed: Decimal,
        total_spent: Decimal,
        income_this_month: Decimal,
        charges_this_month: Decimal,
        spent_this_month: Decimal,
        caution_threshold: Decimal,
        red_threshold: Decimal = Decimal("130"),
    ) -> BalanceSnapshot:
        """
        Build a dashboard balance snapshot from pre-aggregated totals.

        :param opening_balance: Session opening balance.
        :param total_income: Sum of all logged income.
        :param total_committed: Sum of all committed charges.
        :param total_spent: Sum of all spend transactions.
        :param income_this_month: Sum of income entries in the current calendar month.
        :param charges_this_month: Sum of charges due in the current calendar month.
        :param spent_this_month: Sum of spend transactions in the current calendar month.
        :param caution_threshold: Threshold for caution balance state.
        :param red_threshold: Threshold percentage for red on-track state.
        :return: Computed balance snapshot.
        """
        snapshot = self._balance_engine.build_snapshot(
            opening_balance,
            total_income,
            total_committed,
            total_spent,
            income_this_month,
            charges_this_month,
            spent_this_month,
            caution_threshold,
            red_threshold,
        )
        self._logger.info("Built balance snapshot with free money %s.", snapshot.free_money)
        return snapshot

    def aggregate_and_build_snapshot(self, session_id: UUID, income_repository: Protocol, charge_repository: Protocol, transaction_repository: Protocol, caution_threshold: Decimal, session_opening_balance: Decimal, red_threshold: Decimal = Decimal("130")) -> BalanceSnapshot:
        """
        Fetch all repository data for a session, aggregate totals, and build snapshot.

        :param session_id: Active session identifier.
        :param income_repository: Income persistence adapter.
        :param charge_repository: Charge persistence adapter.
        :param transaction_repository: Transaction persistence adapter.
        :param caution_threshold: Threshold for caution balance state.
        :param session_opening_balance: Session opening balance.
        :param red_threshold: Threshold percentage for red on-track state.
        :return: Computed balance snapshot.
        """
        today = date.today()
        year, month = today.year, today.month

        income_entries = income_repository.list_for_session(session_id)
        all_income = sum((entry.amount for entry in income_entries), Decimal("0"))
        income_this_month = sum((entry.amount for entry in income_repository.list_for_month(session_id, year, month)), Decimal("0"))

        charges = charge_repository.list_upcoming(session_id)
        total_committed = sum((charge.amount for charge in charges), Decimal("0"))
        charges_this_month = sum((charge.amount for charge in charge_repository.list_for_month(session_id, year, month)), Decimal("0"))

        transactions = transaction_repository.list_for_month(session_id, year, month)
        total_spent = sum((tx.amount for tx in transactions), Decimal("0"))
        spent_this_month = total_spent

        snapshot = self.build_snapshot(session_opening_balance, all_income, total_committed, total_spent, income_this_month, charges_this_month, spent_this_month, caution_threshold, red_threshold)
        return snapshot

