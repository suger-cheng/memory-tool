"""游戏化系统：XP / 等级 / 成就。Phase 4。"""

from __future__ import annotations

from datetime import datetime

import database as db

# 升级所需累计 XP 曲线：到达 level n 需要 total_xp >= 100 * (n-1) * n / 2
# level 1 = 0, level 2 = 100, level 3 = 300, level 4 = 600 ...
def xp_for_level(level: int) -> int:
    if level <= 1:
        return 0
    return 100 * (level - 1) * level // 2


def level_from_xp(total_xp: int) -> int:
    level = 1
    while xp_for_level(level + 1) <= total_xp:
        level += 1
    return level


def get_progress() -> dict:
    row = db.fetchone("SELECT * FROM user_progress WHERE id=1")
    if not row:
        return {"xp": 0, "total_xp": 0, "level": 1}
    level = level_from_xp(row["total_xp"])
    cur_base = xp_for_level(level)
    next_base = xp_for_level(level + 1)
    xp_in_level = row["total_xp"] - cur_base
    xp_needed = next_base - cur_base
    return {
        "xp": xp_in_level,
        "xp_needed": xp_needed,
        "total_xp": row["total_xp"],
        "level": level,
    }


def add_xp(amount: int) -> dict:
    """增加 XP，自动升级。返回新的进度。"""
    if amount <= 0:
        return get_progress()
    # 原子操作：直接在 SQL 中累加，避免读-改-写竞态
    db.execute(
        "UPDATE user_progress SET total_xp = total_xp + ?, updated_at=? WHERE id=1",
        (amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    # 重新读取并校正 level
    row = db.fetchone("SELECT * FROM user_progress WHERE id=1")
    if row:
        new_level = level_from_xp(row["total_xp"])
        if new_level != row["level"]:
            db.execute("UPDATE user_progress SET level=? WHERE id=1", (new_level,))
            unlock_achievement("level_5", new_level >= 5)
    return get_progress()


def unlock_achievement(code: str, condition: bool = True) -> bool:
    """满足条件时解锁成就，返回是否新解锁。"""
    if not condition:
        return False
    row = db.fetchone("SELECT * FROM achievements WHERE code=?", (code,))
    if not row or row["unlocked"]:
        return False
    db.execute(
        "UPDATE achievements SET unlocked=1, unlocked_at=? WHERE code=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code),
    )
    return True


def list_achievements():
    return db.fetchall("SELECT * FROM achievements ORDER BY code")


def check_session_achievements(stats: dict):
    """复习结束后根据会话统计检查成就。stats: {total_reviews, perfect, graduated}"""
    # 累计复习数
    total = stats.get("total_reviews", 0)
    unlock_achievement("first_review", total >= 1)
    unlock_achievement("review_10", total >= 10)
    unlock_achievement("review_100", total >= 100)
    unlock_achievement("perfect_session", stats.get("perfect", False))
    unlock_achievement("long_term_1", stats.get("graduated", False))


def check_streak_achievements(streak: int):
    unlock_achievement("streak_3", streak >= 3)
    unlock_achievement("streak_7", streak >= 7)
