#!/usr/bin/env python3
"""Lexical audit for product-spine SQLite targeting and bootstrap order.

This pins reviewed call-site intent and failed-open ownership ordering. It is a
source hygiene check, not semantic proof of filesystem identity, SQLite, crash
behavior, or multi-database atomicity.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sqlite_path_security.cpp"),
    Path("src/sqlite_path_security.hpp"),
    Path("src/sync_posix_mount_namespace_authority.cpp"),
    Path("src/sync_posix_mount_namespace_authority.hpp"),
    Path("src/sync_posix_directory_resolution.cpp"),
    Path("src/sync_posix_directory_resolution.hpp"),
    Path("src/sync_replica_deployment_manifest.cpp"),
    Path("tests/persistence/sqlite_persistence_process_authority_fork_test.cpp"),
    Path("tests/sync_posix_directory_resolution_test.cpp"),
    Path("tools/test_anonsync_replica_cli.py"),
    Path("tools/test_anonsync_replica_bootstrap_resume.py"),
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


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(text):
        byte = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if byte == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if byte == "*" and following == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif byte == "\\":
                escaped = True
            elif byte == quote:
                quote = ""
            index += 1
            continue
        if byte == "/" and following == "/":
            line_comment = True
            index += 2
            continue
        if byte == "/" and following == "*":
            block_comment = True
            index += 2
            continue
        if byte == "#":
            line_comment = True
            index += 1
            continue
        if byte in ('"', "'"):
            quote = byte
            index += 1
            continue
        if byte == "{":
            depth += 1
        elif byte == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-replica-database-open-policy-audit-v16",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling and order do not prove path identity, SQLite "
            "durability, crash recovery, race freedom, or cross-store atomicity"
        ),
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

    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    source = (root / "src/anonsync_replica.cpp").read_text(encoding="utf-8")
    path_security = (root / "src/sqlite_path_security.cpp").read_text(
        encoding="utf-8"
    )
    path_security_header = (root / "src/sqlite_path_security.hpp").read_text(
        encoding="utf-8"
    )
    mount_namespace_source = (
        root / "src/sync_posix_mount_namespace_authority.cpp"
    ).read_text(encoding="utf-8")
    mount_namespace_header = (
        root / "src/sync_posix_mount_namespace_authority.hpp"
    ).read_text(encoding="utf-8")
    directory_resolution_source = (
        root / "src/sync_posix_directory_resolution.cpp"
    ).read_text(encoding="utf-8")
    directory_resolution_header = (
        root / "src/sync_posix_directory_resolution.hpp"
    ).read_text(encoding="utf-8")
    directory_resolution_test = (
        root / "tests/sync_posix_directory_resolution_test.cpp"
    ).read_text(encoding="utf-8")
    manifest = (root / "src/sync_replica_deployment_manifest.cpp").read_text(
        encoding="utf-8"
    )
    process_authority_test = (
        root
        / "tests/persistence/sqlite_persistence_process_authority_fork_test.cpp"
    ).read_text(encoding="utf-8")
    process_test = (root / "tools/test_anonsync_replica_cli.py").read_text(
        encoding="utf-8"
    )
    resume_process_test = (
        root / "tools/test_anonsync_replica_bootstrap_resume.py"
    ).read_text(encoding="utf-8")

    candidate_owner = function_body(source, "class UnadoptedSqliteConnection final")
    product_authority = function_body(
        source, "class ProductSqliteDatabaseAuthority final"
    )
    reject_helper = function_body(
        source, "reject_unadopted_database_handle_or_throw("
    )
    open_helper = function_body(
        source, "ProductSqliteDatabaseAuthority open_database_or_throw("
    )
    detached_open = function_body(
        source, "open_detached_bootstrap_database_or_throw("
    )
    operational_profile = function_body(
        source, "configure_operational_database_profile_or_throw("
    )
    candidate_preflight = function_body(
        source, "require_bootstrap_candidate_header_and_namespace_or_throw("
    )
    candidate_lock = function_body(
        source, "retain_exclusive_bootstrap_candidate_locking_mode_or_throw("
    )
    candidate_promotion = function_body(
        source,
        "void promote_bound_bootstrap_candidate_to_operational_or_throw(",
    )
    rooted_vfs_open = function_body(
        path_security, "static int open(sqlite3_vfs* wrapper,"
    )
    rooted_vfs_verify = function_body(
        path_security,
        "void SqliteDescriptorRootedVfs::verify_open_database_or_throw(",
    )
    rooted_vfs_main_file = function_body(
        path_security,
        "[[nodiscard]] sqlite3_file* main_file_for_database_or_throw(",
    )
    rooted_vfs_preopen_read = function_body(
        path_security,
        "read_bounded_main_file_before_open_or_throw(",
    )
    rooted_vfs_live_read = function_body(
        path_security,
        "[[nodiscard]] std::string read_bounded_main_file_or_throw(",
    )
    rooted_vfs_live_sync = function_body(
        path_security,
        "void sync_main_file_and_parent_directory_or_throw(",
    )
    rooted_vfs_shm_map = function_body(
        path_security, "static int shm_map(sqlite3_file* file,"
    )
    rooted_vfs_shm_unmap = function_body(
        path_security, "static int shm_unmap(sqlite3_file* file,"
    )
    rooted_vfs_file_from = function_body(
        path_security,
        "[[nodiscard]] static WrappedFile& from(sqlite3_file* file)",
    )
    rooted_vfs_file_from_context = function_body(
        path_security,
        "[[nodiscard]] static WrappedFile& from_context(",
    )
    rooted_vfs_close = function_body(
        path_security, "static int close(sqlite3_file* file)"
    )
    rooted_vfs_read = function_body(
        path_security, "static int read(sqlite3_file* file,"
    )
    rooted_vfs_write = function_body(
        path_security, "static int write(sqlite3_file* file,"
    )
    rooted_vfs_sync = function_body(
        path_security, "static int sync(sqlite3_file* file,"
    )
    rooted_vfs_lock = function_body(
        path_security, "static int lock(sqlite3_file* file,"
    )
    rooted_vfs_file_control = function_body(
        path_security, "static int file_control(sqlite3_file* file,"
    )
    rooted_vfs_registration = function_body(
        path_security, "register_sqlite_descriptor_rooted_vfs_or_throw("
    )
    rooted_vfs_context_throw = function_body(
        path_security, "void require_current_context_or_throw("
    )
    rooted_vfs_context_noexcept = function_body(
        path_security, "void require_current_context_noexcept() const noexcept"
    )
    rooted_vfs_parent_bridge = function_body(
        path_security,
        "[[nodiscard]] bool retained_parent_bridge_is_current_noexcept()",
    )
    rooted_vfs_retained_main = function_body(
        path_security,
        "[[nodiscard]] FamilyMemberIdentity retained_main_observation_or_throw(",
    )
    rooted_vfs_member_safe = function_body(
        path_security,
        "[[nodiscard]] bool current_member_is_safe_noexcept(",
    )
    rooted_vfs_map_path = function_body(
        path_security,
        "[[nodiscard]] bool map_path_noexcept(",
    )
    relative_mount_observer = function_body(
        directory_resolution_source,
        "sync_posix_observe_relative_mount_noexcept(",
    )
    require(
        "enum class DatabaseOpenDisposition" in source
        and "ExistingOperational = 1U" in source
        and "ExistingBootstrapCandidate = 2U" in source
        and "DatabaseOpenDisposition disposition" in open_helper
        and "= DatabaseOpenDisposition" not in open_helper.split("{", 1)[0]
        and "ProductSqliteDatabaseAuthority open_database_or_throw(" in source,
        "every_database_open_requires_explicit_disposition",
        "no product call site may inherit creation authority from a default",
    )
    require(
        source.count("sqlite3_open_v2(") == 2
        and "SQLITE_OPEN_CREATE" not in open_helper
        and 'sqlite3_open_v2(\n        logical_path.string().c_str()' in open_helper
        and "database.vfs_name_or_throw(label)" in open_helper
        and 'sqlite3_open_v2(\n        ":memory:"' in detached_open
        and "SQLITE_OPEN_CREATE" in detached_open
        and "SQLITE_OPEN_MEMORY" in detached_open
        and ordered(
            detached_open,
            "int flags = SQLITE_OPEN_READWRITE",
            "SQLITE_OPEN_CREATE",
            "SQLITE_OPEN_MEMORY",
            "sqlite3_open_v2",
            '":memory:",',
            "sqlite3_db_filename",
            "detached bootstrap database names a file",
        ),
        "filesystem_open_never_creates_and_create_is_detached_only",
        "selected paths are existing-only; SQLite CREATE is confined to one anonymous bootstrap image",
    )
    require(
        ordered(
            candidate_owner,
            "~UnadoptedSqliteConnection() noexcept",
            "sqlite3_close(handle_)",
            "sqlite3_close_v2(handle_)",
            "sqlite3* release() noexcept",
            "int close_noexcept() noexcept",
        )
        and ordered(
            reject_helper,
            "UnadoptedSqliteConnection& candidate",
            "candidate.close_noexcept()",
            "throw std::runtime_error(std::move(message))",
        )
        and ordered(
            open_helper,
            "ProductSqliteDatabaseAuthority database(",
            "UnadoptedSqliteConnection candidate",
            "sqlite3_open_v2",
            "if (opened != SQLITE_OK)",
            "reject_unadopted_database_handle_or_throw",
            "if (candidate.get() == nullptr)",
            'sqlite3_db_readonly(candidate.get(), "main")',
            "if (read_only != 0)",
            "reject_unadopted_database_handle_or_throw",
            "database.db.out()",
            "*destination = candidate.release()",
            "post-open path attestation",
        ),
        "only_exception_safe_successful_writable_handles_cross_strict_owner_adoption",
        "failed and read-only handles close before strict owner adoption and post-open identity proof",
    )
    require(
        ordered(
            product_authority,
            "SqlitePathFamilyGuard path_guard_",
            "unique_ptr<anonsync::SqliteDescriptorRootedVfs> rooted_vfs_",
            "SyncSqliteDbHandleSlot db",
        )
        and ordered(
            product_authority,
            "db = anonsync::SyncSqliteDbHandleSlot{}",
            "rooted_vfs_.reset()",
            "path_guard_ = anonsync::SqlitePathFamilyGuard{}",
        )
        and ordered(
            product_authority,
            "rooted_vfs_->verify_open_database_or_throw",
            "path_guard_.verify_open_database_or_throw",
        )
        and "rooted_vfs_->name()" in product_authority
        and "rooted_vfs_->read_bounded_main_file_or_throw" in product_authority
        and "rooted_vfs_->verify_sidecars_absent_or_throw" in product_authority
        and "rooted_vfs_->verify_sidecar_absent_or_throw" in product_authority
        and "rooted_vfs_->sync_main_file_and_parent_directory_or_throw"
        in product_authority,
        "descriptor_rooted_vfs_lifetime_is_connection_bound",
        "connection closes before its private VFS unregisters and retained path authority releases",
    )
    require(
        "anonsync_sqlite_path_security" in cmake
        and ordered(
            cmake,
            "target_link_libraries(anonsync_replica PRIVATE",
            "anonsync_sqlite_snapshot_seal",
            "anonsync_sqlite_path_security",
        ),
        "product_directly_links_descriptor_rooted_path_authority",
        "the product executable does not rely on an incidental transitive static-library edge",
    )
    require(
        "SQLITE_OPEN_NOFOLLOW" in open_helper
        and "guard_sqlite_path_family_or_throw" in open_helper
        and "register_sqlite_descriptor_rooted_vfs_or_throw" in open_helper
        and open_helper.count("verify_open_database_or_throw") >= 2
        and "sqlite_set_busy_timeout_or_throw" in open_helper
        and "require_wal_journal_mode_or_throw" in operational_profile
        and "PRAGMA synchronous=FULL;" in operational_profile
        and "PRAGMA wal_autocheckpoint=1;" in operational_profile
        and "PRAGMA temp_store=MEMORY;" in operational_profile
        and "require_bootstrap_candidate_header_and_namespace_or_throw" in open_helper
        and "read_bounded_main_file_before_open_or_throw" in candidate_preflight
        and "require_sealed_rollback_sidecars_absent_or_throw" in candidate_preflight
        and "verify_sidecar_absent_or_throw" in candidate_preflight
        and "PRAGMA main.locking_mode=EXCLUSIVE;" in candidate_lock,
        "successful_opens_retain_reviewed_path_and_durability_profile",
        "operational opens retain one descriptor-rooted family authority; bootstrap candidates preflight and lock it",
    )
    require(
        rooted_vfs_open
        and ordered(
            rooted_vfs_open,
            "if (name == nullptr || *name == '\\0')",
            "anonymous SQLite disk files are outside descriptor-rooted",
            "return reject_unopened_file(SQLITE_CANTOPEN)",
            "FamilyMember member = FamilyMember::Main",
            "state.map_path_noexcept(name, mapped, member)",
            "open_role_matches_member(member, flags)",
            "const bool is_main_database = member == FamilyMember::Main",
            "state.current_member_is_safe_noexcept",
            "member, !is_main_database",
            "const int delegated_flags = flags | SQLITE_OPEN_NOFOLLOW",
            "state.base->xOpen",
            "state.opened_member_matches_retained_name_noexcept",
        )
        and "state.base->xOpen(\n            state.base, wrapped->retained_path"
        in rooted_vfs_open
        and "local_error_slot_noexcept" in path_security
        and "supported_methods_version" in path_security
        and "observed.st_nlink != 1" in path_security
        and "SQLITE_FCNTL_HAS_MOVED" in path_security
        and "deleting the descriptor-rooted main database is forbidden"
        in path_security,
        "private_vfs_rejects_temp_spill_and_binds_each_opened_family_name",
        "anonymous disk files fail closed and every delegated Unix handle must retain a single-linked reviewed name",
    )
    require(
        rooted_vfs_map_path
        and "const std::string*& mapped" in rooted_vfs_map_path
        and "logical_family_paths" in rooted_vfs_map_path
        and "descriptor_family_paths" in rooted_vfs_map_path
        and ".reserve(" not in rooted_vfs_map_path
        and ".append(" not in rooted_vfs_map_path
        and "sqlite3_malloc" not in rooted_vfs_open
        and "sqlite3_free(wrapped.retained_path)" not in rooted_vfs_close
        and ordered(
            rooted_vfs_open,
            "const std::string* mapped = nullptr",
            "state.map_path_noexcept(name, mapped, member)",
            "wrapped->retained_path = mapped->c_str()",
            "state.base->xOpen",
        )
        and "std::array<std::string, 4U> family_basenames" in path_security
        and "std::array<std::string, 4U> logical_family_paths" in path_security
        and "std::array<std::string, 4U> descriptor_family_paths" in path_security,
        "vfs_family_paths_are_precomputed_and_allocation_free_at_callbacks",
        "four immutable logical, basename, and descriptor-rooted paths are owned by registration state instead of rebuilt or heap-retained for every SQLite callback",
    )
    require(
        "must not be used while any SQLite connection in this process may hold"
        in path_security_header
        and "closing any independently opened" in path_security_header
        and "open_readonly_file_or_throw" not in source,
        "raw_main_descriptor_open_is_offline_only_and_absent_from_product_spine",
        "the legacy guarded descriptor primitive documents POSIX lock revocation and the product uses only lock-aware pre-open or exact live sqlite3_file evidence",
    )
    require(
        rooted_vfs_open
        and ordered(
            rooted_vfs_open,
            "if ((flags & SQLITE_OPEN_URI) != 0)",
            "if ((flags & SQLITE_OPEN_DELETEONCLOSE) != 0)",
            "delete-on-close files are outside descriptor-rooted authority",
            "state.map_path_noexcept(name, mapped, member)",
            "state.base->xOpen",
        )
        and "descriptor-rooted SQLite VFS rejects named delete-on-close authority"
        in process_authority_test,
        "private_vfs_rejects_named_delete_on_close_before_delegation",
        "reviewed main, journal, and WAL members cannot acquire deferred unlink authority through xClose",
    )
    require(
        rooted_vfs_verify
        and ordered(
            rooted_vfs_verify,
            "SyncSqliteDatabaseMutexGuard database_lock",
            "main_file_for_database_or_throw",
        )
        and rooted_vfs_main_file
        and ordered(
            rooted_vfs_main_file,
            "verify_retained_namespace_or_throw",
            "sqlite3_db_filename",
            "SQLITE_FCNTL_VFS_POINTER",
            "opened_vfs != &vfs",
            "SQLITE_FCNTL_FILE_POINTER",
            "reinterpret_cast<WrappedFile*>",
            "wrapped->state != this",
            "opened_member_matches_retained_name_noexcept",
        )
        and "exact private VFS" in rooted_vfs_main_file
        and "descriptor-rooted connection proof" in product_authority
        and "logical-path authority proof" in product_authority,
        "live_connections_require_exact_vfs_and_independent_logical_path_proofs",
        "the connection mutex guards exact VFS/file-pointer attestation and a same-path connection through another VFS cannot satisfy product authority",
    )
    require(
        rooted_vfs_shm_map
        and ordered(
            rooted_vfs_shm_map,
            "FamilyMember::SharedMemory, true",
            "xShmMap",
            "FamilyMember::SharedMemory, false",
            "xShmUnmap",
            "SQLITE_IOERR_SHMOPEN",
        )
        and rooted_vfs_shm_unmap
        and ordered(
            rooted_vfs_shm_unmap,
            "FamilyMember::SharedMemory, true",
            "xShmUnmap",
            "FamilyMember::SharedMemory, true",
            "SQLITE_IOERR_SHMOPEN",
        )
        and "refusing to delete an unsafe SQLite sidecar name" in path_security
        and "SQLite family name is neither absent nor a single-linked" in path_security
        and "shared-memory name is outside descriptor-rooted" in path_security,
        "sidecar_callbacks_reject_multiply_linked_names_before_delegation",
        "journal, WAL, and shared-memory names cannot redirect writes through pre-existing hard links",
    )
    require(
        rooted_vfs_close
        and ordered(
            rooted_vfs_close,
            "WrappedFile& wrapped = from_context(file)",
            "wrapped.member == FamilyMember::Main",
            "current_main_path_matches_retained_identity_noexcept",
            "FamilyMember::SharedMemory, true",
            "fail_stop_on_sync_process_capability_violation_noexcept",
            "methods->xClose",
        )
        and all(
            token in process_authority_test
            for token in (
                "descriptor-rooted xClose rejects unsafe shared-memory replacement",
                "xClose fail-stop preserves the hostile shared-memory name",
                "xClose fail-stop leaves foreign bytes unchanged",
            )
        ),
        "close_revalidates_pathful_cleanup_before_unix_vfs_delegation",
        "a late hostile SHM replacement fail-stops before delegated xClose can unlink a foreign family name",
    )
    require(
        rooted_vfs_file_control
        and ordered(
            rooted_vfs_file_control,
            "SQLITE_FCNTL_TEMPFILENAME",
            "temporary filename generation is outside descriptor-rooted",
            "SQLITE_FCNTL_NULL_IO",
            "descriptor invalidation is outside descriptor-rooted authority",
            "SQLITE_FCNTL_SET_LOCKPROXYFILE",
            "lock-proxy path selection is outside descriptor-rooted authority",
            "delegated_file_control_requires_argument(operation)",
            "file-control operation requires a non-null argument",
            "return SQLITE_MISUSE",
        )
        and "delegated_file_control_requires_argument" in path_security
        and all(
            token in process_authority_test
            for token in (
                "denies ambient temporary-filename generation",
                "denies delegated NULL_IO descriptor invalidation",
                "denies lock-proxy pathname authority",
                "rejects malformed null arguments before Unix VFS delegation",
                "denied NULL_IO leaves the attested SQLite descriptor usable",
            )
        )
        and "xFileControl likewise denies ambient temporary-name generation"
        in path_security_header,
        "file_control_cannot_escape_or_invalidate_descriptor_authority",
        "ambient temp paths, lock-proxy paths, NULL_IO closure, and null-pointer delegation are denied at the private VFS boundary",
    )
    require(
        rooted_vfs_file_from
        and "require_current_process_noexcept" in rooted_vfs_file_from
        and "require_current_context_noexcept" not in rooted_vfs_file_from
        and rooted_vfs_file_from_context
        and ordered(
            rooted_vfs_file_from_context,
            "WrappedFile& wrapped = from(file)",
            "require_current_context_noexcept",
        )
        and all(
            "WrappedFile& wrapped = from(file)" in body
            and "from_context(file)" not in body
            for body in (
                rooted_vfs_read,
                rooted_vfs_write,
                rooted_vfs_sync,
                rooted_vfs_lock,
            )
        )
        and all(
            "WrappedFile& wrapped = from_context(file)" in body
            for body in (
                rooted_vfs_close,
                rooted_vfs_file_control,
                rooted_vfs_shm_map,
                rooted_vfs_shm_unmap,
            )
        )
        and "Most sqlite3_io_methods operate only on an already-open descriptor"
        in path_security
        and "Mount-namespace identity is re-proved at pathname-resolution frontiers"
        in path_security_header
        and "pay only the process-incarnation" in path_security_header,
        "mount_namespace_attestation_is_scoped_to_resolution_frontiers",
        "page I/O and lock hot paths keep process authority without reopening procfs namespace handles per callback",
    )
    require(
        rooted_vfs_parent_bridge
        and ordered(
            rooted_vfs_parent_bridge,
            "::fstat(parent_fd",
            "device_value(retained) != parent_device",
            "::stat(descriptor_prefix.c_str()",
            "device_value(bridged) != parent_device",
            "inode_value(bridged) != parent_inode",
            "sync_posix_capture_mount_identity_or_throw",
            "retained_parent_mount",
        )
        and all(
            ordered(
                body,
                "mount_namespace_authority.verify_or_throw",
                "retained_parent_bridge_is_current_noexcept",
            )
            for body in (rooted_vfs_context_throw, rooted_vfs_context_noexcept)
        )
        and "exact retained parent descriptor" in path_security_header
        and "descriptor-rooted VFS fail-stops after retained parent descriptor loss"
        in process_authority_test,
        "path_frontiers_reprove_retained_descriptor_and_procfs_bridge",
        "mount identity cannot mask an overmounted procfs bridge or a closed-and-reused parent descriptor",
    )
    require(
        relative_mount_observer
        and ordered(
            relative_mount_observer,
            "AT_SYMLINK_NOFOLLOW",
            "requested_mount_identity_mask",
            "statx_mount_identity_returned",
            "SyncPosixMountIdentity observed",
            "Disposition::DifferentMount",
        )
        and "::open" not in relative_mount_observer
        and "::close" not in relative_mount_observer
        and "process-associated locks" in directory_resolution_header
        and rooted_vfs_member_safe
        and ordered(
            rooted_vfs_member_safe,
            "::fstatat",
            "observed.st_nlink != 1",
            "sync_posix_observe_relative_mount_noexcept",
            "SyncPosixRelativeMountDisposition::RetainedMount",
            "member == FamilyMember::Main",
        )
        and rooted_vfs_retained_main
        and ordered(
            rooted_vfs_retained_main,
            "inspect_family_member_or_throw",
            "SQLite main pathname no longer names the retained file",
            "sync_posix_observe_relative_mount_noexcept",
            "SyncPosixRelativeMountDisposition::RetainedMount",
            "SQLite main pathname crossed the retained parent mount",
        )
        and rooted_vfs_registration
        and ordered(
            rooted_vfs_registration,
            "sync_posix_probe_directory_resolution_capability_or_throw",
            "sync_posix_directory_resolution_uses_statx_mount_id",
            "sync_posix_capture_mount_identity_or_throw",
            "retained_parent_mount",
            "inspect_family_member_or_throw",
            "sync_posix_observe_relative_mount_noexcept",
            "SQLite main file crosses the retained parent mount",
        )
        and ordered(
            cmake,
            "target_link_libraries(anonsync_sqlite_path_security PUBLIC",
            "anonsync_sync_posix_directory_resolution",
            "anonsync_sync_posix_mount_namespace_authority",
        )
        and all(
            token in directory_resolution_test
            for token in (
                "allocation-free relative mount observation accepts a same-mount member",
                "allocation-free relative observer detects the same-st_dev /proc/bus mount crossing",
            )
        )
        and all(
            token in process_authority_test
            for token in (
                "same-namespace bind-mount family witness",
                "authority rejects same-namespace bind-mounted WAL and exact-inode main names",
                "same-inode main bind-mount namespace proof",
                "same-namespace bind-mount rejection preserves foreign bytes",
            )
        ),
        "same_namespace_mount_family_is_frozen_without_lock_revoking_descriptor",
        "statx rejects same-device bind-mounted SQLite members without opening or closing a lock-bearing inode",
    )
    require(
        "SyncPosixMountNamespaceAuthority mount_namespace_authority"
        in path_security
        and "SyncPosixMountNamespaceAuthority::capture_or_throw"
        in path_security
        and ordered(
            path_security,
            "mount namespace before descriptor capture",
            "retained parent descriptor duplication",
            "retained descriptor procfs resolution",
            "mount namespace after procfs descriptor proof",
            "sqlite3_vfs_register",
        )
        and "mutable std::atomic<bool> revoked_{false}"
        in mount_namespace_header
        and "revoked_.load(std::memory_order_acquire)"
        in mount_namespace_source
        and "revoked_.store(true, std::memory_order_release)"
        in mount_namespace_source
        and "other.revoked_.exchange(false, std::memory_order_acq_rel)"
        in mount_namespace_source
        and ordered(
            cmake,
            "add_library(anonsync_sync_posix_mount_namespace_authority STATIC",
            "add_library(anonsync_sqlite_path_security STATIC",
            "target_link_libraries(anonsync_sqlite_path_security PUBLIC",
            "anonsync_sync_posix_mount_namespace_authority",
        )
        and rooted_vfs_registration
        and ordered(
            rooted_vfs_registration,
            "SyncPosixMountNamespaceAuthority::capture_or_throw",
            "mount namespace before descriptor capture",
            '"/proc/self/fd/"',
            "::stat(descriptor_directory.c_str()",
            "mount namespace after procfs descriptor proof",
            "sqlite3_vfs_register",
        ),
        "mount_namespace_authority_is_captured_before_procfd_and_revocation_is_atomic",
        "the procfd mapping is bracketed by one retained namespace identity and concurrent sticky revocation has no plain-bool race",
    )
    require(
        "dynamic extension loading is outside descriptor-rooted authority"
        in path_security
        and ordered(
            path_security,
            "state->vfs.xDlOpen",
            "State::dynamic_open",
            "state->vfs.xDlError",
            "State::dynamic_error",
            "state->vfs.xDlSym",
            "State::dynamic_symbol",
            "state->vfs.xDlClose",
            "State::dynamic_close",
            "state->vfs.xSetSystemCall = nullptr",
            "state->vfs.xGetSystemCall = nullptr",
            "state->vfs.xNextSystemCall = nullptr",
        )
        and "narrows dynamic loading and syscall replacement capabilities"
        in process_authority_test
        and "rejects extension loading locally without delegation"
        in process_authority_test,
        "private_vfs_denies_extension_and_syscall_table_escape_hatches",
        "copied base-VFS callbacks cannot inherit wrapper pAppData or process-global mutation authority",
    )
    require(
        ordered(
            candidate_promotion,
            "database_journal_mode_or_throw(database.db",
            'if (mode == "delete")',
            "require_sealed_rollback_sidecars_absent_or_throw",
            "SyncSqliteTransaction pin(",
            "acquire_bootstrap_candidate_read_lock_or_throw",
            "exact sealed image before durability flush",
            "database.sync_main_file_and_parent_directory_or_throw",
            "exact sealed image after durability flush",
            "if (exact_before != exact_after)",
            "pin.commit()",
            "PRAGMA main.journal_mode=WAL;",
            "configure_operational_database_profile_or_throw(database.db",
            "post-promotion binding",
            "post-promotion path attestation",
        )
        and rooted_vfs_preopen_read
        and ordered(
            rooted_vfs_preopen_read,
            "file_lifecycle_mutex",
            "open_files.load",
            "base->xOpen",
            "SQLITE_OPEN_READONLY",
            "read_file_through_sqlite_or_throw",
            "file->pMethods->xClose",
        )
        and rooted_vfs_live_read
        and ordered(
            rooted_vfs_live_read,
            "main_file_for_database_or_throw",
            "read_file_through_sqlite_or_throw",
        )
        and rooted_vfs_live_sync
        and ordered(
            rooted_vfs_live_sync,
            "main_file_for_database_or_throw",
            "file->pMethods->xSync",
            "::fsync(parent_fd)",
        )
        and "int main_fd" not in path_security
        and "state->main_fd" not in rooted_vfs_registration
        and "SyncSqliteDatabaseMutexGuard database_lock" in path_security
        and all(
            token in process_authority_test
            for token in (
                "primary SQLite RESERVED lock is present before auxiliary inspection",
                "auxiliary VFS pre-open read uses SQLite lock-aware close semantics",
                "auxiliary pre-open read preserves the primary SQLite RESERVED lock",
                "auxiliary VFS rejects an undersized pre-open read limit",
                "failed auxiliary pre-open read cleanup preserves the primary SQLite RESERVED lock",
                "auxiliary VFS teardown preserves the primary SQLite RESERVED lock",
                "rollback and primary close release the SQLite RESERVED lock",
                "auxiliary_vfs.reset()",
            )
        )
        and "read_sync_bounded_single_link_regular_file_no_symlink_or_throw"
        not in candidate_promotion
        and "reconcile_sync_immutable_file_create_new_no_symlink_or_throw"
        not in candidate_promotion,
        "bootstrap_durability_uses_live_sqlite_handle_without_auxiliary_close",
        "pre-open inspection stays inside the Unix VFS and live reads/fsyncs use the mutex-guarded SQLite main file, with a kernel-lock regression proving auxiliary authority teardown cannot cancel locks",
    )
    require(
        all(
            token in source
            for token in (
                "database_has_persistent_schema_or_throw",
                "SELECT 1 FROM main.sqlite_schema",
                "database_journal_mode_or_throw",
                "PRAGMA main.journal_mode;",
                "require_wal_journal_mode_or_throw",
            )
        )
        and ordered(
            open_helper,
            "guard_sqlite_path_family_or_throw",
            "database_existed_at_preflight",
            "register_sqlite_descriptor_rooted_vfs_or_throw",
            "ProductSqliteDatabaseAuthority database(",
            "require_bootstrap_candidate_header_and_namespace_or_throw",
            "int flags = SQLITE_OPEN_READWRITE",
            "sqlite3_open_v2",
            "sqlite3_db_readonly",
            "candidate.release()",
            "post-open path attestation",
            "retain_exclusive_bootstrap_candidate_locking_mode_or_throw",
            "const bool has_persistent_schema",
            "database_has_persistent_schema_or_throw",
            "if (!has_persistent_schema)",
            "has no persistent schema",
            "DatabaseOpenDisposition::ExistingOperational",
            "configure_operational_database_profile_or_throw",
            "database_journal_mode_or_throw",
            'mode != "delete" && mode != "wal"',
            "post-profile path attestation",
        ),
        "existing_paths_require_schema_and_explicit_operational_or_recovery_profile",
        "file existence cannot mint genesis; identity, schema, and operational/recovery profiles are distinct",
    )

    init = function_body(source, "int command_init(")
    init_resume = function_body(source, "int command_init_resume(")
    create_missing = function_body(
        source, "void create_missing_bootstrap_resources_or_throw("
    )
    sealed_create = function_body(
        source, "void create_sealed_bootstrap_database_or_throw("
    )
    status = function_body(source, "int command_status(")
    clock_observe = function_body(source, "int command_clock_observe(")
    clock_recover = function_body(source, "int command_clock_recover(")
    enqueue = function_body(source, "int command_enqueue_file(")
    membership = function_body(source, "int command_membership_publish(")
    send = function_body(source, "int command_send_one(")
    serve = function_body(source, "int command_serve_one(")
    operational_commands = (
        status,
        clock_observe,
        clock_recover,
        enqueue,
        membership,
        send,
        serve,
    )

    require(
        status.count("open_bound_operational_database_or_throw") == 4
        and "open_database_or_throw" not in status,
        "status_cannot_create_any_authority_store",
        "replica, effect, membership, and anchor observations require existing targets",
    )
    require(
        clock_observe.count("open_bound_operational_database_or_throw") == 1
        and clock_recover.count("open_bound_operational_database_or_throw") == 1
        and "open_database_or_throw" not in clock_observe + clock_recover,
        "clock_operations_require_existing_replica_authority",
        "clock observation and generation-fenced recovery cannot bootstrap a typo",
    )
    require(
        send.count("open_bound_operational_database_or_throw") == 1
        and "open_database_or_throw" not in send,
        "sender_requires_existing_replica_authority",
        "network dispatch cannot manufacture an empty sender store",
    )
    require(
        enqueue.count("open_bound_operational_database_or_throw") == 1
        and membership.count("open_bound_operational_database_or_throw") == 2
        and serve.count("open_bound_operational_database_or_throw") == 4
        and all("open_database_or_throw" not in body for body in operational_commands),
        "all_operational_commands_are_existing_only",
        "all product work paths lack SQLite genesis authority",
    )
    require(
        create_missing.count("create_sealed_bootstrap_database_or_throw") == 4
        and "DatabaseOpenDisposition::" not in create_missing
        and "open_database_or_throw" not in init
        and "open_database_or_throw" not in init_resume
        and init.count("create_missing_bootstrap_resources_or_throw") == 1
        and init_resume.count("create_missing_bootstrap_resources_or_throw") == 1
        and ordered(
            create_missing,
            "replica_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "effect_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "membership_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "anchor_database_present",
            "create_sealed_bootstrap_database_or_throw",
        )
        and ordered(
            sealed_create,
            "open_detached_bootstrap_database_or_throw",
            "initialize_detached_sqlite_deployment_binding_or_throw",
            "initialize_and_verify_role",
            "SealedSqliteSnapshot::capture_database",
            "require_fresh_database_family_or_throw",
            "publish_exact_copy_atomically_create_new_or_throw",
            "open_bound_bootstrap_candidate_or_throw",
            "promote_bound_bootstrap_candidate_to_operational_or_throw",
        )
        and ordered(
            init,
            "encode_sync_replica_deployment_manifest_or_throw",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "create_sync_replica_bootstrap_record_or_throw",
            "create_missing_bootstrap_resources_or_throw",
            "attest_complete_bootstrap_store_set_or_throw",
            "attest_sync_replica_bootstrap_record_unchanged_or_throw",
            "manifest_publication.publish_or_throw()",
        )
        and ordered(
            init_resume,
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "attest_existing_bootstrap_resource_identities_or_throw",
            "promote_existing_bootstrap_sqlite_authorities_or_throw",
            "attest_existing_bootstrap_role_state_or_throw",
            "advanced beyond bootstrap genesis",
            "existing = BootstrapExistingSqliteAuthorities{}",
            "create_missing_bootstrap_resources_or_throw",
            "attest_complete_bootstrap_store_set_or_throw",
            "manifest_publication.publish_or_throw()",
        )
        and "encoded bytes exceed the deployment-manifest read " in manifest
        and '"ceiling"' in manifest
        and "cannot be encoded as strict UTF-8 JSON" in manifest,
        "record_selected_sealed_genesis_is_the_only_database_creation_frontier",
        "fresh init and exact-record resume publish complete bound images while operational commands remain existing-only",
    )
    require(
        serve.count("open_bound_operational_database_or_throw") == 4
        and ordered(
            serve,
            "load_tls_context_or_throw",
            "make_listener_or_throw",
            "SyncReplicaSqliteDeploymentRole::TlsMembership",
            "membership database",
            "SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor",
            "membership anchor database",
            "current_authority_or_throw",
            "SyncReplicaSqliteDeploymentRole::Replica",
            "receiver database",
            "SyncReplicaSqliteDeploymentRole::FileEffect",
            "effect database",
        ),
        "serve_preflights_and_opens_every_authority_without_bootstrap",
        "TLS/listener and membership preflight cannot create or reach later stores on failure",
    )

    require(
        all(
            token in process_test
            for token in (
                "missing-deployment.json",
                "missing-manifest operation minted deployment or payload authority",
                "detach_database_family(",
                "existing-only enqueue",
                "failure path recreated detached database member",
            )
        ),
        "process_test_pins_failed_existing_only_open_without_creation",
        "real missing-manifest and detached-database failures prove no database family is minted",
    )
    require(
        all(
            token in process_test
            for token in (
                "unrelated.sqlite",
                "must be absent for fresh bootstrap",
                "bootstrap rewrote an unrelated persistent SQLite database",
                "orphan-sidecar bootstrap changed the database family",
                "failed wrong-profile bootstrap published a deployment manifest",
                '"manifest-collision bootstrap"',
            )
        ),
        "process_test_pins_explicit_bootstrap_and_wrong_profile_nonmutation",
        "the process refuses unrelated persistent stores and manifest collisions without side effects",
    )
    require(
        all(
            token in process_authority_test
            for token in (
                "same-path wrong-VFS attestation",
                "exact private VFS",
                "multiply-linked rollback journal",
                "multiply-linked family member",
                "multiply-linked foreign target",
                "multiply-linked shared memory before Unix open",
                "foreign bytes unchanged",
            )
        ),
        "process_test_pins_exact_vfs_and_hardlink_sidecar_rejection",
        "same-path VFS substitution and pre-existing journal or SHM hard links fail without foreign mutation",
    )
    require(
        all(
            token in process_test
            for token in (
                "detached-membership-database",
                "existing-only receiver preflight",
                "membership preflight reached the receiver replica database",
                "membership preflight reached the receiver effect database",
                "membership preflight reached the membership anchor",
            )
        ),
        "process_test_pins_serve_preflight_no_creation_or_later_store_access",
        "missing membership fails before receiver, effect, or anchor database access",
    )
    require(
        all(
            token in resume_process_test
            for token in (
                "foreign-binding rejection",
                "advanced beyond bootstrap genesis",
                "committed missing-store refusal",
                "orphan-sidecar refusal",
                "sealed rollback-image resume",
                "rollback-sidecar rejection",
                "unbound SQLite rejection",
                "assert_database_family_absent",
            )
        ),
        "resume_process_test_pins_no_creation_before_attestation_or_after_commit",
        "foreign, advanced, orphaned, and committed-missing states cannot mint a database family",
    )
    require(
        "audit_anonsync_replica_database_open_policy.py" in cmake
        and "anonsync_replica_database_open_policy_source_audit" in cmake,
        "database_open_policy_audit_is_registered",
        "the product targeting boundary runs in the normal CTest lane",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
