from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from expense_tracker.infrastructure.logging_config import LoggerFactory
from expense_tracker.shared.exceptions import (
    ApplicationError,
    ExpenseTrackerError,
    LoggingConfigurationError,
    ValidationError,
)


class TestExceptionHierarchy:

    def test_validation_error_is_expense_tracker_error(self) -> None:
        # ValidationError must be catchable as the base project error
        assert issubclass(ValidationError, ExpenseTrackerError)

    def test_application_error_is_expense_tracker_error(self) -> None:
        # ApplicationError must be catchable as the base project error
        assert issubclass(ApplicationError, ExpenseTrackerError)

    def test_logging_configuration_error_is_expense_tracker_error(self) -> None:
        # LoggingConfigurationError must be catchable as the base project error
        assert issubclass(LoggingConfigurationError, ExpenseTrackerError)

    def test_validation_error_is_value_error(self) -> None:
        # ValidationError inherits ValueError so callers using stdlib error handling still catch it
        assert issubclass(ValidationError, ValueError)


class TestLoggerFactory:

    def test_returns_named_logger(self) -> None:
        # default name is "expense_tracker" when no name is passed
        factory = LoggerFactory(level=logging.DEBUG)
        factory.configure()
        logger = factory.get_logger()
        assert logger.name == "expense_tracker"

    def test_marks_configured_after_first_call(self) -> None:
        # _configured flag prevents basicConfig from being called twice
        factory = LoggerFactory()
        factory.configure()
        assert factory._configured is True

    def test_configure_is_idempotent(self) -> None:
        # calling configure() twice must not raise or reconfigure logging
        factory = LoggerFactory()
        factory.configure()
        factory.configure()  # second call must be a no-op

    def test_wraps_configuration_errors_as_logging_configuration_error(self) -> None:
        # infrastructure failures in basicConfig must surface as a typed project error
        factory = LoggerFactory()
        with patch("logging.basicConfig", side_effect=RuntimeError("boom")):
            with pytest.raises(LoggingConfigurationError):
                factory.configure()
