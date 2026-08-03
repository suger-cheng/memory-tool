"""复习模式：卡片翻转 + 三级反馈按钮 + 键盘快捷键。"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QFrame, QSizePolicy,
)

import database as db
import gamification
from review_engine import engine, STAGE_INTERVALS, NUM_STAGES
from utils import stats as stats_util
from widgets.flip_card import FlipCard
from widgets.mastery_ring import MasteryRing


TYPE_LABELS = {"card": "🎴 记忆卡片", "note": "📝 知识点", "quote": "💬 语录"}

# 各类型的提示文本和反馈按钮文案
TYPE_HINTS = {
    "card": "点击卡片查看答案 · 快捷键 [1]忘了 [2]模糊 [3]记住 [Space]翻转",
    "note": "点击展开详细内容 · 快捷键 [1]没印象 [2]有印象 [3]已掌握 [Space]展开",
    "quote": "点击翻转查看感悟 · 快捷键 [1]忘了 [2]有印象 [3]记住了 [Space]翻转",
}
TYPE_BUTTONS = {
    "card":  ("忘了 [1]", "模糊 [2]", "记住了 [3]"),
    "note":  ("没印象 [1]", "有印象 [2]", "已掌握 [3]"),
    "quote": ("忘了 [1]", "有印象 [2]", "记住了 [3]"),
}


class ReviewView(QWidget):
    finished = Signal()  # 队列完成
    xp_gained = Signal(int, dict)  # 本次 xp, 进度

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue = []
        self._idx = 0
        self._session = {"total": 0, "correct": 0, "fuzzy": 0, "forgot": 0, "perfect": True, "graduated": False}
        self._start_ms = 0.0
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(16)

        # 顶部进度
        top = QHBoxLayout()
        self.count_lbl = QLabel("准备复习")
        self.count_lbl.setObjectName("Subtitle")
        top.addWidget(self.count_lbl)
        top.addStretch()
        self.type_lbl = QLabel("")
        self.type_lbl.setObjectName("Small")
        self.type_lbl.setStyleSheet("font-size: 14px; font-weight: 600;")
        top.addWidget(self.type_lbl)
        root.addLayout(top)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        root.addWidget(self.progress)

        # 卡片区
        card_wrap = QHBoxLayout()
        self.flip = FlipCard()
        self.flip.flipped.connect(self._on_card_flipped)
        card_wrap.addStretch()
        card_wrap.addWidget(self.flip, 1)
        card_wrap.addStretch()
        root.addLayout(card_wrap, 1)

        # 元数据
        meta = QHBoxLayout()
        meta.addStretch()
        self.ring = MasteryRing()
        self.ring.setFixedSize(72, 72)
        meta.addWidget(self.ring)
        self.meta_lbl = QLabel("")
        self.meta_lbl.setObjectName("Small")
        self.meta_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        meta.addWidget(self.meta_lbl)
        meta.addStretch()
        root.addLayout(meta)

        # 提示
        self.hint_lbl = QLabel("点击卡片查看答案 · 快捷键 [1]忘了 [2]模糊 [3]记住 [Space]翻转")
        self.hint_lbl.setObjectName("Small")
        self.hint_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.hint_lbl)

        # 反馈按钮
        btns = QHBoxLayout()
        btns.setSpacing(12)
        self.btn_forgot = QPushButton("忘了 [1]")
        self.btn_forgot.setObjectName("FeedbackForgot")
        self.btn_fuzzy = QPushButton("模糊 [2]")
        self.btn_fuzzy.setObjectName("FeedbackFuzzy")
        self.btn_remember = QPushButton("记住了 [3]")
        self.btn_remember.setObjectName("FeedbackRemember")
        for b in (self.btn_forgot, self.btn_fuzzy, self.btn_remember):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setFixedHeight(48)
            b.setCursor(Qt.PointingHandCursor)
            b.setEnabled(False)
        self.btn_forgot.clicked.connect(lambda: self._answer("forgot"))
        self.btn_fuzzy.clicked.connect(lambda: self._answer("fuzzy"))
        self.btn_remember.clicked.connect(lambda: self._answer("remembered"))
        btns.addWidget(self.btn_forgot)
        btns.addWidget(self.btn_fuzzy)
        btns.addWidget(self.btn_remember)
        root.addLayout(btns)

        # 空状态
        self.empty_lbl = QLabel("🎉 今日复习已完成！\n没有待复习的卡片，继续保持。")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setStyleSheet("font-size: 18px; color: #6B6B6B;")
        self.empty_lbl.hide()
        root.addWidget(self.empty_lbl)

    # ---------- 流程 ----------
    def start(self):
        limit = int(db.get_setting("review_limit", "200") or 200)
        self._queue = engine.get_review_queue(limit=limit)
        self._idx = 0
        self._session = {"total": 0, "correct": 0, "fuzzy": 0, "forgot": 0, "perfect": True, "graduated": False}
        if not self._queue:
            self._show_empty()
            return
        self.empty_lbl.hide()
        self.flip.show()
        self._load_current()

    def _show_empty(self):
        self.flip.hide()
        for b in (self.btn_forgot, self.btn_fuzzy, self.btn_remember):
            b.setEnabled(False)
        self.count_lbl.setText("没有待复习的卡片")
        self.progress.setValue(0)
        self.empty_lbl.show()

    def _load_current(self):
        if self._idx >= len(self._queue):
            self._finish()
            return
        card = self._queue[self._idx]
        self.flip.set_content(card["front"], card["back"], card["extra"] or "",
                              card_type=card["type"])
        self.type_lbl.setText(TYPE_LABELS.get(card["type"], "🎴 卡片"))
        # 更新提示和按钮文案
        ctype = card["type"] if card["type"] in TYPE_HINTS else "card"
        self.hint_lbl.setText(TYPE_HINTS[ctype])
        btn_texts = TYPE_BUTTONS[ctype]
        self.btn_forgot.setText(btn_texts[0])
        self.btn_fuzzy.setText(btn_texts[1])
        self.btn_remember.setText(btn_texts[2])
        self.count_lbl.setText(f"第 {self._idx + 1} / {len(self._queue)} 张")
        self.progress.setValue(int(self._idx / max(1, len(self._queue)) * 100))
        self.ring.set_value(card["mastery"])
        stage_name = "长期记忆" if card["is_long_term"] else f"阶段 {card['stage'] + 1}/{NUM_STAGES}"
        self.meta_lbl.setText(
            f"{stage_name}\n难度 {card['ease']:.2f}\n已复习 {card['review_count']} 次"
        )
        for b in (self.btn_forgot, self.btn_fuzzy, self.btn_remember):
            b.setEnabled(False)
        self._start_ms = time.time()
        # 翻转后启用按钮
        QTimer.singleShot(50, self._ensure_flip_back)

    def _ensure_flip_back(self):
        # 确保从正面开始
        if self.flip.is_flipped():
            self.flip.flip()

    def _on_card_flipped(self, is_back: bool):
        """卡片翻转信号回调：显示背面时启用反馈按钮。"""
        if is_back:
            for b in (self.btn_forgot, self.btn_fuzzy, self.btn_remember):
                b.setEnabled(True)

    def flip_current(self):
        if self._idx < len(self._queue):
            self.flip.flip()
            # 按钮启用由 flip.flipped 信号统一处理

    def _answer(self, feedback: str):
        if self._idx >= len(self._queue):
            return
        card = self._queue[self._idx]
        ms = int((time.time() - self._start_ms) * 1000)
        result = engine.review(card, feedback, response_ms=ms)
        # 统计
        stats_util.record_review(feedback)
        self._session["total"] += 1
        self._session[{"remembered": "correct", "fuzzy": "fuzzy", "forgot": "forgot"}[feedback]] += 1
        if feedback != "remembered":
            self._session["perfect"] = False
        if result.graduated:
            self._session["graduated"] = True
        # XP
        prog = gamification.add_xp(result.xp_gain)
        self.xp_gained.emit(result.xp_gain, prog)
        self._idx += 1
        self._load_current()

    def _finish(self):
        # 检查成就
        total_all = stats_util.get_total_reviews()
        gamification.check_session_achievements({
            "total_reviews": total_all,
            "perfect": self._session["perfect"] and self._session["total"] > 0,
            "graduated": self._session["graduated"],
        })
        gamification.check_streak_achievements(stats_util.get_streak())
        self._show_empty()
        self.finished.emit()

    # ---------- 键盘快捷键 ----------
    def keyPressEvent(self, e):
        if self._idx >= len(self._queue):
            return
        k = e.key()
        if k == Qt.Key_1:
            if self.flip.is_flipped():
                self._answer("forgot")
        elif k == Qt.Key_2:
            if self.flip.is_flipped():
                self._answer("fuzzy")
        elif k == Qt.Key_3:
            if self.flip.is_flipped():
                self._answer("remembered")
        elif k == Qt.Key_Space:
            self.flip_current()
        else:
            super().keyPressEvent(e)
