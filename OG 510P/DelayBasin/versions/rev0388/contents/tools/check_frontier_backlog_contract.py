import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
backlog = json.loads((ROOT / "FRONTIER-BACKLOG.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
if backlog.get("revision") != receipt.get("revision"):
    raise SystemExit("FRONTIER-BACKLOG revision drifted")
items = backlog.get("items") or []
if not items or items[0].get("id") != receipt.get("next_open_question") or items[0].get("priority") != 1:
    raise SystemExit("FRONTIER-BACKLOG top priority must be live successor question")
for row in items:
    if "next_test" not in row or "fanout" not in row or not row.get("allowed_action"):
        raise SystemExit(f"frontier backlog item incomplete: {row.get('id')}")
if "review court" not in backlog.get("non_claim", ""):
    raise SystemExit("FRONTIER-BACKLOG missing anti-review-court non-claim")
print("check_frontier_backlog_contract: OK")
