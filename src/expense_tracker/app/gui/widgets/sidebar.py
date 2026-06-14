from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.constants import STREAK_DAYS_TARGET
from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.fonts import naskh

# Navigation structure: (section_label, [(nav_key, display_text), ...]).
# nav_key is emitted via nav_changed signal when clicked. MainWindow maps it
# to a QStackedWidget index in _on_nav_changed.
_NAV: list[tuple[str, list[tuple[str, str]]]] = [
    ("OVERVIEW", [
        ("dashboard", "Dashboard"),
        ("activity",  "Activity"),
    ]),
    ("INSIGHTS", [
        ("insights", "Insights"),
    ]),
    ("ACCOUNT", [
        ("settings", "Settings"),
    ]),
]


class _AvatarWidget(QWidget):
    """
    33×33 circle: NAVY fill, GOLD initials centered, 9px GREEN status dot
    bottom-right with a 2px SURFACE ring — drawn in paintEvent.
    """

    def __init__(self, initials: str = "KM", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initials = initials
        self.setFixedSize(33, 33)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Main circle
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(tokens.NAVY))
        p.drawEllipse(0, 0, 33, 33)

        # Initials
        p.setPen(QColor(tokens.GOLD))
        font = p.font()
        font.setFamily("DM Mono")
        font.setPointSize(9)
        font.setLetterSpacing(font.SpacingType.AbsoluteSpacing, 1)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._initials)

        # Status dot ring (SURFACE)
        dot_x, dot_y, dot_r = 24, 24, 9
        p.setBrush(QColor(tokens.SURFACE))
        p.drawEllipse(dot_x, dot_y, dot_r, dot_r)

        # Status dot fill (GREEN)
        p.setBrush(QColor(tokens.GREEN))
        p.drawEllipse(dot_x + 2, dot_y + 2, dot_r - 4, dot_r - 4)

        p.end()


class _NavButton(QPushButton):
    """Sidebar nav button with dashboard-matching line icon painted at left."""

    def __init__(self, key: str, text: str) -> None:
        super().__init__(text)
        self._key = key

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        active = self.property("active") == "true"
        active_color = QColor(tokens.FG if active else tokens.MUTED_FG)
        pen = QPen(active_color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        x = 20.0
        y = (self.height() - 15.0) / 2.0
        self._draw_icon(p, x, y)

        if active:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(tokens.GOLD))
            p.drawEllipse(QPointF(self.width() - 16, self.height() / 2), 2.0, 2.0)

        p.end()

    def _draw_icon(self, p: QPainter, x: float, y: float) -> None:
        # Each nav key paints a different icon: dashboard=4-dot grid,
        # activity=3 horizontal lines, insights=5-point star polygon,
        # settings=gear with 6 teeth. Color inverts when active.
        active = self.property("active") == "true"
        color = QColor(tokens.FG if active else tokens.MUTED_FG)
        if self._key == "dashboard":
            size = 4.4
            gap = 5.6
            for row in range(2):
                for col in range(2):
                    p.drawRoundedRect(QRectF(x + col * gap, y + row * gap, size, size), 1, 1)
            return

        if self._key == "activity":
            p.drawLine(QPointF(x, y + 2), QPointF(x + 15, y + 2))
            p.drawLine(QPointF(x, y + 7.5), QPointF(x + 11, y + 7.5))
            p.drawLine(QPointF(x, y + 13), QPointF(x + 7, y + 13))
            return

        if self._key == "insights":
            pts = [
                QPointF(x + 7.5, y),
                QPointF(x + 9.6, y + 5),
                QPointF(x + 15, y + 5.5),
                QPointF(x + 10.9, y + 9),
                QPointF(x + 12, y + 14.5),
                QPointF(x + 7.5, y + 11.8),
                QPointF(x + 3, y + 14.5),
                QPointF(x + 4.1, y + 9),
                QPointF(x, y + 5.5),
                QPointF(x + 5.4, y + 5),
            ]
            p.drawPolygon(QPolygonF(pts))
            return

        if self._key == "settings":
            # Gear: outer rim + inner hub + 6 teeth at 60° intervals
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(x + 4, y + 3, 7, 7))
            p.drawEllipse(QRectF(x + 6, y + 5, 3, 3))
            p.setBrush(color)
            cx, cy = x + 7.5, y + 6.5
            for tx, ty in [
                (cx + 4, cy), (cx + 2, cy - 3.5), (cx - 2, cy - 3.5),
                (cx - 4, cy), (cx - 2, cy + 3.5), (cx + 2, cy + 3.5),
            ]:
                p.drawEllipse(QRectF(tx - 1.5, ty - 1.5, 3, 3))


