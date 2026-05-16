from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QWidget

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.textures import dot_grain


class PaperWidget(QWidget):
    """
    Scroll-content background: solid BG fill + dot-grain texture overlay.
    Uses paintEvent so the QScrollArea viewport cannot override it.
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
