"""Tests for SessionService."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from expense_tracker.application.services.session_service import SessionService
from expense_tracker.domain.models import AppSession
from expense_tracker.ports.repositories import SessionRepository
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class FakeSessionRepository(SessionRepository):
    """In-memory session repository for testing."""

    def __init__(self) -> None:
        """Initialize fake repository."""
        self._active: AppSession | None = None

    def create(self, session: AppSession) -> None:
        """Create a session."""
        self._active = session

    def get_active(self) -> AppSession | None:
        """Get active session."""
        return self._active

    def clear(self) -> None:
        """Clear active session."""
        self._active = None


class TestSessionServiceInitSession:
    """Tests for SessionService.init_session()."""

    def test_init_session_with_positive_balance(self) -> None:
        """Create a session with positive opening balance."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        opening_balance = Decimal("5000")
        service.init_session(opening_balance)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == opening_balance
        assert isinstance(session.session_id, UUID)
        assert session.start_date == date.today()

    def test_init_session_with_zero_balance(self) -> None:
        """Create a session with zero opening balance."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        service.init_session(Decimal("0"))

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == Decimal("0")

    def test_init_session_with_large_balance(self) -> None:
        """Create a session with large opening balance."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        large_balance = Decimal("999999")
        service.init_session(large_balance)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == large_balance

    def test_init_session_with_decimal_precision(self) -> None:
        """Create a session with decimal precision in balance."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        precise_balance = Decimal("1234.56")
        service.init_session(precise_balance)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == precise_balance

    def test_init_session_rejects_negative_balance(self) -> None:
        """Reject session creation with negative opening balance."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        with pytest.raises(ValidationError, match="Opening balance cannot be negative"):
            service.init_session(Decimal("-100"))

    def test_init_session_rejects_duplicate_active_session(self) -> None:
        """Reject session creation when active session exists."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        service.init_session(Decimal("1000"))

        with pytest.raises(ApplicationError, match="An active session already exists"):
            service.init_session(Decimal("2000"))

    def test_init_session_sets_unique_ids(self) -> None:
        """Each session gets a unique session ID."""
        repo1 = FakeSessionRepository()
        service1 = SessionService(repo1)
        service1.init_session(Decimal("1000"))
        session1_id = service1.get_active().session_id

        repo2 = FakeSessionRepository()
        service2 = SessionService(repo2)
        service2.init_session(Decimal("2000"))
        session2_id = service2.get_active().session_id

        assert session1_id != session2_id

    def test_init_session_sets_start_date_to_today(self) -> None:
        """Session start date is set to today."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        service.init_session(Decimal("1000"))

        session = service.get_active()
        assert session.start_date == date.today()


class TestSessionServiceGetActive:
    """Tests for SessionService.get_active()."""

    def test_get_active_returns_none_when_no_session(self) -> None:
        """Return None when no active session."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        result = service.get_active()
        assert result is None

    def test_get_active_returns_active_session(self) -> None:
        """Return the active session when one exists."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        opening_balance = Decimal("5000")
        service.init_session(opening_balance)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == opening_balance

    def test_get_active_returns_same_session_multiple_calls(self) -> None:
        """Multiple calls to get_active return the same session."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        service.init_session(Decimal("5000"))

        session1 = service.get_active()
        session2 = service.get_active()

        assert session1 is not None
        assert session2 is not None
        assert session1.session_id == session2.session_id

    def test_get_active_returns_all_session_fields(self) -> None:
        """get_active returns all session fields correctly."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        opening_balance = Decimal("12345.67")
        service.init_session(opening_balance)

        session = service.get_active()
        assert session is not None
        assert isinstance(session.session_id, UUID)
        assert isinstance(session.start_date, date)
        assert session.opening_balance == opening_balance


class TestSessionServiceIsolation:
    """Tests for session isolation between repositories."""

    def test_separate_services_have_separate_sessions(self) -> None:
        """Sessions are isolated between different service instances."""
        repo1 = FakeSessionRepository()
        service1 = SessionService(repo1)
        service1.init_session(Decimal("1000"))
        session1 = service1.get_active()

        repo2 = FakeSessionRepository()
        service2 = SessionService(repo2)

        # Service 2 should have no active session
        session2 = service2.get_active()
        assert session2 is None

        # Service 2 can create its own session
        service2.init_session(Decimal("2000"))
        session2_after = service2.get_active()
        assert session2_after is not None
        assert session2_after.opening_balance == Decimal("2000")

        # Sessions should have different IDs
        assert session1.session_id != session2_after.session_id

    def test_services_with_same_repo_share_session(self) -> None:
        """Services using the same repository see the same session."""
        repo = FakeSessionRepository()

        service1 = SessionService(repo)
        service1.init_session(Decimal("1000"))
        session1 = service1.get_active()

        service2 = SessionService(repo)
        session2 = service2.get_active()

        assert session1 is not None
        assert session2 is not None
        assert session1.session_id == session2.session_id


class TestSessionServiceEdgeCases:
    """Edge case tests for SessionService."""

    def test_init_session_with_very_small_decimal(self) -> None:
        """Handle very small decimal amounts."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        tiny_amount = Decimal("0.01")
        service.init_session(tiny_amount)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == tiny_amount

    def test_init_session_with_many_decimal_places(self) -> None:
        """Handle amounts with multiple decimal places."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        precise = Decimal("1234.567890")
        service.init_session(precise)

        session = service.get_active()
        assert session is not None
        assert session.opening_balance == precise

    def test_session_data_integrity_after_creation(self) -> None:
        """Session data is not modified after creation."""
        repo = FakeSessionRepository()
        service = SessionService(repo)

        original_balance = Decimal("5000")
        service.init_session(original_balance)

        session = service.get_active()
        assert session.opening_balance == original_balance

        # Get again to verify no modification
        session_again = service.get_active()
        assert session_again.opening_balance == original_balance
