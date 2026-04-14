from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import Sequence

from ..application.services import SessionService
from ..domain.models import AppSession
from ..infrastructure.logging_config import LoggerFactory
from ..shared.exceptions import ExpenseTrackerError
from .cli import CliApplication


@dataclass
class _InMemorySessionRepository:
    """Simple repository used to bootstrap the Stage 1 CLI flow."""

    _active_session: AppSession | None = None

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
            session_service = SessionService(session_repository, logger=logger)
            cli_application = CliApplication(session_service)
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


