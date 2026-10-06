import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
rs = json.loads((ROOT / "RESOLUTION-LEDGER.json").read_text(encoding="utf-8"))["items"]
fp = json.loads((ROOT / "FOREIGN-PRESSURE-LEDGER.json").read_text(encoding="utf-8"))["items"]
tl = json.loads((ROOT / "DATACUBE-TRANSFER-LEDGER.json").read_text(encoding="utf-8"))["items"]
rev = receipt.get("revision")
if not rev:
    raise SystemExit("receipt missing revision")
for name, value in {
    "status.revision": status.get("revision"),
    "manifest.revision": manifest.get("revision"),
    "context.revision": context.get("revision"),
    "frontier.revision": frontier.get("revision"),
}.items():
    if value != rev:
        raise SystemExit(f"{name} mismatch: {value} != {rev}")
bundle = receipt.get("packaged_bundle_filename")
if manifest.get("bundle") != bundle:
    raise SystemExit("manifest bundle does not match receipt")
if status.get("operational_head", {}).get("surface") != bundle:
    raise SystemExit("status operational head does not match receipt bundle")
if receipt.get("current_import_id") != tl[-1]["id"] or receipt.get("current_pressure_id") != fp[-1]["id"]:
    raise SystemExit("receipt current transfer/pressure ids are stale")
latest_resolution = rs[-1]
if receipt.get("resolved_question") not in latest_resolution.get("resolved_objects", []):
    raise SystemExit("receipt resolved_question not carried by latest resolution")
next_oq = receipt.get("next_open_question")
frontier_id = frontier.get("primary_focus", {}).get("id")
context_id = context.get("open_questions", [{}])[-1].get("id")
if len({next_oq, frontier_id, context_id}) != 1:
    raise SystemExit(f"frontier mismatch: receipt={next_oq}, frontier={frontier_id}, context={context_id}")
if receipt.get("resolved_question") == next_oq:
    raise SystemExit("resolved question is still the frontier")
for entry in context.get("decay_watch_overdue", []):
    if entry.get("review_status") != "explicitly-overdue":
        raise SystemExit("overdue decay-watch entry lacks explicit-overdue status")
if not isinstance(context.get("queue_health"), dict):
    raise SystemExit("context missing queue health")
print("check_global_truth_surface_contract: OK")
