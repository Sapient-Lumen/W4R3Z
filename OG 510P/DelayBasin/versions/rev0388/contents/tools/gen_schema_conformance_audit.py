import pathlib

from schema_conformance_lib import write_schema_conformance_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
audit = write_schema_conformance_audit(ROOT)
print("wrote SCHEMA-CONFORMANCE-AUDIT.json")
print("wrote docs/00-meta/schema-conformance-audit.md")
if audit.get("counts", {}).get("failures"):
    raise SystemExit("schema conformance audit has failures")
