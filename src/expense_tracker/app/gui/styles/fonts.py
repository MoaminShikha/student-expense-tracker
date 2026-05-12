from __future__ import annotations

import os

from PyQt6.QtGui import QFont, QFontDatabase

_FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "fonts")

_loaded = False


def load_fonts() -> None:
    """Load all bundled .ttf / .otf files into Qt's font database.

    Safe to call multiple times — skips loading if already done.
    Must be called after QApplication is created and before any widget is shown.
    """
    global _loaded
    if _loaded:
        return

    if not os.path.isdir(_FONTS_DIR):
        return

    for filename in os.listdir(_FONTS_DIR):
        if filename.lower().endswith((".ttf", ".otf")):
            path = os.path.join(_FONTS_DIR, filename)
            result = QFontDatabase.addApplicationFont(path)
            if result == -1:
                import logging
                logging.getLogger(__name__).warning("Failed to load font: %s", path)

    _loaded = True


def playfair(size: int, weight: int = 700) -> QFont:
    """Return a Playfair Display QFont at the given point size and weight.

    Falls back gracefully to the system serif font if not loaded.
    """
    f = QFont("Playfair Display", size)
    f.setWeight(QFont.Weight(weight))
    return f


def dm_mono(size: int, weight: int = 400) -> QFont:
    """Return a DM Mono QFont at the given point size and weight."""
    f = QFont("DM Mono", size)
    f.setWeight(QFont.Weight(weight))
    return f


def naskh(size: int) -> QFont:
    """Return a Noto Naskh Arabic QFont for the ميزان wordmark."""
    f = QFont("Noto Naskh Arabic", size)
    f.setWeight(QFont.Weight(700))
    return f
