"""数据库连接管理与 Schema 初始化。SQLite 单文件，连接复用。

启动时路径解析顺序：
1. 读取用户引导配置 ~/.recall_config.json 中的 data_dir（设置页自定义保存的路径）
2. 否则回退到跨平台默认目录（APPDATA / Application Support / XDG_DATA_HOME）

data_dir 变更：
- 通过 set_data_dir()，会自动把 recall.db + -wal + -shm 一起迁移过去，并写入引导配置。
- 迁移后调用方应提示用户重启应用（连接复用对象 _conn 仍指向旧文件，不重启可能写回旧位置）。
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from typing import Any, Sequence


# ---------------------------------------------------------------------------
# 路径解析（模块加载期就确定好 _DATA_DIR / DB_PATH）
# ---------------------------------------------------------------------------

# 引导配置放在用户 home，**不依赖 data_dir**——否则改了 data_dir 后下次启动找不到自己在哪
# 可用环境变量 RECALL_BOOT_CONFIG 覆盖（主要用于测试、便携版分发）
_BOOT_CONFIG_PATH = os.environ.get("RECALL_BOOT_CONFIG") or os.path.join(
    os.path.expanduser("~"), ".recall_config.json"
)
_DB_FILENAME = "recall.db"


def _default_data_dir() -> str:
    """跨平台默认数据目录（没配自定义路径时用）。"""
    app_name = "Recall"
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, app_name)


def _load_boot_config() -> dict:
    """读 ~/.recall_config.json；不存在或损坏返回空 dict。"""
    if not os.path.isfile(_BOOT_CONFIG_PATH):
        return {}
    try:
        with open(_BOOT_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_boot_config(cfg: dict) -> None:
    with open(_BOOT_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _resolve_data_dir() -> str:
    """按优先级解析最终数据目录，并确保它存在。"""
    cfg = _load_boot_config()
    custom = (cfg.get("data_dir") or "").strip()
    if custom and os.path.isabs(custom):
        path = custom
    else:
        path = _default_data_dir()
    os.makedirs(path, exist_ok=True)
    return path


def _db_files(root_dir: str) -> list[str]:
    """返回目录下所有 recall.db* 文件（含 wal / shm / journal）。"""
    return glob.glob(os.path.join(root_dir, _DB_FILENAME + "*"))


# 数据库存放目录（独立于代码目录，打包后数据不丢失）
_DATA_DIR = _resolve_data_dir()
DB_PATH = os.path.join(_DATA_DIR, _DB_FILENAME)

_conn = None


# ---------------------------------------------------------------------------
# 公共 API：数据目录查询 / 自定义迁移
# ---------------------------------------------------------------------------

def get_data_dir() -> str:
    """当前生效的数据目录绝对路径。"""
    return _DATA_DIR


def get_db_path() -> str:
    """当前生效的数据库文件绝对路径。"""
    return DB_PATH


def get_boot_config_path() -> str:
    """引导配置文件路径（主要用于设置页展示）。"""
    return _BOOT_CONFIG_PATH


def set_data_dir(new_dir: str, move_data: bool = True) -> tuple[bool, str]:
    """更改数据目录，可选迁移现有 recall.db*。

    返回 (是否成功, 描述信息)。
    注意：成功后应用应重启，否则当前会话里的 SQLite 连接仍指向旧文件。
    """
    global _DATA_DIR, DB_PATH

    new_dir = os.path.abspath(os.path.expanduser(new_dir))
    if not new_dir:
        return False, "路径不能为空"
    if new_dir == _DATA_DIR:
        return True, "路径未变更"

    # 1) 尝试预先创建目标目录，校验写权限
    try:
        os.makedirs(new_dir, exist_ok=True)
        probe = os.path.join(new_dir, ".write_probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
    except OSError as e:
        return False, f"目标目录不可写：{e}"

    # 2) 目标若已存在 recall.db，拒绝覆盖（让用户先清空或选别的目录）
    existing_in_target = _db_files(new_dir)
    if existing_in_target:
        return (
            False,
            f"目标目录已存在 Recall 数据库文件，无法覆盖：{existing_in_target[0]}",
        )

    old_dir = _DATA_DIR
    old_files = _db_files(old_dir)

    # 3) 先把连接关干净，避免源库被锁住导致迁移失败
    close_conn()

    # 4) 迁移文件（move 比 copy 快，但跨盘 move 其实也是 copy+删，都能行）
    migrated: list[str] = []
    if move_data and old_files:
        try:
            for src in old_files:
                name = os.path.basename(src)
                dst = os.path.join(new_dir, name)
                shutil.move(src, dst)
                migrated.append(dst)
        except Exception as e:
            # 回滚：把已经迁过去的挪回来
            for m in migrated:
                try:
                    shutil.move(m, os.path.join(old_dir, os.path.basename(m)))
                except OSError:
                    pass
            return False, f"迁移失败：{e}"

    # 5) 更新模块级路径并写入引导配置
    _DATA_DIR = new_dir
    DB_PATH = os.path.join(new_dir, _DB_FILENAME)
    try:
        cfg = _load_boot_config()
        cfg["data_dir"] = new_dir
        _save_boot_config(cfg)
    except Exception as e:
        return False, f"配置写入失败：{e}"

    if move_data and migrated:
        return True, f"已迁移 {len(migrated)} 个文件到新目录，应用需重启以使用新数据库。"
    return True, "新目录已写入配置（未检测到旧数据），应用需重启。"


def reset_data_dir_to_default(move_data: bool = True) -> tuple[bool, str]:
    """撤销自定义路径，回到跨平台默认目录（同样会迁移数据）。"""
    new_dir = _default_data_dir()
    # 先清掉引导配置里的 data_dir，这样走 set_data_dir 内部校验时 new_dir != _DATA_DIR 才正确
    # 这里不直接清，set_data_dir 里写完会再写回 cfg；我们最后再把 cfg 的 data_dir 键移除即可。
    ok, msg = set_data_dir(new_dir, move_data=move_data)
    if not ok:
        return ok, msg
    cfg = _load_boot_config()
    cfg.pop("data_dir", None)
    _save_boot_config(cfg)
    return True, msg + "（已恢复默认目录）"


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON;")
        _conn.execute("PRAGMA journal_mode = WAL;")
        init_schema(_conn)
    return _conn


def init_schema(conn: sqlite3.Connection):
    c = conn.cursor()
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            new_cards_per_day INTEGER DEFAULT 20,
            review_limit INTEGER DEFAULT 200,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (parent_id) REFERENCES decks(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            type TEXT NOT NULL DEFAULT 'card',   -- card | note | quote
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            extra TEXT,                           -- 备注/出处等
            stage INTEGER NOT NULL DEFAULT 0,
            ease REAL NOT NULL DEFAULT 2.5,
            mastery REAL NOT NULL DEFAULT 0.0,
            consecutive_correct INTEGER NOT NULL DEFAULT 0,
            is_long_term INTEGER NOT NULL DEFAULT 0,
            next_review_at TEXT,
            last_reviewed_at TEXT,
            review_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS review_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            feedback TEXT NOT NULL,               -- forgot | fuzzy | remembered
            quality INTEGER NOT NULL,             -- 0 | 1 | 2
            stage_before INTEGER,
            stage_after INTEGER,
            ease_before REAL,
            ease_after REAL,
            mastery_before REAL,
            mastery_after REAL,
            response_ms INTEGER,
            reviewed_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,                -- YYYY-MM-DD
            cards_reviewed INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            fuzzy_count INTEGER DEFAULT 0,
            forgot_count INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            xp INTEGER NOT NULL DEFAULT 0,
            total_xp INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS achievements (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            unlocked INTEGER NOT NULL DEFAULT 0,
            unlocked_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_cards_next_review ON cards(next_review_at);
        CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards(deck_id);
        CREATE INDEX IF NOT EXISTS idx_review_log_card ON review_log(card_id);
        CREATE INDEX IF NOT EXISTS idx_review_log_time ON review_log(reviewed_at);
        """
    )
    # 默认设置
    defaults = {
        "theme": "light",
        "new_cards_per_day": "20",
        "review_limit": "200",
        "reminder_enabled": "1",
        "reminder_interval_min": "30",
    }
    for k, v in defaults.items():
        c.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (k, v)
        )
    # 默认用户进度
    c.execute(
        "INSERT OR IGNORE INTO user_progress(id, xp, total_xp, level) VALUES(1, 0, 0, 1)"
    )
    # 默认卡组
    c.execute("INSERT OR IGNORE INTO decks(id, name, parent_id) VALUES(1, '默认卡组', NULL)")
    # 默认成就定义
    ach = [
        ("first_review", "初次复习", "完成第一次复习", 0, None),
        ("review_10", "勤奋学习者", "累计复习 10 张卡片", 0, None),
        ("review_100", "百卡达人", "累计复习 100 张卡片", 0, None),
        ("streak_3", "三日打卡", "连续学习 3 天", 0, None),
        ("streak_7", "一周坚持", "连续学习 7 天", 0, None),
        ("perfect_session", "完美一轮", "一次复习中全部记住", 0, None),
        ("long_term_1", "长期记忆", "首张卡片毕业进入长期记忆池", 0, None),
        ("level_5", "小有所成", "达到 5 级", 0, None),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO achievements(code, name, description, unlocked, unlocked_at) VALUES(?,?,?,?,?)",
        ach,
    )
    conn.commit()


def close_conn() -> None:
    """关闭数据库连接。应在应用退出时调用。"""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


# ---------- 通用查询助手 ----------
def fetchone(sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
    return get_conn().execute(sql, params).fetchone()


def fetchall(sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    return get_conn().execute(sql, params).fetchall()


def execute(sql: str, params: Sequence[Any] = (), commit: bool = True) -> sqlite3.Cursor:
    conn = get_conn()
    cur = conn.execute(sql, params)
    if commit:
        conn.commit()
    return cur


def get_setting(key: str, default: str | None = None) -> str | None:
    row = fetchone("SELECT value FROM settings WHERE key=?", (key,))
    return row["value"] if row else default


def set_setting(key: str, value: Any) -> None:
    execute(
        "INSERT INTO settings(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
