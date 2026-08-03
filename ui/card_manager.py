"""卡片增删改查。支持三种类型：卡片/笔记/语录。"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QMessageBox, QAbstractItemView, QGroupBox, QSplitter,
)

import database as db
from models.card_model import CardListModel
from models.deck_model import DeckTreeModel


TYPE_LABELS = {"card": "记忆卡片", "note": "知识点", "quote": "语录"}
TYPE_KEYS = {v: k for k, v in TYPE_LABELS.items()}

# 各类型的表单提示文案
TYPE_PLACEHOLDERS = {
    "card": {
        "front": "问题/提示（如：Python 中 list 和 tuple 的区别？）",
        "back":  "答案（如：list 可变，tuple 不可变……）",
        "extra": "备注（可选）",
    },
    "note": {
        "front": "知识点标题/关键词（如：闭包 Closure）",
        "back":  "详细说明/长文本（如：闭包是指一个函数能够记住并访问……）",
        "extra": "来源链接（可选）",
    },
    "quote": {
        "front": "语录原文/名句（如：「千里之行，始于足下。」）",
        "back":  "作者/个人感悟（如：—— 老子。任何伟大成就都从第一步开始……）",
        "extra": "出处（如：《道德经》）",
    },
}


class CardEditDialog(QDialog):
    def __init__(self, parent=None, card=None):
        super().__init__(parent)
        self.setWindowTitle("编辑卡片" if card else "新建卡片")
        self.setMinimumWidth(480)
        self._card = card
        lay = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        self.type_combo = QComboBox()
        for k, v in TYPE_LABELS.items():
            self.type_combo.addItem(v, k)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("类型", self.type_combo)

        self.deck_combo = QComboBox()
        self._load_decks()
        form.addRow("卡组", self.deck_combo)

        self.front_edit = QTextEdit()
        self.front_edit.setPlaceholderText(TYPE_PLACEHOLDERS["card"]["front"])
        self.front_edit.setMinimumHeight(80)
        self.front_label = QLabel("正面")
        form.addRow(self.front_label, self.front_edit)

        self.back_edit = QTextEdit()
        self.back_edit.setPlaceholderText(TYPE_PLACEHOLDERS["card"]["back"])
        self.back_edit.setMinimumHeight(100)
        self.back_label = QLabel("背面")
        form.addRow(self.back_label, self.back_edit)

        self.extra_edit = QLineEdit()
        self.extra_edit.setPlaceholderText(TYPE_PLACEHOLDERS["card"]["extra"])
        self.extra_label = QLabel("附加")
        form.addRow(self.extra_label, self.extra_edit)

        lay.addLayout(form)

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("保存")
        self.btn_ok.setObjectName("Primary")
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_ok)
        lay.addLayout(btns)

        if card:
            self.type_combo.setCurrentIndex(self.type_combo.findData(card["type"]))
            idx = self.deck_combo.findData(card["deck_id"])
            if idx >= 0:
                self.deck_combo.setCurrentIndex(idx)
            self.front_edit.setPlainText(card["front"])
            self.back_edit.setPlainText(card["back"])
            self.extra_edit.setText(card["extra"] or "")

    def _on_type_changed(self) -> None:
        """切换类型时更新表单提示。"""
        ctype = self.type_combo.currentData()
        if ctype in TYPE_PLACEHOLDERS:
            ph = TYPE_PLACEHOLDERS[ctype]
            self.front_edit.setPlaceholderText(ph["front"])
            self.back_edit.setPlaceholderText(ph["back"])
            self.extra_edit.setPlaceholderText(ph["extra"])
            # 知识点类型调整标签
            if ctype == "note":
                self.front_label.setText("标题")
                self.back_label.setText("内容")
                self.extra_label.setText("来源")
            elif ctype == "quote":
                self.front_label.setText("语录")
                self.back_label.setText("感悟")
                self.extra_label.setText("出处")
            else:
                self.front_label.setText("正面")
                self.back_label.setText("背面")
                self.extra_label.setText("附加")

    def _load_decks(self):
        rows = db.fetchall("SELECT id, name FROM decks ORDER BY name")
        for r in rows:
            self.deck_combo.addItem(r["name"], r["id"])

    def get_data(self) -> dict:
        return {
            "type": self.type_combo.currentData(),
            "deck_id": self.deck_combo.currentData(),
            "front": self.front_edit.toPlainText().strip(),
            "back": self.back_edit.toPlainText().strip(),
            "extra": self.extra_edit.text().strip(),
        }


class CardManagerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(16)

        title = QLabel("卡片管理")
        title.setObjectName("Title")
        root.addWidget(title)

        # 工具栏
        bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索卡片内容...")
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.refresh)
        self.search_edit.textChanged.connect(self._on_search_changed)
        bar.addWidget(self.search_edit, 1)

        self.btn_new = QPushButton("+ 新建卡片")
        self.btn_new.setObjectName("Primary")
        self.btn_new.clicked.connect(self._new_card)
        bar.addWidget(self.btn_new)

        self.btn_edit = QPushButton("编辑")
        self.btn_edit.clicked.connect(self._edit_card)
        bar.addWidget(self.btn_edit)

        self.btn_del = QPushButton("删除")
        self.btn_del.setObjectName("Danger")
        self.btn_del.clicked.connect(self._del_card)
        bar.addWidget(self.btn_del)
        root.addLayout(bar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "类型", "正面", "卡组", "阶段", "下次复习"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self._edit_card)
        root.addWidget(self.table, 1)

    def _on_search_changed(self) -> None:
        """防抖搜索：每次输入重置 300ms 定时器。"""
        self._search_timer.start()

    def refresh(self):
        search = self.search_edit.text().strip()
        sql = """
            SELECT c.*, d.name AS deck_name FROM cards c
            LEFT JOIN decks d ON c.deck_id = d.id
        """
        params: list = []
        if search:
            sql += " WHERE c.front LIKE ? OR c.back LIKE ?"
            params = [f"%{search}%", f"%{search}%"]
        sql += " ORDER BY c.created_at DESC LIMIT 500"
        rows = db.fetchall(sql, tuple(params))
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            stage = "长期" if r["is_long_term"] else f"{r['stage']+1}/9"
            items = [
                str(r["id"]),
                TYPE_LABELS.get(r["type"], r["type"]),
                r["front"][:60] + ("…" if len(r["front"]) > 60 else ""),
                r["deck_name"] or "—",
                stage,
                r["next_review_at"] or "—",
            ]
            for j, txt in enumerate(items):
                it = QTableWidgetItem(txt)
                if j != 2:
                    it.setTextAlignment(Qt.AlignCenter)
                it.setData(Qt.UserRole, dict(r))
                self.table.setItem(i, j, it)

    def _current_card(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _new_card(self):
        dlg = CardEditDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d["front"] or not d["back"]:
                QMessageBox.warning(self, "提示", "正面和背面不能为空")
                return
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.execute(
                """INSERT INTO cards(deck_id, type, front, back, extra, next_review_at)
                   VALUES(?,?,?,?,?,?)""",
                (d["deck_id"], d["type"], d["front"], d["back"], d["extra"] or None, now),
            )
            self.refresh()

    def _edit_card(self):
        card = self._current_card()
        if not card:
            QMessageBox.information(self, "提示", "请先选择一张卡片")
            return
        dlg = CardEditDialog(self, card=card)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d["front"] or not d["back"]:
                QMessageBox.warning(self, "提示", "正面和背面不能为空")
                return
            db.execute(
                "UPDATE cards SET deck_id=?, type=?, front=?, back=?, extra=? WHERE id=?",
                (d["deck_id"], d["type"], d["front"], d["back"], d["extra"] or None, card["id"]),
            )
            self.refresh()

    def _del_card(self):
        card = self._current_card()
        if not card:
            return
        if QMessageBox.question(self, "确认", f"删除卡片「{card['front'][:20]}」？") == QMessageBox.Yes:
            db.execute("DELETE FROM cards WHERE id=?", (card["id"],))
            self.refresh()
