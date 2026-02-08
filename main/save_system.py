import json
from datetime import date
from settings import SAVE_PATH, HIGH_PATH

def today_key():
    return date.today().isoformat()

def load_save():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_save(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_highscore():
    try:
        with open(HIGH_PATH, "r", encoding="utf-8") as f:
            return int(f.read().strip() or "0")
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HIGH_PATH, "w", encoding="utf-8") as f:
            f.write(str(int(value)))
    except Exception:
        pass
