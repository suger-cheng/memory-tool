"""复习算法核心。艾宾浩斯间隔重复 + 难度因子 + 熟练度 + 长期记忆池。"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import database as db

# 9 阶段递进间隔（秒）
STAGE_INTERVALS = [
    5 * 60,          # 5 分钟
    30 * 60,         # 30 分钟
    12 * 3600,       # 12 小时
    24 * 3600,       # 1 天
    2 * 24 * 3600,   # 2 天
    4 * 24 * 3600,   # 4 天
    7 * 24 * 3600,   # 7 天
    15 * 24 * 3600,  # 15 天
    30 * 24 * 3600,  # 30 天
]
NUM_STAGES = len(STAGE_INTERVALS)

EASE_MIN = 1.3
EASE_MAX = 3.0
LONG_TERM_BASE_DAYS = 60
LONG_TERM_CAP_DAYS = 180
MASTERY_GRADUATE = 100.0


@dataclass
class ReviewResult:
    feedback: str            # forgot | fuzzy | remembered
    quality: int             # 0 | 1 | 2
    stage_before: int
    stage_after: int
    ease_before: float
    ease_after: float
    mastery_before: float
    mastery_after: float
    is_long_term: bool
    next_review_at: str
    graduated: bool = False  # 本次是否毕业进入长期记忆池
    xp_gain: int = 0


def _now() -> datetime:
    return datetime.now()


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def stage_interval_seconds(stage: int, ease: float) -> float:
    """根据阶段与难度因子计算间隔（秒）。"""
    if stage <= 0:
        return STAGE_INTERVALS[0]
    idx = min(stage, NUM_STAGES - 1)
    base = STAGE_INTERVALS[idx]
    # ease 微调：ease 越高间隔越长
    return base * (ease / 2.5)


def predict_retention(hours_since: float, stage: int, ease: float) -> float:
    """预测记忆强度 R(t) = e^(-t/S)。S 由阶段与难度因子决定。"""
    s_hours = stage_interval_seconds(stage, ease) / 3600.0
    if s_hours <= 0:
        return 0.0
    return math.exp(-hours_since / s_hours)


class ReviewEngine:
    """核心调度引擎。"""

    def review(self, card_row, feedback: str, response_ms: int = 0) -> ReviewResult:
        q = {"forgot": 0, "fuzzy": 1, "remembered": 2}.get(feedback, 1)
        stage = card_row["stage"]
        ease = card_row["ease"]
        mastery = card_row["mastery"]
        consec = card_row["consecutive_correct"]
        is_long = bool(card_row["is_long_term"])

        stage_before, ease_before, mastery_before = stage, ease, mastery

        xp_gain = 0
        graduated = False

        if is_long:
            # 长期记忆卡片
            if q == 0:
                # 忘了 → 退回普通流程
                is_long = False
                stage = 0
                ease = max(EASE_MIN, ease - 0.3)
                mastery = mastery * 0.4
                consec = 0
                xp_gain = 0
            else:
                # 记住/模糊 → 按长期记忆间隔增长
                if q == 2:
                    ease = min(EASE_MAX, ease + 0.05)
                    mastery = min(MASTERY_GRADUATE, mastery + 1)
                    xp_gain = 8
                else:
                    ease = max(EASE_MIN, ease - 0.02)
                    xp_gain = 3
                # 长期记忆间隔：base * ease 增长，上限 180 天
                interval_days = min(LONG_TERM_CAP_DAYS, LONG_TERM_BASE_DAYS * (ease / 2.5))
                next_dt = _now() + timedelta(days=interval_days)
                self._persist(card_row, stage, ease, mastery, consec, is_long, _iso(next_dt), q, feedback, response_ms,
                              stage_before, ease_before, mastery_before)
                return ReviewResult(feedback, q, stage_before, stage, ease_before, ease,
                                    mastery_before, mastery, is_long, _iso(next_dt), graduated, xp_gain)

        # 普通流程
        if q == 2:  # 记住了
            stage = min(stage + 1, NUM_STAGES - 1)
            ease = min(EASE_MAX, ease + 0.08)
            consec = consec + 1
            mastery = min(MASTERY_GRADUATE, mastery + 100.0 / NUM_STAGES * (ease / 2.5))
            xp_gain = 10
        elif q == 1:  # 模糊
            stage = max(0, stage - 1)
            ease = max(EASE_MIN, ease - 0.05)
            consec = 0
            mastery = max(0.0, mastery - 5)
            xp_gain = 4
        else:  # 忘了
            stage = 0
            ease = max(EASE_MIN, ease - 0.3)
            consec = 0
            mastery = mastery * 0.4
            xp_gain = 1

        # 是否毕业
        if mastery >= MASTERY_GRADUATE and not is_long:
            is_long = True
            graduated = True
            interval_days = min(LONG_TERM_CAP_DAYS, LONG_TERM_BASE_DAYS * (ease / 2.5))
            next_dt = _now() + timedelta(days=interval_days)
        else:
            interval_sec = stage_interval_seconds(stage, ease)
            next_dt = _now() + timedelta(seconds=interval_sec)

        next_iso = _iso(next_dt)
        self._persist(card_row, stage, ease, mastery, consec, is_long, next_iso, q, feedback, response_ms,
                      stage_before, ease_before, mastery_before)
        return ReviewResult(feedback, q, stage_before, stage, ease_before, ease,
                            mastery_before, mastery, is_long, next_iso, graduated, xp_gain)

    def _persist(self, card_row, stage, ease, mastery, consec, is_long, next_iso,
                 q, feedback, response_ms, stage_before, ease_before, mastery_before):
        card_id = card_row["id"]
        db.execute(
            """UPDATE cards SET stage=?, ease=?, mastery=?, consecutive_correct=?,
               is_long_term=?, next_review_at=?, last_reviewed_at=?,
               review_count=review_count+1 WHERE id=?""",
            (stage, ease, mastery, consec, int(is_long), next_iso, _iso(_now()), card_id),
        )
        db.execute(
            """INSERT INTO review_log(card_id, feedback, quality, stage_before, stage_after,
               ease_before, ease_after, mastery_before, mastery_after, response_ms)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (card_id, feedback, q, stage_before, stage, ease_before, ease,
             mastery_before, mastery, response_ms),
        )

    # ---------- 复习队列 ----------
    def get_review_queue(self, limit: int = 200) -> List[sqlite3.Row]:
        now_iso = _iso(_now())
        today_end = _iso(datetime.now().replace(hour=23, minute=59, second=59))
        # 优先级：逾期普通 > 今日到期 > 即将到期 > 逾期长期
        rows = db.fetchall(
            """
            SELECT * FROM cards
            WHERE next_review_at IS NOT NULL AND next_review_at <= ?
            ORDER BY is_long_term ASC,
                     CASE WHEN next_review_at < ? THEN 0 ELSE 1 END,
                     next_review_at ASC
            LIMIT ?
            """,
            (today_end, now_iso, limit),
        )
        return rows

    def get_due_count(self) -> int:
        now_iso = _iso(_now())
        row = db.fetchone("SELECT COUNT(*) AS c FROM cards WHERE next_review_at <= ?", (now_iso,))
        return row["c"] if row else 0

    def get_new_count_today(self, deck_id: Optional[int] = None) -> int:
        today = _now().strftime("%Y-%m-%d")
        sql = "SELECT COUNT(*) AS c FROM cards WHERE last_reviewed_at IS NULL OR date(last_reviewed_at) < ?"
        params: tuple = (today,)
        if deck_id:
            sql += " AND deck_id=?"
            params = (today, deck_id)
        row = db.fetchone(sql, params)
        return row["c"] if row else 0


# 让 fetchall 返回的 sqlite3.Row 支持类型提示
engine = ReviewEngine()
