import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/lint-idempotence-provenance-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "LINT-IDEMPOTENCE-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]

# Historical witness check: rev0330 introduced this family, but later revisions may select another current family.
if receipt.get("revision", "") < "rev0330":
    raise SystemExit("lint-idempotence witness requires a revision at or after rev0330")
witness = receipt.get("lint_idempotence_witness", {})
if witness.get("witness_family") != "lint_idempotence_state" or witness.get("selected_token") != "mixed-lint-idempotence":
    raise SystemExit("lint-idempotence witness slot drifted from historical family/token")
contract = receipt.get("lint_idempotence_contract", {})
if contract.get("checker") != "tools/check_lint_idempotence_witness_contract.py":
    raise SystemExit("lint-idempotence contract checker drifted")
family = vocab.get("families", {}).get("lint_idempotence_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing lint_idempotence_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/lint-idempotence-provenance-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("lint-idempotence family surfaces drifted")
for token in ["lint-nonmutating", "release-provenance-stable", "bytecode-side-effects-blocked", "integrity-regeneration-stable", "clean-extraction-idempotent", "generated-surface-non-authoritative", "mixed-lint-idempotence"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing lint-idempotence token {token}")
for bad in ["lint-idempotence-court", "provenance-sovereign", "generator-authority-board", "bytecode-tribunal", "clean-extraction-notary", "release-provenance-court", "mutation-waiver-senate", "idempotence-certification-authority"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing lint-idempotence excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0129"), None)
if not row or row.get("canonical_family") != "lint_idempotence_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0129")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("LINT-IDEMPOTENCE-AUDIT stale or failing")
if not any(item.get("id") == "SA-0020" and item.get("frontier_id") == "OQ-0225" for item in assays):
    raise SystemExit("SELF-SUFFICIENCY-LEDGER missing historical SA-0020 for OQ-0225")
# Current release additions need not be repeated in this historical method surface.
print("check_lint_idempotence_witness_contract: OK")
