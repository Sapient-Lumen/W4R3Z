import pathlib

from archive_economy_audit_lib import write_archive_economy_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
audit = write_archive_economy_audit(ROOT)
print("wrote ARCHIVE-ECONOMY-AUDIT.json")
print("wrote docs/00-meta/archive-economy-audit.md")
if not audit.get("risk_flags"):
    print("archive economy audit found no threshold risk flags")
