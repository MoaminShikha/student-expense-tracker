from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException

from expense_tracker.app.api import _parse_date


def test_parse_date_valid_iso():
    assert _parse_date("2024-06-15", "due_date") == date(2024, 6, 15)


def test_parse_date_invalid_raises_422():
    with pytest.raises(HTTPException) as exc_info:
        _parse_date("not-a-date", "due_date")
    assert exc_info.value.status_code == 422


def test_parse_date_wrong_format_raises_422():
    with pytest.raises(HTTPException) as exc_info:
        _parse_date("15/06/2024", "due_date")
    assert exc_info.value.status_code == 422
