from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from expense_tracker.domain.models import ChargeStatus, CommittedCharge
from expense_tracker.domain.validators import parse_amount, parse_opening_balance
from expense_tracker.infrastructure.json.repositories import JsonChargeRepository
from expense_tracker.shared.exceptions import ValidationError


def _charge(status: ChargeStatus = ChargeStatus.UPCOMING) -> CommittedCharge:
    return CommittedCharge(
        charge_id=uuid4(),
        session_id=uuid4(),
        name="Rent",
        amount=Decimal("1200"),
        due_date=date(2026, 6, 1),
        status=status,
    )


class TestCommittedChargeBehavior:
    def test_mark_paid_returns_paid_copy_without_mutating_original(self) -> None:
        original = _charge()
        paid = original.mark_paid()

        assert paid.status is ChargeStatus.PAID
        assert paid.is_paid is True
        assert original.status is ChargeStatus.UPCOMING  # frozen, untouched
        assert paid.charge_id == original.charge_id

    def test_is_paid_reflects_status(self) -> None:
        assert _charge(ChargeStatus.UPCOMING).is_paid is False
        assert _charge(ChargeStatus.PAID).is_paid is True


class TestNonFiniteAmountsRejected:
    @pytest.mark.parametrize("raw", ["NaN", "Infinity", "-Infinity", "inf"])
    def test_parse_amount_rejects_non_finite(self, raw: str) -> None:
        with pytest.raises(ValidationError):
            parse_amount(raw)

    @pytest.mark.parametrize("raw", ["NaN", "Infinity"])
    def test_parse_opening_balance_rejects_non_finite(self, raw: str) -> None:
        with pytest.raises(ValidationError):
            parse_opening_balance(raw)


class TestChargeRepositoryMarkPaid:
    def test_mark_paid_persists_via_domain_transition(self, tmp_path) -> None:
        repo = JsonChargeRepository(tmp_path / "charges.json")
        charge = _charge()
        repo.add(charge)

        repo.mark_paid(charge.charge_id)

        stored = repo.get_by_id(charge.charge_id)
        assert stored is not None
        assert stored.is_paid is True

    def test_mark_paid_leaves_other_charges_untouched(self, tmp_path) -> None:
        repo = JsonChargeRepository(tmp_path / "charges.json")
        target, other = _charge(), _charge()
        repo.add(target)
        repo.add(other)

        repo.mark_paid(target.charge_id)

        assert repo.get_by_id(other.charge_id).status is ChargeStatus.UPCOMING

    def test_cache_observes_external_write(self, tmp_path) -> None:
        path = tmp_path / "charges.json"
        repo = JsonChargeRepository(path)
        charge = _charge()
        repo.add(charge)
        assert len(repo.list_upcoming(charge.session_id)) == 1

        # A second adapter (e.g. another process) appends to the same file.
        JsonChargeRepository(path).add(CommittedCharge(
            charge_id=uuid4(), session_id=charge.session_id, name="Gym",
            amount=Decimal("99"), due_date=date(2026, 6, 5), status=ChargeStatus.UPCOMING,
        ))

        # mtime-keyed cache must reload rather than serve a stale single record.
        assert len(repo.list_upcoming(charge.session_id)) == 2
