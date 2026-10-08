#!/usr/bin/env python3
"""Fail-closed audit for exact bounded regular-file observation ownership."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_bounded_regular_file.hpp"),
    Path("src/sync_bounded_regular_file.cpp"),
    Path("src/sync_bounded_regular_file_limits.hpp"),
    Path("src/sync_posix_descriptor_snapshot.hpp"),
    Path("src/sync_posix_descriptor_snapshot.cpp"),
    Path("src/json_codec_crypto.cpp"),
    Path("src/sync_domain.cpp"),
    Path("src/sync_operator_cli.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_linked_peer_pairing.cpp"),
    Path("src/sync_replica_peer_service_configuration.cpp"),
    Path("src/sync_replica_peer_service_provisioning.cpp"),
    Path("src/sync_replica_bootstrap_record.cpp"),
    Path("src/sync_replica_deployment_manifest.cpp"),
    Path("src/sync_replica_database_replacement_receipt.cpp"),
    Path("tests/sync_bounded_regular_file_test.cpp"),
    Path("tests/sync_bounded_regular_file_syscall_test.cpp"),
    Path("tools/audit_sync_bounded_regular_file.py"),
    Path("tools/verify_release_package.py"),
)

OLD_SYMBOL = "read_regular_file_bounded_no_symlink_or_throw"
ORDINARY_SYMBOL = "read_sync_bounded_regular_file_no_symlink_or_throw"
SINGLE_LINK_SYMBOL = (
    "read_sync_bounded_single_link_regular_file_no_symlink_or_throw"
)
PRIVATE_SYMBOL = "read_sync_bounded_private_regular_file_no_symlink_or_throw"


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def cmake_invocation_body(text: str, command: str, target: str) -> str:
    """Return one exact, non-nested CMake invocation body.

    The old audit inferred target ownership from the text between two unrelated
    declarations. Adding a new neighboring target therefore made the bounded
    reader appear to acquire dependencies it did not have. Keep the lexical
    audit, but bind it to the exact command/target tuple it claims to inspect.
    """

    match = re.search(
        rf"{re.escape(command)}\({re.escape(target)}\s+(.*?)\)",
        text,
        re.DOTALL,
    )
    return match.group(1) if match else ""


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-bounded-regular-file-audit-v4",
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
    header = text[Path("src/sync_bounded_regular_file.hpp")]
    source = text[Path("src/sync_bounded_regular_file.cpp")]
    limits = text[Path("src/sync_bounded_regular_file_limits.hpp")]
    descriptor_header = text[Path("src/sync_posix_descriptor_snapshot.hpp")]
    descriptor = text[Path("src/sync_posix_descriptor_snapshot.cpp")]
    codec = text[Path("src/json_codec_crypto.cpp")]
    domain = text[Path("src/sync_domain.cpp")]
    cli = text[Path("src/sync_operator_cli.cpp")]
    replica_cli = text[Path("src/anonsync_replica.cpp")]
    sync_cli = text[Path("src/anonsync_sync.cpp")]
    linked_peer_pairing = text[Path("src/sync_linked_peer_pairing.cpp")]
    service_configuration = text[
        Path("src/sync_replica_peer_service_configuration.cpp")
    ]
    service_provisioning = text[
        Path("src/sync_replica_peer_service_provisioning.cpp")
    ]
    bootstrap_record = text[Path("src/sync_replica_bootstrap_record.cpp")]
    deployment_manifest = text[Path("src/sync_replica_deployment_manifest.cpp")]
    replacement_receipt = text[
        Path("src/sync_replica_database_replacement_receipt.cpp")
    ]
    runtime_test = text[Path("tests/sync_bounded_regular_file_test.cpp")]
    syscall_test = text[Path("tests/sync_bounded_regular_file_syscall_test.cpp")]
    verifier = text[Path("tools/verify_release_package.py")]

    production_symbol_sites: dict[str, dict[str, int]] = {
        "ordinary": {},
        "single_link": {},
        "private": {},
    }
    old_symbol_sites: list[str] = []
    for directory in (root / "src", root / "include"):
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix not in {
                ".c", ".cc", ".cpp", ".h", ".hpp"
            }:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            relative = path.relative_to(root).as_posix()
            for contract, symbol in (
                ("ordinary", ORDINARY_SYMBOL),
                ("single_link", SINGLE_LINK_SYMBOL),
                ("private", PRIVATE_SYMBOL),
            ):
                count = content.count(symbol)
                if count:
                    production_symbol_sites[contract][relative] = count
            if OLD_SYMBOL in content:
                old_symbol_sites.append(relative)

    declaration_patterns = {
        contract: re.compile(rf"std::string\s+{re.escape(symbol)}\s*\(")
        for contract, symbol in (
            ("ordinary", ORDINARY_SYMBOL),
            ("single_link", SINGLE_LINK_SYMBOL),
            ("private", PRIVATE_SYMBOL),
        )
    }
    require(
        all(
            len(pattern.findall(header)) == 1
            and len(pattern.findall(source)) == 1
            for pattern in declaration_patterns.values()
        )
        and all(
            symbol not in header.split("namespace anonsync")[0]
            for symbol in (ORDINARY_SYMBOL, SINGLE_LINK_SYMBOL, PRIVATE_SYMBOL)
        ),
        "one_header_contract_and_one_compiled_definition_per_policy",
        f"sites={production_symbol_sites}",
    )
    expected_symbol_sites = {
        "ordinary": {
            "src/json_codec_crypto.cpp": 1,
            "src/anonsync_replica.cpp": 2,
            "src/sync_bounded_regular_file.cpp": 1,
            "src/sync_bounded_regular_file.hpp": 1,
            "src/sync_domain.cpp": 1,
            "src/sync_operator_cli.cpp": 1,
            "src/sync_replica_bootstrap_record.cpp": 1,
            "src/sync_replica_deployment_manifest.cpp": 1,
            "src/sync_linked_peer_pairing.cpp": 1,
        },
        "single_link": {
            "src/sync_bounded_regular_file.cpp": 1,
            "src/sync_bounded_regular_file.hpp": 1,
        },
        "private": {
            "src/anonsync_replica.cpp": 1,
            "src/anonsync_sync.cpp": 1,
            "src/sync_linked_peer_pairing.cpp": 3,
            "src/sync_replica_peer_service_configuration.cpp": 3,
            "src/sync_replica_peer_service_provisioning.cpp": 1,
            "src/sync_replica_database_replacement_receipt.cpp": 1,
            "src/sync_bounded_regular_file.cpp": 1,
            "src/sync_bounded_regular_file.hpp": 1,
        },
    }
    require(
        not old_symbol_sites and production_symbol_sites == expected_symbol_sites,
        "old_hidden_helper_removed_and_policy_consumers_are_exact",
        f"old_sites={old_symbol_sites}; policy_sites={production_symbol_sites}",
    )
    require(
        all(
            '#include "sync_bounded_regular_file.hpp"' in consumer
            and consumer.count(ORDINARY_SYMBOL) == ordinary_count
            and consumer.count(PRIVATE_SYMBOL) == private_count
            and OLD_SYMBOL not in consumer
            for consumer, ordinary_count, private_count in (
                (codec, 1, 0),
                (domain, 1, 0),
                (cli, 1, 0),
                (replica_cli, 2, 1),
                (sync_cli, 0, 1),
                (linked_peer_pairing, 1, 3),
                (service_configuration, 0, 3),
                (service_provisioning, 0, 1),
                (bootstrap_record, 1, 0),
                (deployment_manifest, 1, 0),
                (replacement_receipt, 0, 1),
            )
        ),
        "all_consumers_use_the_owned_header_and_explicit_policy",
        "generic documents use ordinary bounded reads while route/service configuration, TLS private keys, and immutable replacement receipts use the private-file contract",
    )
    require(
        len(header.splitlines()) <= 48
        and "std::filesystem::path" in header
        and "std::uint64_t maximum_bytes" in header
        and "final path component" in header
        and "one-byte sentinel" in header
        and "exactly one filesystem link" in header
        and "effective user with exact mode 0600" in header
        and "owner-only DACL" in header,
        "header_exposes_three_policy_contracts_not_choreography",
        f"header_lines={len(header.splitlines())}",
    )

    core_sources = block_between(
        cmake, "set(ANONSYNC_CORE_SOURCES", "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE"
    )
    leaf_sources = cmake_invocation_body(
        cmake, "set", "ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE"
    )
    leaf_library = cmake_invocation_body(
        cmake, "add_library", "anonsync_sync_bounded_regular_file"
    )
    leaf_links = cmake_invocation_body(
        cmake, "target_link_libraries", "anonsync_sync_bounded_regular_file"
    )
    core_links = block_between(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "if(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    require(
        "src/sync_bounded_regular_file.cpp" in leaf_sources
        and "src/sync_posix_descriptor_snapshot.cpp" in leaf_sources
        and "STATIC" in leaf_library
        and "${ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE}" in leaf_library
        and " ".join(leaf_links.split()) ==
            "PRIVATE anonsync_sha256_digest"
        and "src/sync_bounded_regular_file.cpp" not in core_sources
        and "${ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE}" in cmake,
        "reader_is_a_single_digest_dependent_invariant_owned_leaf",
        "the implementation compiles once outside the core aggregation and depends only on the focused SHA-256 leaf needed by descriptor-stream digest snapshots",
    )
    require(
        "anonsync_sync_bounded_regular_file" in core_links
        and "PRIVATE" in core_links
        and "${ANONSYNC_SYNC_BOUNDED_REGULAR_FILE_SOURCE}" in block_between(
            cmake,
            "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
            "add_library(anonsync_core_lib",
        ),
        "core_consumes_leaf_without_reabsorbing_source",
        "the core links the leaf privately and configure rejects source reinsertion",
    )

    focused_target = block_between(
        cmake,
        "add_executable(anonsync_sync_bounded_regular_file_test",
        "add_executable(anonsync_process_incarnation_test",
    )
    require(
        bool(focused_target)
        and focused_target.count("anonsync_sync_bounded_regular_file") >= 4
        and "anonsync_core_lib" not in focused_target
        and "--wrap=open" in focused_target
        and "--wrap=fstat" in focused_target
        and "--wrap=pread" in focused_target
        and "--wrap=close" in focused_target,
        "focused_proofs_link_only_the_leaf",
        "runtime and deterministic syscall tests do not restore core dependency fan-out",
    )
    require(
        "anonsync_sync_bounded_regular_file" in block_between(
            cmake,
            "foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET",
            "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
        )
        and "focused bounded-read syscall proof must not link anonsync_core_lib"
        in cmake,
        "configure_time_dependency_guards_are_present",
        "both unconditional and Linux-only proofs fail configuration if the core re-enters their link graph",
    )

    posix_flags = block_between(
        source, "[[nodiscard]] int posix_open_flags()", "void close_posix_fd_or_throw"
    )
    posix_adapter = block_between(
        source,
        "std::string read_posix_file_or_throw",
        "\n#endif\n}\n#endif",
    )
    require(
        all(token in posix_flags for token in ("O_RDONLY", "O_NOFOLLOW", "O_NONBLOCK"))
        and "#if !defined(O_NOFOLLOW) || !defined(O_NONBLOCK)" in posix_adapter
        and "O_CLOEXEC" in posix_flags
        and "FD_CLOEXEC" in posix_adapter
        and "O_NOCTTY" in posix_flags,
        "posix_open_is_nonblocking_nofollow_and_exec_safe",
        "a raced FIFO cannot block before descriptor inspection and the descriptor cannot leak through exec",
    )
    require(
        "FrozenSyncPosixRegularFileSnapshot" in descriptor_header
        and "freeze_borrowed_descriptor_or_throw" in descriptor_header
        and "never closes" in descriptor_header
        and "pread(2)" in descriptor_header
        and "::close" not in descriptor,
        "borrowed_descriptor_owner_is_explicit_and_nonclosing",
        "the extracted owner freezes bytes without acquiring descriptor-lifetime authority",
    )
    require(
        bool(posix_adapter)
        and ordered(
            posix_adapter,
            "::open(",
            "FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw",
            "take_bytes()",
            "close_posix_fd_or_throw",
        )
        and "catch (...)" in posix_adapter
        and "(void)::close(fd)" in posix_adapter,
        "pathname_adapter_owns_open_snapshot_and_close_order",
        "the adapter alone owns descriptor acquisition and cleanup while the snapshot remains reusable",
    )
    require(
        "remaining + 1U" in limits
        and "maximum_size - bytes.size()" in descriptor
        and "bytes.append" in descriptor
        and "bytes.resize" not in descriptor
        and "std::string{}.max_size()" in limits
        and "std::numeric_limits<off_t>::max()" in limits,
        "snapshot_proves_eof_and_checked_positional_range",
        "the one-byte sentinel, string capacity, and off_t range are owned by one shared limit policy",
    )
    require(
        ordered(
            descriptor,
            "::fstat(descriptor, &before)",
            "require_regular_snapshot_or_throw(before",
            "::pread(descriptor",
            "received == 0",
            "::fstat(descriptor, &after)",
            "require_regular_snapshot_or_throw(after",
        )
        and "static_cast<off_t>(bytes.size())" in descriptor,
        "descriptor_transition_is_fstat_pread_eof_fstat",
        "every byte and both metadata observations refer to the borrowed kernel object from offset zero",
    )
    require(
        all(
            token in descriptor
            for token in (
                "before.st_dev == after.st_dev",
                "before.st_ino == after.st_ino",
                "before.st_size == after.st_size",
                "before.st_nlink == after.st_nlink",
                "same_modification_snapshot(before, after)",
                "st_nlink == 0",
                "SyncPosixDescriptorLinkPolicy::exactly_one",
            )
        ),
        "descriptor_snapshot_binds_identity_size_metadata_and_topology",
        "unlinked objects, unauthorized aliases, and topology drift cannot mint namespace evidence",
    )
    require(
        "errno == EINTR" in descriptor
        and "positional read failed" in descriptor
        and "::lseek" not in descriptor
        and "::read(" not in descriptor
        and "::close" not in descriptor,
        "positional_read_preserves_offset_and_borrowed_ownership",
        "EINTR is retried without consuming shared offset or closing caller authority",
    )

    require(
        all(
            token in source
            for token in (
                "BoundedRegularFilePolicy::private_owner_mode_0600",
                "status.st_uid != ::geteuid()",
                "status.st_nlink != 1",
                "(status.st_mode & 07777U) != (S_IRUSR | S_IWUSR)",
                "same_private_posix_identity_and_policy",
                "private-file identity or access policy changed",
                "owner-only DACL proof",
            )
        )
        and ordered(
            source,
            "observe_private_posix_file_or_throw(fd, label, false)",
            "FrozenSyncPosixRegularFileSnapshot::freeze_borrowed_descriptor_or_throw",
            "observe_private_posix_file_or_throw(fd, label, true)",
        ),
        "private_policy_is_descriptor_bound_owner_only_and_stable",
        "secret bytes require one link, effective-user ownership, exact mode 0600, and unchanged descriptor policy across the read",
    )

    windows_reader = block_between(
        source, "std::string read_windows_file_or_throw", "#else"
    )
    require(
        bool(windows_reader)
        and all(
            token in windows_reader
            for token in (
                "CreateFileW",
                "FILE_FLAG_OPEN_REPARSE_POINT",
                "GetFileInformationByHandle",
                "ReadFile",
                "CloseHandle",
            )
        )
        and "FILE_ATTRIBUTE_REPARSE_POINT" in source
        and "FILE_TYPE_DISK" in source
        and "symlink_status" not in source
        and "file_size(path" not in source,
        "windows_observation_is_handle_bound_and_reparse_rejecting",
        "path prechecks no longer authorize a later unbounded pathname reopen",
    )
    require(
        all(
            token in source
            for token in (
                "dwVolumeSerialNumber",
                "nFileIndexHigh",
                "nFileIndexLow",
                "ftLastWriteTime",
                "dwFileAttributes",
            )
        ),
        "windows_snapshot_binds_handle_identity_size_and_metadata",
        "the post-read proof refers to the same kernel object rather than a second pathname lookup",
    )

    require(
        "path.native()" in source
        and "path contains an embedded NUL" in source
        and "embedded NUL path bytes" in runtime_test,
        "native_path_cannot_be_truncated_at_an_embedded_nul",
        "the operating-system open call cannot observe a shorter path than the validated C++ path",
    )
    require(
        all(
            token in runtime_test
            for token in (
                "embedded NUL",
                "exact ceilings",
                "borrowed descriptors are frozen from byte zero",
                "shared file offset",
                "unlinked descriptors cannot mint namespace evidence",
                "create_symlink",
                "mkfifo",
                "elapsed < std::chrono::seconds(1)",
                "effective-user single-link mode-0600 files admit secret bytes",
                "group-readable secret files are rejected",
                "multiply-linked secret files are rejected",
                "owner-only DACL proof",
            )
        ),
        "filesystem_contract_test_covers_types_bounds_fifo_and_private_secrets",
        "the live host test proves exact bytes, ceiling edges, final-link rejection, nonblocking FIFO denial, and owner-only secret admission",
    )
    require(
        all(
            token in syscall_test
            for token in (
                "__wrap_open",
                "__wrap_fstat",
                "__wrap_pread",
                "__wrap_close",
                "EINTR",
                "EIO",
                "growth beyond the ceiling",
                "post-read size drift",
                "same-size modification metadata drift",
                "expected_pread_offset",
                "primary read failure",
                "close failure",
            )
        ),
        "syscall_oracle_covers_order_retries_growth_and_error_precedence",
        "deterministic scripts exercise transitions that filesystem timing cannot prove",
    )
    require(
        cmake.count("add_test(NAME anonsync_sync_bounded_regular_file_test") == 1
        and cmake.count(
            "add_test(NAME anonsync_sync_bounded_regular_file_syscall_test"
        )
        == 1
        and cmake.count(
            "add_test(NAME anonsync_sync_bounded_regular_file_source_audit"
        )
        == 1,
        "all_new_proofs_are_ctest_obligations",
        "runtime, syscall, and structural proofs each have exactly one release-gate registration",
    )
    required_release_files = (
        "src/sync_bounded_regular_file.hpp",
        "src/sync_bounded_regular_file.cpp",
        "src/sync_bounded_regular_file_limits.hpp",
        "src/sync_posix_descriptor_snapshot.hpp",
        "src/sync_posix_descriptor_snapshot.cpp",
        "tests/sync_bounded_regular_file_test.cpp",
        "tests/sync_bounded_regular_file_syscall_test.cpp",
        "tools/audit_sync_bounded_regular_file.py",
    )
    require(
        all(f'"{path}"' in verifier for path in required_release_files),
        "release_verifier_pins_reader_tests_and_audit",
        "a package cannot silently omit the extracted boundary or its proof surface",
    )

    metrics = {
        "header_lines": len(header.splitlines()),
        "implementation_lines": len(source.splitlines()),
        "descriptor_owner_lines": len(descriptor.splitlines()),
        "descriptor_header_lines": len(descriptor_header.splitlines()),
        "shared_limit_lines": len(limits.splitlines()),
        "runtime_test_lines": len(runtime_test.splitlines()),
        "syscall_test_lines": len(syscall_test.splitlines()),
        "production_symbol_sites": production_symbol_sites,
        "old_symbol_sites": old_symbol_sites,
        "posix_fstat_calls": descriptor.count("::fstat("),
        "posix_pread_calls": descriptor.count("::pread("),
        "windows_handle_information_calls": windows_reader.count(
            "GetFileInformationByHandle"
        ),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
