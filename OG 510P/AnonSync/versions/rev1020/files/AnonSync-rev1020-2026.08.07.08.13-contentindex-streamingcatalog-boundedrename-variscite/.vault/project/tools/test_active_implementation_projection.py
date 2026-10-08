#!/usr/bin/env python3
"""Regression tests for versioned active-implementation projections."""

from __future__ import annotations

import hashlib

from verify_release_package import (
    ACTIVE_PROJECTION_V2_FORMAT,
    ACTIVE_PROJECTION_V3_FORMAT,
    active_projection_format_allowed_for_revision,
    compute_active_projection,
)


def expected_digest(entries: list[tuple[str, bytes]]) -> str:
    material = bytearray()
    for path, data in sorted(entries):
        material.extend(f"{hashlib.sha256(data).hexdigest()}  {path}\n".encode())
    return hashlib.sha256(material).hexdigest()


def main() -> int:
    files = {
        "CMakeLists.txt": b"root-build-authority\n",
        "src/core.cpp": b"core\n",
        "tests/core_test.cpp": b"test\n",
        "tools/audit.py": b"audit\n",
        "third_party/vendor.c": b"vendor\n",
        "fuzz/core_fuzz.cpp": b"fuzz\n",
        "cmake/ReviewedProfile.cmake": b"profile-v1\n",
        "docs/overview.md": b"documentation\n",
    }
    names = set(files)

    def read(name: str) -> bytes:
        return files[name]

    checks = 0
    v1 = compute_active_projection(names, read, projection_format=None)
    v1_paths = {entry["path"] for entry in v1["files"]}
    assert "fuzz/core_fuzz.cpp" not in v1_paths
    assert "cmake/ReviewedProfile.cmake" not in v1_paths
    checks += 1

    v2 = compute_active_projection(
        names,
        read,
        projection_format=ACTIVE_PROJECTION_V2_FORMAT,
    )
    v2_paths = {entry["path"] for entry in v2["files"]}
    assert "fuzz/core_fuzz.cpp" in v2_paths
    assert "cmake/ReviewedProfile.cmake" not in v2_paths
    checks += 1

    v3 = compute_active_projection(
        names,
        read,
        projection_format=ACTIVE_PROJECTION_V3_FORMAT,
    )
    v3_paths = {entry["path"] for entry in v3["files"]}
    assert "fuzz/core_fuzz.cpp" in v3_paths
    assert "cmake/ReviewedProfile.cmake" in v3_paths
    assert "docs/overview.md" not in v3_paths
    checks += 1

    selected = [(path, files[path]) for path in v3_paths]
    assert v3["sha256"] == expected_digest(selected)
    checks += 1

    original_v2 = v2["sha256"]
    original_v3 = v3["sha256"]
    files["cmake/ReviewedProfile.cmake"] = b"profile-tampered\n"
    changed_v2 = compute_active_projection(
        names,
        read,
        projection_format=ACTIVE_PROJECTION_V2_FORMAT,
    )
    changed_v3 = compute_active_projection(
        names,
        read,
        projection_format=ACTIVE_PROJECTION_V3_FORMAT,
    )
    assert changed_v2["sha256"] == original_v2
    assert changed_v3["sha256"] != original_v3
    checks += 1

    assert active_projection_format_allowed_for_revision(
        ACTIVE_PROJECTION_V2_FORMAT,
        904,
    )
    assert not active_projection_format_allowed_for_revision(
        ACTIVE_PROJECTION_V2_FORMAT,
        905,
    )
    checks += 1

    assert active_projection_format_allowed_for_revision(
        ACTIVE_PROJECTION_V3_FORMAT,
        905,
    )
    assert active_projection_format_allowed_for_revision(
        ACTIVE_PROJECTION_V3_FORMAT,
        9999,
    )
    checks += 1

    print(f"active implementation projection policy passed={checks}/7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
