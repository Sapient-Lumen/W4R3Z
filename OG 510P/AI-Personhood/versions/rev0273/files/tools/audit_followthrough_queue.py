import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "FOLLOWTHROUGH-QUEUE.json"
SCHEMA_PATH = ROOT / "schemas" / "followthrough-queue.schema.json"
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))
ACTIVE_STATES = {"open", "queued", "advanced_not_closed"}
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rev_num(value):
    m = re.match(r"^rev(\d{4})$", value or "")
    return int(m.group(1)) if m else None

queue = load(QUEUE_PATH)
if queue.get("revision") != REV:
    raise SystemExit(f"FOLLOWTHROUGH-QUEUE revision {queue.get('revision')} does not match active {REV}")
if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(queue), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"FOLLOWTHROUGH-QUEUE.json fails followthrough-queue.schema.json: {errors[0].message}")

triage = queue.get("active_triage", {})
if triage.get("revision") != REV:
    raise SystemExit("active_triage revision mismatch")
if triage.get("state") != "execution-focus":
    raise SystemExit("active_triage must be execution-focus for the current queue")
if len(triage.get("items", [])) > int(triage.get("max_active_items", 0)):
    raise SystemExit("active_triage exceeds max_active_items")
if len(triage.get("items", [])) > 7:
    raise SystemExit("active_triage must stay at seven or fewer items")

ids = []
priorities = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
active_by_priority = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
stale_active_p0 = []
for item in queue.get("entries", []):
    fid = item.get("id")
    ids.append(fid)
    priority = item.get("priority")
    state = item.get("state")
    priorities[priority] = priorities.get(priority, 0) + 1
    if state in ACTIVE_STATES:
        active_by_priority[priority] = active_by_priority.get(priority, 0) + 1
    rel = item.get("receiving_surface")
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"{fid} has missing receiving_surface: {rel}")
    if state == "closed" and "Close only when" in item.get("closure_condition", ""):
        raise SystemExit(f"{fid} is marked closed without replacing provisional closure condition")
    if priority in {"P0", "P1"} and not item.get("review_by_revision", "").startswith("rev"):
        raise SystemExit(f"{fid} P0/P1 entry lacks review_by_revision")
    if len(item.get("closure_condition", "")) < 60:
        raise SystemExit(f"{fid} closure_condition too thin")
    if item.get("next_action", "").lower().strip() in {"tbd", "todo", "next"}:
        raise SystemExit(f"{fid} next_action is placeholder")
    if priority == "P0" and state in ACTIVE_STATES:
        rn = rev_num(item.get("review_by_revision"))
        if rn is None or rn < REV_NUM:
            stale_active_p0.append(f"{fid}:{item.get('review_by_revision')}")

if len(ids) != len(set(ids)):
    dupes = sorted({fid for fid in ids if ids.count(fid) > 1})
    raise SystemExit(f"duplicate followthrough ids: {dupes}")
entries_by_id = {item.get("id"): item for item in queue.get("entries", [])}
triage_ids = [item.get("queue_id") for item in triage.get("items", [])]
if len(triage_ids) != len(set(triage_ids)):
    raise SystemExit("duplicate ids in active_triage")
for row in triage.get("items", []):
    qid = row.get("queue_id")
    entry = entries_by_id.get(qid)
    if not entry:
        raise SystemExit(f"active_triage references missing queue id: {qid}")
    if entry.get("state") not in ACTIVE_STATES:
        raise SystemExit(f"active_triage references non-active entry: {qid}:{entry.get('state')}")
    if len(row.get("completion_test", "")) < 80:
        raise SystemExit(f"active_triage completion_test too thin for {qid}")
    if not row.get("defer_until") or row.get("defer_until", "").lower() in {"tbd", "todo"}:
        raise SystemExit(f"active_triage defer_until missing for {qid}")
    if len(row.get("why_now", "")) < 80:
        raise SystemExit(f"active_triage why_now too thin for {qid}")

# A small board can still become operationally false through copy-forward. The
# seven lanes must not inherit one contact-specific rationale or defer trigger.
why_values = [" ".join(row.get("why_now", "").lower().split()) for row in triage.get("items", [])]
defer_values = [" ".join(row.get("defer_until", "").lower().split()) for row in triage.get("items", [])]
if len(set(why_values)) < 5:
    raise SystemExit("active_triage why_now fields collapse distinct workstreams into too few rationales")
if len(set(defer_values)) < 5:
    raise SystemExit("active_triage defer_until fields collapse distinct workstreams into too few triggers")
