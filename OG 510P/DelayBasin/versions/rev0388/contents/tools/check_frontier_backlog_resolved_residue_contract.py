import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
backlog = json.loads((ROOT / "FRONTIER-BACKLOG.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
resolutions = json.loads((ROOT / "RESOLUTION-LEDGER.json").read_text(encoding="utf-8"))
resolved = {}
for row in resolutions.get("items", []):
    for oid in row.get("resolved_objects", []):
        if re.fullmatch(r"OQ-\d{4}", oid):
            succ = row.get("successor_open_question") or row.get("successor_surface") or ""
            successor_id = succ.rsplit("#", 1)[-1] if "#" in succ else row.get("successor")
            resolved[oid] = {"resolved_by": row.get("id"), "successor": successor_id}
items = backlog.get("items", [])
if not items:
    raise SystemExit("frontier backlog must have at least one item")
if items[0].get("id") != receipt.get("next_open_question") or items[0].get("state") != "open" or items[0].get("priority") != 1:
    raise SystemExit("frontier backlog top item must be the live open successor")
problems = []
corrected = 0
for row in items:
    oid = row.get("id")
    if oid in resolved:
        expected = resolved[oid]
        corrected += 1
        if row.get("state") != "resolved":
            problems.append(f"{oid} is resolved by ledger but backlog state is {row.get('state')!r}")
        if row.get("resolved_by") != expected["resolved_by"]:
            problems.append(f"{oid} resolved_by {row.get('resolved_by')!r} != {expected['resolved_by']!r}")
        if expected.get("successor") and row.get("successor") != expected["successor"]:
            problems.append(f"{oid} successor {row.get('successor')!r} != {expected['successor']!r}")
if problems:
    raise SystemExit("frontier backlog resolved residue drift: " + "; ".join(problems[:12]))
audit = backlog.get("resolved_residue_audit", {})
if audit.get("state") != "enforced" or audit.get("checker") != "tools/check_frontier_backlog_resolved_residue_contract.py":
    raise SystemExit("frontier backlog must record enforced resolved-residue audit")
if audit.get("corrected_rows", 0) < corrected:
    raise SystemExit("frontier backlog resolved-residue audit corrected_rows understates resolved rows")
for rel in ["docs/40-session/frontier-backlog-resolved-residue-audit-2026-06-15.md", "tools/check_frontier_backlog_resolved_residue_contract.py"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"frontier backlog residue historical surface missing: {rel}")
if "review court" not in backlog.get("non_claim", ""):
    raise SystemExit("frontier backlog must retain anti-review-court non-claim")
print("check_frontier_backlog_resolved_residue_contract: OK")
