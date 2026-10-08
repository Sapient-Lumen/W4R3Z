#!/usr/bin/env python3
"""Runtime regression matrix for release-package generated-artifact policy."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath


def load_verifier(root: Path):
    path = root / "tools" / "verify_release_package.py"
    spec = importlib.util.spec_from_file_location("anonsync_verify_release_package", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    verifier = load_verifier(args.root.resolve())

    allowed = (
        "REVISION_EVIDENCE/rev0886/validation/build-shape-observation.json",
        "REVISION_EVIDENCE/rev0886/validation/build-failure-analysis.md",
        "tools/build-helper.py",
        "docs/nested/build-policy.txt",
    )
    forbidden = (
        "build-debug/object.txt",
        "nested/build-release/object.txt",
        "CMakeFiles/rules.ninja",
        "nested/Testing/Temporary/LastTest.log",
        "src/object.o",
        "bin/program.exe",
        "tools/__pycache__/audit.pyc",
        ".git/config",
        "CMakeCache.txt",
        "core.dump",
    )

    checks: list[dict[str, object]] = []
    for name in allowed:
        observed = verifier.is_forbidden_release_file(PurePosixPath(name))
        checks.append({"path": name, "expected_forbidden": False, "observed_forbidden": observed,
                       "passed": observed is False})
    for name in forbidden:
        observed = verifier.is_forbidden_release_file(PurePosixPath(name))
        checks.append({"path": name, "expected_forbidden": True, "observed_forbidden": observed,
                       "passed": observed is True})

    donor_entries = {
        "BOOTSTRAPROSE.md",
        ".vault",
        ".vault/README.md",
        ".vault/project",
        ".vault/project/CMakeLists.txt",
        ".vault/parent",
        ".vault/parent/archive.zip",
        ".vault/source-objects",
        ".vault/source-objects/object.bin",
        ".vault/witnesses",
        ".vault/witnesses/receipt.json",
        ".h0p3",
        ".h0p3/README.md",
    }
    donor_files = {
        "BOOTSTRAPROSE.md",
        ".vault/README.md",
        ".vault/project/CMakeLists.txt",
        ".vault/parent/archive.zip",
        ".vault/source-objects/object.bin",
        ".vault/witnesses/receipt.json",
        ".h0p3/README.md",
    }
    project_names, violations = verifier.analyze_bootstrap_wrapper_layout(
        donor_entries, donor_files
    )
    checks.append({
        "path": "wrapper:retained-hidden-donors",
        "expected_forbidden": False,
        "observed_forbidden": bool(violations),
        "passed": not violations and project_names == {"CMakeLists.txt"},
        "detail": violations,
    })

    bad_entries = set(donor_entries) | {
        "README.md",
        ".vault/mystery",
        ".vault/mystery/file.txt",
    }
    bad_files = set(donor_files) | {"README.md", ".vault/mystery/file.txt"}
    _, violations = verifier.analyze_bootstrap_wrapper_layout(
        bad_entries, bad_files
    )
    checks.append({
        "path": "wrapper:visible-and-unknown-vault-content",
        "expected_forbidden": True,
        "observed_forbidden": bool(violations),
        "passed": any("unexpected release-root entries" in item for item in violations)
        and any("unexpected .vault entries" in item for item in violations),
        "detail": violations,
    })

    _, violations = verifier.analyze_bootstrap_wrapper_layout(
        donor_entries, donor_files | {".vault", ".h0p3"}
    )
    checks.append({
        "path": "wrapper:hidden-root-type-confusion",
        "expected_forbidden": True,
        "observed_forbidden": bool(violations),
        "passed": any(".vault must be" in item for item in violations)
        and any(".h0p3 must be" in item for item in violations),
        "detail": violations,
    })

    report = {
        "format": "anonsync-release-package-path-policy-test-v1",
        "check_count": len(checks),
        "passed_check_count": sum(bool(check["passed"]) for check in checks),
        "passed": all(bool(check["passed"]) for check in checks),
        "checks": checks,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
