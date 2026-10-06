import json
import pathlib

from lint_idempotence_audit_lib import build_lint_idempotence_audit, render_lint_idempotence_audit_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
payload = build_lint_idempotence_audit(ROOT)
(ROOT / "LINT-IDEMPOTENCE-AUDIT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs/00-meta/lint-idempotence-audit.md").write_text(render_lint_idempotence_audit_md(payload), encoding="utf-8")
print("wrote LINT-IDEMPOTENCE-AUDIT.json")
print("wrote docs/00-meta/lint-idempotence-audit.md")
