from __future__ import annotations

import logging
import sys
from typing import Sequence
from uuid import UUID

from ..application.calculations import BalanceEngine
from ..application.services import BalanceService, IncomeService, SessionService
from ..domain.models import AppSession, IncomeEntry
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
            session_service = SessionService(session_repository, logger=logger)
            income_service = IncomeService(session_repository, income_repository, logger=logger)
            balance_engine = BalanceEngine()
            balance_service = BalanceService(balance_engine, logger=logger)
            cli_application = CliApplication(session_service, balance_service, income_service)
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


