from __future__ import annotations

from decimal import Decimal

import pytest

from expense_tracker.application.calculations import BalanceEngine
from expense_tracker.domain.models import BalanceState, OnTrackState


class TestCalculateFreeMoney:

    @pytest.mark.parametrize(
        "opening_balance,total_income,total_committed,total_spent,expected",
        [
            pytest.param(
                Decimal("1000"), Decimal("1200"), Decimal("900"), Decimal("450"), Decimal("850"),
                id="positive result",  # income + balance comfortably covers all charges and spend
            ),
            pytest.param(
                Decimal("100"), Decimal("50"), Decimal("120"), Decimal("30"), Decimal("0"),
                id="zero boundary",  # committed charges exactly exhaust all available funds
            ),
            pytest.param(
                Decimal("0"), Decimal("20"), Decimal("15"), Decimal("10"), Decimal("-5"),
                id="negative result",  # spend pushes free money below zero — crisis territory
            ),
            pytest.param(
                Decimal("10.25"), Decimal("2.75"), Decimal("5.50"), Decimal("1.00"), Decimal("6.50"),
                id="decimal precision",  # Decimal arithmetic is exact — no float rounding errors
            ),
        ],
    )
    def test_calculate_free_money(
        self,
        engine: BalanceEngine,
        opening_balance: Decimal,
        total_income: Decimal,
        total_committed: Decimal,
        total_spent: Decimal,
        expected: Decimal,
    ) -> None:
        result = engine.calculate_free_money(opening_balance, total_income, total_committed, total_spent)
        assert result == expected


class TestClassifyBalanceState:

    @pytest.mark.parametrize(
        "free_money,caution_threshold,expected",
        [
            pytest.param(
                Decimal("150"), Decimal("100"), BalanceState.NORMAL,
                id="above caution threshold — normal state",  # free money safely above the warning line
            ),
            pytest.param(
                Decimal("100"), Decimal("100"), BalanceState.CAUTION,
                id="equal to caution threshold — caution boundary",  # threshold is inclusive on the caution side
            ),
            pytest.param(
                Decimal("1"), Decimal("100"), BalanceState.CAUTION,
                id="below threshold but positive — caution state",  # any positive free money below threshold is caution
            ),
            pytest.param(
                Decimal("0"), Decimal("100"), BalanceState.CRISIS,
                id="zero free money — crisis boundary",  # zero is not safe — triggers crisis
            ),
            pytest.param(
                Decimal("-1"), Decimal("100"), BalanceState.CRISIS,
                id="negative free money — crisis state",  # spent more than available — crisis confirmed
            ),
        ],
    )
    def test_classify_balance_state(
        self,
        engine: BalanceEngine,
        free_money: Decimal,
        caution_threshold: Decimal,
        expected: BalanceState,
    ) -> None:
        result = engine.classify_balance_state(free_money, caution_threshold)
        assert result is expected


class TestClassifyOnTrackState:

    @pytest.mark.parametrize(
        "monthly_budget,monthly_spent,red_threshold,expected",
        [
            pytest.param(
                Decimal("1000"), Decimal("850"), Decimal("130"), OnTrackState.GREEN,
                id="85% spent — green",  # well under budget
            ),
            pytest.param(
                Decimal("1000"), Decimal("1000"), Decimal("130"), OnTrackState.YELLOW,
                id="100% spent — yellow boundary",  # exactly at budget; yellow starts at 100%
            ),
            pytest.param(
                Decimal("1000"), Decimal("1200"), Decimal("130"), OnTrackState.YELLOW,
                id="120% spent — yellow mid-band",  # over budget but below red threshold
            ),
            pytest.param(
                Decimal("1000"), Decimal("1300"), Decimal("130"), OnTrackState.RED,
                id="130% spent — red boundary",  # exactly at red threshold; red is inclusive
            ),
            pytest.param(
                Decimal("1000"), Decimal("1400"), Decimal("130"), OnTrackState.RED,
                id="140% spent — red",  # well above red threshold
            ),
            pytest.param(
                Decimal("0"), Decimal("50"), Decimal("130"), OnTrackState.TIGHT_MONTH,
                id="zero monthly budget — tight month",  # charges equal income; no spendable budget this month
            ),
            pytest.param(
                Decimal("-10"), Decimal("50"), Decimal("130"), OnTrackState.TIGHT_MONTH,
                id="negative monthly budget — tight month",  # charges exceed income; division is never attempted
            ),
        ],
    )
    def test_classify_on_track_state(
        self,
        engine: BalanceEngine,
        monthly_budget: Decimal,
        monthly_spent: Decimal,
        red_threshold: Decimal,
        expected: OnTrackState,
    ) -> None:
        result = engine.classify_on_track_state(monthly_budget, monthly_spent, red_threshold)
        assert result is expected


class TestCalculateMonthlyBudget:

    @pytest.mark.parametrize(
        "income_this_month,charges_this_month,spent_this_month,red_threshold,"
        "expected_budget,expected_spent,expected_left,expected_state",
        [
            pytest.param(
                Decimal("1000"), Decimal("300"), Decimal("350"), Decimal("130"),
                Decimal("700"), Decimal("350"), Decimal("350"), OnTrackState.GREEN,
                id="50% spent — green",  # spend is half the available budget
            ),
            pytest.param(
                Decimal("1000"), Decimal("300"), Decimal("700"), Decimal("130"),
                Decimal("700"), Decimal("700"), Decimal("0"), OnTrackState.YELLOW,
                id="100% spent — yellow boundary",  # spent exactly equals budget; monthly_left is zero
            ),
            pytest.param(
                Decimal("1000"), Decimal("300"), Decimal("1000"), Decimal("130"),
                Decimal("700"), Decimal("1000"), Decimal("-300"), OnTrackState.RED,
                id="143% spent — red",  # spend exceeds budget and crosses red threshold
            ),
            pytest.param(
                Decimal("300"), Decimal("300"), Decimal("50"), Decimal("130"),
                Decimal("0"), Decimal("50"), Decimal("-50"), OnTrackState.TIGHT_MONTH,
                id="zero monthly budget — tight month",  # charges equal income; any spend goes negative
            ),
        ],
    )
    def test_calculate_monthly_budget(
        self,
        engine: BalanceEngine,
        income_this_month: Decimal,
        charges_this_month: Decimal,
        spent_this_month: Decimal,
        red_threshold: Decimal,
        expected_budget: Decimal,
        expected_spent: Decimal,
        expected_left: Decimal,
        expected_state: OnTrackState,
    ) -> None:
        result = engine.calculate_monthly_budget(income_this_month, charges_this_month, spent_this_month, red_threshold)
        assert result.monthly_budget == expected_budget
        assert result.monthly_spent == expected_spent
        assert result.monthly_left == expected_left
        assert result.on_track_state is expected_state


class TestBuildSnapshot:

    def test_composes_all_outputs(self, engine: BalanceEngine) -> None:
        # healthy session: positive free money, under monthly budget — all green
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

    def test_tight_month_and_crisis_states(self, engine: BalanceEngine) -> None:
        # crisis session: zero free money and charges equal income — both worst-case states together
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
