import json
import pathlib
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER_SPECS = [
    ("FOLLOWTHROUGH-QUEUE.json", "followthrough_witness", "state"),
    ("ASSUMPTION-LEDGER.json", "assumption_witness", "state"),
    ("OBLIGATION-LEDGER.json", "obligation_witness", "state"),
    ("APPLICABILITY-LEDGER.json", "applicability_witness", "state"),
    ("FOREIGN-PRESSURE-LEDGER.json", "foreign_pressure_witness", "state"),
    ("DATACUBE-TRANSFER-LEDGER.json", "transfer_witness", "state"),
    ("RESOLUTION-LEDGER.json", "resolution_witness", "state"),
    ("RETROSPECTIVE-QUEUE.json", "retrospective_write_witness", "state"),
    ("FIREBREAK-LEDGER.json", "reasoning_firebreak_witness", "state"),
    ("SELF-SUFFICIENCY-LEDGER.json", "self_sufficiency_witness", "assay_state"),
]

def load(rel): return json.loads((ROOT / rel).read_text(encoding="utf-8"))

DEBT_STATE_SPECS = {
    "FOLLOWTHROUGH-QUEUE.json": {"state_key": "state", "live_state": "queued", "transition_keys": ["expiry_revision"]},
    "ASSUMPTION-LEDGER.json": {"state_key": "state", "live_state": "active", "transition_keys": ["retirement_revision"]},
    "OBLIGATION-LEDGER.json": {"state_key": "state", "live_state": "open", "transition_keys": ["retirement_revision"]},
    "RETROSPECTIVE-QUEUE.json": {"state_key": "state", "live_state": "cooling", "transition_keys": ["retirement_revision"]},
}

def debt_pressure_summary(root_revision: str):
    rows=[]
    transition_groups=defaultdict(lambda: {"count": 0, "ids": [], "states": Counter(), "all_have_reason": True, "latest_id_in_group": False})
    for rel, spec in DEBT_STATE_SPECS.items():
        data=load(rel); items=data.get("items", [])
        latest_id=items[-1].get("id") if items else None
        state_key=spec["state_key"]
        counts=Counter(str(item.get(state_key, item.get("state", "missing"))) for item in items)
        rows.append({
            "surface": rel,
            "state_key": state_key,
            "live_state": spec["live_state"],
            "item_count": len(items),
            "live_count": counts.get(spec["live_state"], 0),
            "latest_id": latest_id,
            "state_counts": dict(sorted(counts.items())),
        })
        for item in items:
            for key in spec["transition_keys"]:
                rev = item.get(key)
                if not rev:
                    continue
                group_key=(rel, key, str(rev))
                group=transition_groups[group_key]
                group["count"] += 1
                group["ids"].append(item.get("id"))
                group["states"][str(item.get(state_key, item.get("state", "missing")))] += 1
                if item.get("id") == latest_id:
                    group["latest_id_in_group"] = True
                reason = item.get("retirement_reason") or item.get("expiry_reason") or item.get("discharge")
                if not reason:
                    group["all_have_reason"] = False
    transitions=[]
    for (rel, key, rev), group in sorted(transition_groups.items()):
        transitions.append({
            "surface": rel,
            "transition_key": key,
            "transition_revision": rev,
            "count": group["count"],
            "ids_sample": group["ids"][:8],
            "state_counts": dict(sorted(group["states"].items())),
            "all_have_reason": group["all_have_reason"],
            "latest_id_in_group": group["latest_id_in_group"],
            "boundary": "bulk state transitions are sediment triage evidence only; they do not adjudicate truth, priority, or historical merit",
        })
    return {
        "state": "generated-ledger-debt-pressure-summary",
        "revision": root_revision,
        "rows": rows,
        "transition_groups": transitions,
        "non_review_gate": "a stale-debt burn-down is admissible only as state-count repair when transitioned rows are non-latest, retain reasons, and are not treated as semantic waivers",
    }


def witness_id(witness):
    if not isinstance(witness, dict): return None
    if witness.get("id"): return witness.get("id")
    surf = witness.get("witness_surface") or witness.get("assumption_surface")
    if isinstance(surf, str) and "#" in surf: return surf.rsplit("#", 1)[1]
    return None

receipt = load("REVISION-RECEIPT.json")
rows=[]
for rel, wkey, state_key in LEDGER_SPECS:
    data=load(rel); items=data.get("items", [])
    counts=dict(sorted(Counter(str(item.get(state_key, item.get("state", "missing"))) for item in items).items()))
    latest=items[-1] if items else {}
    rows.append({
        "surface": rel,
        "witness_key": wkey,
        "item_count": len(items),
        "latest_id": latest.get("id"),
        "latest_revision": latest.get("revision"),
        "receipt_witness_id": witness_id(receipt.get(wkey)),
        "state_key": state_key,
        "state_counts": counts,
        "aligned_with_receipt": latest.get("id") == witness_id(receipt.get(wkey)) if wkey != "self_sufficiency_witness" else latest.get("revision") == receipt.get("revision"),
    })
payload={
    "project":"DelayBasin",
    "revision":receipt["revision"],
    "surface":"LEDGER-AUDIT.json",
    "state":"generated-continuity-ledger-audit",
    "non_claim":"This is not a ledger review court, priority tribunal, or successor authority; it summarizes continuity-ledger shape and latest-id alignment only.",
    "generated_from":[rel for rel,_,_ in LEDGER_SPECS],
    "ledgers":rows,
    "debt_pressure": debt_pressure_summary(receipt["revision"]),
    "repair":"ordinary-continuation",
}
(ROOT / "LEDGER-AUDIT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
lines=["# Ledger audit", "", "Generated continuity-ledger inventory. This surface summarizes counts and latest-id alignment; it is not a ledger review court.", "", "| Surface | Items | Latest | Receipt witness | States |", "| --- | ---: | --- | --- | --- |"]
for row in rows:
    states=", ".join(f"{k}:{v}" for k,v in row["state_counts"].items())
    lines.append(f"| `{row['surface']}` | {row['item_count']} | `{row['latest_id']}` | `{row['receipt_witness_id']}` | {states} |")
lines.extend(["", "## Debt pressure", "", "This section is a non-review gate for stale-debt burn-downs: it records state counts and bulk transition groups without adjudicating historical merit.", ""])
debt = payload["debt_pressure"]
for row in debt["rows"]:
    lines.append(f"- `{row['surface']}` live `{row['live_state']}` count `{row['live_count']}` of `{row['item_count']}` items.")
if debt["transition_groups"]:
    lines.extend(["", "## Bulk state-transition groups"] )
    for group in debt["transition_groups"]:
        states=", ".join(f"{k}:{v}" for k,v in group["state_counts"].items())
        lines.append(f"- `{group['surface']}` `{group['transition_key']}` `{group['transition_revision']}` count `{group['count']}`; states {states}; latest-in-group `{group['latest_id_in_group']}`.")
(ROOT / "docs/00-meta/ledger-audit.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
print("wrote LEDGER-AUDIT.json")
print("wrote docs/00-meta/ledger-audit.md")
