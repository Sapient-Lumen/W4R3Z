import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ledger = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin" or ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("self-sufficiency ledger project/revision mismatch")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("self-sufficiency ledger missing items")
entry = next((item for item in items if item.get("id") == "SA-0001"), None)
if not entry:
    raise SystemExit("self-sufficiency ledger missing SA-0001")
required = {"capsule-only", "startup-compact", "full-archive"}
observed = {test.get("id") for test in entry.get("packet_tests", [])}
if observed != required:
    raise SystemExit(f"self-sufficiency tests mismatch: {observed}")
for test in entry["packet_tests"]:
    surfaces = test.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise SystemExit(f"{test.get('id')} missing surfaces")
    for rel in surfaces:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"self-sufficiency surface missing: {rel}")
if context.get("self_sufficiency_ledger", {}).get("surface") != "SELF-SUFFICIENCY-LEDGER.json":
    raise SystemExit("context-pack missing self-sufficiency ledger pointer")
print("check_self_sufficiency_ledger_contract: OK")
