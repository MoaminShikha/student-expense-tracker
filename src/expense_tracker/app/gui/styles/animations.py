"""Animation utilities for micro-interactions."""

from __future__ import annotations

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPushButton, QWidget


def add_button_hover_effect(button: QPushButton, duration_ms: int = 150) -> None:
    """Add smooth hover state transition to button."""
    original_stylesheet = button.styleSheet()

    def on_enter() -> None:
        button.setStyleSheet(
            original_stylesheet
            + f"background-color: rgba(199, 154, 57, 0.1);"
        )

    def on_leave() -> None:
        button.setStyleSheet(original_stylesheet)

    button.enterEvent = lambda _: on_enter()
    button.leaveEvent = lambda _: on_leave()


def add_focus_glow(widget: QWidget, color: str = "#f1b619", glow_radius: int = 4) -> None:
    """Add focus glow effect to widget."""
    widget.setStyleSheet(
        f"""
        {widget.styleSheet()}
        {{
            border: 2px solid {color};
            box-shadow: 0 0 {glow_radius}px {color};
        }}
        """
    )


def animate_widget_fade_in(widget: QWidget, duration_ms: int = 300) -> QPropertyAnimation:
    """Create fade-in animation for widget."""
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    return anim


def animate_widget_scale(widget: QWidget, start_scale: float = 0.95, duration_ms: int = 200) -> None:
    """Simple scale animation for entrance (visual feedback only)."""
    # Note: PyQt6 doesn't have built-in scale animation for widgets
    # This is a placeholder for custom implementation
    pass


def get_transition_stylesheet(property_name: str = "all", duration_ms: int = 150) -> str:
    """Get CSS for smooth transitions (web-like)."""
    # Note: QSS has limited animation support; this is a reference
    return f"transition: {property_name} {duration_ms}ms ease-out;"
