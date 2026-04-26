from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from expense_tracker.application.services import ChargeService
from expense_tracker.domain.models import AppSession, ChargeStatus, CommittedCharge, RecurringFrequency
from expense_tracker.infrastructure.json.repositories import JsonChargeRepository, JsonRecurringRuleRepository, JsonSessionRepository
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


def _build_charge_service(tmp_path: Path, active_session: AppSession | None = None) -> tuple[ChargeService, JsonSessionRepository, JsonChargeRepository, JsonRecurringRuleRepository]:
    session_repo = JsonSessionRepository(tmp_path / "session.json")
    charge_repo = JsonChargeRepository(tmp_path / "charges.json")
    rule_repo = JsonRecurringRuleRepository(tmp_path / "rules.json")
    if active_session is not None:
        session_repo.create(active_session)
    service = ChargeService(
        session_repository=session_repo,
        charge_repository=charge_repo,
        recurring_rule_repository=rule_repo,
    )
    return service, session_repo, charge_repo, rule_repo


@pytest.fixture
def active_session() -> AppSession:
    """Provide one active session for charge service tests."""
    return AppSession(session_id=uuid4(), start_date=date(2026, 4, 1), opening_balance=Decimal("1000"))


class TestChargeServiceAddCharge:

    def test_add_charge_persists_committed_charge(self, tmp_path, active_session: AppSession) -> None:
        # valid input with an active session must create and persist one committed charge
        service, _, charge_repo, _ = _build_charge_service(tmp_path, active_session)

        charge = service.add_charge(name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20))

        charges = charge_repo.list_upcoming(active_session.session_id)
        assert len(charges) == 1
        assert charges[0] == charge
        assert charge.session_id == active_session.session_id
        assert charge.name == "Rent"
        assert charge.amount == Decimal("500.00")
        assert charge.due_date == date(2026, 4, 20)
        assert charge.status is ChargeStatus.UPCOMING

    def test_add_charge_rejects_when_no_active_session(self, tmp_path) -> None:
        # service must fail fast if the caller tries to add a charge before starting a session
        service, _, _, _ = _build_charge_service(tmp_path, active_session=None)

        with pytest.raises(ApplicationError):
            service.add_charge(name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20))

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount"),
            pytest.param(Decimal("-1.00"), id="negative amount"),
        ],
    )
    def test_add_charge_rejects_non_positive_amount(self, tmp_path, active_session: AppSession, amount: Decimal) -> None:
        # committed charges must represent an actual positive obligation
        service, _, _, _ = _build_charge_service(tmp_path, active_session)

        with pytest.raises(ValidationError):
            service.add_charge(name="Rent", amount=amount, due_date=date(2026, 4, 20))

    def test_add_charge_rejects_blank_name(self, tmp_path, active_session: AppSession) -> None:
        # blank names create unusable charge records and are not allowed
        service, _, _, _ = _build_charge_service(tmp_path, active_session)

        with pytest.raises(ValidationError):
            service.add_charge(name="   ", amount=Decimal("500.00"), due_date=date(2026, 4, 20))


class TestChargeServiceMarkPaid:

    def test_mark_paid_updates_matching_charge_status(self, tmp_path) -> None:
        # mark_paid must flip only the status and keep all charge details intact
        service, _, charge_repo, _ = _build_charge_service(tmp_path, active_session=None)
        original = CommittedCharge(charge_id=uuid4(), session_id=uuid4(), name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        charge_repo.add(original)

        service.mark_paid(original.charge_id)

        updated = charge_repo.get_by_id(original.charge_id)
        assert updated is not None
        assert updated.charge_id == original.charge_id
        assert updated.session_id == original.session_id
        assert updated.name == original.name
        assert updated.amount == original.amount
        assert updated.due_date == original.due_date
        assert updated.recurring_rule_id == original.recurring_rule_id
        assert updated.status is ChargeStatus.PAID

    def test_mark_paid_does_not_require_active_session(self, tmp_path) -> None:
        # status transitions operate on the charge repository directly and do not need a live session
        service, _, charge_repo, _ = _build_charge_service(tmp_path, active_session=None)
        original = CommittedCharge(charge_id=uuid4(), session_id=uuid4(), name="Rent", amount=Decimal("500.00"), due_date=date(2026, 4, 20), status=ChargeStatus.UPCOMING)
        charge_repo.add(original)

        service.mark_paid(original.charge_id)

        assert charge_repo.get_by_id(original.charge_id).status is ChargeStatus.PAID

    def test_mark_paid_rejects_invalid_charge_id(self, tmp_path) -> None:
        # non-UUID identifiers are not valid charge references
        service, _, _, _ = _build_charge_service(tmp_path, active_session=None)

        with pytest.raises(ValidationError):
            service.mark_paid("not-a-uuid")  # type: ignore[arg-type]

    def test_mark_paid_creates_next_recurring_charge(self, tmp_path, monkeypatch: pytest.MonkeyPatch, active_session: AppSession) -> None:
        # recurring charges must spawn the next occurrence as soon as the current one is paid
        class _FixedDate(date):

            @classmethod
            def today(cls) -> date:
                return cls(2026, 4, 10)

        monkeypatch.setattr("expense_tracker.application.services.charge_service.date", _FixedDate)
        service, _, charge_repo, rule_repo = _build_charge_service(tmp_path, active_session)

        original_charge = service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)
        service.mark_paid(original_charge.charge_id)

        all_charges = charge_repo.list_for_month(active_session.session_id, 2026, 4) + charge_repo.list_for_month(active_session.session_id, 2026, 5)
        assert len(all_charges) == 2
        paid_charge = charge_repo.get_by_id(original_charge.charge_id)
        assert paid_charge is not None
        assert paid_charge.status is ChargeStatus.PAID

        next_charge = [c for c in all_charges if c.charge_id != original_charge.charge_id][0]
        assert next_charge.session_id == active_session.session_id
        assert next_charge.name == "Rent"
        assert next_charge.amount == Decimal("500.00")
        assert next_charge.due_date == date(2026, 5, 15)
        assert next_charge.status is ChargeStatus.UPCOMING
        rules = rule_repo.list_for_session(active_session.session_id)
        assert next_charge.recurring_rule_id == rules[0].rule_id

    def test_mark_paid_rejects_missing_charge(self, tmp_path) -> None:
        # charge identifiers must resolve to a stored committed charge before status changes happen
        service, _, _, _ = _build_charge_service(tmp_path, active_session=None)

        with pytest.raises(ApplicationError):
            service.mark_paid(uuid4())


