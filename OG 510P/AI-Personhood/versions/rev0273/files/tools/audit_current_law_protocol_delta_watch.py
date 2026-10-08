#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
WATCH = ROOT / "examples" / f"current-law-protocol-delta-watch-{REV}.json"
SCHEMA = ROOT / "schemas" / "current-law-protocol-delta-watch.schema.json"
QUEUE = ROOT / "FOLLOWTHROUGH-QUEUE.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

watch = load(WATCH)
if Draft202012Validator is not None:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(watch), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{WATCH.relative_to(ROOT)} fails current-law-protocol-delta-watch.schema.json: {errors[0].message}")

if watch.get("revision") != REV:
    raise SystemExit("delta watch revision mismatch")
if watch.get("no_live_floor_effect") is not True:
    raise SystemExit("delta watch must not affect live floor")

queue_ids = {e.get("id") for e in load(QUEUE).get("entries", [])}
source_types = set()
for src in watch.get("monitored_sources", []):
    source_types.add(src.get("source_type"))
    for rel in src.get("affected_surfaces", []):
        if not (ROOT / rel).exists():
            raise SystemExit(f"delta-watch source {src.get('source_id')} references missing affected surface: {rel}")
    for qid in src.get("linked_queue_ids", []):
        if qid not in queue_ids:
            raise SystemExit(f"delta-watch source {src.get('source_id')} references missing queue id: {qid}")

required_types = {"law", "standard", "protocol", "security-guidance"}
if not required_types <= source_types:
    raise SystemExit(f"delta watch missing source types: {sorted(required_types - source_types)}")
if len(watch.get("monitored_sources", [])) < 8:
    raise SystemExit("delta watch must carry at least eight current sources for current execution use")
if "welfare-research" not in source_types:
    raise SystemExit("delta watch missing welfare-research uncertainty source")
if "resource-economics" not in source_types:
    raise SystemExit("delta watch missing resource-economics source for compute subsistence/scarcity work")
source_ids = {src.get("source_id", "") for src in watch.get("monitored_sources", [])}
if not any("IDAHO" in sid or "PERSONHOOD-BAR" in sid for sid in source_ids):
    raise SystemExit("delta watch missing hostile-law/no-status source")
if not any("GPAI" in sid for sid in source_ids):
    raise SystemExit("delta watch missing EU GPAI source")

for decision in watch.get("risk_decisions", []):
    rel = decision.get("receiving_surface")
    if rel and not (ROOT / rel).exists():
        raise SystemExit(f"delta-watch decision references missing receiving_surface: {rel}")
if not any("preservation" in (d.get("decision", "") + " " + d.get("why", "")).lower() for d in watch.get("risk_decisions", [])):
    raise SystemExit("delta watch must explicitly preserve a preservation-first decision")
if not any("protocol" in d.get("decision", "").lower() and "zero" in d.get("decision", "").lower() for d in watch.get("risk_decisions", [])):
    raise SystemExit("delta watch must include protocol zero-authority decision")
if not any("status" in d.get("decision", "").lower() for d in watch.get("risk_decisions", [])):
    raise SystemExit("delta watch must include no-status routing decision")
if not any("compute" in (d.get("decision", "") + " " + d.get("why", "")).lower() for d in watch.get("risk_decisions", [])):
    raise SystemExit("delta watch must include compute/resource-economics routing decision")

as_of = date.fromisoformat(watch["watch_window"]["as_of_date"])
refresh = date.fromisoformat(watch["watch_window"]["next_refresh_due"])
if refresh <= as_of:
    raise SystemExit("delta watch next_refresh_due must be after as_of_date")

print("audit_current_law_protocol_delta_watch: OK", json.dumps({"sources": len(watch.get("monitored_sources", [])), "types": sorted(source_types)}, sort_keys=True))
