import json
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]

from ledger_debt_policy_lib import (
    LEDGER_DEBT_POLICIES,
    live_retrospectives_with_nonlive_obligations,
    state_mirror_mismatches,
)

receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
revision = receipt.get("revision")
if not isinstance(revision, str) or not revision.startswith("rev"):
    raise SystemExit("ledger debt guard requires current receipt revision")

ledger_items: dict[str, list[dict]] = {}
problems: list[str] = []
for rel, spec in LEDGER_DEBT_POLICIES.items():
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list) or not items:
        problems.append(f"{rel} missing items")
        continue
    ledger_items[rel] = items

    counts = Counter(str(item.get(spec["state_key"], item.get("state", "missing"))) for item in items)
    live_count = counts.get(spec["live_state"], 0)
    if live_count > int(spec["budget"]):
        problems.append(f"{rel} live {spec['live_state']} count {live_count} exceeds budget {spec['budget']}")
    minimum_headroom = int(spec.get("minimum_headroom", 0))
    headroom = int(spec["budget"]) - live_count
    if headroom < minimum_headroom:
        problems.append(
            f"{rel} live {spec['live_state']} headroom {headroom} is below required reserve {minimum_headroom}; "
            "retire stale rows before admitting another live tail"
        )

    latest = items[-1]
    if latest.get("revision") != revision or latest.get("origin_revision") != revision:
        problems.append(f"{rel} latest row must originate in current revision {revision}")

    transitioned = [
        item for item in items[:-1]
        if re.fullmatch(r"rev\d{4}", str(item.get(spec["transition_key"], "")))
        and item.get(spec["state_key"], item.get("state")) == spec["transition_state"]
    ]
    if len(transitioned) < int(spec["min_cumulative_transitions"]):
        problems.append(f"{rel} cumulative stale-debt transition count {len(transitioned)} < {spec['min_cumulative_transitions']}")
    for item in transitioned:
        transition_revision = str(item.get(spec["transition_key"]))
        reason = item.get("retirement_reason") or item.get("expiry_reason") or item.get("discharge")
        # Legacy transitions predate the rev0355 budget guard and often used compact
        # disposition language. New guard-era transitions must name the revision
        # that made them non-live so the debt burn-down remains auditable.
        if (not item.get("cold_compacted")) and transition_revision >= "rev0355" and (not reason or transition_revision not in str(reason)):
            problems.append(f"{rel} {item.get('id')} missing transition reason naming {transition_revision}")
        if item.get("id") == latest.get("id"):
            problems.append(f"{rel} latest row must not be included in stale-debt transition")

    for mismatch in state_mirror_mismatches(items, spec):
        problems.append(
            f"{rel} {mismatch['id']} {mismatch['mirror_key']}={mismatch['mirror_state']} "
            f"disagrees with {mismatch['canonical_key']}={mismatch['canonical_state']}"
        )

retrospectives = ledger_items.get("RETROSPECTIVE-QUEUE.json", [])
obligations = ledger_items.get("OBLIGATION-LEDGER.json", [])
for orphan in live_retrospectives_with_nonlive_obligations(retrospectives, obligations):
    pairs = ", ".join(f"{row['id']}={row['state']}" for row in orphan["paired_obligations"])
    problems.append(
        f"RETROSPECTIVE-QUEUE.json {orphan['retrospective_id']} remains cooling while "
        f"same-origin obligations are non-live ({pairs})"
    )

if problems:
    raise SystemExit("ledger debt guard failed:\n- " + "\n- ".join(problems[:40]))
print("check_ledger_debt_guard: OK")
