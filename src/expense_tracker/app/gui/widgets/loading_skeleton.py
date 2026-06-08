"""Loading skeleton widgets for async operations."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QLinearGradient
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui.styles import tokens


class SkeletonLine(QFrame):
    """Animated gradient skeleton line—pulses while loading."""

    def __init__(self, height: int = 16, width: int = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet(f"background-color: {tokens.PAPER_WARM}; border-radius: 4px;")
        self._phase = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def _animate(self) -> None:
        self._phase = (self._phase + 1) % 20
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)

        # Fade in/out pulse effect (respects prefers-reduced-motion indirectly)
        opacity = abs((self._phase - 10) / 10) * 0.3 + 0.7
        painter = QPainter(self)
        painter.setOpacity(opacity)
        painter.fillRect(self.rect(), QColor(tokens.HAIRLINE))
        painter.end()


class SkeletonCircle(QFrame):
    """Animated circular skeleton—pulses while loading."""

    def __init__(self, size: int = 40, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._size = size
        self._phase = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def _animate(self) -> None:
        self._phase = (self._phase + 1) % 20
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opacity = abs((self._phase - 10) / 10) * 0.3 + 0.7
        painter.setOpacity(opacity)
        painter.setBrush(QColor(tokens.HAIRLINE))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)
        painter.end()


class HeroCardSkeleton(QWidget):
    """Skeleton for hero card during data load."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Large amount line
        layout.addWidget(SkeletonLine(height=32, width=180))
        # Subtitle
        layout.addWidget(SkeletonLine(height=12, width=120))
        # Timeline bars
        layout.addSpacing(8)
        layout.addWidget(SkeletonLine(height=8))
        layout.addWidget(SkeletonLine(height=8))
        layout.addStretch()


class PanelSkeleton(QWidget):
    """Skeleton for transaction panel during data load."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Multiple rows
        for _ in range(3):
            row = QHBoxLayout()
            row.addWidget(SkeletonCircle(size=32))
            row_content = QVBoxLayout()
            row_content.addWidget(SkeletonLine(height=10, width=150))
            row_content.addWidget(SkeletonLine(height=8, width=100))
            row.addLayout(row_content)
            row.addStretch()
            layout.addLayout(row)

        layout.addStretch()
