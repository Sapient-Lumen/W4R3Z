#!/usr/bin/env python3
"""Process-level proof for sealed, crash-recoverable replica bootstrap.

The shipped executable is the only authority exercised here. The corpus proves
that fresh init publishes an exact immutable pre-commit record and private
fully-bound SQLite stores, init-resume is idempotent without schema or
membership repair for committed deployments, a sealed rollback-journal genesis
image is promoted to WAL after restart, genesis partial store sets can be
completed only against the record, advanced partial sets fail closed, every
present database is identity-attested before an earlier missing database can be
created, unbound or sidecar-contaminated SQLite candidates are not adopted, and
committed deployments are never repaired by minting a missing authority store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import tempfile
from typing import Any, NoReturn, Sequence


_RECORD_PATH_DOMAIN = b"anonsync:replica-bootstrap-record-path:v1\n"
_DATABASE_SUFFIXES = ("", "-journal", "-wal", "-shm")


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def run_success(
    command: Sequence[str], *, timeout: float = 30.0
) -> tuple[dict[str, Any], bytes]:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if completed.returncode != 0:
        fail(
            f"command failed with status {completed.returncode}: "
            f"{' '.join(command)}\nstdout:\n{completed.stdout!r}\n"
            f"stderr:\n{completed.stderr.decode(errors='replace')}"
        )
    if completed.stderr:
        fail(
            f"successful command wrote diagnostics: {' '.join(command)}\n"
            f"{completed.stderr.decode(errors='replace')}"
        )
    try:
        value = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(
            f"command did not publish one UTF-8 JSON value: "
            f"{' '.join(command)}: {error}; stdout={completed.stdout!r}"
        )
    if not isinstance(value, dict):
        fail(f"command JSON is not an object: {' '.join(command)}")
    return value, completed.stdout


def run_failure(
    command: Sequence[str],
    *,
    stderr_contains: str,
    timeout: float = 30.0,
) -> bytes:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if completed.returncode != 1:
        fail(
            f"command returned {completed.returncode}, expected 1: "
            f"{' '.join(command)}\nstdout:\n{completed.stdout!r}\n"
            f"stderr:\n{completed.stderr.decode(errors='replace')}"
        )
    if completed.stdout:
        fail(
            f"failed command published stdout: {' '.join(command)}\n"
            f"{completed.stdout!r}"
        )
    stderr = completed.stderr.decode(errors="replace")
    if stderr_contains not in stderr:
        fail(
            f"failed command diagnostic omitted {stderr_contains!r}: "
            f"{' '.join(command)}\nstderr:\n{stderr}"
        )
    return completed.stderr


def record_path(manifest_path: Path) -> Path:
    digest = hashlib.sha256(
        _RECORD_PATH_DOMAIN + str(manifest_path).encode("utf-8")
    ).hexdigest()
    return manifest_path.parent / f".anonsync-replica-bootstrap-{digest}.json"


def assert_private_regular_file(path: Path, label: str) -> None:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        fail(f"{label} is not a non-symlink regular file: {path}")
    if stat.S_IMODE(info.st_mode) != 0o600:
        fail(f"{label} mode is {oct(stat.S_IMODE(info.st_mode))}, expected 0o600")


def verify_exact_recorded_manifest(
    manifest_path: Path,
    exact_stdout: bytes,
    expected_profile: str,
    label: str,
) -> dict[str, Any]:
    durable = manifest_path.read_bytes()
    record = record_path(manifest_path)
    recorded = record.read_bytes()
    if durable != exact_stdout or recorded != exact_stdout:
        fail(f"{label} final manifest, record, and stdout are not byte-identical")
    assert_private_regular_file(manifest_path, f"{label} final manifest")
    assert_private_regular_file(record, f"{label} bootstrap record")
    value = json.loads(exact_stdout)
    if value.get("profile") != expected_profile:
        fail(
            f"{label} profile is {value.get('profile')!r}, "
            f"expected {expected_profile!r}"
        )
    if value.get("manifest_path") != str(manifest_path):
        fail(f"{label} manifest path is not self-bound")
    return value


def clear_directory(directory: Path) -> None:
    for child in tuple(directory.iterdir()):
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def remove_database_family(database: Path) -> None:
    for suffix in _DATABASE_SUFFIXES:
        candidate = Path(str(database) + suffix)
        try:
            candidate.unlink()
        except FileNotFoundError:
            pass


def assert_database_family_absent(database: Path, label: str) -> None:
    present = [str(database) + suffix for suffix in _DATABASE_SUFFIXES
               if Path(str(database) + suffix).exists()]
    if present:
        fail(f"{label} unexpectedly materialized database family entries: {present}")


def assert_clean_private_database(database: Path, label: str) -> None:
    assert_private_regular_file(database, label)
    for suffix in _DATABASE_SUFFIXES[1:]:
        sidecar = Path(str(database) + suffix)
        if sidecar.exists():
            fail(f"{label} retained unexpected SQLite sidecar: {sidecar}")


def sqlite_journal_mode(database: Path) -> str:
    connection = sqlite3.connect(
        f"file:{database}?mode=rw", uri=True, isolation_level=None
    )
    try:
        row = connection.execute("PRAGMA main.journal_mode;").fetchone()
        if row is None or not isinstance(row[0], str):
            fail(f"SQLite returned no journal mode for {database}")
        return row[0].lower()
    finally:
        connection.close()


def set_sqlite_journal_mode_delete(database: Path) -> None:
    connection = sqlite3.connect(
        f"file:{database}?mode=rw", uri=True, isolation_level=None
    )
    try:
        row = connection.execute("PRAGMA main.journal_mode=DELETE;").fetchone()
        if row is None or str(row[0]).lower() != "delete":
            fail(f"could not place bootstrap fixture in DELETE mode: {database}")
    finally:
        connection.close()
    if sqlite_journal_mode(database) != "delete":
        fail(f"bootstrap fixture did not retain DELETE mode: {database}")


def create_unbound_sqlite_database(database: Path) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "CREATE TABLE unrelated_authority(id INTEGER PRIMARY KEY, value TEXT);"
        )
        connection.execute(
            "INSERT INTO unrelated_authority(value) VALUES('foreign');"
        )
        connection.commit()
    finally:
        connection.close()
    database.chmod(0o600)


def init_sender(replica: Path, root: Path, stem: str) -> tuple[dict[str, Any], bytes]:
    root.mkdir()
    payload = root / "payload"
    payload.mkdir()
    return run_success([
        str(replica), "init",
        "--manifest", str(root / "deployment.json"),
        "--replica-db", str(root / "replica.db"),
        "--payload-root", str(payload),
        "--folder", f"folder{stem}",
        "--local-device", f"device{stem}",
        "--local-epoch", "1",
        "--max-payload-bytes", "1048576",
    ])


def init_receiver(replica: Path, root: Path, stem: str) -> tuple[dict[str, Any], bytes]:
    root.mkdir()
    files = root / "files"
    files.mkdir()
    return run_success([
        str(replica), "init",
        "--manifest", str(root / "deployment.json"),
        "--replica-db", str(root / "replica.db"),
        "--effect-db", str(root / "effect.db"),
        "--files-root", str(files),
        "--membership-db", str(root / "membership.db"),
        "--anchor-db", str(root / "anchor.db"),
        "--folder", f"folder{stem}",
        "--local-device", f"device{stem}",
        "--local-epoch", "1",
        "--max-payload-bytes", "1048576",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", type=Path, required=True)
    arguments = parser.parse_args()
    replica = arguments.replica.resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix="anonsync-bootstrap-resume-") as raw:
        root = Path(raw)

        # Fresh record-first sender bootstrap and committed idempotence.
        sender = root / "sender"
        sender_manifest = sender / "deployment.json"
        sender_value, sender_exact = init_sender(replica, sender, "a")
        verify_exact_recorded_manifest(
            sender_manifest, sender_exact, "sender", "fresh sender")
        resumed_value, resumed_exact = run_success([
            str(replica), "init-resume", "--manifest", str(sender_manifest)
        ])
        if resumed_exact != sender_exact or resumed_value != sender_value:
            fail("committed init-resume did not return the exact recorded manifest")

        # All exact stores may be operationally advanced when none is missing:
        # loss of only the final commit marker can be recovered from the record.
        source = sender / "source.txt"
        source.write_bytes(b"advanced complete deployment\n")
        enqueue, _ = run_success([
            str(replica), "enqueue-file",
            "--manifest", str(sender_manifest),
            "--destination-device", "peerone",
            "--canonical-path", "documents/advanced.txt",
            "--source-file", str(source),
        ])
        if enqueue.get("operation_id") is None:
            fail("enqueue did not advance the complete sender deployment")
        sender_manifest.unlink()
        advanced_value, advanced_exact = run_success([
            str(replica), "init-resume", "--manifest", str(sender_manifest)
        ])
        if advanced_exact != sender_exact or advanced_value != sender_value:
            fail("complete advanced resume changed the recorded deployment")
        status_value, _ = run_success([
            str(replica), "status", "--manifest", str(sender_manifest)
        ])
        if status_value.get("replica_evidence_operations") != 1:
            fail("complete advanced resume lost the durable operation")

        # A genesis partial set may create exactly the missing payload store.
        partial_sender = root / "partial-sender"
        partial_manifest = partial_sender / "deployment.json"
        _, partial_exact = init_sender(replica, partial_sender, "b")
        partial_manifest.unlink()
        clear_directory(partial_sender / "payload")
        partial_value, partial_resumed_exact = run_success([
            str(replica), "init-resume", "--manifest", str(partial_manifest)
        ])
        if partial_resumed_exact != partial_exact:
            fail("genesis payload resume changed the exact recorded manifest")
        if partial_value.get("deployment_id") != json.loads(partial_exact).get(
            "deployment_id"
        ):
            fail("genesis payload resume changed deployment identity")
        verify_exact_recorded_manifest(
            partial_manifest, partial_exact, "sender", "partial sender resume")
        if not any((partial_sender / "payload").iterdir()):
            fail("partial sender resume did not recreate the payload identity")

        # A genesis receiver can likewise recreate one absent SQLite role.
        receiver = root / "receiver"
        receiver_manifest = receiver / "deployment.json"
        _, receiver_exact = init_receiver(replica, receiver, "c")
        receiver_manifest.unlink()
        remove_database_family(receiver / "replica.db")
        _, receiver_resumed_exact = run_success([
            str(replica), "init-resume", "--manifest", str(receiver_manifest)
        ])
        if receiver_resumed_exact != receiver_exact:
            fail("genesis receiver resume changed the exact recorded manifest")
        if not (receiver / "replica.db").is_file():
            fail("genesis receiver resume did not recreate the missing replica DB")
        verify_exact_recorded_manifest(
            receiver_manifest, receiver_exact, "receiver", "receiver resume")
        for name in ("replica.db", "effect.db", "membership.db", "anchor.db"):
            assert_clean_private_database(
                receiver / name, f"receiver resume {name}")

        # The exact create-new SQLite image is durable before WAL promotion.
        # Model a crash after namespace publication by returning one clean,
        # fully-bound main file to rollback-journal mode, removing only the
        # final commit marker, and resuming through the shipped executable.
        rollback_resume = root / "rollback-resume"
        rollback_manifest = rollback_resume / "deployment.json"
        _, rollback_exact = init_receiver(replica, rollback_resume, "i")
        rollback_manifest.unlink()
        set_sqlite_journal_mode_delete(rollback_resume / "replica.db")
        _, rollback_resumed_exact = run_success([
            str(replica), "init-resume", "--manifest", str(rollback_manifest)
        ])
        if rollback_resumed_exact != rollback_exact:
            fail("rollback-image recovery changed the exact recorded manifest")
        if sqlite_journal_mode(rollback_resume / "replica.db") != "wal":
            fail("rollback-image recovery did not promote the sealed DB to WAL")
        verify_exact_recorded_manifest(
            rollback_manifest, rollback_exact, "receiver",
            "sealed rollback-image resume")
        for name in ("replica.db", "effect.db", "membership.db", "anchor.db"):
            assert_clean_private_database(
                rollback_resume / name, f"sealed rollback-image resume {name}")

        # A rollback-mode candidate with any sidecar is not the canonical
        # create-new image and must fail before final-manifest publication.
        contaminated = root / "rollback-sidecar"
        contaminated_manifest = contaminated / "deployment.json"
        init_receiver(replica, contaminated, "j")
        contaminated_manifest.unlink()
        set_sqlite_journal_mode_delete(contaminated / "replica.db")
        contaminated_journal = Path(str(contaminated / "replica.db") + "-journal")
        contaminated_journal.write_bytes(b"not a sealed genesis namespace")
        contaminated_journal.chmod(0o600)
        run_failure(
            [
                str(replica), "init-resume",
                "--manifest", str(contaminated_manifest),
            ],
            stderr_contains="SQLite sidecar must be absent",
        )
        if contaminated_manifest.exists():
            fail("rollback-sidecar rejection published the final manifest")

        # A namespace entry is never treated as an empty slot merely because
        # it is an otherwise valid SQLite file. Exact role/deployment binding
        # must fail, and the unrelated file must not be replaced.
        unbound = root / "unbound-main"
        unbound_manifest = unbound / "deployment.json"
        init_receiver(replica, unbound, "k")
        unbound_manifest.unlink()
        remove_database_family(unbound / "replica.db")
        create_unbound_sqlite_database(unbound / "replica.db")
        unbound_before = hashlib.sha256(
            (unbound / "replica.db").read_bytes()).hexdigest()
        run_failure(
            [str(replica), "init-resume", "--manifest", str(unbound_manifest)],
            stderr_contains="store-set binding",
        )
        unbound_after = hashlib.sha256(
            (unbound / "replica.db").read_bytes()).hexdigest()
        if unbound_before != unbound_after:
            fail("unbound SQLite rejection mutated or replaced the selected file")
        if unbound_manifest.exists():
            fail("unbound SQLite rejection published the final manifest")

        # Identity is attested across all present DBs before a missing earlier
        # role may be created. A copied foreign effect DB must fail first.
        target = root / "identity-target"
        foreign = root / "identity-foreign"
        target_manifest = target / "deployment.json"
        init_receiver(replica, target, "d")
        init_receiver(replica, foreign, "e")
        target_manifest.unlink()
        remove_database_family(target / "replica.db")
        remove_database_family(target / "effect.db")
        shutil.copy2(foreign / "effect.db", target / "effect.db")
        run_failure(
            [str(replica), "init-resume", "--manifest", str(target_manifest)],
            stderr_contains="store-set binding",
        )
        assert_database_family_absent(
            target / "replica.db",
            "foreign-binding rejection",
        )
        if target_manifest.exists():
            fail("foreign-binding rejection published the final manifest")

        # Advanced present state cannot authorize creation of a missing store.
        advanced_partial = root / "advanced-partial"
        advanced_partial_manifest = advanced_partial / "deployment.json"
        init_sender(replica, advanced_partial, "f")
        advanced_source = advanced_partial / "source.txt"
        advanced_source.write_bytes(b"state that forbids partial recomposition")
        run_success([
            str(replica), "enqueue-file",
            "--manifest", str(advanced_partial_manifest),
            "--destination-device", "peertwo",
            "--canonical-path", "advanced.txt",
            "--source-file", str(advanced_source),
        ])
        advanced_partial_manifest.unlink()
        clear_directory(advanced_partial / "payload")
        run_failure(
            [
                str(replica), "init-resume",
                "--manifest", str(advanced_partial_manifest),
            ],
            stderr_contains="advanced beyond bootstrap genesis",
        )
        if advanced_partial_manifest.exists():
            fail("advanced partial rejection published the final manifest")
        if any((advanced_partial / "payload").iterdir()):
            fail("advanced partial rejection recreated the missing payload store")

        # A committed deployment cannot recreate a missing authority store
        # or enter the role-schema/membership repair frontier, despite having a
        # valid retained record.
        committed_missing = root / "committed-missing"
        committed_manifest = committed_missing / "deployment.json"
        init_receiver(replica, committed_missing, "g")
        remove_database_family(committed_missing / "replica.db")
        run_failure(
            [str(replica), "init-resume", "--manifest", str(committed_manifest)],
            stderr_contains="store set remains incomplete",
        )
        assert_database_family_absent(
            committed_missing / "replica.db", "committed missing-store refusal"
        )
        if not committed_manifest.is_file():
            fail("committed missing-store refusal removed the commit marker")

        # A missing SQLite main with any orphan sidecar is not an empty slot.
        orphan = root / "orphan-sidecar"
        orphan_manifest = orphan / "deployment.json"
        init_sender(replica, orphan, "h")
        orphan_manifest.unlink()
        remove_database_family(orphan / "replica.db")
        Path(str(orphan / "replica.db") + "-wal").write_bytes(b"not authority")
        run_failure(
            [str(replica), "init-resume", "--manifest", str(orphan_manifest)],
            stderr_contains="must be absent when the main database is absent",
        )
        if (orphan / "replica.db").exists() or orphan_manifest.exists():
            fail("orphan-sidecar refusal minted a DB or final manifest")

        # The deterministic pathname cannot turn a copied record into authority:
        # the exact bytes remain bound to their original final manifest path.
        copied_record = root / "copied-record"
        copied_record.mkdir()
        copied_manifest = copied_record / "deployment.json"
        copied_record_path = record_path(copied_manifest)
        shutil.copy2(record_path(sender_manifest), copied_record_path)
        run_failure(
            [str(replica), "init-resume", "--manifest", str(copied_manifest)],
            stderr_contains="manifest_path does not bind the expected final file name",
        )
        if copied_manifest.exists():
            fail("copied bootstrap record published a final manifest")

    print("anonsync replica bootstrap resume process test passed (12 scenarios)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - test driver must report context
        print(f"FAIL: {error}", file=os.sys.stderr)
        raise SystemExit(1)
