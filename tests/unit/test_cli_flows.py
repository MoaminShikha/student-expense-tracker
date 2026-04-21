from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from expense_tracker.app.cli import CliApplication
from expense_tracker.domain.models import IncomeSourceTag
from expense_tracker.shared.exceptions import ApplicationError


class _FakeSessionService:

    def init_session(self, opening_balance: Decimal) -> None:
        self.last_opening_balance = opening_balance


class _FakeBalanceService:
    pass


class _FakeIncomeService:

    def __init__(self, error_to_raise: Exception | None = None) -> None:
        self._error_to_raise = error_to_raise
        self.calls: list[tuple[Decimal, IncomeSourceTag, date]] = []

    def add_income(self, amount: Decimal, source_tag: IncomeSourceTag, entry_date: date) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.calls.append((amount, source_tag, entry_date))


def _build_cli(income_service: _FakeIncomeService | None = None) -> CliApplication:
    return CliApplication(session_service=_FakeSessionService(), balance_service=_FakeBalanceService(), income_service=income_service or _FakeIncomeService())


class TestCliIncomeAdd:

    def test_run_income_add_calls_income_service_with_parsed_values(self) -> None:
        # valid raw args are parsed in CLI and forwarded to the income service as typed values
        income_service = _FakeIncomeService()
        cli = _build_cli(income_service)

        exit_code = cli.run(["income", "add", "--amount", "250.00", "--source", "work", "--date", "2026-04-15"])

        assert exit_code == 0
        assert income_service.calls == [(Decimal("250.00"), IncomeSourceTag.WORK, date(2026, 4, 15))]

    @pytest.mark.parametrize(
        "arguments,missing_name",
        [
            pytest.param(["income", "add", "--source", "work", "--date", "2026-04-15"], "--amount", id="missing amount"),
            pytest.param(["income", "add", "--amount", "250.00", "--date", "2026-04-15"], "--source", id="missing source"),
            pytest.param(["income", "add", "--amount", "250.00", "--source", "work"], "--date", id="missing date"),
        ],
    )
    def test_run_income_add_requires_all_three_arguments(self, arguments: list[str], missing_name: str) -> None:
        # CLI must fail fast when one required input is missing before it reaches the service layer
        income_service = _FakeIncomeService()
        cli = _build_cli(income_service)

        exit_code = cli.run(arguments)

        assert exit_code == 1
        assert income_service.calls == []

    def test_run_income_add_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        income_service = _FakeIncomeService()
        cli = _build_cli(income_service)

        exit_code = cli.run(["income", "add", "--amount", "250.00", "--source", "work", "--date", "2026-04-15", "--extra", "x"])

        assert exit_code == 1
        assert income_service.calls == []

    def test_run_income_add_returns_error_on_invalid_input(self) -> None:
        # validator failures at CLI boundary should return a non-zero exit code without service invocation
        income_service = _FakeIncomeService()
        cli = _build_cli(income_service)

        exit_code = cli.run(["income", "add", "--amount", "not-a-number", "--source", "work", "--date", "2026-04-15"])

        assert exit_code == 1
        assert income_service.calls == []

    def test_run_income_add_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        income_service = _FakeIncomeService(error_to_raise=ApplicationError("No active session."))
        cli = _build_cli(income_service)

        exit_code = cli.run(["income", "add", "--amount", "250.00", "--source", "work", "--date", "2026-04-15"])

        assert exit_code == 1
        assert income_service.calls == []

