#!/usr/bin/env python3
"""Lexical hygiene audit for rev0881 POSIX mount and namespace authority.

This inventories reviewed source ownership, capability classification, mount
fencing, descriptor cleanup, runtime witnesses, build wiring, and package
inventory. It deliberately does not claim semantic proof of kernel behavior,
control flow, race freedom, or descriptor lifetime.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/sync_directory_authority.hpp"),
    Path("src/sync_directory_authority_internal.hpp"),
    Path("src/sync_directory_authority.cpp"),
    Path("src/sync_posix_mount_namespace_authority.hpp"),
    Path("src/sync_posix_mount_namespace_authority.cpp"),
    Path("src/sync_posix_mount_namespace_authority.hpp"),
    Path("src/sync_posix_mount_namespace_authority.cpp"),
    Path("src/sync_atomic_file_publication.cpp"),
    Path("src/persistence/local_jsonl_replay_namespace.cpp"),
    Path("src/sqlite_path_security.cpp"),
    Path("tests/sync_posix_directory_resolution_test.cpp"),
    Path("tools/audit_sync_atomic_file_publication.py"),
    Path("tools/audit_local_jsonl_replay_crash_protocol.py"),
    Path("tools/audit_sync_effect_root_authority.py"),
    Path("tools/audit_sync_mount_boundary_authority.py"),
    Path("tools/verify_release_package.py"),
    Path("MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md"),
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
        "format": "anonsync-sync-mount-boundary-authority-audit-v2",
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
    header = text["src/sync_posix_directory_resolution.hpp"]
    source = text["src/sync_posix_directory_resolution.cpp"]
    authority_header = text["src/sync_directory_authority.hpp"]
    authority_internal = text["src/sync_directory_authority_internal.hpp"]
    authority = text["src/sync_directory_authority.cpp"]
    namespace_header = text["src/sync_posix_mount_namespace_authority.hpp"]
    namespace_source = text["src/sync_posix_mount_namespace_authority.cpp"]
    namespace_header = text["src/sync_posix_mount_namespace_authority.hpp"]
    namespace_source = text["src/sync_posix_mount_namespace_authority.cpp"]
    atomic = text["src/sync_atomic_file_publication.cpp"]
    jsonl_namespace = text["src/persistence/local_jsonl_replay_namespace.cpp"]
    sqlite_path = text["src/sqlite_path_security.cpp"]
    runtime = text["tests/sync_posix_directory_resolution_test.cpp"]
    atomic_audit = text["tools/audit_sync_atomic_file_publication.py"]
    jsonl_audit = text["tools/audit_local_jsonl_replay_crash_protocol.py"]
    root_audit = text["tools/audit_sync_effect_root_authority.py"]
    verifier = text["tools/verify_release_package.py"]
    design = text["MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md"]

    require(
        all(
            token in header
            for token in (
                "DeviceIdentityOnly",
                "LinuxStatxMountId",
                "LinuxOpenat2NoXdev",
                "LinuxOpenat2NoXdevAndStatxMountId",
                "SyncPosixKernelProbeDisposition",
                "Available",
                "ReportedUnavailable",
                "Fatal",
            )
        ),
        "resolution_capability_is_closed_and_typed",
        "portable, statx, openat2, combined, and probe dispositions are explicit",
    )

    capability_name = function_body(
        source, "sync_posix_directory_resolution_capability_name("
    )
    require(
        all(
            token in capability_name
            for token in (
                '"portable-device-identity-v1"',
                '"linux-statx-mount-id-v1"',
                '"linux-openat2-no-xdev-v1"',
                '"linux-openat2-no-xdev-statx-mount-id-v1"',
            )
        ),
        "capabilities_have_stable_canonical_names",
        "each observed resolution mode has a versioned name",
    )

    open_classifier = function_body(
        source, "sync_posix_classify_openat2_probe_result(\n    long syscall_result"
    )
    require(
        "syscall_result >= 0" in open_classifier
        and "error_number == ENOSYS" in open_classifier
        and open_classifier.count("ReportedUnavailable") == 1
        and "Fatal" in open_classifier,
        "openat2_probe_only_downgrades_explicit_enosys",
        "permission, contract, and unexpected failures cannot silently become portable authority",
    )

    statx_classifier = function_body(
        source, "sync_posix_classify_statx_mount_id_probe_result(\n    long syscall_result"
    )
    require(
        "mount_id_returned" in statx_classifier
        and "error_number == ENOSYS" in statx_classifier
        and "ReportedUnavailable" in statx_classifier
        and "Fatal" in statx_classifier,
        "statx_probe_requires_returned_mask_or_explicit_enosys",
        "syscall success without a mount-ID mask does not mint mount authority",
    )

    open_probe = function_body(source, "probe_openat2_no_xdev(")
    require(
        all(
            token in open_probe
            for token in (
                "SYS_openat2",
                'directory_descriptor, "."',
                "RESOLVE_BENEATH",
                "RESOLVE_NO_MAGICLINKS",
                "RESOLVE_NO_SYMLINKS",
                "RESOLVE_NO_XDEV",
                "sync_posix_classify_openat2_probe_result",
            )
        ),
        "openat2_capability_is_observed_with_complete_policy",
        "the running syscall accepts the exact flags later used for rooted traversal",
    )

    statx_probe = function_body(source, "probe_statx_mount_id(")
    require(
        all(
            token in statx_probe
            for token in (
                "SYS_statx",
                "AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW",
                "requested_mount_identity_mask()",
                "statx_mount_identity_returned(status)",
            )
        ),
        "statx_capability_is_descriptor_and_mask_observed",
        "mount identity is requested on the retained descriptor and trusted only when returned",
    )

    require(
        "STATX_MNT_ID | STATX_MNT_ID_UNIQUE" in source
        and "statx_unique_mount_identity_returned" in source
        and "bool unique = false" in header
        and "status.stx_mnt_id" in source,
        "extended_mount_id_is_preferred_and_typed",
        "the unique ID bit is requested when compiled and identity kind participates in equality",
    )

    component_open = function_body(
        source, "open_component_with_policy_and_flags("
    )
    require(
        ordered(
            component_open,
            "RequireRetainedRootMount",
            "sync_posix_directory_resolution_uses_openat2_no_xdev",
            "RESOLVE_BENEATH",
            "RESOLVE_NO_SYMLINKS",
            "RESOLVE_NO_XDEV",
            "kMaximumRaceRetries = 8U",
            "error_number == EAGAIN",
            "::openat(parent_descriptor",
        ),
        "rooted_component_open_uses_bounded_kernel_fence_then_portable_fallback",
        "openat2 no-XDEV is selected only for retained-root policy and EAGAIN cannot loop forever",
    )

    component_resolution = function_body(
        source, "open_directory_component_with_missing_policy_or_throw("
    )
    require(
        ordered(
            component_resolution,
            "component.empty()",
            "::fstatat(parent_descriptor, component.c_str()",
            "AT_SYMLINK_NOFOLLOW",
            "S_ISLNK(before.st_mode)",
            "S_ISDIR(before.st_mode)",
            "open_directory_component_with_policy",
            "::fstat(owned.get(), &after)",
            "same_identity(before, after)",
        ),
        "component_resolution_is_no_follow_and_identity_stable",
        "unsafe spelling, symlink/type changes, and rename substitution fail before descriptor transfer",
    )

    require(
        "open_error == EXDEV" in component_resolution
        and "component crosses the retained root mount" in component_resolution,
        "openat2_mount_crossing_has_explicit_failure",
        "EXDEV is not collapsed into an ordinary open error",
    )

    require(
        ordered(
            component_resolution,
            "sync_posix_directory_resolution_uses_statx_mount_id",
            "retained_root_mount.available",
            "sync_posix_capture_mount_identity_or_throw",
            "opened_mount != retained_root_mount",
            "component crosses the retained root mount",
        ),
        "opened_component_is_checked_against_retained_mount_identity",
        "statx-capable traversal independently rejects a post-open mount mismatch",
    )

    require(
        "class ScopedFd final" in source
        and "~ScopedFd() { reset(); }" in source
        and "return SyncPosixOpenedDirectory{owned.release(), after};" in source,
        "shared_resolver_owns_intermediate_descriptors",
        "exceptions close descriptors and success performs one explicit ownership transfer",
    )

    require(
        "SyncPosixDirectoryResolutionCapability resolution_capability_" in authority_header
        and "SyncPosixMountIdentity mount_identity_" in authority_header
        and "resolution_capability() const noexcept" in authority_header,
        "directory_authority_freezes_live_mount_capability",
        "resolution mode and root mount identity are owned beside the retained descriptor",
    )

    require(
        "class SyncPosixMountNamespaceAuthority final" in namespace_header
        and "const SyncPosixMountNamespaceAuthority&) = delete;" in namespace_header
        and "operator=(" in namespace_header
        and "= delete;" in namespace_header
        and "mutable std::atomic<bool> revoked_{false}" in namespace_header,
        "mount_namespace_authority_is_move_only_and_sticky",
        "the calling thread namespace is represented by one noncopyable live capability",
    )
    namespace_verify = function_body(
        namespace_source, "SyncPosixMountNamespaceAuthority::verify_or_throw("
    )
    require(
        '"/proc/thread-self/ns/mnt"' in namespace_source
        and "::fstat" in namespace_source
        and "status.st_dev" in namespace_source
        and "status.st_ino" in namespace_source
        and "open_current_mount_namespace_or_throw" in namespace_verify
        and "revoked_.store(true, std::memory_order_release)" in namespace_verify,
        "mount_namespace_reproof_uses_retained_and_fresh_kernel_handles",
        "documented st_dev/st_ino identity is compared on every proof and any contradiction revokes",
    )

    authority_open = function_body(
        authority, "SyncDirectoryAuthority::open_or_throw("
    )
    require(
        ordered(
            authority_open,
            "traverse_directory_or_throw",
            "capture_attestation_or_throw",
            "require_owner_controlled_mutation_surface_or_throw",
            "sync_posix_probe_directory_resolution_capability_or_throw",
            "sync_posix_capture_mount_identity_or_throw",
            "initial proof",
        ),
        "authority_mint_observes_capability_after_structural_root_proof",
        "the root exists, is owner controlled, and then freezes actual syscall/mount evidence",
    )

    authority_verify = function_body(
        authority, "SyncDirectoryAuthority::verify_or_throw("
    )
    require(
        ordered(
            authority_verify,
            "sync_posix_verify_directory_resolution_capability_or_throw",
            "sync_posix_capture_mount_identity_or_throw",
            "retained_mount != mount_identity_",
            "traverse_directory_or_throw(path_",
            "reached_mount != mount_identity_",
            "revoked_ = true",
        ),
        "authority_reproof_binds_retained_and_reached_mount_with_sticky_failure",
        "capability loss, retained mount change, or path mount change permanently revokes the live owner",
    )

    digest = function_body(
        authority, "sync_directory_attestation_digest_or_throw("
    )
    require(
        "resolution_capability" not in digest
        and "mount_identity" not in digest
        and "mount_namespace" not in digest
        and "anonsync-sync-directory-attestation-v1" in digest
        and "runtime-ephemeral" in authority_header
        and "not restart-stable identity" in authority_header,
        "ephemeral_mount_evidence_is_not_smuggled_into_durable_v1_digest",
        "restart identity remains structural while namespace and mount IDs stay explicitly live-only",
    )
    namespace_verify = function_body(
        namespace_source, "SyncPosixMountNamespaceAuthority::verify_or_throw("
    )
    require(
        "/proc/thread-self/ns/mnt" in namespace_source
        and "status.st_dev" in namespace_source
        and "status.st_ino" in namespace_source
        and "revoked_.load(std::memory_order_acquire)" in namespace_verify
        and "revoked_.store(true, std::memory_order_release)" in namespace_verify
        and "mount namespace changed" in namespace_verify
        and "SyncPosixMountNamespaceAuthority" in namespace_header,
        "calling_thread_mount_namespace_is_live_and_sticky",
        "retained-root mount policy is invalidated if the calling thread changes namespace context",
    )

    authority_traversal = function_body(authority, "traverse_directory_or_throw(")
    rooted_traversal = function_body(
        atomic, "open_relative_directory_from_root_or_throw("
    )
    absolute_traversal = function_body(atomic, "open_parent_directory_or_throw(")
    require(
        "sync_posix_open_directory_component_or_throw" in authority_traversal
        and "::fstatat" not in authority_traversal
        and "::openat(" not in authority_traversal
        and "sync_posix_open_directory_component_or_throw" in rooted_traversal
        and "::fstatat" not in rooted_traversal
        and "::openat(" not in rooted_traversal
        and "sync_posix_open_directory_component_or_throw" in absolute_traversal
        and "::fstatat" not in absolute_traversal
        and "::openat(" not in absolute_traversal,
        "three_component_loops_delegate_to_one_syscall_owner",
        "authority, rooted publication, and absolute publication no longer copy component traversal",
    )

    require(
        "SyncPosixDirectoryMountPolicy::RequireRetainedRootMount"
        in rooted_traversal
        and "lease.resolution_capability" in rooted_traversal
        and "lease.mount_identity" in rooted_traversal,
        "rooted_publication_consumes_frozen_mount_policy",
        "the duplicate descriptor travels with the exact capability and retained mount identity",
    )

    duplicate = function_body(
        authority,
        "SyncDirectoryAuthorityAccess::duplicate_shared_open_description_or_throw(",
    )
    duplicate_cleanup = function_body(
        authority,
        "SyncDirectorySharedOpenDescriptionLease::reset_noexcept()",
    )
    require(
        ordered(
            duplicate,
            "root authority before descriptor duplication",
            "descriptor_no_verify",
            "F_DUPFD_CLOEXEC",
            "SyncDirectorySharedOpenDescriptionLease lease",
            "root authority after descriptor duplication",
            "return lease",
        )
        and "::close(descriptor_)" in duplicate_cleanup,
        "post_duplication_reproof_failure_closes_untransferred_descriptor",
        "the centralized move-only lease closes an untransferred duplicate when post-duplication authority reproof rejects it",
    )

    require(
        "resolution_capability_no_verify()" in duplicate
        and "mount_identity_no_verify()" in duplicate
        and "SyncPosixMountIdentity mount_identity" in authority_internal
        and "file offsets and status flags are shared" in authority_internal
        and "duplicate_shared_open_description_or_throw" in atomic,
        "verified_descriptor_lease_transfers_complete_live_evidence",
        "one explicitly shared-open-description bridge transfers the exact capability and retained mount evidence without pretending cursor independence",
    )

    descendant_policy = function_body(
        atomic, "require_owner_controlled_descendant_directory_or_throw("
    )
    require(
        all(
            token in descendant_policy
            for token in (
                "posix_device_value(status)",
                "root.device",
                "status.st_uid",
                "root.effective_user_id",
                "S_IRUSR | S_IWUSR | S_IXUSR",
                "S_IWGRP | S_IWOTH",
            )
        ),
        "mount_fence_composes_with_owner_and_mode_policy",
        "new Linux evidence strengthens rather than replaces the portable mutation-surface checks",
    )

    require(
        "::openat(" in jsonl_namespace
        and "regular_open_flags" in jsonl_namespace
        and "journal_basename_" in jsonl_namespace
        and "::openat(" in sqlite_path
        and "::mkdirat(" in sqlite_path
        and "SQLite family member" in sqlite_path,
        "remaining_openat_users_are_member_or_creation_contracts",
        "JSONL regular members and SQLite create/member policy remain distinct from directory-only traversal",
    )

    require(
        all(
            token in runtime
            for token in (
                "successful openat2 probe is available",
                "ENOSYS openat2 probe is explicitly unavailable",
                "EINVAL openat2 probe cannot silently downgrade policy",
                "permission-hidden openat2 cannot silently downgrade policy",
                "unexpected openat2 failure is fatal",
                "statx mount-id mask proves availability",
                "successful statx without mount-id mask is unavailable",
            )
        ),
        "runtime_has_deterministic_probe_classifier_matrix",
        "success, explicit absence, policy denial, contract failure, and unexpected failure are distinguished",
    )

    require(
        all(
            token in runtime
            for token in (
                "ordinary same-mount child opens as a directory",
                "symbolic-link child is rejected",
                "parent escape component is rejected",
                "repeated live mount observation preserves value and identity kind",
                "retained authority reproof survives move ownership",
            )
        ),
        "runtime_exercises_component_and_live_authority_contract",
        "ordinary, unsafe, symlink, repeated mount, move, and reproof paths are executable",
    )

    require(
        all(
            token in runtime
            for token in (
                'fs::is_directory("/proc/bus"',
                "parent_status.st_dev == child_status.st_dev",
                "proc_mount != proc_bus_mount",
                "uses_statx_mount_id",
                'proc.get(), "bus", "/proc/bus"',
                "same-st_dev /proc/bus mount crossing is rejected",
            )
        ),
        "runtime_uses_actual_same_device_mount_witness",
        "the cloud host can prove the exact bind-like boundary class without CAP_SYS_ADMIN",
    )

    resolution_library = cmake_call(
        cmake, "add_library(anonsync_sync_posix_directory_resolution"
    )
    resolution_test = cmake_call(
        cmake, "add_executable(anonsync_sync_posix_directory_resolution_test"
    )
    require(
        "${ANONSYNC_SYNC_POSIX_DIRECTORY_RESOLUTION_SOURCE}"
        in resolution_library
        and "tests/sync_posix_directory_resolution_test.cpp" in resolution_test
        and "anonsync_sync_posix_directory_resolution_test" in cmake,
        "cmake_owns_shared_leaf_and_runtime_test",
        "the new source is not hidden inside a monolith and has a registered executable",
    )

    require(
        "anonsync_sync_posix_directory_resolution\n"
        in cmake
        and "anonsync_sync_posix_directory_resolution_test\n" in cmake
        and "ANONSYNC_SANITIZER_COMPILE_TARGETS" in cmake,
        "focused_and_sanitizer_lanes_include_resolution_targets",
        "both library and executable participate in the focused boundary and sanitizer inventories",
    )

    require(
        "anonsync_sync_mount_boundary_authority_source_audit" in cmake
        and "audit_sync_mount_boundary_authority.py" in cmake
        and "PROPERTIES TIMEOUT 20" in cmake,
        "mount_boundary_audit_is_registered",
        "the lexical inventory runs in the complete CTest registry",
    )

    require(
        all(
            token in verifier
            for token in (
                "revision_number >= 880",
                '"src/sync_posix_directory_resolution.hpp"',
                '"src/sync_posix_directory_resolution.cpp"',
                '"tests/sync_posix_directory_resolution_test.cpp"',
                '"tools/audit_sync_mount_boundary_authority.py"',
                '"MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md"',
            )
        ),
        "release_verifier_requires_rev0880_surface",
        "a package cannot claim rev0880 while omitting implementation, test, audit, or design record",
    )

    require(
        "sync_posix_directory_resolution" in atomic_audit
        and "sync_posix_directory_resolution" in root_audit
        and "sync_directory_authority" in jsonl_audit,
        "inherited_audits_follow_refactored_ownership",
        "older hygiene checks were adapted instead of preserving false duplicated-source assumptions",
    )

    require(
        all(
            token in design
            for token in (
                "https://man7.org/linux/man-pages/man2/openat2.2.html",
                "https://man7.org/linux/man-pages/man2/statx.2.html",
                "https://docs.kernel.org/filesystems/path-lookup.html",
                "STATX_MNT_ID_UNIQUE",
                "boot-epoch",
                "Explicit mount allowlists",
                "Deliberate nonclaims",
                "lexical hygiene",
            )
        ),
        "design_record_contains_primary_research_speculation_and_scope",
        "kernel sources, future protocols, nonclaims, and audit limitations are explicit",
    )

    require(
        "does not claim" in __doc__
        and "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(
            encoding="utf-8"
        ),
        "audit_disclaims_semantic_proof",
        "source vocabulary is never reported as behavioral or formal assurance",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
