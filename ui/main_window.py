"""主窗口：侧边栏 + 内容区 + 全局快捷键 + XP 浮动提示。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QMessageBox, QGraphicsOpacityEffect,
)

import database as db
import gamification
from review_engine import engine
from utils import stats as stats_util
from utils.scheduler import ReminderScheduler, make_icon
from ui.theme import apply_theme, current_theme
from ui.dashboard_view import DashboardView
from ui.review_view import ReviewView
from ui.card_manager import CardManagerView
from ui.deck_manager import DeckManagerView
from ui.stats_view import StatsView
from ui.settings_view import SettingsView
from ui.achievements_view import AchievementsView


class XPToast(QFrame):
    """+XP 浮动提示动画。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.lbl = QLabel("+0 XP")
        f = self.lbl.font(); f.setPointSize(18); f.setBold(True); self.lbl.setFont(f)
        self.lbl.setStyleSheet("color: #5B8C7A;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.addWidget(self.lbl)
        self.setFixedHeight(56)
        self.hide()
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

    def show_xp(self, xp: int):
        if xp <= 0:
            return
        self.lbl.setText(f"+{xp} XP")
        self.adjustSize()
        self.setFixedWidth(max(120, self.lbl.sizeHint().width() + 40))
        parent = self.parentWidget()
        if parent:
            x = parent.width() - self.width() - 30
            y = 30
            self.move(x, y)
        self.show()
        self.raise_()
        self._anim = QPropertyAnimation(self._opacity, b"opacity", self)
        self._anim.setDuration(300)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()
        QTimer.singleShot(1200, self._fade_out)

    def _fade_out(self):
        self._anim = QPropertyAnimation(self._opacity, b"opacity", self)
        self._anim.setDuration(400)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.InCubic)
        self._anim.finished.connect(self.hide)
        self._anim.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("艾宾浩斯智能复习工具")
        self.resize(1180, 760)
        self.setMinimumSize(960, 640)
        self.setWindowIcon(make_icon())

        apply_theme(current_theme())

        central = QWidget()
        central.setObjectName("Root")
        self.setCentralWidget(central)
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # 侧边栏
        self.sidebar = self._build_sidebar()
        lay.addWidget(self.sidebar)

        # 内容区
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack, 1)

        # 视图
        self.view_dashboard = DashboardView()
        self.view_review = ReviewView()
        self.view_cards = CardManagerView()
        self.view_decks = DeckManagerView()
        self.view_stats = StatsView()
        self.view_achievements = AchievementsView()
        self.view_settings = SettingsView()
        for v in [self.view_dashboard, self.view_review, self.view_cards,
                  self.view_decks, self.view_stats, self.view_achievements,
                  self.view_settings]:
            self.stack.addWidget(v)

        # XP 浮层
        self.xp_toast = XPToast(self.centralWidget())

        # 连接
        self.view_dashboard.start_review.connect(self._goto_review)
        self.view_review.finished.connect(self._on_review_finished)
        self.view_review.xp_gained.connect(self._on_xp)
        self.view_settings.theme_changed.connect(lambda name: apply_theme(name))

        # 提醒
        self.scheduler = ReminderScheduler(self)
        self.scheduler.setup_tray()
        self.scheduler.reminder_triggered.connect(self._on_reminder)
        self.scheduler.start()

        # 全局快捷键
        self._setup_shortcuts()

        # 初始
        self._show_view("dashboard")
        self._refresh_all()

    def _build_sidebar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("SideBar")
        bar.setFixedWidth(200)
        v = QVBoxLayout(bar)
        v.setContentsMargins(14, 20, 14, 16)
        v.setSpacing(6)

        brand = QLabel("📖 Recall")
        f = brand.font(); f.setPointSize(18); f.setBold(True); brand.setFont(f)
        brand.setStyleSheet("color: #5B8C7A; padding: 6px 8px 16px 8px;")
        v.addWidget(brand)

        self.nav_buttons: dict[str, QPushButton] = {}
        navs = [
            ("dashboard", "🏠  今日概览"),
            ("review", "🔁  开始复习"),
            ("cards", "🗂  卡片管理"),
            ("decks", "📁  卡组管理"),
            ("stats", "📊  统计面板"),
            ("achievements", "🏅  成就墙"),
            ("settings", "⚙️  设置"),
        ]
        for key, text in navs:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self._show_view(k))
            self.nav_buttons[key] = btn
            v.addWidget(btn)

        v.addStretch()

        # 底部连续天数
        self.streak_lbl = QLabel("🔥 连续 0 天")
        self.streak_lbl.setObjectName("Small")
        self.streak_lbl.setStyleSheet("padding: 8px;")
        v.addWidget(self.streak_lbl)

        self.level_lbl = QLabel("Lv.1 · 0 XP")
        self.level_lbl.setObjectName("Small")
        self.level_lbl.setStyleSheet("padding: 4px 8px;")
        v.addWidget(self.level_lbl)

        return bar

    def _show_view(self, key: str):
        mapping = {
            "dashboard": self.view_dashboard, "review": self.view_review,
            "cards": self.view_cards, "decks": self.view_decks,
            "stats": self.view_stats, "achievements": self.view_achievements,
            "settings": self.view_settings,
        }
        widget = mapping[key]
        self.stack.setCurrentWidget(widget)
        for k, b in self.nav_buttons.items():
            b.setChecked(k == key)
        # 进入视图时刷新
        if hasattr(widget, "refresh"):
            widget.refresh()
        if key == "review":
            self.view_review.start()
            self.view_review.setFocus()

    def _goto_review(self):
        self._show_view("review")

    def _on_review_finished(self):
        self._refresh_all()

    def _on_xp(self, xp: int, prog: dict):
        self.xp_toast.show_xp(xp)
        self.level_lbl.setText(f"Lv.{prog['level']} · {prog['total_xp']} XP")

    def _on_reminder(self, due: int):
        if due > 0:
            self.view_dashboard.refresh()

    def _refresh_all(self):
        self.view_dashboard.refresh()
        streak = stats_util.get_streak()
        self.streak_lbl.setText(f"🔥 连续 {streak} 天")
        prog = gamification.get_progress()
        self.level_lbl.setText(f"Lv.{prog['level']} · {prog['total_xp']} XP")

    def _setup_shortcuts(self):
        # Ctrl+1..7 切换视图
        for i, key in enumerate(["dashboard", "review", "cards", "decks", "stats", "achievements", "settings"], 1):
            act = QAction(self)
            act.setShortcut(QKeySequence(f"Ctrl+{i}"))
            act.triggered.connect(lambda _=False, k=key: self._show_view(k))
            self.addAction(act)
        # Ctrl+N 新建卡片
        act_new = QAction(self)
        act_new.setShortcut(QKeySequence("Ctrl+N"))
        act_new.triggered.connect(self._quick_new_card)
        self.addAction(act_new)

    def _quick_new_card(self):
        self._show_view("cards")
        self.view_cards._new_card()

    def closeEvent(self, e):
        self.scheduler.stop()
        db.close_conn()
        super().closeEvent(e)
