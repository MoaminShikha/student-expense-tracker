from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QWidget

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.textures import dot_grain


class PaperWidget(QWidget):
    """
    Scroll-content background used by every page inside its QScrollArea.

    Two layers painted in paintEvent:
      1. Solid cream fill (tokens.BG)
      2. Dot-grain texture at 50% opacity (matching the HTML mockup's paper feel)

    paintEvent is used instead of QSS because QScrollArea's viewport widget
    would override a stylesheet background. WA_OpaquePaintEvent prevents
    flicker by telling Qt the widget fully paints its own background.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(tokens.BG))
        p.setOpacity(0.5)
        p.fillRect(self.rect(), QBrush(dot_grain()))
        p.end()
