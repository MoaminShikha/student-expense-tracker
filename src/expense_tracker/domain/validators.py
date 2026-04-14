from __future__ import annotations

from decimal import Decimal, InvalidOperation

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


