from __future__ import annotations

import logging
from pathlib import Path
from typing import NamedTuple

from ..application.calculations import BalanceEngine
from ..application.services import (
    BalanceService,
    ChargeService,
    FuzzyChargeService,
    IncomeService,
    SessionService,
    SpendService,
)
from ..infrastructure.json.repositories import (
    JsonChargeRepository,
    JsonFuzzyChargeRepository,
    JsonIncomeRepository,
    JsonRecurringRuleRepository,
    JsonSessionRepository,
    JsonTransactionRepository,
)


class Services(NamedTuple):
    session_service: SessionService
    income_service: IncomeService
    charge_service: ChargeService
    fuzzy_charge_service: FuzzyChargeService
    spend_service: SpendService
    balance_service: BalanceService


def build_services(data_dir: Path, logger: logging.Logger | None = None) -> Services:
    """
    Wire repositories and services against the JSON files in ``data_dir``.

    :param data_dir: Directory holding the application's JSON data files.
    :param logger: Optional logger injected into every service.
    :return: A :class:`Services` container with all services constructed.
    """
    session_repository = JsonSessionRepository(data_dir / "session.json")
    income_repository = JsonIncomeRepository(data_dir / "income.json")
    charge_repository = JsonChargeRepository(data_dir / "charges.json")
    recurring_rule_repository = JsonRecurringRuleRepository(data_dir / "recurring_rules.json")
    fuzzy_charge_repository = JsonFuzzyChargeRepository(data_dir / "fuzzy_charges.json")
    transaction_repository = JsonTransactionRepository(data_dir / "transactions.json")

    return Services(
        session_service=SessionService(session_repository, logger=logger),
        income_service=IncomeService(session_repository, income_repository, logger=logger),
        charge_service=ChargeService(session_repository, charge_repository, recurring_rule_repository, logger=logger),
        fuzzy_charge_service=FuzzyChargeService(
            session_repository, fuzzy_charge_repository, charge_repository, income_repository, logger=logger
        ),
        spend_service=SpendService(session_repository, transaction_repository, logger=logger),
        balance_service=BalanceService(
            BalanceEngine(), income_repository, charge_repository, transaction_repository, logger=logger
        ),
    )
