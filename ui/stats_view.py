"""统计图表：柱状图 + 面积图 + 阶段分布 + 遗忘曲线。Phase 2。"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
)

import database as db
from review_engine import STAGE_INTERVALS, NUM_STAGES, predict_retention
from utils import stats as stats_util
from widgets.stat_card import StatCard


class StatsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(18)

        title = QLabel("统计面板")
        title.setObjectName("Title")
        root.addWidget(title)

        # 顶部数字卡
        grid = QGridLayout()
        grid.setSpacing(14)
        self.s_total = StatCard("累计复习", "0", "总复习次数", "#5B8C7A")
        self.s_retention = StatCard("留存率", "0%", "整体正确率", "#7BAFD4")
        self.s_streak = StatCard("连续天数", "0", "当前连续", "#D4A574")
        self.s_cards = StatCard("卡片总数", "0", "全部卡片", "#C48B9F")
        grid.addWidget(self.s_total, 0, 0)
        grid.addWidget(self.s_retention, 0, 1)
        grid.addWidget(self.s_streak, 0, 2)
        grid.addWidget(self.s_cards, 0, 3)
        root.addLayout(grid)

        # 图表区
        charts = QHBoxLayout()
        charts.setSpacing(16)

        # 左：每日复习柱状图
        left = QFrame(); left.setObjectName("Card")
        ll = QVBoxLayout(left); ll.setContentsMargins(16, 14, 16, 14)
        ll.addWidget(self._label("近 30 天复习量"))
        self.daily_plot = pg.PlotWidget()
        self.daily_plot.setFixedHeight(220)
        self.daily_plot.showGrid(x=False, y=True, alpha=0.2)
        ll.addWidget(self.daily_plot)
        charts.addWidget(left, 1)

        # 右：反馈分布堆叠柱状图
        right = QFrame(); right.setObjectName("Card")
        rl = QVBoxLayout(right); rl.setContentsMargins(16, 14, 16, 14)
        rl.addWidget(self._label("近 14 天反馈分布"))
        self.feedback_plot = pg.PlotWidget()
        self.feedback_plot.setFixedHeight(220)
        self.feedback_plot.showGrid(x=False, y=True, alpha=0.2)
        rl.addWidget(self.feedback_plot)
        charts.addWidget(right, 1)
        root.addLayout(charts)

        charts2 = QHBoxLayout()
        charts2.setSpacing(16)

        # 阶段分布
        sf = QFrame(); sf.setObjectName("Card")
        sl = QVBoxLayout(sf); sl.setContentsMargins(16, 14, 16, 14)
        sl.addWidget(self._label("卡片阶段分布"))
        self.stage_plot = pg.PlotWidget()
        self.stage_plot.setFixedHeight(200)
        self.stage_plot.showGrid(x=False, y=True, alpha=0.2)
        sl.addWidget(self.stage_plot)
        charts2.addWidget(sf, 1)

        # 遗忘曲线
        cf = QFrame(); cf.setObjectName("Card")
        cl = QVBoxLayout(cf); cl.setContentsMargins(16, 14, 16, 14)
        cl.addWidget(self._label("理论遗忘曲线 R(t)=e^(-t/S)"))
        self.curve_plot = pg.PlotWidget()
        self.curve_plot.setFixedHeight(200)
        self.curve_plot.showGrid(x=True, y=True, alpha=0.2)
        self.curve_plot.setLabel("bottom", "时间（小时）")
        self.curve_plot.setLabel("left", "留存率")
        cl.addWidget(self.curve_plot)
        charts2.addWidget(cf, 1)
        root.addLayout(charts2)

        root.addStretch()

    def _label(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setObjectName("Subtitle")
        return l

    def refresh(self):
        # 数字
        self.s_total.set_value(str(stats_util.get_total_reviews()))
        self.s_retention.set_value(f"{stats_util.get_retention_rate()*100:.0f}%")
        self.s_streak.set_value(str(stats_util.get_streak()))
        total = db.fetchone("SELECT COUNT(*) AS c FROM cards")["c"]
        self.s_cards.set_value(str(total))

        self._plot_daily()
        self._plot_feedback()
        self._plot_stage()
        self._plot_curve()

    def _plot_daily(self):
        rows = stats_util.get_last_n_days_stats(30)
        x = list(range(len(rows)))
        y = [r["cards_reviewed"] for r in rows]
        self.daily_plot.clear()
        bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush=QColor("#5B8C7A"))
        self.daily_plot.addItem(bg)
        self.daily_plot.setYRange(0, max(max(y) if y else 1, 1) * 1.2)
        ticks = [[(i, r["date"][5:]) for i, r in enumerate(rows) if i % 5 == 0]]
        self.daily_plot.getAxis("bottom").setTicks(ticks)

    def _plot_feedback(self):
        rows = stats_util.get_last_n_days_stats(14)
        x = list(range(len(rows)))
        correct = [r["correct_count"] for r in rows]
        fuzzy = [r["fuzzy_count"] for r in rows]
        forgot = [r["forgot_count"] for r in rows]
        self.feedback_plot.clear()
        w = 0.35
        self.feedback_plot.addItem(pg.BarGraphItem(x=x, height=correct, width=w, brush=QColor("#5B8C7A")))
        self.feedback_plot.addItem(pg.BarGraphItem(x=[i + w for i in x], height=fuzzy, width=w, brush=QColor("#D4A574")))
        self.feedback_plot.addItem(pg.BarGraphItem(x=[i + 2*w for i in x], height=forgot, width=w, brush=QColor("#C0504D")))
        ticks = [[(i, r["date"][5:]) for i, r in enumerate(rows) if i % 3 == 0]]
        self.feedback_plot.getAxis("bottom").setTicks(ticks)

    def _plot_stage(self):
        rows = db.fetchall(
            "SELECT stage, is_long_term, COUNT(*) AS c FROM cards GROUP BY stage, is_long_term"
        )
        counts = [0] * (NUM_STAGES + 1)  # 0..8 + 长期
        for r in rows:
            if r["is_long_term"]:
                counts[NUM_STAGES] += r["c"]
            else:
                idx = min(r["stage"], NUM_STAGES - 1)
                counts[idx] += r["c"]
        labels = [f"S{i+1}" for i in range(NUM_STAGES)] + ["长期"]
        x = list(range(len(labels)))
        self.stage_plot.clear()
        colors = [QColor("#7BAFD4")] * NUM_STAGES + [QColor("#5B8C7A")]
        for i, c in enumerate(counts):
            self.stage_plot.addItem(pg.BarGraphItem(x=[i], height=[c], width=0.6, brush=colors[i]))
        ticks = [[(i, labels[i]) for i in range(len(labels))]]
        self.stage_plot.getAxis("bottom").setTicks(ticks)
        self.stage_plot.setYRange(0, max(max(counts) if counts else 1, 1) * 1.2)

    def _plot_curve(self):
        self.curve_plot.clear()
        hours = list(range(0, 24 * 30 + 1, 6))
        # 不同阶段的遗忘曲线
        colors = ["#7BAFD4", "#5B8C7A", "#D4A574", "#C48B9F"]
        for stage in [0, 3, 6, 8]:
            ease = 2.5
            y = [predict_retention(h, stage, ease) * 100 for h in hours]
            pen = pg.mkPen(color=QColor(colors[stage % len(colors)]), width=2)
            self.curve_plot.plot(hours, y, pen=pen, name=f"阶段{stage+1}")
        self.curve_plot.setYRange(0, 105)
        self.curve_plot.addLegend(offset=(10, 10))
