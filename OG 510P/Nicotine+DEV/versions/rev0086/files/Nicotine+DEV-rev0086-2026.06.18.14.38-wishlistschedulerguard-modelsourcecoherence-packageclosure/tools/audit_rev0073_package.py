#!/usr/bin/env python3
"""Fail-closed coherence audit for the rev0073 research cube package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REVISION = "rev0073"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
MANIFEST_PATH = Path("handoff/rev0073/MANIFEST.sha256")
ARCHIVED_U123_HASHES = {
    Path("docs/archive/rev0072-active-u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py"): "375997c599f99e3add46952d35b95b5af7a2e923369062ae6c249ed723338620",
    Path("docs/archive/rev0072-active-u123/test_downloads_duplicate_transfer_token_fixed_regression.py"): "f16f2fc81bc02ef17b17ca6f269da9cfd3298002264930588d70bccdd9f6d6c9",
    Path("docs/archive/rev0072-active-u123/test_downloads_duplicate_transfer_token_identity_guard_regression.py"): "7ea766956d19ebef0276399e7a345230e7c7403b6d899a163331a35ca20690ca",
    Path("docs/archive/rev0072-active-u123/test_downloads_duplicate_transfer_token_reproducer.py"): "7e8d6d79851bba75a3096749f338a7afd1658ed0e8c2184115a235eb77e5fd38",
}

SELF_EXCLUDED = {
    Path("data/rev0073_package_preflight.json"),
    Path("evidence/rev0073-package-validation.md"),
}

REQUIRED_PATHS = (
    Path("README.md"),
    Path("REVISION.txt"),
    Path("docs/START-HERE.md"),
    Path("docs/U123-CURRENT-DISPOSITION-REV0073.md"),
    Path("docs/U123-ARTIFACT-COHERENCE-REFACTOR-REV0073.md"),
    Path("docs/VALIDATION-HARNESS-ISOLATION-REV0073.md"),
    Path("docs/UPSTREAM-AI-CONTRIBUTION-BOUNDARY-REV0073.md"),
    Path("docs/DUPLICATE-PROVENANCE-AUDIT-REV0073.md"),
    Path("docs/SELF-REFERENTIAL-AUDIT-REFACTOR-REV0073.md"),
    Path("docs/PACKAGE-COHERENCE-GATE-REV0073.md"),
    Path("data/rev0073_u123_disposition_summary.json"),
    Path("data/rev0073_u123_native_patch_summary.json"),
    Path("data/rev0073_research_boundary_summary.json"),
    Path("data/rev0073_delta_inventory.csv"),
    Path("data/rev0073_delta_inventory.json"),
    Path("data/rev0073_package_preflight.json"),
    Path("handoff/rev0073/README.md"),
    Path("handoff/rev0073/REVISION-SUMMARY.md"),
    Path("handoff/rev0073/U123-RESEARCH-DISPOSITION.md"),
    Path("handoff/rev0073/UPSTREAM-USE-BOUNDARY.md"),
    Path("handoff/rev0073/u123/README.md"),
    Path("handoff/rev0073/u123-research/README.md"),
    Path("evidence/rev0073-u123-public-overlap.md"),
    Path("evidence/rev0073-research-boundary-audit.md"),
    Path("evidence/rev0073-package-validation.md"),
    Path("tools/probe_rev0073_u123_disposition.py"),
    Path("tools/probe_rev0073_u123_native_patch.py"),
    Path("tools/audit_rev0073_research_boundary.py"),
    Path("tools/audit_rev0073_package.py"),
    Path("tools/build_rev0073_delta_inventory.py"),
    Path("tools/run_u123_state_matrix_rev0073.py"),
    Path("tools/measure_u123_burst_rev0073.py"),
)

CURRENT_PYTHON_GLOBS = (
    "maintainer_artifacts/u123/*.py",
    "tools/*rev0073*.py",
    "tools/archive/rev0073/*.py",
)

STALE_CURRENT_TOKENS = (
    "rev0073_u123_unit_parity",
    "probe_rev0073_u123_current.py",
    "code-only-p0.patch",
    "18,333",
    "63.86%",
)

CURRENT_TEXT_PATHS = (
    Path("README.md"),
    Path("docs/START-HERE.md"),
    Path("docs/U123-CURRENT-DISPOSITION-REV0073.md"),
    Path("docs/U123-ARTIFACT-COHERENCE-REFACTOR-REV0073.md"),
    Path("docs/VALIDATION-HARNESS-ISOLATION-REV0073.md"),
    Path("docs/UPSTREAM-AI-CONTRIBUTION-BOUNDARY-REV0073.md"),
    Path("docs/DUPLICATE-PROVENANCE-AUDIT-REV0073.md"),
    Path("docs/SELF-REFERENTIAL-AUDIT-REFACTOR-REV0073.md"),
    Path("docs/PACKAGE-COHERENCE-GATE-REV0073.md"),
    Path("handoff/rev0073/README.md"),
    Path("handoff/rev0073/REVISION-SUMMARY.md"),
    Path("handoff/rev0073/U123-RESEARCH-DISPOSITION.md"),
    Path("handoff/rev0073/UPSTREAM-USE-BOUNDARY.md"),
    Path("handoff/rev0073/u123/README.md"),
    Path("handoff/rev0073/u123-research/README.md"),
    Path("maintainer_artifacts/u123/README.md"),
    Path("workspace/NEXT-REVISION-QUEUE.md"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def all_files(root: Path) -> list[Path]:
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root) != MANIFEST_PATH
    )


def verify_manifest(root: Path, errors: list[str]) -> dict[str, Any]:
    path = root / MANIFEST_PATH
    if not path.is_file():
        errors.append(f"missing manifest: {MANIFEST_PATH}")
        return {"status": "missing", "rows": 0}

    rows: dict[Path, str] = {}
    malformed: list[str] = []
    duplicate_paths: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            malformed.append(f"line {number}")
            continue
        relative_path = Path(relative)
        if relative_path in rows:
            duplicate_paths.append(relative)
        rows[relative_path] = digest
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
            malformed.append(f"line {number} digest")

    if malformed:
        errors.append("malformed manifest rows: " + ", ".join(malformed))

    actual = set(all_files(root))
    listed = set(rows)
    missing = sorted(actual - listed)
    extra = sorted(listed - actual)
    mismatched = sorted(
        relative
        for relative in actual & listed
        if sha256_file(root / relative) != rows[relative]
    )

    if duplicate_paths:
        errors.append(f"manifest has duplicate path rows: {duplicate_paths[:5]}")
    if missing:
        errors.append(f"manifest missing {len(missing)} file(s): {missing[:5]}")
    if extra:
        errors.append(f"manifest has {len(extra)} extra file(s): {extra[:5]}")
    if mismatched:
        errors.append(f"manifest hash mismatch for {len(mismatched)} file(s): {mismatched[:5]}")

    return {
        "status": "pass" if not (malformed or duplicate_paths or missing or extra or mismatched) else "fail",
        "rows": len(rows),
        "missing": [str(item) for item in missing],
        "extra": [str(item) for item in extra],
        "mismatched": [str(item) for item in mismatched],
        "duplicate_paths": duplicate_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allow-missing-manifest", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    missing_required = [str(path) for path in REQUIRED_PATHS if not (root / path).is_file()]
    if missing_required:
        errors.append("missing required paths: " + ", ".join(missing_required))

    revision = (root / "REVISION.txt").read_text(encoding="utf-8").strip() if (root / "REVISION.txt").is_file() else ""
    if revision != REVISION:
        errors.append(f"REVISION.txt is {revision!r}, expected {REVISION!r}")

    forbidden_paths: list[str] = []
    symlinks: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            symlinks.append(str(relative))
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in relative.parts):
            forbidden_paths.append(str(relative))
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            forbidden_paths.append(str(relative))
        elif path.is_dir() and path.name == "pynicotine":
            forbidden_paths.append(str(relative))
        elif path.is_file() and "nicotine-source" in path.name.lower():
            forbidden_paths.append(str(relative))

    if forbidden_paths:
        errors.append(f"forbidden generated/source paths: {forbidden_paths[:10]}")
    if symlinks:
        errors.append(f"symlinks are not allowed in package: {symlinks[:10]}")

    compile_rows: list[dict[str, str]] = []
    seen: set[Path] = set()
    for pattern in CURRENT_PYTHON_GLOBS:
        for path in sorted(root.glob(pattern)):
            relative = path.relative_to(root)
            if relative in seen or not path.is_file():
                continue
            seen.add(relative)
            try:
                source = path.read_text(encoding="utf-8")
                compile(source, str(relative), "exec")
                status, error = "pass", ""
            except Exception as exc:  # pragma: no cover - audit output
                status, error = "fail", f"{type(exc).__name__}: {exc}"
                errors.append(f"compile failed for {relative}: {error}")
            compile_rows.append({"path": str(relative), "status": status, "error": error})

    stale_hits: list[dict[str, str]] = []
    for relative in CURRENT_TEXT_PATHS:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in STALE_CURRENT_TOKENS:
            if token in text:
                stale_hits.append({"path": str(relative), "token": token})
    if stale_hits:
        errors.append(f"stale current-surface tokens: {stale_hits}")

    status_checks: list[dict[str, Any]] = []
    try:
        disposition = load_json(root, "data/rev0073_u123_disposition_summary.json")
        checks = {
            "disposition_status": disposition.get("status") == "pass",
            "exact_current_ref": disposition.get("exact_current_ref_match") is True,
            "expected_ref": disposition.get("expected_ref") == EXPECTED_REF,
            "focused_18_of_18": (
                disposition.get("test_expectations_passed"),
                disposition.get("test_expectations_total"),
            ) == (18, 18),
            "burst_3_of_3": (
                disposition.get("burst_expectations_passed"),
                disposition.get("burst_expectations_total"),
            ) == (3, 3),
            "upstream_parity": disposition.get("upstream_unit_parity") is True,
        }
        status_checks.extend({"check": key, "pass": value} for key, value in checks.items())
        for patch_row in disposition.get("patches", []):
            patch_path = root / str(patch_row.get("patch", ""))
            patch_ok = (
                patch_path.is_file()
                and sha256_file(patch_path) == patch_row.get("sha256")
                and patch_row.get("status") == "pass"
            )
            status_checks.append({
                "check": f"disposition_patch_hash:{patch_row.get('state', 'unknown')}",
                "pass": patch_ok,
            })
    except Exception as exc:
        errors.append(f"could not inspect disposition summary: {exc}")

    try:
        native = load_json(root, "data/rev0073_u123_native_patch_summary.json")
        checks = {
            "native_patch_status": native.get("status") == "pass",
            "native_patch_3_of_3": (
                native.get("test_expectations_passed"),
                native.get("test_expectations_total"),
            ) == (3, 3),
            "native_patch_ref": native.get("expected_ref") == EXPECTED_REF,
        }
        status_checks.extend({"check": key, "pass": value} for key, value in checks.items())
        for patch_row in native.get("patches", []):
            patch_path = root / str(patch_row.get("patch", ""))
            patch_ok = (
                patch_path.is_file()
                and sha256_file(patch_path) == patch_row.get("sha256")
                and patch_row.get("status") == "pass"
            )
            status_checks.append({
                "check": f"native_patch_hash:{patch_row.get('state', 'unknown')}",
                "pass": patch_ok,
            })
    except Exception as exc:
        errors.append(f"could not inspect native-patch summary: {exc}")

    try:
        boundary = load_json(root, "data/rev0073_research_boundary_summary.json")
        status_checks.append({"check": "research_boundary_status", "pass": boundary.get("status") == "pass"})
        status_checks.append({"check": "research_boundary_idempotence", "pass": boundary.get("idempotence_verified") is True})
    except Exception as exc:
        errors.append(f"could not inspect research-boundary summary: {exc}")

    for relative, expected_digest in ARCHIVED_U123_HASHES.items():
        path = root / relative
        status_checks.append({
            "check": f"rev0072_archive_hash:{relative.name}",
            "pass": path.is_file() and sha256_file(path) == expected_digest,
        })

    failed_checks = [row["check"] for row in status_checks if not row["pass"]]
    if failed_checks:
        errors.append("failed status checks: " + ", ".join(failed_checks))

    if (root / MANIFEST_PATH).is_file():
        manifest = verify_manifest(root, errors)
    elif args.allow_missing_manifest:
        manifest = {"status": "not-yet-generated", "rows": 0}
    else:
        manifest = verify_manifest(root, errors)

    files = [path for path in all_files(root) if path not in SELF_EXCLUDED]
    payload_bytes = sum((root / path).stat().st_size for path in files)
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "root": ".",
        "payload_files_excluding_self_outputs_and_manifest": len(files),
        "payload_bytes_excluding_self_outputs_and_manifest": payload_bytes,
        "required_paths": len(REQUIRED_PATHS),
        "missing_required_paths": missing_required,
        "compiled_python_files": len(compile_rows),
        "compile_failures": [row for row in compile_rows if row["status"] != "pass"],
        "forbidden_paths": forbidden_paths,
        "symlinks": symlinks,
        "stale_current_surface_hits": stale_hits,
        "status_checks": status_checks,
        "manifest": manifest,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
