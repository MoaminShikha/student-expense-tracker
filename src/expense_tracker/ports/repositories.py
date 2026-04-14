from __future__ import annotations

from typing import Protocol
from uuid import UUID

from ..domain.models import AppSession, CommittedCharge, FuzzyCharge, FuzzyChargeStatus, IncomeEntry, Transaction


class SessionRepository(Protocol):
    """Defines storage operations for application sessions."""

    def create(self, session: AppSession) -> None:
        """
        Persist a new active session.

        :param session: The session to persist.
        :return: None.
        """
        pass

    def get_active(self) -> AppSession | None:
        """
        Fetch the currently active session.

        :return: Active session if present; otherwise None.
        """
        pass


class IncomeRepository(Protocol):
    """Defines storage operations for income entries."""

    def add(self, entry: IncomeEntry) -> None:
        """
        Persist one income entry.

        :param entry: The income entry to persist.
        :return: None.
        """
        pass

    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]:
        """
        List income entries for a session.

        :param session_id: The session identifier.
        :return: Income entries for the session.
        """
        pass

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]:
        """
        List income entries for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Income entries for the month.
        """
        pass


class ChargeRepository(Protocol):
    """Defines storage operations for committed charges."""

    def add(self, charge: CommittedCharge) -> None:
        """
        Persist one committed charge.

        :param charge: The committed charge to persist.
        :return: None.
        """
        pass

    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]:
        """
        List upcoming charges for a session.

        :param session_id: The session identifier.
        :return: Upcoming committed charges.
        """
        pass

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]:
        """
        List committed charges for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Committed charges for the month.
        """
        pass

    def mark_paid(self, charge_id: UUID) -> None:
        """
        Mark a committed charge as paid.

        :param charge_id: Identifier of the charge to update.
        :return: None.
        """
        pass


class FuzzyChargeRepository(Protocol):
    """Defines storage operations for fuzzy charges."""

    def add(self, charge: FuzzyCharge) -> None:
        """
        Persist one fuzzy charge.

        :param charge: The fuzzy charge to persist.
        :return: None.
        """
        pass

    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]:
        """
        List pending fuzzy charges for a session.

        :param session_id: The session identifier.
        :return: Pending fuzzy charges for the session.
        """
        pass

    def update_status(self, fuzzy_id: UUID, status: FuzzyChargeStatus) -> None:
        """
        Update the status of one fuzzy charge.

        :param fuzzy_id: Identifier of the fuzzy charge.
        :param status: New fuzzy charge status.
        :return: None.
        """
        pass


class TransactionRepository(Protocol):
    """Defines storage operations for spend transactions."""

    def add(self, transaction: Transaction) -> None:
        """
        Persist one spend transaction.

        :param transaction: The transaction to persist.
        :return: None.
        """
        pass

    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]:
        """
        List spend transactions for one calendar month.

        :param session_id: The session identifier.
        :param year: Calendar year filter.
        :param month: Calendar month filter.
        :return: Transactions for the month.
        """
        pass


