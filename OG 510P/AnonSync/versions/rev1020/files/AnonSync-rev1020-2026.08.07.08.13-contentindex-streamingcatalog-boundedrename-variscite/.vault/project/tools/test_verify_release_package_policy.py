#!/usr/bin/env python3
"""Executable regression matrix for release and bootstrap-wrapper policy."""
from __future__ import annotations

from pathlib import PurePosixPath

from verify_release_package import (
    analyze_bootstrap_wrapper_layout,
    ancestor_file_conflicts,
    bootstrap_restart_page_binding_violations,
    is_forbidden_release_file,
    normalized_member,
    sha256_bytes,
)


checks = 0


def require(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def require_raises(call, message: str) -> None:
    global checks
    checks += 1
    try:
        call()
    except ValueError:
        return
    raise AssertionError(message)


def test_generated_path_policy() -> None:
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
    for raw in rejected:
        require(
            is_forbidden_release_file(PurePosixPath(raw)),
            f"accepted forbidden path: {raw}",
        )
    for raw in accepted:
        require(
            not is_forbidden_release_file(PurePosixPath(raw)),
            f"rejected legitimate path: {raw}",
        )


def test_canonical_member_spelling() -> None:
    for raw in (
        "AnonSync/BOOTSTRAPROSE.md",
        "AnonSync/.vault/project/src/main.cpp",
        "AnonSync/.h0p3/donor/README.md",
    ):
        require(
            normalized_member(raw).as_posix() == raw,
            f"canonical member changed spelling: {raw}",
        )
    for raw in (
        "/AnonSync/file",
        "./AnonSync/file",
        "AnonSync//file",
        "AnonSync/./file",
        "AnonSync/../file",
        "AnonSync\\file",
        "AnonSync/file\x00tail",
    ):
        require_raises(
            lambda raw=raw: normalized_member(raw),
            f"accepted non-canonical or unsafe member spelling: {raw!r}",
        )


def test_hidden_wrapper_layout() -> None:
    entries = {
        "BOOTSTRAPROSE.md",
        ".vault",
        ".vault/README.md",
        ".vault/project",
        ".vault/project/CMakeLists.txt",
        ".vault/project/src",
        ".vault/project/src/main.cpp",
        ".vault/parent",
        ".vault/parent/LINEAGE.json",
        ".vault/source-objects",
        ".vault/source-objects/object.bin",
        ".vault/witnesses",
        ".vault/witnesses/release.json",
        ".h0p3",
        ".h0p3/donor",
        ".h0p3/donor/BOOTSTRAPROSE.md",
    }
    files = {
        "BOOTSTRAPROSE.md",
        ".vault/README.md",
        ".vault/project/CMakeLists.txt",
        ".vault/project/src/main.cpp",
        ".vault/parent/LINEAGE.json",
        ".vault/source-objects/object.bin",
        ".vault/witnesses/release.json",
        ".h0p3/donor/BOOTSTRAPROSE.md",
    }
    project, violations = analyze_bootstrap_wrapper_layout(entries, files)
    require(
        violations == [],
        f"rejected retained hidden donor/history material: {violations}",
    )
    require(
        project == {"CMakeLists.txt", "src/main.cpp"},
        f"hidden active project projection was wrong: {sorted(project)}",
    )

    _, visible_violation = analyze_bootstrap_wrapper_layout(
        entries | {"README.md"}, files | {"README.md"}
    )
    require(
        any("unexpected release-root entries" in item for item in visible_violation),
        "accepted a second visible release-root file",
    )
    _, missing_bootstrap = analyze_bootstrap_wrapper_layout(
        entries - {"BOOTSTRAPROSE.md"}, files - {"BOOTSTRAPROSE.md"}
    )
    require(
        any("not a regular root file" in item for item in missing_bootstrap),
        "accepted a wrapper without the visible restart page",
    )
    _, project_as_file = analyze_bootstrap_wrapper_layout(
        entries, files | {".vault/project"}
    )
    require(
        any(".vault/project must be a directory" in item for item in project_as_file),
        "accepted .vault/project as a regular file",
    )
    require(
        ancestor_file_conflicts(
            {".vault", ".vault/project", ".vault/project/src/main.cpp"},
            {".vault/project"},
        ) == [".vault/project is a file ancestor of .vault/project/src/main.cpp"],
        "did not reject a file/directory namespace collision",
    )


def test_visible_restart_page_binding() -> None:
    page = b"# AnonSync\n\nReplace Resilio Sync.\n"
    valid = {
        "revision": "rev0944",
        "restart_page": {
            "path": "BOOTSTRAPROSE.md",
            "bytes": len(page),
            "sha256": sha256_bytes(page),
        },
    }
    require(
        bootstrap_restart_page_binding_violations(valid, page) == [],
        "rejected an exact visible restart-page binding",
    )
    require(
        bootstrap_restart_page_binding_violations(
            {"revision": "rev0943"}, page
        ) == [],
        "made the rev0944 binding retroactive",
    )
    missing = bootstrap_restart_page_binding_violations(
        {"revision": "rev0944"}, page
    )
    require(
        any("absent" in item for item in missing),
        "accepted rev0944 without a visible restart-page binding",
    )
    changed = bootstrap_restart_page_binding_violations(valid, page + b"drift")
    require(
        any("actual=" in item for item in changed),
        "accepted a visible restart page that drifted from hidden release authority",
    )


def main() -> int:
    test_generated_path_policy()
    test_canonical_member_spelling()
    test_hidden_wrapper_layout()
    test_visible_restart_page_binding()
    print(f"release/bootstrap wrapper policy: {checks}/{checks} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
