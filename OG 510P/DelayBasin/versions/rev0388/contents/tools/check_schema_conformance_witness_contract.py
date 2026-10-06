import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/schema-conformance-audit-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "SCHEMA-CONFORMANCE-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]

# Historical witness check: rev0331 introduced this family; later revisions may select another current family.
if receipt.get("revision", "") < "rev0331":
    raise SystemExit("schema-conformance witness requires a revision at or after rev0331")
witness = receipt.get("schema_conformance_witness", {})
if witness.get("witness_family") != "schema_conformance_state" or witness.get("selected_token") != "mixed-schema-conformance":
    raise SystemExit("schema-conformance witness slot drifted from historical family/token")
contract = receipt.get("schema_conformance_contract", {})
if contract.get("checker") != "tools/check_schema_conformance_witness_contract.py":
    raise SystemExit("schema-conformance contract checker drifted")
family = vocab.get("families", {}).get("schema_conformance_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing schema_conformance_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/schema-conformance-audit-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("schema-conformance family surfaces drifted")
for token in ["schema-required-checked", "schema-type-checked", "schema-const-checked", "schema-self-checked", "public-shape-bounded", "semantic-non-authoritative", "mixed-schema-conformance"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing schema-conformance token {token}")
for bad in ["schema-conformance-court", "type-sovereign", "contract-adjudication-board", "schema-waiver-senate", "generated-audit-notary", "public-shape-tribunal", "validation-authority-court", "typed-surface-certifier"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing schema-conformance excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0130"), None)
if not row or row.get("canonical_family") != "schema_conformance_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0130")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("SCHEMA-CONFORMANCE-AUDIT stale or failing")
if not any(item.get("id") == "SA-0021" and item.get("frontier_id") == "OQ-0226" for item in assays):
    raise SystemExit("SELF-SUFFICIENCY-LEDGER missing historical SA-0021 for OQ-0226")
# Current release additions need not be repeated in this historical method surface.
print("check_schema_conformance_witness_contract: OK")
