from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase

_log = logging.getLogger(__name__)

_FONTS_DIR = Path(__file__).resolve().parent.parent / "resources" / "fonts"

_loaded = False


def load_fonts() -> None:
    """Load all bundled .ttf / .otf files into Qt's font database.

    Safe to call multiple times — skips if already loaded.
    Must be called after QApplication is created and before any widget is shown.
    """
    global _loaded
    if _loaded:
        return

    if not _FONTS_DIR.is_dir():
        _log.warning("Fonts directory not found: %s", _FONTS_DIR)
        return

    for path in _FONTS_DIR.iterdir():
        if path.suffix.lower() in (".ttf", ".otf"):
            if QFontDatabase.addApplicationFont(str(path)) == -1:
                _log.warning("Failed to load font: %s", path)

    _loaded = True


def playfair(size: int, weight: int = 700) -> QFont:
    """Playfair Display at the given point size and weight (falls back to system serif)."""
    f = QFont("Playfair Display", size)
    f.setWeight(QFont.Weight(weight))
    return f


def dm_mono(size: int, weight: int = 400) -> QFont:
    """DM Mono at the given point size and weight."""
    f = QFont("DM Mono", size)
    f.setWeight(QFont.Weight(weight))
    return f


def naskh(size: int) -> QFont:
    """Noto Naskh Arabic bold — for the ميزان wordmark."""
    f = QFont("Noto Naskh Arabic", size)
    f.setWeight(QFont.Weight(700))
    return f
