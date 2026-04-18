from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from expense_tracker.domain.models import (
    AppSession,
    ChargeStatus,
    CommittedCharge,
    FuzzyCharge,
    FuzzyChargeStatus,
    FuzzyEntryDirection,
    IncomeEntry,
    IncomeSourceTag,
    RecurringFrequency,
    RecurringRule,
    Transaction,
    TransactionCategory,
)
from expense_tracker.infrastructure.json.repositories import (
    JsonChargeRepository,
    JsonFuzzyChargeRepository,
    JsonIncomeRepository,
    JsonRecurringRuleRepository,
    JsonSessionRepository,
    JsonTransactionRepository,
)


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def session_id():
    """Provide a stable session UUID for filtering tests."""
    return uuid4()


@pytest.fixture
def other_session_id():
    """Provide a second session UUID to verify cross-session isolation."""
    return uuid4()


# ---------------------------------------------------------------------------
# JsonSessionRepository
# ---------------------------------------------------------------------------


class TestJsonSessionRepository:

    def test_get_active_returns_none_when_file_does_not_exist(self, tmp_path: Path) -> None:
        # a missing file means no session has been started yet
        repo = JsonSessionRepository(tmp_path / "session.json")

        assert repo.get_active() is None

    def test_create_then_get_active_round_trips_all_fields(self, tmp_path: Path) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonSessionRepository(tmp_path / "session.json")
        session = AppSession(
            session_id=uuid4(),
            start_date=date(2026, 4, 1),
            opening_balance=Decimal("1500.00"),
        )

        repo.create(session)
        result = repo.get_active()

        assert result is not None
        assert result.session_id == session.session_id
        assert result.start_date == session.start_date
        assert result.opening_balance == session.opening_balance

    def test_create_persists_across_adapter_restart(self, tmp_path: Path) -> None:
        # data written by one adapter instance must survive a fresh instance reading the same path
        path = tmp_path / "session.json"
        session = AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("2000"))

        JsonSessionRepository(path).create(session)
        result = JsonSessionRepository(path).get_active()

        assert result is not None
        assert result.session_id == session.session_id

    def test_create_overwrites_previous_session(self, tmp_path: Path) -> None:
        # only the most recently created session should be returned as active
        repo = JsonSessionRepository(tmp_path / "session.json")
        first = AppSession(session_id=uuid4(), start_date=date(2026, 1, 1), opening_balance=Decimal("500"))
        second = AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))

        repo.create(first)
        repo.create(second)

        result = repo.get_active()
        assert result is not None
        assert result.session_id == second.session_id


# ---------------------------------------------------------------------------
# JsonIncomeRepository
# ---------------------------------------------------------------------------


class TestJsonIncomeRepository:

    def test_add_then_list_for_session_round_trips_all_fields(self, tmp_path: Path, session_id) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonIncomeRepository(tmp_path / "income.json")
        entry = IncomeEntry(
            income_id=uuid4(),
            session_id=session_id,
            amount=Decimal("800.00"),
            source_tag=IncomeSourceTag.SCHOLARSHIP,
            date=date(2026, 4, 5),
        )

        repo.add(entry)
        results = repo.list_for_session(session_id)

        assert len(results) == 1
        result = results[0]
        assert result.income_id == entry.income_id
        assert result.session_id == entry.session_id
        assert result.amount == entry.amount
        assert result.source_tag == entry.source_tag
        assert result.date == entry.date

    def test_list_for_session_excludes_other_sessions(self, tmp_path: Path, session_id, other_session_id) -> None:
        # income entries from a different session must not appear in the results
        repo = JsonIncomeRepository(tmp_path / "income.json")
        own_entry = IncomeEntry(income_id=uuid4(), session_id=session_id, amount=Decimal("500"), source_tag=IncomeSourceTag.FAMILY, date=date(2026, 4, 1))
        other_entry = IncomeEntry(income_id=uuid4(), session_id=other_session_id, amount=Decimal("300"), source_tag=IncomeSourceTag.WORK, date=date(2026, 4, 1))

        repo.add(own_entry)
        repo.add(other_entry)

        results = repo.list_for_session(session_id)
        assert len(results) == 1
        assert results[0].income_id == own_entry.income_id

    def test_list_for_month_returns_matching_entries(self, tmp_path: Path, session_id) -> None:
        # only entries whose date falls within the requested month should be returned
        repo = JsonIncomeRepository(tmp_path / "income.json")
        april_entry = IncomeEntry(income_id=uuid4(), session_id=session_id, amount=Decimal("500"), source_tag=IncomeSourceTag.SCHOLARSHIP, date=date(2026, 4, 10))
        may_entry = IncomeEntry(income_id=uuid4(), session_id=session_id, amount=Decimal("300"), source_tag=IncomeSourceTag.FAMILY, date=date(2026, 5, 1))

        repo.add(april_entry)
        repo.add(may_entry)

        results = repo.list_for_month(session_id, 2026, 4)
        assert len(results) == 1
        assert results[0].income_id == april_entry.income_id

    def test_list_returns_empty_when_file_does_not_exist(self, tmp_path: Path, session_id) -> None:
        # a missing storage file should return an empty list, not raise an error
        repo = JsonIncomeRepository(tmp_path / "income.json")

        assert repo.list_for_session(session_id) == []
        assert repo.list_for_month(session_id, 2026, 4) == []

    def test_add_persists_across_adapter_restart(self, tmp_path: Path, session_id) -> None:
        # entries written by one adapter instance must be readable by a fresh instance
        path = tmp_path / "income.json"
        entry = IncomeEntry(income_id=uuid4(), session_id=session_id, amount=Decimal("400"), source_tag=IncomeSourceTag.WORK, date=date(2026, 4, 1))

        JsonIncomeRepository(path).add(entry)
        results = JsonIncomeRepository(path).list_for_session(session_id)

        assert len(results) == 1
        assert results[0].income_id == entry.income_id


