import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/path-alias-ledger-audit-witnesses.md").read_text(encoding="utf-8")
ledger = json.loads((ROOT / "PATH-ALIAS-LEDGER.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]

if receipt.get("path_alias_witness", {}).get("witness_family") != "path_alias_state":
    raise SystemExit("path-alias receipt witness drifted")
if receipt.get("path_alias_witness", {}).get("selected_token") != "mixed-path-alias":
    raise SystemExit("path-alias selected token drifted")
family = vocab.get("families", {}).get("path_alias_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing path_alias_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/path-alias-ledger-audit-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("path-alias family surfaces drifted")
for token in ["batch-alias-bounded", "alias-ledger-bounded", "long-path-refactored", "stable-handle-routed", "reference-rewrite-verified", "path-budget-hardened", "old-path-audit-only", "generated-surface-resynced", "mixed-path-alias"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing path-alias token {token}")
for bad in ["path-migration-court", "alias-authority-board", "filename-canonization", "ledger-review-court", "stale-path-senate", "reference-rewrite-tribunal", "portability-notary", "redirect-registry-authority", "wrapper-regrowth-by-alias"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in ledger.get("non_claim", "") + " " + ledger.get("alias_rule", ""):
        raise SystemExit(f"missing path-alias excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0125"), None)
if not row or row.get("canonical_family") != "path_alias_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0125")
if ledger.get("governing_method") != "docs/10-method/path-alias-ledger-audit-witnesses.md" or ledger.get("entry_count", 0) < 20:
    raise SystemExit("PATH-ALIAS-LEDGER missing governing method or entries")
if "must not recreate wrapper files" not in ledger.get("batch_alias_rule", ""):
    raise SystemExit("PATH-ALIAS-LEDGER missing batch alias non-regrowth rule")
if not any(row.get("id") == "SA-0016" and row.get("frontier_id") == "OQ-0221" for row in assays):
    raise SystemExit("self-sufficiency ledger must retain SA-0016 path-alias assay")
for rel in ["tools/check_path_alias_witness_contract.py", "tools/check_path_alias_ledger_contract.py", "tools/check_path_portability_contract.py", "tools/check_json_schema_surface_contract.py", "tools/check_current_witness_receipt_slot.py"]:
    if rel not in method:
        raise SystemExit(f"path-alias method surface missing validation check {rel}")
print("check_path_alias_witness_contract: OK")
