from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Sequence
from decimal import Decimal

from ..application.calculations import BalanceEngine
from ..application.services import BalanceService, ChargeService, FuzzyChargeService, IncomeService, SessionService, SpendService
from ..infrastructure.json.repositories import (
    JsonChargeRepository,
    JsonFuzzyChargeRepository,
    JsonIncomeRepository,
    JsonRecurringRuleRepository,
    JsonSessionRepository,
    JsonTransactionRepository,
)
from ..infrastructure.logging_config import LoggerFactory
from ..ports.repositories import ChargeRepository, FuzzyChargeRepository, IncomeRepository, RecurringRuleRepository, SessionRepository, TransactionRepository
from ..shared.exceptions import ExpenseTrackerError
from .cli import CliApplication

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
_CAUTION_THRESHOLD = Decimal("100")


class ApplicationEntryPoint:
    """Bootstraps the command-line application."""

    def run(self, arguments: Sequence[str] | None = None) -> int:
        """
        Start the application lifecycle.

        :param arguments: Optional command-line arguments.
        :return: Process exit code.
        """
        logger_factory = LoggerFactory()
        cli_arguments = list(arguments if arguments is not None else sys.argv[1:])

        try:
            logger_factory.configure()
            logger = logger_factory.get_logger(__name__)
            logger.info("Application started.")

            session_repository: SessionRepository = JsonSessionRepository(_DATA_DIR / "session.json")
            income_repository: IncomeRepository = JsonIncomeRepository(_DATA_DIR / "income.json")
            charge_repository: ChargeRepository = JsonChargeRepository(_DATA_DIR / "charges.json")
            recurring_rule_repository: RecurringRuleRepository = JsonRecurringRuleRepository(_DATA_DIR / "recurring_rules.json")
            fuzzy_charge_repository: FuzzyChargeRepository = JsonFuzzyChargeRepository(_DATA_DIR / "fuzzy_charges.json")
            transaction_repository: TransactionRepository = JsonTransactionRepository(_DATA_DIR / "transactions.json")

            session_service = SessionService(session_repository, logger=logger)
            income_service = IncomeService(session_repository, income_repository, logger=logger)
            charge_service = ChargeService(session_repository, charge_repository, recurring_rule_repository, logger=logger)
            fuzzy_charge_service = FuzzyChargeService(session_repository, fuzzy_charge_repository, charge_repository, income_repository, logger=logger)
            spend_service = SpendService(session_repository, transaction_repository, logger=logger)
            balance_engine = BalanceEngine()
            balance_service = BalanceService(balance_engine, income_repository, charge_repository, transaction_repository, logger=logger)

            cli_application = CliApplication(
                session_service,
                balance_service,
                income_service,
                charge_service,
                fuzzy_charge_service,
                spend_service,
                caution_threshold=_CAUTION_THRESHOLD,
            )
            return cli_application.run(cli_arguments)
        except ExpenseTrackerError as exc:
            logging.getLogger(__name__).error("Application error: %s", exc)
            return 1
        except Exception:  # pragma: no cover - defensive top-level guard
            logging.getLogger(__name__).exception("Unexpected application failure.")
            return 1


def main(arguments: Sequence[str] | None = None) -> int:
    """
    Execute the application entrypoint.

    :param arguments: Optional command-line arguments.
    :return: Process exit code.
    """
    return ApplicationEntryPoint().run(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
