#!/usr/bin/env python3
"""Lexical hygiene audit for retained-root file-effect authority.

This audit deliberately does not claim semantic proof. It inventories the
load-bearing root capability, descriptor-relative publication, exact schema,
and adversarial runtime surface so later refactors cannot silently substitute
pathname text or duplicated traversal code for the reviewed authority boundary.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority_internal.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/persistence/local_jsonl_replay_directory_authority.hpp"),
    Path("src/persistence/local_jsonl_replay_directory_authority.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.hpp"),
    Path("src/sync_replica_file_effect_sqlite_owner.cpp"),
    Path("tests/persistence/local_jsonl_replay_directory_authority_tests.cpp"),
    Path("tests/sync_replica_file_effect_sqlite_owner_test.cpp"),
    Path("tests/sync_posix_directory_resolution_test.cpp"),
    Path("tools/audit_sync_atomic_file_publication.py"),
    Path("tools/audit_local_jsonl_replay_crash_protocol.py"),
    Path("tools/audit_sync_effect_root_authority.py"),
    Path("tools/verify_release_package.py"),
    Path("ROOTED_EFFECT_DIRECTORY_AUTHORITY_AUDIT_rev0879.md"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def delimited_body(text: str, signature: str, opening: str, closing: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    for index in range(boundary, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def function_body(text: str, signature: str) -> str:
    return delimited_body(text, signature, "{", "}")


def cmake_call(text: str, command_prefix: str) -> str:
    return delimited_body(text, command_prefix, "(", ")")


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-effect-root-authority-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
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
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    cmake = text["CMakeLists.txt"]
    authority_header = text["src/sync_directory_authority.hpp"]
    authority_internal = text["src/sync_directory_authority_internal.hpp"]
    authority = text["src/sync_directory_authority.cpp"]
    resolution_header = text["src/sync_posix_directory_resolution.hpp"]
    resolution = text["src/sync_posix_directory_resolution.cpp"]
    wrapper_header = text[
        "src/persistence/local_jsonl_replay_directory_authority.hpp"
    ]
    wrapper = text[
        "src/persistence/local_jsonl_replay_directory_authority.cpp"
    ]
    atomic_header = text["src/sync_atomic_file_publication.hpp"]
    atomic = text["src/sync_atomic_file_publication.cpp"]
    effect_header = text["src/sync_replica_file_effect_sqlite_owner.hpp"]
    effect = text["src/sync_replica_file_effect_sqlite_owner.cpp"]
    directory_runtime = text[
        "tests/persistence/local_jsonl_replay_directory_authority_tests.cpp"
    ]
    effect_runtime = text["tests/sync_replica_file_effect_sqlite_owner_test.cpp"]
    atomic_audit = text["tools/audit_sync_atomic_file_publication.py"]
    jsonl_audit = text["tools/audit_local_jsonl_replay_crash_protocol.py"]
    verifier = text["tools/verify_release_package.py"]
    design_record = text["ROOTED_EFFECT_DIRECTORY_AUTHORITY_AUDIT_rev0879.md"]

    require(
        all(
            token in authority_header
            for token in (
                "class SyncDirectoryAuthority final",
                "SyncDirectoryAuthority(const SyncDirectoryAuthority&) = delete",
                "SyncDirectoryAuthority(SyncDirectoryAuthority&& other) noexcept",
                "SyncProcessIncarnation process_id_",
                "SyncThreadIncarnation thread_id_",
                "int descriptor_ = -1",
                "mutable bool revoked_ = false",
            )
        ),
        "directory_authority_is_move_only_affine_retained_capability",
        "the shared owner retains one descriptor and cannot be copied across process/thread authority",
    )

    open_authority = function_body(
        authority, "SyncDirectoryAuthority::open_or_throw("
    )
    require(
        ordered(
            open_authority,
            "current_sync_process_incarnation_noexcept",
            "current_sync_thread_incarnation_noexcept",
            "traverse_directory_or_throw",
            "capture_attestation_or_throw",
            "require_owner_controlled_mutation_surface_or_throw",
            "initial proof",
        ),
        "authority_mint_freezes_identity_policy_before_return",
        "the root descriptor, credentials, mode, mount observations, and first reproof precede capability return",
    )

    traversal = function_body(authority, "traverse_directory_or_throw(")
    directory_component = function_body(
        resolution, "sync_posix_open_directory_component_or_throw("
    )
    directory_open = function_body(
        resolution, "open_directory_component_with_policy("
    )
    require(
        ordered(
            traversal,
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
        and "O_NOFOLLOW" in resolution
        and "SyncPosixOpenedDirectory" in resolution_header,
        "absolute_traversal_is_componentwise_and_identity_checked",
        "a lexical root path delegates to one shared component resolver that rejects symlinks and identity changes",
    )

    policy = function_body(
        authority, "require_owner_controlled_mutation_surface_or_throw("
    )
    require(
        all(
            token in policy
            for token in (
                "owner_user_id != attestation.effective_user_id",
                "S_IRUSR | S_IWUSR | S_IXUSR",
                "S_IWGRP | S_IWOTH",
                "ST_RDONLY",
            )
        ),
        "root_policy_rejects_unowned_or_shared_mutation_surface",
        "minting requires effective-user ownership, owner rwx, no group/other write, and a writable mount",
    )

    verification = function_body(
        authority, "SyncDirectoryAuthority::verify_or_throw("
    )
    require(
        ordered(
            verification,
            "require_current_owner_or_throw",
            "revoked_",
            "::fstat(descriptor_",
            "capture_attestation_or_throw",
            "same_attestation",
            "traverse_directory_or_throw(path_",
            "path no longer names the retained directory",
            "revoked_ = true",
        ),
        "reproof_binds_retained_object_and_current_path_with_sticky_failure",
        "both descriptor and path must still match the frozen attestation; any failed proof permanently revokes the object",
    )

    digest = function_body(
        authority, "sync_directory_attestation_digest_or_throw("
    )
    digest_fields = (
        "attestation.device",
        "attestation.inode",
        "attestation.owner_user_id",
        "attestation.owner_group_id",
        "attestation.effective_user_id",
        "attestation.effective_group_id",
        "attestation.permission_mode",
        "attestation.filesystem_id",
        "attestation.mount_flags",
        "attestation.filesystem_name_maximum",
        "attestation.path_name_maximum",
    )
    require(
        "anonsync-sync-directory-attestation-v1" in digest
        and all(field in digest for field in digest_fields)
        and digest.count("append_u64") >= len(digest_fields),
        "directory_attestation_digest_is_domain_separated_and_complete",
        "all frozen scalar observations participate in the canonical SHA-256 root identity",
    )

    require(
        "using LocalJsonlReplayDirectoryAttestation = SyncDirectoryAttestation"
        in wrapper_header
        and "SyncDirectoryAuthority authority_" in wrapper_header
        and all(
            token in wrapper
            for token in (
                "SyncDirectoryAuthority::open_or_throw",
                "return authority_.path()",
                "return authority_.absolute_path()",
                "return authority_.attestation()",
                "authority_.verify_or_throw(label)",
                "authority_.descriptor_no_verify()",
                "authority_.name_maximum_no_verify()",
            )
        ),
        "local_jsonl_owner_delegates_to_shared_authority",
        "the compatibility facade preserves API shape while one generic implementation owns traversal and revocation",
    )
    require(
        all(
            token not in wrapper
            for token in (
                "::open(",
                "::openat(",
                "::fstatat(",
                "descriptor_ =",
                "attestation_ =",
                "revoked_ =",
            )
        ),
        "local_jsonl_wrapper_contains_no_duplicate_security_state_machine",
        "future fixes cannot diverge between JSONL and file-effect roots through a copied syscall owner",
    )

    rooted_header_tokens = (
        "write_sync_file_atomically_create_new_under_directory_or_throw",
        "reconcile_sync_immutable_file_create_new_under_directory_or_throw",
        "const SyncDirectoryAuthority& root_authority",
        "canonical_relative_path",
    )
    require(
        all(token in atomic_header for token in rooted_header_tokens)
        and atomic_header.count("#if !defined(_WIN32)") >= 2,
        "atomic_publication_exposes_posix_rooted_effect_apis",
        "publication and restart reconciliation consume the same opaque retained root capability",
    )

    relative_validation = function_body(
        atomic, "rooted_relative_destination_or_throw("
    )
    require(
        all(
            token in relative_validation
            for token in (
                "relative_path.empty()",
                "relative_path.is_absolute()",
                "has_root_name()",
                "has_root_directory()",
                'component == "."',
                'component == ".."',
                "component.find('/')",
                "component.find('\\\\')",
                "component.find('\\0')",
                "lexically_normal() != relative_path",
            )
        ),
        "rooted_destination_requires_strict_canonical_relative_path",
        "absolute, rooted, dot, separator-bearing, NUL-bearing, and noncanonical components are rejected",
    )

    duplicate_root = function_body(
        authority,
        "SyncDirectoryAuthorityAccess::duplicate_shared_open_description_or_throw(",
    )
    duplicate_cleanup = function_body(
        authority,
        "SyncDirectorySharedOpenDescriptionLease::reset_noexcept()",
    )
    require(
        ordered(
            duplicate_root,
            "root authority before descriptor duplication",
            "descriptor_no_verify",
            "F_DUPFD_CLOEXEC",
            "SyncDirectorySharedOpenDescriptionLease lease",
            "root authority after descriptor duplication",
            "return lease",
        )
        and "::close(descriptor_)" in duplicate_cleanup
        and "file offsets and status flags are shared" in authority_internal
        and "duplicate_shared_open_description_or_throw" in atomic,
        "root_descriptor_duplication_is_bracketed_by_reproof",
        "the rooted operation receives one RAII-owned close-on-exec shared-open-description duplicate only while the owning capability remains valid",
    )

    relative_open = function_body(
        atomic, "open_relative_directory_from_root_or_throw("
    )
    require(
        ordered(
            relative_open,
            "duplicate_root_directory_or_throw",
            "sync_posix_open_directory_component_or_throw",
            "SyncPosixDirectoryComponentRole::RootedDescendant",
            "SyncPosixDirectoryMountPolicy::RequireRetainedRootMount",
            "require_owner_controlled_descendant_directory_or_throw",
            "root_authority.verify_or_throw",
        )
        and ordered(
            directory_component,
            "::fstatat(parent_descriptor, component.c_str(),",
            "open_directory_component_with_policy",
            "same_identity(before, after)",
        ),
        "relative_traversal_is_descriptor_based_identity_checked_and_reproved",
        "each descendant uses the shared descriptor-relative resolver and retained-root mount policy before any mutation can reserve a temp inode",
    )

    descendant_policy = function_body(
        atomic, "require_owner_controlled_descendant_directory_or_throw("
    )
    require(
        all(
            token in descendant_policy
            for token in (
                "root.device",
                "root.effective_user_id",
                "S_IRUSR | S_IWUSR | S_IXUSR",
                "S_IWGRP | S_IWOTH",
            )
        ),
        "descendant_policy_rejects_device_owner_or_mode_escape",
        "relative parents cannot cross st_dev, change owner, lose owner rwx, or grant group/other write",
    )

    common_publish = function_body(
        atomic, "publish_posix_from_retained_directory_or_throw("
    )
    require(
        ordered(
            common_publish,
            "verify_directory",
            "create_unique_temp_at_or_throw",
            "fsync_fd_or_throw(temp.get()",
            "verify_directory",
            "publish_temp_name_or_throw",
            "fsync_fd_or_throw(directory.get()",
            "verify_directory",
        ),
        "one_publication_state_machine_revalidates_before_and_after_mutation",
        "absolute and rooted callers share temp reservation, file sync, no-replace rename, directory sync, and proof cutpoints",
    )
    require(
        atomic.count("publish_posix_from_retained_directory_or_throw(") == 4,
        "rooted_publication_does_not_duplicate_the_syscall_state_machine",
        "one definition plus three call sites serve prepared/absolute/rooted paths rather than copied protocols",
    )

    common_reconcile = function_body(
        atomic,
        "reconcile_posix_immutable_file_from_retained_directory_or_throw(",
    )
    require(
        ordered(
            common_reconcile,
            "::fstatat",
            "verify_directory",
            "::openat",
            "freeze_borrowed_descriptor_or_throw",
            "fsync_fd_or_throw(file.get()",
            "fsync_fd_or_throw(directory.get()",
            "verify_directory",
            "same_inode",
        ),
        "one_reconciliation_state_machine_proves_exact_bytes_and_directory",
        "absence, conflict, and exact durable identity are classified from a retained parent and caller-supplied reproof",
    )

    require(
        "SyncDirectoryAuthority root_authority_" in effect_header
        and "std::string root_authority_digest_" in effect_header
        and "std::string root_authority_digest" in effect_header,
        "effect_owner_and_snapshot_carry_root_identity",
        "process-lifetime capability and durable digest are both visible at the ownership boundary",
    )
    require(
        "constexpr std::uint64_t kSchemaVersion = 3U" in effect
        and "constexpr std::uint64_t kLegacySchemaVersion = 2U" in effect
        and effect.count("root_authority_digest TEXT NOT NULL") >= 2
        and "database does not match exact file-effect schema v2 or v3" in effect,
        "effect_schema_v2_v3_require_exact_root_digest",
        "migration and current state both retain the exact root identity instead of accepting whichever object occupies the path",
    )
    require(
        "anonsync-replica-file-effect-publication-v2" in effect
        and "anonsync-replica-file-effect-cutpoint-v2" in effect
        and effect.count("digest_field(digest, root_authority_digest)") >= 1
        and "digest_field(cutpoint, root_authority_digest)" in effect,
        "publication_and_cutpoint_digests_bind_root_authority",
        "filesystem identity participates in both terminal effect evidence and complete database attestation",
    )

    constructor = function_body(
        effect,
        "SyncReplicaFileEffectSqliteOwner::SyncReplicaFileEffectSqliteOwner(",
    )
    require(
        ordered(
            constructor,
            "SyncDirectoryAuthority::open_or_throw",
            "sync_directory_attestation_digest_or_throw",
            "schema initialization root authority",
            "SyncSqliteTransactionMode::Immediate",
            "root_authority_digest_",
            "pre-commit root authority",
            "transaction.commit()",
        ),
        "effect_owner_mints_and_rechecks_root_around_schema_cutpoint",
        "new and existing databases are accepted only while the exact retained root matches the durable digest",
    )

    stage = function_body(
        effect,
        "SyncReplicaFileEffectSqliteOwner::stage_with_diagnostics_or_throw(",
    )
    require(
        ordered(
            stage,
            "stage root authority",
            "SyncSqliteTransactionMode::Immediate",
            "load_state_or_throw",
            "stage mutation root authority",
            "insert_effect_or_throw",
            "load_state_or_throw",
            "staged cutpoint pre-commit root authority",
            "transaction.commit()",
        ),
        "staging_brackets_mutation_and_commit_with_root_reproof",
        "a same-path replacement cannot manufacture or redirect a staged durable effect cutpoint",
    )

    materialize = function_body(
        effect, "SyncReplicaFileEffectSqliteOwner::materialize_or_throw("
    )
    require(
        all(
            token in materialize
            for token in (
                "canonical_relative_effect_path_or_throw",
                "reconcile_sync_immutable_file_create_new_under_directory_or_throw",
                "write_sync_file_atomically_create_new_under_directory_or_throw",
                "publication mark root authority",
                "published cutpoint pre-commit root authority",
                "post-mark terminal proof",
            )
        )
        and "root_path_ /" not in materialize,
        "materialization_is_rooted_and_terminally_reconciled",
        "POSIX publication never rebuilds an absolute destination from root text and still re-proves exact bytes after the database mark",
    )

    require(
        all(
            token in effect_runtime
            for token in (
                "test_live_root_rebind_sticky_revocation",
                "same-path root replacement must be detected before stage mutation",
                "replacement tree must receive neither staged nor materialized bytes",
                "a revoked root must block materialization",
                "test_restart_rejects_same_path_replacement_root",
                "root directory authority identity mismatch",
                "test_descendant_directory_policy_blocks_uncontrolled_publication",
                "group/other-writable descendant directory",
                "must receive no temporary or final effect entry",
            )
        ),
        "runtime_covers_live_restart_and_descendant_negative_paths",
        "same-path replacement, sticky revocation, restart mismatch, and shared-writable descendants are executable failures",
    )
    require(
        all(
            token in directory_runtime
            for token in (
                "test_attestation_change_is_sticky_revocation",
                "test_path_topology_reproof",
                "test_foreign_thread_rejected_without_revocation",
                "test_fork_inheritance_fail_stops",
                "move preserves the frozen directory identity",
            )
        ),
        "shared_authority_retains_existing_runtime_capability_matrix",
        "the JSONL refactor preserves mode drift, topology, move, thread, and fork evidence",
    )

    generic_target = cmake_call(
        cmake, "add_library(anonsync_sync_directory_authority STATIC"
    )
    atomic_links = cmake_call(
        cmake, "target_link_libraries(anonsync_sync_atomic_file_publication"
    )
    wrapper_links = cmake_call(
        cmake,
        "target_link_libraries(anonsync_local_jsonl_replay_directory_authority",
    )
    require(
        "ANONSYNC_SYNC_DIRECTORY_AUTHORITY_SOURCE" in generic_target
        and "anonsync_sync_directory_authority" in atomic_links
        and "anonsync_sync_directory_authority" in wrapper_links,
        "build_graph_has_one_shared_directory_authority_leaf",
        "atomic publication and JSONL compatibility code converge on the generic library",
    )
    require(
        cmake.count("anonsync_sync_directory_authority") >= 7
        and "anonsync_sync_effect_root_authority_source_audit" in cmake
        and "audit_sync_effect_root_authority.py" in cmake,
        "shared_authority_and_audit_participate_in_registered_gates",
        "focused-source guards, sanitizer inventory, dependency graph, and CTest can observe the new boundary",
    )

    require(
        "verify_directory(" in atomic_audit
        and "late_parent_rebind_is_observed_after_durability" in atomic_audit
        and "src/sync_directory_authority.cpp" in jsonl_audit
        and "SyncDirectoryAuthority authority_" in jsonl_audit
        and "generic_directory_cpp" in jsonl_audit,
        "neighboring_audits_track_refactored_ownership",
        "older audits were updated rather than relaxed or left pointed at removed duplicate code",
    )

    verifier_tokens = (
        "revision_number >= 879",
        "src/sync_directory_authority.hpp",
        "src/sync_directory_authority.cpp",
        "tools/audit_sync_effect_root_authority.py",
        "ROOTED_EFFECT_DIRECTORY_AUTHORITY_AUDIT_rev0879.md",
    )
    require(
        all(token in verifier for token in verifier_tokens),
        "release_verifier_requires_rev0879_root_authority_surface",
        "a rev0879 package cannot omit generic code, the focused audit, or its design record",
    )

    require(
        all(
            token in design_record
            for token in (
                "same-path directory replacement",
                "schema version 2",
                "RESOLVE_NO_XDEV",
                "same-device bind mount",
                "Windows",
                "O(history)",
                "lexical hygiene",
            )
        ),
        "design_record_names_limits_and_nonclaims",
        "the revision documents migration refusal, platform asymmetry, mount limitations, oracle cost, and audit scope",
    )

    own_source = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in own_source
        and "does not claim semantic proof" in own_source,
        "audit_does_not_overclaim_lexical_checks",
        "compiler, runtime, sanitizer, restart, and package evidence remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
