#!/usr/bin/env python3
"""Audit the invariant-owned report/heartbeat publication boundary."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def source_list_block(cmake: str, variable: str) -> str:
    match = re.search(rf"set\({re.escape(variable)}\s+(.*?)\)", cmake, re.DOTALL)
    return match.group(1) if match else ""


def target_block(cmake: str, command: str, target: str) -> str:
    match = re.search(
        rf"{re.escape(command)}\({re.escape(target)}\s+(.*?)\)",
        cmake,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def ordered(source: str, tokens: list[str]) -> bool:
    cursor = -1
    for token in tokens:
        cursor = source.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def function_body(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        return ""
    opening = source.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    paths = {
        "header": root / "src/sync_atomic_file_publication.hpp",
        "internal_header": root / "src/sync_atomic_file_publication_internal.hpp",
        "state_header": root / "src/sync_atomic_file_publication_state.hpp",
        "state_source": root / "src/sync_atomic_file_publication_state.cpp",
        "source": root / "src/sync_atomic_file_publication.cpp",
        "directory_internal": root / "src/sync_directory_authority_internal.hpp",
        "directory_source": root / "src/sync_directory_authority.cpp",
        "resolution_header": root / "src/sync_posix_directory_resolution.hpp",
        "resolution_source": root / "src/sync_posix_directory_resolution.cpp",
        "resolution_test": root / "tests/sync_posix_directory_resolution_test.cpp",
        "test": root / "tests/sync_atomic_file_publication_test.cpp",
        "prepared_test": root / "tests/sync_atomic_file_publication_prepared_test.cpp",
        "state_test": root / "tests/sync_atomic_file_publication_state_test.cpp",
        "cutpoint_test": root / "tests/sync_atomic_file_publication_cutpoint_test.cpp",
        "reconciliation_test": root / "tests/sync_atomic_file_reconciliation_test.cpp",
        "unlink_test": root / "tests/sync_atomic_file_publication_unlink_authority_test.cpp",
        "audit": root / "tools/audit_sync_atomic_file_publication.py",
        "cmake": root / "CMakeLists.txt",
        "domain": root / "src/sync_domain.cpp",
        "cli": root / "src/sync_operator_cli.cpp",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        result = {
            "audit": "sync_atomic_file_publication",
            "passed": 0,
            "total": 1,
            "checks": [
                {
                    "check_id": "required_files_exist",
                    "passed": False,
                    "detail": f"missing={missing}",
                }
            ],
        }
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        print(rendered, end="")
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered)
        return 1

    text = {name: path.read_text() for name, path in paths.items()}
    header = text["header"]
    internal_header = text["internal_header"]
    state_header = text["state_header"]
    state_source = text["state_source"]
    source = text["source"]
    directory_internal = text["directory_internal"]
    directory_source = text["directory_source"]
    resolution_header = text["resolution_header"]
    resolution_source = text["resolution_source"]
    test = text["test"]
    prepared_test = text["prepared_test"]
    state_test = text["state_test"]
    cutpoint_test = text["cutpoint_test"]
    reconciliation_test = text["reconciliation_test"]
    unlink_test = text["unlink_test"]
    audit_source = text["audit"]
    cmake = text["cmake"]
    domain = text["domain"]
    cli = text["cli"]
    verifier = text["verifier"]
    conditional_removal_impl = function_body(
        source,
        "void remove_sync_file_atomically_if_expected_impl_or_throw(",
    )
    conditional_removal_wrapper = function_body(
        source,
        "void remove_sync_file_atomically_if_expected_under_directory_or_throw(",
    )
    conditional_content_removal_wrapper = function_body(
        source,
        "remove_sync_file_atomically_if_expected_content_under_directory_or_throw(",
    )
    conditional_removal_surface = (
        conditional_removal_impl
        + conditional_removal_wrapper
        + conditional_content_removal_wrapper
    )
    publication_source = source
    for conditional_owner in (
        conditional_removal_impl,
        conditional_removal_wrapper,
        conditional_content_removal_wrapper,
    ):
        if conditional_owner:
            publication_source = publication_source.replace(conditional_owner, "")

    checks: list[dict[str, object]] = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append(
            {"check_id": check_id, "passed": bool(passed), "detail": detail}
        )

    check(
        "required_files_exist",
        not missing,
        "public/internal APIs, state owner, syscall owner, six tests, audit, callers, and verifier are present",
    )

    shared_duplicate = function_body(
        directory_source,
        "SyncDirectoryAuthorityAccess::duplicate_shared_open_description_or_throw(",
    )
    shared_duplicate_cleanup = function_body(
        directory_source,
        "SyncDirectorySharedOpenDescriptionLease::reset_noexcept()",
    )
    check(
        "root_duplicate_bridge_is_centralized_raii_and_names_shared_offsets",
        all(
            token in directory_internal
            for token in (
                "class SyncDirectorySharedOpenDescriptionLease final",
                "file offsets and status flags are shared",
                "not for an independently",
                "fdopendir/readdir observation",
            )
        )
        and ordered(
            shared_duplicate,
            [
                "root authority before descriptor duplication",
                "descriptor_no_verify",
                "F_DUPFD_CLOEXEC",
                "SyncDirectorySharedOpenDescriptionLease lease",
                "root authority after descriptor duplication",
                "return lease",
            ],
        )
        and "::close(descriptor_)" in shared_duplicate_cleanup
        and source.count("duplicate_shared_open_description_or_throw(") == 1
        and "class SyncDirectoryAuthorityAccess final" not in source,
        "atomic publication consumes the sole move-only descriptor bridge and cannot mistake lifetime duplication for an independent observation cursor",
    )

    declarations = [
        "write_sync_json_file_atomically_no_symlink_or_throw(",
        "write_sync_file_atomically_no_symlink_or_throw(",
        "write_sync_cli_report_json_or_throw(",
        "class SyncPreparedImmutableJsonPublication final",
        "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw(",
        "prepare_sync_cli_immutable_json_create_new_or_throw(",
        "write_sync_file_atomically_create_new_no_symlink_or_throw(",
        "enum class SyncImmutableFileReconciliationOutcome",
        "reconcile_sync_immutable_file_create_new_no_symlink_or_throw(",
    ]
    check(
        "header_owns_all_publication_entry_points",
        all(token in header for token in declarations)
        and "namespace anonsync" in header,
        "one focused public header declares replacing, immutable one-shot, and prepared capability publication",
    )

    check(
        "binary_publication_is_span_based_and_observer_compatible",
        "#include <span>" in header
        and "std::span<const unsigned char> payload" in header
        and "write_sync_file_atomically_with_observer_or_throw(" in internal_header
        and "std::span<const unsigned char> payload" in internal_header
        and "write_sync_file_atomically_no_symlink_or_throw(" in source
        and "write_sync_file_atomically_with_observer_or_throw(" in source,
        "sealed binary artifacts reuse the same synchronous span-based public and deterministic-observer owner without an intermediate string copy",
    )

    public_outcome_tokens = [
        "enum class SyncAtomicFilePublicationOutcome",
        "NotPublished",
        "PublishedDurabilityIndeterminate",
        "PublishedAndDirectorySynced",
        "enum class SyncAtomicFilePublicationResidue",
        "TemporaryArtifactMayRemain",
        "sync_atomic_file_publication_residue_name(",
        "class SyncAtomicFilePublicationError : public std::runtime_error",
        "SyncAtomicFilePublicationOutcome outcome() const noexcept",
        "SyncAtomicFilePublicationResidue residue() const noexcept",
    ]
    check(
        "public_failures_are_machine_classified",
        all(token in header for token in public_outcome_tokens),
        "callers can distinguish publication effects and possible temp residue without parsing diagnostic text",
    )

    check(
        "prepared_capability_is_move_only_and_single_use",
        all(token in header for token in [
            "class SyncPreparedImmutableJsonPublication final",
            "SyncPreparedImmutableJsonPublication&&) noexcept;",
            "const SyncPreparedImmutableJsonPublication&) = delete;",
            "void publish_or_throw();",
            "std::unique_ptr<Impl> implementation_",
        ])
        and "std::unique_ptr<SyncPreparedImmutableJsonPublication::Impl> implementation =" in source
        and "std::move(publication.implementation_)" in source
        and "empty or already consumed" in source,
        "destination authority has one move-only owner and is consumed before every attempted publication",
    )

    check(
        "prepared_capability_owns_payload_and_parent_authority",
        "std::string payload" in header
        and "implementation->payload = std::move(payload);" in source
        and "implementation->directory = open_parent_directory_or_throw(" in source
        and "verify_parent_directory_identity_or_throw(" in source
        and "prepared parent directory identity" in source,
        "the plan owns immutable bytes and retains the exact verified POSIX parent descriptor before an intervening durable transition",
    )

    common_writer_publication = function_body(
        source,
        "void publish_posix_from_retained_directory_writer_or_throw(",
    )
    span_publication_adapter = function_body(
        source,
        "void publish_posix_from_retained_directory_or_throw(",
    )
    descriptor_copy = function_body(
        source,
        "void copy_exact_regular_file_to_fd_or_throw(",
    )
    temp_name_body = function_body(source, "std::string next_temp_basename(")

    check(
        "retained_parent_revalidation_precedes_temp_reservation",
        ordered(
            common_writer_publication,
            [
                "retained parent directory before temp reservation",
                "inspect_final_entry_at_or_throw(",
                "create_unique_temp_at_or_throw(",
                "progress.mark_temp_reserved()",
            ],
        ),
        "path-to-parent identity and final-name absence are re-proven before any temp inode is created",
    )

    check(
        "prepared_authority_is_process_incarnation_bound",
        ordered(
            source,
            [
                "PreparedImmutableJsonPublicationObserverAccess::publish_or_throw(",
                "std::move(publication.implementation_)",
                "require_sync_process_incarnation_or_fail_stop(",
                "implementation->owner_process_incarnation",
                "prepared immutable JSON publication destination authority",
                "publish_posix_from_retained_directory_or_throw(",
            ],
        )
        and "kSyncProcessCapabilityViolationExitCode" in prepared_test
        and "implementation->label +" not in source
        and "belongs to a different process incarnation" not in source
        and "anonsync_process_incarnation"
        in target_block(
            cmake, "target_link_libraries", "anonsync_sync_atomic_file_publication"
        ),
        "a fork-inherited destination capability fail-stops before filesystem mutation instead of unwinding through application code",
    )

    prepared_tokens = [
        "preparation creates neither final entry nor temp residue",
        "move transfers authority and empties the source",
        "consumed capability cannot replay stale authority",
        "capability owns bytes independently of caller storage",
        "creator arriving after preparation wins without temp reservation",
        "parent rebind is denied against retained directory authority",
        "replacement parent receives no receipt",
        "displaced pinned parent receives no receipt after denial",
        "rebind denial occurs before any temp reservation",
        "fork child cannot exercise inherited publication authority",
        "original process retains and exercises its exact authority",
    ]
    check(
        "focused_prepared_oracle_covers_rebind_move_reuse_and_fork",
        all(token in prepared_test for token in prepared_tokens)
        and "fs::rename(intended_parent, displaced_parent);" in prepared_test
        and '#include "inherited_test_process.hpp"' in prepared_test
        and prepared_test.count("spawn_inherited_test_process_or_throw(") == 1
        and "wait_for_exit(" in prepared_test
        and "::fork()" not in prepared_test
        and "::waitpid(" not in prepared_test
        and "anonsync_inherited_test_process" in cmake
        and "anonsync_inherited_test_process_source_audit" in cmake,
        "the focused executable proves authority ownership while its sole inherited-capability probe delegates deadline, process-group kill, and reap to the shared audited owner",
    )

    check(
        "typed_exception_can_retain_nested_cause",
        "class SyncAtomicFilePublicationError final" not in header
        and "std::throw_with_nested(SyncAtomicFilePublicationError" in source
        and "std::rethrow_if_nested(error)" in cutpoint_test,
        "the exception is deliberately non-final so throw_with_nested preserves the original failing frontier",
    )

    check(
        "test_observer_is_not_public_runtime_api",
        "AtomicFilePublicationObserver" in internal_header
        and "AtomicFilePublicationCutpoint" in internal_header
        and "class PreparedImmutableJsonPublicationObserverAccess final"
        in internal_header
        and "PreparedImmutableJsonPublicationObserverAccess" in header
        and "*this, nullptr, nullptr" in source
        and "AtomicFilePublicationObserver" not in header
        and "with_observer" not in header,
        "deterministic failure injection is confined to an internal header",
    )

    state_tokens = [
        "mark_temp_reserved() noexcept",
        "mark_namespace_published() noexcept",
        "mark_directory_synced() noexcept",
        "SyncAtomicFilePublicationResidue residue() const noexcept",
        "SyncAtomicFilePublicationOutcome outcome() const noexcept",
    ]
    check(
        "state_owner_is_allocation_free_and_explicit",
        all(token in state_header for token in state_tokens)
        and "std::string" not in state_header
        and "std::vector" not in state_header,
        "effect and residue classification require only noexcept boolean state transitions",
    )

    check(
        "state_model_is_monotone",
        "temp_artifact_may_remain_ = false;" in state_source
        and "if (!namespace_published_) temp_artifact_may_remain_ = true;"
        in state_source
        and "if (namespace_published_) directory_synced_ = true;" in state_source
        and ordered(
            state_source,
            [
                "if (directory_synced_)",
                "PublishedAndDirectorySynced",
                "if (namespace_published_)",
                "PublishedDurabilityIndeterminate",
                "NotPublished",
            ],
        ),
        "publication consumes possible temp residue permanently and directory durability cannot exist before rename",
    )

    core_sources = source_list_block(cmake, "ANONSYNC_CORE_SOURCES")
    invariant_sources_match = re.search(
        r"foreach\(ANONSYNC_INVARIANT_OWNED_SOURCE\s+(.*?)\)\s*\n\s*list\(FIND",
        cmake,
        re.DOTALL,
    )
    invariant_sources = (
        invariant_sources_match.group(1) if invariant_sources_match else ""
    )
    check(
        "implementation_is_outside_the_core_monolith",
        "src/sync_atomic_file_publication.cpp" not in core_sources
        and "src/sync_atomic_file_publication_state.cpp" not in core_sources
        and "${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_SOURCE}" in invariant_sources
        and "${ANONSYNC_SYNC_ATOMIC_FILE_PUBLICATION_STATE_SOURCE}"
        in invariant_sources,
        "the source-ownership guard prevents state or syscall logic from returning to anonsync_core_lib",
    )

    state_links = target_block(
        cmake,
        "target_link_libraries",
        "anonsync_sync_atomic_file_publication_state",
    )
    publication_links = target_block(
        cmake, "target_link_libraries", "anonsync_sync_atomic_file_publication"
    )
    core_links = target_block(cmake, "target_link_libraries", "anonsync_core_lib")
    check(
        "dependency_direction_is_state_to_syscall_owner_to_core",
        "add_library(anonsync_sync_atomic_file_publication_state STATIC" in cmake
        and "add_library(anonsync_sync_atomic_file_publication STATIC" in cmake
        and "anonsync_core_lib" not in state_links
        and "anonsync_core_lib" not in publication_links
        and "anonsync_sync_atomic_file_publication_state" in publication_links
        and "anonsync_sync_atomic_file_publication" in core_links,
        "the pure classifier and syscall owner have no reverse core dependency",
    )

    check(
        "both_production_callers_use_the_focused_header",
        '#include "sync_atomic_file_publication.hpp"' in domain
        and '#include "sync_atomic_file_publication.hpp"' in cli
        and "void write_sync_cli_report_json_or_throw(" not in cli
        and "void write_sync_json_file_atomically_no_symlink_or_throw(" not in domain
        and "void write_sync_cli_report_json_or_throw(" not in domain,
        "heartbeat and operator CLI call the same separately owned implementation",
    )

    check(
        "temp_names_are_unique_per_call_and_not_payload_derived",
        "std::atomic<std::uint64_t> g_publication_nonce" in source
        and "fetch_add(1, std::memory_order_relaxed)" in temp_name_body
        and "current_process_id()" in temp_name_body
        and "fnv1a_64(final_basename)" in temp_name_body
        and "sha256" not in temp_name_body.lower()
        and '".tmp-" + ' not in temp_name_body,
        "temp basename binds destination, process, and monotone call nonce rather than shared payload bytes",
    )

    check(
        "parent_directory_chain_is_component_bound_and_revalidated",
        "for (const fs::path& component_path : parent.relative_path())" in source
        and source.count("sync_posix_open_directory_component_or_throw(") >= 2
        and "SyncPosixDirectoryComponentRole::RootedDescendant" in source
        and "SyncPosixDirectoryMountPolicy::AllowMountCrossing" in source
        and "SyncPosixDirectoryMountPolicy::RequireRetainedRootMount" in source
        and "::fstatat(parent_descriptor, component.c_str()," in resolution_source
        and "AT_SYMLINK_NOFOLLOW" in resolution_source
        and "component must not be a symlink" in resolution_source
        and "::openat(parent_descriptor, component.c_str()," in resolution_source
        and "same_identity(before, after)" in resolution_source
        and "verify_parent_directory_identity_or_throw(" in source
        and "no longer names the retained directory identity" in source
        and source.count("verify_parent_directory_identity_or_throw(") >= 3
        and "ParentDirectoryPostpublicationRevalidated" in source
        and "SyncPosixOpenedDirectory" in resolution_header
        and "O_DIRECTORY" in resolution_source
        and "O_NOFOLLOW" in resolution_source,
        "the shared POSIX resolver inspects and opens every component without link following, while the exact terminal directory is re-proven before rename and after directory sync",
    )

    check(
        "temp_creation_is_exclusive_directory_relative_and_private",
        "::openat(directory_fd, temp_basename.c_str(), flags, 0600)" in source
        and "O_CREAT | O_EXCL" in source
        and "O_NOFOLLOW" in source
        and "error != EEXIST" in source,
        "each writer reserves its own 0600 entry with openat(O_EXCL) and retries only collisions",
    )

    check(
        "final_entry_type_is_interpreted_without_following_links",
        "::fstatat(directory_fd, final_basename.c_str(), &status" in source
        and "AT_SYMLINK_NOFOLLOW" in source
        and "S_ISLNK(status.st_mode)" in source
        and "S_ISREG(status.st_mode)" in source,
        "existing symlinks and non-regular final entries are rejected relative to the pinned directory",
    )

    check(
        "payload_is_fully_written_reproved_and_file_synced_before_publish",
        "write made no progress" in source
        and "error == EINTR" in source
        and "write_fd_all_or_throw(" in span_publication_adapter
        and ordered(
            common_writer_publication,
            [
                'write_payload(temp.get(), label + " temp file")',
                "AtomicFilePublicationCutpoint::PayloadWritten",
                'fsync_fd_or_throw(temp.get(), label + " temp file")',
                "publish_temp_name_or_throw(",
            ],
        )
        and ordered(
            descriptor_copy,
            [
                "source preflight",
                "Sha256DigestBuilder digest",
                "::pread(",
                "write_fd_all_or_throw(",
                "source final proof",
                "digest.finish_hex()",
                "source SHA-256 changed before publication",
                "::fstat(destination_descriptor",
                "destination did not receive the exact source extent",
            ],
        )
        and "descriptor source create-new publishes exact bytes" in test
        and "descriptor source conditional replacement publishes exact bytes" in test
        and "descriptor source publication independently verifies content identity" in test
        and "descriptor source publication rejects a stale source observation" in test,
        "short writes and EINTR are handled; descriptor sources are re-attested, re-hashed, and exact-extent checked before the temp inode is synced and renamed",
    )

    check(
        "temp_path_ownership_is_inode_and_privacy_bound",
        "temp_name_is_private_single_link_inode" in source
        and "is_private_single_link_owned_regular_file" in source
        and "same_inode(observed, expected)" in source
        and "status.st_nlink == 1" in source
        and "(status.st_mode & 07777) == (S_IRUSR | S_IWUSR)" in source
        and "status.st_uid == ::geteuid()" in source
        and "set_fd_private_mode_or_throw(temp.get(), label + \" temp file\")"
        in source
        and "private singly linked writer-owned inode" in source
        and "widened temp permissions are detected before rename" in cutpoint_test,
        "device/inode identity, exact 0600 mode, same ownership, and exclusive linkage are re-proven before publication",
    )

    check(
        "replacement_is_atomic_and_directory_relative",
        "::renameat(directory_fd, temp_basename.c_str(), directory_fd,"
        in source
        and "final_basename.c_str()" in source,
        "source and destination names are resolved under the same pinned directory descriptor",
    )
    check(
        "create_new_is_atomic_noreplace_and_directory_relative",
        "::renameat2(directory_fd, temp_basename.c_str()," in source
        and "directory_fd, final_basename.c_str()," in source
        and "RENAME_NOREPLACE" in source
        and "::syscall(" not in source,
        "immutable publication uses the typed Linux no-replace API under one pinned directory instead of an unchecked variadic syscall",
    )

    reconciliation_tokens = [
        "SyncImmutableFileReconciliationOutcome::Absent",
        "SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced",
        "SyncImmutableFileReconciliationOutcome::ConflictingEntry",
        "FrozenSyncPosixRegularFileSnapshot::",
        "SyncPosixDescriptorLinkPolicy::exactly_one",
        "fsync_fd_or_throw(file.get(), label + \" exact final file\")",
        "label + \" exact final parent directory\"",
        "is_private_single_link_owned_regular_file(named_after)",
    ]
    reconciliation_test_tokens = [
        "post-rename interruption must report indeterminate durability",
        "restart reconciliation must convert an exact ambiguous effect into a durable terminal fact",
        "publication must normalize final mode to 0600 despite umask",
        "exact bytes with widened permissions must not become terminal effect authority",
        "exact bytes in a multiply linked inode must not become terminal effect authority",
        "parent-component symlinks must be rejected rather than followed",
    ]
    check(
        "immutable_reconciliation_requires_exact_private_durable_identity",
        all(token in source for token in reconciliation_tokens)
        and all(token in reconciliation_test for token in reconciliation_test_tokens)
        and "cannot prove parent-directory durability" in header,
        "restart repair proves stable bytes, same-owner mode-0600 single-link identity, file sync, directory sync, and post-sync identity while Windows fails closed on its unproved directory boundary",
    )

    posix_transition_order = [
        "progress.mark_temp_reserved();",
        "AtomicFilePublicationCutpoint::TempReserved",
        "AtomicFilePublicationCutpoint::PayloadWritten",
        "AtomicFilePublicationCutpoint::TempFileSynced",
        "AtomicFilePublicationCutpoint::TempNameRevalidated",
        "AtomicFilePublicationCutpoint::ParentDirectoryRevalidated",
        "AtomicFilePublicationCutpoint::FinalEntryRevalidated",
        "publish_temp_name_or_throw(",
        "progress.mark_namespace_published();",
        "AtomicFilePublicationCutpoint::NamespacePublished",
        "parent directory after publication",
        "progress.mark_directory_synced();",
        "AtomicFilePublicationCutpoint::DirectorySynced",
        "AtomicFilePublicationCutpoint::ParentDirectoryPostpublicationRevalidated",
        "AtomicFilePublicationCutpoint::TempDescriptorClosed",
        "AtomicFilePublicationCutpoint::ParentDirectoryDescriptorClosed",
    ]
    check(
        "kernel_effects_advance_state_before_observation",
        ordered(source, posix_transition_order),
        "temp reservation, rename, and directory fsync advance allocation-free state before any injectable callback",
    )

    check(
        "every_runtime_failure_is_wrapped_with_current_outcome",
        "AtomicFilePublicationProgress progress;" in source
        and "rethrow_publication_failure(label, progress);" in source
        and "publication_failure_message" in source
        and "catch (const SyncAtomicFilePublicationError&)" not in source
        and "PublishedDurabilityIndeterminate" in source
        and "PublishedAndDirectorySynced" in source
        and "const SyncAtomicFilePublicationResidue residue = progress.residue();"
        in source,
        "preflight, write, sync, rename, already-typed callback, and close failures share one typed composition boundary with current effect and residue state",
    )

    check(
        "failure_path_uses_descriptor_sanitization_not_path_deletion",
        bool(conditional_removal_surface)
        and bool(conditional_removal_impl)
        and bool(conditional_removal_wrapper)
        and bool(conditional_content_removal_wrapper)
        and re.search(r"::unlinkat\s*\(", publication_source) is None
        and re.search(r"::unlink\s*\(", publication_source) is None
        and "DeleteFileA(" not in publication_source
        and "DeleteFileW(" not in publication_source
        and "fs::remove(" not in publication_source
        and "sanitize_unpublished_temp_fd_noexcept" in publication_source
        and "::fchmod(fd, S_IRUSR | S_IWUSR)" in publication_source
        and "::ftruncate(fd, 0)" in publication_source
        and "::fsync(fd)" in publication_source
        and "sanitize_unpublished_temp_noexcept(progress, temp);"
        in publication_source
        and "sanitize_windows_temp_handle_noexcept(temp.get());"
        in publication_source
        and "compare-and-unlink primitive" in publication_source
        and "TemporaryArtifactMayRemain" in publication_source,
        "publication failure handling sanitizes only the retained writer handle, reports residue, and performs no guessed pathname deletion; the separately audited conditional-removal owner is excluded",
    )

    check(
        "conditional_removal_displaces_before_private_unlink",
        bool(conditional_removal_impl)
        and conditional_removal_impl.count("::renameat2(") == 2
        and conditional_removal_impl.count("::unlinkat(") == 1
        and "RENAME_NOREPLACE" in conditional_removal_impl
        and "destination.basename.c_str(),"
        in conditional_removal_impl
        and "displaced_basename.c_str(), 0" in conditional_removal_impl
        and "metadata_matches_after_same_directory_rename("
        in conditional_removal_impl
        and "final path was recreated during removal"
        in conditional_removal_impl
        and "destination.basename.c_str(), &final_status"
        in conditional_removal_impl
        and re.search(
            r"::unlinkat\s*\(\s*directory\.get\(\),\s*"
            r"destination\.basename\.c_str\(\)",
            conditional_removal_impl,
        )
        is None
        and "remove_sync_file_atomically_if_expected_impl_or_throw("
        in conditional_removal_wrapper
        and "std::nullopt" in conditional_removal_wrapper
        and "remove_sync_file_atomically_if_expected_impl_or_throw("
        in conditional_content_removal_wrapper
        and "expected_destination_sha256"
        in conditional_content_removal_wrapper,
        "conditional deletion atomically moves the checked final entry to a unique private name, re-proves identity, unlinks only that private name, and preserves any recreated final entry",
    )

    check(
        "temp_residue_is_recorded_before_first_postcreate_failure",
        source.count("progress.mark_temp_reserved();") == 2
        and ordered(
            source,
            [
                "if (!temp.valid())",
                "progress.mark_temp_reserved();",
                "try {",
                "AtomicFilePublicationCutpoint::TempReserved",
            ],
        )
        and ordered(
            source,
            [
                "auto [temp, temp_basename] = create_unique_temp_at_or_throw(",
                "progress.mark_temp_reserved();",
                "try {",
                "if (::fstat(temp.get(), &temp_identity) != 0)",
            ],
        ),
        "both platform paths record possible residue immediately after successful reservation and before any later fallible operation",
    )

    required_test_tokens = [
        "kThreadCount = 10",
        "kRounds = 10",
        "same-process same-payload writers succeed",
        "distinct-payload final bytes equal one complete writer",
        "same-payload self-exec writer",
        "legacy predictable temp is not deleted or overwritten",
        "existing final symlink is rejected",
        "existing final directory is rejected",
        "terminal parent-directory symlink is rejected",
        "intermediate parent-directory symlink is rejected",
        "existing final symlink rejection is typed not-published",
        "publication_temp_count(root.path()) == 0",
        "published file grants no group or other access",
    ]
    check(
        "focused_runtime_test_covers_race_and_path_adversaries",
        all(token in test for token in required_test_tokens),
        "threads and fresh-image processes prove complete-payload linearization, legacy-owner preservation, path types, mode, and residue",
    )

    gate_publication = function_body(
        test, "void publish_start_gate_or_throw(const fs::path& gate_path)"
    )
    check(
        "cross_process_gate_is_complete_before_visibility",
        bool(gate_publication)
        and "O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW" in gate_publication
        and "staged_basename" in gate_publication
        and "RENAME_NOREPLACE" in gate_publication
        and ordered(
            gate_publication,
            [
                "::openat(",
                "::write(staged_descriptor",
                "::fsync(staged_descriptor)",
                "::close(staged_descriptor)",
                "::renameat2(",
                "staged_name_exists = false;",
                "::fsync(parent_descriptor)",
            ],
        )
        and "::open(gate_path.c_str()," not in gate_publication,
        "the test control gate is fully written and file-synced under a private staging name, then atomically published no-replace before any worker can observe it",
    )

    state_test_tokens = [
        "initial outcome is not published",
        "initial state has no possible temp residue",
        "directory sync cannot precede namespace publication",
        "reserved temp records possible pre-publication residue",
        "namespace publication consumes the temp artifact name",
        "possible temp residue cannot reopen after publication",
        "repeated monotone evidence cannot regress outcome or residue",
        "typed exception retains machine-readable outcome",
        "typed exception retains machine-readable residue",
        "two-argument compatibility constructor defaults to no residue",
        "typed exception remains runtime_error-compatible",
    ]
    check(
        "pure_state_test_covers_monotonicity_and_api_compatibility",
        all(token in state_test for token in state_test_tokens),
        "the no-filesystem test proves all outcomes, residue monotonicity, stable names, idempotence, and exception compatibility",
    )

    cutpoint_tokens = [
        "TempReserved",
        "PayloadWritten",
        "TempFileSynced",
        "TempNameRevalidated",
        "ParentDirectoryRevalidated",
        "FinalEntryRevalidated",
        "NamespacePublished",
        "DirectorySynced",
        "ParentDirectoryPostpublicationRevalidated",
        "TempDescriptorClosed",
        "ParentDirectoryDescriptorClosed",
        "throw_observer",
        "has_injected_nested_cause",
        "throw reports exact residue state",
        "caught failure leaves one sanitized private residue",
        "parent rebind is detected after temp synchronization",
        "detached original parent retains prior final generation",
        "parent rebind leaves one sanitized private residue in the retained directory",
        "post-sync parent rebind cannot return false success",
        "late detached parent contains the exact synced generation",
        "already-typed nested failures are recomposed",
        "outer typed status reflects the actual completed effects",
        "stale typed failure remains available as nested evidence",
        "temp permission mutation leaves one re-privatized empty residue",
    ]
    check(
        "caught_failure_oracle_covers_every_frontier",
        all(token in cutpoint_test for token in cutpoint_tokens)
        and "for (AtomicFilePublicationCutpoint point : posix_cutpoints())"
        in cutpoint_test,
        "each completed effect is interrupted by a thrown exception and checked for outcome, residue, visible generation, nested cause, and descriptor-bound sanitation",
    )

    unlink_authority_tokens = [
        "__wrap_unlinkat",
        "foreign-owner-payload",
        "replace_temp_name_then_fail",
        "failure handling performs no pathname deletion",
        "no check-use window can delete a foreign replacement",
        "exact temp descriptor is sanitized and residue is retained",
        "foreign replacement remains byte-exact and unsanitized",
        "descriptor sanitation does not chmod the foreign replacement",
        "sanitation follows the exact writer descriptor after name rebind",
    ]
    check(
        "unlink_authority_regression_proves_check_use_gap_closed",
        all(token in unlink_test for token in unlink_authority_tokens)
        and "-Wl,--wrap=unlinkat" in cmake,
        "the focused Linux proof detects any pathname deletion and independently proves sanitation remains bound to the writer descriptor after name replacement",
    )

    check(
        "late_parent_rebind_is_observed_after_durability",
        ordered(
            source,
            [
                "AtomicFilePublicationCutpoint::DirectorySynced",
                "verify_directory(",
                "parent directory after publication",
                "AtomicFilePublicationCutpoint::ParentDirectoryPostpublicationRevalidated",
            ],
        )
        and "verify_parent_directory_identity_or_throw(" in source
        and "post-sync parent rebind cannot return false success" in cutpoint_test
        and "PublishedAndDirectorySynced" in cutpoint_test,
        "a parent detached after the pre-rename check is re-observed only after the pinned directory has been synced, so the call fails with the exact completed-effect outcome",
    )

    crash_tokens = [
        "--anonsync-atomic-publication-crash-helper-v1",
        "verify_self_exec_child_boundary_or_throw()",
        "spawn_self_exec_test_process_or_throw(",
        "wait_for_exact_exit(",
        "::_exit(context.exit_code)",
        "crash preserves prior final generation",
        "crash leaves exactly one private temp",
        "crash residue has frontier-exact size",
        "crash exposes complete new generation",
        "post-rename crash leaves no temp name",
    ]
    check(
        "process_exit_oracle_covers_namespace_frontiers",
        all(token in cutpoint_test for token in crash_tokens)
        and "::fork()" not in cutpoint_test
        and "::waitpid(" not in cutpoint_test
        and "for (std::size_t index = 0; index < posix_cutpoints().size(); ++index)"
        in cutpoint_test,
        "a fresh exec image terminates at every frontier and the parent classifies old-final/temp versus new-final/no-temp state",
    )

    focused_loop_match = re.search(
        r"foreach\(ANONSYNC_FOCUSED_BOUNDARY_TARGET\s+(.*?)\)\s*\n\s*get_target_property",
        cmake,
        re.DOTALL,
    )
    focused_loop = focused_loop_match.group(1) if focused_loop_match else ""
    guarded_targets = [
        "anonsync_sync_atomic_file_publication_state",
        "anonsync_sync_atomic_file_publication",
        "anonsync_sync_atomic_file_publication_state_test",
        "anonsync_sync_atomic_file_publication_cutpoint_test",
        "anonsync_sync_atomic_file_publication_test",
        "anonsync_sync_atomic_file_publication_prepared_test",
        "anonsync_sync_atomic_file_reconciliation_test",
    ]
    check(
        "focused_libraries_and_tests_are_guarded_from_core_linkage",
        all(target in focused_loop for target in guarded_targets)
        and "ANONSYNC_UNLINK_AUTHORITY_LINK_LIBRARIES" in cmake
        and "focused unlink-authority proof must not link anonsync_core_lib" in cmake,
        "configure-time no-core dependency guards cover the classifier, syscall owner, and all focused proofs",
    )

    sanitizer_compile = source_list_block(cmake, "ANONSYNC_SANITIZER_COMPILE_TARGETS")
    sanitizer_link_match = re.search(
        r"foreach\(tgt\s+(.*?)\)\s*\n\s*target_link_options",
        cmake,
        re.DOTALL,
    )
    sanitizer_link = sanitizer_link_match.group(1) if sanitizer_link_match else ""
    sanitizer_targets = [
        "anonsync_sync_atomic_file_publication_state",
        "anonsync_sync_atomic_file_publication",
        "anonsync_sync_atomic_file_publication_state_test",
        "anonsync_sync_atomic_file_publication_cutpoint_test",
        "anonsync_sync_atomic_file_publication_test",
        "anonsync_sync_atomic_file_publication_prepared_test",
        "anonsync_sync_atomic_file_reconciliation_test",
    ]
    check(
        "focused_owner_is_in_sanitizer_lanes",
        all(target in sanitizer_compile for target in sanitizer_targets)
        and all(
            target in sanitizer_link
            for target in [
                "anonsync_sync_atomic_file_publication_state_test",
                "anonsync_sync_atomic_file_publication_cutpoint_test",
                "anonsync_sync_atomic_file_publication_test",
                "anonsync_sync_atomic_file_publication_prepared_test",
                "anonsync_sync_atomic_file_reconciliation_test",
            ]
        )
        and "list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS" in cmake
        and "anonsync_sync_atomic_file_publication_unlink_authority_test" in cmake
        and "target_link_options(anonsync_sync_atomic_file_publication_unlink_authority_test PRIVATE" in cmake
        and "-fsanitize=address,undefined" in cmake,
        "classifier, implementation, and all regression executables receive ASan/UBSan instrumentation and link flags",
    )

    ctest_targets = [
        "add_test(NAME anonsync_sync_atomic_file_publication_test",
        "add_test(NAME anonsync_sync_atomic_file_publication_prepared_test",
        "add_test(NAME anonsync_sync_atomic_file_publication_state_test",
        "add_test(NAME anonsync_sync_atomic_file_publication_cutpoint_test",
        "add_test(NAME anonsync_sync_atomic_file_reconciliation_test",
        "add_test(NAME anonsync_sync_atomic_file_publication_unlink_authority_test",
        "add_test(NAME anonsync_sync_atomic_file_publication_source_audit",
    ]
    check(
        "runtime_and_source_audits_are_release_tests",
        all(token in cmake for token in ctest_targets)
        and "PROPERTIES TIMEOUT 60" in cmake
        and "PROPERTIES TIMEOUT 120" in cmake
        and "PROPERTIES TIMEOUT 30" in cmake
        and "audit_sync_atomic_file_publication.py" in cmake,
        "CTest registers the race/path corpus, prepared-authority proof, pure model, cutpoint oracle, unlink-authority proof, and structural audit",
    )

    verifier_required = [
        "src/sync_atomic_file_publication.hpp",
        "src/sync_atomic_file_publication_internal.hpp",
        "src/sync_atomic_file_publication_state.hpp",
        "src/sync_atomic_file_publication_state.cpp",
        "src/sync_atomic_file_publication.cpp",
        "tests/sync_atomic_file_publication_test.cpp",
        "tests/sync_atomic_file_publication_prepared_test.cpp",
        "tests/sync_atomic_file_publication_state_test.cpp",
        "tests/sync_atomic_file_publication_cutpoint_test.cpp",
        "tests/sync_atomic_file_reconciliation_test.cpp",
        "tests/sync_atomic_file_publication_unlink_authority_test.cpp",
        "tools/audit_sync_atomic_file_publication.py",
    ]
    check(
        "release_verifier_requires_the_complete_proof_surface",
        all(token in verifier for token in verifier_required),
        "package verification cannot silently omit the API, model, observer, syscall owner, tests, or audit",
    )

    check(
        "audit_is_not_self_satisfied_by_missing_logic",
        len(audit_source.splitlines()) > 350
        and "public_failures_are_machine_classified" in audit_source
        and "caught_failure_oracle_covers_every_frontier" in audit_source
        and "process_exit_oracle_covers_namespace_frontiers" in audit_source
        and "failure_path_uses_descriptor_sanitization_not_path_deletion"
        in audit_source
        and "unlink_authority_regression_proves_check_use_gap_closed"
        in audit_source
        and "conditional_removal_displaces_before_private_unlink"
        in audit_source
        and "prepared_capability_is_move_only_and_single_use" in audit_source
        and "retained_parent_revalidation_precedes_temp_reservation" in audit_source
        and "prepared_authority_is_process_incarnation_bound" in audit_source
        and "immutable_reconciliation_requires_exact_private_durable_identity"
        in audit_source,
        "the audit itself contains substantive architecture, prepared-authority, transition-order, exception, crash, descriptor-sanitation, unlink-authority, and restart-reconciliation checks",
    )

    passed = sum(1 for item in checks if item["passed"])
    result = {
        "audit": "sync_atomic_file_publication",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
