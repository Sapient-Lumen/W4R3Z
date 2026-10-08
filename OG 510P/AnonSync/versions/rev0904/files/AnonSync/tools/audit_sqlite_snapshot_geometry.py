#!/usr/bin/env python3
"""Fail-closed audit for exact SQLite snapshot file geometry authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/persistence/sqlite_snapshot_geometry.hpp"),
    Path("src/persistence/sqlite_snapshot_geometry.cpp"),
    Path("src/persistence/sqlite_snapshot_seal.hpp"),
    Path("src/persistence/sqlite_snapshot_seal.cpp"),
    Path("tests/persistence/sqlite_snapshot_geometry_tests.cpp"),
    Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp"),
    Path("tests/persistence/sqlite_snapshot_seal_tests.cpp"),
    Path("fuzz/fuzz_sqlite_snapshot_geometry.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-snapshot-geometry-audit-v1",
            "passed": False,
            "violations": [f"missing required file: {item}" for item in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    text = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in REQUIRED
    }
    cmake = text[Path("CMakeLists.txt")]
    geometry_hpp = text[Path("src/persistence/sqlite_snapshot_geometry.hpp")]
    geometry_cpp = text[Path("src/persistence/sqlite_snapshot_geometry.cpp")]
    seal_hpp = text[Path("src/persistence/sqlite_snapshot_seal.hpp")]
    seal_cpp = text[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    pure_test = text[Path("tests/persistence/sqlite_snapshot_geometry_tests.cpp")]
    binding_test = text[Path("tests/persistence/sqlite_snapshot_geometry_binding_test.cpp")]
    seal_test = text[Path("tests/persistence/sqlite_snapshot_seal_tests.cpp")]
    fuzz_target = text[Path("fuzz/fuzz_sqlite_snapshot_geometry.cpp")]
    checks: list[Check] = []

    seal_link = re.search(
        r"target_link_libraries\(anonsync_sqlite_snapshot_seal(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    require(
        checks,
        "add_library(anonsync_sqlite_snapshot_geometry STATIC" in cmake
        and seal_link is not None
        and "anonsync_sqlite_snapshot_geometry" in seal_link.group("body"),
        "geometry_is_independent_production_owner",
        "the pure geometry boundary must remain separately linkable and feed the seal",
    )
    core = re.search(r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S)
    require(
        checks,
        core is not None and "sqlite_snapshot_geometry.cpp" not in core.group("body"),
        "geometry_source_is_not_reabsorbed_by_core",
        "exact file geometry must not become a private monolith helper",
    )
    require(
        checks,
        all(
            marker in cmake
            for marker in (
                "anonsync_sqlite_snapshot_geometry_test",
                "anonsync_sqlite_snapshot_geometry_binding_test",
                "focused persistence boundary must not depend on anonsync_core_lib",
            )
        ),
        "focused_proofs_have_no_core_dependency",
        "pure and filesystem-integrated proofs must remain cheap focused targets",
    )
    require(
        checks,
        "anonsync_sqlite_snapshot_geometry_source_audit" in cmake,
        "geometry_source_audit_is_registered",
        "CTest must enforce this architecture rather than relying on release notes",
    )

    require(
        checks,
        "kMaximumUntrustedSqliteSnapshotBytes" in geometry_hpp
        and "kMaximumUntrustedSqliteSnapshotPages" in geometry_hpp
        and "maximum_bytes" in geometry_hpp
        and "maximum_pages" in geometry_hpp,
        "byte_and_page_authority_have_reviewed_hard_ceilings",
        "callers receive only a tighten-able byte/page policy",
    )
    require(
        checks,
        "may tighten but not widen the reviewed ceiling" in geometry_cpp
        and "policy.maximum_bytes > kMaximumUntrustedSqliteSnapshotBytes" in geometry_cpp
        and "policy.maximum_pages > kMaximumUntrustedSqliteSnapshotPages" in geometry_cpp,
        "caller_policy_cannot_mint_more_authority",
        "both dimensions must reject widening, not merely document defaults",
    )
    require(
        checks,
        "kSqliteMagic" in geometry_cpp
        and "SQLite format 3" not in geometry_cpp
        and "invalid database header magic" in geometry_cpp,
        "sqlite_header_magic_is_byte_exact",
        "the terminating NUL is part of the 16-byte SQLite format signature",
    )
    require(
        checks,
        all(marker in geometry_cpp for marker in ("read_be16(header, 16U)", "65536U", "is_power_of_two")),
        "page_size_encoding_is_exact",
        "the 1=>65536 encoding and power-of-two range are both enforced",
    )
    require(
        checks,
        "read_be32(header, 24U)" in geometry_cpp
        and "read_be32(header, 92U)" in geometry_cpp
        and "header page count is stale" in geometry_cpp,
        "page_count_is_used_only_when_header_validity_matches",
        "a stale in-header size is observation, not extent authority",
    )
    require(
        checks,
        "read_be32(header, 28U)" in geometry_cpp
        and "page_count_value == 0U" in geometry_cpp
        and "exceeds the page ceiling" in geometry_cpp,
        "page_count_is_nonzero_and_bounded",
        "malicious page cardinality cannot bypass the reviewed ceiling",
    )
    require(
        checks,
        "geometry.byte_count != exact_file_bytes" in geometry_cpp
        and "header page count does not match exact file bytes" in geometry_cpp,
        "header_pages_bind_the_entire_descriptor_extent",
        "no ignored prefix, suffix, trailing page, or partial page is authorized",
    )

    source_geometry = seal_cpp.find("out.geometry_ = verify_sqlite_snapshot_geometry_or_throw")
    resident_allocation = seal_cpp.find(
        "SqliteAllocatedBytes captured = copy_source_exact_or_throw(")
    require(
        checks,
        source_geometry >= 0
        and resident_allocation >= 0
        and source_geometry < resident_allocation,
        "geometry_is_proven_before_resident_allocation",
        "malformed bytes must not mint process-resident copy authority",
    )
    require(
        checks,
        "out.serialized_bytes_.reset(captured.release())" in seal_cpp
        and "out.finalize_resident_bytes_or_throw(label + \" captured bytes\")" in seal_cpp
        and "header_from_bytes_or_throw(bytes, label)" in seal_cpp
        and "geometry_ = verify_sqlite_snapshot_geometry_or_throw(" in seal_cpp
        and "sha256_hex_ = sha256_bytes_or_throw(bytes, label)" in seal_cpp,
        "resident_copy_is_reproved_without_path_reopen",
        "the process-owned destination must reproduce both source geometry and digest",
    )
    require(
        checks,
        seal_cpp.count("verify_sqlite_snapshot_geometry_or_throw") >= 3
        and "resident snapshot geometry changed while copying" in seal_cpp
        and "sealed SQLite snapshot geometry changed after capture" in seal_cpp,
        "geometry_is_reproved_at_each_promotion_boundary",
        "source descriptor, resident promotion, and live capability are all checked",
    )
    require(
        checks,
        all(marker in seal_hpp for marker in ("geometry_", "geometry_policy_", "page_size()", "page_count()"))
        and "current_geometry != geometry_" in seal_cpp,
        "seal_retains_and_reasserts_geometry_evidence",
        "later opens consume the captured geometry capability rather than reparsing unchecked bytes",
    )

    require(
        checks,
        all(
            marker in pure_test
            for marker in (
                "trailing page",
                "trailing byte",
                "truncated page",
                "stale page count",
                "widened bytes",
                "widened pages",
            )
        ),
        "pure_adversarial_corpus_covers_geometry_edges",
        "extent, freshness, encoding, and policy monotonicity have executable proofs",
    )
    require(
        checks,
        "ordinary SQLite did not accept the padded database" in binding_test
        and "backup_logical_database" in binding_test
        and "SQLite backup did not discard the authenticated trailing page" in binding_test,
        "exploit_proof_demonstrates_logical_byte_normalization",
        "ordinary SQLite acceptance and backup suffix loss are both permanent evidence",
    )
    require(
        checks,
        "header page count does not match exact file bytes" in binding_test
        and "geometry rejection changed the legacy staging namespace" in binding_test,
        "production_seal_rejects_before_resident_promotion",
        "the exploit is rejected for exact geometry while the former staging namespace remains untouched",
    )
    require(
        checks,
        "LLVMFuzzerTestOneInput" in fuzz_target
        and "anonsync_fuzz_sqlite_snapshot_geometry" in cmake
        and "anonsync_fuzz_sqlite_snapshot_geometry_smoke" in cmake
        and "verify_sqlite_snapshot_geometry_or_throw" in fuzz_target,
        "coverage_guided_geometry_fuzz_boundary_is_real",
        "the header parser is exercised by libFuzzer rather than a fuzz-named corpus binary",
    )

    require(
        checks,
        "maximum_pages = 0" in seal_test
        and "kMaximumUntrustedSqliteSnapshotPages + 1U" in seal_test
        and "sealed page geometry does not bind exact bytes" in seal_test,
        "existing_seal_proof_consumes_page_authority",
        "the mature seal suite exercises the new capability and monotone policy",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-snapshot-geometry-audit-v1",
        "passed": not violations,
        "check_count": len(checks),
        "passed_check_count": len(checks) - len(violations),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
