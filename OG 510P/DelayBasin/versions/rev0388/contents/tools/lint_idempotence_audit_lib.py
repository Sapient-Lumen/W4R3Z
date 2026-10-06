import json
import pathlib
from typing import Any

from generated_surface_lib import DRIFT_VALIDATION_MODE


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def status(observed: Any, expected: Any) -> str:
    return "pass" if observed == expected else "fail"


def find_bytecode_artifacts(root: pathlib.Path) -> list[str]:
    rows: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if any(part == ".git" for part in path.parts):
            continue
        if path.is_dir() and path.name == "__pycache__":
            rows.append(rel + "/")
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            rows.append(rel)
    return sorted(rows)


def expected_package_command(manifest: dict[str, Any]) -> str:
    return f"make package-release STAMP={manifest['timestamp']} SLUG={manifest['slug']}"


def text_contains(root: pathlib.Path, rel: str, needle: str) -> bool:
    path = root / rel
    return path.exists() and needle in path.read_text(encoding="utf-8")


def build_lint_idempotence_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_json(root, "REVISION-RECEIPT.json")
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    provenance = load_json(root, "RELEASE-PROVENANCE.json")
    expected_command = expected_package_command(manifest)
    bytecode_artifacts = find_bytecode_artifacts(root)
    rows = [
        {
            "surface": "RELEASE-PROVENANCE.json",
            "path": "generator",
            "expected": "tools/package_release.py",
            "observed": provenance.get("generator"),
            "status": status(provenance.get("generator"), "tools/package_release.py"),
        },
        {
            "surface": "RELEASE-PROVENANCE.json",
            "path": "command",
            "expected": expected_command,
            "observed": provenance.get("command"),
            "status": status(provenance.get("command"), expected_command),
        },
        {
            "surface": "tools/gen_release_integrity.py",
            "path": "write_release_integrity_call",
            "expected": "canonical package provenance",
            "observed": "canonical package provenance" if text_contains(root, "tools/gen_release_integrity.py", "write_release_integrity(ROOT, None, None)") else "helper provenance",
            "status": "pass" if text_contains(root, "tools/gen_release_integrity.py", "write_release_integrity(ROOT, None, None)") else "fail",
        },
        {
            "surface": "tools/release_integrity_lib.py",
            "path": "canonical_package_command",
            "expected": "present",
            "observed": "present" if text_contains(root, "tools/release_integrity_lib.py", "def canonical_package_command") else "missing",
            "status": "pass" if text_contains(root, "tools/release_integrity_lib.py", "def canonical_package_command") else "fail",
        },
        {
            "surface": "Makefile",
            "path": "PYTHON",
            "expected": "PYTHONDONTWRITEBYTECODE=1",
            "observed": "PYTHONDONTWRITEBYTECODE=1" if text_contains(root, "Makefile", "PYTHONDONTWRITEBYTECODE=1") else "missing",
            "status": "pass" if text_contains(root, "Makefile", "PYTHONDONTWRITEBYTECODE=1") else "fail",
        },
        {
            "surface": "tools/run_lint_suite.py",
            "path": "sys.dont_write_bytecode",
            "expected": True,
            "observed": text_contains(root, "tools/run_lint_suite.py", "sys.dont_write_bytecode = True"),
            "status": "pass" if text_contains(root, "tools/run_lint_suite.py", "sys.dont_write_bytecode = True") else "fail",
        },
        {
            "surface": "tools/generated_surface_lib.py",
            "path": "generated_surface_drift.validation_mode",
            "expected": "temporary-copy-read-only-target",
            "observed": DRIFT_VALIDATION_MODE,
            "status": status(DRIFT_VALIDATION_MODE, "temporary-copy-read-only-target"),
        },
        {
            "surface": "tools/check_generated_surface_nonmutation_canary.py",
            "path": "validation_toolchain_membership",
            "expected": True,
            "observed": text_contains(root, "tools/validation_toolchain_lib.py", '"check_generated_surface_nonmutation_canary.py"'),
            "status": "pass" if text_contains(root, "tools/validation_toolchain_lib.py", '"check_generated_surface_nonmutation_canary.py"') else "fail",
        },
        {
            "surface": "worktree",
            "path": "bytecode_artifacts",
            "expected": [],
            "observed": bytecode_artifacts,
            "status": status(bytecode_artifacts, []),
        },
    ]
    failures = [row for row in rows if row["status"] != "pass"]
    return {
        "project": "DelayBasin",
        "revision": receipt.get("revision"),
        "surface": "LINT-IDEMPOTENCE-AUDIT.json",
        "guide_surface": "docs/00-meta/lint-idempotence-audit.md",
        "state": "generated-lint-idempotence-audit",
        "generated_from": [
            "REVISION-RECEIPT.json",
            "RELEASE-MANIFEST.json",
            "RELEASE-PROVENANCE.json",
            "Makefile",
            "tools/run_lint_suite.py",
            "tools/generated_surface_lib.py",
            "tools/check_generated_surface_nonmutation_canary.py",
            "tools/validation_toolchain_lib.py",
            "tools/gen_release_integrity.py",
            "tools/release_integrity_lib.py",
        ],
        "expected": {
            "revision": receipt.get("revision"),
            "bundle": manifest.get("bundle"),
            "resolved_question": receipt.get("resolved_question"),
            "next_open_question": receipt.get("next_open_question"),
            "resolution_id": receipt.get("resolution_witness", {}).get("id"),
            "provenance_generator": "tools/package_release.py",
            "provenance_command": expected_command,
        },
        "non_claim": "lint-idempotence-court, provenance-sovereign, generator-authority-board, bytecode-tribunal, clean-extraction-notary, release-provenance-court, mutation-waiver-senate, and idempotence-certification-authority are forbidden; this audit blocks validation side effects and release-provenance drift, but it does not certify semantic truth, legal status, minimality, or continuation authority.",
        "rows": rows,
        "known_repaired_findings": [
            {
                "id": "rev0329-lint-mutates-release-provenance",
                "finding": "A clean rev0329 extraction could pass make lint while rewriting RELEASE-PROVENANCE.json from tools/package_release.py to tools/gen_release_integrity.py.",
                "repair": "rev0330 makes gen_release_integrity emit canonical package provenance derived from RELEASE-MANIFEST.json, so lint regeneration and package-release provenance agree.",
                "status": "closed-by-rev0330",
            },
            {
                "id": "rev0329-lint-bytecode-side-effect",
                "finding": "A clean rev0329 make lint invocation left tools/__pycache__ bytecode artifacts even though release hygiene excluded them from packaging.",
                "repair": "rev0330 sets PYTHONDONTWRITEBYTECODE=1 in the Makefile and sets sys.dont_write_bytecode before the lint wrapper imports helper modules.",
                "status": "closed-by-rev0330",
            },
        ],
        "scan_policy": {
            "scope": "release provenance generator/command stability, read-only generated-surface drift detection, lint bytecode side effects, and integrity-regeneration routing",
            "repair": "fail closed on validation-side mutation; repair lint/package helper behavior instead of treating a green lint count as evidence that no files changed",
            "non_authority_boundary": "idempotence evidence is operational hygiene only, not a proof of semantic correctness, canon sufficiency, or release legitimacy",
        },
        "counts": {"rows": len(rows), "failures": len(failures), "bytecode_artifacts": len(bytecode_artifacts)},
        "failures": failures,
    }