class TestChargeServiceRecurringDueDateHelper:

    def test_helper_returns_same_month_due_date_before_target_day(self, tmp_path) -> None:
        # a future day in the same month should stay in the current month
        service, _, _, _ = _build_charge_service(tmp_path)

        result = service._next_recurring_due_date(date(2026, 4, 10), 15)

        assert result == date(2026, 4, 15)

    def test_helper_rolls_forward_to_next_month_after_target_day(self, tmp_path) -> None:
        # once the day has passed, the next occurrence moves into the following month
        service, _, _, _ = _build_charge_service(tmp_path)

        result = service._next_recurring_due_date(date(2026, 4, 20), 15)

        assert result == date(2026, 5, 15)

    def test_helper_rolls_december_to_january(self, tmp_path) -> None:
        # December should roll into January of the next year without special handling elsewhere
        service, _, _, _ = _build_charge_service(tmp_path)

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
    def test_helper_clamps_short_months(self, tmp_path, reference_date: date, day_of_month: int, expected: date) -> None:
        # short months must still produce a valid calendar date for the recurring rule
        service, _, _, _ = _build_charge_service(tmp_path)

        result = service._next_recurring_due_date(reference_date, day_of_month)

        assert result == expected


class TestChargeServiceAddRecurringCharge:

    def test_add_recurring_charge_persists_rule_and_first_charge(self, tmp_path, monkeypatch: pytest.MonkeyPatch, active_session: AppSession) -> None:
        # valid recurring input must create a rule and the first committed charge occurrence
        class _FixedDate(date):

            @classmethod
            def today(cls) -> date:
                return cls(2026, 4, 10)

        monkeypatch.setattr("expense_tracker.application.services.charge_service.date", _FixedDate)
        service, _, charge_repo, rule_repo = _build_charge_service(tmp_path, active_session)

        charge = service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)

        rules = rule_repo.list_for_session(active_session.session_id)
        charges = charge_repo.list_upcoming(active_session.session_id)
        assert len(rules) == 1
        assert len(charges) == 1
        rule = rules[0]
        assert rule.session_id == active_session.session_id
        assert rule.name == "Rent"
        assert rule.amount == Decimal("500.00")
        assert rule.frequency is RecurringFrequency.MONTHLY
        assert rule.day_of_month == 15
        assert rule.reminder_days == 3
        assert charge.recurring_rule_id == rule.rule_id
        assert charge.due_date == date(2026, 4, 15)
        assert charge.status is ChargeStatus.UPCOMING

    def test_add_recurring_charge_rejects_when_no_active_session(self, tmp_path) -> None:
        # recurring charges still require an active session before creation
        service, _, _, _ = _build_charge_service(tmp_path, active_session=None)

        with pytest.raises(ApplicationError):
            service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=15)

    @pytest.mark.parametrize(
        "amount",
        [
            pytest.param(Decimal("0"), id="zero amount"),
            pytest.param(Decimal("-1.00"), id="negative amount"),
        ],
    )
    def test_add_recurring_charge_rejects_non_positive_amount(self, tmp_path, active_session: AppSession, amount: Decimal) -> None:
        # recurring charges must represent an actual positive obligation
        service, _, _, _ = _build_charge_service(tmp_path, active_session)

        with pytest.raises(ValidationError):
            service.add_recurring_charge(name="Rent", amount=amount, day_of_month=15)

    @pytest.mark.parametrize(
        "day_of_month",
        [
            pytest.param(0, id="below lower boundary"),
            pytest.param(32, id="above upper boundary"),
        ],
    )
    def test_add_recurring_charge_rejects_invalid_day_of_month(self, tmp_path, active_session: AppSession, day_of_month: int) -> None:
        # recurring rules only accept calendar days in the inclusive 1..31 range
        service, _, _, _ = _build_charge_service(tmp_path, active_session)

        with pytest.raises(ValidationError):
            service.add_recurring_charge(name="Rent", amount=Decimal("500.00"), day_of_month=day_of_month)
