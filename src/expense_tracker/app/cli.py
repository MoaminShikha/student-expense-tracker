from __future__ import annotations

from typing import Sequence

from ..application.services import SessionService


class CliApplication:
    """Routes supported Stage 1 CLI commands."""

    def __init__(self, session_service: SessionService) -> None:
        """
        Initialize command routing dependencies.

        :param session_service: Service for session-related commands.
        :return: None.
        """
        pass

    def run(self, arguments: Sequence[str]) -> int:
        """
        Route top-level command-line arguments.

        :param arguments: Arguments passed to the CLI.
        :return: Process exit code.
        """
        pass

    def handle_session_init(self, arguments: Sequence[str]) -> int:
        """
        Handle the `session init` command flow.

        :param arguments: Arguments specific to session initialization.
        :return: Process exit code.
        """
        pass

