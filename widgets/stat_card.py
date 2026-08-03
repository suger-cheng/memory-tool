"""统计数字卡片组件。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout


class StatCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#5B8C7A", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._color = color
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(6)

        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("Small")
        lay.addWidget(self.title_lbl)

        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("BigNum")
        f = self.value_lbl.font()
        f.setPointSize(28)
        f.setBold(True)
        self.value_lbl.setFont(f)
        self.value_lbl.setStyleSheet(f"color: {color};")
        lay.addWidget(self.value_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setObjectName("Small")
        lay.addWidget(self.sub_lbl)

    def set_value(self, value: str, subtitle: str = ""):
        self.value_lbl.setText(value)
        if subtitle:
            self.sub_lbl.setText(subtitle)

    def set_color(self, color: str):
        self._color = color
        self.value_lbl.setStyleSheet(f"color: {color};")
