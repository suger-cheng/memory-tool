"""成就墙：等级大圆环 + 本周 XP 柱状图 + 成就徽章。Phase 4。"""

from __future__ import annotations

import math

import pyqtgraph as pg
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
)

import database as db
import gamification
from ui.theme import get_color
from utils import stats as stats_util
from widgets.stat_card import StatCard

ACH_ICONS = {
    "first_review": "🌱",
    "review_10": "📚",
    "review_100": "🏆",
    "streak_3": "🔥",
    "streak_7": "⚡",
    "perfect_session": "✨",
    "long_term_1": "🧠",
    "level_5": "⭐",
}


class LevelRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = 1
        self._pct = 0.0
        self.setMinimumSize(180, 180)

    def set_data(self, level: int, pct: float):
        self._level = level
        self._pct = pct
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height()) - 16
        rect = QRect((self.width()-side)//2, (self.height()-side)//2, side, side)

        p.setPen(QPen(QColor(get_color("border", "#E0DED8")), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, 0, 360 * 16)

        p.setPen(QPen(QColor(get_color("primary", "#5B8C7A")), 12, Qt.SolidLine, Qt.RoundCap))
        span = int(-self._pct / 100.0 * 360 * 16)
        p.drawArc(rect, 90 * 16, span)

        p.setPen(QColor(get_color("text", "#2D2D2D")))
        f = QFont(); f.setPointSize(36); f.setBold(True); p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, f"Lv.{self._level}")


class AchievementBadge(QFrame):
    def __init__(self, code, name, desc, unlocked, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFixedSize(140, 150)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 14, 10, 14)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignCenter)

        icon = QLabel(ACH_ICONS.get(code, "🏅"))
        font = icon.font(); font.setPointSize(34); icon.setFont(font)
        icon.setAlignment(Qt.AlignCenter)
        if not unlocked:
            icon.setStyleSheet(f"color: {get_color('subtext', '#B0B0B0')};")
            icon.setText("🔒")
        lay.addWidget(icon)

        name_lbl = QLabel(name)
        name_lbl.setObjectName("Subtitle")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet(f"color: {get_color('text', '#2D2D2D')}; font-weight: 600;")
        if not unlocked:
            name_lbl.setStyleSheet(f"color: {get_color('subtext', '#9A9AB0')};")
        lay.addWidget(name_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setObjectName("Small")
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(desc_lbl)


class AchievementsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(18)

        title = QLabel("成就墙")
        title.setObjectName("Title")
        root.addWidget(title)

        top = QHBoxLayout()
        top.setSpacing(16)
        # 等级环
        ring_frame = QFrame(); ring_frame.setObjectName("Card")
        rl = QVBoxLayout(ring_frame); rl.setContentsMargins(20, 16, 20, 16)
        rl.setAlignment(Qt.AlignCenter)
        self.ring = LevelRing()
        rl.addWidget(self.ring)
        self.level_info = QLabel("等级 1")
        self.level_info.setObjectName("Subtitle")
        self.level_info.setAlignment(Qt.AlignCenter)
        rl.addWidget(self.level_info)
        top.addWidget(ring_frame)

        # 本周 XP
        xp_frame = QFrame(); xp_frame.setObjectName("Card")
        xl = QVBoxLayout(xp_frame); xl.setContentsMargins(16, 14, 16, 14)
        xl.addWidget(self._lbl("本周 XP 趋势"))
        self.xp_plot = pg.PlotWidget()
        self.xp_plot.setFixedHeight(180)
        self.xp_plot.showGrid(x=False, y=True, alpha=0.2)
        xl.addWidget(self.xp_plot)
        top.addWidget(xp_frame, 1)
        root.addLayout(top)

        # 成就徽章
        badges_title = QLabel("成就徽章")
        badges_title.setObjectName("Subtitle")
        root.addWidget(badges_title)

        self.badges_grid = QGridLayout()
        self.badges_grid.setSpacing(14)
        root.addLayout(self.badges_grid)
        root.addStretch()

    def _lbl(self, t):
        l = QLabel(t); l.setObjectName("Subtitle"); return l

    def refresh(self):
        prog = gamification.get_progress()
        pct = prog["xp"] / max(1, prog["xp_needed"]) * 100
        self.ring.set_data(prog["level"], pct)
        self.level_info.setText(f"等级 {prog['level']} · 累计 {prog['total_xp']} XP")

        # 本周 XP（用近 7 天复习量 * 平均 XP 近似）
        rows = stats_util.get_last_n_days_stats(7)
        x = list(range(len(rows)))
        y = [r["cards_reviewed"] * 7 for r in rows]  # 近似 XP
        self.xp_plot.clear()
        self.xp_plot.addItem(pg.BarGraphItem(x=x, height=y, width=0.5, brush=QColor("#5B8C7A")))
        ticks = [[(i, r["date"][5:]) for i, r in enumerate(rows)]]
        self.xp_plot.getAxis("bottom").setTicks(ticks)

        # 徽章
        achs = gamification.list_achievements()
        # 清空旧徽章
        while self.badges_grid.count():
            it = self.badges_grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i, a in enumerate(achs):
            badge = AchievementBadge(a["code"], a["name"], a["description"], a["unlocked"])
            self.badges_grid.addWidget(badge, i // 4, i % 4)
