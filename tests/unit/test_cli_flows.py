from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

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


class _FakeChargeService:

    def __init__(self, error_to_raise: Exception | None = None) -> None:
        self._error_to_raise = error_to_raise
        self.calls: list[tuple[str, Decimal, date]] = []
        self.recurring_calls: list[tuple[str, Decimal, int]] = []

    def add_charge(self, name: str, amount: Decimal, due_date: date) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.calls.append((name, amount, due_date))

    def add_recurring_charge(self, name: str, amount: Decimal, day_of_month: int) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.recurring_calls.append((name, amount, day_of_month))


class _FakeFuzzyChargeService:

    def __init__(self, error_to_raise: Exception | None = None) -> None:
        self._error_to_raise = error_to_raise
        self.calls: list[tuple[str, date, Decimal | None]] = []
        self.resolve_calls: list[tuple[UUID, Decimal]] = []
        self.discard_calls: list[UUID] = []

    def add_fuzzy_charge(self, name: str, expected_date: date, estimated_amount: Decimal | None = None) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.calls.append((name, expected_date, estimated_amount))

    def resolve(self, fuzzy_id: UUID, resolved_amount: Decimal) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.resolve_calls.append((fuzzy_id, resolved_amount))

    def discard(self, fuzzy_id: UUID) -> None:
        if self._error_to_raise is not None:
            raise self._error_to_raise
        self.discard_calls.append(fuzzy_id)


def _build_cli(income_service: _FakeIncomeService | None = None, charge_service: _FakeChargeService | None = None, fuzzy_charge_service: _FakeFuzzyChargeService | None = None) -> CliApplication:
    session_service: Any = _FakeSessionService()
    balance_service: Any = _FakeBalanceService()
    income_service_impl: Any = income_service or _FakeIncomeService()
    charge_service_impl: Any = charge_service or _FakeChargeService()
    fuzzy_charge_service_impl: Any = fuzzy_charge_service or _FakeFuzzyChargeService()
    return CliApplication(session_service=session_service, balance_service=balance_service, income_service=income_service_impl, charge_service=charge_service_impl, fuzzy_charge_service=fuzzy_charge_service_impl)


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


class TestCliChargeAdd:

    def test_run_charge_add_calls_charge_service_with_parsed_values(self) -> None:
        # valid raw args are parsed in CLI and forwarded to the charge service as typed values
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--name", "Rent", "--amount", "1200.00", "--due-date", "2026-04-20"])

        assert exit_code == 0
        assert charge_service.calls == [("Rent", Decimal("1200.00"), date(2026, 4, 20))]

    @pytest.mark.parametrize(
        "arguments",
        [
            pytest.param(["charge", "add", "--amount", "1200.00", "--due-date", "2026-04-20"], id="missing name"),
            pytest.param(["charge", "add", "--name", "Rent", "--due-date", "2026-04-20"], id="missing amount"),
            pytest.param(["charge", "add", "--name", "Rent", "--amount", "1200.00"], id="missing due date"),
        ],
    )
    def test_run_charge_add_requires_all_three_arguments(self, arguments: list[str]) -> None:
        # CLI must fail fast when one required input is missing before it reaches the service layer
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(arguments)

        assert exit_code == 1
        assert charge_service.calls == []

    def test_run_charge_add_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--name", "Rent", "--amount", "1200.00", "--due-date", "2026-04-20", "--extra", "x"])

        assert exit_code == 1
        assert charge_service.calls == []

    def test_run_charge_add_returns_error_on_invalid_input(self) -> None:
        # validator failures at CLI boundary should return a non-zero exit code without service invocation
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--name", "Rent", "--amount", "not-a-number", "--due-date", "2026-04-20"])

        assert exit_code == 1
        assert charge_service.calls == []

    def test_run_charge_add_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        charge_service = _FakeChargeService(error_to_raise=ApplicationError("No active session."))
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--name", "Rent", "--amount", "1200.00", "--due-date", "2026-04-20"])

        assert exit_code == 1
        assert charge_service.calls == []


