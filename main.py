"""艾宾浩斯智能复习工具 — 应用入口。

使用 Python 3.10.14 + PySide6。
运行：python main.py
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 高 DPI 支持
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

# pyqtgraph 全局配置（统一在此设置，避免各模块重复调用）
try:
    import pyqtgraph as pg
    pg.setConfigOption("background", "transparent")
    pg.setConfigOption("foreground", "#6B6B6B")
    pg.setConfigOption("antialias", True)
except ImportError:
    pass

from ui.main_window import MainWindow
import database as db


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Recall")
    app.setOrganizationName("Recall")

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    finally:
        db.close_conn()
