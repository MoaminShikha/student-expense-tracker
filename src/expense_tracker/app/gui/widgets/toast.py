"""Toast notification widget — auto-dismissing feedback message."""
from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QFrame
from expense_tracker.app.gui.styles import tokens


class Toast(QWidget):
    """Auto-dismissing notification toast (2.5 seconds)."""

    def __init__(self, message: str, kind: str = "info", parent: QWidget | None = None) -> None:
        """
        Initialize toast.

        Args:
            message: Notification text
            kind: "success", "error", or "info"
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Color scheme by kind
        if kind == "success":
            bg_color = tokens.GREEN
            text_color = "#ffffff"
            icon = "✓"
        elif kind == "error":
            bg_color = tokens.RED
            text_color = "#ffffff"
            icon = "✕"
        else:
            bg_color = tokens.GOLD
            text_color = tokens.FG
            icon = "ℹ"

        # Frame
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 6px;
                padding: 12px 16px;
                color: {text_color};
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 14px;")

        # Message
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(
            f"color: {text_color}; font-size: 12px; "
            f"font-family: 'DM Mono', Consolas, monospace;"
        )
        msg_lbl.setWordWrap(True)

        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl, stretch=1)

        # Root
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.addWidget(frame, stretch=1)

        # Auto-dismiss timer
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.dismiss)

    def show_for(self, duration_ms: int = 2500) -> None:
        """Show toast and auto-dismiss after duration."""
        self.show()
        self._timer.start(duration_ms)

    def dismiss(self) -> None:
        """Dismiss the toast."""
        self._timer.stop()
        self.close()
        self.deleteLater()


def show_toast(message: str, kind: str = "info", parent: QWidget | None = None) -> None:
    """Show a toast notification.

    Args:
        message: Notification text
        kind: "success", "error", or "info"
        parent: Parent widget for positioning
    """
    toast = Toast(message, kind, parent)
    toast.adjustSize()  # compute real size before we need its dimensions
    if parent:
        pos = parent.mapToGlobal(parent.rect().bottomRight())
        toast.move(pos.x() - toast.width() - 20, pos.y() - toast.height() - 20)
    toast.show_for()
