"""今日概览面板：四宫格统计 + 快捷入口 + XP 进度。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame,
)

import database as db
import gamification
from review_engine import engine
from utils import stats as stats_util
from widgets.stat_card import StatCard


class DashboardView(QWidget):
    start_review = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(20)

        title = QLabel("今日概览")
        title.setObjectName("Title")
        root.addWidget(title)

        # 四宫格
        grid = QGridLayout()
        grid.setSpacing(16)
        self.card_due = StatCard("待复习", "0", "今日到期卡片", "#5B8C7A")
        self.card_retention = StatCard("留存率", "0%", "整体正确率", "#7BAFD4")
        self.card_total = StatCard("总卡片", "0", "全部卡片数", "#D4A574")
        self.card_streak = StatCard("连续天数", "0", "坚持打卡", "#C48B9F")
        grid.addWidget(self.card_due, 0, 0)
        grid.addWidget(self.card_retention, 0, 1)
        grid.addWidget(self.card_total, 1, 0)
        grid.addWidget(self.card_streak, 1, 1)
        root.addLayout(grid)

        # XP 进度卡
        xp_frame = QFrame()
        xp_frame.setObjectName("Card")
        xp_lay = QVBoxLayout(xp_frame)
        xp_lay.setContentsMargins(20, 16, 20, 16)
        xp_lay.setSpacing(8)
        self.xp_title = QLabel("等级 1")
        self.xp_title.setObjectName("Subtitle")
        xp_lay.addWidget(self.xp_title)
        from PySide6.QtWidgets import QProgressBar
        self.xp_bar = QProgressBar()
        self.xp_bar.setTextVisible(True)
        self.xp_bar.setFixedHeight(16)
        xp_lay.addWidget(self.xp_bar)
        self.xp_detail = QLabel("0 / 100 XP")
        self.xp_detail.setObjectName("Small")
        xp_lay.addWidget(self.xp_detail)
        root.addWidget(xp_frame)

        # 今日统计
        today_frame = QFrame()
        today_frame.setObjectName("Card")
        tl = QHBoxLayout(today_frame)
        tl.setContentsMargins(20, 16, 20, 16)
        tl.addWidget(self._mk_label("今日复习", "#5B8C7A"))
        self.today_correct = self._mk_label("记住 0", "#5B8C7A")
        self.today_fuzzy = self._mk_label("模糊 0", "#D4A574")
        self.today_forgot = self._mk_label("忘了 0", "#C0504D")
        tl.addWidget(self.today_correct)
        tl.addWidget(self.today_fuzzy)
        tl.addWidget(self.today_forgot)
        tl.addStretch()
        root.addWidget(today_frame)

        root.addStretch()

        # 开始复习按钮
        self.btn_review = QPushButton("开始今日复习")
        self.btn_review.setObjectName("Primary")
        self.btn_review.setFixedHeight(48)
        self.btn_review.setCursor(Qt.PointingHandCursor)
        self.btn_review.clicked.connect(self.start_review.emit)
        root.addWidget(self.btn_review)

    def _mk_label(self, text: str, color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-size: 15px; font-weight: 600;")
        return lbl

    def refresh(self):
        due = engine.get_due_count()
        total = db.fetchone("SELECT COUNT(*) AS c FROM cards")["c"]
        retention = stats_util.get_retention_rate()
        streak = stats_util.get_streak()
        today = stats_util.get_today_stats()
        self.card_due.set_value(str(due), "今日到期卡片")
        self.card_retention.set_value(f"{retention*100:.0f}%", "整体正确率")
        self.card_total.set_value(str(total), "全部卡片数")
        self.card_streak.set_value(str(streak), "坚持打卡")
        self.today_correct.setText(f"记住 {today['correct']}")
        self.today_fuzzy.setText(f"模糊 {today['fuzzy']}")
        self.today_forgot.setText(f"忘了 {today['forgot']}")
        # XP
        prog = gamification.get_progress()
        self.xp_title.setText(f"等级 {prog['level']} · 累计 {prog['total_xp']} XP")
        pct = int(prog["xp"] / max(1, prog["xp_needed"]) * 100)
        self.xp_bar.setValue(pct)
        self.xp_bar.setFormat(f"{prog['xp']} / {prog['xp_needed']} XP")
        self.xp_detail.setText(f"距离下一级还需 {prog['xp_needed'] - prog['xp']} XP")
        self.btn_review.setText(f"开始今日复习（{due}）" if due > 0 else "今日已完成")
