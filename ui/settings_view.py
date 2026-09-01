"""设置页：主题切换 + 每日限额 + 提醒 + 导入导出 + 备份 + 数据目录。"""

from __future__ import annotations

import os

from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog, QLineEdit,
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

        # 数据存储位置
        g_store = QGroupBox("数据存储位置")
        fs = QFormLayout(g_store)

        path_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setObjectName("PathEdit")
        self.path_edit.setReadOnly(True)
        self.path_edit.setFocusPolicy(Qt.NoFocus)
        self.path_edit.setMinimumWidth(360)
        self.btn_browse = QPushButton("选择…")
        self.btn_browse.clicked.connect(self._browse_data_dir)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.btn_browse)
        fs.addRow("当前目录", path_row)

        btn_row3 = QHBoxLayout()
        self.btn_open = QPushButton("打开当前目录")
        self.btn_open.clicked.connect(self._open_data_dir)
        self.btn_open_cfg = QPushButton("打开引导配置位置")
        self.btn_open_cfg.clicked.connect(self._open_boot_config_dir)
        btn_row3.addWidget(self.btn_open)
        btn_row3.addWidget(self.btn_open_cfg)
        fs.addRow("", btn_row3)

        btn_row4 = QHBoxLayout()
        self.btn_apply_dir = QPushButton("应用并迁移")
        self.btn_apply_dir.setObjectName("Primary")
        self.btn_apply_dir.clicked.connect(self._apply_data_dir)
        self.btn_reset_dir = QPushButton("恢复默认")
        self.btn_reset_dir.clicked.connect(self._reset_data_dir)
        btn_row4.addWidget(self.btn_apply_dir)
        btn_row4.addWidget(self.btn_reset_dir)
        fs.addRow("", btn_row4)

        tip = QLabel("更改后 Recall 会自动把现有数据库（含 wal / shm 附属文件）移动到新位置。")
        tip.setWordWrap(True)
        tip.setObjectName("Hint")
        fs.addRow(tip)
        tip2 = QLabel("注意：迁移完成后应用需重启，否则当前会话里的卡片读取仍走旧连接。")
        tip2.setWordWrap(True)
        tip2.setObjectName("Hint")
        fs.addRow(tip2)

        root.addWidget(g_store)

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
        self._show_path(db.get_data_dir())

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

    # ------------------------------------------------------------------
    # 数据目录
    # ------------------------------------------------------------------

    def _show_path(self, text: str):
        """路径框统一入口：完整路径放 tooltip（悬停可看全），光标归零保证显示开头。"""
        self.path_edit.setText(text)
        self.path_edit.setToolTip(text)
        self.path_edit.setCursorPosition(0)

    def _open_data_dir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(db.get_data_dir()))

    def _open_boot_config_dir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(db.get_boot_config_path())))

    def _browse_data_dir(self):
        start = db.get_data_dir()
        chosen = QFileDialog.getExistingDirectory(self, "选择新的数据存储位置", start)
        if chosen:
            self._show_path(chosen)

    def _apply_data_dir(self):
        target = self.path_edit.text().strip()
        if not target:
            QMessageBox.warning(self, "路径为空", "请先选择目标目录")
            return
        if os.path.abspath(target) == os.path.abspath(db.get_data_dir()):
            QMessageBox.information(self, "未变更", "新目录和当前目录相同。")
            return
        ret = QMessageBox.question(
            self,
            "确认迁移",
            f"Recall 将关闭数据库连接并把所有 recall.db* 文件移动到：\n\n"
            f"{target}\n\n"
            f"迁移成功后应用需立即重启，确认继续吗？",
        )
        if ret != QMessageBox.Yes:
            return
        ok, msg = db.set_data_dir(target, move_data=True)
        if not ok:
            QMessageBox.critical(self, "迁移失败", msg)
            # 失败了把显示内容回滚到实际生效的目录
            self._show_path(db.get_data_dir())
            return
        QMessageBox.information(self, "迁移成功", msg)
        QMessageBox.information(
            self,
            "请重启应用",
            "为避免数据错乱，请立刻关闭 Recall 并重新打开。新位置下次启动自动生效。",
        )

    def _reset_data_dir(self):
        ret = QMessageBox.question(
            self,
            "恢复默认目录",
            "确定把数据目录恢复到跨平台默认位置？现有数据会被一并迁移过去。",
        )
        if ret != QMessageBox.Yes:
            return
        ok, msg = db.reset_data_dir_to_default(move_data=True)
        if not ok:
            QMessageBox.critical(self, "操作失败", msg)
            self._show_path(db.get_data_dir())
            return
        self._show_path(db.get_data_dir())
        QMessageBox.information(self, "操作成功", msg)
        QMessageBox.information(
            self,
            "请重启应用",
            "目录已重置。请立刻关闭并重新打开 Recall 以使用新连接。",
        )
