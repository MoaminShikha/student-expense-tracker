from __future__ import annotations

from enum import IntEnum


class PageIndex(IntEnum):
    DASHBOARD = 0
    ACTIVITY  = 1
    INSIGHTS  = 2
    SETTINGS  = 3


PAGE_NAMES: dict[str, str] = {
    "dashboard": "DASHBOARD / 01",
    "activity":  "ACTIVITY / 01",
    "insights":  "INSIGHTS / 01",
    "settings":  "SETTINGS / 01",
}

PAGE_KEYS: dict[int, str] = {v: k for k, v in {"dashboard": 0, "activity": 1, "insights": 2, "settings": 3}.items()}
