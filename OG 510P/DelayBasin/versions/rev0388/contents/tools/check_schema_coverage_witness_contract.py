import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
vocab = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
method = (ROOT / "docs/10-method/schema-coverage-audit-witnesses.md").read_text(encoding="utf-8")
audit = json.loads((ROOT / "SCHEMA-COVERAGE-AUDIT.json").read_text(encoding="utf-8"))
assays = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))["items"]

# Historical witness check: rev0332 introduced this family; later revisions may select another current family.
if receipt.get("revision", "") < "rev0332":
    raise SystemExit("schema-coverage witness requires a revision at or after rev0332")
witness = receipt.get("schema_coverage_witness", {})
if witness.get("witness_family") != "schema_coverage_state" or witness.get("selected_token") != "mixed-schema-coverage":
    raise SystemExit("schema-coverage witness slot drifted from historical family/token")
contract = receipt.get("schema_coverage_contract", {})
if contract.get("checker") != "tools/check_schema_coverage_witness_contract.py":
    raise SystemExit("schema-coverage contract checker drifted")
family = vocab.get("families", {}).get("schema_coverage_state")
if not family:
    raise SystemExit("WITNESS-VOCABULARY missing schema_coverage_state")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", "docs/10-method/schema-coverage-audit-witnesses.md"]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("schema-coverage family surfaces drifted")
for token in ["root-json-inventoried", "schema-backed-classified", "contract-only-classified", "external-standard-classified", "validator-surface-linked", "coverage-gap-bounded", "mixed-schema-coverage"]:
    if token not in family.get("allowed", []) or token not in method:
        raise SystemExit(f"missing schema-coverage token {token}")
for bad in ["schema-coverage-court", "schema-completeness-sovereign", "contract-exemption-board", "coverage-waiver-senate", "schema-taxonomy-tribunal", "public-surface-notary", "validator-monopoly", "schema-backfill-authority"]:
    if bad not in family.get("excluded_synonyms", []) or bad not in method or bad not in audit.get("non_claim", ""):
        raise SystemExit(f"missing schema-coverage excluded synonym {bad}")
row = next((row for row in handles.get("families", []) if row.get("handle") == "WVF-0131"), None)
if not row or row.get("canonical_family") != "schema_coverage_state":
    raise SystemExit("WITNESS-FAMILY-HANDLES missing WVF-0131")
if audit.get("revision") != receipt.get("revision") or audit.get("counts", {}).get("failures") != 0:
    raise SystemExit("SCHEMA-COVERAGE-AUDIT stale or failing")
if not any(item.get("id") == "SA-0022" and item.get("frontier_id") == "OQ-0227" for item in assays):
    raise SystemExit("SELF-SUFFICIENCY-LEDGER missing historical SA-0022 for OQ-0227")
print("check_schema_coverage_witness_contract: OK")
