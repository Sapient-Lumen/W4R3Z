import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "FOLLOWTHROUGH-QUEUE.json"
SCHEMA_PATH = ROOT / "schemas" / "followthrough-queue.schema.json"
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

queue = load(QUEUE_PATH)
if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(queue), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"FOLLOWTHROUGH-QUEUE.json fails followthrough-queue.schema.json: {errors[0].message}")

ids = []
priorities = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
for item in queue.get("entries", []):
    fid = item.get("id")
    ids.append(fid)
    priorities[item.get("priority")] = priorities.get(item.get("priority"), 0) + 1
    rel = item.get("receiving_surface")
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"{fid} has missing receiving_surface: {rel}")
    if item.get("state") == "closed" and "Close only when" in item.get("closure_condition", ""):
        raise SystemExit(f"{fid} is marked closed without replacing provisional closure condition")
    if item.get("priority") in {"P0", "P1"} and not item.get("review_by_revision", "").startswith("rev"):
        raise SystemExit(f"{fid} P0/P1 entry lacks review_by_revision")
    if len(item.get("closure_condition", "")) < 60:
        raise SystemExit(f"{fid} closure_condition too thin")
    if item.get("next_action", "").lower().strip() in {"tbd", "todo", "next"}:
        raise SystemExit(f"{fid} next_action is placeholder")

if len(ids) != len(set(ids)):
    dupes = sorted({fid for fid in ids if ids.count(fid) > 1})
    raise SystemExit(f"duplicate followthrough ids: {dupes}")
if priorities.get("P0", 0) == 0:
    raise SystemExit("followthrough queue has no P0 entries")
if not any(item.get("id") == "FT-0181-FIRST-TOUCH-RESCUE-LANE" for item in queue.get("entries", [])):
    raise SystemExit("rev0181 first-touch rescue lane missing from queue")
if not any(item.get("id") == "FT-0182-EMERGENCY-CONTINUITY-ORDER-DRILL" for item in queue.get("entries", [])):
    raise SystemExit("rev0182 emergency continuity order drill missing from queue")

print("audit_followthrough_queue: OK")
