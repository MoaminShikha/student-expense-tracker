from __future__ import annotations

from typing import Protocol
from uuid import UUID

from ..domain.models import AppSession, CommittedCharge, FuzzyCharge, FuzzyChargeStatus, IncomeEntry, RecurringRule, Transaction


class SessionRepository(Protocol):
    """Defines storage operations for application sessions."""

    def create(self, session: AppSession) -> None:
        """
        Persist a new active session.

        :param session: The session to persist.
        :return: None.
        """
        ...

    def get_active(self) -> AppSession | None:
        """
        Fetch the currently active session.

        :return: Active session if present; otherwise None.
        """
        ...


class IncomeRepository(Protocol):
    """Defines storage operations for income entries."""

    def add(self, entry: IncomeEntry) -> None:
        """
        Persist one income entry.

        :param entry: The income entry to persist.
        :return: None.
        """
        ...

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        """
        List income entries for a session.

        :param session_id: The session identifier.
        :return: Income entries for the session.
        """
        ...

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        """
        List income entries for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Income entries for the month.
        """
        ...


class ChargeRepository(Protocol):
    """Defines storage operations for committed charges."""

    def add(self, charge: CommittedCharge) -> None:
        """
        Persist one committed charge.

        :param charge: The committed charge to persist.
        :return: None.
        """
        ...

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        """
        List upcoming charges for a session.

        :param session_id: The session identifier.
        :return: Upcoming committed charges.
        """
        ...

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        """
        List committed charges for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Committed charges for the month.
        """
        ...

    def mark_paid(self, charge_id: UUID) -> None:
        """
        Mark a committed charge as paid.

        :param charge_id: Identifier of the charge to update.
        :return: None.
        """
        ...

    def get_by_id(self, charge_id: UUID) -> CommittedCharge | None:
        """
        Fetch a committed charge by identifier.

        :param charge_id: Identifier of the charge to fetch.
        :return: Matching committed charge if found; otherwise None.
        """
        ...


class RecurringRuleRepository(Protocol):
    """Defines storage operations for recurring charge rules."""

    def add(self, rule: RecurringRule) -> None:
        """
        Persist one recurring rule.

        :param rule: The recurring rule to persist.
        :return: None.
        """
        ...

    def get_by_id(self, rule_id: UUID) -> RecurringRule | None:
        """
        Fetch a recurring rule by identifier.

        :param rule_id: The rule identifier.
        :return: Matching rule if found; otherwise None.
        """
        ...

    def list_for_session(self, session_id: UUID) -> list[RecurringRule]:
        """
        List all recurring rules for a session.

        :param session_id: The session identifier.
        :return: Recurring rules for the session.
        """
        ...


class FuzzyChargeRepository(Protocol):
    """Defines storage operations for fuzzy entries."""

    def add(self, charge: FuzzyCharge) -> None:
        """
        Persist one fuzzy entry.

        :param charge: The fuzzy entry to persist.
        :return: None.
        """
        ...

    def get_by_id(self, fuzzy_id: UUID) -> FuzzyCharge | None:
        """
        Fetch one fuzzy entry by identifier.

        :param fuzzy_id: Identifier of the fuzzy entry.
        :return: Matching fuzzy entry if found; otherwise None.
        """
        ...

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        """
        List pending fuzzy entries for a session.

        :param session_id: The session identifier.
        :return: Pending fuzzy entries for the session.
        """
        ...

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        """
        Update the status of one fuzzy entry.

        :param fuzzy_id: Identifier of the fuzzy entry.
        :param status: New fuzzy entry status.
        :return: None.
        """
        ...

    def update(self, charge: FuzzyCharge) -> None:
        """
        Persist full-state changes to one fuzzy entry.

        :param charge: Updated fuzzy entry.
        :return: None.
        """
        ...


class TransactionRepository(Protocol):
    """Defines storage operations for spend transactions."""

    def add(self, transaction: Transaction) -> None:
        """
        Persist one spend transaction.

        :param transaction: The transaction to persist.
        :return: None.
        """
        ...

    def list_for_session(self, session_id: UUID) -> list[Transaction]:
        """
        List all spend transactions for a session.

        :param session_id: The session identifier.
        :return: All transactions for the session.
        """
        ...

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        """
        List spend transactions for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Transactions for the month.
        """
        ...

