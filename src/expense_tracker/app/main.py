from __future__ import annotations

import logging
import sys
from typing import Sequence
from uuid import UUID

from ..application.calculations import BalanceEngine
from ..application.services import BalanceService, ChargeService, FuzzyChargeService, IncomeService, SessionService, SpendService
from ..domain.models import AppSession, ChargeStatus, CommittedCharge, FuzzyCharge, FuzzyChargeStatus, IncomeEntry, RecurringRule, Transaction
from ..infrastructure.logging_config import LoggerFactory
from ..shared.exceptions import ExpenseTrackerError
from .cli import CliApplication


class _InMemorySessionRepository:
    """Simple in-process repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._active_session: AppSession | None = None

    def create(self, session: AppSession) -> None:
        """
        Persist a new active session.

        :param session: Session to persist.
        :return: None.
        """
        self._active_session = session

    def get_active(self) -> AppSession | None:
        """
        Fetch the currently active session.

        :return: Active session if present; otherwise None.
        """
        return self._active_session


class _InMemoryIncomeRepository:
    """Simple in-process income repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._entries: list[IncomeEntry] = []

    def add(self, entry: IncomeEntry) -> None:
        """
        Persist one income entry.

        :param entry: Income entry to persist.
        :return: None.
        """
        self._entries.append(entry)

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        """
        List income entries for one session.

        :param session_id: Session identifier.
        :return: Session income entries.
        """
        return [entry for entry in self._entries if entry.session_id == session_id]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        """
        List income entries for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Monthly income entries.
        """
        return [entry for entry in self._entries if entry.session_id == session_id and entry.date.year == year and entry.date.month == month]


class _InMemoryChargeRepository:
    """Simple in-process charge repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._charges: dict[UUID, CommittedCharge] = {}

    def add(self, charge: CommittedCharge) -> None:
        """
        Persist one committed charge.

        :param charge: Charge to persist.
        :return: None.
        """
        self._charges[charge.charge_id] = charge

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        """
        List upcoming charges for one session.

        :param session_id: Session identifier.
        :return: Upcoming committed charges.
        """
        return [charge for charge in self._charges.values() if charge.session_id == session_id and charge.status == ChargeStatus.UPCOMING]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        """
        List committed charges for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Monthly committed charges.
        """
        return [charge for charge in self._charges.values() if charge.session_id == session_id and charge.due_date.year == year and charge.due_date.month == month]

    def mark_paid(self, charge_id: UUID) -> None:
        """
        Mark one committed charge as paid.

        :param charge_id: Charge identifier.
        :return: None.
        """
        charge = self._charges.get(charge_id)
        if charge is not None:
            self._charges[charge_id] = CommittedCharge(charge_id=charge.charge_id, session_id=charge.session_id, name=charge.name, amount=charge.amount, due_date=charge.due_date, status=ChargeStatus.PAID, recurring_rule_id=charge.recurring_rule_id)

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        """
        Fetch one committed charge by identifier.

        :param charge_id: Charge identifier.
        :return: Matching committed charge if present; otherwise None.
        """
        return self._charges.get(charge_id)


class _InMemoryRecurringRuleRepository:
    """Simple in-process recurring-rule repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._rules: dict[UUID, RecurringRule] = {}

    def add(self, rule: RecurringRule) -> None:
        """
        Persist one recurring rule.

        :param rule: Rule to persist.
        :return: None.
        """
        self._rules[rule.rule_id] = rule

    def get_by_id(self, rule_id: UUID) -> RecurringRule | None:
        """
        Fetch one recurring rule by identifier.

        :param rule_id: Rule identifier.
        :return: Matching recurring rule if present; otherwise None.
        """
        return self._rules.get(rule_id)

    def list_for_session(self, session_id: UUID) -> list[RecurringRule]:
        """
        List recurring rules for one session.

        :param session_id: Session identifier.
        :return: Recurring rules for the session.
        """
        return [rule for rule in self._rules.values() if rule.session_id == session_id]


class _InMemoryFuzzyChargeRepository:
    """Simple in-process fuzzy repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._entries: dict[UUID, FuzzyCharge] = {}

    def add(self, charge: FuzzyCharge) -> None:
        """
        Persist one fuzzy entry.

        :param charge: Fuzzy entry to persist.
        :return: None.
        """
        self._entries[charge.fuzzy_id] = charge


class _InMemoryTransactionRepository:
    """Simple in-process transaction repository used to bootstrap the Stage 1 CLI flow."""

    def __init__(self) -> None:
        self._transactions: list[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        """
        Persist one spend transaction.

        :param transaction: Spend transaction to persist.
        :return: None.
        """
        self._transactions.append(transaction)

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        """
        List spend transactions for one calendar month.

        :param session_id: Session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Monthly spend transactions.
        """
        return [transaction for transaction in self._transactions if transaction.session_id == session_id and transaction.date.year == year and transaction.date.month == month]

    def get_by_id(self, fuzzy_id: UUID) -> FuzzyCharge | None:
        """
        Fetch one fuzzy entry by identifier.

        :param fuzzy_id: Fuzzy entry identifier.
        :return: Matching fuzzy entry if present; otherwise None.
        """
        return self._entries.get(fuzzy_id)

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        """
        List pending fuzzy entries for one session.

        :param session_id: Session identifier.
        :return: Pending fuzzy entries for the session.
        """
        return [entry for entry in self._entries.values() if entry.session_id == session_id and entry.status == FuzzyChargeStatus.PENDING]

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        """
        Update one fuzzy entry status.

        :param fuzzy_id: Fuzzy entry identifier.
        :param status: New status value.
        :return: None.
        """
        existing = self._entries.get(fuzzy_id)
        if existing is not None:
            self._entries[fuzzy_id] = FuzzyCharge(fuzzy_id=existing.fuzzy_id, session_id=existing.session_id, name=existing.name, direction=existing.direction, status=status, expected_date=existing.expected_date, estimated_amount=existing.estimated_amount, resolved_amount=existing.resolved_amount, resolved_date=existing.resolved_date)

    def update(self, charge: FuzzyCharge) -> None:
        """
        Persist a full fuzzy entry replacement.

        :param charge: Updated fuzzy entry.
        :return: None.
        """
        self._entries[charge.fuzzy_id] = charge


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

            session_repository = _InMemorySessionRepository()
            income_repository = _InMemoryIncomeRepository()
            charge_repository = _InMemoryChargeRepository()
            recurring_rule_repository = _InMemoryRecurringRuleRepository()
            fuzzy_charge_repository = _InMemoryFuzzyChargeRepository()
            transaction_repository = _InMemoryTransactionRepository()
            session_service = SessionService(session_repository, logger=logger)
            income_service = IncomeService(session_repository, income_repository, logger=logger)
            charge_service = ChargeService(session_repository, charge_repository, recurring_rule_repository, logger=logger)
            fuzzy_charge_service = FuzzyChargeService(session_repository, fuzzy_charge_repository, charge_repository, income_repository, logger=logger)
            spend_service = SpendService(session_repository, transaction_repository, logger=logger)
            balance_engine = BalanceEngine()
            balance_service = BalanceService(balance_engine, logger=logger)
            cli_application = CliApplication(session_service, balance_service, income_service, charge_service, fuzzy_charge_service, spend_service)
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


