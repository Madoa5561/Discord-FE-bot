import json
import os
from datetime import date

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/questions.json")

def load_questions() -> list:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_today_question() -> dict:
    questions = load_questions()
    index = date.today().toordinal() % len(questions)
    return questions[index]
