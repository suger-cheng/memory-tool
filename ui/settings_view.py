"""设置页：主题切换 + 每日限额 + 提醒 + 导入导出 + 备份。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
)

import database as db
from utils import import_export
from ui.theme import THEMES


class SettingsView(QWidget):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(18)

        title = QLabel("设置")
        title.setObjectName("Title")
        root.addWidget(title)

        # 外观
        g_theme = QGroupBox("外观")
        ft = QFormLayout(g_theme)
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色（现代简约）", "light")
        self.theme_combo.addItem("深色", "dark")
        self.theme_combo.addItem("护眼", "eye")
        self.theme_combo.currentIndexChanged.connect(self._on_theme)
        ft.addRow("主题", self.theme_combo)
        root.addWidget(g_theme)

        # 学习限额
        g_limit = QGroupBox("学习限额")
        fl = QFormLayout(g_limit)
        self.new_per_day = QSpinBox()
        self.new_per_day.setRange(1, 500)
        fl.addRow("每日新卡数", self.new_per_day)
        self.review_limit = QSpinBox()
        self.review_limit.setRange(1, 1000)
        fl.addRow("每日复习上限", self.review_limit)
        self.btn_save_limit = QPushButton("保存")
        self.btn_save_limit.setObjectName("Primary")
        self.btn_save_limit.clicked.connect(self._save_limit)
        fl.addRow("", self.btn_save_limit)
        root.addWidget(g_limit)

        # 提醒
        g_remind = QGroupBox("复习提醒")
        fr = QFormLayout(g_remind)
        self.chk_remind = QCheckBox("启用系统托盘提醒")
        fr.addRow(self.chk_remind)
        self.interval = QSpinBox()
        self.interval.setRange(1, 240)
        self.interval.setSuffix(" 分钟")
        fr.addRow("检查间隔", self.interval)
        self.btn_save_remind = QPushButton("保存")
        self.btn_save_remind.setObjectName("Primary")
        self.btn_save_remind.clicked.connect(self._save_remind)
        fr.addRow("", self.btn_save_remind)
        root.addWidget(g_remind)

        # 数据管理
        g_data = QGroupBox("数据管理")
        fd = QFormLayout(g_data)
        btn_row1 = QHBoxLayout()
        self.btn_export = QPushButton("导出 JSON")
        self.btn_export.clicked.connect(self._export)
        self.btn_import = QPushButton("导入 JSON")
        self.btn_import.clicked.connect(self._import)
        btn_row1.addWidget(self.btn_export)
        btn_row1.addWidget(self.btn_import)
        fd.addRow("导入/导出", btn_row1)

        btn_row2 = QHBoxLayout()
        self.btn_backup = QPushButton("备份数据库")
        self.btn_backup.clicked.connect(self._backup)
        btn_row2.addWidget(self.btn_backup)
        fd.addRow("备份", btn_row2)
        root.addWidget(g_data)

        root.addStretch()

    def _load(self):
        theme = db.get_setting("theme", "light")
        idx = self.theme_combo.findData(theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.new_per_day.setValue(int(db.get_setting("new_cards_per_day", "20") or 20))
        self.review_limit.setValue(int(db.get_setting("review_limit", "200") or 200))
        self.chk_remind.setChecked(db.get_setting("reminder_enabled", "1") == "1")
        self.interval.setValue(int(db.get_setting("reminder_interval_min", "30") or 30))

    def _on_theme(self):
        name = self.theme_combo.currentData()
        db.set_setting("theme", name)
        self.theme_changed.emit(name)

    def _save_limit(self):
        db.set_setting("new_cards_per_day", self.new_per_day.value())
        db.set_setting("review_limit", self.review_limit.value())
        QMessageBox.information(self, "已保存", "学习限额已更新")

    def _save_remind(self):
        db.set_setting("reminder_enabled", "1" if self.chk_remind.isChecked() else "0")
        db.set_setting("reminder_interval_min", self.interval.value())
        QMessageBox.information(self, "已保存", "提醒设置已更新（重启应用后生效）")

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出数据", "recall_export.json", "JSON (*.json)")
        if path:
            n = import_export.export_data(path)
            QMessageBox.information(self, "导出成功", f"已导出 {n} 张卡片")

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入数据", "", "JSON (*.json)")
        if not path:
            return
        replace = QMessageBox.question(self, "导入模式", "是否替换现有数据？（否=合并）") == QMessageBox.Yes
        try:
            n = import_export.import_data(path, replace=replace)
            QMessageBox.information(self, "导入成功", f"已导入 {n} 张卡片")
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))

    def _backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "备份数据库", "recall_backup.db", "SQLite (*.db)")
        if path:
            import_export.backup_db(path)
            QMessageBox.information(self, "备份成功", f"已备份到 {path}")
