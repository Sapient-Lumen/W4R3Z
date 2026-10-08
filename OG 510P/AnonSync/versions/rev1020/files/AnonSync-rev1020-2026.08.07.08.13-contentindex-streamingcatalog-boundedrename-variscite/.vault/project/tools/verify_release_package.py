#!/usr/bin/env python3
"""Fail-closed verifier for a full-source AnonSync release directory or ZIP."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable

MANIFEST_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")
REVISION_RE = re.compile(r"^rev[0-9]{4}$")
PACKAGE_FILENAME_RE = re.compile(
    r"^AnonSync-(rev[0-9]{4})-"
    r"[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}-"
    r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.zip$")
ACTIVE_PROJECTION_V1_PREFIXES = ("include/", "src/", "tests/", "tools/", "third_party/")
ACTIVE_PROJECTION_V2_PREFIXES = (*ACTIVE_PROJECTION_V1_PREFIXES, "fuzz/")
ACTIVE_PROJECTION_V3_PREFIXES = (*ACTIVE_PROJECTION_V2_PREFIXES, "cmake/")
ACTIVE_PROJECTION_FIXED_FILES = {".gitignore", "CMakeLists.txt"}
ACTIVE_PROJECTION_LEGACY_V1_FORMAT = "anonsync-active-projection-v1"
ACTIVE_PROJECTION_V1_FORMAT = "anonsync-active-implementation-projection-v1"
ACTIVE_PROJECTION_V2_FORMAT = "anonsync-active-implementation-projection-v2"
ACTIVE_PROJECTION_V3_FORMAT = "anonsync-active-implementation-projection-v3"
SUPPORTED_ACTIVE_PROJECTION_FORMATS = {
    None,
    ACTIVE_PROJECTION_LEGACY_V1_FORMAT,
    ACTIVE_PROJECTION_V1_FORMAT,
    ACTIVE_PROJECTION_V2_FORMAT,
    ACTIVE_PROJECTION_V3_FORMAT,
}
FORBIDDEN_SUFFIXES = {
    ".a", ".o", ".obj", ".so", ".dylib", ".dll", ".exe", ".pdb", ".pyc",
    ".profraw", ".gcda", ".gcno", ".class",
}
FORBIDDEN_PARTS = {
    ".git", ".svn", "__pycache__", "CMakeFiles", "Testing", "node_modules",
}
FORBIDDEN_BASENAMES = {"CMakeCache.txt", "cmake_install.cmake", "core", "core.dump"}
FORBIDDEN_BUILD_DIRECTORY_BASENAMES = {"build"}
FORBIDDEN_BUILD_DIRECTORY_PREFIXES = ("build-", "cmake-build-")
BOOTSTRAP_WRAPPER_PROJECT_PREFIX = ".vault/project/"
BOOTSTRAP_WRAPPER_ALLOWED_ROOT_ENTRIES = {
    "BOOTSTRAPROSE.md",
    ".vault",
    ".h0p3",
}
BOOTSTRAP_WRAPPER_ALLOWED_VAULT_ENTRIES = {
    "README.md",
    "project",
    "parent",
    "source-objects",
    "witnesses",
}
BOOTSTRAP_WRAPPER_VAULT_DIRECTORY_ENTRIES = {
    "project",
    "parent",
    "source-objects",
    "witnesses",
}
BOOTSTRAP_WRAPPER_REQUIRED_FROM_REVISION = 908
BOOTSTRAP_RESTART_BINDING_REQUIRED_FROM_REVISION = 944


def ancestor_file_conflicts(
    entries: set[str],
    files: set[str],
) -> list[str]:
    """Return normalized paths whose ancestor is also represented as a file."""
    conflicts: list[str] = []
    for name in sorted(entries):
        parts = PurePosixPath(name).parts
        for depth in range(1, len(parts)):
            ancestor = PurePosixPath(*parts[:depth]).as_posix()
            if ancestor in files:
                conflicts.append(f"{ancestor} is a file ancestor of {name}")
                break
    return conflicts


def analyze_bootstrap_wrapper_layout(
    entries: set[str],
    files: set[str],
) -> tuple[set[str], list[str]]:
    """Return hidden project files and exact wrapper-policy violations.

    ``entries`` contains every normalized path beneath the one archive/directory
    root, including directories. ``files`` is its regular-file subset. The
    wrapper intentionally exposes one restart page and keeps the complete source
    under ``.vault/project``. Other ``.vault`` and ``.h0p3`` descendants are
    hidden donor/history material: they remain packaged but are not interpreted
    as the active source projection.
    """
    violations: list[str] = []
    root_entries = {
        PurePosixPath(name).parts[0]
        for name in entries
        if PurePosixPath(name).parts
    }
    unexpected_root = sorted(
        root_entries - BOOTSTRAP_WRAPPER_ALLOWED_ROOT_ENTRIES
    )
    if unexpected_root:
        violations.append(
            "unexpected release-root entries: " + ", ".join(unexpected_root)
        )
    if "BOOTSTRAPROSE.md" not in files:
        violations.append("BOOTSTRAPROSE.md is not a regular root file")
    if any(name.startswith("BOOTSTRAPROSE.md/") for name in entries):
        violations.append("BOOTSTRAPROSE.md is also used as a directory")
    if ".vault" in files:
        violations.append(".vault must be a hidden directory, not a file")
    if ".h0p3" in files:
        violations.append(".h0p3 must be a hidden directory, not a file")

    vault_entries = {
        PurePosixPath(name).parts[1]
        for name in entries
        if len(PurePosixPath(name).parts) >= 2
        and PurePosixPath(name).parts[0] == ".vault"
    }
    unexpected_vault = sorted(
        vault_entries - BOOTSTRAP_WRAPPER_ALLOWED_VAULT_ENTRIES
    )
    if unexpected_vault:
        violations.append(
            "unexpected .vault entries: " + ", ".join(unexpected_vault)
        )
    for basename in sorted(BOOTSTRAP_WRAPPER_VAULT_DIRECTORY_ENTRIES):
        candidate = f".vault/{basename}"
        if candidate in files:
            violations.append(candidate + " must be a directory, not a file")
    if ".vault/README.md" in entries and ".vault/README.md" not in files:
        violations.append(".vault/README.md must be a regular file, not a directory")

    project_names = {
        PurePosixPath(name).relative_to(".vault/project").as_posix()
        for name in files
        if name.startswith(BOOTSTRAP_WRAPPER_PROJECT_PREFIX)
    }
    project_present = (
        ".vault/project" in entries
        or any(
            name.startswith(BOOTSTRAP_WRAPPER_PROJECT_PREFIX)
            for name in entries
        )
    )
    if not project_present or not project_names:
        violations.append("hidden .vault/project source tree is absent")

    violations.extend(ancestor_file_conflicts(entries, files))
    return project_names, sorted(set(violations))


def wrapper_required_for_revision(expected_revision: str | None) -> bool:
    if expected_revision is None or not REVISION_RE.fullmatch(expected_revision):
        return False
    return (
        int(expected_revision.removeprefix("rev"))
        >= BOOTSTRAP_WRAPPER_REQUIRED_FROM_REVISION
    )


def is_forbidden_release_file(path: PurePosixPath) -> bool:
    """Return whether one normalized release file path is generated or binary.

    Every component except the final basename is known to be a directory because
    callers inventory files only.  Build-directory prefixes therefore apply to
    ``path.parts[:-1]`` and not to evidence or documentation filenames such as
    ``build-shape-observation.json``.
    """
    directory_parts = path.parts[:-1]
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        return True
    if any(
        part in FORBIDDEN_BUILD_DIRECTORY_BASENAMES
        or part.startswith(FORBIDDEN_BUILD_DIRECTORY_PREFIXES)
        for part in directory_parts
    ):
        return True
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    return path.name in FORBIDDEN_BASENAMES


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_active_projection(
    names: set[str],
    read: Callable[[str], bytes],
    *,
    projection_format: str | None,
) -> dict[str, object]:
    if projection_format == ACTIVE_PROJECTION_V3_FORMAT:
        prefixes = ACTIVE_PROJECTION_V3_PREFIXES
    elif projection_format == ACTIVE_PROJECTION_V2_FORMAT:
        prefixes = ACTIVE_PROJECTION_V2_PREFIXES
    else:
        prefixes = ACTIVE_PROJECTION_V1_PREFIXES
    active_names = sorted(
        name for name in names
        if name in ACTIVE_PROJECTION_FIXED_FILES or name.startswith(prefixes)
    )
    files: list[dict[str, object]] = []
    material = bytearray()
    total_bytes = 0
    for name in active_names:
        data = read(name)
        digest = sha256_bytes(data)
        total_bytes += len(data)
        files.append({"bytes": len(data), "path": name, "sha256": digest})
        material.extend(f"{digest}  {name}\n".encode("utf-8"))
    return {
        "bytes": total_bytes,
        "file_count": len(files),
        "files": files,
        "sha256": sha256_bytes(bytes(material)),
    }


def active_projection_format_allowed_for_revision(
    projection_format: str | None,
    revision_number: int | None,
) -> bool:
    """Return whether a declared projection generation meets the revision floor.

    Rev0905 made CMake modules active build authority, so that and every later
    revision must use v3. Older published packages retain their original v1/v2
    meaning and remain verifiable.
    """
    return revision_number is None or revision_number < 905 or (
        projection_format == ACTIVE_PROJECTION_V3_FORMAT
    )


def normalized_member(name: str) -> PurePosixPath:
    if "\\" in name or "\x00" in name:
        raise ValueError(f"unsafe archive member spelling: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe archive member path: {name!r}")
    # PurePosixPath deliberately normalizes repeated separators and dot
    # components. A release archive must not rely on that normalization: two
    # spellings that extract to one pathname are ambiguous input, not aliases.
    if path.as_posix() != name:
        raise ValueError(f"non-canonical archive member spelling: {name!r}")
    return path


def bootstrap_restart_page_binding_violations(
    release_gate: object,
    restart_page: bytes,
) -> list[str]:
    """Validate the visible restart page against hidden release authority.

    Rev0944 makes this binding mandatory. Older packages remain verifiable, but
    any older package that declares a binding must still declare it correctly.
    """
    if not isinstance(release_gate, dict):
        return ["RELEASE_GATE.json is not an object"]
    revision = release_gate.get("revision")
    revision_number = (
        int(revision.removeprefix("rev"))
        if isinstance(revision, str) and REVISION_RE.fullmatch(revision)
        else None
    )
    binding = release_gate.get("restart_page")
    required = (
        revision_number is not None
        and revision_number >= BOOTSTRAP_RESTART_BINDING_REQUIRED_FROM_REVISION
    )
    if binding is None and not required:
        return []
    if not isinstance(binding, dict):
        return ["release gate restart_page binding is absent or not an object"]

    violations: list[str] = []
    if binding.get("path") != "BOOTSTRAPROSE.md":
        violations.append("restart_page.path is not BOOTSTRAPROSE.md")
    declared_bytes = binding.get("bytes")
    if not isinstance(declared_bytes, int) or isinstance(declared_bytes, bool):
        violations.append("restart_page.bytes is not an integer")
    elif declared_bytes != len(restart_page):
        violations.append(
            f"restart_page.bytes={declared_bytes} actual={len(restart_page)}"
        )
    declared_sha256 = binding.get("sha256")
    actual_sha256 = sha256_bytes(restart_page)
    if (
        not isinstance(declared_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", declared_sha256) is None
    ):
        violations.append("restart_page.sha256 is not lowercase SHA-256")
    elif declared_sha256 != actual_sha256:
        violations.append(
            f"restart_page.sha256={declared_sha256} actual={actual_sha256}"
        )
    return violations


def parse_manifest(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"MANIFEST.sha256 is not UTF-8: {error}") from error
    result: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        match = MANIFEST_RE.fullmatch(line)
        if not match:
            raise ValueError(f"invalid manifest line {line_number}: {line!r}")
        digest, rel = match.groups()
        path = normalized_member(rel)
        canonical = path.as_posix()
        if canonical == "MANIFEST.sha256":
            raise ValueError("manifest must not recursively list itself")
        if canonical in result:
            raise ValueError(f"duplicate manifest path: {canonical}")
        result[canonical] = digest
    return result


def package_checks(names: set[str], read: Callable[[str], bytes], expected_revision: str | None) -> tuple[list[dict[str, object]], dict[str, object]]:
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    required = {
        "CMakeLists.txt",
        "README.md",
        "RELEASE_GATE.json",
        "MANIFEST.sha256",
        "include/anonsync_core.hpp",
        "include/anonsync_selftest_api.hpp",
        "src/sync_process_incarnation.hpp",
        "src/sync_process_incarnation_internal.hpp",
        "src/sync_process_incarnation.cpp",
        "src/sync_thread_incarnation.hpp",
        "src/sync_thread_incarnation.cpp",
        "src/sha256_digest.hpp",
        "src/sha256_digest.cpp",
        "src/sync_atomic_file_publication.hpp",
        "src/sync_atomic_file_publication_internal.hpp",
        "src/sync_atomic_file_publication_state.hpp",
        "src/sync_atomic_file_publication_state.cpp",
        "src/sync_atomic_file_publication.cpp",
        "src/sync_bounded_regular_file.hpp",
        "src/sync_bounded_regular_file.cpp",
        "src/sync_bounded_regular_file_limits.hpp",
        "src/sync_posix_descriptor_snapshot.hpp",
        "src/sync_posix_descriptor_snapshot.cpp",
        "src/persistence/local_jsonl_replay_publication.hpp",
        "src/persistence/local_jsonl_replay_publication.cpp",
        "src/persistence/local_jsonl_replay_directory_authority.hpp",
        "src/persistence/local_jsonl_replay_directory_authority.cpp",
        "src/persistence/local_jsonl_replay_namespace.hpp",
        "src/persistence/local_jsonl_replay_namespace.cpp",
        "src/sync_peer_ingress_schema.hpp",
        "src/sync_peer_ingress_schema.cpp",
        "src/sync_peer_ingress_payload_store_schema.cpp",
        "src/sync_peer_ingress_lifecycle.cpp",
        "src/sqlite_path_security.hpp",
        "src/sqlite_path_security.cpp",
        "src/persistence/sqlite_snapshot_seal.hpp",
        "src/persistence/sqlite_snapshot_seal.cpp",
        "src/persistence/sqlite_snapshot_geometry.hpp",
        "src/persistence/sqlite_snapshot_geometry.cpp",
        "src/persistence/sqlite_live_backup.hpp",
        "src/persistence/sqlite_live_backup.cpp",
        "src/persistence/sqlite_busy_handler_owner.hpp",
        "src/persistence/sqlite_busy_handler_owner.cpp",
        "src/persistence/sqlite_replay_ledger_write_gate.hpp",
        "src/persistence/sqlite_replay_ledger_write_gate.cpp",
        "src/persistence/sqlite_replay_ledger_restore_lock.hpp",
        "src/persistence/sqlite_replay_ledger_restore_lock.cpp",
        "src/persistence/sqlite_replay_ledger_reset.hpp",
        "src/persistence/sqlite_replay_ledger_reset.cpp",
        "src/persistence/sqlite_replay_ledger_reset_documents.hpp",
        "src/persistence/sqlite_replay_ledger_reset_documents.cpp",
        "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.hpp",
        "src/persistence/sqlite_replay_ledger_reset_receipt_protocol_internal.hpp",
        "src/persistence/sqlite_replay_ledger_reset_receipt_protocol.cpp",
        "src/persistence/sqlite_verification_budget.hpp",
        "src/persistence/sqlite_verification_budget.cpp",
        "tests/persistence/sqlite_verification_budget_tests.cpp",
        "tests/persistence/sqlite_snapshot_seal_tests.cpp",
        "tests/persistence/sqlite_busy_handler_owner_tests.cpp",
        "src/sync_sqlite_handle_slot.hpp",
        "src/sync_sqlite_handle_slot.cpp",
        "src/sync_sqlite_support.cpp",
        "src/sync_sqlite_connection_authority.cpp",
        "src/sync_sqlite_transaction.cpp",
        "src/sqlite_replay_ledger.cpp",
        "src/sqlite_replay_ledger_selftest_bridge.hpp",
        "tests/sqlite_replay_ledger_selftests.cpp",
        "tests/self_exec_test_process.hpp",
        "tests/self_exec_test_process.cpp",
        "tests/self_exec_test_process_test.cpp",
        "tests/test_process_topology_owner.hpp",
        "tests/test_process_topology_owner.cpp",
        "tests/test_process_topology_owner_test.cpp",
        "tests/inherited_test_process.hpp",
        "tests/inherited_test_process.cpp",
        "tests/inherited_test_process_test.cpp",
        "tests/process_incarnation_tests.cpp",
        "tests/thread_incarnation_tests.cpp",
        "tests/sqlite_process_authority_fork_test.cpp",
        "tests/sqlite_connection_authority_test.cpp",
        "tests/sqlite_owner_generation_borrow_test.cpp",
        "tests/sqlite_transaction_exception_composition_test.cpp",
        "tests/sqlite_transaction_allocator_fault_test.cpp",
        "tests/sqlite_source_first_move_test.cpp",
        "tests/sqlite_restore_namespace_authority_test.cpp",
        "tests/sqlite_backup_namespace_authority_test.cpp",
        "tests/sync_atomic_file_publication_test.cpp",
        "tests/sync_atomic_file_publication_prepared_test.cpp",
        "tests/sync_atomic_file_publication_state_test.cpp",
        "tests/sync_atomic_file_publication_cutpoint_test.cpp",
        "tests/sync_atomic_file_reconciliation_test.cpp",
        "tests/sync_atomic_file_publication_unlink_authority_test.cpp",
        "tests/sync_bounded_regular_file_test.cpp",
        "tests/sync_bounded_regular_file_syscall_test.cpp",
        "tests/persistence/local_jsonl_replay_publication_tests.cpp",
        "tests/persistence/local_jsonl_replay_directory_authority_tests.cpp",
        "tests/persistence/local_jsonl_replay_namespace_tests.cpp",
        "tests/local_jsonl_replay_backend_namespace_test.cpp",
        "tests/local_jsonl_replay_crash_state_machine_test.cpp",
        "tests/peer_ingress_schema_attestation_test.cpp",
        "tests/sync_peer_ingress_lifecycle_selftest_main.cpp",
        "tests/persistence/sqlite_persistence_process_authority_fork_test.cpp",
        "tests/persistence/sqlite_live_backup_tests.cpp",
        "tests/persistence/sqlite_replay_ledger_reset_tests.cpp",
        "tests/persistence/sqlite_replay_ledger_reset_fixture.hpp",
        "tests/persistence/sqlite_replay_ledger_reset_crash_frontier_test.cpp",
        "tests/persistence/sqlite_replay_ledger_reset_documents_tests.cpp",
        "tools/audit_self_exec_test_process.py",
        "tools/audit_inherited_test_process.py",
        "tools/audit_test_process_topology_owner.py",
        "tools/audit_raw_fork_boundaries.py",
        "tools/audit_runtime_selftest_separation.py",
        "tools/audit_sqlite_replay_ledger_selftest_separation.py",
        "tools/test_sqlite_replay_ledger_reset_cli.py",
        "tools/audit_sqlite_replay_ledger_reset.py",
        "tools/audit_sqlite_replay_ledger_reset_crash_frontier.py",
        "tools/audit_sqlite_replay_ledger_reset_receipt.py",
        "tools/audit_sqlite_replay_ledger_reset_receipt_protocol.py",
        "tools/audit_replay_ledger_load_authority.py",
        "tools/audit_sync_process_incarnation.py",
        "tools/audit_sync_thread_incarnation.py",
        "tools/audit_sqlite_process_authority.py",
        "tools/audit_sqlite_mutex_capability.py",
        "tools/audit_sqlite_owner_generation.py",
        "tools/audit_sqlite_transaction_stack_authority.py",
        "tools/audit_sqlite_transaction_exception_composition.py",
        "tools/audit_sqlite_transaction_allocator_fault.py",
        "tools/audit_sqlite_source_first_move.py",
        "tools/audit_sqlite_restore_publication.py",
        "tools/audit_sqlite_backup_publication.py",
        "tools/audit_sqlite_live_backup.py",
        "tools/audit_sqlite_snapshot_seal.py",
        "tools/audit_sqlite_verification_budget.py",
        "tools/audit_sqlite_busy_handler_owner.py",
        "tools/audit_sync_atomic_file_publication.py",
        "tools/audit_sync_bounded_regular_file.py",
        "tools/audit_local_jsonl_replay_crash_protocol.py",
        "tools/audit_peer_ingress_schema_owner_generation.py",
        "tools/verify_release_package.py",
    }
    missing = sorted(required - names)
    require(not missing, "required_files_present", "missing: " + ", ".join(missing) if missing else "all required source, test, audit, and release files are present")

    source_cpp = sorted(name for name in names if name.startswith("src/") and name.endswith((".cpp", ".cc", ".cxx")))
    source_headers = sorted(name for name in names if name.startswith(("src/", "include/")) and name.endswith((".h", ".hpp", ".hh", ".hxx")))
    tests = sorted(name for name in names if name.startswith("tests/") and name.endswith((".cpp", ".cc", ".cxx")))
    require(len(source_cpp) >= 20, "full_source_tree_present", f"production implementation files={len(source_cpp)} (minimum 20)")
    require(len(source_headers) >= 10, "full_header_tree_present", f"production header files={len(source_headers)} (minimum 10)")
    require(len(tests) >= 10, "full_test_tree_present", f"test implementation files={len(tests)} (minimum 10)")

    forbidden = sorted(
        name for name in names
        if is_forbidden_release_file(PurePosixPath(name))
    )
    require(not forbidden, "generated_and_binary_artifacts_absent", "forbidden entries: " + ", ".join(forbidden[:30]) if forbidden else "no VCS metadata, build trees, object files, binaries, or Python cache files")

    release_gate: dict[str, object] = {}
    try:
        release_gate = json.loads(read("RELEASE_GATE.json"))
        require(isinstance(release_gate, dict), "release_gate_is_json_object", "RELEASE_GATE.json parses as one object")
    except Exception as error:
        require(False, "release_gate_is_json_object", f"RELEASE_GATE.json parse failed: {error}")
    revision = str(release_gate.get("revision", "")) if isinstance(release_gate, dict) else ""
    require(bool(REVISION_RE.fullmatch(revision)), "release_gate_revision_is_canonical", f"revision={revision!r}")
    if expected_revision is not None:
        require(revision == expected_revision, "release_gate_revision_matches_expected", f"expected={expected_revision} actual={revision}")
    require(release_gate.get("required_gate_passed") is True, "required_release_gate_passed", "the package may not publish a failed or absent required gate")
    required_gate = release_gate.get("required") if isinstance(release_gate, dict) else None
    require(isinstance(required_gate, dict) and bool(required_gate) and all(value is True for value in required_gate.values()), "every_required_gate_entry_is_true", "all named required release conditions must be true")

    # Release verification must evolve without making the current verifier
    # reject a sealed parent that legitimately predates a newly mandatory
    # boundary.  Keep revision-scoped package members explicit rather than
    # weakening the global required inventory or relying on CMake to expose a
    # missing source file only during a later rebuild.
    revision_number = (
        int(revision.removeprefix("rev"))
        if REVISION_RE.fullmatch(revision)
        else None
    )
    revision_scoped_required: set[str] = set()
    if revision_number is not None and revision_number >= 895:
        try:
            readme_text = read("README.md").decode("utf-8")
            readme_heading = readme_text.splitlines()[0] if readme_text else ""
            require(
                readme_heading == f"# AnonSync {revision}",
                "readme_revision_matches_release_gate",
                f"expected='# AnonSync {revision}' actual={readme_heading!r}",
            )
        except Exception as error:
            require(False, "readme_revision_matches_release_gate", str(error))
        require(
            release_gate.get("artifact_revision") == revision,
            "artifact_revision_matches_release_gate",
            f"revision={revision!r} artifact_revision={release_gate.get('artifact_revision')!r}",
        )
        package_filename = release_gate.get("package_filename")
        filename_match = (
            PACKAGE_FILENAME_RE.fullmatch(package_filename)
            if isinstance(package_filename, str)
            else None
        )
        require(
            filename_match is not None and filename_match.group(1) == revision,
            "declared_package_filename_is_canonical",
            f"revision={revision!r} package_filename={package_filename!r}",
        )
    if revision_number is not None and revision_number >= 849:
        revision_scoped_required.update({
            "src/persistence/sqlite_retained_callback_claim.hpp",
            "src/persistence/sqlite_retained_callback_claim.cpp",
        })
    if revision_number is not None and revision_number >= 850:
        revision_scoped_required.update({
            "src/persistence/sqlite_authorizer_owner.hpp",
            "src/persistence/sqlite_authorizer_owner.cpp",
            "tests/persistence/sqlite_authorizer_owner_tests.cpp",
            "tools/audit_sqlite_authorizer_owner.py",
        })
    if revision_number is not None and revision_number >= 851:
        revision_scoped_required.update({
            "src/sync_sqlite_owned_authorizer_policy.hpp",
            "src/sync_sqlite_owned_authorizer_policy.cpp",
            "tests/sqlite_owned_authorizer_policy_test.cpp",
        })
    if revision_number is not None and revision_number >= 852:
        revision_scoped_required.update({
            "src/sync_sqlite_owned_authorizer_policy.hpp",
            "src/sync_sqlite_owned_authorizer_policy.cpp",
            "tests/sqlite_owned_authorizer_policy_test.cpp",
            "tests/sqlite_connection_authority_test.cpp",
            "tests/sqlite_transaction_exception_composition_test.cpp",
            "tools/audit_sqlite_authorizer_owner.py",
        })
    if revision_number is not None and revision_number >= 853:
        revision_scoped_required.update({
            "src/persistence/sqlite_retained_callback_slots.hpp",
        })
    if revision_number is not None and revision_number >= 854:
        revision_scoped_required.update({
            "src/sync_sqlite_database_mutex_guard.hpp",
            "src/sync_sqlite_database_mutex_guard.cpp",
            "tests/sqlite_support_test.cpp",
            "tests/persistence/sqlite_busy_handler_owner_tests.cpp",
            "tests/persistence/sqlite_verification_budget_tests.cpp",
            "tests/persistence/sqlite_authorizer_owner_tests.cpp",
            "tools/audit_sqlite_mutex_capability.py",
            "tools/audit_sqlite_busy_handler_owner.py",
            "tools/audit_sqlite_verification_budget.py",
            "tools/audit_sqlite_authorizer_owner.py",
            "tools/audit_sqlite_process_authority.py",
        })
    if revision_number is not None and revision_number >= 855:
        revision_scoped_required.update({
            "src/sync_sqlite_execution_affinity.hpp",
            "src/sync_sqlite_execution_affinity.cpp",
            "src/sync_sqlite_busy_timeout_mutation_guard.hpp",
            "src/sync_sqlite_busy_timeout_mutation_guard.cpp",
            "tests/sqlite_process_authority_fork_test.cpp",
        })
    if revision_number is not None and revision_number >= 856:
        revision_scoped_required.update({
            "src/sync_conflict_resolution.hpp",
            "src/sync_conflict_resolution.cpp",
            "tests/sync_conflict_resolution_test.cpp",
            "tests/sync_manifest_conflict_convergence_test.cpp",
            "tools/audit_sync_conflict_convergence.py",
        })
    if revision_number is not None and revision_number >= 857:
        revision_scoped_required.update({
            "src/security_tuple_digest.hpp",
            "src/security_tuple_digest.cpp",
            "src/sync_manifest_identity.hpp",
            "src/sync_manifest_identity.cpp",
            "tests/sync_manifest_identity_test.cpp",
            "tests/sync_manifest_hash_locale_test.cpp",
            "tools/audit_sync_manifest_identity.py",
        })
    if revision_number is not None and revision_number >= 858:
        revision_scoped_required.update({
            "src/sync_manifest_validation.hpp",
            "src/sync_manifest_validation.cpp",
            "tests/sync_manifest_validation_test.cpp",
            "tools/audit_sync_manifest_validation.py",
        })
    if revision_number is not None and revision_number >= 859:
        revision_scoped_required.update({
            "src/sync_manifest_stream_decoder.hpp",
            "src/sync_manifest_stream_decoder.cpp",
            "tests/sync_manifest_stream_decoder_test.cpp",
            "tools/audit_sync_manifest_stream_decoder.py",
        })
    if revision_number is not None and revision_number >= 860:
        revision_scoped_required.update({
            "src/sync_sqlite_manifest_chunk_subset.hpp",
            "src/sync_sqlite_manifest_chunk_subset.cpp",
            "tests/sync_sqlite_manifest_chunk_subset_test.cpp",
            "tools/audit_sync_sqlite_manifest_chunk_subset.py",
        })
    if revision_number is not None and revision_number >= 861:
        revision_scoped_required.update({
            "src/sync_sqlite_sidecar_claimed_path_snapshot.hpp",
            "src/sync_sqlite_sidecar_claimed_path_snapshot.cpp",
            "tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp",
            "tools/audit_sync_sqlite_sidecar_snapshot.py",
        })
    if revision_number is not None and revision_number >= 862:
        revision_scoped_required.update({
            "src/persistence/sqlite_verification_budget.hpp",
            "src/persistence/sqlite_verification_budget.cpp",
            "tools/audit_sqlite_verification_budget.py",
        })
    if revision_number is not None and revision_number >= 863:
        revision_scoped_required.update({
            "src/persistence/sqlite_busy_handler_owner.hpp",
            "src/persistence/sqlite_busy_handler_owner.cpp",
            "src/sync_sqlite_sidecar_claimed_path_snapshot.hpp",
            "src/sync_sqlite_sidecar_claimed_path_snapshot.cpp",
            "tests/persistence/sqlite_busy_handler_owner_tests.cpp",
            "tests/sync_sqlite_sidecar_claimed_path_snapshot_test.cpp",
            "tools/audit_sqlite_busy_handler_owner.py",
            "tools/audit_sync_sqlite_sidecar_snapshot.py",
        })
    if revision_number is not None and revision_number >= 864:
        revision_scoped_required.update({
            "src/sync_peer_transport_digest_bound_frame.hpp",
            "src/sync_peer_transport_digest_bound_frame.cpp",
            "tests/sync_peer_transport_digest_bound_frame_test.cpp",
        })
    if revision_number is not None and revision_number >= 865:
        revision_scoped_required.update({
            "src/sync_replica_model.hpp",
            "src/sync_replica_model.cpp",
            "src/sync_replica_network_simulator.hpp",
            "src/sync_replica_network_simulator.cpp",
            "tests/sync_replica_network_model_test.cpp",
        })
    if revision_number is not None and revision_number >= 866:
        revision_scoped_required.update({
            "src/sync_replica_operation_codec.cpp",
            "src/sync_replica_operation_codec_internal.hpp",
            "src/sync_replica_evidence_projection.cpp",
            "src/sync_replica_evidence_projection.hpp",
            "tests/sync_replica_hash_graph_projection_test.cpp",
            "tests/sync_replica_allocation_atomicity_test.cpp",
        })
    if revision_number is not None and revision_number >= 867:
        revision_scoped_required.update({
            "tests/sync_replica_aggregate_budget_test.cpp",
            "tools/audit_sync_replica_aggregate_budget.py",
        })
    if revision_number is not None and revision_number >= 868:
        revision_scoped_required.update({
            "tests/sync_replica_capacity_backpressure_test.cpp",
            "tools/audit_sync_replica_capacity_backpressure.py",
        })
    if revision_number is not None and revision_number >= 869:
        revision_scoped_required.update({
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tools/audit_sync_replica_sqlite_owner.py",
        })
    if revision_number is not None and revision_number >= 870:
        revision_scoped_required.update({
            "src/sync_replica_outbox_lease.hpp",
            "src/sync_replica_outbox_lease.cpp",
            "tests/sync_replica_outbox_lease_test.cpp",
            "tools/audit_sync_replica_outbox_lease.py",
            "RECEIPT_BOUND_OUTBOX_AUDIT_rev0870.md",
        })
    if revision_number is not None and revision_number >= 871:
        revision_scoped_required.update({
            "LEASE_HEARTBEAT_AUTHORITY_AUDIT_rev0871.md",
        })
    if revision_number is not None and revision_number >= 872:
        revision_scoped_required.update({
            "DURABLE_TIME_FENCE_AUDIT_rev0872.md",
        })
    if revision_number is not None and revision_number >= 873:
        revision_scoped_required.update({
            "RETRY_RELEASE_PROVENANCE_AUDIT_rev0873.md",
        })
    if revision_number == 873:
        revision_scoped_required.update({
            "src/sync_replica_outbox_time_fence.hpp",
            "src/sync_replica_outbox_time_fence.cpp",
            "tests/sync_replica_outbox_time_fence_test.cpp",
        })
    if revision_number is not None and revision_number >= 874:
        revision_scoped_required.update({
            "src/sync_replica_outbox_clock.hpp",
            "src/sync_replica_outbox_clock.cpp",
            "src/sync_replica_outbox_clock_linux.cpp",
            "tests/sync_replica_outbox_clock_test.cpp",
            "tools/audit_sync_replica_outbox_clock.py",
            "OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md",
        })
    if revision_number is not None and revision_number >= 875:
        revision_scoped_required.update({
            "src/sync_replica_outbox_clock_linux_internal.hpp",
            "TIME_NAMESPACE_CAPABILITY_AUDIT_rev0875.md",
        })
    if revision_number is not None and revision_number >= 876:
        revision_scoped_required.update({
            "src/sync_replica_delivery_protocol.hpp",
            "src/sync_replica_delivery_protocol.cpp",
            "src/sync_replica_delivery_service.hpp",
            "src/sync_replica_delivery_service.cpp",
            "src/sync_replica_tls_transport.hpp",
            "src/sync_replica_tls_transport.cpp",
            "tests/sync_replica_delivery_protocol_test.cpp",
            "tests/sync_replica_delivery_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "AUTHENTICATED_EVIDENCE_DELIVERY_AUDIT_rev0876.md",
        })
    if revision_number is not None and revision_number >= 877:
        revision_scoped_required.update({
            "src/sync_replica_delivery_channel.hpp",
            "src/sync_replica_delivery_channel.cpp",
            "tests/sync_replica_delivery_test_channel.hpp",
            "tests/sync_replica_delivery_test_channel.cpp",
            "tools/audit_sync_replica_delivery_channel.py",
            "AUTHENTICATED_CHANNEL_CAPABILITY_AUDIT_rev0877.md",
        })
    if revision_number is not None and revision_number >= 878:
        revision_scoped_required.update({
            "src/sync_replica_file_effect_identity.hpp",
            "src/sync_replica_file_effect_identity.cpp",
            "src/sync_replica_file_delivery_protocol.hpp",
            "src/sync_replica_file_delivery_protocol.cpp",
            "src/sync_replica_file_effect_sqlite_owner.hpp",
            "src/sync_replica_file_effect_sqlite_owner.cpp",
            "src/sync_replica_file_delivery_service.hpp",
            "src/sync_replica_file_delivery_service.cpp",
            "tests/sync_atomic_file_reconciliation_test.cpp",
            "tests/sync_replica_file_effect_sqlite_owner_test.cpp",
            "tests/sync_replica_file_delivery_protocol_test.cpp",
            "tests/sync_replica_file_delivery_service_test.cpp",
            "tools/audit_sync_replica_file_delivery.py",
            "EFFECT_TERMINAL_CUTPOINT_GUARD_AUDIT_rev0878.md",
        })
    if revision_number is not None and revision_number >= 879:
        revision_scoped_required.update({
            "src/sync_directory_authority.hpp",
            "src/sync_directory_authority.cpp",
            "tools/audit_sync_effect_root_authority.py",
            "ROOTED_EFFECT_DIRECTORY_AUTHORITY_AUDIT_rev0879.md",
        })
    if revision_number is not None and revision_number >= 880:
        revision_scoped_required.update({
            "src/sync_posix_directory_resolution.hpp",
            "src/sync_posix_directory_resolution.cpp",
            "tests/sync_posix_directory_resolution_test.cpp",
            "tools/audit_sync_mount_boundary_authority.py",
            "MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md",
        })
    if revision_number is not None and revision_number >= 881:
        revision_scoped_required.update({
            "src/sync_manifest_validation.hpp",
            "src/sync_manifest_validation.cpp",
            "src/sync_posix_mount_namespace_authority.hpp",
            "src/sync_posix_mount_namespace_authority.cpp",
            "src/sync_system_epoch_identity.hpp",
            "src/sync_system_epoch_identity.cpp",
            "tests/sync_manifest_validation_test.cpp",
            "tests/sync_system_epoch_identity_test.cpp",
            "tests/sync_replica_file_effect_sqlite_owner_test.cpp",
            "tests/sync_replica_file_delivery_protocol_test.cpp",
            "tests/sync_replica_file_delivery_service_test.cpp",
            "tools/audit_sync_file_effect_path_capability.py",
            "tools/audit_sync_outbox_dispatch_guard.py",
            "FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md",
            "OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md",
        })
    if revision_number is not None and revision_number >= 882:
        revision_scoped_required.update({
            "src/sync_replica_file_tls_dispatch.hpp",
            "src/sync_replica_file_tls_dispatch.cpp",
            "tools/audit_sync_file_tls_dispatch.py",
            "TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md",
        })
    if revision_number is not None and revision_number >= 883:
        revision_scoped_required.update({
            "TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md",
        })
    if revision_number is not None and revision_number >= 884:
        revision_scoped_required.update({
            "tools/audit_sync_tls_receive_continuation.py",
            "TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md",
        })
    if revision_number is not None and revision_number >= 885:
        revision_scoped_required.update({
            "src/sync_socket_readiness_identity.hpp",
            "src/sync_socket_readiness_identity.cpp",
            "tests/sync_socket_readiness_identity_test.cpp",
            "tools/audit_sync_socket_readiness_identity.py",
            "TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md",
        })
    if revision_number is not None and revision_number >= 886:
        revision_scoped_required.update({
            "src/sync_replica_tls_poll.hpp",
            "src/sync_replica_tls_poll.cpp",
            "tools/audit_sync_tls_transport_anchor.py",
            "tools/audit_sync_tls_write_continuation.py",
            "tools/audit_sync_tls_poll_owner.py",
            "tools/test_verify_release_package_policy.py",
            "TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md",
            "TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md",
            "TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md",
            "CLOUDTAINER_BUILD_RETENTION_AUDIT_rev0886.md",
            "REVISION_NOTES_rev0886.md",
        })
    if revision_number is not None and revision_number >= 887:
        revision_scoped_required.update({
            "src/sync_replica_file_delivery_service.hpp",
            "src/sync_replica_file_tls_dispatch.hpp",
            "src/sync_replica_file_tls_dispatch.cpp",
            "src/sync_replica_file_tls_exchange.hpp",
            "src/sync_replica_file_tls_exchange.cpp",
            "src/sync_replica_tls_io_policy.hpp",
            "src/sync_replica_tls_io_policy.cpp",
            "tests/sync_replica_tls_io_policy_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_file_tls_dispatch.py",
            "tools/audit_sync_file_tls_exchange.py",
            "tools/audit_sync_tls_io_policy.py",
            "TLS_FILE_DISPATCH_CONTINUATION_AUDIT_rev0887.md",
            "TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md",
            "TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md",
            "REVISION_NOTES_rev0887.md",
        })
    if revision_number is not None and revision_number >= 888:
        revision_scoped_required.update({
            "src/sync_replica_tls_transport.hpp",
            "src/sync_replica_tls_transport.cpp",
            "src/sync_replica_file_tls_exchange.hpp",
            "src/sync_replica_file_tls_exchange.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_tls_write_continuation.py",
            "tools/audit_sync_file_tls_exchange.py",
            "TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md",
            "SQLITE_CONNECTION_AUTHORITY_TEST_SYNCHRONIZATION_AUDIT_rev0888.md",
            "REVISION_NOTES_rev0888.md",
        })
    if revision_number is not None and revision_number >= 889:
        revision_scoped_required.update({
            "src/sync_replica_file_delivery_service.hpp",
            "src/sync_replica_file_delivery_service.cpp",
            "src/sync_replica_file_tls_exchange.hpp",
            "src/sync_replica_file_tls_exchange.cpp",
            "src/sync_stream_socket_deadline_poll.hpp",
            "src/sync_stream_socket_deadline_poll.cpp",
            "src/sync_replica_file_tls_server.hpp",
            "src/sync_replica_file_tls_server.cpp",
            "tests/sync_socket_readiness_identity_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_file_tls_exchange.py",
            "tools/audit_sync_file_tls_receiver_session.py",
            "tools/audit_sync_socket_readiness_identity.py",
            "tools/audit_sync_file_tls_server.py",
            "tools/audit_sync_file_effect_capacity_accounting.py",
            "TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md",
            "TLS_ACCEPTED_SESSION_AUTHORITY_AUDIT_rev0889.md",
            "RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md",
            "FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md",
            "FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md",
            "REVISION_NOTES_rev0889.md",
        })
    if revision_number is not None and revision_number >= 890:
        revision_scoped_required.update({
            "src/sync_replica_tls_membership_snapshot.hpp",
            "src/sync_replica_tls_membership_snapshot.cpp",
            "src/sync_replica_file_tls_server.hpp",
            "src/sync_replica_file_tls_server.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_tls_membership_snapshot.py",
            "tools/audit_authority_callback_boundaries.py",
            "tools/audit_sync_file_tls_server.py",
            "TLS_IMMUTABLE_MEMBERSHIP_SNAPSHOT_AUDIT_rev0890.md",
            "CALLBACK_AUTHORITY_BOUNDARY_AUDIT_rev0890.md",
            "REVISION_NOTES_rev0890.md",
        })
    if revision_number is not None and revision_number >= 891:
        revision_scoped_required.update({
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_sqlite_owner.cpp",
            "src/sync_replica_tls_membership_snapshot.hpp",
            "src/sync_replica_tls_membership_snapshot.cpp",
            "src/sync_replica_file_tls_server.hpp",
            "src/sync_replica_file_tls_server.cpp",
            "tests/sync_replica_tls_membership_sqlite_owner_test.hpp",
            "tests/sync_replica_tls_membership_sqlite_owner_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_tls_membership_sqlite_owner.py",
            "tools/audit_sync_tls_membership_snapshot.py",
            "tools/audit_sync_file_tls_server.py",
            "TLS_DURABLE_MEMBERSHIP_AUTHORITY_AUDIT_rev0891.md",
            "TLS_SERVER_CONTEXT_RETENTION_AUDIT_rev0891.md",
            "REVISION_NOTES_rev0891.md",
        })
    if revision_number is not None and revision_number >= 892:
        revision_scoped_required.update({
            "src/sync_replica_tls_policy_sqlite_profile.hpp",
            "src/sync_replica_tls_policy_sqlite_profile.cpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
            "src/sync_replica_tls_membership_anchored_owner.hpp",
            "src/sync_replica_tls_membership_anchored_owner.cpp",
            "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.hpp",
            "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp",
            "tools/audit_sync_tls_membership_anchor.py",
            "TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md",
            "src/sync_replica_file_content_inventory.hpp",
            "src/sync_replica_file_content_inventory.cpp",
            "src/sync_replica_file_payload_snapshot.hpp",
            "src/sync_replica_file_payload_snapshot.cpp",
            "src/sync_replica_file_delivery_service.hpp",
            "src/sync_replica_file_delivery_service.cpp",
            "tests/sync_replica_file_delivery_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_file_payload_snapshot.py",
            "tools/audit_authority_callback_boundaries.py",
            "tools/audit_sync_replica_file_delivery.py",
            "tools/audit_sync_file_effect_path_capability.py",
            "tools/audit_sync_outbox_dispatch_guard.py",
            "FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md",
            "REVISION_NOTES_rev0892.md",
        })
    if revision_number is not None and revision_number >= 893:
        revision_scoped_required.update({
            "src/sync_posix_directory_resolution.hpp",
            "src/sync_posix_directory_resolution.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_file_delivery_service.hpp",
            "src/sync_replica_file_delivery_service.cpp",
            "src/sync_replica_file_tls_dispatch.hpp",
            "src/sync_replica_file_tls_dispatch.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_file_delivery_service_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md",
            "REVISION_NOTES_rev0893.md",
        })
    if revision_number is not None and revision_number >= 894:
        revision_scoped_required.update({
            "src/sync_directory_authority_internal.hpp",
            "src/sync_directory_authority.cpp",
            "src/sync_atomic_file_publication.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "DURABLE_FILE_PAYLOAD_STORE_AUDIT_rev0893.md",
            "PAYLOAD_STORE_WRITER_LEASE_AUTHORITY_AUDIT_rev0894.md",
            "REVISION_NOTES_rev0894.md",
        })
    if revision_number is not None and revision_number >= 895:
        revision_scoped_required.update({
            "src/anonsync_replica.cpp",
            "src/sync_replica_file_tls_client.hpp",
            "src/sync_replica_file_tls_client.cpp",
            "tools/test_anonsync_replica_cli.py",
            "MISSION_PRODUCT_SPINE_ASSESSMENT_rev0895.md",
            "PRODUCT_SPINE_TLS_CLIENT_AUDIT_rev0895.md",
            "REVISION_NOTES_rev0895.md",
        })
    if revision_number is not None and revision_number >= 897:
        revision_scoped_required.update({
            "src/anonsync_replica.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tools/test_anonsync_replica_cli.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "PRODUCT_CLOCK_RECOVERY_AND_DATABASE_TARGET_AUDIT_rev0897.md",
            "REVISION_NOTES_rev0897.md",
        })
    if revision_number is not None and revision_number >= 898:
        revision_scoped_required.update({
            "include/anonsync_json_parser.hpp",
            "src/anonsync_json_parser.cpp",
            "src/anonsync_replica.cpp",
            "src/sync_replica_deployment_manifest.hpp",
            "src/sync_replica_deployment_manifest.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_deployment_manifest_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_replica_cli.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_anonsync_replica_bootstrap_authority.py",
            "tools/audit_sync_bounded_regular_file.py",
            "EXPLICIT_STORE_SET_BOOTSTRAP_AND_MANIFEST_AUTHORITY_AUDIT_rev0898.md",
            "REVISION_NOTES_rev0898.md",
        })
    if revision_number is not None and revision_number >= 899:
        revision_scoped_required.update({
            "src/sync_replica_deployment_identity.hpp",
            "src/sync_replica_deployment_identity.cpp",
            "src/sync_replica_deployment_binding.hpp",
            "src/sync_replica_deployment_binding.cpp",
            "src/sync_replica_deployment_manifest.hpp",
            "src/sync_replica_deployment_manifest.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_deployment_binding_test.cpp",
            "tests/sync_replica_deployment_manifest_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/test_anonsync_replica_cli.py",
            "tools/audit_anonsync_replica_deployment_binding.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_anonsync_replica_bootstrap_authority.py",
            "tools/audit_sync_file_payload_store.py",
            "STORE_SET_BIRTH_ATTESTATION_AND_FRESH_BOOTSTRAP_AUDIT_rev0899.md",
            "REVISION_NOTES_rev0899.md",
        })
    if revision_number is not None and revision_number >= 900:
        revision_scoped_required.update({
            "src/sync_replica_bootstrap_record.hpp",
            "src/sync_replica_bootstrap_record.cpp",
            "src/sync_replica_deployment_manifest.hpp",
            "src/sync_replica_deployment_manifest.cpp",
            "src/anonsync_replica.cpp",
            "tests/sync_replica_bootstrap_record_test.cpp",
            "tests/sync_replica_deployment_manifest_test.cpp",
            "tools/test_anonsync_replica_bootstrap_resume.py",
            "tools/audit_anonsync_replica_bootstrap_authority.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_anonsync_replica_deployment_binding.py",
            "CRASH_RECOVERABLE_BOOTSTRAP_RECORD_AND_IDEMPOTENT_RESUME_AUDIT_rev0900.md",
            "REVISION_NOTES_rev0900.md",
        })
    if revision_number is not None and revision_number >= 901:
        revision_scoped_required.update({
            "src/anonsync_replica.cpp",
            "src/persistence/sqlite_snapshot_seal.hpp",
            "src/persistence/sqlite_snapshot_seal.cpp",
            "src/sync_replica_deployment_binding.hpp",
            "src/sync_replica_deployment_binding.cpp",
            "src/sync_replica_tls_policy_sqlite_profile.hpp",
            "src/sync_replica_tls_policy_sqlite_profile.cpp",
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_sqlite_owner.cpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
            "tests/persistence/sqlite_snapshot_seal_tests.cpp",
            "tests/sync_replica_deployment_binding_test.cpp",
            "tests/sync_replica_tls_membership_sqlite_owner_test.cpp",
            "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp",
            "tools/test_anonsync_replica_bootstrap_resume.py",
            "tools/audit_anonsync_replica_bootstrap_authority.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_anonsync_replica_deployment_binding.py",
            "ATOMIC_SQLITE_GENESIS_IMAGE_AND_RECOVERY_ADMISSION_AUDIT_rev0901.md",
            "REVISION_NOTES_rev0901.md",
        })
    if revision_number is not None and revision_number >= 904:
        revision_scoped_required.update({
            "src/sqlite_path_security.hpp",
            "src/sqlite_path_security.cpp",
            "src/sync_posix_directory_resolution.hpp",
            "src/sync_posix_directory_resolution.cpp",
            "tests/persistence/sqlite_persistence_process_authority_fork_test.cpp",
            "tests/sync_posix_directory_resolution_test.cpp",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_sqlite_snapshot_seal.py",
            "SQLITE_DESCRIPTOR_ROOTED_LOCK_AND_MOUNT_FAMILY_AUTHORITY_AUDIT_rev0904.md",
            "REVISION_NOTES_rev0904.md",
        })
    if revision_number is not None and revision_number >= 905:
        revision_scoped_required.update({
            "cmake/AnonSyncBundledSqliteProfile.cmake",
            "cmake/AnonSyncVerifyBundledSqlite.cmake",
            "cmake/AnonSyncVerifyBundledSqliteAtBuild.cmake",
            "cmake/anonsync_bundled_sqlite_profile.hpp.in",
            "src/sync_sqlite_runtime.hpp",
            "src/sync_sqlite_runtime.cpp",
            "tests/sqlite_runtime_policy_test.cpp",
            "tests/sqlite_runtime_payload_store_test.cpp",
            "third_party/sqlite-3.53.3/UPSTREAM-PROVENANCE.md",
            "tools/verify_bundled_sqlite_profile.py",
            "tools/test_verify_bundled_sqlite_profile.py",
            "tools/test_bundled_sqlite_native_build_gate.py",
            "tools/test_active_implementation_projection.py",
            "BUNDLED_SQLITE_SINGLE_PROFILE_ATTESTATION_AUDIT_rev0905.md",
            "FORENSIC_STATUS_AND_SQLITE_FILENAME_FAMILY_AUTHORITY_AUDIT_rev0905.md",
            "REVISION_NOTES_rev0905.md",
        })
    if revision_number is not None and revision_number >= 907:
        revision_scoped_required.update({
            "src/sync_replica_session_supervisor.hpp",
            "src/sync_replica_session_supervisor.cpp",
            "tests/sync_replica_session_supervisor_test.cpp",
            "ABSOLUTE_COMMAND_DEADLINE_IDLE_CLOSE_PRECLAIM_AND_LEASE_HORIZON_AUDIT_rev0907.md",
            "REVISION_NOTES_rev0907.md",
        })
    if revision_number is not None and revision_number >= 908:
        revision_scoped_required.update({
            "src/sync_replica_stream_connector.hpp",
            "src/sync_replica_stream_connector.cpp",
            "tests/sync_replica_stream_connector_test.cpp",
            "tools/test_anonsync_replica_anonymous_routes.py",
            "RESILIO_REPLACEMENT_TOR_I2P_TRANSPORT_BOUNDARY_AUDIT_rev0908.md",
            "REVISION_NOTES_rev0908.md",
        })
    if revision_number is not None and revision_number >= 954:
        revision_scoped_required.update({
            "DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md",
            "REVISION_NOTES_rev0954.md",
            "src/sync_replica_file_payload_verification_index.hpp",
            "src/sync_replica_file_payload_verification_index.cpp",
            "tests/sync_replica_file_payload_verification_index_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/audit_sync_file_payload_store.py",
        })
    if revision_number is not None and revision_number >= 955:
        revision_scoped_required.update({
            "DURABLE_BYTE_BOUNDED_PAYLOAD_SCRUB_AUDIT_rev0955.md",
            "REVISION_NOTES_rev0955.md",
            "src/resumable_sha256.hpp",
            "src/resumable_sha256.cpp",
            "src/sync_replica_file_payload_scrub_state.hpp",
            "src/sync_replica_file_payload_scrub_state.cpp",
            "src/sync_posix_regular_file_snapshot_codec.hpp",
            "src/sync_posix_regular_file_snapshot_codec.cpp",
            "tests/resumable_sha256_test.cpp",
            "tests/sync_replica_file_payload_scrub_state_test.cpp",
            "tools/test_anonsync_service_process.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/test_anonsync_provisioning.py",
        })
    if revision_number is not None and revision_number >= 956:
        revision_scoped_required.update({
            "PAYLOAD_INTEGRITY_SERVICE_RECOVERY_AUDIT_rev0956.md",
            "REVISION_NOTES_rev0956.md",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_folder_process.hpp",
            "src/sync_replica_folder_process.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "src/sync_replica_tls_transport.hpp",
            "src/sync_replica_tls_transport.cpp",
            "src/anonsync_sync.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/audit_sync_file_payload_store.py",
        })
    if revision_number is not None and revision_number >= 957:
        revision_scoped_required.update({
            "PAYLOAD_REPROOF_HANDOFF_AND_EXACT_OWNER_AUDIT_rev0957.md",
            "REVISION_NOTES_rev0957.md",
            "CMakeLists.txt",
            "src/anonsync_folder.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_folder_process.hpp",
            "src/sync_replica_folder_process.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "src/sync_replica_peer_service_integrity_evidence.hpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_replica_peer_service_integrity_evidence_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
        })
    if revision_number is not None and revision_number >= 958:
        revision_scoped_required.update({
            "SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md",
            "REVISION_NOTES_rev0958.md",
            "src/sync_replica_file_payload_scrub_state.hpp",
            "src/sync_replica_file_payload_scrub_state.cpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_file_payload_scrub_state_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 959:
        revision_scoped_required.update({
            "MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md",
            "REVISION_NOTES_rev0959.md",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_replica_cli.py",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 960:
        revision_scoped_required.update({
            "OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md",
            "REVISION_NOTES_rev0960.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_folder_wake.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/test_anonsync_service_process.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 961:
        revision_scoped_required.update({
            "EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md",
            "REVISION_NOTES_rev0961.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 962:
        revision_scoped_required.update({
            "EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md",
            "REVISION_NOTES_rev0962.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 963:
        revision_scoped_required.update({
            "RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md",
            "REVISION_NOTES_rev0963.md",
            "src/anonsync_sync.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_folder_wake.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 964:
        revision_scoped_required.update({
            "BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md",
            "REVISION_NOTES_rev0964.md",
            "src/sync_replica_folder_observer.hpp",
            "src/sync_replica_folder_observer.cpp",
            "tests/sync_replica_folder_observer_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 965:
        revision_scoped_required.update({
            "GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md",
            "REVISION_NOTES_rev0965.md",
            "src/sync_replica_folder_observer.hpp",
            "src/sync_replica_folder_observer.cpp",
            "tests/sync_replica_folder_observer_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 966:
        revision_scoped_required.update({
            "EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md",
            "REVISION_NOTES_rev0966.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_model.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 967:
        revision_scoped_required.update({
            "PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md",
            "REVISION_NOTES_rev0967.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_model.hpp",
            "src/sync_replica_model.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_network_model_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 968:
        revision_scoped_required.update({
            "EXACT_CAUSAL_HISTORY_SOURCE_CUTPOINT_AUDIT_rev0968.md",
            "REVISION_NOTES_rev0968.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 969:
        revision_scoped_required.update({
            "EXACT_CURRENT_BOUND_HISTORICAL_RESTORE_AUDIT_rev0969.md",
            "REVISION_NOTES_rev0969.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/test_anonsync_sync_process.py",
            "tools/test_anonsync_replica_reconciliation_process.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 970:
        revision_scoped_required.update({
            "CAUSAL_METADATA_HISTORY_INSPECTION_AUDIT_rev0970.md",
            "REVISION_NOTES_rev0970.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 971:
        revision_scoped_required.update({
            "BOUNDED_HISTORICAL_STATUS_PAGE_AND_SINGLE_RESULT_AUDIT_rev0971.md",
            "REVISION_NOTES_rev0971.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.hpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 972:
        revision_scoped_required.update({
            "RETAINED_PAYLOAD_REACHABILITY_AND_CANONICAL_STATUS_FRONTIER_AUDIT_rev0972.md",
            "REVISION_NOTES_rev0972.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_model.hpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.hpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 973:
        revision_scoped_required.update({
            "HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md",
            "REVISION_NOTES_rev0973.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 974:
        revision_scoped_required.update({
            "DELETION_FREE_EXACT_RETENTION_PLAN_AUDIT_rev0974.md",
            "REVISION_NOTES_rev0974.md",
            "README.md",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.hpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 975:
        revision_scoped_required.update({
            "PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md",
            "REVISION_NOTES_rev0975.md",
            "README.md",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 976:
        revision_scoped_required.update({
            "EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md",
            "REVISION_NOTES_rev0976.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 977:
        revision_scoped_required.update({
            "EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md",
            "PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md",
            "REVISION_NOTES_rev0977.md",
            "README.md",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_inherited_test_process.py",
            "tools/audit_raw_fork_boundaries.py",
            "tools/audit_self_exec_test_process.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 978:
        revision_scoped_required.update({
            "PROCESS_STORE_LIVE_CAPABILITY_AND_WRITER_FENCED_RETENTION_AUDIT_rev0978.md",
            "REVISION_NOTES_rev0978.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 979:
        revision_scoped_required.update({
            "DURABLE_PAYLOAD_RETENTION_MARK_AND_POLICY_AUDIT_rev0979.md",
            "REVISION_NOTES_rev0979.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_file_payload_retention_mark.hpp",
            "src/sync_replica_file_payload_retention_mark.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_historical_version_query.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_file_payload_retention_mark_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 980:
        revision_scoped_required.update({
            "REPLICA_DATABASE_LINEAGE_AND_RETENTION_WITNESS_AUDIT_rev0980.md",
            "REVISION_NOTES_rev0980.md",
            "README.md",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_file_payload_retention_mark.hpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_historical_version_inventory_json.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/audit_sync_replica_sqlite_owner.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 981:
        revision_scoped_required.update({
            "OFFLINE_DATABASE_RECOVERY_AND_DEPLOYMENT_SINGLETON_AUDIT_rev0981.md",
            "REVISION_NOTES_rev0981.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_replica_operational_database.hpp",
            "src/sync_replica_operational_database.cpp",
            "src/sync_replica_folder_process.hpp",
            "src/sync_replica_folder_process.cpp",
            "src/sync_replica_peer_service_singleton.hpp",
            "src/sync_replica_peer_service_singleton.cpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tools/test_anonsync_database_recovery.py",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/audit_anonsync_replica_database_open_policy.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 982:
        revision_scoped_required.update({
            "OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md",
            "REVISION_NOTES_rev0982.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_replica_database_backup.hpp",
            "src/sync_replica_database_backup.cpp",
            "src/sync_replica_deployment_binding.hpp",
            "src/sync_replica_deployment_binding.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/persistence/sqlite_snapshot_seal_tests.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_replica_deployment_binding_test.cpp",
            "tools/test_anonsync_database_recovery.py",
            "tools/audit_anonsync_replica_deployment_binding.py",
            "tools/audit_sync_replica_database_backup.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 983:
        revision_scoped_required.update({
            "OFFLINE_REPLICA_DATABASE_REPLACEMENT_AUDIT_rev0983.md",
            "REVISION_NOTES_rev0983.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/persistence/sqlite_live_backup.hpp",
            "src/persistence/sqlite_live_backup.cpp",
            "src/sync_replica_database_artifact_internal.hpp",
            "src/sync_replica_database_backup.hpp",
            "src/sync_replica_database_backup.cpp",
            "src/sync_replica_database_replacement.hpp",
            "src/sync_replica_database_replacement.cpp",
            "tests/persistence/sqlite_live_backup_tests.cpp",
            "tools/test_anonsync_database_recovery.py",
            "tools/audit_sqlite_live_backup.py",
            "tools/audit_sync_replica_database_backup.py",
            "tools/audit_sync_replica_database_replacement.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 984:
        revision_scoped_required.update({
            "IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md",
            "REVISION_NOTES_rev0984.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_replica_database_artifact_internal.hpp",
            "src/sync_replica_database_replacement.hpp",
            "src/sync_replica_database_replacement.cpp",
            "src/sync_replica_database_replacement_receipt_internal.hpp",
            "src/sync_replica_database_replacement_receipt.cpp",
            "tools/test_anonsync_database_recovery.py",
            "tools/audit_sync_replica_database_replacement.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 985:
        revision_scoped_required.update({
            "ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md",
            "REVISION_NOTES_rev0985.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_replica_database_backup.hpp",
            "src/sync_replica_database_backup.cpp",
            "src/sync_replica_file_effect_sqlite_owner.hpp",
            "src/sync_replica_file_effect_sqlite_owner.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_tls_policy_sqlite_profile.hpp",
            "src/sync_replica_tls_policy_sqlite_profile.cpp",
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_sqlite_owner.cpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp",
            "src/sync_replica_tls_membership_anchor_sqlite_owner.cpp",
            "tools/test_anonsync_database_role_backup.py",
            "tools/audit_sync_replica_database_backup.py",
            "tools/audit_sync_replica_database_role_backup.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 986:
        revision_scoped_required.update({
            "FIXED_BLOCK_DELTA_AND_MULTI_TERABYTE_CAPACITY_AUDIT_rev0986.md",
            "REVISION_NOTES_rev0986.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_payload_extent.hpp",
            "src/sync_replica_deployment_manifest.hpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_deployment_manifest_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_content_defined_delta.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 987:
        revision_scoped_required.update({
            "BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md",
            "REVISION_NOTES_rev0987.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_folder.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_selective_sync_policy.hpp",
            "src/sync_replica_selective_sync_policy.cpp",
            "src/sync_replica_folder_observer.hpp",
            "src/sync_replica_folder_observer.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_selective_sync_policy_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/test_anonsync_folder_cli.py",
            "tools/audit_sync_replica_selective_sync.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 988:
        revision_scoped_required.update({
            "TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md",
            "REVISION_NOTES_rev0988.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_folder.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_targeted_catalog_cutpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 989:
        revision_scoped_required.update({
            "TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md",
            "REVISION_NOTES_rev0989.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_folder.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_targeted_path_cutpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 991:
        revision_scoped_required.update({
            "TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md",
            "REVISION_NOTES_rev0991.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_digest_accumulator.hpp",
            "src/sync_replica_digest_accumulator.cpp",
            "src/sync_replica_model.hpp",
            "src/sync_replica_model.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "tests/sync_replica_hash_graph_projection_test.cpp",
            "tests/sync_replica_prepared_publication_test.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tools/audit_sync_replica_targeted_local_publication.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 992:
        revision_scoped_required.update({
            "MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md",
            "REVISION_NOTES_rev0992.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_content_defined_delta.py",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_replica_selective_sync.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 993:
        revision_scoped_required.update({
            "REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md",
            "REVISION_NOTES_rev0993.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 994:
        revision_scoped_required.update({
            "CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md",
            "REVISION_NOTES_rev0994.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_content_defined_chunker.hpp",
            "src/sync_replica_content_defined_chunker.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_content_defined_chunker_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_content_defined_delta.py",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 995:
        revision_scoped_required.update({
            "SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md",
            "REVISION_NOTES_rev0995.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_source_chunk_index.py",
            "tools/audit_sync_replica_content_defined_delta.py",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 996:
        revision_scoped_required.update({
            "MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md",
            "REVISION_NOTES_rev0996.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_multi_range_window.py",
            "tools/audit_sync_replica_source_chunk_index.py",
            "tools/audit_sync_replica_content_defined_delta.py",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_replica_targeted_source_access.py",
            "tools/audit_sync_replica_selective_sync.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/test_anonsync_replica_reconciliation_process.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 997:
        revision_scoped_required.update({
            "DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md",
            "SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md",
            "REVISION_NOTES_rev0997.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "src/sync_replica_tls_transport.hpp",
            "src/sync_replica_tls_transport.cpp",
            "src/sync_replica_tls_record_exchange.hpp",
            "src/sync_replica_tls_record_exchange.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_frame_memory_test.cpp",
            "tests/sync_replica_reconciliation_memory_shape_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/audit_sync_replica_response_frame_memory.py",
            "tools/audit_sync_replica_response_memory_shape.py",
            "tools/audit_sync_replica_multi_range_window.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/audit_sync_tls_write_continuation.py",
            "tools/test_anonsync_replica_reconciliation_process.py",
            "tools/test_anonsync_sync_process.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 998:
        revision_scoped_required.update({
            "DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md",
            "REVISION_NOTES_rev0998.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_source_frame_memory_test.cpp",
            "tools/audit_sync_replica_direct_source_frame.py",
            "tools/audit_sync_replica_response_memory_shape.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 999:
        revision_scoped_required.update({
            "BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md",
            "REVISION_NOTES_rev0999.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_bounded_history_access.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1000:
        revision_scoped_required.update({
            "CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md",
            "REVISION_NOTES_rev1000.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_cross_file_delta.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1001:
        revision_scoped_required.update({
            "BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md",
            "REVISION_NOTES_rev1001.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_bounded_cross_file_projection.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1002:
        revision_scoped_required.update({
            "BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md",
            "REVISION_NOTES_rev1002.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_bounded_local_reuse.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1003:
        revision_scoped_required.update({
            "BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md",
            "REVISION_NOTES_rev1003.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_bounded_cross_file_projection.py",
            "tools/audit_sync_replica_bounded_predecessor_projection.py",
            "tools/audit_sync_replica_manifest_reference.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1004:
        revision_scoped_required.update({
            "BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md",
            "REVISION_NOTES_rev1004.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_file_payload_terminal_verification_state.hpp",
            "src/sync_replica_file_payload_terminal_verification_state.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "tests/sync_replica_file_payload_terminal_verification_state_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tools/audit_sync_replica_bounded_predecessor_projection.py",
            "tools/audit_sync_replica_terminal_verification_continuation.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1005:
        revision_scoped_required.update({
            "TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md",
            "REVISION_NOTES_rev1005.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/test_anonsync_replica_reconciliation_process.py",
            "tools/audit_sync_replica_terminal_verification_continuation.py",
            "tools/audit_sync_replica_targeted_terminal_local_pulse.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1006:
        revision_scoped_required.update({
            "RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md",
            "REVISION_NOTES_rev1006.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_terminal_verification_fixture.cpp",
            "tools/test_anonsync_service_terminal_verification_scheduler.py",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_replica_receiver_local_terminal_scheduler.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1007:
        revision_scoped_required.update({
            "BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md",
            "REVISION_NOTES_rev1007.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_replica.cpp",
            "src/anonsync_sync.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_reconciliation_tls_exchange.hpp",
            "src/sync_replica_reconciliation_tls_exchange.cpp",
            "src/sync_replica_sync_once.hpp",
            "src/sync_replica_sync_once.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_sync_once_test.cpp",
            "tests/sync_replica_tls_transport_test.cpp",
            "tools/test_anonsync_replica_reconciliation_process.py",
            "tools/test_anonsync_sync_process.py",
            "tools/audit_sync_replica_bounded_source_manifest_projection.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1008:
        revision_scoped_required.update({
            "SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md",
            "REVISION_NOTES_rev1008.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_peer_server_owner.hpp",
            "src/sync_replica_peer_server_owner.cpp",
            "src/sync_replica_peer_service.hpp",
            "src/sync_replica_peer_service.cpp",
            "src/sync_replica_peer_service_status.hpp",
            "src/sync_replica_peer_service_status.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/test_anonsync_service_source_manifest_scheduler.py",
            "tools/test_anonsync_service_configuration_status.py",
            "tools/test_anonsync_service_i2p_ingress.py",
            "tools/audit_sync_replica_source_local_manifest_scheduler.py",
            "tools/audit_sync_replica_bounded_source_manifest_projection.py",
            "tools/audit_sync_replica_receiver_local_terminal_scheduler.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1010:
        revision_scoped_required.update({
            "DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md",
            "REVISION_NOTES_rev1010.md",
            "README.md",
            "CMakeLists.txt",
            "src/resumable_sha256.hpp",
            "src/sync_replica_content_defined_chunker.hpp",
            "src/sync_replica_content_defined_chunker.cpp",
            "src/sync_replica_source_manifest_checkpoint.hpp",
            "src/sync_replica_source_manifest_checkpoint.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_peer_server_owner.hpp",
            "src/sync_replica_peer_server_owner.cpp",
            "src/sync_replica_peer_service.cpp",
            "tests/self_exec_test_process.hpp",
            "tests/sync_replica_content_defined_chunker_test.cpp",
            "tests/sync_replica_source_manifest_checkpoint_test.cpp",
            "tests/sync_replica_source_manifest_restart_test.cpp",
            "tools/audit_sync_replica_durable_source_manifest_checkpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1011:
        revision_scoped_required.update({
            "SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md",
            "REVISION_NOTES_rev1011.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_source_manifest_checkpoint.hpp",
            "src/sync_replica_source_manifest_checkpoint.cpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_source_manifest_checkpoint_test.cpp",
            "tools/audit_sync_replica_source_manifest_checkpoint_memory.py",
            "tools/audit_sync_replica_durable_source_manifest_checkpoint.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1012:
        revision_scoped_required.update({
            "COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md",
            "REVISION_NOTES_rev1012.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_content_defined_chunker.cpp",
            "src/sync_replica_reconciliation_compact_manifest.hpp",
            "src/sync_replica_reconciliation_compact_manifest.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_compact_manifest_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tools/audit_sync_replica_compact_source_manifest_cache.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1013:
        revision_scoped_required.update({
            "FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md",
            "REVISION_NOTES_rev1013.md",
            "README.md",
            "CMakeLists.txt",
            "src/sha256_digest.hpp",
            "src/sha256_digest.cpp",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_compact_manifest.hpp",
            "src/sync_replica_reconciliation_compact_manifest.cpp",
            "src/sync_replica_source_manifest_checkpoint.hpp",
            "src/sync_replica_source_manifest_checkpoint.cpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_compact_manifest_test.cpp",
            "tests/sync_replica_reconciliation_protocol_test.cpp",
            "tests/sync_replica_source_manifest_checkpoint_test.cpp",
            "tools/audit_sync_replica_fixed_binary_manifest.py",
            "tools/audit_sync_replica_compact_source_manifest_cache.py",
            "tools/audit_sync_replica_source_manifest_checkpoint_memory.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1014:
        revision_scoped_required.update({
            "BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md",
            "REVISION_NOTES_rev1014.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_reconciliation_protocol.hpp",
            "src/sync_replica_reconciliation_protocol.cpp",
            "src/sync_replica_reconciliation_compact_manifest.hpp",
            "src/sync_replica_reconciliation_compact_manifest.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/sync_replica_reconciliation_compact_manifest_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_reconciliation_source_frame_memory_test.cpp",
            "tools/audit_sync_replica_borrowed_manifest_frame.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1015:
        revision_scoped_required.update({
            "ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md",
            "TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md",
            "REVISION_NOTES_rev1015.md",
            "README.md",
            "CMakeLists.txt",
            "src/sha256_digest.hpp",
            "src/resumable_sha256.hpp",
            "src/resumable_sha256.cpp",
            "src/sync_replica_file_payload_store.hpp",
            "src/sync_replica_file_payload_store.cpp",
            "src/sync_replica_source_manifest_checkpoint.hpp",
            "src/sync_replica_source_manifest_checkpoint.cpp",
            "src/sync_replica_reconciliation_service.hpp",
            "src/sync_replica_reconciliation_service.cpp",
            "tests/resumable_sha256_test.cpp",
            "tests/sync_replica_file_payload_store_test.cpp",
            "tests/sync_replica_reconciliation_source_frame_memory_test.cpp",
            "tests/sync_replica_reconciliation_service_test.cpp",
            "tests/sync_replica_source_manifest_checkpoint_test.cpp",
            "tools/audit_sync_replica_active_source_manifest_memory.py",
            "tools/audit_sync_replica_terminal_manifest_cache.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1016:
        revision_scoped_required.update({
            "LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md",
            "REVISION_NOTES_rev1016.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_local_status_socket.hpp",
            "src/sync_local_status_socket.cpp",
            "src/sync_linux_process_resources.hpp",
            "src/sync_linux_process_resources.cpp",
            "tests/sync_local_status_socket_test.cpp",
            "tests/sync_linux_process_resources_test.cpp",
            "tests/sync_linux_process_resources_fixture.cpp",
            "tools/test_anonsync_process_resources.py",
            "tools/audit_sync_linux_process_resources.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1017:
        revision_scoped_required.update({
            "LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md",
            "REVISION_NOTES_rev1017.md",
            "README.md",
            "CMakeLists.txt",
            "src/anonsync_sync.cpp",
            "src/sync_linux_process_resources.hpp",
            "tests/sync_linux_process_resources_fixture.cpp",
            "tools/test_anonsync_process_resources.py",
            "tools/audit_sync_linux_process_resources.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1018:
        revision_scoped_required.update({
            "HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md",
            "SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md",
            "REVISION_NOTES_rev1018.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_delivery_service.cpp",
            "src/sync_replica_reconciliation_service.cpp",
            "src/sync_replica_file_delivery_service.cpp",
            "src/sync_replica_file_effect_sqlite_owner.hpp",
            "src/sync_replica_file_effect_sqlite_owner.cpp",
            "tests/sync_replica_reconciliation_source_frame_memory_test.cpp",
            "tools/audit_sync_replica_service_startup.py",
            "tools/test_anonsync_sparse_multiterabyte_selective_resources.py",
            "tools/audit_sync_sparse_multiterabyte_selective_resources.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1019:
        revision_scoped_required.update({
            "IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md",
            "REVISION_NOTES_rev1019.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_model.hpp",
            "src/sync_replica_model.cpp",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_folder_scan_owner.hpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "src/anonsync_folder.cpp",
            "src/anonsync_sync.cpp",
            "tests/sync_replica_network_model_test.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_identity_preserving_rename.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    if revision_number is not None and revision_number >= 1020:
        revision_scoped_required.update({
            "BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md",
            "REVISION_NOTES_rev1020.md",
            "README.md",
            "CMakeLists.txt",
            "src/sync_replica_sqlite_owner.hpp",
            "src/sync_replica_sqlite_owner.cpp",
            "src/sync_replica_folder_scan_owner.cpp",
            "tests/sync_replica_sqlite_owner_test.cpp",
            "tests/sync_replica_folder_scan_owner_test.cpp",
            "tools/audit_sync_replica_bounded_rename_planning.py",
            "tools/audit_sync_file_payload_store.py",
            "tools/verify_release_package.py",
        })
    missing_revision_scoped = sorted(revision_scoped_required - names)
    require(
        not missing_revision_scoped,
        "revision_scoped_required_files_present",
        "missing: " + ", ".join(missing_revision_scoped)
        if missing_revision_scoped
        else f"all files mandatory from {revision or 'the declared revision'} are present",
    )

    if REVISION_RE.fullmatch(revision):
        revision_files = {
            f"REVISION_NOTES_{revision}.md",
            f"REVISION_EVIDENCE/{revision}/ACTIVE_IMPLEMENTATION_PROJECTION.json",
            f"REVISION_EVIDENCE/{revision}/AUDIT.md",
            f"REVISION_EVIDENCE/{revision}/LINEAGE.md",
            f"REVISION_EVIDENCE/{revision}/LINEAGE.json",
            f"REVISION_EVIDENCE/{revision}/validation/VALIDATION_SUMMARY.json",
        }
        missing_revision = sorted(revision_files - names)
        require(not missing_revision, "revision_handoff_evidence_present", "missing: " + ", ".join(missing_revision) if missing_revision else "revision notes, lineage, active projection, audit, and validation summary are present")

        projection_path = f"REVISION_EVIDENCE/{revision}/ACTIVE_IMPLEMENTATION_PROJECTION.json"
        try:
            projection = json.loads(read(projection_path))
            projection_format = projection.get("format")
            require(
                projection_format in SUPPORTED_ACTIVE_PROJECTION_FORMATS,
                "active_projection_format_supported",
                f"format={projection_format!r}; absent format is the legacy v1 representation",
            )
            require(
                active_projection_format_allowed_for_revision(
                    projection_format,
                    revision_number,
                ),
                "active_projection_format_meets_revision_floor",
                f"revision={revision} format={projection_format!r}; "
                f"rev0905+ requires {ACTIVE_PROJECTION_V3_FORMAT}",
            )
            actual_projection = compute_active_projection(
                names, read, projection_format=projection_format)
            declared_digest = projection.get("sha256", projection.get("expected_sha256"))
            require(
                declared_digest == actual_projection["sha256"],
                "active_projection_digest_matches",
                f"declared={declared_digest} actual={actual_projection['sha256']}",
            )
            require(
                projection.get("file_count") == actual_projection["file_count"],
                "active_projection_file_count_matches",
                f"declared={projection.get('file_count')} actual={actual_projection['file_count']}",
            )
            require(
                projection.get("bytes") == actual_projection["bytes"],
                "active_projection_byte_count_matches",
                f"declared={projection.get('bytes')} actual={actual_projection['bytes']}",
            )
            require(
                projection.get("files") == actual_projection["files"],
                "active_projection_file_inventory_matches",
                "every active path, byte count, and file digest matches the recomputed projection",
            )
            if projection_format in {
                ACTIVE_PROJECTION_V2_FORMAT,
                ACTIVE_PROJECTION_V3_FORMAT,
            }:
                fuzz_sources = [entry for entry in actual_projection["files"]
                                if str(entry["path"]).startswith("fuzz/")]
                require(
                    bool(fuzz_sources),
                    "active_projection_v2_plus_binds_fuzz_sources",
                    f"fuzz source files={len(fuzz_sources)}",
                )
            if projection_format == ACTIVE_PROJECTION_V3_FORMAT:
                cmake_sources = [entry for entry in actual_projection["files"]
                                 if str(entry["path"]).startswith("cmake/")]
                require(
                    bool(cmake_sources),
                    "active_projection_v3_binds_cmake_authority",
                    f"cmake authority files={len(cmake_sources)}",
                )
        except Exception as error:
            require(False, "active_projection_parses_and_recomputes", str(error))

    manifest: dict[str, str] = {}
    try:
        manifest = parse_manifest(read("MANIFEST.sha256"))
        require(True, "manifest_parses", f"manifest entries={len(manifest)}")
    except Exception as error:
        require(False, "manifest_parses", str(error))
    expected_manifest_names = names - {"MANIFEST.sha256"}
    require(set(manifest) == expected_manifest_names, "manifest_has_exact_file_set", f"missing={sorted(expected_manifest_names - set(manifest))[:20]} extra={sorted(set(manifest) - expected_manifest_names)[:20]}")
    mismatches: list[str] = []
    for name, expected_digest in sorted(manifest.items()):
        try:
            actual = sha256_bytes(read(name))
        except Exception as error:
            mismatches.append(f"{name}: unreadable ({error})")
            continue
        if actual != expected_digest:
            mismatches.append(f"{name}: expected {expected_digest} actual {actual}")
    require(not mismatches, "manifest_hashes_verify", "; ".join(mismatches[:20]) if mismatches else "every manifested file matches its SHA-256")

    metadata = {
        "revision": revision,
        "file_count": len(names),
        "source_cpp_count": len(source_cpp),
        "source_header_count": len(source_headers),
        "test_cpp_count": len(tests),
        "manifest_entry_count": len(manifest),
        "forbidden_entries": forbidden,
    }
    return checks, metadata


def verify_zip(path: Path, expected_revision: str | None) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(
            {"check_id": check_id, "passed": bool(condition), "detail": detail}
        )

    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        raw_name_counts = Counter(info.filename for info in infos)
        duplicate_names = sorted(
            name for name, count in raw_name_counts.items() if count > 1
        )
        require(
            not duplicate_names,
            "zip_member_names_are_unique",
            f"duplicates={duplicate_names[:20]}",
        )
        unsafe: list[str] = []
        symlinks: list[str] = []
        unsupported_types: list[str] = []
        malformed_directories: list[str] = []
        normalized_infos: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
        for info in infos:
            raw = info.filename.rstrip("/")
            if not raw:
                unsafe.append(info.filename)
                continue
            try:
                normalized = normalized_member(raw)
                normalized_infos.append((info, normalized))
            except ValueError:
                unsafe.append(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            file_type = stat.S_IFMT(mode)
            if stat.S_ISLNK(mode):
                symlinks.append(info.filename)
            elif file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
                unsupported_types.append(info.filename)
            if info.is_dir() and info.file_size != 0:
                malformed_directories.append(info.filename)
        require(not unsafe, "zip_paths_are_safe", f"unsafe={unsafe[:20]}")
        require(
            not symlinks,
            "zip_contains_no_symlinks",
            f"symlinks={symlinks[:20]}",
        )
        require(
            not unsupported_types,
            "zip_contains_only_regular_files_and_directories",
            f"unsupported={unsupported_types[:20]}",
        )
        require(
            not malformed_directories,
            "zip_directory_members_have_zero_extent",
            f"malformed={malformed_directories[:20]}",
        )

        normalized_name_counts = Counter(
            normalized.as_posix() for _, normalized in normalized_infos
        )
        normalized_collisions = sorted(
            name for name, count in normalized_name_counts.items() if count > 1
        )
        require(
            not normalized_collisions,
            "zip_normalized_member_paths_are_unique",
            f"collisions={normalized_collisions[:20]}",
        )
        absolute_entries = {
            normalized.as_posix() for _, normalized in normalized_infos
        }
        absolute_files = {
            normalized.as_posix()
            for info, normalized in normalized_infos
            if not info.is_dir()
        }
        file_ancestor_conflicts = ancestor_file_conflicts(
            absolute_entries, absolute_files
        )
        require(
            not file_ancestor_conflicts,
            "zip_files_are_not_path_ancestors",
            f"conflicts={file_ancestor_conflicts[:20]}",
        )

        roots = {
            normalized.parts[0]
            for _, normalized in normalized_infos
            if normalized.parts
        }
        require(
            len(roots) == 1,
            "zip_has_one_release_root",
            f"roots={sorted(roots)}",
        )
        root_name = next(iter(roots), "")
        relative_entries: set[str] = set()
        relative_files: set[str] = set()
        if root_name:
            for info, normalized in normalized_infos:
                if not normalized.parts or normalized.parts[0] != root_name:
                    continue
                relative = PurePosixPath(*normalized.parts[1:])
                if not relative.parts:
                    continue
                canonical = relative.as_posix()
                relative_entries.add(canonical)
                if not info.is_dir():
                    relative_files.add(canonical)

        wrapper_layout = (
            "BOOTSTRAPROSE.md" in relative_entries
            or any(
                name == ".vault/project"
                or name.startswith(BOOTSTRAP_WRAPPER_PROJECT_PREFIX)
                for name in relative_entries
            )
        )
        require(
            not wrapper_required_for_revision(expected_revision) or wrapper_layout,
            "bootstrap_wrapper_required_for_current_revision",
            f"expected_revision={expected_revision!r} wrapper={wrapper_layout}",
        )

        if wrapper_layout:
            require(
                PACKAGE_FILENAME_RE.fullmatch(path.name) is not None,
                "zip_filename_has_canonical_revision_shape",
                f"filename={path.name!r}",
            )
            require(
                root_name == path.stem,
                "zip_root_matches_complete_filename_stem",
                f"root={root_name!r} stem={path.stem!r}",
            )
            project_names, wrapper_violations = analyze_bootstrap_wrapper_layout(
                relative_entries, relative_files
            )
            require(
                not wrapper_violations,
                "bootstrap_wrapper_exposes_only_restart_page_and_hidden_material",
                "; ".join(wrapper_violations)
                if wrapper_violations
                else "only BOOTSTRAPROSE.md is visible and source is under .vault/project",
            )

            def read(name: str) -> bytes:
                return archive.read(
                    f"{root_name}/{BOOTSTRAP_WRAPPER_PROJECT_PREFIX}{name}"
                )

            names = project_names
            try:
                release_gate = json.loads(read("RELEASE_GATE.json"))
                restart_page = archive.read(
                    f"{root_name}/BOOTSTRAPROSE.md"
                )
                restart_violations = (
                    bootstrap_restart_page_binding_violations(
                        release_gate, restart_page
                    )
                )
                require(
                    not restart_violations,
                    "visible_bootstraprose_matches_hidden_release_binding",
                    "; ".join(restart_violations)
                    if restart_violations
                    else "visible BOOTSTRAPROSE.md matches RELEASE_GATE.json",
                )
            except Exception as error:
                require(
                    False,
                    "visible_bootstraprose_matches_hidden_release_binding",
                    str(error),
                )
        else:
            require(
                root_name == "AnonSync",
                "legacy_zip_has_one_anonsync_root",
                f"root={root_name!r}",
            )
            names = relative_files

            def read(name: str) -> bytes:
                return archive.read(f"{root_name}/{name}")

        package, metadata = package_checks(names, read, expected_revision)
        checks.extend(package)
        revision = str(metadata.get("revision", ""))
        revision_number = (
            int(revision.removeprefix("rev"))
            if REVISION_RE.fullmatch(revision)
            else None
        )
        if revision_number is not None and revision_number >= 895:
            try:
                declared_filename = json.loads(read("RELEASE_GATE.json")).get(
                    "package_filename"
                )
                require(
                    path.name == declared_filename,
                    "zip_filename_matches_release_gate",
                    f"actual={path.name!r} declared={declared_filename!r}",
                )
            except Exception as error:
                require(False, "zip_filename_matches_release_gate", str(error))
        bad_member = archive.testzip()
        require(
            bad_member is None,
            "zip_crc_integrity_passes",
            f"bad_member={bad_member}",
        )
    return {"metadata": metadata, "checks": checks}


def verify_directory(path: Path, expected_revision: str | None) -> dict[str, object]:
    wrapper_root = path
    wrapper_layout = (wrapper_root / ".vault" / "project").is_dir()
    if wrapper_layout:
        project_root = wrapper_root / ".vault" / "project"
        entries: set[str] = set()
        files: set[str] = set()
        symlinks: list[str] = []
        special_entries: list[str] = []
        for item in sorted(wrapper_root.rglob("*")):
            rel = item.relative_to(wrapper_root).as_posix()
            entries.add(rel)
            if item.is_symlink():
                symlinks.append(rel)
            elif item.is_file():
                files.add(rel)
            elif not item.is_dir():
                special_entries.append(rel)
        project_names, wrapper_violations = analyze_bootstrap_wrapper_layout(
            entries, files
        )
        names = project_names

        def read(name: str) -> bytes:
            return (project_root / name).read_bytes()

        checks, metadata = package_checks(names, read, expected_revision)
        try:
            release_gate = json.loads(read("RELEASE_GATE.json"))
            restart_violations = bootstrap_restart_page_binding_violations(
                release_gate, (wrapper_root / "BOOTSTRAPROSE.md").read_bytes()
            )
            checks.insert(
                0,
                {
                    "check_id": "visible_bootstraprose_matches_hidden_release_binding",
                    "passed": not restart_violations,
                    "detail": "; ".join(restart_violations)
                    if restart_violations
                    else "visible BOOTSTRAPROSE.md matches RELEASE_GATE.json",
                },
            )
        except Exception as error:
            checks.insert(
                0,
                {
                    "check_id": "visible_bootstraprose_matches_hidden_release_binding",
                    "passed": False,
                    "detail": str(error),
                },
            )
        checks.insert(
            0,
            {
                "check_id": "directory_contains_only_regular_files_and_directories",
                "passed": not special_entries,
                "detail": f"special_entries={special_entries[:20]}",
            },
        )
        checks.insert(
            0,
            {
                "check_id": "bootstrap_wrapper_exposes_only_restart_page_and_hidden_material",
                "passed": not wrapper_violations,
                "detail": "; ".join(wrapper_violations)
                if wrapper_violations
                else "only BOOTSTRAPROSE.md is visible and source is under .vault/project",
            },
        )
        checks.insert(
            0,
            {
                "check_id": "directory_contains_no_symlinks",
                "passed": not symlinks,
                "detail": f"symlinks={symlinks[:20]}",
            },
        )
        canonical_filename = wrapper_root.name + ".zip"
        checks.insert(
            0,
            {
                "check_id": "wrapper_directory_name_has_canonical_revision_shape",
                "passed": PACKAGE_FILENAME_RE.fullmatch(canonical_filename)
                is not None,
                "detail": f"derived_filename={canonical_filename!r}",
            },
        )
        try:
            declared_filename = json.loads(read("RELEASE_GATE.json")).get(
                "package_filename"
            )
            checks.insert(
                0,
                {
                    "check_id": "wrapper_directory_name_matches_release_gate",
                    "passed": declared_filename == canonical_filename,
                    "detail": f"derived={canonical_filename!r} declared={declared_filename!r}",
                },
            )
        except Exception as error:
            checks.insert(
                0,
                {
                    "check_id": "wrapper_directory_name_matches_release_gate",
                    "passed": False,
                    "detail": str(error),
                },
            )
        return {"metadata": metadata, "checks": checks}

    root = path / "AnonSync" if (path / "AnonSync").is_dir() else path
    names: set[str] = set()
    symlinks: list[str] = []
    for item in sorted(root.rglob("*")):
        rel = item.relative_to(root).as_posix()
        if item.is_symlink():
            symlinks.append(rel)
        elif item.is_file():
            names.add(rel)

    def read(name: str) -> bytes:
        return (root / name).read_bytes()

    checks, metadata = package_checks(names, read, expected_revision)
    checks.insert(
        0,
        {
            "check_id": "directory_contains_no_symlinks",
            "passed": not symlinks,
            "detail": f"symlinks={symlinks[:20]}",
        },
    )
    checks.insert(
        0,
        {
            "check_id": "bootstrap_wrapper_required_for_current_revision",
            "passed": not wrapper_required_for_revision(expected_revision),
            "detail": f"expected_revision={expected_revision!r} wrapper=False",
        },
    )
    return {"metadata": metadata, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-revision")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    path = args.path.resolve()
    try:
        if path.is_file() and zipfile.is_zipfile(path):
            result = verify_zip(path, args.expected_revision)
            kind = "zip"
        elif path.is_dir():
            result = verify_directory(path, args.expected_revision)
            kind = "directory"
        else:
            raise ValueError("path is neither a release directory nor a ZIP archive")
        checks = result["checks"]
        passed = all(bool(check["passed"]) for check in checks)
        report = {
            "format": "anonsync-release-package-verification-v1",
            "path": str(path),
            "kind": kind,
            "passed": passed,
            "check_count": len(checks),
            "passed_check_count": sum(bool(check["passed"]) for check in checks),
            "checks": checks,
            **result["metadata"],
        }
    except Exception as error:
        report = {
            "format": "anonsync-release-package-verification-v1",
            "path": str(path),
            "passed": False,
            "fatal_error": str(error),
        }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
