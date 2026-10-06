import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/currentness-cue-audit-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "CURRENTNESS-CUE-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]
if receipt.get("revision", "") < "rev0328":
    raise SystemExit("currentness witness requires rev0328 or later receipt posture")
if receipt.get("currentness_cue_witness", {}).get("selected_token") != "mixed-currentness-cue":
    raise SystemExit("currentness-cue selected token drifted")
family = vocab.get("families", {}).get("currentness_cue_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing currentness_cue_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/currentness-cue-audit-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("currentness-cue family surfaces drifted")
for token in ["stale-current-key-detected", "status-field-synchronized", "landing-cue-synchronized", "generated-audit-backed", "compact-surface-resynced", "currentness-non-authoritative", "mixed-currentness-cue"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing currentness-cue token {token}")
for bad in ["currentness-cue-court", "latest-head-tribunal", "status-sovereign", "bundle-revision-notary", "recency-court", "landing-cue-authority", "green-lint-currentness-waiver", "current-key-senate"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing currentness-cue excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0127"), None)
if not row or row.get("canonical_family") != "currentness_cue_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0127")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("CURRENTNESS-CUE-AUDIT stale or failing")
if not any(row.get("id") == "SA-0018" and row.get("frontier_id") == "OQ-0223" for row in assays):
    raise SystemExit("self-sufficiency ledger must retain SA-0018 for OQ-0223")
for rel in ["tools/check_currentness_witness_contract.py", "tools/check_currentness_cue_audit_contract.py", "tools/check_surface_status_current_key_coherence.py", "tools/check_current_witness_receipt_slot.py"]:
    if rel not in method:
        raise SystemExit(f"method surface missing validation check {rel}")
print("check_currentness_witness_contract: OK")