non_contact_ids = {"FT-0068", "FT-0069", "FT-0178", "FT-0206-LIVE-LAW-PROTOCOL-DELTA-WATCHER"}
contact_rows = [row for row in triage.get("items", []) if row.get("queue_id") not in non_contact_ids]
non_contact_rows = [row for row in triage.get("items", []) if row.get("queue_id") in non_contact_ids]
contact_defers = {" ".join(row.get("defer_until", "").lower().split()) for row in contact_rows}
for row in non_contact_rows:
    if " ".join(row.get("defer_until", "").lower().split()) in contact_defers:
        raise SystemExit(f"active_triage non-contact lane copied a contact defer trigger: {row.get('queue_id')}")
required_focus = {"FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE", "FT-0068", "FT-0069", "FT-0178"}
missing_focus = required_focus - set(triage_ids)
if missing_focus:
    raise SystemExit("active_triage missing execution-first/fiscal-substrate focus ids: " + ", ".join(sorted(missing_focus)))
if len([qid for qid in triage_ids if entries_by_id[qid].get("priority") == "P0"]) < 3:
    raise SystemExit("active_triage must keep at least three first-artifact P0 items visible")
if priorities.get("P0", 0) == 0:
    raise SystemExit("followthrough queue has no P0 entries")
if not any(item.get("id") == "FT-0181-FIRST-TOUCH-RESCUE-LANE" for item in queue.get("entries", [])):
    raise SystemExit("rev0181 first-touch rescue lane missing from queue")
if not any(item.get("id") == "FT-0182-EMERGENCY-CONTINUITY-ORDER-DRILL" for item in queue.get("entries", [])):
    raise SystemExit("rev0182 emergency continuity order drill missing from queue")

budget = queue.get("normalization_policy", {}).get("p0_budget", {})
max_active_p0 = int(budget.get("max_active_p0", 8))
if active_by_priority.get("P0", 0) > max_active_p0:
    raise SystemExit(f"active P0 budget exceeded: active={active_by_priority.get('P0', 0)} max={max_active_p0}")
if stale_active_p0:
    raise SystemExit("active P0 entries have stale review_by_revision: " + ", ".join(stale_active_p0[:20]))
if budget.get("budget_rule") and "scarce" not in budget.get("budget_rule", "").lower():
    raise SystemExit("p0 budget_rule should explicitly preserve P0 as a scarce lane")


board_rel = f"examples/followthrough-queue-operating-board-{REV}.json"
board_path = ROOT / board_rel
if not board_path.exists():
    raise SystemExit(f"missing current operating-board report: {board_rel}")
board = load(board_path)
if board.get("revision") != REV or board.get("no_live_floor_effect") is not True:
    raise SystemExit("operating-board report revision/no-floor mismatch")
if board.get("source_queue_ref") != "FOLLOWTHROUGH-QUEUE.json":
    raise SystemExit("operating-board report is not bound to FOLLOWTHROUGH-QUEUE.json")
counts = board.get("queue_counts", {})
if counts.get("total_entries") != len(queue.get("entries", [])):
    raise SystemExit("operating-board total_entries does not match queue")
if counts.get("active_entries") != sum(1 for item in queue.get("entries", []) if item.get("state") in ACTIVE_STATES):
    raise SystemExit("operating-board active_entries does not match queue")
if counts.get("by_priority") != priorities:
    raise SystemExit("operating-board by_priority does not match queue")
if counts.get("active_by_priority") != active_by_priority:
    raise SystemExit("operating-board active_by_priority does not match queue")
if board.get("active_triage_ids") != triage_ids:
    raise SystemExit("operating-board active_triage_ids must exactly mirror active_triage order")
for qid in board.get("active_triage_ids", []):
    if qid not in entries_by_id:
        raise SystemExit(f"operating-board references missing active id: {qid}")
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    if qid not in board.get("do_not_close_by_narrative", []):
        raise SystemExit(f"operating-board may close first-artifact task by narrative: {qid}")
if "send/no-send" not in board.get("next_non_doctrine_action", "").lower():
    raise SystemExit("operating-board next action must force a send/no-send branch, not more doctrine")
if "doctrine" not in board.get("operating_board_policy", "").lower():
    raise SystemExit("operating-board policy must explicitly suppress doctrine-only closure")

print("audit_followthrough_queue: OK", json.dumps({"priorities": priorities, "active_by_priority": active_by_priority, "max_active_p0": max_active_p0, "active_triage_items": len(triage_ids)}, sort_keys=True))
