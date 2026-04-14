from __future__ import annotations

from decimal import Decimal


class ValidationError(ValueError):
    """Represents invalid user input for domain operations."""


def parse_opening_balance(raw_value: str) -> Decimal:
    """
    Parse an opening balance string into Decimal.

    :param raw_value: Raw balance value from user input.
    :return: Parsed Decimal opening balance.
    """
    pass


