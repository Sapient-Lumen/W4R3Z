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
