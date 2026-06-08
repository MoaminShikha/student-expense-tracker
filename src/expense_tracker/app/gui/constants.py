"""GUI application constants."""

from decimal import Decimal
from enum import IntEnum


class PageIndex(IntEnum):
    """Stacked widget page indices."""

    DASHBOARD = 0
    ACTIVITY = 1
    INSIGHTS = 2
    SETTINGS = 3


# Balance thresholds (percentage)
RED_THRESHOLD_PERCENTAGE = Decimal("130")  # On-track red threshold (130% of budget)
CAUTION_THRESHOLD = Decimal("100")  # Balance caution threshold (₪)

# Sidebar
AVATAR_SIZE = 33  # Avatar widget size in pixels
AVATAR_STATUS_DOT_SIZE = 9  # Status indicator dot size
STREAK_DAYS_TARGET = 14  # Target number of consecutive activity days

# Timeline & visualization
HERO_CARD_FONT_SIZE = 48  # Hero "FREE MONEY" display font size
HERO_CARD_BORDER_OPACITY = 0.8  # Hero card border opacity
