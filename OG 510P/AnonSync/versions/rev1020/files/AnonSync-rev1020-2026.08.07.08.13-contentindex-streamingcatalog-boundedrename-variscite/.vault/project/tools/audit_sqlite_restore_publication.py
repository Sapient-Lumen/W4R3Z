#!/usr/bin/env python3
"""Fail-closed audit of the SQLite snapshot restore publication protocol.

The restore path may replace its destination main file only through the shared
atomic publisher. It must not reserve a predictable SQLite staging database,
open a second writable reconstruction database, or delete destination sidecar
names that it has not proved it owns.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def slice_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    paths = {
        "cmake": root / "CMakeLists.txt",
        "ledger": root / "src/sqlite_replay_ledger.cpp",
        "seal_header": root / "src/persistence/sqlite_snapshot_seal.hpp",
        "seal_source": root / "src/persistence/sqlite_snapshot_seal.cpp",
        "publisher_header": root / "src/sync_atomic_file_publication.hpp",
        "publisher_internal": root / "src/sync_atomic_file_publication_internal.hpp",
        "publisher_source": root / "src/sync_atomic_file_publication.cpp",
        "test": root / "tests/sqlite_restore_namespace_authority_test.cpp",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        result = {
            "format": "anonsync-sqlite-restore-publication-audit-v1",
            "passed": False,
            "checks": [],
            "violations": [f"missing required file: {name}" for name in missing],
        }
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    text = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    restore = slice_between(
        text["ledger"],
        "void restore_sqlite_snapshot_into_ledger_internal(",
        "void restore_sqlite_snapshot_into_ledger(",
    )
    writer_probe = slice_between(
        text["ledger"],
        "void assert_restore_destination_not_writer_locked(",
        "void reject_sqlite_family_symlinks(",
    )
    quiescence = slice_between(
        text["ledger"],
        "void checkpoint_destination_before_restore_replace(",
        "void restore_atomic_publication_fault_observer(",
    )
    checks: list[Check] = []

    def require(check_id: str, condition: bool, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    require("restore_function_was_located", bool(restore),
            "the production restore implementation must remain discoverable")
    require("writer_lock_probe_was_located", bool(writer_probe),
            "the preflight writer-lock owner must remain discoverable")
    require("destination_quiescence_function_was_located", bool(quiescence),
            "the destination family gate must remain discoverable")
    require(
        "writer_lock_probe_is_sidecar_first_identity_bound_and_fail_closed",
        writer_probe.find("verify_sidecars_absent_or_throw") >= 0
        and writer_probe.find("verify_sidecars_absent_or_throw") < writer_probe.find("sqlite_open_or_throw")
        and "verify_open_database_or_throw" in writer_probe
        and "writer-lock probe failed" in writer_probe
        and "sqlite3_open_v2" not in writer_probe,
        "the lock probe must reject foreign sidecars before open, bind identity, and reject non-lock SQLite errors",
    )
    require(
        "restore_publishes_the_sealed_resident_bytes",
        "publish_exact_copy_atomically_with_observer_or_throw" in restore
        and "SealedSqliteSnapshot::capture" in restore,
        "one source byte seal feeds verification, continuity, and publication",
    )
    forbidden_restore = (
        "restore_temp_path_for", "unlink_sqlite_family", "sqlite3_backup_init",
        "sqlite3_backup_step", "std::filesystem::rename", "std::remove", "::unlink(",
    )
    require(
        "restore_has_no_private_reconstruction_namespace",
        all(token not in restore for token in forbidden_restore),
        "restore must not create, pre-delete, clean up, or rename a writable SQLite staging family",
    )
    require(
        "quiescence_rejects_sidecars_instead_of_deleting_them",
        quiescence.count("verify_sidecars_absent_or_throw") >= 3
        and "verify_open_database_or_throw" in quiescence
        and all(token not in quiescence for token in ("std::remove", "::unlink(", "unlink_sqlite_family")),
        "destination WAL, SHM, and journal names are evidence failures, not cleanup authority",
    )
    require(
        "binary_atomic_publication_is_explicitly_typed",
        "std::span<const unsigned char> payload" in text["publisher_header"]
        and "write_sync_file_atomically_with_observer_or_throw" in text["publisher_internal"]
        and "publish_posix_or_throw(normalized_path, payload" in text["publisher_source"],
        "exact SQLite bytes must not be coerced through a text-only API",
    )
    require(
        "snapshot_seal_owns_exact_copy_publication",
        "publish_exact_copy_atomically_or_throw" in text["seal_header"]
        and "serialized_bytes_" in text["seal_source"]
        and "write_sync_file_atomically_with_observer_or_throw" in text["seal_source"],
        "the move-only byte capability, not a reopened source pathname, authorizes publication",
    )
    require(
        "focused_adversarial_test_is_registered",
        "anonsync_sqlite_restore_namespace_authority_test" in text["cmake"]
        and "foreign-predictable-temp" in text["test"]
        and "foreign-sidecar-authority" in text["test"],
        "CTest preserves foreign predictable names and all three SQLite sidecar classes",
    )
    require(
        "source_audit_is_registered",
        "anonsync_sqlite_restore_publication_source_audit" in text["cmake"],
        "architectural drift fails the normal CTest gate",
    )

    violations = [check.check_id for check in checks if not check.passed]
    result = {
        "format": "anonsync-sqlite-restore-publication-audit-v1",
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
