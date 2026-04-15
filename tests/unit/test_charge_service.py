from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from expense_tracker.application.services import ChargeService
from expense_tracker.domain.models import AppSession, ChargeStatus, CommittedCharge, RecurringFrequency, RecurringRule
from expense_tracker.ports.repositories import RecurringRuleRepository
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class _InMemorySessionRepository:

    def __init__(self, active_session: AppSession | None = None) -> None:
        self._active_session = active_session

    def create(self, session: AppSession) -> None:
        self._active_session = session

    def get_active(self) -> AppSession | None:
        return self._active_session


class _InMemoryChargeRepository:

    def __init__(self) -> None:
        self.charges: list[CommittedCharge] = []

    def add(self, charge: CommittedCharge) -> None:
        self.charges.append(charge)

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        return [charge for charge in self.charges if charge.session_id == session_id and charge.status is ChargeStatus.UPCOMING]

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        return [charge for charge in self.charges if charge.session_id == session_id and charge.due_date.year == year and charge.due_date.month == month]

    def mark_paid(self, charge_id: UUID) -> None:
        self.charges = [CommittedCharge(charge_id=charge.charge_id, session_id=charge.session_id, name=charge.name, amount=charge.amount, due_date=charge.due_date, status=ChargeStatus.PAID, recurring_rule_id=charge.recurring_rule_id) if charge.charge_id == charge_id else charge for charge in self.charges]

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        for charge in self.charges:
            if charge.charge_id == charge_id:
                return charge
        return None


class _InMemoryRecurringRuleRepository:

    def __init__(self) -> None:
        self.rules: list[RecurringRule] = []

    def add(self, rule: RecurringRule) -> None:
        self.rules.append(rule)

    def get_by_id(self, rule_id: UUID) -> RecurringRule | None:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def list_for_session(self, session_id: UUID) -> list[RecurringRule]:
        return [rule for rule in self.rules if rule.session_id == session_id]


def _build_charge_service(
    session_repository: _InMemorySessionRepository,
    charge_repository: _InMemoryChargeRepository,
    recurring_rule_repository: _InMemoryRecurringRuleRepository | None = None,
) -> ChargeService:
    resolved_recurring_rule_repository: RecurringRuleRepository
    if recurring_rule_repository is None:
        resolved_recurring_rule_repository = _InMemoryRecurringRuleRepository()
    else:
        resolved_recurring_rule_repository = recurring_rule_repository

    return ChargeService(
        session_repository=session_repository,
        charge_repository=charge_repository,
        recurring_rule_repository=resolved_recurring_rule_repository,
    )


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for charge service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestChargeServiceAddCharge:

    def test_add_charge_persists_committed_charge(self, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one committed charge
        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        service = _build_charge_service(session_repository, charge_repository)

        charge = service.add_charge(name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20))

        assert len(charge_repository.charges) == 1
        assert charge_repository.charges[0] == charge
        assert charge.session_id == active_session.session_id
        assert charge.name == "Rent"
        assert charge.amount == Decimal("500.00")
        assert charge.due_date == date(2026, 4, 20)
        assert charge.status is ChargeStatus.UPCOMING

    def test_add_charge_rejects_when_no_active_session(self) -> None:
        # service must fail fast if the caller tries to add a charge before starting a session
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        service = _build_charge_service(session_repository, charge_repository)

        with pytest.raises(ApplicationError):
            service.add_charge(name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount",),
            pytest.param(Decimal("-1.00"), id="negative amount",),
        ],
    )
    def test_add_charge_rejects_non_positive_amount(self, active_session: AppSession, amount: Decimal) -> None:
        # committed charges must represent an actual positive obligation
        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        service = _build_charge_service(session_repository, charge_repository)

        with pytest.raises(ValidationError):
            service.add_charge(name="Rent", amount=amount, due_date=date(2026, 4, 20))

    def test_add_charge_rejects_blank_name(self, active_session: AppSession) -> None:
        # blank names create unusable charge records and are not allowed
        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        service = _build_charge_service(session_repository, charge_repository)

        with pytest.raises(ValidationError):
            service.add_charge(name="   ", amount=Decimal("500.00"), due_date=date(2026, 4, 20))


