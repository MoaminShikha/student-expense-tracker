"""Entity <-> JSON-record mappers.

Centralizes all (de)serialization that was previously hand-rolled and
duplicated across every repository adapter. Each mapper is the single place a
model's field names are written, so serialization can no longer drift between
the read and write paths.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from ...domain.models import (
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

class SessionMapper:
    """Mapper for :class:`AppSession`."""

    def to_dict(self, entity: AppSession) -> dict:
        return {
            "session_id": str(entity.session_id),
            "start_date": entity.start_date.isoformat(),
            "opening_balance": str(entity.opening_balance),
        }

    def from_dict(self, record: dict) -> AppSession:
        return AppSession(
            session_id=UUID(record["session_id"]),
            start_date=date.fromisoformat(record["start_date"]),
            opening_balance=Decimal(record["opening_balance"]),
        )


class IncomeMapper:
    """Mapper for :class:`IncomeEntry`."""

    def to_dict(self, entity: IncomeEntry) -> dict:
        return {
            "income_id": str(entity.income_id),
            "session_id": str(entity.session_id),
            "amount": str(entity.amount),
            "source_tag": entity.source_tag.value,
            "date": entity.date.isoformat(),
        }

    def from_dict(self, record: dict) -> IncomeEntry:
        return IncomeEntry(
            income_id=UUID(record["income_id"]),
            session_id=UUID(record["session_id"]),
            amount=Decimal(record["amount"]),
            source_tag=IncomeSourceTag(record["source_tag"]),
            date=date.fromisoformat(record["date"]),
        )


class ChargeMapper:
    """Mapper for :class:`CommittedCharge`."""

    def to_dict(self, entity: CommittedCharge) -> dict:
        return {
            "charge_id": str(entity.charge_id),
            "session_id": str(entity.session_id),
            "name": entity.name,
            "amount": str(entity.amount),
            "due_date": entity.due_date.isoformat(),
            "status": entity.status.value,
            "recurring_rule_id": str(entity.recurring_rule_id) if entity.recurring_rule_id else None,
        }

    def from_dict(self, record: dict) -> CommittedCharge:
        return CommittedCharge(
            charge_id=UUID(record["charge_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            amount=Decimal(record["amount"]),
            due_date=date.fromisoformat(record["due_date"]),
            status=ChargeStatus(record["status"]),
            recurring_rule_id=UUID(record["recurring_rule_id"]) if record["recurring_rule_id"] else None,
        )


class RecurringRuleMapper:
    """Mapper for :class:`RecurringRule`."""

    def to_dict(self, entity: RecurringRule) -> dict:
        return {
            "rule_id": str(entity.rule_id),
            "session_id": str(entity.session_id),
            "name": entity.name,
            "amount": str(entity.amount),
            "frequency": entity.frequency.value,
            "day_of_month": entity.day_of_month,
            "reminder_days": entity.reminder_days,
        }

    def from_dict(self, record: dict) -> RecurringRule:
        return RecurringRule(
            rule_id=UUID(record["rule_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            amount=Decimal(record["amount"]),
            frequency=RecurringFrequency(record["frequency"]),
            day_of_month=record["day_of_month"],
            reminder_days=record["reminder_days"],
        )


class TransactionMapper:
    """Mapper for :class:`Transaction`."""

    def to_dict(self, entity: Transaction) -> dict:
        return {
            "transaction_id": str(entity.transaction_id),
            "session_id": str(entity.session_id),
            "amount": str(entity.amount),
            "description": entity.description,
            "category": entity.category.value if entity.category else None,
            "date": entity.date.isoformat(),
        }

    def from_dict(self, record: dict) -> Transaction:
        return Transaction(
            transaction_id=UUID(record["transaction_id"]),
            session_id=UUID(record["session_id"]),
            amount=Decimal(record["amount"]),
            description=record["description"],
            category=TransactionCategory(record["category"]) if record["category"] else None,
            date=date.fromisoformat(record["date"]),
        )


class FuzzyChargeMapper:
    """Mapper for :class:`FuzzyCharge`."""

    def to_dict(self, entity: FuzzyCharge) -> dict:
        return {
            "fuzzy_id": str(entity.fuzzy_id),
            "session_id": str(entity.session_id),
            "name": entity.name,
            "direction": entity.direction.value,
            "status": entity.status.value,
            "expected_date": entity.expected_date.isoformat() if entity.expected_date else None,
            "estimated_amount": str(entity.estimated_amount) if entity.estimated_amount else None,
            "resolved_amount": str(entity.resolved_amount) if entity.resolved_amount else None,
            "resolved_date": entity.resolved_date.isoformat() if entity.resolved_date else None,
        }

    def from_dict(self, record: dict) -> FuzzyCharge:
        return FuzzyCharge(
            fuzzy_id=UUID(record["fuzzy_id"]),
            session_id=UUID(record["session_id"]),
            name=record["name"],
            direction=FuzzyEntryDirection(record["direction"]),
            status=FuzzyChargeStatus(record["status"]),
            expected_date=date.fromisoformat(record["expected_date"]) if record["expected_date"] else None,
            estimated_amount=Decimal(record["estimated_amount"]) if record["estimated_amount"] else None,
            resolved_amount=Decimal(record["resolved_amount"]) if record["resolved_amount"] else None,
            resolved_date=date.fromisoformat(record["resolved_date"]) if record["resolved_date"] else None,
        )
