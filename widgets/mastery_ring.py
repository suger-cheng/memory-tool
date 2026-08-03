"""熟练度环形进度条。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget

from ui.theme import get_color


class MasteryRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._color = QColor("#5B8C7A")
        self.setMinimumSize(80, 80)

    def set_value(self, v: float, color: QColor | None = None):
        self._value = max(0.0, min(100.0, v))
        if color is not None:
            self._color = color
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height()) - 8
        x = (self.width() - side) // 2
        y = (self.height() - side) // 2
        rect = QRect(x, y, side, side)

        # 背景环
        pen = QPen(QColor(get_color("border", "#E0DED8")), 8, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 360 * 16)

        # 进度环
        pen = QPen(self._color, 8, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        span = int(-self._value / 100.0 * 360 * 16)
        p.drawArc(rect, 90 * 16, span)

        # 文本
        p.setPen(QColor(get_color("text", "#2D2D2D")))
        f = QFont(); f.setPointSize(12); f.setBold(True); p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, f"{int(self._value)}")


def QRect_centered(w: QWidget, side: int) -> QRect:
    x = (w.width() - side) // 2
    y = (w.height() - side) // 2
    return QRect(x, y, side, side)
