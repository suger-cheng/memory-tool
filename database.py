"""数据库连接管理与 Schema 初始化。SQLite 单文件，连接复用。"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Any, Sequence

# 数据库存放目录（独立于代码目录，打包后数据不丢失）
_DATA_DIR = r"E:\data\ai\memory-tool-data"
os.makedirs(_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(_DATA_DIR, "recall.db")

_conn = None


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
