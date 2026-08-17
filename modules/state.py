"""
state.py — Lưu/đọc trạng thái poll trước vào file JSON.
Dùng để so sánh xem có thay đổi đáng kể không.
"""
import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "state.json")

def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[state] Lỗi lưu state: {e}")

def get(key: str, default=None):
    return load_state().get(key, default)

def set(key: str, value):
    state = load_state()
    state[key] = value
    save_state(state)

def set_many(updates: dict):
    state = load_state()
    state.update(updates)
    save_state(state)