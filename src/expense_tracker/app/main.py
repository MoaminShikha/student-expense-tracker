from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Sequence
from decimal import Decimal

from ..infrastructure.logging_config import LoggerFactory
from ..shared.exceptions import ExpenseTrackerError
from .cli import CliApplication
from .composition import build_services

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

            services = build_services(_DATA_DIR, logger=logger)

            cli_application = CliApplication(
                services.session_service,
                services.balance_service,
                services.income_service,
                services.charge_service,
                services.fuzzy_charge_service,
                services.spend_service,
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
