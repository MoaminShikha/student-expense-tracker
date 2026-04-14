from __future__ import annotations

import logging

from ..shared.exceptions import LoggingConfigurationError


class LoggerFactory:
    """
    Configures and returns project loggers.
    """

    def __init__(self, level: int = logging.INFO) -> None:
        """
        Initialize the logger factory.

        :param level: Logging level to apply when configuring logging.
        :return: None.
        """
        self._level = level
        self._configured = False

    def configure(self) -> None:
        """
        Configure root logging once.

        :return: None.
        """
        if self._configured:
            return

        try:
            logging.basicConfig(level=self._level, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise LoggingConfigurationError("Unable to configure logging.") from exc

        self._configured = True

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """
        Return a configured logger.

        :param name: Optional logger name.
        :return: Logger instance.
        """
        if not self._configured:
            self.configure()

        return logging.getLogger(name or "expense_tracker")