# ---------------------------------------------------------------------------
# JsonChargeRepository
# ---------------------------------------------------------------------------


class TestJsonChargeRepository:

    def test_add_then_get_by_id_round_trips_all_fields(self, tmp_path: Path, session_id) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonChargeRepository(tmp_path / "charges.json")
        charge = CommittedCharge(
            charge_id=uuid4(),
            session_id=session_id,
            name="Rent",
            amount=Decimal("1200.00"),
            due_date=date(2026, 4, 20),
            status=ChargeStatus.UPCOMING,
            recurring_rule_id=None,
        )

        repo.add(charge)
        result = repo.get_by_id(charge.charge_id)

        assert result is not None
        assert result.charge_id == charge.charge_id
        assert result.session_id == charge.session_id
        assert result.name == charge.name
        assert result.amount == charge.amount
        assert result.due_date == charge.due_date
        assert result.status == charge.status
        assert result.recurring_rule_id is None

    def test_add_preserves_recurring_rule_id(self, tmp_path: Path, session_id) -> None:
        # recurring_rule_id must survive the JSON round-trip without becoming None
        repo = JsonChargeRepository(tmp_path / "charges.json")
        rule_id = uuid4()
        charge = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 1), status=ChargeStatus.UPCOMING, recurring_rule_id=rule_id)

        repo.add(charge)
        result = repo.get_by_id(charge.charge_id)

        assert result is not None
        assert result.recurring_rule_id == rule_id

    def test_get_by_id_returns_none_for_unknown_id(self, tmp_path: Path) -> None:
        # a query for a non-existent charge must return None, not raise
        repo = JsonChargeRepository(tmp_path / "charges.json")

        assert repo.get_by_id(uuid4()) is None

    def test_list_upcoming_filters_by_status(self, tmp_path: Path, session_id) -> None:
        # list_upcoming must exclude paid charges
        repo = JsonChargeRepository(tmp_path / "charges.json")
        upcoming = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        paid = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Electric", amount=Decimal("100"), due_date=date(2026, 4, 5), status=ChargeStatus.PAID)

        repo.add(upcoming)
        repo.add(paid)

        results = repo.list_upcoming(session_id)
        assert len(results) == 1
        assert results[0].charge_id == upcoming.charge_id

    def test_list_for_month_filters_by_due_date(self, tmp_path: Path, session_id) -> None:
        # only charges whose due_date falls in the requested month should be returned
        repo = JsonChargeRepository(tmp_path / "charges.json")
        april = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        may = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Phone", amount=Decimal("80"), due_date=date(2026, 5, 1), status=ChargeStatus.UPCOMING)

        repo.add(april)
        repo.add(may)

        results = repo.list_for_month(session_id, 2026, 4)
        assert len(results) == 1
        assert results[0].charge_id == april.charge_id

    def test_mark_paid_updates_status_and_preserves_other_fields(self, tmp_path: Path, session_id) -> None:
        # mark_paid must flip only the status field; all other fields must remain unchanged
        repo = JsonChargeRepository(tmp_path / "charges.json")
        charge = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        repo.add(charge)

        repo.mark_paid(charge.charge_id)
        result = repo.get_by_id(charge.charge_id)

        assert result is not None
        assert result.status == ChargeStatus.PAID
        assert result.name == charge.name
        assert result.amount == charge.amount
        assert result.due_date == charge.due_date

    def test_mark_paid_does_not_affect_other_charges(self, tmp_path: Path, session_id) -> None:
        # marking one charge paid must leave all other charges untouched
        repo = JsonChargeRepository(tmp_path / "charges.json")
        target = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        other = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Phone", amount=Decimal("80"), due_date=date(2026, 4, 15), status=ChargeStatus.UPCOMING)

        repo.add(target)
        repo.add(other)
        repo.mark_paid(target.charge_id)

        other_result = repo.get_by_id(other.charge_id)
        assert other_result is not None
        assert other_result.status == ChargeStatus.UPCOMING

    def test_add_persists_across_adapter_restart(self, tmp_path: Path, session_id) -> None:
        # charges written by one adapter instance must be readable by a fresh instance
        path = tmp_path / "charges.json"
        charge = CommittedCharge(charge_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)

        JsonChargeRepository(path).add(charge)
        result = JsonChargeRepository(path).get_by_id(charge.charge_id)

        assert result is not None
        assert result.charge_id == charge.charge_id


