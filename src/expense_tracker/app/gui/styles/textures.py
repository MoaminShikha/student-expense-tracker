"""
Cached dot-grain pixmap used for the page background and hero card overlay.
Matches the HTML body::before radial-gradient dot pattern.
"""
from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap


@lru_cache(maxsize=4)
def dot_grain(color_hex: str = "#9e9474", alpha: int = 35, tile: int = 3) -> QPixmap:
    """
    Return a tiny tiled QPixmap with a single 1×1 dot in the top-left corner.
    Set as a widget's background brush to get the HTML dot-grain texture.

    Usage:
        palette = widget.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(dot_grain()))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)
    """
    pm = QPixmap(tile, tile)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    c = QColor(color_hex)
    c.setAlpha(alpha)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(c)
    p.drawRect(0, 0, 1, 1)
    p.end()
    return pm
