#!/usr/bin/env python3
"""Executable regression matrix for release-path artifact policy."""
from __future__ import annotations

from pathlib import PurePosixPath

from verify_release_package import is_forbidden_release_file


def main() -> int:
    rejected = (
        ".git/HEAD",
        "build/CMakeCache.txt",
        "build-debug/src/object.o",
        "cmake-build-release/bin/anonsync_core",
        "src/CMakeFiles/anonsync.dir/object.o",
        "src/object.o",
        "tools/__pycache__/audit.cpython-313.pyc",
        "core.dump",
    )
    accepted = (
        "REVISION_EVIDENCE/rev0886/validation/build-shape-observation.json",
        "REVISION_EVIDENCE/rev0886/validation/cmake-build-observation.json",
        "docs/rebuild-notes.md",
        "build-report.json",
        "src/build_policy.cpp",
    )

    failures: list[str] = []
    for raw in rejected:
        if not is_forbidden_release_file(PurePosixPath(raw)):
            failures.append(f"accepted forbidden path: {raw}")
    for raw in accepted:
        if is_forbidden_release_file(PurePosixPath(raw)):
            failures.append(f"rejected legitimate path: {raw}")

    if failures:
        raise SystemExit("release path policy failures:\n" + "\n".join(failures))
    print(
        "release path policy: "
        f"{len(rejected) + len(accepted)}/{len(rejected) + len(accepted)} checks passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
