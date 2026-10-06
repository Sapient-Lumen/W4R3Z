import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
audit = json.loads((ROOT / "LEDGER-AUDIT.json").read_text(encoding="utf-8"))
guide = (ROOT / "docs/00-meta/ledger-audit.md").read_text(encoding="utf-8")
if audit.get("project") != "DelayBasin" or audit.get("revision") != receipt.get("revision"):
    raise SystemExit("LEDGER-AUDIT project/revision drifted")
if "review court" not in audit.get("non_claim", "") or "not a ledger review court" not in guide:
    raise SystemExit("LEDGER-AUDIT missing non-authority warning")
rows = audit.get("ledgers")
if not isinstance(rows, list) or len(rows) < 10:
    raise SystemExit("LEDGER-AUDIT must cover root continuity ledgers plus self-sufficiency")

def wid(w):
    if not isinstance(w, dict): return None
    if w.get("id"): return w.get("id")
    for key in ("witness_surface", "assumption_surface"):
        val=w.get(key)
        if isinstance(val, str) and "#" in val: return val.rsplit("#",1)[1]
    return None
for row in rows:
    rel = row.get("surface")
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    items = data.get("items", [])
    if row.get("item_count") != len(items):
        raise SystemExit(f"LEDGER-AUDIT item_count drifted for {rel}")
    latest = items[-1]
    if row.get("latest_id") != latest.get("id") or row.get("latest_revision") != latest.get("revision"):
        raise SystemExit(f"LEDGER-AUDIT latest row drifted for {rel}")
    state_key = row.get("state_key")
    expected_counts = dict(sorted(Counter(str(item.get(state_key, item.get("state", "missing"))) for item in items).items()))
    if row.get("state_counts") != expected_counts:
        raise SystemExit(f"LEDGER-AUDIT state counts drifted for {rel}")
    if row.get("witness_key") != "self_sufficiency_witness":
        expected_wid = wid(receipt.get(row.get("witness_key")))
        if row.get("receipt_witness_id") != expected_wid or row.get("latest_id") != expected_wid:
            raise SystemExit(f"LEDGER-AUDIT receipt alignment drifted for {rel}")
print("check_ledger_audit_contract: OK")


debt = audit.get("debt_pressure")
if not isinstance(debt, dict) or debt.get("state") != "generated-ledger-debt-pressure-summary":
    raise SystemExit("LEDGER-AUDIT missing generated debt-pressure summary")
if "not treated as semantic waivers" not in debt.get("non_review_gate", ""):
    raise SystemExit("LEDGER-AUDIT debt-pressure summary missing non-review gate")
row_by_surface = {row.get("surface"): row for row in debt.get("rows", [])}
for rel, live_state in {
    "FOLLOWTHROUGH-QUEUE.json": "queued",
    "ASSUMPTION-LEDGER.json": "active",
    "OBLIGATION-LEDGER.json": "open",
    "RETROSPECTIVE-QUEUE.json": "cooling",
}.items():
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    items = data.get("items", [])
    row = row_by_surface.get(rel)
    if not row:
        raise SystemExit(f"LEDGER-AUDIT debt pressure missing surface: {rel}")
    counts = Counter(str(item.get(row.get("state_key"), item.get("state", "missing"))) for item in items)
    if row.get("live_state") != live_state or row.get("live_count") != counts.get(live_state, 0):
        raise SystemExit(f"LEDGER-AUDIT debt pressure live count drifted for {rel}")
    if row.get("state_counts") != dict(sorted(counts.items())):
        raise SystemExit(f"LEDGER-AUDIT debt pressure state counts drifted for {rel}")
for group in debt.get("transition_groups", []):
    if group.get("latest_id_in_group"):
        raise SystemExit("LEDGER-AUDIT stale-debt transition group includes latest ledger row")
    if not group.get("all_have_reason"):
        raise SystemExit("LEDGER-AUDIT stale-debt transition group has rows without reasons")
    states = group.get("state_counts", {})
    if not set(states).issubset({"expired", "retired"}):
        raise SystemExit(f"LEDGER-AUDIT stale-debt transition group has live states: {group}")
if "## Debt pressure" not in guide or "Bulk state-transition groups" not in guide:
    raise SystemExit("ledger audit guide missing debt-pressure sections")
