"""卡片列表模型（QAbstractListModel）。"""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
import database as db


class CardListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []

    def refresh(self, deck_id: int | None = None, search: str = ""):
        self.beginResetModel()
        sql = "SELECT * FROM cards"
        params: list = []
        clauses = []
        if deck_id:
            clauses.append("deck_id=?")
            params.append(deck_id)
        if search:
            clauses.append("(front LIKE ? OR back LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY created_at DESC"
        self._rows = db.fetchall(sql, tuple(params))
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        if role == Qt.DisplayRole:
            return row["front"]
        if role == Qt.UserRole:
            return dict(row)
        return None

    def get_row(self, i: int):
        if 0 <= i < len(self._rows):
            return dict(self._rows[i])
        return None
