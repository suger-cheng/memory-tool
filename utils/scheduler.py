"""QTimer 定时提醒 + 系统托盘通知。"""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QSystemTrayIcon, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

import database as db
from review_engine import engine


def make_icon() -> QIcon:
    """生成一个简单的应用图标。"""
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#5B8C7A"))
    p.setPen(QColor("#5B8C7A"))
    p.drawEllipse(4, 4, 56, 56)
    p.setPen(QColor("#FFFFFF"))
    font = p.font()
    font.setPointSize(28)
    font.setBold(True)
    p.setFont(font)
    p.drawText(pix.rect(), 0x0084, "R")  # AlignCenter
    p.end()
    return QIcon(pix)


class ReminderScheduler(QObject):
    reminder_triggered = Signal(int)  # due_count

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check)
        self.tray: QSystemTrayIcon | None = None
        self._interval_min = 30

    def setup_tray(self):
        app = QApplication.instance()
        if app is None:
            return
        self.tray = QSystemTrayIcon(make_icon(), parent=self)
        self.tray.setToolTip("艾宾浩斯智能复习")
        self.tray.show()

    def start(self):
        enabled = db.get_setting("reminder_enabled", "1") == "1"
        if not enabled:
            self.stop()
            return
        try:
            self._interval_min = int(db.get_setting("reminder_interval_min", "30"))
        except (TypeError, ValueError):
            self._interval_min = 30
        self._interval_min = max(1, self._interval_min)
        self.timer.start(self._interval_min * 60 * 1000)
        # 启动时立即检查一次
        QTimer.singleShot(3000, self._check)

    def stop(self):
        self.timer.stop()

    def restart(self):
        self.stop()
        self.start()

    def _check(self):
        due = engine.get_due_count()
        self.reminder_triggered.emit(due)
        if due > 0 and self.tray:
            self.tray.showMessage(
                "复习提醒",
                f"你有 {due} 张卡片待复习，快来巩固记忆吧！",
                QSystemTrayIcon.Information,
                5000,
            )
