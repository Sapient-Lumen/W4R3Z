#!/usr/bin/env python3
"""Audit the neutral, typed live-process incarnation boundary.

This source-shape gate complements the fork-adversarial executable. It prevents
SQLite naming or linkage from leaking back into the generic owner, keeps raw
representation access off the public header, and inventories every active use
of the retired SQLite-prefixed API.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
ACTIVE_TOPS = ("include", "src", "tests", "fuzz")


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def source_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for top in ACTIVE_TOPS:
        base = root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
                result.append(path.relative_to(root))
    return result


def target_body(cmake: str, target: str) -> str:
    match = re.search(
        rf"add_library\({re.escape(target)}\s+STATIC.*?"
        rf"target_compile_options\({re.escape(target)}\s+PRIVATE.*?\)",
        cmake,
        re.S,
    )
    return match.group(0) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    required = {
        "public_header": Path("src/sync_process_incarnation.hpp"),
        "internal_header": Path("src/sync_process_incarnation_internal.hpp"),
        "implementation": Path("src/sync_process_incarnation.cpp"),
        "runtime_test": Path("tests/process_incarnation_tests.cpp"),
        "publication": Path("src/sync_atomic_file_publication.cpp"),
        "cmake": Path("CMakeLists.txt"),
    }
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [name for name, rel in required.items() if not (root / rel).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        report = {
            "format": "anonsync-sync-process-incarnation-audit-v3",
            "passed": False,
            "checks": [asdict(item) for item in checks],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 2

    texts = {
        name: (root / rel).read_text(encoding="utf-8")
        for name, rel in required.items()
    }
    public = texts["public_header"]
    internal = texts["internal_header"]
    implementation = texts["implementation"]
    runtime_test = texts["runtime_test"]
    publication = texts["publication"]
    cmake = texts["cmake"]

    retired_paths = (
        Path("src/sync_sqlite_process_incarnation.cpp"),
        Path("src/sync_sqlite_process_incarnation.hpp"),
        Path("src/sync_sqlite_process_incarnation_internal.hpp"),
        Path("tests/sqlite_process_incarnation_tests.cpp"),
    )
    present_retired = [rel.as_posix() for rel in retired_paths if (root / rel).exists()]
    require(
        not present_retired,
        "sqlite_prefixed_implementation_is_retired",
        f"present={present_retired}",
    )

    require(
        "class SyncProcessIncarnation final" in public
        and "using SyncProcessIncarnation" not in public,
        "public_proof_is_a_distinct_type",
        "the process proof must not collapse back to an integer alias",
    )
    require(
        "explicit constexpr SyncProcessIncarnation(std::uint64_t value)" in public
        and public.find("explicit constexpr SyncProcessIncarnation")
        > public.find("private:"),
        "integer_constructor_is_private",
        "raw integer construction must remain outside the public API",
    )
    require(
        "!std::is_constructible_v<SyncProcessIncarnation, std::uint64_t>" in public
        and "!std::is_convertible_v<std::uint64_t, SyncProcessIncarnation>" in public,
        "integer_nonconstruction_is_asserted",
        "compile-time shape guards must reject direct or implicit integer construction",
    )
    require(
        "!std::is_trivially_copyable_v<SyncProcessIncarnation>" in public
        and "constexpr ~SyncProcessIncarnation() noexcept {}" in public
        and "std::bit_cast" in public,
        "well_defined_bitwise_construction_is_closed",
        "the public proof must not be constructible from arbitrary bits with std::bit_cast",
    )
    require(
        "class SyncProcessIncarnationAccess;" in public
        and "class SyncProcessIncarnationAccess final" not in public
        and "from_raw(" not in public
        and "raw(" not in public,
        "raw_representation_is_not_public",
        "the public header may forward-declare but must not define representation access",
    )
    require(
        "class SyncProcessIncarnationAccess final" in internal
        and "from_raw(" in internal
        and "raw(" in internal,
        "raw_representation_has_one_internal_owner",
        "constexpr algebra receives raw access only from the internal header",
    )
    require(
        "sqlite" not in public.lower()
        and "sqlite" not in internal.lower()
        and "sqlite" not in implementation.lower(),
        "generic_owner_has_no_sqlite_vocabulary",
        "the neutral process owner must not encode a database-layer dependency",
    )
    require(
        "std::atomic<std::uint64_t>::is_always_lock_free" in implementation
        and "live_process_incarnation_raw" in implementation
        and "pthread_atfork" in implementation
        and "current_kernel_pid_or_fail_stop" in implementation,
        "fork_refresh_is_lock_free_and_registered",
        "child refresh must retain the reviewed lock-free atfork/PID fallback structure",
    )
    require(
        "std::_Exit(kSyncProcessCapabilityViolationExitCode)" in implementation,
        "capability_violation_is_direct_exit",
        "inherited authority must not unwind or run process teardown hooks",
    )
    require(
        "ordinary" in public.lower() and "fork() descendant" in public,
        "fork_scope_is_not_overclaimed",
        "the public contract must distinguish ordinary fork lineage from unsupported process creation",
    )
    require(
        "pthread_atfork()" in public
        and "POSIX _Fork()" in public
        and "must not re-enter" in public
        and "before exec" in public,
        "atfork_bypass_scope_is_explicit",
        "children created without the registered hook must be excluded from the live-authority contract",
    )
    require(
        "non-serializable" not in public.lower()
        and "not an interchange format" in public.lower(),
        "serialization_claim_is_bounded",
        "typed in-process evidence must not be falsely described as impossible to copy as bytes",
    )

    generic_target = target_body(cmake, "anonsync_process_incarnation")
    require(
        bool(generic_target)
        and "set(ANONSYNC_PROCESS_INCARNATION_SOURCE" in cmake
        and "src/sync_process_incarnation.cpp" in cmake
        and "${ANONSYNC_PROCESS_INCARNATION_SOURCE}" in generic_target
        and "Threads::Threads" in generic_target,
        "generic_target_owns_exact_source_and_threads",
        "one separately linked owner must compile the implementation and pthread registration",
    )
    require(
        "ANONSYNC_SQLITE_TARGET" not in generic_target
        and "anonsync_sqlite" not in generic_target.lower(),
        "generic_target_has_no_sqlite_linkage",
        "the process proof library must not link SQLite or SQLite-specific owners",
    )
    require(
        "anonsync_process_incarnation_test" in cmake
        and "tests/process_incarnation_tests.cpp" in cmake
        and "add_test(NAME anonsync_process_incarnation_test" in cmake,
        "generic_runtime_test_is_registered",
        "the renamed algebra/fork executable must remain a CTest obligation",
    )
    require(
        "anonsync_sync_process_incarnation_source_audit" in cmake
        and "audit_sync_process_incarnation.py" in cmake,
        "structural_audit_is_registered",
        "this architecture gate must remain in CTest",
    )

    require(
        '#include "sync_process_incarnation.hpp"' in publication
        and "sync_sqlite_process_incarnation" not in publication,
        "filesystem_publication_uses_generic_header",
        "the non-SQLite publication owner must consume only the neutral process proof",
    )
    publication_link = re.search(
        r"target_link_libraries\(anonsync_sync_atomic_file_publication(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    require(
        publication_link is not None
        and "anonsync_process_incarnation" in publication_link.group("body")
        and "anonsync_sqlite_process_incarnation" not in publication_link.group("body"),
        "filesystem_publication_links_generic_owner",
        "the CMake graph must not route filesystem authority through a SQLite-named target",
    )

    active = source_files(root)
    old_pattern = re.compile(
        r"sync_sqlite_process_incarnation|SyncSqliteProcessId|"
        r"current_sync_sqlite_process_id|sync_sqlite_process_id_is_current|"
        r"kSyncSqliteCapabilityViolationExitCode|"
        r"fail_stop_on_sync_sqlite_capability_violation"
    )
    retired_hits: list[dict[str, object]] = []
    internal_include_hits: list[str] = []
    for rel in active:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        if old_pattern.search(text):
            retired_hits.append({"path": rel.as_posix(), "matches": sorted(set(old_pattern.findall(text)))})
        if 'sync_process_incarnation_internal.hpp' in text:
            internal_include_hits.append(rel.as_posix())
    require(
        not retired_hits,
        "active_source_has_no_retired_api",
        f"hits={retired_hits}",
    )
    expected_internal = [
        "src/sync_process_incarnation.cpp",
        "src/sync_sqlite_handle_slot.hpp",
        "src/sync_thread_incarnation.cpp",
        "tests/process_incarnation_tests.cpp",
    ]
    require(
        sorted(internal_include_hits) == expected_internal,
        "internal_representation_access_is_inventory_bounded",
        f"observed={sorted(internal_include_hits)} expected={expected_internal}",
    )

    require(
        "!std::is_constructible_v<SyncProcessIncarnation, std::uint64_t>" in runtime_test
        and "!std::is_trivially_copyable_v<SyncProcessIncarnation>" in runtime_test
        and "bit-casts cannot manufacture" in runtime_test
        and "test_empty_process_proof_rejected" in runtime_test
        and "test_direct_fork" in runtime_test
        and "test_unobserved_intermediate_fork" in runtime_test
        and "test_inherited_token_fail_stop" in runtime_test,
        "runtime_test_covers_type_and_fork_contract",
        "the executable must prove both public type separation and fork-lineage behavior",
    )
    require(
        "kSyncProcessMaximumLineageGeneration" in runtime_test
        and "lineage exhaustion fails closed" in runtime_test
        and "recycled ancestor PID" in runtime_test,
        "runtime_test_covers_wrap_and_pid_reuse",
        "lineage wrap and PID recycling must remain explicit executable cases",
    )

    passed_count = sum(item.passed for item in checks)
    report = {
        "format": "anonsync-sync-process-incarnation-audit-v3",
        "passed": passed_count == len(checks),
        "summary": {"passed": passed_count, "total": len(checks)},
        "checks": [asdict(item) for item in checks],
        "inventories": {
            "active_source_files": len(active),
            "retired_api_hits": retired_hits,
            "internal_header_includes": sorted(internal_include_hits),
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
