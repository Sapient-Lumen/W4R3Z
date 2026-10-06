import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))

wit = receipt.get("status_witness")
if not isinstance(wit, dict):
    raise SystemExit("receipt status_witness must be an object")
required = [
    "candidate_surface",
    "decision_surface",
    "decision_state",
    "execution_surface",
    "execution_state",
    "frozen_public_surface",
    "public_state",
    "durable_status_surface",
    "mismatch_consequence",
    "repair",
]
for key in required:
    if key not in wit:
        raise SystemExit(f"receipt status_witness missing key: {key}")

lanes = status.get("status_lanes", {})
if wit.get("candidate_surface") != lanes.get("candidate_surface"):
    raise SystemExit("receipt status_witness candidate_surface must match SURFACE-STATUS.json")
if wit.get("decision_surface") != lanes.get("decision_surface") or wit.get("decision_state") != lanes.get("decision_state"):
    raise SystemExit("receipt status_witness decision lane must match SURFACE-STATUS.json")
if wit.get("execution_surface") != lanes.get("execution_surface") or wit.get("execution_state") != lanes.get("execution_state"):
    raise SystemExit("receipt status_witness execution lane must match SURFACE-STATUS.json")
if wit.get("frozen_public_surface") != lanes.get("frozen_public_surface") or wit.get("public_state") != lanes.get("public_state"):
    raise SystemExit("receipt status_witness public lane must match SURFACE-STATUS.json")
if wit.get("durable_status_surface") != status.get("durable_status_surface"):
    raise SystemExit("receipt status_witness durable_status_surface must match SURFACE-STATUS.json")
if receipt.get("packaged_bundle_filename") != wit.get("frozen_public_surface"):
    raise SystemExit("receipt packaged_bundle_filename must match receipt status_witness frozen_public_surface")
if not isinstance(wit.get("mismatch_consequence"), str) or not wit.get("mismatch_consequence").strip():
    raise SystemExit("receipt status_witness mismatch_consequence must be a non-empty string")
if wit.get("repair") not in {"ordinary-continuation", "citation-warning", "rollback-or-repackage", "hold", "recover-resync"}:
    raise SystemExit("receipt status_witness.repair invalid")
for rel in [wit.get("decision_surface"), wit.get("execution_surface"), wit.get("durable_status_surface")]:
    if rel and not (ROOT / rel).exists():
        raise SystemExit(f"receipt status_witness referenced surface missing: {rel}")
print("check_status_lane_witness_contract: OK")
