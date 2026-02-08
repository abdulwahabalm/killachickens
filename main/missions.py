import random
from save_system import today_key, write_save

MISSION_POOL = [
    {"id": "corn", "text": "Collect {n} corn", "min": 35, "max": 90},
    {"id": "kills", "text": "Defeat {n} enemies", "min": 10, "max": 35},
    {"id": "survive", "text": "Survive {n} seconds", "min": 120, "max": 240},
    {"id": "dodges", "text": "Dodge {n} eggs (near-miss)", "min": 25, "max": 90},
    {"id": "combo", "text": "Reach a {n} combo", "min": 8, "max": 16},
]

def seeded_rng_for_today():
    y, m, d = today_key().split("-")
    seed = int(f"{y}{m}{d}")
    return random.Random(seed)

def generate_daily_missions():
    rng = seeded_rng_for_today()
    pool = MISSION_POOL[:]
    rng.shuffle(pool)
    chosen = pool[:3]
    missions = []
    for m in chosen:
        target = rng.randint(m["min"], m["max"])
        missions.append({
            "id": m["id"],
            "text": m["text"].format(n=target),
            "target": target,
            "progress": 0,
            "done": False
        })
    return missions

def load_or_create_daily(save_data):
    key = today_key()
    daily = save_data.get("daily", {})
    if daily.get("date") != key or "missions" not in daily:
        daily = {"date": key, "missions": generate_daily_missions(), "bonus_claimed": False}
        save_data["daily"] = daily
        write_save(save_data)
    return daily

def all_done(daily):
    return all(m["done"] for m in daily["missions"])

def update_progress(state, mid, value, absolute=False):
    daily = state.daily
    changed = False
    for m in daily["missions"]:
        if m["id"] != mid or m["done"]:
            continue
        if absolute:
            m["progress"] = max(m["progress"], int(value))
        else:
            m["progress"] += int(value)
        if m["progress"] >= m["target"]:
            m["progress"] = m["target"]
            m["done"] = True
        changed = True

    if changed:
        state.save_data["daily"] = daily
        write_save(state.save_data)
    return changed
