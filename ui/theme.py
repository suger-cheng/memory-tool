"""QSS 主题系统：浅色 / 深色 / 护眼。现代简约风配色。"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

import database as db

THEMES = {
    "light": {
        "bg": "#F7F6F3",
        "card": "#FFFFFF",
        "panel": "#FFFFFF",
        "text": "#2D2D2D",
        "subtext": "#6B6B6B",
        "primary": "#5B8C7A",
        "primary_hover": "#4A7264",
        "accent_blue": "#7BAFD4",
        "accent_orange": "#D4A574",
        "accent_pink": "#C48B9F",
        "danger": "#C0504D",
        "border": "#E0DED8",
        "shadow": "rgba(0,0,0,0.06)",
    },
    "dark": {
        "bg": "#1A1A2E",
        "card": "#232342",
        "panel": "#20203A",
        "text": "#EAEAF0",
        "subtext": "#9A9AB0",
        "primary": "#7BAFD4",
        "primary_hover": "#5E92BA",
        "accent_blue": "#7BAFD4",
        "accent_orange": "#D4A574",
        "accent_pink": "#C48B9F",
        "danger": "#EF4444",
        "border": "#33335A",
        "shadow": "rgba(0,0,0,0.3)",
    },
    "eye": {
        "bg": "#F2EEDF",
        "card": "#FBF8EC",
        "panel": "#FBF8EC",
        "text": "#3A3A2A",
        "subtext": "#7A7A60",
        "primary": "#6B8E5A",
        "primary_hover": "#557045",
        "accent_blue": "#6A9BB5",
        "accent_orange": "#C99A5C",
        "accent_pink": "#B57A8E",
        "danger": "#B05A4A",
        "border": "#DDD6BF",
        "shadow": "rgba(0,0,0,0.05)",
    },
}


def current_theme() -> str:
    return db.get_setting("theme", "light")


def get_color(key: str, fallback: str = "#2D2D2D") -> str:
    """获取当前主题的指定颜色值。供自定义 Widget 在 paintEvent 中使用。"""
    t = THEMES.get(current_theme(), THEMES["light"])
    return t.get(key, fallback)


def set_theme(name: str):
    db.set_setting("theme", name)


def build_qss(name: str) -> str:
    t = THEMES.get(name, THEMES["light"])
    return f"""
    * {{ font-family: "Microsoft YaHei", "Segoe UI", sans-serif; font-size: 13px; }}
    QWidget#Root {{ background: {t['bg']}; }}
    QFrame#Card, QFrame#Panel {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 14px;
    }}
    QFrame#SideBar {{
        background: {t['card']};
        border-right: 1px solid {t['border']};
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
    }}
    QLabel {{ color: {t['text']}; background: transparent; }}
    QLabel#Title {{ font-size: 22px; font-weight: 600; }}
    QLabel#Subtitle {{ font-size: 15px; font-weight: 500; color: {t['subtext']}; }}
    QLabel#BigNum {{ font-size: 30px; font-weight: 700; color: {t['primary']}; }}
    QLabel#Small {{ color: {t['subtext']}; font-size: 12px; }}
    QLabel#Muted {{ color: {t['subtext']}; }}
    QPushButton#NavBtn {{
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 10px;
        color: {t['subtext']};
        font-size: 14px;
        background: transparent;
    }}
    QPushButton#NavBtn:hover {{ background: {t['bg']}; color: {t['text']}; }}
    QPushButton#NavBtn:checked {{
        background: {t['primary']};
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 7px 14px;
        color: {t['text']};
    }}
    QPushButton:hover {{ border-color: {t['primary']}; }}
    QPushButton:disabled {{ color: {t['subtext']}; }}
    QPushButton#Primary {{
        background: {t['primary']};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton#Primary:hover {{ background: {t['primary_hover']}; }}
    QPushButton#Danger {{ background: {t['danger']}; color: #FFFFFF; border: none; }}
    QPushButton#FeedbackForgot {{ background: {t['danger']}; color: #FFFFFF; border: none; font-weight: 600; font-size: 15px; padding: 14px; border-radius: 12px; }}
    QPushButton#FeedbackFuzzy {{ background: {t['accent_orange']}; color: #FFFFFF; border: none; font-weight: 600; font-size: 15px; padding: 14px; border-radius: 12px; }}
    QPushButton#FeedbackRemember {{ background: {t['primary']}; color: #FFFFFF; border: none; font-weight: 600; font-size: 15px; padding: 14px; border-radius: 12px; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDateEdit {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 7px 10px;
        color: {t['text']};
        selection-background-color: {t['primary']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{ border-color: {t['primary']}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: {t['card']};
        border: 1px solid {t['border']};
        selection-background-color: {t['primary']};
        color: {t['text']};
    }}
    QTableWidget, QTableView, QTreeView, QListView {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        gridline-color: {t['border']};
        color: {t['text']};
        outline: 0;
    }}
    QHeaderView::section {{
        background: {t['bg']};
        color: {t['subtext']};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {t['border']};
        font-weight: 600;
    }}
    QTableWidget::item, QTableView::item {{ padding: 6px; border-bottom: 1px solid {t['border']}; }}
    QTableWidget::item:selected, QTableView::item:selected {{ background: {t['primary']}; color: #FFFFFF; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 5px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {t['subtext']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: {t['border']}; border-radius: 5px; min-width: 30px; }}
    QProgressBar {{
        background: {t['bg']};
        border: none;
        border-radius: 7px;
        text-align: center;
        color: {t['text']};
        height: 14px;
    }}
    QProgressBar::chunk {{ background: {t['primary']}; border-radius: 7px; }}
    QTabWidget::pane {{ border: 1px solid {t['border']}; border-radius: 10px; top: -1px; }}
    QTabBar::tab {{
        background: transparent;
        color: {t['subtext']};
        padding: 8px 18px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{ color: {t['primary']}; border-bottom: 2px solid {t['primary']}; }}
    QGroupBox {{
        border: 1px solid {t['border']};
        border-radius: 10px;
        margin-top: 12px;
        padding-top: 10px;
        color: {t['subtext']};
        font-weight: 600;
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
    QCheckBox {{ color: {t['text']}; spacing: 8px; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid {t['border']}; background: {t['card']}; }}
    QCheckBox::indicator:checked {{ background: {t['primary']}; border-color: {t['primary']}; }}
    QToolTip {{ background: {t['card']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 4px; }}
    """


def apply_theme(name: str | None = None):
    if name is None:
        name = current_theme()
    app = QApplication.instance()
    if app is None:
        return
    app.setStyleSheet(build_qss(name))
    # 调色板
    t = THEMES.get(name, THEMES["light"])
    pal = app.palette()
    pal.setColor(QPalette.Window, QColor(t["bg"]))
    pal.setColor(QPalette.WindowText, QColor(t["text"]))
    pal.setColor(QPalette.Base, QColor(t["card"]))
    pal.setColor(QPalette.Text, QColor(t["text"]))
    pal.setColor(QPalette.AlternateBase, QColor(t["bg"]))
    app.setPalette(pal)
