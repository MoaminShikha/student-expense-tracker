from __future__ import annotations

from decimal import Decimal

from PyQt6.QtCore import QEasingCurve, QVariantAnimation
from PyQt6.QtWidgets import QLabel


class CountingLabel(QLabel):
    """QLabel that animates between numeric values with a count-up/count-down effect.

    Float interpolation is cosmetic only — domain Decimals are the source of truth.
    """

    def __init__(self, fmt: str = "{:,.0f}", parent=None) -> None:
        super().__init__(parent)
        self._fmt = fmt
        self._value = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_tick)
        self.setText(fmt.format(0.0))

    def set_value(self, value: Decimal, animate: bool = True) -> None:
        """Set the displayed value, optionally animating from the current value."""
        target = float(value)
        if not animate or self._value == target:
            self._anim.stop()
            self._value = target
            self.setText(self._fmt.format(target))
            return
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(target)
        self._anim.start()
        self._value = target

    def _on_tick(self, v: float) -> None:
        self.setText(self._fmt.format(v))