def render_lint_idempotence_audit_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Lint idempotence audit")
    lines.append("")
    lines.append("This generated surface exposes validation-side effects so a green lint cannot silently rewrite release provenance, repair generated surfaces in place, or leave transient bytecode artifacts.")
    lines.append("")
    lines.append(f"- Revision: `{payload['revision']}`")
    lines.append(f"- Bundle: `{payload['expected']['bundle']}`")
    lines.append(f"- Resolved question: `{payload['expected']['resolved_question']}`")
    lines.append(f"- Live successor: `{payload['expected']['next_open_question']}`")
    lines.append(f"- Failures: `{payload['counts']['failures']}`")
    lines.append("")
    lines.append("## Non-claim")
    lines.append(payload["non_claim"])
    lines.append("")
    lines.append("## Rows")
    for row in payload["rows"]:
        lines.append(f"- `{row['surface']}#{row['path']}` — expected `{row['expected']}`, observed `{row['observed']}`: `{row['status']}`")
    lines.append("")
    lines.append("## Repaired findings")
    for row in payload["known_repaired_findings"]:
        lines.append(f"- `{row['id']}` — {row['finding']} Repair: {row['repair']}")
    lines.append("")
    lines.append("## Scan policy")
    lines.append(f"- Scope: {payload['scan_policy']['scope']}")
    lines.append(f"- Repair: {payload['scan_policy']['repair']}")
    lines.append(f"- Boundary: {payload['scan_policy']['non_authority_boundary']}")
    return "\n".join(lines).rstrip() + "\n"
