import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/release-hardening-witnesses.md").read_text(encoding="utf-8")
if receipt.get("release_hardening_witness", {}).get("selected_token") != "mixed-release-hardening":
    raise SystemExit("release-hardening selected token drifted")
family = vocab.get("families", {}).get("release_hardening_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing release_hardening_state")
if family.get("surfaces") != ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/release-hardening-witnesses.md"]:
    raise SystemExit("release-hardening family surfaces drifted")
for token in ["receipt-delta-coherent", "path-portable-bounded", "release-manifest-hashed", "schema-backed", "assay-scored", "metadata-exposed", "mixed-release-hardening"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing release-hardening token {token}")
for bad in ["tombstone-history-review-layer", "portable-closeout-history-expiry-court", "warning-renewal-by-closeout-history", "successor-review-senate", "redaction-vault-by-history-portability", "self-certifying-release-court", "checksum-tribunal", "canary-review-board"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method:
        raise SystemExit(f"missing release-hardening excluded synonym {bad}")
handle = [row for row in handles.get("families", []) if row.get("handle") == "WVF-0123"]
if not handle or handle[0].get("canonical_family") != "release_hardening_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0123")
for rel in ["tools/check_receipt_delta_coherence.py", "tools/check_path_portability_contract.py", "tools/check_release_integrity_contract.py", "tools/check_self_sufficiency_assay_contract.py"]:
    if rel not in method:
        raise SystemExit(f"method surface missing validation check {rel}")
print("check_release_hardening_witness_contract: OK")
