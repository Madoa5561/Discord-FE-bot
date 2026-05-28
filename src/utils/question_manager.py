import json
import os
import random
import asyncio
from datetime import datetime, timezone, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
USED_IDS_PATH = os.path.join(DATA_DIR, "used_ids.json")
VIEW_STATES_PATH = os.path.join(DATA_DIR, "view_states.json")

_STATE_TTL_DAYS = 30  # view_states の保持期間

_used_ids_lock = asyncio.Lock()
_view_states_lock = asyncio.Lock()


def load_questions() -> list:
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question_by_id(question_id: int) -> dict:
    for q in load_questions():
        if q["id"] == question_id:
            return q
    raise ValueError(f"question_id={question_id} が見つかりません")


def _load_used_ids() -> list:
    if not os.path.exists(USED_IDS_PATH):
        return []
    with open(USED_IDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _save_used_ids(used_ids: list):
    with open(USED_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(used_ids, f, ensure_ascii=False, indent=2)


async def get_today_question() -> dict:
    async with _used_ids_lock:
        questions = load_questions()
        if not questions:
            raise ValueError("questions.json に問題がありません")

        used_ids = _load_used_ids()
        all_ids = [q["id"] for q in questions]
        remaining = [qid for qid in all_ids if qid not in used_ids]

        if not remaining:
            # 全問使用済み → リセット
            used_ids = []
            remaining = all_ids

        chosen_id = random.choice(remaining)
        used_ids.append(chosen_id)
        _save_used_ids(used_ids)

        return next(q for q in questions if q["id"] == chosen_id)


# --- View状態の永続化 ---

def _load_view_states_raw() -> dict:
    if not os.path.exists(VIEW_STATES_PATH):
        return {}
    with open(VIEW_STATES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_view_states_raw(states: dict):
    with open(VIEW_STATES_PATH, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)


def _prune_old_states(states: dict) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=_STATE_TTL_DAYS)
    pruned = {}
    for k, v in states.items():
        created_at_str = v.get("created_at", "2000-01-01T00:00:00+00:00")
        try:
            created_at = datetime.fromisoformat(created_at_str)
            if created_at > cutoff:
                pruned[k] = v
        except ValueError:
            pass  # パースできないエントリは削除
    return pruned


async def get_view_state(message_id: int) -> dict:
    async with _view_states_lock:
        return _load_view_states_raw().get(str(message_id))


async def save_view_state(message_id: int, question_id: int, answered_users: list, top_user_ids: list):
    async with _view_states_lock:
        states = _load_view_states_raw()
        key = str(message_id)
        existing = states.get(key, {})
        states[key] = {
            "question_id": question_id,
            "answered_users": answered_users,
            "top_user_ids": top_user_ids,
            "created_at": existing.get("created_at", datetime.now(timezone.utc).isoformat()),
        }
        states = _prune_old_states(states)
        _save_view_states_raw(states)
