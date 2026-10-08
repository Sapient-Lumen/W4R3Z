#!/usr/bin/env python3
"""Audit the generic exact-thread-incarnation capability boundary.

This deterministic source-shape gate complements the runtime test. It protects
four properties that are easy to lose during refactoring: reusable native
thread identifiers never become authority, fork-copied thread-local bytes are
reseeded through the process incarnation, the allocator cannot inherit a
function-static initialization lock from a vanished thread, and thread-local
state cannot require destructor registration in a post-fork child.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature_fragment: str) -> str:
    start = text.find(signature_fragment)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace : index + 1]
    return ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


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
        "cmake": Path("CMakeLists.txt"),
        "public": Path("src/sync_thread_incarnation.hpp"),
        "implementation": Path("src/sync_thread_incarnation.cpp"),
        "process_public": Path("src/sync_process_incarnation.hpp"),
        "process_implementation": Path("src/sync_process_incarnation.cpp"),
        "sqlite_public": Path("src/sync_sqlite_mutex_capability.hpp"),
        "sqlite_implementation": Path("src/sync_sqlite_mutex_capability.cpp"),
        "directory_authority_public": Path("src/sync_directory_authority.hpp"),
        "directory_authority_implementation": Path("src/sync_directory_authority.cpp"),
        "directory_public": Path("src/persistence/local_jsonl_replay_directory_authority.hpp"),
        "directory_implementation": Path("src/persistence/local_jsonl_replay_directory_authority.cpp"),
        "namespace_public": Path("src/persistence/local_jsonl_replay_namespace.hpp"),
        "namespace_implementation": Path("src/persistence/local_jsonl_replay_namespace.cpp"),
        "budget_public": Path("src/persistence/sqlite_verification_budget.hpp"),
        "budget_implementation": Path("src/persistence/sqlite_verification_budget.cpp"),
        "budget_test": Path("tests/persistence/sqlite_verification_budget_tests.cpp"),
        "runtime_test": Path("tests/thread_incarnation_tests.cpp"),
        "directory_test": Path("tests/persistence/local_jsonl_replay_directory_authority_tests.cpp"),
        "namespace_test": Path("tests/persistence/local_jsonl_replay_namespace_tests.cpp"),
        "verifier": Path("tools/verify_release_package.py"),
    }
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [name for name, rel in required.items() if not (root / rel).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        report = {
            "format": "anonsync-sync-thread-incarnation-audit-v5",
            "passed": False,
            "checks": [asdict(item) for item in checks],
            "violations": [item.check_id for item in checks if not item.passed],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 2

    text = {
        name: (root / rel).read_text(encoding="utf-8", errors="strict")
        for name, rel in required.items()
    }
    cmake = text["cmake"]
    public = text["public"]
    implementation = text["implementation"]
    sqlite_public = text["sqlite_public"]
    sqlite_implementation = text["sqlite_implementation"]
    directory_authority_public = text["directory_authority_public"]
    directory_authority_implementation = text["directory_authority_implementation"]
    directory_public = text["directory_public"]
    directory_implementation = text["directory_implementation"]
    namespace_public = text["namespace_public"]
    namespace_implementation = text["namespace_implementation"]
    budget_public = text["budget_public"]
    budget_implementation = text["budget_implementation"]
    budget_test = text["budget_test"]
    runtime_test = text["runtime_test"]
    directory_test = text["directory_test"]
    namespace_test = text["namespace_test"]
    verifier = text["verifier"]

    require(
        "class SyncThreadIncarnation final" in public
        and "using SyncThreadIncarnation" not in public,
        "public_proof_is_a_distinct_type",
        "thread authority must not collapse back to an integer alias",
    )
    require(
        "affinity proof, not synchronization" in public
        and "object-lifetime violation" in public,
        "affinity_contract_does_not_overclaim_synchronization",
        "the token rejects sequential misuse but cannot legalize concurrent lifetime races",
    )
    require(
        "explicit constexpr SyncThreadIncarnation(std::uint64_t value)" in public
        and public.find("explicit constexpr SyncThreadIncarnation") > public.find("private:"),
        "integer_constructor_is_private",
        "ordinary numeric values must not construct live thread authority",
    )
    require(
        "!std::is_trivially_copyable_v<SyncThreadIncarnation>" in public
        and "!std::is_constructible_v<SyncThreadIncarnation, std::uint64_t>" in public
        and "!std::is_convertible_v<std::uint64_t, SyncThreadIncarnation>" in public,
        "numeric_and_bitwise_construction_is_closed",
        "rows, wire values, integer literals, and std::bit_cast bytes cannot manufacture the proof",
    )
    require(
        "class SyncThreadIncarnationAccess;" in public
        and "class SyncThreadIncarnationAccess final" not in public
        and "from_raw(" not in public,
        "raw_representation_is_not_public",
        "the public header exposes no representation constructor",
    )
    require(
        "class SyncThreadIncarnationAccess final" in implementation
        and "std::uint64_t raw(" in implementation
        and "from_raw(" in implementation,
        "raw_representation_has_one_implementation_owner",
        "only the generic implementation can bridge between opaque proofs and raw internal storage",
    )
    require(
        "sqlite" not in public.lower() and "sqlite" not in implementation.lower(),
        "generic_owner_has_no_sqlite_vocabulary",
        "the exact-thread primitive remains independent of the first consumer that needed it",
    )
    require(
        "std::atomic<std::uint64_t>::is_always_lock_free" in implementation
        and "constinit std::atomic<std::uint64_t> next_thread_incarnation_raw{1U}" in implementation,
        "allocator_is_constant_initialized_and_lock_free",
        "post-fork allocation cannot depend on a copied userspace lock",
    )
    allocator = function_body(implementation, "allocate_thread_incarnation_noexcept() noexcept")
    require(
        bool(allocator)
        and "compare_exchange_weak" in allocator
        and "std::numeric_limits<std::uint64_t>::max()" in allocator
        and "fail_stop_on_sync_thread_capability_violation_noexcept" in allocator
        and "static std::atomic" not in allocator,
        "allocator_is_monotonic_bounded_and_guard_free",
        "one generation is consumed per thread and wraparound or a copied function-static guard cannot resurrect authority",
    )
    tls_match = re.search(
        r"struct ThreadLocalIncarnationRaw final \{(?P<body>.*?)\};",
        implementation,
        re.S,
    )
    tls_body = tls_match.group("body") if tls_match else ""
    require(
        bool(tls_body)
        and "std::uint64_t process_raw" in tls_body
        and "std::uint64_t incarnation_raw" in tls_body
        and "SyncProcessIncarnation" not in tls_body
        and "SyncThreadIncarnation" not in tls_body
        and "std::is_trivially_copyable_v<ThreadLocalIncarnationRaw>" in implementation
        and "std::is_trivially_destructible_v<ThreadLocalIncarnationRaw>" in implementation
        and "constinit thread_local ThreadLocalIncarnationRaw live_thread_incarnation_raw" in implementation,
        "thread_local_state_is_raw_trivial_and_constant_initialized",
        "post-fork lookup cannot require a copied TLS initialization guard or destructor registration",
    )
    current = function_body(implementation, "current_sync_thread_incarnation_noexcept() noexcept")
    require(
        ordered(
            current,
            "current_sync_process_incarnation_noexcept",
            "SyncProcessIncarnationAccess::raw(current_process)",
            "live_thread_incarnation_raw.process_raw != current_process_raw",
            "allocate_thread_incarnation_noexcept",
            "live_thread_incarnation_raw.process_raw = current_process_raw",
            "SyncThreadIncarnationAccess::raw(replacement)",
            "SyncThreadIncarnationAccess::from_raw",
        )
        and "constinit thread_local" not in current,
        "thread_local_state_is_process_incarnation_scoped",
        "fork-copied raw TLS bytes are rejected and replaced before authority is returned",
    )
    require(
        "expected.valid()" in function_body(
            implementation, "sync_thread_incarnation_is_current("
        )
        and "thread-affinity proof is empty" in implementation
        and "must execute on its originating thread" in implementation,
        "empty_and_foreign_proofs_are_distinguished",
        "programming errors throw distinctly from foreign-thread use",
    )
    require(
        "fail_stop_on_sync_process_capability_violation_noexcept();" in function_body(
            implementation,
            "[[noreturn]] void fail_stop_on_sync_thread_capability_violation_noexcept()",
        ),
        "noexcept_violation_reuses_direct_process_exit",
        "destructors and noexcept accessors neither unwind nor run teardown hooks",
    )
    for marker in (
        "std::thread::id",
        "std::this_thread::get_id",
        "hash<std::thread::id>",
        "pthread_self",
        "gettid",
    ):
        require(
            marker not in implementation,
            "implementation_avoids_" + re.sub(r"[^a-z0-9]+", "_", marker.lower()).strip("_"),
            f"reusable or representation-specific {marker} must not become authority",
        )

    generic_target = target_body(cmake, "anonsync_thread_incarnation")
    require(
        bool(generic_target)
        and "set(ANONSYNC_THREAD_INCARNATION_SOURCE" in cmake
        and "src/sync_thread_incarnation.cpp" in cmake
        and "${ANONSYNC_THREAD_INCARNATION_SOURCE}" in generic_target
        and "anonsync_process_incarnation" in generic_target,
        "generic_target_owns_exact_source_and_process_dependency",
        "fork reseeding is linked through the one neutral process-incarnation owner",
    )
    require(
        "anonsync_sqlite" not in generic_target.lower(),
        "generic_target_has_no_sqlite_linkage",
        "filesystem consumers do not inherit a database dependency",
    )
    require(
        "using SyncSqliteThreadIncarnation = SyncThreadIncarnation" in sqlite_public
        and "return current_sync_thread_incarnation_noexcept();" in sqlite_implementation
        and "return sync_thread_incarnation_is_current(expected);" in sqlite_implementation
        and "allocate_thread_incarnation_noexcept" not in sqlite_implementation,
        "sqlite_adapter_delegates_without_parallel_allocator",
        "SQLite preserves compatibility while generic code owns allocation and fork behavior",
    )
    require(
        directory_authority_public.count("SyncThreadIncarnation thread_id_") == 1
        and namespace_public.count("SyncThreadIncarnation thread_id_") == 2
        and budget_public.count("SyncThreadIncarnation thread_id_") == 1
        and "SyncDirectoryAuthority authority_" in directory_public
        and "SyncThreadIncarnation thread_id_" not in directory_public,
        "mutable_callback_and_filesystem_owners_carry_exact_thread_proofs",
        "the shared directory capability, namespace, opened-file, and SQLite callback owners bind mutable state to one exact thread incarnation while the JSONL facade delegates",
    )
    require(
        ordered(
            function_body(
                directory_authority_implementation,
                "SyncDirectoryAuthority::require_current_owner_or_throw(",
            ),
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and "authority_.verify_or_throw(label);" in function_body(
            directory_implementation,
            "LocalJsonlReplayDirectoryAuthority::verify_or_throw(",
        )
        and ordered(
            function_body(namespace_implementation, "LocalJsonlReplayOpenFile::require_current_owner_or_throw("),
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and ordered(
            function_body(namespace_implementation, "LocalJsonlReplayNamespace::require_current_owner_or_throw("),
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and ordered(
            function_body(budget_implementation, "void SqliteVerificationBudget::require_current_execution_or_throw("),
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        ),
        "throwing_owners_reject_process_then_thread_before_state",
        "fork children fail stopped and foreign threads throw before descriptor, lock, or revocation state is touched; the JSONL facade reaches that proof only through the shared capability",
    )
    require(
        directory_authority_implementation.count(
            "require_current_owner_noexcept();"
        ) >= 9
        and namespace_implementation.count("require_current_owner_noexcept();") >= 13
        and budget_implementation.count("require_current_execution_noexcept();") >= 8
        and "fail_stop_on_sync_thread_capability_violation_noexcept"
        in directory_authority_implementation
        and namespace_implementation.count(
            "fail_stop_on_sync_thread_capability_violation_noexcept"
        ) >= 2
        and "fail_stop_on_sync_thread_capability_violation_noexcept"
        in budget_implementation
        and "return authority_.path();" in directory_implementation
        and "return authority_.absolute_path();" in directory_implementation
        and "return authority_.attestation();" in directory_implementation,
        "noexcept_owner_surface_is_fail_stopped",
        "moves, accessors, lock release, and destruction cannot silently cross thread lifetimes; the JSONL facade has no parallel affinity implementation",
    )
    require(
        all(
            token in runtime_test
            for token in (
                "test_stable_current_thread_identity",
                "test_empty_and_foreign_proofs_rejected",
                "test_live_and_recycled_threads_receive_unique_incarnations",
                "test_fork_refreshes_thread_identity",
                "test_noexcept_foreign_thread_violation_fails_stopped",
                "!std::is_trivially_copyable_v<SyncThreadIncarnation>",
            )
        ),
        "generic_runtime_and_type_corpus_is_complete",
        "stability, uniqueness, reuse, fork refresh, fail-stop, and opacity are executable",
    )
    require(
        '#include "inherited_test_process.hpp"' in runtime_test
        and runtime_test.count("spawn_inherited_test_process_or_throw(") == 2
        and "::fork(" not in runtime_test
        and "::waitpid(" not in runtime_test
        and "::kill(" not in runtime_test
        and "::pipe(" not in runtime_test,
        "fork_sensitive_runtime_cases_use_the_shared_process_owner",
        "fork refresh and fail-stop probes share bounded process-group, deadline, exact-reap, and numeric-authority ownership",
    )
    require(
        "test_foreign_thread_rejected_without_revocation" in directory_test
        and "test_foreign_thread_noexcept_access_fails_stopped" in directory_test
        and "test_foreign_thread_rejected_without_consuming_owners" in namespace_test
        and "test_foreign_thread_noexcept_release_fails_stopped" in namespace_test
        and "test_exact_thread_authority" in budget_test
        and "foreign throwing rejection preserves mutable counters" in budget_test
        and "foreign SQLite callback fails stopped before budget state" in budget_test
        and "foreign detach fails stopped before callback replacement" in budget_test
        and "foreign destructor fails stopped before callback replacement" in budget_test,
        "real_consumers_have_throwing_and_noexcept_adversarial_tests",
        "foreign-thread rejection is proved non-consuming and fail-stopped at filesystem and SQLite callback capability surfaces",
    )
    budget_target = target_body(cmake, "anonsync_sqlite_verification_budget")
    require(
        bool(budget_target)
        and "anonsync_thread_incarnation" in budget_target
        and "anonsync_process_incarnation" not in budget_target,
        "sqlite_callback_owner_links_the_generic_thread_leaf",
        "the callback budget receives process reseeding transitively through the exact-thread capability rather than maintaining a parallel affinity primitive",
    )
    require(
        "anonsync_sqlite_verification_budget_test" in cmake
        and "PROPERTIES TIMEOUT 20" in cmake
        and "anonsync_inherited_test_process" in cmake,
        "sqlite_callback_affinity_corpus_is_registered_and_bounded",
        "throwing, callback, detach, and destructor affinity proofs remain finite CTest obligations",
    )
    require(
        "anonsync_thread_incarnation_test" in cmake
        and "tests/thread_incarnation_tests.cpp" in cmake
        and "add_test(NAME anonsync_thread_incarnation_test" in cmake
        and re.search(
            r"set_tests_properties\([^)]*anonsync_thread_incarnation_test[^)]*PROPERTIES TIMEOUT 20\)",
            cmake,
            re.S,
        ) is not None,
        "runtime_test_is_registered_and_bounded",
        "the exact-thread runtime corpus is a finite CTest obligation",
    )
    require(
        "anonsync_sync_thread_incarnation_source_audit" in cmake
        and "audit_sync_thread_incarnation.py" in cmake,
        "structural_audit_is_registered",
        "this architecture gate remains in CTest",
    )
    require(
        all(
            path in verifier
            for path in (
                "src/sync_thread_incarnation.hpp",
                "src/sync_thread_incarnation.cpp",
                "src/sync_directory_authority.hpp",
                "src/sync_directory_authority.cpp",
                "tests/thread_incarnation_tests.cpp",
                "src/persistence/sqlite_verification_budget.hpp",
                "src/persistence/sqlite_verification_budget.cpp",
                "tests/persistence/sqlite_verification_budget_tests.cpp",
                "tools/audit_sqlite_verification_budget.py",
                "tools/audit_sync_thread_incarnation.py",
            )
        ),
        "release_verifier_requires_complete_thread_surface",
        "source, runtime proof, and structural gate cannot be omitted from a sealed handoff",
    )

    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-sync-thread-incarnation-audit-v5",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(item) for item in checks],
        "metrics": {
            "generic_header_lines": len(public.splitlines()),
            "generic_implementation_lines": len(implementation.splitlines()),
            "runtime_test_functions": len(re.findall(r"void test_[a-z0-9_]+\(", runtime_test)),
            "thread_bound_owner_fields": directory_authority_public.count(
                "SyncThreadIncarnation thread_id_"
            )
            + namespace_public.count("SyncThreadIncarnation thread_id_")
            + budget_public.count("SyncThreadIncarnation thread_id_"),
            "directory_facade_direct_thread_fields": directory_public.count(
                "SyncThreadIncarnation thread_id_"
            ),
        },
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
