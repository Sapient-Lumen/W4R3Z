import json
import pathlib

from basis_provenance_audit_lib import build_basis_provenance_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "BASIS-PROVENANCE-AUDIT.json"
GUIDE = ROOT / "docs/00-meta/basis-provenance-audit.md"
SCHEMA = ROOT / "schemas/basis-provenance-audit.schema.json"
for path in (AUDIT, GUIDE, SCHEMA):
    if not path.exists():
        raise SystemExit(f"missing basis provenance surface: {path.relative_to(ROOT)}")
actual = json.loads(AUDIT.read_text(encoding="utf-8"))
expected = build_basis_provenance_audit(ROOT)
if actual != expected:
    raise SystemExit("BASIS-PROVENANCE-AUDIT.json drifted from generated basis provenance audit")
if actual.get("counts", {}).get("failures") != 0 or actual.get("failures"):
    raise SystemExit("BASIS-PROVENANCE-AUDIT.json must have zero failures")
text = GUIDE.read_text(encoding="utf-8")
for needle in ["not a basis-provenance-court", "session-underlier hygiene", "does not certify semantic truth"]:
    if needle not in text:
        raise SystemExit(f"basis provenance guide missing {needle}")
print("check_basis_provenance_audit_contract: OK")
