from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.fonts import naskh

# Navigation structure: (section_label, [(key, display_text), ...])
_NAV: list[tuple[str, list[tuple[str, str]]]] = [
    ("OVERVIEW", [
        ("dashboard",    "◆  Dashboard"),
        ("history",      "○  History"),
    ]),
    ("MONEY", [
        ("income",       "+  Income"),
        ("charges",      "−  Charges"),
        ("transactions", "•  Transactions"),
    ]),
    ("YOU", [
        ("insights",     "◇  Insights"),
        ("profile",      "◌  Profile"),
    ]),
]

_STREAK_TOTAL = 14


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


class Sidebar(QWidget):
    """
    Left navigation sidebar — presentation only.

    Emits nav_changed(key) when a nav item is clicked.
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
                border-right: 2px solid {tokens.HAIRLINE_S};
            }}
            QFrame#sbDivider {{
                background: {tokens.HAIRLINE};
            }}
            QLabel#sbTag {{
                font-size: {tokens.T_MICRO}px;
                letter-spacing: 3px;
                color: {tokens.MUTED};
                background: transparent;
                text-transform: uppercase;
            }}
            QLabel#sbWordmark {{
                color: {tokens.MUTED};
                font-family: "Noto Naskh Arabic";
                font-size: 25px;
                font-weight: 400;
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
                padding-left: 18px;
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
                border-left: 3px solid {tokens.GOLD};
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
        """Light up the first `days` segments in gold, rest in hairline."""
        for i, seg in enumerate(self._streak_segs):
            seg.setObjectName("sbStreakSegOn" if i < days else "sbStreakSegOff")
            seg.style().unpolish(seg)
            seg.style().polish(seg)

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
        wordmark = QLabel("ميزان")
        wordmark.setObjectName("sbWordmark")
        wordmark.setFont(naskh(25))
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
        layout.addWidget(self._build_streak())
        layout.addSpacing(6)

        return w

    def _build_nav_btn(self, key: str, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("sbNavItem")
        btn.setProperty("active", "true" if key == self._active else "false")
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
        unit = QLabel("days")
        unit.setObjectName("sbStreakUnit")
        count_row.addWidget(num)
        count_row.addWidget(unit)

        header.addWidget(lbl)
        header.addStretch()
        header.addLayout(count_row)

        segs = QHBoxLayout()
        segs.setSpacing(3)
        for _ in range(_STREAK_TOTAL):
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

    def _on_nav_clicked(self, key: str) -> None:
        self._active = key
        for k, btn in self._nav_btns.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.nav_changed.emit(key)
