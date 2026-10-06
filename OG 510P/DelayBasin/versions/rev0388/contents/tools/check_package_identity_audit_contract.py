import json
import pathlib

from package_identity_audit_lib import build_package_identity_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "PACKAGE-IDENTITY-AUDIT.json"
GUIDE = ROOT / "docs/00-meta/package-identity-audit.md"
if not AUDIT.exists() or not GUIDE.exists():
    raise SystemExit("missing package identity audit surfaces")
observed = json.loads(AUDIT.read_text(encoding="utf-8"))
expected = build_package_identity_audit(ROOT)
if observed != expected:
    raise SystemExit("PACKAGE-IDENTITY-AUDIT.json drifted; run tools/gen_package_identity_audit.py")
if observed.get("counts", {}).get("failures") != 0 or observed.get("failures"):
    raise SystemExit("PACKAGE-IDENTITY-AUDIT contains failures")
guide = GUIDE.read_text(encoding="utf-8")
for needle in ["# Package identity audit", "Failures: `0`", "rev0328-license-stale-release-line", "rev0328-path-alias-current-revision-stale"]:
    if needle not in guide:
        raise SystemExit(f"package identity audit guide missing {needle}")
for bad in ["package-identity-court", "metadata-sovereign", "release-name-tribunal", "license-revision-notary", "current-key-senate", "checksum-authority", "manifest-court", "identity-spillover-board"]:
    if bad not in observed.get("non_claim", "") or bad not in guide:
        raise SystemExit(f"package identity audit missing non-claim {bad}")
print("check_package_identity_audit_contract: OK")
