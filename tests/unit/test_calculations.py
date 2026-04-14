from __future__ import annotations

from decimal import Decimal
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from expense_tracker.application.calculations import BalanceEngine, BalanceState, OnTrackState


# Section: calculate_free_money
@pytest.mark.parametrize(
    "opening_balance,total_income,total_committed,total_spent,expected",
    [
        (Decimal("1000"), Decimal("1200"), Decimal("900"), Decimal("450"), Decimal("850")),  # > 0
        (Decimal("100"), Decimal("50"), Decimal("120"), Decimal("30"), Decimal("0")),  # == 0 boundary
        (Decimal("0"), Decimal("20"), Decimal("15"), Decimal("10"), Decimal("-5")),  # < 0
        (Decimal("10.25"), Decimal("2.75"), Decimal("5.50"), Decimal("1.00"), Decimal("6.50")),  # decimal precision check
    ],
)
def test_calculate_free_money(opening_balance: Decimal, total_income: Decimal, total_committed: Decimal,
                              total_spent: Decimal, expected: Decimal) -> None:
    engine = BalanceEngine()
    result = engine.calculate_free_money(opening_balance, total_income, total_committed, total_spent)
    assert result == expected

# ---------------------------------------------------------------------------------------------------------------------

# Section: classify_balance_state
@pytest.mark.parametrize(
    "free_money,caution_threshold,expected",
    [
        (Decimal("150"), Decimal("100"), BalanceState.NORMAL),  # > caution threshold
        (Decimal("100"), Decimal("100"), BalanceState.CAUTION),  # == caution threshold boundary
        (Decimal("1"), Decimal("100"), BalanceState.CAUTION),  # 0 < free money <= caution threshold
        (Decimal("0"), Decimal("100"), BalanceState.CRISIS),  # == 0 boundary
        (Decimal("-1"), Decimal("100"), BalanceState.CRISIS),  # < 0 boundary
    ],
)
def test_classify_balance_state(free_money: Decimal, caution_threshold: Decimal, expected: BalanceState) -> None:
    engine = BalanceEngine()
    result = engine.classify_balance_state(free_money, caution_threshold)
    assert result is expected

# ---------------------------------------------------------------------------------------------------------------------


# Section: classify_on_track_state
@pytest.mark.parametrize(
    "monthly_budget,monthly_spent,red_threshold,expected",
    [
        (Decimal("1000"), Decimal("850"), Decimal("130"), OnTrackState.GREEN),  # < 100%
        (Decimal("1000"), Decimal("1000"), Decimal("130"), OnTrackState.YELLOW),  # == 100% boundary
        (Decimal("1000"), Decimal("1200"), Decimal("130"), OnTrackState.YELLOW),  # 100% <= pct < red threshold
        (Decimal("1000"), Decimal("1300"), Decimal("130"), OnTrackState.RED),  # == red threshold boundary
        (Decimal("1000"), Decimal("1400"), Decimal("130"), OnTrackState.RED),  # > red threshold
        (Decimal("0"), Decimal("50"), Decimal("130"), OnTrackState.TIGHT_MONTH),  # monthly_budget == 0
        (Decimal("-10"), Decimal("50"), Decimal("130"), OnTrackState.TIGHT_MONTH),  # monthly_budget < 0
    ],
)
def test_classify_on_track_state(monthly_budget: Decimal, monthly_spent: Decimal, red_threshold: Decimal, expected: OnTrackState) -> None:
    engine = BalanceEngine()
    result = engine.classify_on_track_state(monthly_budget, monthly_spent, red_threshold)
    assert result is expected


# ---------------------------------------------------------------------------------------------------------------------