# ---------------------------------------------------------------------------
# JsonRecurringRuleRepository
# ---------------------------------------------------------------------------


class TestJsonRecurringRuleRepository:

    def test_add_then_get_by_id_round_trips_all_fields(self, tmp_path: Path, session_id) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonRecurringRuleRepository(tmp_path / "rules.json")
        rule = RecurringRule(
            rule_id=uuid4(),
            session_id=session_id,
            name="Rent",
            amount=Decimal("1200.00"),
            frequency=RecurringFrequency.MONTHLY,
            day_of_month=15,
            reminder_days=3,
        )

        repo.add(rule)
        result = repo.get_by_id(rule.rule_id)

        assert result is not None
        assert result.rule_id == rule.rule_id
        assert result.session_id == rule.session_id
        assert result.name == rule.name
        assert result.amount == rule.amount
        assert result.frequency == rule.frequency
        assert result.day_of_month == rule.day_of_month
        assert result.reminder_days == rule.reminder_days

    def test_get_by_id_returns_none_for_unknown_id(self, tmp_path: Path) -> None:
        # a query for a non-existent rule must return None, not raise
        repo = JsonRecurringRuleRepository(tmp_path / "rules.json")

        assert repo.get_by_id(uuid4()) is None

    def test_list_for_session_returns_matching_rules(self, tmp_path: Path, session_id, other_session_id) -> None:
        # rules belonging to another session must not appear in the results
        repo = JsonRecurringRuleRepository(tmp_path / "rules.json")
        own_rule = RecurringRule(rule_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), frequency=RecurringFrequency.MONTHLY, day_of_month=15, reminder_days=3)
        other_rule = RecurringRule(rule_id=uuid4(), session_id=other_session_id, name="Phone", amount=Decimal("80"), frequency=RecurringFrequency.MONTHLY, day_of_month=5, reminder_days=3)

        repo.add(own_rule)
        repo.add(other_rule)

        results = repo.list_for_session(session_id)
        assert len(results) == 1
        assert results[0].rule_id == own_rule.rule_id

    def test_add_persists_across_adapter_restart(self, tmp_path: Path, session_id) -> None:
        # rules written by one adapter instance must be readable by a fresh instance
        path = tmp_path / "rules.json"
        rule = RecurringRule(rule_id=uuid4(), session_id=session_id, name="Rent", amount=Decimal("500"), frequency=RecurringFrequency.MONTHLY, day_of_month=15, reminder_days=3)

        JsonRecurringRuleRepository(path).add(rule)
        result = JsonRecurringRuleRepository(path).get_by_id(rule.rule_id)

        assert result is not None
        assert result.rule_id == rule.rule_id


