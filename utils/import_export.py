"""数据导入导出（JSON）。"""

from __future__ import annotations

import json
from datetime import datetime

import database as db


def export_data(path: str):
    conn = db.get_conn()
    data = {
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decks": [dict(r) for r in conn.execute("SELECT * FROM decks")],
        "cards": [dict(r) for r in conn.execute("SELECT * FROM cards")],
        "review_log": [dict(r) for r in conn.execute("SELECT * FROM review_log")],
        "daily_stats": [dict(r) for r in conn.execute("SELECT * FROM daily_stats")],
        "settings": [dict(r) for r in conn.execute("SELECT * FROM settings")],
        "user_progress": [dict(r) for r in conn.execute("SELECT * FROM user_progress")],
        "achievements": [dict(r) for r in conn.execute("SELECT * FROM achievements")],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data["cards"])


def import_data(path: str, replace: bool = False):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    conn = db.get_conn()
    try:
        if replace:
            # 按外键依赖顺序删除：子表先删，父表后删
            for t in ["review_log", "daily_stats", "achievements", "user_progress",
                       "settings", "cards", "decks"]:
                conn.execute(f"DELETE FROM {t}")
        # decks
        for d in data.get("decks", []):
            conn.execute(
                "INSERT OR REPLACE INTO decks(id, name, parent_id, new_cards_per_day, review_limit, created_at) "
                "VALUES(?,?,?,?,?,?)",
                (d["id"], d["name"], d.get("parent_id"), d.get("new_cards_per_day", 20),
                 d.get("review_limit", 200), d.get("created_at")),
            )
        # cards
        for c in data.get("cards", []):
            conn.execute(
                """INSERT OR REPLACE INTO cards(id, deck_id, type, front, back, extra, stage, ease, mastery,
                   consecutive_correct, is_long_term, next_review_at, last_reviewed_at, review_count, created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (c["id"], c.get("deck_id"), c.get("type", "card"), c["front"], c["back"], c.get("extra"),
                 c.get("stage", 0), c.get("ease", 2.5), c.get("mastery", 0.0), c.get("consecutive_correct", 0),
                 c.get("is_long_term", 0), c.get("next_review_at"), c.get("last_reviewed_at"),
                 c.get("review_count", 0), c.get("created_at")),
            )
        for t, cols in [
            ("daily_stats", ["date", "cards_reviewed", "correct_count", "fuzzy_count", "forgot_count", "streak_days"]),
            ("settings", ["key", "value"]),
            ("user_progress", ["id", "xp", "total_xp", "level", "updated_at"]),
            ("achievements", ["code", "name", "description", "unlocked", "unlocked_at"]),
        ]:
            for row in data.get(t, []):
                placeholders = ",".join("?" * len(cols))
                conn.execute(f"INSERT OR REPLACE INTO {t}({','.join(cols)}) VALUES({placeholders})",
                             [row.get(col) for col in cols])
        conn.commit()
        return len(data.get("cards", []))
    except Exception:
        conn.rollback()
        raise


def backup_db(path: str):
    """备份数据库文件。"""
    import shutil
    shutil.copy2(db.DB_PATH, path)
