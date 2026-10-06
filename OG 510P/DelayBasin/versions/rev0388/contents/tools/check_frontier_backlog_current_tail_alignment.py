"""Fail closed if FRONTIER-BACKLOG current-tail shortcuts drift behind the receipt."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
backlog = json.loads((ROOT / "FRONTIER-BACKLOG.json").read_text(encoding="utf-8"))
resolutions = json.loads((ROOT / "RESOLUTION-LEDGER.json").read_text(encoding="utf-8"))

rev = receipt.get("revision")
resolved_q = receipt.get("resolved_question")
next_q = receipt.get("next_open_question")
items = backlog.get("items") or []
if backlog.get("revision") != rev:
    raise SystemExit("FRONTIER-BACKLOG revision must match receipt")
if not items:
    raise SystemExit("FRONTIER-BACKLOG must have a current item")
top = items[0]
if top.get("id") != next_q or top.get("state") != "open" or top.get("priority") != 1:
    raise SystemExit("FRONTIER-BACKLOG top row must be the receipt next_open_question")
primary = backlog.get("primary_focus")
if not isinstance(primary, dict):
    raise SystemExit("FRONTIER-BACKLOG primary_focus must be an object")
for key in ["id", "title", "risk", "next_test", "allowed_action", "state"]:
    if primary.get(key) != top.get(key):
        raise SystemExit(f"FRONTIER-BACKLOG primary_focus.{key} drifted from top row")
if primary.get("priority") != top.get("priority"):
    raise SystemExit("FRONTIER-BACKLOG primary_focus priority drifted from top row")
if primary.get("fanout") != top.get("fanout"):
    raise SystemExit("FRONTIER-BACKLOG primary_focus fanout drifted from top row")
if backlog.get("queue_head") != next_q:
    raise SystemExit("FRONTIER-BACKLOG queue_head must match receipt next_open_question")
if backlog.get("next_open_question") != next_q:
    raise SystemExit("FRONTIER-BACKLOG next_open_question must match receipt")
if backlog.get("resolved_question") != resolved_q:
    raise SystemExit("FRONTIER-BACKLOG resolved_question must match receipt")
if backlog.get("generated_from") != f"REVISION-RECEIPT.json#{rev}":
    raise SystemExit("FRONTIER-BACKLOG generated_from must name the current receipt revision")
resolved_ids = set()
for row in resolutions.get("items", []):
    for oid in row.get("resolved_objects", []):
        if re.fullmatch(r"OQ-\d{4}", str(oid)):
            resolved_ids.add(oid)
if next_q in resolved_ids:
    raise SystemExit("FRONTIER-BACKLOG current top row is already resolved")
if resolved_q not in resolved_ids:
    raise SystemExit("receipt resolved_question is not resolved in RESOLUTION-LEDGER")
audit = backlog.get("current_tail_alignment_audit", {})
if audit.get("state") != "enforced" or audit.get("checker") != "tools/check_frontier_backlog_current_tail_alignment.py":
    raise SystemExit("FRONTIER-BACKLOG missing enforced current-tail alignment audit")
if audit.get("primary_focus_id") != next_q or audit.get("queue_head") != next_q:
    raise SystemExit("FRONTIER-BACKLOG alignment audit does not name current successor")
if "review court" not in backlog.get("non_claim", "") or "deletion authority" not in backlog.get("non_claim", ""):
    raise SystemExit("FRONTIER-BACKLOG non_claim must retain anti-court/deletion boundary")
print("check_frontier_backlog_current_tail_alignment: OK")