# ---------------------------------------------------------------------------
# JsonFuzzyChargeRepository
# ---------------------------------------------------------------------------


class TestJsonFuzzyChargeRepository:

    def test_add_then_get_by_id_round_trips_all_fields(self, tmp_path: Path, session_id) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
        entry = FuzzyCharge(
            fuzzy_id=uuid4(),
            session_id=session_id,
            name="Dentist",
            direction=FuzzyEntryDirection.EXPENSE,
            status=FuzzyChargeStatus.PENDING,
            expected_date=date(2026, 4, 20),
            estimated_amount=Decimal("200.00"),
            resolved_amount=None,
            resolved_date=None,
        )

        repo.add(entry)
        result = repo.get_by_id(entry.fuzzy_id)

        assert result is not None
        assert result.fuzzy_id == entry.fuzzy_id
        assert result.session_id == entry.session_id
        assert result.name == entry.name
        assert result.direction == entry.direction
        assert result.status == entry.status
        assert result.expected_date == entry.expected_date
        assert result.estimated_amount == entry.estimated_amount
        assert result.resolved_amount is None
        assert result.resolved_date is None

    def test_add_handles_all_optional_fields_as_none(self, tmp_path: Path, session_id) -> None:
        # a fuzzy entry with no date or amount estimate must round-trip without errors
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
        entry = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Unknown expense", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING)

        repo.add(entry)
        result = repo.get_by_id(entry.fuzzy_id)

        assert result is not None
        assert result.expected_date is None
        assert result.estimated_amount is None
        assert result.resolved_amount is None
        assert result.resolved_date is None

    def test_get_by_id_returns_none_for_unknown_id(self, tmp_path: Path) -> None:
        # a query for a non-existent entry must return None, not raise
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")

        assert repo.get_by_id(uuid4()) is None

    def test_list_pending_filters_by_status_and_session(self, tmp_path: Path, session_id, other_session_id) -> None:
        # list_pending must exclude resolved/discarded entries and entries from other sessions
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
        pending = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Dentist", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING)
        resolved = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Tax refund", direction=FuzzyEntryDirection.INCOME, status=FuzzyChargeStatus.RESOLVED)
        other_session = FuzzyCharge(fuzzy_id=uuid4(), session_id=other_session_id, name="Dentist", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING)

        repo.add(pending)
        repo.add(resolved)
        repo.add(other_session)

        results = repo.list_pending(session_id)
        assert len(results) == 1
        assert results[0].fuzzy_id == pending.fuzzy_id

    def test_update_status_changes_only_status(self, tmp_path: Path, session_id) -> None:
        # update_status must flip only the status; all other fields must remain unchanged
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
        entry = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Dentist", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING, estimated_amount=Decimal("200"))
        repo.add(entry)

        repo.update_status(entry.fuzzy_id, FuzzyChargeStatus.DISCARDED)
        result = repo.get_by_id(entry.fuzzy_id)

        assert result is not None
        assert result.status == FuzzyChargeStatus.DISCARDED
        assert result.name == entry.name
        assert result.estimated_amount == entry.estimated_amount

    def test_update_replaces_full_record(self, tmp_path: Path, session_id) -> None:
        # update must persist all fields including resolved_amount and resolved_date
        repo = JsonFuzzyChargeRepository(tmp_path / "fuzzy.json")
        original = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Dentist", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING, estimated_amount=Decimal("200"))
        repo.add(original)

        resolved = FuzzyCharge(
            fuzzy_id=original.fuzzy_id,
            session_id=original.session_id,
            name=original.name,
            direction=original.direction,
            status=FuzzyChargeStatus.RESOLVED,
            estimated_amount=original.estimated_amount,
            resolved_amount=Decimal("185.50"),
            resolved_date=date(2026, 4, 18),
        )
        repo.update(resolved)
        result = repo.get_by_id(original.fuzzy_id)

        assert result is not None
        assert result.status == FuzzyChargeStatus.RESOLVED
        assert result.resolved_amount == Decimal("185.50")
        assert result.resolved_date == date(2026, 4, 18)

    def test_add_persists_across_adapter_restart(self, tmp_path: Path, session_id) -> None:
        # entries written by one adapter instance must be readable by a fresh instance
        path = tmp_path / "fuzzy.json"
        entry = FuzzyCharge(fuzzy_id=uuid4(), session_id=session_id, name="Dentist", direction=FuzzyEntryDirection.EXPENSE, status=FuzzyChargeStatus.PENDING)

        JsonFuzzyChargeRepository(path).add(entry)
        result = JsonFuzzyChargeRepository(path).get_by_id(entry.fuzzy_id)

        assert result is not None
        assert result.fuzzy_id == entry.fuzzy_id