class TestCliRecurringChargeAdd:

    def test_run_charge_add_recurring_calls_charge_service_with_parsed_values(self) -> None:
        # valid recurring charge args are parsed in CLI and forwarded to the charge service as typed values
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--recurring", "--name", "Rent", "--amount", "1200.00", "--day-of-month", "15"])

        assert exit_code == 0
        assert charge_service.recurring_calls == [("Rent", Decimal("1200.00"), 15)]

    @pytest.mark.parametrize(
        "arguments",
        [
            pytest.param(["charge", "add", "--recurring", "--amount", "1200.00", "--day-of-month", "15"], id="missing name"),
            pytest.param(["charge", "add", "--recurring", "--name", "Rent", "--day-of-month", "15"], id="missing amount"),
            pytest.param(["charge", "add", "--recurring", "--name", "Rent", "--amount", "1200.00"], id="missing day of month"),
        ],
    )
    def test_run_charge_add_recurring_requires_all_three_arguments(self, arguments: list[str]) -> None:
        # CLI must fail fast when one required recurring input is missing before it reaches the service layer
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(arguments)

        assert exit_code == 1
        assert charge_service.recurring_calls == []

    def test_run_charge_add_recurring_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--recurring", "--name", "Rent", "--amount", "1200.00", "--day-of-month", "15", "--extra", "x"])

        assert exit_code == 1
        assert charge_service.recurring_calls == []

    def test_run_charge_add_recurring_returns_error_on_invalid_input(self) -> None:
        # validator failures at CLI boundary should return a non-zero exit code without service invocation
        charge_service = _FakeChargeService()
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--recurring", "--name", "Rent", "--amount", "1200.00", "--day-of-month", "not-a-day"])

        assert exit_code == 1
        assert charge_service.recurring_calls == []

    def test_run_charge_add_recurring_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        charge_service = _FakeChargeService(error_to_raise=ApplicationError("No active session."))
        cli = _build_cli(charge_service=charge_service)

        exit_code = cli.run(["charge", "add", "--recurring", "--name", "Rent", "--amount", "1200.00", "--day-of-month", "15"])

        assert exit_code == 1
        assert charge_service.recurring_calls == []


class TestCliFuzzyChargeAdd:

    def test_run_fuzzy_charge_add_calls_fuzzy_service_with_required_values(self) -> None:
        # valid fuzzy charge args are parsed in CLI and forwarded to the fuzzy service as typed values
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "add", "--name", "Electric", "--due-date", "2026-04-28"])

        assert exit_code == 0
        assert fuzzy_charge_service.calls == [("Electric", date(2026, 4, 28), None)]

    def test_run_fuzzy_charge_add_calls_fuzzy_service_with_estimate(self) -> None:
        # optional estimate should be parsed and forwarded when provided
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "add", "--name", "Electric", "--due-date", "2026-04-28", "--estimate", "250.00"])

        assert exit_code == 0
        assert fuzzy_charge_service.calls == [("Electric", date(2026, 4, 28), Decimal("250.00"))]

    @pytest.mark.parametrize(
        "arguments",
        [
            pytest.param(["fuzzy-charge", "add", "--due-date", "2026-04-28"], id="missing name"),
            pytest.param(["fuzzy-charge", "add", "--name", "Electric"], id="missing due date"),
        ],
    )
    def test_run_fuzzy_charge_add_requires_name_and_due_date(self, arguments: list[str]) -> None:
        # CLI must fail fast when one required fuzzy input is missing before it reaches the service layer
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(arguments)

        assert exit_code == 1
        assert fuzzy_charge_service.calls == []

    def test_run_fuzzy_charge_add_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "add", "--name", "Electric", "--due-date", "2026-04-28", "--extra", "x"])

        assert exit_code == 1
        assert fuzzy_charge_service.calls == []

    def test_run_fuzzy_charge_add_returns_error_on_invalid_input(self) -> None:
        # validator failures at CLI boundary should return a non-zero exit code without service invocation
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "add", "--name", "Electric", "--due-date", "bad-date", "--estimate", "bad-amount"])

        assert exit_code == 1
        assert fuzzy_charge_service.calls == []

    def test_run_fuzzy_charge_add_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        fuzzy_charge_service = _FakeFuzzyChargeService(error_to_raise=ApplicationError("No active session."))
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "add", "--name", "Electric", "--due-date", "2026-04-28"])

        assert exit_code == 1
        assert fuzzy_charge_service.calls == []


