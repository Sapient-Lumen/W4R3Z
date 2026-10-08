#!/usr/bin/env python3
"""Fail-closed structural audit for the local JSONL crash protocol."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core_internal.hpp"),
    Path("src/persistence/local_jsonl_replay_publication.hpp"),
    Path("src/persistence/local_jsonl_replay_publication.cpp"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/persistence/local_jsonl_replay_directory_authority.hpp"),
    Path("src/persistence/local_jsonl_replay_directory_authority.cpp"),
    Path("src/persistence/local_jsonl_replay_namespace.hpp"),
    Path("src/persistence/local_jsonl_replay_namespace.cpp"),
    Path("src/sync_thread_incarnation.hpp"),
    Path("src/sync_thread_incarnation.cpp"),
    Path("src/replay_ledger.cpp"),
    Path("src/reporting.cpp"),
    Path("src/reporting_selftests.cpp"),
    Path("src/runner.cpp"),
    Path("tests/persistence/local_jsonl_replay_publication_tests.cpp"),
    Path("tests/persistence/local_jsonl_replay_directory_authority_tests.cpp"),
    Path("tests/persistence/local_jsonl_replay_namespace_tests.cpp"),
    Path("tests/thread_incarnation_tests.cpp"),
    Path("tests/local_jsonl_replay_backend_namespace_test.cpp"),
    Path("tests/local_jsonl_replay_crash_state_machine_test.cpp"),
    Path("tools/audit_local_jsonl_replay_crash_protocol.py"),
    Path("tools/audit_sync_thread_incarnation.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-local-jsonl-replay-crash-protocol-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


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

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    text = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text[Path("CMakeLists.txt")]
    internal = text[Path("include/anonsync_core_internal.hpp")]
    publication_h = text[Path("src/persistence/local_jsonl_replay_publication.hpp")]
    publication = text[Path("src/persistence/local_jsonl_replay_publication.cpp")]
    generic_directory_h = text[Path("src/sync_directory_authority.hpp")]
    generic_directory_cpp = text[Path("src/sync_directory_authority.cpp")]
    resolution_h = text[Path("src/sync_posix_directory_resolution.hpp")]
    resolution_cpp = text[Path("src/sync_posix_directory_resolution.cpp")]
    directory_component = function_body(
        resolution_cpp, "open_directory_component_with_missing_policy_or_throw("
    )
    directory_open = function_body(
        resolution_cpp, "open_directory_component_with_policy("
    )
    directory_h = text[
        Path("src/persistence/local_jsonl_replay_directory_authority.hpp")
    ]
    directory_cpp = text[
        Path("src/persistence/local_jsonl_replay_directory_authority.cpp")
    ]
    namespace_h = text[Path("src/persistence/local_jsonl_replay_namespace.hpp")]
    namespace_cpp = text[Path("src/persistence/local_jsonl_replay_namespace.cpp")]
    thread_h = text[Path("src/sync_thread_incarnation.hpp")]
    thread_cpp = text[Path("src/sync_thread_incarnation.cpp")]
    replay = text[Path("src/replay_ledger.cpp")]
    reporting = text[Path("src/reporting.cpp")]
    reporting_tests = text[Path("src/reporting_selftests.cpp")]
    runner = text[Path("src/runner.cpp")]
    publication_tests = text[
        Path("tests/persistence/local_jsonl_replay_publication_tests.cpp")
    ]
    directory_tests = text[
        Path("tests/persistence/local_jsonl_replay_directory_authority_tests.cpp")
    ]
    namespace_tests = text[
        Path("tests/persistence/local_jsonl_replay_namespace_tests.cpp")
    ]
    thread_tests = text[Path("tests/thread_incarnation_tests.cpp")]
    backend_tests = text[Path("tests/local_jsonl_replay_backend_namespace_test.cpp")]
    crash_tests = text[Path("tests/local_jsonl_replay_crash_state_machine_test.cpp")]
    verifier = text[Path("tools/verify_release_package.py")]

    core_sources = block_between(
        cmake, "set(ANONSYNC_CORE_SOURCES", "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE"
    )
    core_links = block_between(
        cmake, "target_link_libraries(anonsync_core_lib", "target_compile_options"
    )
    generic_directory_leaf = block_between(
        cmake,
        "set(ANONSYNC_SYNC_DIRECTORY_AUTHORITY_SOURCE",
        "# Report and heartbeat publication is a filesystem authority boundary",
    )
    directory_leaf = block_between(
        cmake,
        "set(ANONSYNC_LOCAL_JSONL_REPLAY_DIRECTORY_AUTHORITY_SOURCE",
        "# The local JSONL ledger is a namespace authority",
    )
    namespace_leaf = block_between(
        cmake,
        "set(ANONSYNC_LOCAL_JSONL_REPLAY_NAMESPACE_SOURCE",
        "# Exact file bytes are still only an observation.",
    )
    focused_guard = block_between(
        cmake,
        "foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )
    sanitizer_targets = block_between(
        cmake,
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
        "foreach(tgt IN LISTS ANONSYNC_SANITIZER_COMPILE_TARGETS)",
    )
    sanitizer_links = block_between(
        cmake,
        "foreach(tgt\n      anonsync_core",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )

    require(
        "add_library(anonsync_sync_directory_authority STATIC"
        in generic_directory_leaf
        and "src/sync_directory_authority.cpp" in generic_directory_leaf
        and "anonsync_sync_posix_directory_resolution" in generic_directory_leaf
        and "anonsync_process_incarnation" in generic_directory_leaf
        and "anonsync_thread_incarnation" in generic_directory_leaf
        and "add_library(anonsync_local_jsonl_replay_directory_authority STATIC"
        in directory_leaf
        and "src/persistence/local_jsonl_replay_directory_authority.cpp"
        in directory_leaf
        and "anonsync_sync_directory_authority" in directory_leaf,
        "directory_authority_is_an_independent_invariant_leaf",
        "one generic path/attestation owner compiles independently and the local JSONL compatibility leaf delegates to it",
    )
    require(
        "add_library(anonsync_local_jsonl_replay_namespace STATIC" in namespace_leaf
        and "src/persistence/local_jsonl_replay_namespace.cpp" in namespace_leaf
        and "anonsync_local_jsonl_replay_directory_authority" in namespace_leaf
        and "anonsync_process_incarnation" in namespace_leaf
        and "anonsync_thread_incarnation" in namespace_leaf
        and "anonsync_sync_bounded_regular_file" in namespace_leaf
        and "anonsync_local_jsonl_replay_publication" in namespace_leaf,
        "namespace_is_an_independent_invariant_leaf",
        "the retained namespace compiles once with only its explicit invariant dependencies",
    )
    require(
        "src/persistence/local_jsonl_replay_namespace.cpp" not in core_sources
        and '${ANONSYNC_LOCAL_JSONL_REPLAY_NAMESPACE_SOURCE}' in cmake
        and "anonsync_local_jsonl_replay_namespace" in core_links,
        "core_links_namespace_privately_without_source_reabsorption",
        "the monolithic core consumes the leaf without compiling its source again",
    )
    require(
        all(
            target in focused_guard
            for target in (
                "anonsync_thread_incarnation",
                "anonsync_thread_incarnation_test",
                "anonsync_local_jsonl_replay_publication",
                "anonsync_local_jsonl_replay_publication_test",
                "anonsync_local_jsonl_replay_directory_authority",
                "anonsync_local_jsonl_replay_directory_authority_test",
                "anonsync_local_jsonl_replay_namespace",
                "anonsync_local_jsonl_replay_namespace_test",
            )
        ),
        "focused_leaf_targets_are_guarded_from_core_reentry",
        "publication and namespace leaf proofs cannot silently acquire anonsync_core_lib",
    )
    require(
        all(
            target in sanitizer_targets
            for target in (
                "anonsync_thread_incarnation_test",
                "anonsync_local_jsonl_replay_publication_test",
                "anonsync_local_jsonl_replay_directory_authority_test",
                "anonsync_local_jsonl_replay_namespace_test",
                "anonsync_local_jsonl_replay_backend_namespace_test",
                "anonsync_local_jsonl_replay_crash_state_machine_test",
            )
        )
        and all(
            target in sanitizer_links
            for target in (
                "anonsync_thread_incarnation_test",
                "anonsync_local_jsonl_replay_publication_test",
                "anonsync_local_jsonl_replay_directory_authority_test",
                "anonsync_local_jsonl_replay_namespace_test",
                "anonsync_local_jsonl_replay_backend_namespace_test",
                "anonsync_local_jsonl_replay_crash_state_machine_test",
            )
        ),
        "focused_protocol_tests_participate_in_sanitizer_lanes",
        "all four direct or integration proofs receive sanitizer compile and link flags",
    )
    require(
        all(
            f"add_test(NAME {name}" in cmake
            for name in (
                "anonsync_thread_incarnation_test",
                "anonsync_local_jsonl_replay_publication_test",
                "anonsync_local_jsonl_replay_directory_authority_test",
                "anonsync_local_jsonl_replay_namespace_test",
                "anonsync_local_jsonl_replay_backend_namespace_test",
                "anonsync_local_jsonl_replay_crash_state_machine_test",
            )
        ),
        "all_protocol_proofs_are_registered",
        "publication, namespace, backend authority, and crash frontier are CTest gates",
    )
    require(
        "anonsync_local_jsonl_replay_crash_protocol_source_audit" in cmake
        and "audit_local_jsonl_replay_crash_protocol.py" in cmake
        and "anonsync_sync_thread_incarnation_source_audit" in cmake
        and "audit_sync_thread_incarnation.py" in cmake,
        "this_audit_is_a_registered_release_gate",
        "the structural contract executes in the normal CTest registry",
    )

    require(
        "LocalJsonlReplayDirectoryAuthority(" in directory_h
        and "const LocalJsonlReplayDirectoryAuthority&) = delete" in directory_h
        and "SyncDirectoryAuthority authority_" in directory_h
        and "const SyncDirectoryAuthority&) = delete" in generic_directory_h
        and "SyncProcessIncarnation process_id_" in generic_directory_h
        and "SyncThreadIncarnation thread_id_" in generic_directory_h
        and "LocalJsonlReplayOpenFile(const LocalJsonlReplayOpenFile&) = delete" in namespace_h
        and "LocalJsonlReplayNamespace(const LocalJsonlReplayNamespace&) = delete"
        in namespace_h
        and namespace_h.count("SyncProcessIncarnation process_id_") == 2
        and namespace_h.count("SyncThreadIncarnation thread_id_") == 2,
        "file_and_namespace_authorities_are_move_only_process_and_thread_bound",
        "copying cannot duplicate descriptor or flock authority, and each mutable owner is affine to its minting process and thread incarnation",
    )
    directory_owner_throw = block_between(
        generic_directory_cpp,
        "void SyncDirectoryAuthority::require_current_owner_or_throw(",
        "void SyncDirectoryAuthority::transfer_from_noexcept(",
    )
    directory_verify = block_between(
        generic_directory_cpp,
        "void SyncDirectoryAuthority::verify_or_throw(",
        "int SyncDirectoryAuthority::descriptor_no_verify()",
    )
    open_file_owner_throw = block_between(
        namespace_cpp,
        "void LocalJsonlReplayOpenFile::require_current_owner_or_throw(",
        "void LocalJsonlReplayOpenFile::transfer_from_noexcept(",
    )
    namespace_owner_throw = block_between(
        namespace_cpp,
        "void LocalJsonlReplayNamespace::require_current_owner_or_throw(",
        "void LocalJsonlReplayNamespace::transfer_from_noexcept(",
    )
    require(
        "class SyncThreadIncarnation final" in thread_h
        and "std::atomic<std::uint64_t>::is_always_lock_free" in thread_cpp
        and ordered(
            directory_owner_throw,
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and ordered(
            open_file_owner_throw,
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and ordered(
            namespace_owner_throw,
            "require_sync_process_incarnation_or_fail_stop",
            "require_sync_thread_incarnation_or_throw",
        )
        and ordered(
            directory_verify,
            "require_current_owner_or_throw(label)",
            "if (revoked_)",
            "::fstat(descriptor_",
        ),
        "owner_checks_precede_mutable_state_and_kernel_resource_use",
        "fork children fail stopped and foreign threads throw before revocation state, descriptors, or locks are observed or mutated",
    )
    require(
        generic_directory_cpp.count("require_current_owner_noexcept();") >= 7
        and namespace_cpp.count("require_current_owner_noexcept();") >= 13
        and "fail_stop_on_sync_process_capability_violation_noexcept" in generic_directory_cpp
        and "fail_stop_on_sync_thread_capability_violation_noexcept" in generic_directory_cpp
        and "fail_stop_on_sync_process_capability_violation_noexcept" in namespace_cpp
        and namespace_cpp.count("fail_stop_on_sync_thread_capability_violation_noexcept") >= 2,
        "noexcept_owner_surfaces_fail_stop_before_resource_use",
        "destruction, movement, accessors, lock release, and descriptor access cannot silently cross process or thread lifetime boundaries",
    )
    require(
        all(
            token in thread_tests
            for token in (
                "test_live_and_recycled_threads_receive_unique_incarnations",
                "test_fork_refreshes_thread_identity",
                "test_noexcept_foreign_thread_violation_fails_stopped",
            )
        )
        and "test_foreign_thread_rejected_without_revocation" in directory_tests
        and "test_foreign_thread_noexcept_access_fails_stopped" in directory_tests
        and "test_foreign_thread_rejected_without_consuming_owners" in namespace_tests
        and "test_foreign_thread_noexcept_release_fails_stopped" in namespace_tests,
        "thread_affinity_has_generic_and_real_owner_adversarial_proof",
        "uniqueness, fork refresh, non-consuming throwing rejection, and real noexcept fail-stop paths are executable",
    )
    require(
        "SyncDirectoryAttestation attestation_" in generic_directory_h
        and "int descriptor_ = -1" in generic_directory_h
        and "SyncDirectoryAuthority authority_" in directory_h
        and "LocalJsonlReplayDirectoryAuthority directory_authority_" in namespace_h
        and "int parent_descriptor_" not in namespace_h
        and all(
            needle in generic_directory_cpp
            for needle in (
                "traverse_directory_or_throw",
                "::fstat(descriptor_",
                "path no longer names the retained directory",
                "same_attestation(attestation_, retained)",
            )
        ),
        "parent_directory_identity_is_retained_and_reproved",
        "later mutations are bound to one directory inode rather than a reusable pathname",
    )
    require(
        ordered(
            generic_directory_cpp,
            "sync_posix_open_filesystem_root_directory_or_throw",
            "sync_posix_open_directory_component_or_throw",
            "SyncPosixDirectoryComponentRole::AbsoluteParent",
            "SyncPosixDirectoryMountPolicy::AllowMountCrossing",
        )
        and ordered(
            directory_component,
            "::fstatat(parent_descriptor, component.c_str(),",
            "AT_SYMLINK_NOFOLLOW",
            "S_ISLNK(before.st_mode)",
            "S_ISDIR(before.st_mode)",
            "open_directory_component_with_policy",
            "::fstat(owned.get(), &after)",
            "same_identity(before, after)",
        )
        and ordered(
            directory_open,
            "return open_component_with_policy_and_flags",
            "directory_open_flags()",
        )
        and "SyncPosixOpenedDirectory" in resolution_h,
        "absolute_parent_is_traversed_component_by_component",
        "the generic owner delegates each component to one shared no-follow inspect/open/identity resolver",
    )
    require(
        all(
            field in generic_directory_h
            for field in (
                "owner_user_id",
                "owner_group_id",
                "effective_user_id",
                "effective_group_id",
                "permission_mode",
                "filesystem_id",
                "mount_flags",
                "filesystem_name_maximum",
                "path_name_maximum",
            )
        )
        and "::fstatvfs(descriptor, &filesystem)" in generic_directory_cpp
        and "::fpathconf(descriptor, _PC_NAME_MAX)" in generic_directory_cpp,
        "parent_directory_attestation_freezes_identity_credentials_mode_and_mount_observations",
        "the runtime contract is one owned value rather than prose around a descriptor",
    )
    require(
        all(
            token in generic_directory_cpp
            for token in (
                "owner_user_id != attestation.effective_user_id",
                "S_IRUSR | S_IWUSR | S_IXUSR",
                "S_IWGRP | S_IWOTH",
                "refuses a group/other-writable directory",
            )
        ),
        "parent_directory_policy_requires_owner_controlled_mutation_surface",
        "the selected directory is owned by the effective UID, owner accessible, and not writable by group or other",
    )
    require(
        "mutable bool revoked_ = false" in generic_directory_h
        and ordered(
            generic_directory_cpp,
            "if (revoked_)",
            "try {",
            "} catch (...) {",
            "revoked_ = true",
        )
        and "restoring visible mode cannot resurrect authority" in directory_tests
        and "path rebinding permanently revokes" in directory_tests
        and generic_directory_cpp.count("parent traversal component") >= 1
        and namespace_cpp.count("parent traversal component") >= 1
        and "lexical parent traversal" in directory_tests
        and "parent traversal ambiguity" in namespace_tests,
        "failed_directory_reproof_is_sticky_revocation",
        "an observed breach cannot be hidden by restoring mode or path before a retry",
    )
    require(
        "O_NOFOLLOW" in resolution_cpp
        and "O_CLOEXEC" in resolution_cpp
        and "O_DIRECTORY" in resolution_cpp
        and "O_NONBLOCK" in namespace_cpp,
        "descriptor_open_flags_reject_link_and_special_file_surprises",
        "directory and regular-file opens carry the available no-follow, close-on-exec, and nonblocking protections",
    )
    require(
        namespace_cpp.count("!S_ISREG") >= 2
        and namespace_cpp.count("st_nlink != 1") >= 2
        and "S_ISLNK" in namespace_cpp
        and "LocalJsonlReplayJournalPublicationState::linked_pair" in namespace_cpp
        and "journal_after.status.st_nlink != 2" in namespace_cpp
        and "same_identity(journal_after.status, staging_after.status)" in namespace_cpp,
        "all_named_members_require_exact_regular_file_topology",
        "members are single-link regular files except the one explicit two-name journal publication state",
    )
    require(
        ordered(
            namespace_cpp,
            "::flock(descriptor.get(), LOCK_EX | LOCK_NB)",
            "verify_descriptor_bound_or_throw(lock_basename_",
            "lock_descriptor_ = descriptor.release()",
        )
        and "retained lock" in namespace_cpp,
        "flock_authority_remains_bound_to_the_named_lock_inode",
        "unlink/recreate of the lock pathname cannot create a second silent writer",
    )
    require(
        "FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw"
        in namespace_cpp
        and "SyncPosixDescriptorLinkPolicy::exactly_one" in namespace_cpp
        and ordered(
            namespace_cpp,
            "freeze_borrowed_descriptor_or_throw",
            "verify_descriptor_bound_or_throw(basename",
        ),
        "member_reads_use_the_bounded_descriptor_snapshot_owner",
        "reads preserve offsets, prove EOF and metadata stability, and rebind the descriptor to its final name",
    )
    require(
        "journal_staging_basename_ =" in namespace_cpp
        and 'out.ledger_basename_ + ".journal.stage"' in namespace_cpp
        and "create_journal_staging_exclusive_or_throw" in namespace_cpp,
        "journal_staging_uses_one_reserved_fixed_member",
        "partial journal bytes cannot appear under the authoritative final journal name",
    )
    require(
        ordered(
            namespace_cpp,
            "publish_open_journal_staging_to_journal_or_throw",
            "verify_descriptor_bound_or_throw(",
            "journal_exists_or_throw(label + \" destination precheck\")",
            "linkat_nointr(directory_authority_.descriptor_no_verify()",
            "LocalJsonlReplayJournalPublicationState::linked_pair",
            "require_descriptor_matches_name_or_throw(",
            "unlinkat_nointr(directory_authority_.descriptor_no_verify()",
            "verify_descriptor_bound_or_throw(journal_basename_",
            "staging name survived publication",
        )
        and "RENAME_NOREPLACE" not in namespace_cpp,
        "journal_stage_link_publication_is_no_replace_and_descriptor_bound",
        "the complete fsynced inode is linked without overwrite, identity checked, and reduced to one final name",
    )
    require(
        namespace_cpp.count("::openat(") >= 4
        and "::linkat(" in namespace_cpp
        and "::renameat(" in namespace_cpp
        and "::unlinkat(" in namespace_cpp
        and "linkat_nointr" in namespace_cpp
        and "renameat_nointr" in namespace_cpp
        and "unlinkat_nointr" in namespace_cpp
        and namespace_cpp.count("errno == EINTR") >= 4
        and "::fsync(directory_authority_.descriptor_no_verify())"
        in namespace_cpp,
        "member_mutation_is_descriptor_relative_and_directory_durable",
        "open, no-replace link, rename, unlink, and directory sync operate through the retained parent descriptor with EINTR retry",
    )
    require(
        all(
            needle in namespace_cpp
            for needle in (
                "std::from_chars",
                "text.size() > 1 && text.front() == '0'",
                "suffix.find('.', separator + 1)",
                "kLocalJsonlReplayMaximumEntryCount) + 1U",
                "kLocalJsonlReplayMaximumTemporaryNameBytes",
            )
        ),
        "temporary_names_have_exact_canonical_ownership_grammar",
        "recovery may retire only basename.tmp.<positive-pid>.<bounded-sequence> minted spellings",
    )
    require(
        "std::numeric_limits<ssize_t>::max()" in namespace_cpp
        and "if (errno == EINTR) continue" in namespace_cpp
        and "write made no progress" in namespace_cpp,
        "descriptor_writes_are_bounded_and_progress_checked",
        "oversized write requests, EINTR, and zero-progress writes are handled explicitly",
    )

    require(
        "kLocalJsonlReplayJournalV3Format" in publication_h
        and "LocalJsonlReplayJournalVersion::crash_complete_v3" in publication
        and "freeze_v2_or_throw" in publication
        and "freeze_v3_or_throw" in publication,
        "journal_owner_mints_v3_and_retains_exact_v2_compatibility",
        "version selection is typed rather than inferred during emission",
    )
    require(
        all(
            token in publication_h
            for token in (
                "create-journal-stage",
                "fsync-journal-stage",
                "link-journal-stage-to-journal",
                "unlink-journal-stage",
                "create-temp",
                "fsync-temp",
                "rename-temp-to-ledger",
                "unlink-journal",
            )
        )
        and publication_h.count("fsync-directory") == 3,
        "v3_wire_protocol_names_all_three_directory_barriers",
        "journal publication, ledger replacement, and journal retirement each expose their durability edge",
    )
    require(
        "previous_payload_sha256" in publication_h
        and "temporary_name" in publication_h
        and "previous_payload_sha256" in publication
        and "temporary_name" in publication,
        "v3_witness_binds_previous_payload_and_exact_temporary_name",
        "startup can distinguish safe rollback from committed replacement without guessing paths",
    )
    require(
        "expected_journal_v3" in publication_tests
        and "journal JSON is not the exact v3 crash-complete publication"
        in publication_tests
        and "v2 journal accepted v3-only fields" in publication_tests
        and "v3 journal accepted missing v3-only fields" in publication_tests,
        "versioned_publication_has_exact_positive_and_negative_corpus",
        "wire bytes and field-set separation are directly executable",
    )

    journal_writer = block_between(
        replay, "bool ReplayLedger::write_journal_record(", "void ReplayLedger::recover_or_reject_journal()"
    )
    commit = block_between(
        replay, "bool ReplayLedger::durable_replace_lines(", "void ReplayLedger::load("
    )
    recovery = block_between(
        replay, "void ReplayLedger::recover_or_reject_journal()", "bool ReplayLedger::durable_replace_lines("
    )
    require(
        ordered(
            journal_writer,
            "freeze_v3_or_throw",
            "create_journal_staging_exclusive_or_throw",
            "write_all_or_throw",
            "fsync_or_throw",
            'maybe_inject_crash(\n            "after-journal-stage-fsync-before-publication")',
            "publish_open_journal_staging_to_journal_or_throw",
            "close_or_throw",
        ),
        "journal_publication_is_atomic_after_complete_file_fsync",
        "arbitrary crashes during journal write leave only rollback staging residue",
    )
    require(
        ordered(
            commit,
            "read_ledger_or_empty_or_throw",
            "sha256_hex(observed_durable_payload) != durable_payload_sha256",
            "changed since load before commit witness publication",
            "create_temporary_exclusive_or_throw",
            'maybe_inject_crash("after-temp-create-before-write")',
            "write_all_or_throw",
            "fsync_or_throw",
            'maybe_inject_crash("after-temp-fsync")',
            "write_journal_record(",
            'maybe_inject_crash(\n            "after-journal-fsync-before-directory-fsync")',
            'sync_directory("after journal publication")',
            "rename_open_temporary_over_ledger_or_throw",
            'sync_directory("after ledger rename")',
            "unlink_journal_if_present_or_throw",
            'sync_directory("after journal retirement")',
        ),
        "commit_rechecks_loaded_state_then_orders_data_witness_and_retirement",
        "uncooperative precommit rewrites are rejected before side effects, complete temporary bytes precede witness publication, and no replacement mutation precedes the durable witness",
    )
    require(
        ordered(
            recovery,
            "journal_publication_state_or_throw",
            "LocalJsonlReplayJournalPublicationState::linked_pair",
            "complete_linked_journal_publication_or_throw",
            'sync_directory("after linked journal publication recovery")',
            "LocalJsonlReplayJournalPublicationState::staging_only",
            "Preserve it rather than converting a",
            "journal_rolled_back_before_commit",
            "read_journal_or_throw",
        ),
        "linked_publication_is_completed_and_staging_only_is_unparsed_preservation",
        "the exact two-link crash state becomes one final witness, while an unbound staging inode is preserved rather than treated as unlink authority",
    )
    require(
        "payload_digest == journal_fields.payload_sha256" in recovery
        and "payload_digest == journal_fields.previous_payload_sha256" in recovery
        and "previous_line_count != summary.line_count" in recovery
        and "previous_head != summary.head" in recovery,
        "recovery_classifies_only_digest_bound_previous_or_next_states",
        "rollback and roll-forward decisions are tied to complete canonical ledger evidence",
    )
    require(
        ordered(
            recovery,
            "read_temporary_if_present_or_throw",
            "sha256_hex(*temporary)",
            "validate_ledger_payload_or_throw(*temporary)",
            "unlink_temporary_if_present_or_throw",
        )
        and recovery.count("retire_v3_temporary_if_present();") == 2
        and "require_complete_replacement" not in recovery,
        "every_journal_bound_temporary_requires_exact_bytes_before_unlink",
        "temp-before-journal ordering makes complete digest and canonical-chain proof mandatory on both sides of rename",
    )
    require(
        "LocalJsonlReplayJournalVersion::legacy_v2" in recovery
        and "legacy v2 journal does not match the committed ledger payload" in recovery
        and "previous_state" in recovery,
        "legacy_v2_is_read_only_postcommit_compatibility",
        "only v3 carries sufficient previous-state evidence for authenticated rollback",
    )
    forbidden_replay_calls = [
        token
        for token in (
            "std::ofstream",
            "std::ifstream",
            "::open(",
            "::openat(",
            "::rename(",
            "::renameat(",
            "::unlink(",
            "::unlinkat(",
            "::flock(",
        )
        if token in replay
    ]
    require(
        not forbidden_replay_calls,
        "replay_domain_no_longer_performs_raw_namespace_syscalls",
        f"forbidden_sites={forbidden_replay_calls}",
    )

    metric_files = (internal, replay, runner, reporting, reporting_tests)
    require(
        all("journal_rolled_back_before_commit" in value for value in metric_files)
        and "ledger_journal_rolled_back_before_commit" in internal
        and "ledger_journal_rolled_back_before_commit" in reporting,
        "rollback_classification_flows_through_stats_and_report",
        "operators can distinguish clean precommit recovery from corruption rejection and postcommit recovery",
    )
    require(
        all(
            f'"{field}"' in runner
            for field in (
                "journal_v3_mint",
                "journal_v2_recovery_compatibility",
                "journal_precommit_rollback",
                "journal_directory_durability",
                "retained_directory_descriptor_namespace",
                "owner_controlled_parent_directory_required",
                "parent_directory_attestation_reproved_before_namespace_io",
                "group_or_other_writable_parent_rejected",
                "parent_traversal_components_rejected",
                "failed_parent_directory_reproof_permanently_revokes_authority",
                "failed_namespace_reproof_permanently_revokes_authority",
                "parent_directory_mount_observations_frozen",
                "parent_directory_process_exclusivity_not_claimed",
                "reject_symlink_sidecars",
            )
        )
        and "journal_v2_only" not in runner,
        "capability_manifest_states_the_actual_local_jsonl_contract",
        "runtime selection no longer advertises the retired v2-only protocol",
    )

    crash_injection_selftest = block_between(
        reporting_tests,
        "int run_ledger_crash_injection_selftest()",
        "int run_ledger_batch_transaction_selftest()",
    )
    backend_interface_selftest = block_between(
        reporting_tests,
        "int run_ledger_backend_interface_selftest()",
        "int run_ledger_effect_idempotency_selftest()",
    )
    require(
        all(
            "SelftestPrivateDirectory workspace" in selftest
            and 'const std::string dir = "/tmp"' not in selftest
            and 'return dir + "/"' not in selftest
            for selftest in (crash_injection_selftest, backend_interface_selftest)
        ),
        "legacy_local_jsonl_selftests_use_private_parent_capabilities",
        "crash injection and backend interface fixtures cannot bypass the owner-controlled parent policy through shared /tmp",
    )

    require(
        all(
            token in directory_tests
            for token in (
                "test_frozen_attestation_and_move",
                "test_initial_permission_policy",
                "test_attestation_change_is_sticky_revocation",
                "test_path_topology_reproof",
                "test_fork_inheritance_fail_stops",
                "group-writable parent",
                "symbolic-link parent component",
            )
        ),
        "directory_authority_has_direct_adversarial_proof",
        "typed tests cover ownership policy, sticky revocation, topology, movement, and fork inheritance",
    )

    require(
        all(
            token in namespace_tests
            for token in (
                "test_parent_rebinding_rejected",
                "test_fork_child_cannot_unlock_parent",
                "create_journal_staging_exclusive_or_throw",
                "test_journal_publication_reuses_reserved_names",
                "test_journal_linked_pair_topology_is_exact",
                "hard-link",
                "symbolic-link",
            )
        ),
        "namespace_adversarial_corpus_covers_identity_topology_and_fork",
        "direct leaf tests exercise the authority properties lexical audits cannot prove",
    )
    require(
        all(
            token in backend_tests
            for token in (
                "cwd",
                "parent rebinding",
                "spawn_inherited_test_process_or_throw",
                "inherited destructor misuse",
                "test_backend_rejects_stale_durable_payload_before_witness",
                "changed since load",
                "directory_fsync_attempts == 3",
            )
        ),
        "backend_integration_corpus_preserves_namespace_authority",
        "the core adapter cannot regress to cwd-relative or pathname-only behavior",
    )
    require(
        "mutable bool revoked_ = false" in namespace_h
        and "namespace authority is revoked" in namespace_cpp
        and "revoked_ = true" in namespace_cpp
        and "test_restored_lock_name_cannot_resurrect_owner" in namespace_tests
        and "restoring the exact locked inode cannot resurrect" in namespace_tests
        and "parent-directory-process-exclusivity-overclaim" in reporting_tests,
        "failed_namespace_reproof_is_sticky_revocation",
        "a transient retained-lock or directory proof failure cannot be hidden by restoring names before retry",
    )
    require(
        all(
            token in crash_tests
            for token in (
                "after-journal-stage-fsync-before-publication",
                "{partial-journal",
                "remained operator evidence",
                "test_linked_journal_publication_completion",
                "create_hard_link(staging_path, journal_path)",
                "after-temp-create-before-write",
                "test_prejournal_temporary_frontiers",
                "after-rename-before-dir-fsync",
                "after-journal-unlink-before-directory-fsync",
                "forged temporary name",
                "test_precommit_rebound_temporary_bytes_are_preserved",
                "temporary payload digest",
            )
        ),
        "crash_corpus_spans_partial_precommit_postcommit_and_retirement_frontiers",
        "the executable state machine includes unbound partial bytes, authenticated rollback, and hostile recovery metadata without unrelated deletion",
    )
    verifier_required = (
        "src/persistence/local_jsonl_replay_publication.hpp",
        "src/persistence/local_jsonl_replay_publication.cpp",
        "src/persistence/local_jsonl_replay_directory_authority.hpp",
        "src/persistence/local_jsonl_replay_directory_authority.cpp",
        "src/persistence/local_jsonl_replay_namespace.hpp",
        "src/persistence/local_jsonl_replay_namespace.cpp",
        "src/sync_thread_incarnation.hpp",
        "src/sync_thread_incarnation.cpp",
        "tests/thread_incarnation_tests.cpp",
        "tests/persistence/local_jsonl_replay_publication_tests.cpp",
        "tests/persistence/local_jsonl_replay_directory_authority_tests.cpp",
        "tests/persistence/local_jsonl_replay_namespace_tests.cpp",
        "tests/local_jsonl_replay_backend_namespace_test.cpp",
        "tests/local_jsonl_replay_crash_state_machine_test.cpp",
        "tools/audit_local_jsonl_replay_crash_protocol.py",
        "tools/audit_sync_thread_incarnation.py",
    )
    require(
        all(path in verifier for path in verifier_required),
        "release_verifier_requires_the_complete_protocol_surface",
        "source, tests, and the structural audit cannot be omitted from a sealed handoff",
    )

    metrics = {
        "thread_incarnation_lines": len(thread_cpp.splitlines()),
        "thread_incarnation_test_functions": len(
            re.findall(r"void test_[a-z0-9_]+\(", thread_tests)
        ),
        "directory_authority_lines": len(generic_directory_cpp.splitlines()),
        "local_directory_wrapper_lines": len(directory_cpp.splitlines()),
        "directory_authority_test_functions": len(
            re.findall(r"void test_[a-z0-9_]+\(", directory_tests)
        ),
        "namespace_openat_calls": namespace_cpp.count("::openat("),
        "namespace_linkat_calls": namespace_cpp.count("::linkat("),
        "namespace_renameat_calls": namespace_cpp.count("::renameat("),
        "namespace_unlinkat_calls": namespace_cpp.count("::unlinkat("),
        "directory_fsync_calls": namespace_cpp.count(
            "::fsync(directory_authority_.descriptor_no_verify())"
        ),
        "crash_checkpoints": len(set(re.findall(r'after-[a-z0-9-]+', replay))),
        "namespace_test_functions": len(re.findall(r"void test_[a-z0-9_]+\(", namespace_tests)),
        "crash_test_functions": len(re.findall(r"void test_[a-z0-9_]+\(", crash_tests)),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
