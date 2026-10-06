import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/basis-provenance-audit-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "BASIS-PROVENANCE-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]
if receipt.get("revision", "") < "rev0333":
    raise SystemExit("basis-provenance witness requires rev0333 or later receipt posture")
slot = receipt.get("current_witness_slot", {})
if slot.get("family") == "basis_provenance_state" and slot.get("handle") != "WVF-0132":
    raise SystemExit("basis-provenance witness slot handle drifted")
if receipt.get("basis_provenance_witness", {}).get("selected_token") != "mixed-basis-provenance":
    raise SystemExit("basis-provenance selected token drifted")
family = vocab.get("families", {}).get("basis_provenance_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing basis_provenance_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/basis-provenance-audit-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("basis-provenance family surfaces drifted")
for token in ["expected-head-current", "observed-head-current", "session-provenance-aligned", "direct-underlier-anchored", "innovation-anchor-resynced", "stale-carryover-blocked", "mixed-basis-provenance"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing basis-provenance token {token}")
for bad in ['basis-provenance-court', 'session-underlier-sovereign', 'reread-notary', 'anchor-freshness-tribunal', 'basis-waiver-board', 'resync-authority-senate', 'provenance-certification-court', 'underlier-currentness-oracle']:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing basis-provenance excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0132"), None)
if not row or row.get("canonical_family") != "basis_provenance_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0132")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("BASIS-PROVENANCE-AUDIT stale or failing")
basis_assay = next((row for row in assays if row.get("id") == "SA-0023"), None)
if not basis_assay or basis_assay.get("frontier_id") != "OQ-0228":
    raise SystemExit("self-sufficiency ledger must retain SA-0023 for OQ-0228")
expected_validation_checks = [
    "tools/check_basis_provenance_witness_contract.py",
    "tools/check_basis_provenance_audit_contract.py",
    "tools/check_basis_provenance_currentness_contract.py",
]
for rel in expected_validation_checks:
    if rel not in method:
        raise SystemExit(f"basis-provenance method surface missing retained validation check {rel}")
print("check_basis_provenance_witness_contract: OK")
