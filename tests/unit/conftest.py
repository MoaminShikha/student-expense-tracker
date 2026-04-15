from __future__ import annotations

import pytest

from expense_tracker.application.calculations import BalanceEngine


@pytest.fixture
def engine() -> BalanceEngine:
    """Provide a shared BalanceEngine instance for all unit tests."""
    return BalanceEngine()

