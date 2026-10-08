#!/usr/bin/env python3
"""Build the rev0837 audit for package-release rights gating.

The rights ledger can intentionally keep the development gate green while
publication is blocked.  This audit makes sure that the operator-facing full
archive packager cannot emit a named release ZIP until that ledger is resolved.
rev0838 refactored the guard into scripts/publication_rights_gate.py; this
builder accepts that shared-helper form while preserving the rev0837 audit path.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "PUBLICATION_RIGHTS_GATE_REV0837.json"
MD_OUT = ROOT / "AUDIT" / "PUBLICATION_RIGHTS_GATE_REV0837.md"
PACKAGE = ROOT / "scripts" / "package_release.py"
HELPER = ROOT / "scripts" / "publication_rights_gate.py"
RIGHTS_LEDGER = ROOT / "RIGHTS" / "component_license_ledger.json"
REQUIRED_SNIPPETS = [
    "RIGHTS/component_license_ledger.json",
    "assert_publication_rights_ready",
    "publication rights gate blocked",
    "decision_required_before_publication",
    "blocking_findings",
    "root_license_or_notice_file_present",
    "before any release-root checks",
]
HELPER_REQUIRED_SNIPPETS = [
    "RIGHTS/component_license_ledger.json",
    "assert_publication_rights_ready",
    "publication_rights_gate_status",
    "publication rights gate blocked",
    "decision_required_before_publication",
    "blocking_findings",
    "root_license_or_notice_file_present",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def build(root: Path = ROOT) -> dict[str, Any]:
    package = root / "scripts" / "package_release.py"
    helper = root / "scripts" / "publication_rights_gate.py"
    ledger_path = root / "RIGHTS" / "component_license_ledger.json"
    package_text = package.read_text(encoding="utf-8") if package.is_file() else ""
    helper_text = helper.read_text(encoding="utf-8") if helper.is_file() else ""
    combined_text = package_text + "\n" + helper_text
    ledger = load_json(ledger_path) if ledger_path.is_file() else {}
    missing_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in combined_text]
    missing_helper_snippets = [snippet for snippet in HELPER_REQUIRED_SNIPPETS if snippet not in helper_text]
    call_index = package_text.find("\n    assert_publication_rights_ready(ROOT, 'package-release')")
    refresh_index = package_text.find("\n    run_package_refresh_sequence()")
    write_index = package_text.find("\n    digest = write_bundle_atomically(")
    guard_call_precedes_refresh = call_index >= 0 and refresh_index >= 0 and call_index < refresh_index
    guard_function_precedes_write = not missing_helper_snippets and call_index >= 0 and write_index >= 0 and call_index < write_index
    imports_shared_helper = "from publication_rights_gate import assert_publication_rights_ready" in package_text
    blockers = ledger.get("blocking_findings", []) if isinstance(ledger.get("blocking_findings", []), list) else []
    blocker_ids = [str(item.get("id")) for item in blockers if isinstance(item, dict) and item.get("id")]
    decision_required = bool(ledger.get("decision_required_before_publication"))
    status = str(ledger.get("status", "missing"))
    root_rights_present = bool(ledger.get("root_license_or_notice_file_present"))
    guarded = not missing_snippets and not missing_helper_snippets and imports_shared_helper and guard_call_precedes_refresh and guard_function_precedes_write
    current_tree_blocked = decision_required or bool(blocker_ids) or status.startswith("publication_blocked") or not root_rights_present
    return {
        "version": 2,
        "revision_context": "rev0837-session-patch-over-rev0836-over-rev0826; rev0838 shared-helper refactor compatible",
        "status": "package_release_guarded_and_current_tree_blocked" if guarded and current_tree_blocked else "publication_rights_gate_attention_required",
        "purpose": "Ensure scripts/package_release.py cannot emit a named full-archive ZIP while RIGHTS/component_license_ledger.json says publication rights are unresolved.",
        "protected_operator_path": "scripts/package_release.py",
        "shared_helper": "scripts/publication_rights_gate.py",
        "rights_ledger": "RIGHTS/component_license_ledger.json",
        "package_release_sha256": sha256_file(package) if package.is_file() else None,
        "shared_helper_sha256": sha256_file(helper) if helper.is_file() else None,
        "rights_ledger_sha256": sha256_file(ledger_path) if ledger_path.is_file() else None,
        "required_snippets": REQUIRED_SNIPPETS,
        "missing_required_snippets": missing_snippets,
        "helper_required_snippets": HELPER_REQUIRED_SNIPPETS,
        "missing_helper_required_snippets": missing_helper_snippets,
        "imports_shared_helper": imports_shared_helper,
        "guard_call_precedes_package_refresh": guard_call_precedes_refresh,
        "guard_function_precedes_zip_write": guard_function_precedes_write,
        "rights_ledger_status": status,
        "decision_required_before_publication": decision_required,
        "root_license_or_notice_file_present": root_rights_present,
        "blocking_finding_ids": blocker_ids,
        "current_tree_expected_to_refuse_package_release": current_tree_blocked,
        "validator": "scripts/validate_publication_rights_gate_rev0837.py",
        "builder": "scripts/build_publication_rights_gate_audit_rev0837.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Publication rights gate audit — rev0837",
        "",
        "This audit checks a concrete release-safety invariant: an archive may keep development validation green while rights are unresolved, but the full named packager must fail fast before creating a distributable ZIP.",
        "",
        f"- Status: `{data['status']}`",
        f"- Protected operator path: `{data['protected_operator_path']}`",
        f"- Shared helper: `{data.get('shared_helper', '')}`",
        f"- Rights ledger: `{data['rights_ledger']}`",
        f"- Package-release SHA-256: `{data['package_release_sha256']}`",
        f"- Shared-helper SHA-256: `{data.get('shared_helper_sha256')}`",
        f"- Rights-ledger SHA-256: `{data['rights_ledger_sha256']}`",
        f"- Imports shared helper: `{str(data.get('imports_shared_helper', False)).lower()}`",
        f"- Guard call precedes package refresh: `{str(data['guard_call_precedes_package_refresh']).lower()}`",
        f"- Guard resolves before ZIP writer: `{str(data['guard_function_precedes_zip_write']).lower()}`",
        f"- Current rights status: `{data['rights_ledger_status']}`",
        f"- Decision required before publication: `{str(data['decision_required_before_publication']).lower()}`",
        f"- Root LICENSE/COPYING/NOTICE present: `{str(data['root_license_or_notice_file_present']).lower()}`",
        f"- Current tree expected to refuse package release: `{str(data['current_tree_expected_to_refuse_package_release']).lower()}`",
        "",
        "## Blocking finding IDs surfaced by the rights ledger",
        "",
    ]
    if data["blocking_finding_ids"]:
        lines.extend(f"- `{item}`" for item in data["blocking_finding_ids"])
    else:
        lines.append("- none")
    lines.extend(["", "## Required guard snippets", ""])
    for snippet in data["required_snippets"]:
        mark = "present" if snippet not in data["missing_required_snippets"] else "missing"
        lines.append(f"- `{snippet}` — {mark}")
    lines.extend(["", "## Shared-helper required snippets", ""])
    for snippet in data.get("helper_required_snippets", []):
        mark = "present" if snippet not in data.get("missing_helper_required_snippets", []) else "missing"
        lines.append(f"- `{snippet}` — {mark}")
    lines.extend([
        "",
        "## Validator behavior",
        "",
        "`scripts/validate_publication_rights_gate_rev0837.py` regenerates this audit and invokes `scripts/package_release.py` in the current blocked tree. The expected result is a non-zero exit containing `publication rights gate blocked` before any package-refresh or package-write step appears.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(f"publication-rights-gate-audit-build: OK ({data['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
