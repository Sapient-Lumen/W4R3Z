import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/alias-retention-toolchain-manifest-witnesses.md").read_text(encoding="utf-8")
policy = json.loads((ROOT / "ALIAS-RETENTION-POLICY.json").read_text(encoding="utf-8"))
toolchain = json.loads((ROOT / "VALIDATION-TOOLCHAIN-MANIFEST.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]
if receipt.get("alias_retention_witness", {}).get("selected_token") != "mixed-alias-retention":
    raise SystemExit("alias-retention selected token drifted")
family = vocab.get("families", {}).get("alias_retention_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing alias_retention_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/alias-retention-toolchain-manifest-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("alias-retention family surfaces drifted")
for token in ["alias-retained-audit-only", "alias-compaction-deferred", "old-path-non-routing", "toolchain-fingerprinted", "manifest-backed-retirement", "admission-wrapper-audited", "mixed-alias-retention"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing alias-retention token {token}")
for bad in ["redirect-authority-board", "path-alias-court", "lint-sovereign", "toolchain-certification-tribunal", "hash-governance-court", "manifest-notary-authority", "old-path-resurrection-registry", "validation-score-sovereign"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in policy.get("non_claim", ""):
        raise SystemExit(f"missing alias-retention excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0126"), None)
if not row or row.get("canonical_family") != "alias_retention_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0126")
if policy.get("witness_family") != "alias_retention_state" or toolchain.get("revision") != receipt.get("revision"):
    raise SystemExit("alias-retention policy/toolchain manifest drifted")
if not any(row.get("id") == "SA-0017" and row.get("frontier_id") == "OQ-0222" for row in assays):
    raise SystemExit("self-sufficiency ledger must retain SA-0017 alias-retention assay")
for rel in ["tools/check_alias_retention_witness_contract.py", "tools/check_alias_retention_policy_contract.py", "tools/check_validation_toolchain_manifest_contract.py", "tools/check_current_witness_receipt_slot.py"]:
    if rel not in method:
        raise SystemExit(f"alias-retention method surface missing validation check {rel}")
print("check_alias_retention_witness_contract: OK")
