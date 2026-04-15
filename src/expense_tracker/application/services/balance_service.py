from __future__ import annotations

import logging
from decimal import Decimal

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