class TestChargeServiceMarkPaid:

    def test_mark_paid_updates_matching_charge_status(self) -> None:
        # mark_paid must flip only the status and keep all charge details intact
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        original = CommittedCharge(charge_id=uuid4(), session_id=uuid4(), name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        charge_repository.add(original)
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        service.mark_paid(original.charge_id)

        assert len(charge_repository.charges) == 1
        updated = charge_repository.charges[0]
        assert updated.charge_id == original.charge_id
        assert updated.session_id == original.session_id
        assert updated.name == original.name
        assert updated.amount == original.amount
        assert updated.due_date == original.due_date
        assert updated.recurring_rule_id == original.recurring_rule_id
        assert updated.status is ChargeStatus.PAID

    def test_mark_paid_does_not_require_active_session(self) -> None:
        # status transitions operate on the charge repository directly and do not need a live session
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        original = CommittedCharge(charge_id=uuid4(), session_id=uuid4(), name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        charge_repository.add(original)
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        service.mark_paid(original.charge_id)

        assert charge_repository.charges[0].status is ChargeStatus.PAID

    def test_mark_paid_rejects_invalid_charge_id(self) -> None:
        # non-UUID identifiers are not valid charge references
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        with pytest.raises(ValidationError):
            service.mark_paid("not-a-uuid")  # type: ignore[arg-type]

    def test_mark_paid_creates_next_recurring_charge(self, monkeypatch: pytest.MonkeyPatch, active_session: AppSession) -> None:
        # recurring charges must spawn the next occurrence as soon as the current one is paid
        class _FixedDate(date):

            @classmethod
            def today(cls) -> date:
                return cls(2026, 4, 10)

        monkeypatch.setattr("expense_tracker.application.services.charge_service.date", _FixedDate)

        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        original_charge = service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)

        service.mark_paid(original_charge.charge_id)

        assert len(charge_repository.charges) == 2
        paid_charge = charge_repository.get_by_id(original_charge.charge_id)
        assert paid_charge is not None
        assert paid_charge.status is ChargeStatus.PAID

        next_charge = [charge for charge in charge_repository.charges if charge.charge_id != original_charge.charge_id][0]
        assert next_charge.session_id == active_session.session_id
        assert next_charge.name == "Rent"
        assert next_charge.amount == Decimal("500.00")
        assert next_charge.due_date == date(2026, 5, 15)
        assert next_charge.status is ChargeStatus.UPCOMING
        assert next_charge.recurring_rule_id == recurring_rule_repository.rules[0].rule_id

    def test_mark_paid_rejects_missing_charge(self) -> None:
        # charge identifiers must resolve to a stored committed charge before status changes happen
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        with pytest.raises(ApplicationError):
            service.mark_paid(uuid4())


class TestChargeServiceRecurringDueDateHelper:

    def test_helper_returns_same_month_due_date_before_target_day(self) -> None:
        # a future day in the same month should stay in the current month
        service = _build_charge_service(_InMemorySessionRepository(), _InMemoryChargeRepository())

        result = service._next_recurring_due_date(date(2026, 4, 10), 15)

        assert result == date(2026, 4, 15)

    def test_helper_rolls_forward_to_next_month_after_target_day(self) -> None:
        # once the day has passed, the next occurrence moves into the following month
        service = _build_charge_service(_InMemorySessionRepository(), _InMemoryChargeRepository())

        result = service._next_recurring_due_date(date(2026, 4, 20), 15)

        assert result == date(2026, 5, 15)

    def test_helper_rolls_december_to_january(self) -> None:
        # December should roll into January of the next year without special handling elsewhere
        service = _build_charge_service(_InMemorySessionRepository(), _InMemoryChargeRepository())

        result = service._next_recurring_due_date(date(2026, 12, 31), 15)

        assert result == date(2027, 1, 15)

    @pytest.mark.parametrize(
        "reference_date,day_of_month,expected",
        [
            pytest.param(date(2026, 3, 1), 29, date(2026, 3, 29), id="29th stays in a long month"),
            pytest.param(date(2026, 4, 1), 30, date(2026, 4, 30), id="30th stays in a thirty-day month"),
            pytest.param(date(2026, 4, 1), 31, date(2026, 4, 30), id="31st clamps to month end when needed"),
            pytest.param(date(2026, 1, 31), 31, date(2026, 2, 28), id="short february clamps to 28"),
            pytest.param(date(2024, 1, 31), 31, date(2024, 2, 29), id="leap february clamps to 29"),
            pytest.param(date(2026, 4, 30), 31, date(2026, 5, 31), id="thirty day month still reaches 31 next month"),
            pytest.param(date(2026, 1, 31), 30, date(2026, 2, 28), id="30th clamps in short february"),
            pytest.param(date(2026, 1, 31), 29, date(2026, 2, 28), id="29th clamps in non-leap february"),
        ],
    )
    def test_helper_clamps_short_months(self, reference_date: date, day_of_month: int, expected: date) -> None:
        # short months must still produce a valid calendar date for the recurring rule
        service = _build_charge_service(_InMemorySessionRepository(), _InMemoryChargeRepository())

        result = service._next_recurring_due_date(reference_date, day_of_month)

        assert result == expected


class TestChargeServiceAddRecurringCharge:

    def test_add_recurring_charge_persists_rule_and_first_charge(self, monkeypatch: pytest.MonkeyPatch, active_session: AppSession) -> None:
        # valid recurring input must create a rule and the first committed charge occurrence
        class _FixedDate(date):

            @classmethod
            def today(cls) -> date:
                return cls(2026, 4, 10)

        monkeypatch.setattr("expense_tracker.application.services.charge_service.date", _FixedDate)

        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        charge = service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)

        assert len(recurring_rule_repository.rules) == 1
        assert len(charge_repository.charges) == 1
        rule = recurring_rule_repository.rules[0]
        assert rule.session_id == active_session.session_id
        assert rule.name == "Rent"
        assert rule.amount == Decimal("500.00")
        assert rule.frequency is RecurringFrequency.MONTHLY
        assert rule.day_of_month == 15
        assert rule.reminder_days == 3
        assert charge.recurring_rule_id == rule.rule_id
        assert charge.due_date == date(2026, 4, 15)
        assert charge.status is ChargeStatus.UPCOMING

    def test_add_recurring_charge_rejects_when_no_active_session(self) -> None:
        # recurring charges still require an active session before creation
        session_repository = _InMemorySessionRepository(active_session=None)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        with pytest.raises(ApplicationError):
            service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount"),
            pytest.param(Decimal("-1.00"), id="negative amount"),
        ],
    )
    def test_add_recurring_charge_rejects_non_positive_amount(self, active_session: AppSession, amount: Decimal) -> None:
        # recurring charges must represent an actual positive obligation
        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        with pytest.raises(ValidationError):
            service.add_recurring_charge(name="Rent", amount=amount, day_of_month=15)

    @pytest.mark.parametrize(
        "day_of_month",
        [
            pytest.param(0, id="below lower boundary"),
            pytest.param(32, id="above upper boundary"),
        ],
    )
    def test_add_recurring_charge_rejects_invalid_day_of_month(self, active_session: AppSession, day_of_month: int) -> None:
        # recurring rules only accept calendar days in the inclusive 1..31 range
        session_repository = _InMemorySessionRepository(active_session=active_session)
        charge_repository = _InMemoryChargeRepository()
        recurring_rule_repository = _InMemoryRecurringRuleRepository()
        service = _build_charge_service(session_repository, charge_repository, recurring_rule_repository)

        with pytest.raises(ValidationError):
            service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=day_of_month)


