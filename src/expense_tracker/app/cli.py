from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Protocol, Sequence
from uuid import UUID

from ..application.services import BalanceService, ChargeService, FuzzyChargeService, IncomeService, SessionService, SpendService
from ..domain.validators import parse_amount, parse_day_of_month, parse_due_date, parse_income_source_tag, parse_opening_balance, parse_transaction_category
from ..shared.exceptions import ApplicationError, ValidationError


class CliApplication:
    """Routes supported Stage 1 CLI commands."""

    def __init__(self, session_service: SessionService, balance_service: BalanceService, income_service: IncomeService, charge_service: ChargeService, fuzzy_charge_service: FuzzyChargeService, spend_service: SpendService, session_repository: Protocol, income_repository: Protocol, charge_repository: Protocol, transaction_repository: Protocol) -> None:
        """
        Initialize command routing dependencies.

        :param session_service: Service for session-related commands.
        :param balance_service: Service for dashboard balance commands.
        :param income_service: Service for income commands.
        :param charge_service: Service for charge commands.
        :param fuzzy_charge_service: Service for fuzzy-charge commands.
        :param spend_service: Service for spend commands.
        :param session_repository: Session persistence adapter.
        :param income_repository: Income persistence adapter.
        :param charge_repository: Charge persistence adapter.
        :param transaction_repository: Transaction persistence adapter.
        :return: None.
        """
        self._session_service = session_service
        self._balance_service = balance_service
        self._income_service = income_service
        self._charge_service = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._spend_service = spend_service
        self._session_repository = session_repository
        self._income_repository = income_repository
        self._charge_repository = charge_repository
        self._transaction_repository = transaction_repository
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

        if arguments[0] == "charge" and len(arguments) > 1 and arguments[1] == "mark-paid":
            return self.handle_charge_mark_paid(arguments[2:])

        if arguments[0] == "fuzzy-charge" and len(arguments) > 1 and arguments[1] == "add":
            return self.handle_fuzzy_charge_add(arguments[2:])

        if arguments[0] == "fuzzy-charge" and len(arguments) > 1 and arguments[1] == "resolve":
            return self.handle_fuzzy_charge_resolve(arguments[2:])

        if arguments[0] == "fuzzy-charge" and len(arguments) > 1 and arguments[1] == "discard":
            return self.handle_fuzzy_charge_discard(arguments[2:])

        if arguments[0] == "spend" and len(arguments) > 1 and arguments[1] == "add":
            return self.handle_spend_add(arguments[2:])

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
        repository layer through the service layer via aggregation.

        :param arguments: Arguments passed after `dashboard show` (must be empty).
        :return: Process exit code.
        """
        if arguments:
            self._logger.error("dashboard show accepts no arguments. Data is fetched from the repository layer.")
            return 1

        try:
            active_session = self._session_service.get_active()
            if active_session is None:
                self._logger.error("No active session. Initialize one with: session init --balance <amount>")
                return 1

            caution_threshold = Decimal("100")
            snapshot = self._balance_service.aggregate_and_build_snapshot(active_session.session_id, self._income_repository, self._charge_repository, self._transaction_repository, caution_threshold, active_session.opening_balance)

            self._logger.info("Dashboard snapshot: free_money=%s monthly_budget=%s monthly_spent=%s monthly_left=%s on_track_state=%s balance_state=%s", snapshot.free_money, snapshot.monthly_budget, snapshot.monthly_spent, snapshot.monthly_left, snapshot.on_track_state.value, snapshot.balance_state.value)
            return 0
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
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

    def handle_fuzzy_charge_add(self, arguments: Sequence[str]) -> int:
        """
        Handle the `fuzzy-charge add` command flow.

        :param arguments: Arguments specific to adding a fuzzy charge.
        :return: Process exit code.
        """
        raw_name: str | None = None
        raw_due_date: str | None = None
        raw_estimate: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--name" and index + 1 < len(arguments):
                raw_name = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--due-date" and index + 1 < len(arguments):
                raw_due_date = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--estimate" and index + 1 < len(arguments):
                raw_estimate = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_name is None:
            self._logger.error("Missing required argument: --name")
            return 1

        if raw_due_date is None:
            self._logger.error("Missing required argument: --due-date")
            return 1

        try:
            expected_date = parse_due_date(raw_due_date)
            estimated_amount = parse_amount(raw_estimate) if raw_estimate is not None else None
            self._fuzzy_charge_service.add_fuzzy_charge(raw_name, expected_date, estimated_amount)
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Fuzzy charge added successfully.")
        return 0

    def handle_fuzzy_charge_resolve(self, arguments: Sequence[str]) -> int:
        """
        Handle the `fuzzy-charge resolve` command flow.

        :param arguments: Arguments specific to resolving a fuzzy charge.
        :return: Process exit code.
        """
        raw_id: str | None = None
        raw_amount: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--id" and index + 1 < len(arguments):
                raw_id = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--amount" and index + 1 < len(arguments):
                raw_amount = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_id is None:
            self._logger.error("Missing required argument: --id")
            return 1

        if raw_amount is None:
            self._logger.error("Missing required argument: --amount")
            return 1

        try:
            fuzzy_id = UUID(raw_id)
            resolved_amount = parse_amount(raw_amount)
            self._fuzzy_charge_service.resolve(fuzzy_id, resolved_amount)
        except ValueError:
            self._logger.error("Fuzzy entry identifier must be a valid UUID.")
            return 1
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Fuzzy charge resolved successfully.")
        return 0

    def handle_fuzzy_charge_discard(self, arguments: Sequence[str]) -> int:
        """
        Handle the `fuzzy-charge discard` command flow.

        :param arguments: Arguments specific to discarding a fuzzy charge.
        :return: Process exit code.
        """
        raw_id: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--id" and index + 1 < len(arguments):
                raw_id = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_id is None:
            self._logger.error("Missing required argument: --id")
            return 1

        try:
            fuzzy_id = UUID(raw_id)
            self._fuzzy_charge_service.discard(fuzzy_id)
        except ValueError:
            self._logger.error("Fuzzy entry identifier must be a valid UUID.")
            return 1
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Fuzzy charge discarded successfully.")
        return 0

    def handle_spend_add(self, arguments: Sequence[str]) -> int:
        """
        Handle the `spend add` command flow.

        :param arguments: Arguments specific to adding a spend transaction.
        :return: Process exit code.
        """
        raw_amount: str | None = None
        raw_description: str | None = None
        raw_category: str | None = None
        raw_date: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--amount" and index + 1 < len(arguments):
                raw_amount = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--description" and index + 1 < len(arguments):
                raw_description = arguments[index + 1]
                index += 2
                continue

            if arguments[index] == "--category" and index + 1 < len(arguments):
                raw_category = arguments[index + 1]
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

        if raw_description is None:
            self._logger.error("Missing required argument: --description")
            return 1

        try:
            amount = parse_amount(raw_amount)
            category = parse_transaction_category(raw_category)
            spent_on = parse_due_date(raw_date) if raw_date is not None else date.today()
            self._spend_service.add_transaction(amount, raw_description, category, spent_on)
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Spend transaction added successfully.")
        return 0

    def handle_charge_mark_paid(self, arguments: Sequence[str]) -> int:
        """
        Handle the `charge mark-paid` command flow.

        :param arguments: Arguments specific to marking a charge as paid.
        :return: Process exit code.
        """
        raw_id: str | None = None
        index = 0

        while index < len(arguments):
            if arguments[index] == "--id" and index + 1 < len(arguments):
                raw_id = arguments[index + 1]
                index += 2
                continue

            self._logger.error("Unsupported argument: %s", arguments[index])
            return 1

        if raw_id is None:
            self._logger.error("Missing required argument: --id")
            return 1

        try:
            charge_id = UUID(raw_id)
            self._charge_service.mark_paid(charge_id)
        except ValueError:
            self._logger.error("Charge identifier must be a valid UUID.")
            return 1
        except (ValidationError, ApplicationError) as exc:
            self._logger.error(str(exc))
            return 1

        self._logger.info("Charge marked as paid successfully.")
        return 0

