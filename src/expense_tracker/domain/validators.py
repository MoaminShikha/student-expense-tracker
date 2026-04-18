from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from .models import TransactionCategory
from .models.income import IncomeSourceTag

from ..shared.exceptions import ValidationError


def parse_opening_balance(raw_value: str) -> Decimal:
    """
    Parse an opening balance string into Decimal.

    :param raw_value: Raw balance value from user input.
    :return: Parsed Decimal opening balance.
    """
    try:
        opening_balance = Decimal(raw_value)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError("Opening balance must be a valid decimal value.") from exc

    if opening_balance < 0:
        raise ValidationError("Opening balance cannot be negative.")

    return opening_balance


def parse_amount(raw_value: str) -> Decimal:
    """
    Parse an amount string into Decimal.

    :param raw_value: Raw amount value from user input.
    :return: Parsed Decimal amount.
    """
    try:
        amount = Decimal(raw_value)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError("Amount must be a valid decimal value.") from exc

    if amount < 0:
        raise ValidationError("Amount cannot be negative.")

    return amount


def parse_income_source_tag(raw_value: str) -> IncomeSourceTag:
    """
    Parse an income source tag string.

    :param raw_value: Raw tag value from user input.
    :return: Parsed income source tag.
    """
    normalized_value = raw_value.strip().lower()

    if not normalized_value:
        raise ValidationError("Income source tag cannot be empty.")

    try:
        return IncomeSourceTag(normalized_value)
    except ValueError as exc:
        valid_tags = ", ".join(tag.value for tag in IncomeSourceTag)
        raise ValidationError(f"Invalid income source tag. Valid options are: {valid_tags}.") from exc


def parse_due_date(raw_value: str) -> date:
    """
    Parse a due date string into a date object.

    :param raw_value: Raw due date value from user input (expected format: YYYY-MM-DD).
    :return: Parsed date object.
    """
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValidationError("Due date must be in YYYY-MM-DD format.") from exc


def parse_day_of_month(raw_value: str) -> int:
    """
    Parse a day of month string into an integer.

    :param raw_value: Raw day of month value from user input.
    :return: Parsed day of month as an integer.
    """
    try:
        day = int(raw_value)
    except ValueError as exc:
        raise ValidationError("Day of month must be an integer.") from exc

    if not 1 <= day <= 31:
        raise ValidationError("Day of month must be between 1 and 31.")

    return day


def parse_transaction_category(raw_value: str | None) -> TransactionCategory | None:
    """
    Parse a transaction category string into a TransactionCategory enum.

    :param raw_value: Raw category value from user input (can be None).
    :return: Parsed TransactionCategory enum or None if input is None.
    """
    if raw_value is None:
        return None

    try:
        return TransactionCategory(raw_value.strip().lower())
    except ValueError as exc:
        valid_categories = ", ".join([cat.value for cat in TransactionCategory])
        raise ValidationError(f"Invalid transaction category. Valid options are: {valid_categories}.") from exc


def parse_transaction_description(raw_value: str) -> str:
    """
    Parse and validate a transaction description.

    :param raw_value: Raw description text from user input.
    :return: Normalized non-empty description.
    """
    if not isinstance(raw_value, str):
        raise ValidationError("Transaction description is invalid.")

    normalized_value = raw_value.strip()
    if not normalized_value:
        raise ValidationError("Transaction description cannot be empty.")

    return normalized_value