class TestCliFuzzyChargeResolve:

    def test_run_fuzzy_charge_resolve_calls_fuzzy_service_with_parsed_values(self) -> None:
        # valid resolve args are parsed in CLI and forwarded to the fuzzy service as typed values
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)
        fuzzy_id = uuid4()

        exit_code = cli.run(["fuzzy-charge", "resolve", "--id", str(fuzzy_id), "--amount", "185.50"])

        assert exit_code == 0
        assert fuzzy_charge_service.resolve_calls == [(fuzzy_id, Decimal("185.50"))]

    @pytest.mark.parametrize(
        "arguments",
        [
            pytest.param(["fuzzy-charge", "resolve", "--amount", "185.50"], id="missing id"),
            pytest.param(["fuzzy-charge", "resolve", "--id", str(uuid4())], id="missing amount"),
        ],
    )
    def test_run_fuzzy_charge_resolve_requires_id_and_amount(self, arguments: list[str]) -> None:
        # CLI must fail fast when one required resolve input is missing before it reaches the service layer
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(arguments)

        assert exit_code == 1
        assert fuzzy_charge_service.resolve_calls == []

    def test_run_fuzzy_charge_resolve_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "resolve", "--id", str(uuid4()), "--amount", "185.50", "--extra", "x"])

        assert exit_code == 1
        assert fuzzy_charge_service.resolve_calls == []

    def test_run_fuzzy_charge_resolve_returns_error_on_invalid_uuid(self) -> None:
        # invalid UUID at CLI boundary should return a non-zero exit code without service invocation
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "resolve", "--id", "not-a-uuid", "--amount", "185.50"])

        assert exit_code == 1
        assert fuzzy_charge_service.resolve_calls == []

    def test_run_fuzzy_charge_resolve_returns_error_on_invalid_input(self) -> None:
        # validator failures at CLI boundary should return a non-zero exit code without service invocation
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "resolve", "--id", str(uuid4()), "--amount", "bad-amount"])

        assert exit_code == 1
        assert fuzzy_charge_service.resolve_calls == []

    def test_run_fuzzy_charge_resolve_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        fuzzy_charge_service = _FakeFuzzyChargeService(error_to_raise=ApplicationError("Fuzzy entry not found."))
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "resolve", "--id", str(uuid4()), "--amount", "185.50"])

        assert exit_code == 1
        assert fuzzy_charge_service.resolve_calls == []


class TestCliFuzzyChargeDiscard:

    def test_run_fuzzy_charge_discard_calls_fuzzy_service_with_parsed_values(self) -> None:
        # valid discard args are parsed in CLI and forwarded to the fuzzy service as typed values
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)
        fuzzy_id = uuid4()

        exit_code = cli.run(["fuzzy-charge", "discard", "--id", str(fuzzy_id)])

        assert exit_code == 0
        assert fuzzy_charge_service.discard_calls == [fuzzy_id]

    def test_run_fuzzy_charge_discard_requires_id(self) -> None:
        # CLI must fail fast when required discard input is missing before it reaches the service layer
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "discard"])

        assert exit_code == 1
        assert fuzzy_charge_service.discard_calls == []

    def test_run_fuzzy_charge_discard_rejects_unknown_argument(self) -> None:
        # unsupported flags must be rejected to keep CLI input contract strict and explicit
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "discard", "--id", str(uuid4()), "--extra", "x"])

        assert exit_code == 1
        assert fuzzy_charge_service.discard_calls == []

    def test_run_fuzzy_charge_discard_returns_error_on_invalid_uuid(self) -> None:
        # invalid UUID at CLI boundary should return a non-zero exit code without service invocation
        fuzzy_charge_service = _FakeFuzzyChargeService()
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "discard", "--id", "not-a-uuid"])

        assert exit_code == 1
        assert fuzzy_charge_service.discard_calls == []

    def test_run_fuzzy_charge_discard_returns_error_when_service_fails(self) -> None:
        # application-level service failures must be surfaced as CLI command failures
        fuzzy_charge_service = _FakeFuzzyChargeService(error_to_raise=ApplicationError("Fuzzy entry not found."))
        cli = _build_cli(fuzzy_charge_service=fuzzy_charge_service)

        exit_code = cli.run(["fuzzy-charge", "discard", "--id", str(uuid4())])

        assert exit_code == 1
        assert fuzzy_charge_service.discard_calls == []


