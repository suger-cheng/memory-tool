"""每日统计与连续打卡天数。"""

from __future__ import annotations

from datetime import datetime, timedelta

import database as db


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def record_review(feedback: str) -> None:
    """记录一次复习到 daily_stats。"""
    today = today_str()
    row = db.fetchone("SELECT * FROM daily_stats WHERE date=?", (today,))
    if row is None:
        # 新的一天，计算 streak
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        prev = db.fetchone("SELECT * FROM daily_stats WHERE date=?", (yesterday,))
        streak = (prev["streak_days"] + 1) if prev else 1
        correct = 1 if feedback == "remembered" else 0
        fuzzy = 1 if feedback == "fuzzy" else 0
        forgot = 1 if feedback == "forgot" else 0
        db.execute(
            "INSERT INTO daily_stats(date, cards_reviewed, correct_count, fuzzy_count, forgot_count, streak_days) "
            "VALUES(?, 1, ?, ?, ?, ?)",
            (today, correct, fuzzy, forgot, streak),
        )
    else:
        # 使用参数化查询更新对应列
        col_map = {
            "remembered": ("correct_count", 1, 0, 0),
            "fuzzy": ("fuzzy_count", 0, 1, 0),
            "forgot": ("forgot_count", 0, 0, 1),
        }
        _, c, f, g = col_map[feedback]
        db.execute(
            "UPDATE daily_stats SET cards_reviewed=cards_reviewed+1, "
            "correct_count=correct_count+?, fuzzy_count=fuzzy_count+?, forgot_count=forgot_count+? "
            "WHERE date=?",
            (c, f, g, today),
        )


def get_today_stats() -> dict:
    row = db.fetchone("SELECT * FROM daily_stats WHERE date=?", (today_str(),))
    if not row:
        return {"reviewed": 0, "correct": 0, "fuzzy": 0, "forgot": 0, "streak": 0}
    return {
        "reviewed": row["cards_reviewed"],
        "correct": row["correct_count"],
        "fuzzy": row["fuzzy_count"],
        "forgot": row["forgot_count"],
        "streak": row["streak_days"],
    }


def get_streak() -> int:
    row = db.fetchone("SELECT * FROM daily_stats WHERE date=?", (today_str(),))
    if row:
        return row["streak_days"]
    # 今天还没复习，看昨天
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    prev = db.fetchone("SELECT * FROM daily_stats WHERE date=?", (yesterday,))
    return prev["streak_days"] if prev else 0


def get_last_n_days_stats(n: int = 30):
    """返回最近 n 天的统计列表。"""
    rows = db.fetchall(
        "SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?", (n,)
    )
    return list(reversed(rows))


def get_total_reviews() -> int:
    row = db.fetchone("SELECT COALESCE(SUM(cards_reviewed),0) AS c FROM daily_stats")
    return row["c"] if row else 0


def get_retention_rate() -> float:
    """整体留存率 = 正确数 / (正确+模糊+忘了)。"""
    row = db.fetchone(
        "SELECT COALESCE(SUM(correct_count),0) AS c, COALESCE(SUM(fuzzy_count),0) AS f, "
        "COALESCE(SUM(forgot_count),0) AS g FROM daily_stats"
    )
    total = row["c"] + row["f"] + row["g"]
    return (row["c"] / total) if total > 0 else 0.0
