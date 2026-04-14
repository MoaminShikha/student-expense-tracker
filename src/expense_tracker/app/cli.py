from __future__ import annotations

import logging
from typing import Sequence

from ..application.services import SessionService
from ..domain.validators import parse_opening_balance
from ..shared.exceptions import ApplicationError, ValidationError


class CliApplication:
    """Routes supported Stage 1 CLI commands."""

    def __init__(self, session_service: SessionService) -> None:
        """
        Initialize command routing dependencies.

        :param session_service: Service for session-related commands.
        :return: None.
        """
        self._session_service = session_service
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

