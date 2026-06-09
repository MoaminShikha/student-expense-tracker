from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from expense_tracker.domain.models import IncomeSourceTag, TransactionCategory
from expense_tracker.domain.validators import (
    parse_amount,
    parse_day_of_month,
    parse_due_date,
    parse_income_source_tag,
    parse_opening_balance,
    parse_transaction_category,
    parse_transaction_description,
)
from expense_tracker.shared.exceptions import ValidationError


class TestParseOpeningBalance:

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("0", Decimal("0"),
                         id="zero",  # zero is a valid opening balance — student starts with nothing
                         ),
            pytest.param("100", Decimal("100"),
                         id="whole number",  # typical integer input parses correctly
                         ),
            pytest.param("100.25", Decimal("100.25"),
                         id="decimal",  # fractional amounts parse without precision loss
                         ),
        ],
    )
    def test_valid_values(self, raw_value: str, expected: Decimal) -> None:
        assert parse_opening_balance(raw_value) == expected

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("abc", id="non-numeric string"),   # letters cannot be parsed as Decimal
            pytest.param("", id="empty string"),            # blank input has no valid interpretation
            pytest.param("12.3.4", id="malformed decimal"), # two decimal points are not valid
        ],
    )
    def test_rejects_invalid_decimal(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_opening_balance(raw_value)

    def test_rejects_negative(self) -> None:
        # a negative opening balance has no valid meaning — student cannot start in debt
        with pytest.raises(ValidationError):
            parse_opening_balance("-1")


class TestParseAmount:

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("42", Decimal("42"),
                         id="whole number",  # typical integer amount parses correctly
                         ),
            pytest.param("42.75", Decimal("42.75"),
                         id="decimal",  # fractional amounts parse without precision loss
                         ),
        ],
    )
    def test_valid_values(self, raw_value: str, expected: Decimal) -> None:
        assert parse_amount(raw_value) == expected

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("abc", id="non-numeric string"),   # letters cannot be parsed as Decimal
            pytest.param("", id="empty string"),            # blank input has no valid interpretation
            pytest.param("1.2.3", id="malformed decimal"),  # two decimal points are not valid
        ],
    )
    def test_rejects_invalid_decimal(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_amount(raw_value)

    def test_rejects_negative(self) -> None:
        # negative amounts are not valid for charges or income entries
        with pytest.raises(ValidationError):
            parse_amount("-0.01")


class TestParseIncomeSourceTag:

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("scholarship", IncomeSourceTag.SCHOLARSHIP,
                         id="exact lowercase match",  # canonical form passes through
                         ),
            pytest.param("  FAMILY  ", IncomeSourceTag.FAMILY,
                         id="uppercase with surrounding whitespace",  # input is stripped and lowercased
                         ),
            pytest.param("Work", IncomeSourceTag.WORK,
                         id="mixed case",  # case-insensitive matching is required
                         ),
            pytest.param("other", IncomeSourceTag.OTHER,
                         id="other tag",  # catch-all tag parses correctly
                         ),
        ],
    )
    def test_valid_values(self, raw_value: str, expected: IncomeSourceTag) -> None:
        assert parse_income_source_tag(raw_value) is expected

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("", id="empty string"),        # blank input cannot map to any tag
            pytest.param("   ", id="whitespace only"),  # whitespace-only collapses to empty after strip
        ],
    )
    def test_rejects_empty(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_income_source_tag(raw_value)

    def test_rejects_unknown_value(self) -> None:
        # values outside the defined enum are rejected — no silent fallback to OTHER
        with pytest.raises(ValidationError):
            parse_income_source_tag("salary")


class TestParseDueDate:

    def test_valid_iso_date(self) -> None:
        # ISO 8601 (YYYY-MM-DD) is the only accepted format for now
        assert parse_due_date("2026-04-15") == date(2026, 4, 15)

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("15-04-2026", id="day-month-year format"),  # wrong order is rejected
            pytest.param("2026/04/15", id="slash separator"),        # slash separators are not ISO 8601
            pytest.param("2026-02-30", id="impossible date"),        # Feb 30 does not exist
            pytest.param("", id="empty string"),                     # blank input cannot be parsed
        ],
    )
    def test_rejects_invalid(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_due_date(raw_value)


class TestParseDayOfMonth:

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("1", 1,   id="lower boundary",  # 1 is the earliest valid day of month
                         ),
            pytest.param("15", 15, id="mid-range value", # typical mid-month day
                         ),
            pytest.param("31", 31, id="upper boundary",  # 31 is the highest valid day of month
                         ),
        ],
    )
    def test_valid_values(self, raw_value: str, expected: int) -> None:
        assert parse_day_of_month(raw_value) == expected

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("0",  id="below lower boundary"),  # 0 is not a valid calendar day
            pytest.param("32", id="above upper boundary"),  # 32 does not exist in any month
            pytest.param("-1", id="negative value"),        # negative days have no meaning
        ],
    )
    def test_rejects_out_of_range(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_day_of_month(raw_value)

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("abc", id="non-numeric string"),  # letters cannot be parsed as int
            pytest.param("1.5", id="float string"),        # fractional days are not valid
            pytest.param("",    id="empty string"),        # blank input cannot be parsed
        ],
    )
    def test_rejects_invalid_type(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_day_of_month(raw_value)


class TestParseTransactionCategory:

    def test_none_returns_none(self) -> None:
        # None is the explicit signal for "no category" — must pass through unchanged
        assert parse_transaction_category(None) is None

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("food", TransactionCategory.FOOD,
                         id="exact lowercase match",  # canonical form passes through
                         ),
            pytest.param(" TRANSPORT ", TransactionCategory.TRANSPORT,
                         id="uppercase with surrounding whitespace",  # input is stripped and lowercased
                         ),
            pytest.param("Education", TransactionCategory.EDUCATION,
                         id="mixed case",  # case-insensitive matching is required
                         ),
            pytest.param("entertainment", TransactionCategory.ENTERTAINMENT,
                         id="entertainment tag",  # multi-character tag parses correctly
                         ),
            pytest.param("other", TransactionCategory.OTHER,
                         id="other tag",  # catch-all category parses correctly
                         ),
        ],
    )
    def test_valid_values(self, raw_value: str, expected: TransactionCategory) -> None:
        assert parse_transaction_category(raw_value) is expected

    def test_rejects_invalid_value(self) -> None:
        # values outside the spec-defined five categories are rejected — no silent fallback
        with pytest.raises(ValidationError):
            parse_transaction_category("health")


class TestParseTransactionDescription:

    @pytest.mark.parametrize(
        "raw_value,expected",
        [
            pytest.param("Lunch", "Lunch", id="plain text — accepted",),  # standard description passes through unchanged
            pytest.param("  Bus fare  ", "Bus fare", id="trimmed text — normalized",),  # leading and trailing spaces are removed
        ],
    )
    def test_valid_values(self, raw_value: str, expected: str) -> None:
        assert parse_transaction_description(raw_value) == expected

    @pytest.mark.parametrize(
        "raw_value",
        [
            pytest.param("", id="empty string — validation error",),  # empty descriptions provide no usable transaction context
            pytest.param("   ", id="whitespace only — validation error",),  # whitespace-only input collapses to empty after strip
        ],
    )
    def test_rejects_blank_values(self, raw_value: str) -> None:
        with pytest.raises(ValidationError):
            parse_transaction_description(raw_value)

    def test_rejects_non_string_value(self) -> None:
        # description must be text so the CLI and future UI can display it consistently
        with pytest.raises(ValidationError):
            parse_transaction_description(123)  # type: ignore[arg-type]

