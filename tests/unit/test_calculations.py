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


# Section: calculate_monthly_budget
@pytest.mark.parametrize(
    "income_this_month,charges_this_month,spent_this_month,red_threshold,expected_budget,expected_spent,expected_left,expected_state",
    [
        (Decimal("1000"), Decimal("300"), Decimal("350"), Decimal("130"), Decimal("700"), Decimal("350"), Decimal("350"),
         OnTrackState.GREEN),  # under budget
        (Decimal("1000"), Decimal("300"), Decimal("700"), Decimal("130"), Decimal("700"), Decimal("700"), Decimal("0"),
         OnTrackState.YELLOW),  # exactly 100%
        (Decimal("1000"), Decimal("300"), Decimal("1000"), Decimal("130"), Decimal("700"), Decimal("1000"), Decimal("-300"),
         OnTrackState.RED),  # above red threshold
        (Decimal("300"), Decimal("300"), Decimal("50"), Decimal("130"), Decimal("0"), Decimal("50"), Decimal("-50"),
         OnTrackState.TIGHT_MONTH),  # zero monthly budget
    ],
)
def test_calculate_monthly_budget(income_this_month: Decimal, charges_this_month: Decimal, spent_this_month: Decimal,
                                  red_threshold: Decimal, expected_budget: Decimal, expected_spent: Decimal,
                                  expected_left: Decimal, expected_state: OnTrackState) -> None:
    engine = BalanceEngine()
    result = engine.calculate_monthly_budget(income_this_month, charges_this_month, spent_this_month, red_threshold)
    assert result.monthly_budget == expected_budget
    assert result.monthly_spent == expected_spent
    assert result.monthly_left == expected_left
    assert result.on_track_state is expected_state


# ---------------------------------------------------------------------------------------------------------------------


# Section: build_snapshot
def test_build_snapshot_composes_all_outputs() -> None:
    engine = BalanceEngine()
    result = engine.build_snapshot(
        opening_balance=Decimal("1000"),
        total_income=Decimal("1200"),
        total_committed=Decimal("900"),
        total_spent=Decimal("450"),
        income_this_month=Decimal("1000"),
        charges_this_month=Decimal("300"),
        spent_this_month=Decimal("350"),
        caution_threshold=Decimal("100"),
        red_threshold=Decimal("130"),
    )
    assert result.free_money == Decimal("850")
    assert result.monthly_budget == Decimal("700")
    assert result.monthly_spent == Decimal("350")
    assert result.monthly_left == Decimal("350")
    assert result.on_track_state is OnTrackState.GREEN
    assert result.balance_state is BalanceState.NORMAL


def test_build_snapshot_uses_tight_month_and_crisis_states() -> None:
    engine = BalanceEngine()
    result = engine.build_snapshot(
        opening_balance=Decimal("100"),
        total_income=Decimal("50"),
        total_committed=Decimal("120"),
        total_spent=Decimal("30"),
        income_this_month=Decimal("300"),
        charges_this_month=Decimal("300"),
        spent_this_month=Decimal("50"),
        caution_threshold=Decimal("100"),
        red_threshold=Decimal("130"),
    )
    assert result.free_money == Decimal("0")
    assert result.monthly_budget == Decimal("0")
    assert result.monthly_spent == Decimal("50")
    assert result.monthly_left == Decimal("-50")
    assert result.on_track_state is OnTrackState.TIGHT_MONTH
    assert result.balance_state is BalanceState.CRISIS


# ---------------------------------------------------------------------------------------------------------------------


