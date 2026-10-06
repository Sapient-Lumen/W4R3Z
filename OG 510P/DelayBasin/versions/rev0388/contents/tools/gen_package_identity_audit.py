import json
import pathlib

from package_identity_audit_lib import build_package_identity_audit, render_package_identity_audit_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
payload = build_package_identity_audit(ROOT)
(ROOT / "PACKAGE-IDENTITY-AUDIT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs/00-meta/package-identity-audit.md").write_text(render_package_identity_audit_md(payload), encoding="utf-8")
print("wrote PACKAGE-IDENTITY-AUDIT.json")
print("wrote docs/00-meta/package-identity-audit.md")
