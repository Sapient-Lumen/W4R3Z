import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/package-identity-spillover-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "PACKAGE-IDENTITY-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]
if receipt.get("revision", "") < "rev0329":
    raise SystemExit("package identity witness requires rev0329 or later receipt posture")
if receipt.get("package_identity_witness", {}).get("selected_token") != "mixed-package-identity":
    raise SystemExit("package-identity selected token drifted")
family = vocab.get("families", {}).get("package_identity_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing package_identity_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/package-identity-spillover-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("package-identity family surfaces drifted")
for token in ["external-metadata-synchronized", "root-json-revision-synchronized", "current-key-spillover-detected", "license-revision-repaired", "path-alias-current-repaired", "package-identity-non-authoritative", "mixed-package-identity"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing package-identity token {token}")
for bad in ["package-identity-court", "metadata-sovereign", "release-name-tribunal", "license-revision-notary", "current-key-senate", "checksum-authority", "manifest-court", "identity-spillover-board"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing package-identity excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0128"), None)
if not row or row.get("canonical_family") != "package_identity_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0128")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("PACKAGE-IDENTITY-AUDIT stale or failing")
if not any(row.get("id") == "SA-0019" and row.get("frontier_id") == "OQ-0224" for row in assays):
    raise SystemExit("self-sufficiency ledger must retain SA-0019 for OQ-0224")
expected_validation_checks = [
    "tools/check_package_identity_witness_contract.py",
    "tools/check_package_identity_audit_contract.py",
    "tools/gen_package_identity_audit.py",
    "tools/check_external_metadata_contract.py",
    "tools/check_json_schema_surface_contract.py",
    "tools/check_current_witness_receipt_slot.py",
]
for rel in expected_validation_checks:
    if rel not in method:
        raise SystemExit(f"package-identity method surface missing retained validation check {rel}")
print("check_package_identity_witness_contract: OK")
