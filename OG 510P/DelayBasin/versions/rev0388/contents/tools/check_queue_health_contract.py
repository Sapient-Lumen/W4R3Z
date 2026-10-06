import json
import pathlib

from ledger_debt_policy_lib import LEDGER_DEBT_POLICIES, live_debt_snapshot

ROOT = pathlib.Path(__file__).resolve().parents[1]
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
qh = context.get("queue_health")
if not isinstance(qh, dict):
    raise SystemExit("context-pack missing queue_health")

legacy_fields = {
    "FOLLOWTHROUGH-QUEUE.json": {
        "total": "followthrough_total",
        "live": "followthrough_queued",
        "latest": "latest_followthrough_id",
        "oldest": "oldest_queued_followthrough_id",
    },
    "ASSUMPTION-LEDGER.json": {
        "total": "assumptions_total",
        "live": "assumptions_active",
        "latest": "latest_assumption_id",
        "oldest": "oldest_active_assumption_id",
    },
    "OBLIGATION-LEDGER.json": {
        "total": "obligations_total",
        "live": "obligations_open",
        "latest": "latest_obligation_id",
        "oldest": "oldest_open_obligation_id",
    },
}

for filename, fields in legacy_fields.items():
    policy = LEDGER_DEBT_POLICIES[filename]
    items = json.loads((ROOT / filename).read_text(encoding="utf-8"))["items"]
    snapshot = live_debt_snapshot(items, policy, receipt["revision"])
    expected = {
        fields["total"]: len(items),
        fields["live"]: snapshot["live_count"],
        fields["latest"]: items[-1].get("id") if items else None,
        fields["oldest"]: snapshot["oldest_live_id"],
    }
    for key, value in expected.items():
        if qh.get(key) != value:
            raise SystemExit(f"queue_health.{key} mismatch")

if set(qh) != {key for fields in legacy_fields.values() for key in fields.values()}:
    raise SystemExit("queue_health must remain the compact backward-compatible field set")
print("check_queue_health_contract: OK")
