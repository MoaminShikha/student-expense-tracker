from __future__ import annotations

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from expense_tracker.app.gui_v2 import tokens


class Toast(QFrame):
    """Auto-dismissing bottom-right notification toast.

    Use the module-level show_toast() helper for convenience.
    """

    def __init__(
        self,
        message: str,
        variant: str = "info",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("toastFrame")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if variant == "success":
            bg, fg_color, icon = tokens.GREEN, "#ffffff", "✓"
        elif variant == "error":
            bg, fg_color, icon = tokens.RED, "#ffffff", "✕"
        else:
            bg, fg_color, icon = tokens.GOLD, tokens.FG, "ℹ"

        self.setStyleSheet(f"""
            QFrame#toastFrame {{
                background: {bg};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {fg_color}; font-weight: bold; font-size: 14px; background: transparent;")
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(
            f"color: {fg_color}; font-size: {tokens.T_SM}px;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        msg_lbl.setWordWrap(True)
        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl, stretch=1)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)

        self._slide_anim: QPropertyAnimation | None = None

    def show_message(self, text: str | None = None, variant: str | None = None, duration_ms: int = 3000) -> None:
        """Show the toast and auto-dismiss after duration_ms."""
        self.show()
        if self.parent():
            parent_rect = self.parent().rect()  # type: ignore[union-attr]
            target_pos = self.parent().mapToGlobal(  # type: ignore[union-attr]
                QPoint(
                    parent_rect.width() - self.sizeHint().width() - 20,
                    parent_rect.height() - self.sizeHint().height() - 20,
                )
            )
            start_pos = QPoint(target_pos.x(), target_pos.y() + 30)
            self.move(start_pos)
            self._slide_anim = QPropertyAnimation(self, b"pos", self)
            self._slide_anim.setDuration(200)
            self._slide_anim.setStartValue(start_pos)
            self._slide_anim.setEndValue(target_pos)
            self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._slide_anim.start()
        self._timer.start(duration_ms)

    def _dismiss(self) -> None:
        self._timer.stop()
        self.close()
        self.deleteLater()


def show_toast(
    message: str,
    variant: str = "info",
    parent: QWidget | None = None,
    duration_ms: int = 3000,
) -> None:
    """Show a self-dismissing toast notification at the parent widget's bottom-right."""
    toast = Toast(message, variant, parent)
    toast.show_message(duration_ms=duration_ms)
