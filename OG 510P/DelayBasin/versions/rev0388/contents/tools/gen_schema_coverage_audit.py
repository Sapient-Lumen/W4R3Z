import pathlib

from schema_coverage_lib import write_schema_coverage_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
audit = write_schema_coverage_audit(ROOT)
print("wrote SCHEMA-COVERAGE-AUDIT.json")
print("wrote docs/00-meta/schema-coverage-audit.md")
if audit.get("counts", {}).get("failures"):
    raise SystemExit("schema coverage audit has failures")
