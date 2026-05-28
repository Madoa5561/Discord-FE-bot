import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
USED_IDS_PATH = os.path.join(DATA_DIR, "used_ids.json")
VIEW_STATES_PATH = os.path.join(DATA_DIR, "view_states.json")


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


def get_today_question() -> dict:
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

def load_view_states() -> dict:
    if not os.path.exists(VIEW_STATES_PATH):
        return {}
    with open(VIEW_STATES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_view_states(states: dict):
    with open(VIEW_STATES_PATH, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)


def get_view_state(message_id: int) -> dict:
    return load_view_states().get(str(message_id))


def save_view_state(message_id: int, question_id: int, answered_users: list, top_user_ids: list):
    states = load_view_states()
    states[str(message_id)] = {
        "question_id": question_id,
        "answered_users": answered_users,
        "top_user_ids": top_user_ids,
    }
    _save_view_states(states)
