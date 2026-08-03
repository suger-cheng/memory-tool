"""卡组管理：树形结构 + 增删改 + 每日限额。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeView, QLineEdit,
    QSpinBox, QFormLayout, QDialog, QMessageBox, QGroupBox, QHeaderView, QComboBox,
)

import database as db
from models.deck_model import DeckTreeModel


class DeckEditDialog(QDialog):
    def __init__(self, parent=None, deck=None, exclude_id=None):
        super().__init__(parent)
        self.setWindowTitle("编辑卡组" if deck else "新建卡组")
        self.setMinimumWidth(360)
        lay = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow("名称", self.name_edit)

        self.parent_combo = QComboBox()
        self.parent_combo.addItem("（无 / 顶层）", None)
        rows = db.fetchall("SELECT id, name FROM decks ORDER BY name")
        for r in rows:
            if exclude_id and r["id"] == exclude_id:
                continue
            self.parent_combo.addItem(r["name"], r["id"])
        form.addRow("父卡组", self.parent_combo)

        self.new_per_day = QSpinBox()
        self.new_per_day.setRange(1, 500)
        self.new_per_day.setValue(20)
        form.addRow("每日新卡数", self.new_per_day)

        self.review_limit = QSpinBox()
        self.review_limit.setRange(1, 1000)
        self.review_limit.setValue(200)
        form.addRow("复习上限", self.review_limit)

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

        if deck:
            self.name_edit.setText(deck["name"])
            self.new_per_day.setValue(deck["new_cards_per_day"] or 20)
            self.review_limit.setValue(deck["review_limit"] or 200)
            if deck["parent_id"]:
                idx = self.parent_combo.findData(deck["parent_id"])
                if idx >= 0:
                    self.parent_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "parent_id": self.parent_combo.currentData(),
            "new_cards_per_day": self.new_per_day.value(),
            "review_limit": self.review_limit.value(),
        }


class DeckManagerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(16)

        title = QLabel("卡组管理")
        title.setObjectName("Title")
        root.addWidget(title)

        bar = QHBoxLayout()
        self.btn_new = QPushButton("+ 新建卡组")
        self.btn_new.setObjectName("Primary")
        self.btn_new.clicked.connect(self._new_deck)
        self.btn_edit = QPushButton("编辑")
        self.btn_edit.clicked.connect(self._edit_deck)
        self.btn_del = QPushButton("删除")
        self.btn_del.setObjectName("Danger")
        self.btn_del.clicked.connect(self._del_deck)
        bar.addWidget(self.btn_new)
        bar.addWidget(self.btn_edit)
        bar.addWidget(self.btn_del)
        bar.addStretch()
        root.addLayout(bar)

        self.tree = QTreeView()
        self.tree.setHeaderHidden(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self._model = DeckTreeModel()
        self.tree.setModel(self._model)
        root.addWidget(self.tree, 1)

        # 统计
        self.stat_lbl = QLabel("")
        self.stat_lbl.setObjectName("Small")
        root.addWidget(self.stat_lbl)

    def refresh(self):
        self._model.refresh()
        self.tree.expandAll()
        total = db.fetchone("SELECT COUNT(*) AS c FROM decks")["c"]
        cards = db.fetchone("SELECT COUNT(*) AS c FROM cards")["c"]
        self.stat_lbl.setText(f"共 {total} 个卡组 · {cards} 张卡片")

    def _current_deck(self):
        idx = self.tree.currentIndex()
        if not idx.isValid():
            return None
        deck_id = self.tree.model().get_deck_id(idx)
        if not deck_id:
            return None
        return db.fetchone("SELECT * FROM decks WHERE id=?", (deck_id,))

    def _new_deck(self):
        dlg = DeckEditDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d["name"]:
                QMessageBox.warning(self, "提示", "名称不能为空")
                return
            db.execute(
                "INSERT INTO decks(name, parent_id, new_cards_per_day, review_limit) VALUES(?,?,?,?)",
                (d["name"], d["parent_id"], d["new_cards_per_day"], d["review_limit"]),
            )
            self.refresh()

    def _edit_deck(self):
        deck = self._current_deck()
        if not deck:
            QMessageBox.information(self, "提示", "请先选择一个卡组")
            return
        if deck["id"] == 1:
            QMessageBox.information(self, "提示", "默认卡组不可编辑")
            return
        dlg = DeckEditDialog(self, deck=deck, exclude_id=deck["id"])
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d["name"]:
                QMessageBox.warning(self, "提示", "名称不能为空")
                return
            db.execute(
                "UPDATE decks SET name=?, parent_id=?, new_cards_per_day=?, review_limit=? WHERE id=?",
                (d["name"], d["parent_id"], d["new_cards_per_day"], d["review_limit"], deck["id"]),
            )
            self.refresh()

    def _del_deck(self):
        deck = self._current_deck()
        if not deck:
            return
        if deck["id"] == 1:
            QMessageBox.information(self, "提示", "默认卡组不可删除")
            return
        if QMessageBox.question(self, "确认", f"删除卡组「{deck['name']}」？\n其中的卡片会变为未分组。") == QMessageBox.Yes:
            db.execute("DELETE FROM decks WHERE id=?", (deck["id"],))
            self.refresh()
