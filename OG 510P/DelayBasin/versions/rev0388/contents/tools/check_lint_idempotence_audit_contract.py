import json
import pathlib

from lint_idempotence_audit_lib import build_lint_idempotence_audit, render_lint_idempotence_audit_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
audit_path = ROOT / "LINT-IDEMPOTENCE-AUDIT.json"
guide_path = ROOT / "docs/00-meta/lint-idempotence-audit.md"
if not audit_path.exists() or not guide_path.exists():
    raise SystemExit("missing lint idempotence audit surface")
expected = build_lint_idempotence_audit(ROOT)
observed = json.loads(audit_path.read_text(encoding="utf-8"))
if observed != expected:
    raise SystemExit("LINT-IDEMPOTENCE-AUDIT.json drifted from generator")
if guide_path.read_text(encoding="utf-8") != render_lint_idempotence_audit_md(expected):
    raise SystemExit("docs/00-meta/lint-idempotence-audit.md drifted from generator")
if expected.get("counts", {}).get("failures") != 0:
    raise SystemExit("lint idempotence audit has failures")
for repaired_id in ["rev0329-lint-mutates-release-provenance", "rev0329-lint-bytecode-side-effect"]:
    if not any(row.get("id") == repaired_id for row in expected.get("known_repaired_findings", [])):
        raise SystemExit(f"missing repaired finding {repaired_id}")
print("check_lint_idempotence_audit_contract: OK")
