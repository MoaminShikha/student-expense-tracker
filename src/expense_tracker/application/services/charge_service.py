from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from ...domain.models import ChargeStatus, CommittedCharge, RecurringFrequency, RecurringRule
from ...ports.repositories import ChargeRepository, RecurringRuleRepository, SessionRepository
from ...shared.exceptions import ApplicationError, ValidationError


class ChargeService:
    """Coordinates committed-charge lifecycle operations for an active session."""

    def __init__(self, session_repository: SessionRepository, charge_repository: ChargeRepository,
                 recurring_rule_repository: RecurringRuleRepository, logger: logging.Logger | None = None) -> None:
        """
        Initialize the charge service.

        :param session_repository: Repository abstraction for session persistence.
        :param charge_repository: Repository abstraction for committed-charge persistence.
        :param recurring_rule_repository: Repository abstraction for recurring-rule persistence.
        :param logger: Optional logger for charge operations.
        :return: None.
        """
        self._session_repository = session_repository
        self._charge_repository = charge_repository
        self._recurring_rule_repository = recurring_rule_repository
        self._logger = logger or logging.getLogger(__name__)

    def add_charge(self, name: str, amount: Decimal, due_date: date) -> CommittedCharge:
        """
        Add one committed charge to the active session.

        :param name: Human-readable charge name.
        :param amount: Charge amount to commit.
        :param due_date: Calendar due date for the charge.
        :return: Persisted committed charge.
        """
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Charge name cannot be empty.")

        if amount <= 0:
            raise ValidationError("Charge amount must be greater than zero.")

        if not isinstance(due_date, date):
            raise ValidationError("Charge due date is invalid.")

        active_session = self._session_repository.get_active()
        if active_session is None:
            raise ApplicationError("No active session. Start a session before adding charges.")

        charge = CommittedCharge(charge_id=uuid4(), session_id=active_session.session_id, name=normalized_name,
                                 amount=amount, due_date=due_date, status=ChargeStatus.UPCOMING)
        self._charge_repository.add(charge)
        self._logger.info("Added committed charge %s for session %s.", charge.charge_id, active_session.session_id)
        return charge

    def mark_paid(self, charge_id: UUID) -> None:
        """
        Mark one committed charge as paid.

        :param charge_id: Identifier of the charge to update.
        :return: None.
        """
        if not isinstance(charge_id, UUID):
            raise ValidationError("Charge identifier is invalid.")

        charge = self._charge_repository.get_by_id(charge_id)
        if charge is None:
            raise ApplicationError("Charge not found.")

        next_charge: CommittedCharge | None = None
        if charge.recurring_rule_id is not None:
            recurring_rule = self._recurring_rule_repository.get_by_id(charge.recurring_rule_id)
            if recurring_rule is None:
                raise ApplicationError("Recurring rule not found.")

            next_charge = CommittedCharge(
                charge_id=uuid4(),
                session_id=charge.session_id,
                name=charge.name,
                amount=charge.amount,
                due_date=self._next_recurring_due_date(charge.due_date, recurring_rule.day_of_month),
                status=ChargeStatus.UPCOMING,
                recurring_rule_id=recurring_rule.rule_id,
            )

        self._charge_repository.mark_paid(charge_id)

        if next_charge is not None:
            self._charge_repository.add(next_charge)

        self._logger.info("Marked committed charge %s as paid.", charge_id)

    def add_recurring_charge(self, name: str, amount: Decimal, day_of_month: int,
                             reminder_days: int = 3) -> CommittedCharge:
        """
        Add one monthly recurring charge and create its first occurrence.

        :param name: Human-readable recurring charge name.
        :param amount: Charge amount to commit.
        :param day_of_month: Day of month for future occurrences.
        :param reminder_days: Reminder lead time in days.
        :return: First persisted committed charge occurrence.
        """
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Charge name cannot be empty.")

        if amount <= 0:
            raise ValidationError("Charge amount must be greater than zero.")

        if not 1 <= day_of_month <= 31:
            raise ValidationError("Recurring day of month must be between 1 and 31.")

        if reminder_days < 0:
            raise ValidationError("Reminder days cannot be negative.")

        active_session = self._session_repository.get_active()
        if active_session is None:
            raise ApplicationError("No active session. Start a session before adding charges.")

        rule = RecurringRule(rule_id=uuid4(),
                             session_id=active_session.session_id,
                             name=normalized_name,
                             amount=amount,
                             frequency=RecurringFrequency.MONTHLY,
                             day_of_month=day_of_month,
                             reminder_days=reminder_days, )
        self._recurring_rule_repository.add(rule)

        charge = CommittedCharge(charge_id=uuid4(),
                                 session_id=active_session.session_id,
                                 name=normalized_name,
                                 amount=amount,
                                 due_date=self._next_recurring_due_date(date.today(), day_of_month),
                                 status=ChargeStatus.UPCOMING,
                                 recurring_rule_id=rule.rule_id, )

        self._charge_repository.add(charge)
        self._logger.info("Added recurring charge %s for session %s.", charge.charge_id, active_session.session_id)
        return charge

    def get_charges_for_month(self, session_id: UUID, year: int, month: int) -> list:
        """Return upcoming committed charges due in the given month."""
        return [
            c for c in self._charge_repository.list_for_month(session_id, year, month)
            if c.status == ChargeStatus.UPCOMING
        ]

    def list_all_for_month(self, session_id: UUID, year: int, month: int) -> list:
        """Return all committed charges due in the given month (any status)."""
        return self._charge_repository.list_for_month(session_id, year, month)

    def get_monthly_committed_total(self, session_id: UUID, year: int, month: int) -> Decimal:
        """Return the sum of upcoming committed charges due in the given month."""
        charges = self.get_charges_for_month(session_id, year, month)
        return sum((c.amount for c in charges), Decimal("0"))

    @staticmethod
    def _next_recurring_due_date(reference_date: date, day_of_month: int) -> date:
        """
        Calculate the next recurring due date from a reference date.

        :param reference_date: Date to calculate forward from.
        :param day_of_month: Desired recurring day within the month.
        :return: Next valid due date.
        """
        if not 1 <= day_of_month <= 31:
            raise ValidationError("Recurring day of month must be between 1 and 31.")

        year = reference_date.year
        month = reference_date.month

        last_day = monthrange(year, month)[1]
        candidate = date(year, month, min(day_of_month, last_day))

        if candidate <= reference_date:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

            last_day = monthrange(year, month)[1]
            candidate = date(year, month, min(day_of_month, last_day))

        return candidate