class Sidebar(QWidget):
    """
    Left navigation sidebar — presentation only.

    Emits nav_changed(key) when a nav item is clicked.
    MainWindow.main_window connects this to _on_nav_changed
    which switches the QStackedWidget page.

    Call set_streak(days) to light up the segment bar.
    """

    nav_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebarRoot")
        self.setFixedWidth(tokens.SIDEBAR_W)
        self._active = "dashboard"
        self._nav_btns: dict[str, QPushButton] = {}
        self._streak_segs: list[QFrame] = []
        self._streak_count_lbl: QLabel | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_brand())
        layout.addWidget(self._build_nav(), stretch=1)
        layout.addWidget(self._build_user())

        self.setStyleSheet(f"""
            QWidget {{
                background: {tokens.SURFACE};
                color: {tokens.MUTED_FG};
                font-family: "DM Mono", Consolas, monospace;
            }}
            QWidget#sidebarRoot {{
                border-right: 1px solid {tokens.HAIRLINE_S};
            }}      
            QFrame#sbDivider {{
                background: {tokens.HAIRLINE};
            }}
            QLabel#sbTag {{
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 3px;
                color: {tokens.AMBER};
                background: transparent;
                text-transform: uppercase;
            }}
            QLabel#sbWordmark {{
                color: {tokens.GOLD_LEAF};
                font-family: "Noto Naskh Arabic";
                font-size: 25px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#sbSub {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 2px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#sbSectionLabel {{
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 3px;
                color: {tokens.MUTED};
                padding: 9px 20px 3px 20px;
                background: transparent;
            }}
            QPushButton#sbNavItem {{
                text-align: left;
                padding-left: 44px;
                padding-right: 22px;
                height: 33px;
                border: none;
                border-left: 3px solid transparent;
                background: transparent;
                color: {tokens.MUTED_FG};
                font-size: {tokens.T_SM}px;
                font-family: "DM Mono", Consolas, monospace;
                border-radius: 0px;
            }}
            QPushButton#sbNavItem:hover {{
                background: rgba(36,28,10,0.08);
                color: {tokens.FG};
                border-left: 3px solid {tokens.HAIRLINE_S};
            }}
            QPushButton#sbNavItem[active="true"] {{
                border-left: 2px solid {tokens.GOLD};
                background: rgba(199,154,57,0.16);
                color: {tokens.FG};
                font-weight: 500;
            }}
            QFrame#sbStreak {{
                background: {tokens.PAPER_WARM};
                border-radius: 10px;
            }}
            QLabel#sbStreakLabel {{
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 3px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#sbStreakCount {{
                font-size: {tokens.T_LG}px;
                font-weight: 700;
                font-family: "Playfair Display";
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#sbStreakUnit {{
                font-size: {tokens.T_XS}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QFrame#sbStreakSegOn {{
                background: {tokens.GOLD};
                border-radius: 3px;
            }}
            QFrame#sbStreakSegOff {{
                background: {tokens.HAIRLINE};
                border-radius: 3px;
            }}
            QFrame#sbUserDivider {{
                background: {tokens.HAIRLINE};
            }}
            QLabel#sbUserName {{
                font-size: {tokens.T_SM}px;
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#sbUserSub {{
                font-size: {tokens.T_MINI}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
        """)

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def set_streak(self, days: int) -> None:
        """Light up the first `days` segments in gold, rest in hairline. Update count display."""
        capped_days = max(0, min(14, days))
        for i, seg in enumerate(self._streak_segs):
            seg.setObjectName("sbStreakSegOn" if i < capped_days else "sbStreakSegOff")
            seg.style().unpolish(seg)
            seg.style().polish(seg)
        if self._streak_count_lbl:
            self._streak_count_lbl.setText(str(capped_days) if days > 0 else "—")

    # ── SECTIONS ──────────────────────────────────────────────────────────────

    def _build_brand(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 18, 20, 0)
        layout.setSpacing(2)

        # Top row: tag + Arabic wordmark
        top = QHBoxLayout()
        tag = QLabel("M—01")
        tag.setObjectName("sbTag")
        tag.setStyleSheet(
            f"QLabel#sbTag {{ color: {tokens.GOLD}; font-size: {tokens.T_MICRO}px;"
            f"letter-spacing: 3px; background: transparent; }}"
        )
        wordmark = QLabel("ميزان")
        wordmark.setObjectName("sbWordmark")
        wordmark.setFont(naskh(25))
        wordmark.setStyleSheet(
            f"color: {tokens.GOLD_LEAF};"
            'font-family: "Noto Naskh Arabic";'
            "font-size: 25px;"
            "font-weight: 700;"
            "background: transparent;"
        )
        wordmark.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top.addWidget(tag)
        top.addStretch()
        top.addWidget(wordmark)

        # Sub row: label + version
        sub = QHBoxLayout()
        sub_l = QLabel("STUDENT BUDGET")
        sub_l.setObjectName("sbSub")
        sub_r = QLabel("v0.9")
        sub_r.setObjectName("sbSub")
        sub.addWidget(sub_l)
        sub.addStretch()
        sub.addWidget(sub_r)

        layout.addLayout(top)
        layout.addLayout(sub)
        layout.addSpacing(14)

        divider = QFrame()
        divider.setObjectName("sbDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        return w

    def _build_nav(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        for section_label, items in _NAV:
            lbl = QLabel(section_label)
            lbl.setObjectName("sbSectionLabel")
            layout.addWidget(lbl)

            for key, text in items:
                btn = self._build_nav_btn(key, text)
                self._nav_btns[key] = btn
                layout.addWidget(btn)

        layout.addStretch()

        # Streak box with horizontal margin matching HTML (6px top, 14px sides, 8px bottom)
        streak_wrap = QWidget()
        streak_wrap_l = QHBoxLayout(streak_wrap)
        streak_wrap_l.setContentsMargins(14, 6, 14, 8)
        streak_wrap_l.setSpacing(0)
        streak_wrap_l.addWidget(self._build_streak())
        layout.addWidget(streak_wrap)

        return w

    def _build_nav_btn(self, key: str, text: str) -> QPushButton:
        btn = _NavButton(key, text)
        btn.setObjectName("sbNavItem")
        btn.setAccessibleName(f"Navigate to {text}")
        btn.setAccessibleDescription(f"Click to go to {text} page")
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setProperty("active", "true" if key == self._active else "false")
        # Capture key in default arg so the lambda closes over the right value
        btn.clicked.connect(lambda _checked, k=key: self._on_nav_clicked(k))
        return btn

    def _build_streak(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sbStreak")

        # Outer margin via a container — layout parented to frame
        container = QVBoxLayout(frame)
        container.setContentsMargins(12, 9, 12, 9)
        container.setSpacing(6)

        header = QHBoxLayout()
        lbl = QLabel("STREAK")
        lbl.setObjectName("sbStreakLabel")

        # Count: number + "days" separate labels so Playfair only hits the number
        count_row = QHBoxLayout()
        count_row.setSpacing(3)
        count_row.setContentsMargins(0, 0, 0, 0)
        num = QLabel("—")
        num.setObjectName("sbStreakCount")
        self._streak_count_lbl = num
        unit = QLabel("days")
        unit.setObjectName("sbStreakUnit")
        count_row.addWidget(num)
        count_row.addWidget(unit)

        header.addWidget(lbl)
        header.addStretch()
        header.addLayout(count_row)

        segs = QHBoxLayout()
        segs.setSpacing(3)
        for _ in range(STREAK_DAYS_TARGET):
            seg = QFrame()
            seg.setObjectName("sbStreakSegOff")
            seg.setFixedHeight(6)
            segs.addWidget(seg)
            self._streak_segs.append(seg)

        container.addLayout(header)
        container.addLayout(segs)

        return frame

    def _build_user(self) -> QWidget:
        w = QWidget()
        layout_outer = QVBoxLayout(w)
        layout_outer.setContentsMargins(0, 0, 0, 0)
        layout_outer.setSpacing(0)

        divider = QFrame()
        divider.setObjectName("sbUserDivider")
        divider.setFixedHeight(1)
        layout_outer.addWidget(divider)

        row_w = QWidget()
        row = QHBoxLayout(row_w)
        row.setContentsMargins(20, 12, 20, 16)
        row.setSpacing(11)

        avatar = _AvatarWidget("KM")

        info_w = QWidget()
        info = QVBoxLayout(info_w)
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)
        name = QLabel("Student")
        name.setObjectName("sbUserName")
        sub = QLabel("University · Dashboard")
        sub.setObjectName("sbUserSub")
        info.addWidget(name)
        info.addWidget(sub)

        row.addWidget(avatar)
        row.addWidget(info_w)
        row.addStretch()

        layout_outer.addWidget(row_w)
        return w

    # ── NAV STATE ─────────────────────────────────────────────────────────────

    def navigate_to(self, key: str) -> None:
        """Switch sidebar active state to ``key`` and emit nav_changed."""
        self._on_nav_clicked(key)

    def _on_nav_clicked(self, key: str) -> None:
        # Update active state on all buttons, then emit the nav key.
        # MainWindow._on_nav_changed receives this and switches pages.
        self._active = key
        for k, btn in self._nav_btns.items():
            btn.setProperty("active", "true" if k == key else "false")
            # Force stylesheet re-evaluation so the [active="true"] QSS applies
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.nav_changed.emit(key)
