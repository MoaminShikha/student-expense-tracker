from __future__ import annotations

import logging
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from expense_tracker.infrastructure.logging_config import LoggerFactory
from expense_tracker.shared.exceptions import ApplicationError, ExpenseTrackerError, LoggingConfigurationError, ValidationError


class SharedCrossCuttingTests(TestCase):
    def test_exception_hierarchy(self) -> None:
        self.assertTrue(issubclass(ValidationError, ExpenseTrackerError))
        self.assertTrue(issubclass(ApplicationError, ExpenseTrackerError))
        self.assertTrue(issubclass(LoggingConfigurationError, ExpenseTrackerError))
        self.assertTrue(issubclass(ValidationError, ValueError))

    def test_logger_factory_returns_named_logger(self) -> None:
        factory = LoggerFactory(level=logging.DEBUG)
        factory.configure()
        logger = factory.get_logger()
        self.assertEqual(logger.name, "expense_tracker")
        self.assertTrue(factory._configured)

    def test_logger_factory_wraps_configuration_errors(self) -> None:
        factory = LoggerFactory()
        with patch("logging.basicConfig", side_effect=RuntimeError("boom")):
            with self.assertRaises(LoggingConfigurationError):
                factory.configure()

