from __future__ import annotations


class ExpenseTrackerError(Exception):
	"""Base class for all project-wide errors."""


class ValidationError(ExpenseTrackerError, ValueError):
	"""Raised when user input fails validation."""


class ApplicationError(ExpenseTrackerError):
	"""Raised when an application use case cannot complete."""


class InfrastructureError(ExpenseTrackerError):
	"""Raised when infrastructure services fail."""


class LoggingConfigurationError(ExpenseTrackerError):
	"""Raised when logging setup fails."""

