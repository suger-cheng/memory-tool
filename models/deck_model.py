"""卡组树模型（QAbstractItemModel），支持嵌套。"""

from __future__ import annotations

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
import database as db


class DeckNode:
    def __init__(self, row_id, name, parent=None):
        self.row_id = row_id
        self.name = name
        self.parent = parent
        self.children: list[DeckNode] = []

    def child_count(self) -> int:
        return len(self.children)


class DeckTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = DeckNode(0, "根")
        self.refresh()

    def refresh(self):
        self.beginResetModel()
        self.root.children.clear()
        nodes = {0: self.root}
        rows = db.fetchall("SELECT * FROM decks ORDER BY name")
        # 多趟构建以处理嵌套
        remaining = list(rows)
        for _ in range(10):
            if not remaining:
                break
            still = []
            for r in remaining:
                pid = r["parent_id"] if r["parent_id"] else 0
                if pid in nodes:
                    node = DeckNode(r["id"], r["name"], nodes[pid])
                    nodes[pid].children.append(node)
                    nodes[r["id"]] = node
                else:
                    still.append(r)
            remaining = still
        self.endResetModel()

    def index(self, row, column, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_node = parent.internalPointer() if parent.isValid() else self.root
        if row < 0 or row >= parent_node.child_count():
            return QModelIndex()
        child = parent_node.children[row]
        return self.createIndex(row, column, child)

    def parent(self, index) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        parent = node.parent
        if parent is None or parent is self.root:
            return QModelIndex()
        grand = parent.parent
        if grand is None:
            return QModelIndex()
        row = grand.children.index(parent) if parent in grand.children else 0
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent=QModelIndex()) -> int:
        node = parent.internalPointer() if parent.isValid() else self.root
        return node.child_count() if node else 0

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return node.name
        if role == Qt.UserRole:
            return node.row_id
        return None

    def get_deck_id(self, index: QModelIndex) -> int | None:
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.row_id if node else None
