from __future__ import annotations

import logging
from typing import Sequence

from ..application.services import BalanceService, ChargeService, IncomeService, SessionService
from ..domain.validators import parse_amount, parse_day_of_month, parse_due_date, parse_income_source_tag, parse_opening_balance
from ..shared.exceptions import ApplicationError, ValidationError


class CliApplication:
    """Routes supported Stage 1 CLI commands."""

    def __init__(self, session_service: SessionService, balance_service: BalanceService, income_service: IncomeService, charge_service: ChargeService) -> None:
        """
        Initialize command routing dependencies.

        :param session_service: Service for session-related commands.
        :param balance_service: Service for dashboard balance commands.
        :param income_service: Service for income commands.
        :param charge_service: Service for charge commands.
        :return: None.
        """
        self._session_service = session_service
        self._balance_service = balance_service
        self._income_service = income_service
        self._charge_service = charge_service
        self._logger = logging.getLogger(__name__)

    def run(self, arguments: Sequence[str]) -> int:
        """
        Route top-level command-line arguments.

        :param arguments: Arguments passed to the CLI.
        :return: Process exit code.
        """
        if not arguments:
            self._logger.error("No command provided.")
            return 1

        if arguments[0] == "session" and len(arguments) > 1 and arguments[1] == "init":
            return self.handle_session_init(arguments[2:])

        if arguments[0] == "dashboard" and len(arguments) > 1 and arguments[1] == "show":
            return self.handle_dashboard_show(arguments[2:])

        if arguments[0] == "income" and len(arguments) > 1 and arguments[1] == "add":
            return self.handle_income_add(arguments[2:])

        if arguments[0] == "charge" and len(arguments) > 1 and arguments[1] == "add":
            return self.handle_charge_add(arguments[2:])

        self._logger.error("Unknown command: %s", " ".join(arguments))
        return 1

    def handle_session_init(self, arguments: Sequence[str]) -> int:
        """
        Handle the `session init` command flow.

        :param arguments: Arguments specific to session initialization.
        :return: Process exit code.
        """
        raw_balance: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--balance" and index + 1 < len(arguments):
                raw_balance = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_balance is None:
            self._logger.error("Missing required argument: --balance")
            return 1

        try:
            opening_balance = parse_opening_balance(raw_balance)
            self._session_service.init_session(opening_balance)
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Session initialized successfully.")
        return 0

    def handle_dashboard_show(self, arguments: Sequence[str]) -> int:
        """
        Handle the `dashboard show` command flow.

        `dashboard show` accepts no arguments — all data is fetched from the
        repository layer through the service layer. Manual argument passing is
        not permitted; it would bypass the data layer entirely.

        # TODO Phase D: inject income, charge, and transaction repositories into
        # CliApplication; delegate aggregation to a DashboardService (or extend
        # SessionService) that queries the repos, sums the totals, and calls
        # BalanceService.build_snapshot. Print the returned BalanceSnapshot here.

        :param arguments: Arguments passed after `dashboard show` (must be empty).
        :return: Process exit code.
        """
        if arguments:
            self._logger.error("dashboard show accepts no arguments. Data is fetched from the repository layer.")
            return 1

        self._logger.error("dashboard show is not yet available — repository layer not wired (Phase D).")
        return 1

    def handle_income_add(self, arguments: Sequence[str]) -> int:
        """
        Handle the `income add` command flow.

        :param arguments: Arguments specific to adding income.
        :return: Process exit code.
        """
        raw_amount: str | None = None
        raw_source: str | None = None
        raw_date: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--amount" and index + 1 < len(arguments):
                raw_amount = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--source" and index + 1 < len(arguments):
                raw_source = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--date" and index + 1 < len(arguments):
                raw_date = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_amount is None:
            self._logger.error("Missing required argument: --amount")
            return 1

        if raw_source is None:
            self._logger.error("Missing required argument: --source")
            return 1

        if raw_date is None:
            self._logger.error("Missing required argument: --date")
            return 1

        try:
            amount = parse_amount(raw_amount)
            source_tag = parse_income_source_tag(raw_source)
            entry_date = parse_due_date(raw_date)
            self._income_service.add_income(amount, source_tag, entry_date)
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Income entry added successfully.")
        return 0

    def handle_charge_add(self, arguments: Sequence[str]) -> int:
        """
        Handle the `charge add` command flow.

        :param arguments: Arguments specific to adding a committed charge.
        :return: Process exit code.
        """
        raw_name: str | None = None
        raw_amount: str | None = None
        raw_due_date: str | None = None
        raw_day_of_month: str | None = None
        recurring = False
        index = 0

        while index < len(arguments):
            if arguments[index] == "--recurring":
                recurring = True
                index += 1
                continue

            if arguments[index] == "--name" and index + 1 < len(arguments):
                raw_name = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--amount" and index + 1 < len(arguments):
                raw_amount = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--due-date" and index + 1 < len(arguments):
                raw_due_date = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--day-of-month" and index + 1 < len(arguments):
                raw_day_of_month = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_name is None:
            self._logger.error("Missing required argument: --name")
            return 1

        if raw_amount is None:
            self._logger.error("Missing required argument: --amount")
            return 1

        if not recurring and raw_due_date is None:
            self._logger.error("Missing required argument: --due-date")
            return 1

        if recurring and raw_day_of_month is None:
            self._logger.error("Missing required argument: --day-of-month")
            return 1

        try:
            amount = parse_amount(raw_amount)
            if recurring:
                day_of_month = parse_day_of_month(raw_day_of_month or "")
                self._charge_service.add_recurring_charge(raw_name, amount, day_of_month)
            else:
                assert raw_due_date is not None
                due_date = parse_due_date(raw_due_date)
                self._charge_service.add_charge(raw_name, amount, due_date)
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Recurring charge added successfully." if recurring else "Charge entry added successfully.")
        return 0