# ---------------------------------------------------------------------------
# JsonTransactionRepository
# ---------------------------------------------------------------------------


class TestJsonTransactionRepository:

    def test_add_then_list_for_month_round_trips_all_fields(self, tmp_path: Path, session_id) -> None:
        # every field written to disk must deserialise back to the exact same value
        repo = JsonTransactionRepository(tmp_path / "transactions.json")
        transaction = Transaction(
            transaction_id=uuid4(),
            session_id=session_id,
            amount=Decimal("45.50"),
            description="Supermarket",
            category=TransactionCategory.FOOD,
            date=date(2026, 4, 10),
        )

        repo.add(transaction)
        results = repo.list_for_month(session_id, 2026, 4)

        assert len(results) == 1
        result = results[0]
        assert result.transaction_id == transaction.transaction_id
        assert result.session_id == transaction.session_id
        assert result.amount == transaction.amount
        assert result.description == transaction.description
        assert result.category == transaction.category
        assert result.date == transaction.date

    def test_add_handles_none_category(self, tmp_path: Path, session_id) -> None:
        # a transaction with no category must round-trip without errors
        repo = JsonTransactionRepository(tmp_path / "transactions.json")
        transaction = Transaction(transaction_id=uuid4(), session_id=session_id, amount=Decimal("20"), description="Misc", category=None, date=date(2026, 4, 5))

        repo.add(transaction)
        results = repo.list_for_month(session_id, 2026, 4)

        assert len(results) == 1
        assert results[0].category is None

    def test_list_for_month_excludes_other_months(self, tmp_path: Path, session_id) -> None:
        # transactions from a different month must not appear in the results
        repo = JsonTransactionRepository(tmp_path / "transactions.json")
        april = Transaction(transaction_id=uuid4(), session_id=session_id, amount=Decimal("30"), description="Bus", category=TransactionCategory.TRANSPORT, date=date(2026, 4, 15))
        may = Transaction(transaction_id=uuid4(), session_id=session_id, amount=Decimal("50"), description="Books", category=TransactionCategory.EDUCATION, date=date(2026, 5, 1))

        repo.add(april)
        repo.add(may)

        results = repo.list_for_month(session_id, 2026, 4)
        assert len(results) == 1
        assert results[0].transaction_id == april.transaction_id

    def test_list_for_month_excludes_other_sessions(self, tmp_path: Path, session_id, other_session_id) -> None:
        # transactions from another session must not appear in the results
        repo = JsonTransactionRepository(tmp_path / "transactions.json")
        own = Transaction(transaction_id=uuid4(), session_id=session_id, amount=Decimal("30"), description="Coffee", category=TransactionCategory.FOOD, date=date(2026, 4, 5))
        other = Transaction(transaction_id=uuid4(), session_id=other_session_id, amount=Decimal("100"), description="Rent", category=None, date=date(2026, 4, 5))

        repo.add(own)
        repo.add(other)

        results = repo.list_for_month(session_id, 2026, 4)
        assert len(results) == 1
        assert results[0].transaction_id == own.transaction_id

    def test_list_returns_empty_when_file_does_not_exist(self, tmp_path: Path, session_id) -> None:
        # a missing storage file should return an empty list, not raise an error
        repo = JsonTransactionRepository(tmp_path / "transactions.json")

        assert repo.list_for_month(session_id, 2026, 4) == []

    def test_add_persists_across_adapter_restart(self, tmp_path: Path, session_id) -> None:
        # transactions written by one adapter instance must be readable by a fresh instance
        path = tmp_path / "transactions.json"
        transaction = Transaction(transaction_id=uuid4(), session_id=session_id, amount=Decimal("45"), description="Lunch", category=TransactionCategory.FOOD, date=date(2026, 4, 10))

        JsonTransactionRepository(path).add(transaction)
        results = JsonTransactionRepository(path).list_for_month(session_id, 2026, 4)

        assert len(results) == 1
        assert results[0].transaction_id == transaction.transaction_id
