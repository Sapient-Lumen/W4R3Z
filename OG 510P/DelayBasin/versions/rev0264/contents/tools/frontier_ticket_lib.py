import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def latest_open_obligation(items):
    return next((item for item in reversed(items) if item.get("state") == "open" or item.get("obligation_state") == "open"), None)


def latest_cooling_retrospective(items):
    return next((item for item in reversed(items) if item.get("state") == "cooling"), None)
