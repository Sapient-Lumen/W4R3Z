#!/usr/bin/env python3
"""Process-level proof for the bounded AnonSync replica product spine.

Every authority transition launches the shipped executable. The proof covers
explicit store-set bootstrap, exact deployment-manifest gating, non-creating
operational failure paths, membership publication, durable enqueue, clock
quarantine/recovery, separate TLS client/server processes, exact filesystem
publication, bounded multi-session supervision, and terminal sender settlement.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Sequence


def fail(message: str) -> "NoReturn":
    raise RuntimeError(message)


def run_json_output(
    command: Sequence[str], *, timeout: float = 30.0
) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        fail(
            f"command failed with status {completed.returncode}: "
            f"{' '.join(command)}\nstdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(
            f"command did not return one JSON object: {' '.join(command)}: "
            f"{error}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"command JSON is not an object: {' '.join(command)}")
    if completed.stderr:
        fail(
            f"successful command wrote diagnostics: {' '.join(command)}\n"
            f"{completed.stderr}"
        )
    return value, completed.stdout


def run_json(command: Sequence[str], *, timeout: float = 30.0) -> dict[str, Any]:
    return run_json_output(command, timeout=timeout)[0]


def run_failure(
    command: Sequence[str],
    *,
    stderr_contains: str,
    expected_returncode: int = 1,
    timeout: float = 30.0,
) -> None:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != expected_returncode:
        fail(
            f"command returned {completed.returncode}, expected "
            f"{expected_returncode}: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if completed.stdout:
        fail(
            f"failed command published stdout: {' '.join(command)}\n"
            f"{completed.stdout}"
        )
    if stderr_contains not in completed.stderr:
        fail(
            f"failed command diagnostic omitted {stderr_contains!r}: "
            f"{' '.join(command)}\nstderr:\n{completed.stderr}"
        )


def openssl(openssl_executable: str, arguments: Sequence[str]) -> None:
    completed = subprocess.run(
        [openssl_executable, *arguments],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30.0,
    )
    if completed.returncode != 0:
        fail(
            f"openssl {' '.join(arguments)} failed with status "
            f"{completed.returncode}: {completed.stderr}"
        )


def generate_tls_fixture(root: Path, openssl_executable: str) -> None:
    extension = root / "leaf.ext"
    extension.write_text(
        "basicConstraints=critical,CA:FALSE\n"
        "keyUsage=critical,digitalSignature\n"
        "extendedKeyUsage=serverAuth,clientAuth\n",
        encoding="ascii",
    )
    openssl(openssl_executable, [
        "genpkey", "-algorithm", "ED25519", "-out", str(root / "ca.key")
    ])
    openssl(openssl_executable, [
        "req", "-new", "-x509", "-key", str(root / "ca.key"),
        "-out", str(root / "ca.pem"), "-subj", "/CN=AnonSync-CLI-Test-CA",
        "-days", "1", "-addext", "basicConstraints=critical,CA:TRUE",
        "-addext", "keyUsage=critical,keyCertSign,cRLSign",
    ])
    for name in ("sender", "receiver"):
        openssl(openssl_executable, [
            "genpkey", "-algorithm", "ED25519",
            "-out", str(root / f"{name}.key"),
        ])
        openssl(openssl_executable, [
            "req", "-new", "-key", str(root / f"{name}.key"),
            "-out", str(root / f"{name}.csr"),
            "-subj", f"/CN=AnonSync-CLI-{name}",
        ])
        openssl(openssl_executable, [
            "x509", "-req", "-in", str(root / f"{name}.csr"),
            "-CA", str(root / "ca.pem"), "-CAkey", str(root / "ca.key"),
            "-CAcreateserial", "-out", str(root / f"{name}.pem"),
            "-days", "1", "-extfile", str(extension),
        ])


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def linux_port_is_listening(port: int) -> bool:
    encoded_port = f"{port:04X}"
    for filename in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            lines = Path(filename).read_text(encoding="ascii").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) < 4:
                continue
            local = fields[1]
            state = fields[3]
            if local.rsplit(":", 1)[-1].upper() == encoded_port and state == "0A":
                return True
    return False


def wait_until_listening(process: subprocess.Popen[str], port: int) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"serve-one exited before listening with status "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        if linux_port_is_listening(port):
            return
        time.sleep(0.02)
    fail(f"serve-one did not expose port {port} before the readiness deadline")


def expect_fields(value: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, wanted in expected.items():
        observed = value.get(key)
        if observed != wanted:
            fail(
                f"{label} field {key!r} was {observed!r}, expected {wanted!r}: "
                f"{json.dumps(value, sort_keys=True)}"
            )


def verify_deployment_manifest(
    value: dict[str, Any],
    stdout: str,
    manifest_path: Path,
    expected: dict[str, Any],
    label: str,
) -> None:
    durable = manifest_path.read_text(encoding="utf-8")
    if durable != stdout:
        fail(f"{label} stdout differs from the immutable durable manifest")
    if json.loads(durable) != value:
        fail(f"{label} parsed stdout differs from the durable manifest object")
    expect_fields(value, expected, label)
    if manifest_path.stat().st_mode & 0o777 != 0o600:
        fail(f"{label} manifest is not private mode 0600")

    require_lowercase_sha256(value.get("deployment_id"), f"{label} deployment ID")
    require_lowercase_sha256(value.get("manifest_digest"), f"{label} manifest digest")
    wanted_digest = canonical_manifest_digest(durable)
    if value.get("manifest_digest") != wanted_digest:
        fail(f"{label} self-digest does not bind the exact unsigned document")


def require_lowercase_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(byte not in "0123456789abcdef" for byte in value)
    ):
        fail(f"{label} is not a lowercase 256-bit hexadecimal value: {value!r}")
    return value


def canonical_manifest_digest(exact_document: str) -> str:
    marker = ',"manifest_digest":'
    if exact_document.count(marker) != 1 or not exact_document.endswith("}\n"):
        fail("deployment manifest is not a canonical terminal-digest document")
    unsigned_prefix, _ = exact_document[:-1].split(marker, 1)
    unsigned_document = unsigned_prefix + "}"
    return hashlib.sha256(
        b"anonsync:replica-deployment-manifest:v2\n" +
        unsigned_document.encode("utf-8")
    ).hexdigest()


def forge_manifest_deployment_id(
    exact_document: str,
    prior_deployment_id: str,
    forged_deployment_id: str,
) -> str:
    require_lowercase_sha256(prior_deployment_id, "prior deployment ID")
    require_lowercase_sha256(forged_deployment_id, "forged deployment ID")
    before = f'"deployment_id":"{prior_deployment_id}"'
    after = f'"deployment_id":"{forged_deployment_id}"'
    if exact_document.count(before) != 1:
        fail("manifest deployment-ID substitution is not unique")
    replaced = exact_document.replace(before, after, 1)
    marker = ',"manifest_digest":'
    unsigned_prefix, _ = replaced[:-1].split(marker, 1)
    forged_digest = canonical_manifest_digest(
        unsigned_prefix + marker + '"' + ('0' * 64) + '"}\n'
    )
    return unsigned_prefix + marker + json.dumps(forged_digest) + "}\n"


def append_digest_string(digest: Any, value: str) -> None:
    encoded = value.encode("utf-8")
    digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
    digest.update(encoded)


def expected_database_binding_digest(
    path: Path,
    deployment: dict[str, Any],
    role: str,
    application_id: int,
) -> str:
    digest = hashlib.sha256()
    for value in (
        "anonsync:sqlite-deployment-binding:v1",
        "anonsync-sqlite-deployment-binding-v1",
        deployment["deployment_id"],
        deployment["manifest_digest"],
        deployment["manifest_path"],
        role,
        str(path),
        deployment["folder_id"],
        deployment["local_device_id"],
    ):
        append_digest_string(digest, value)
    digest.update(int(deployment["local_epoch"]).to_bytes(
        8, byteorder="big", signed=False
    ))
    digest.update(application_id.to_bytes(8, byteorder="big", signed=False))
    return digest.hexdigest()


def verify_database_binding(
    path: Path,
    deployment: dict[str, Any],
    role: str,
    application_id: int,
    label: str,
) -> None:
    uri = path.as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as database:
        observed_application_id = int(
            database.execute("PRAGMA application_id").fetchone()[0]
        )
        row = database.execute(
            "SELECT format,deployment_id,manifest_digest,manifest_path,"
            "store_role,database_path,folder_id,local_device_id,local_epoch,"
            "sqlite_application_id,binding_digest "
            "FROM anonsync_store_set_binding ORDER BY id"
        ).fetchall()
    if observed_application_id != application_id:
        fail(
            f"{label} application_id was {observed_application_id}, "
            f"expected {application_id}"
        )
    if len(row) != 1:
        fail(f"{label} does not contain exactly one store-set binding row")
    observed = row[0]
    expected = (
        "anonsync-sqlite-deployment-binding-v1",
        deployment["deployment_id"],
        deployment["manifest_digest"],
        deployment["manifest_path"],
        role,
        str(path),
        deployment["folder_id"],
        deployment["local_device_id"],
        deployment["local_epoch"],
        application_id,
    )
    if tuple(observed[:-1]) != expected:
        fail(
            f"{label} binding row does not match its deployment: "
            f"{observed!r}"
        )
    wanted_digest = expected_database_binding_digest(
        path, deployment, role, application_id
    )
    if observed[-1] != wanted_digest:
        fail(
            f"{label} binding digest was {observed[-1]!r}, "
            f"expected {wanted_digest!r}"
        )


def frame_identity_field(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return str(len(encoded)).encode("ascii") + b":" + encoded


def expected_product_payload_identity(deployment: dict[str, Any]) -> bytes:
    fields = (
        deployment["deployment_id"],
        deployment["manifest_digest"],
        deployment["manifest_path"],
        deployment["folder_id"],
        deployment["local_device_id"],
        str(deployment["local_epoch"]),
        "anonsync:sync-replica-file-payload-store-flock-lease:v1",
    )
    return (
        b"anonsync:sync-replica-file-payload-store-identity:v3\n" +
        b"".join(frame_identity_field(value) for value in fields)
    )


def verify_product_payload_identity(
    path: Path, deployment: dict[str, Any], label: str
) -> None:
    marker = path / ".anonsync-payload-store-identity-v3-reader-fence-v1"
    if not marker.is_file() or marker.is_symlink():
        fail(f"{label} product payload identity marker is absent or not regular")
    observed = marker.read_bytes()
    expected = expected_product_payload_identity(deployment)
    if observed != expected:
        fail(f"{label} product payload identity bytes are not deployment-bound")
    if marker.stat().st_mode & 0o777 != 0o600:
        fail(f"{label} product payload identity marker is not private mode 0600")


def remove_database_family(path: Path) -> None:
    for member in database_family(path):
        try:
            member.unlink()
        except FileNotFoundError:
            pass


def clone_database_for_recomposition(source: Path, destination: Path) -> None:
    source_uri = source.as_uri() + "?mode=ro"
    with closing(sqlite3.connect(source_uri, uri=True)) as source_database:
        with closing(sqlite3.connect(destination)) as destination_database:
            source_database.backup(destination_database)
            mode = destination_database.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()[0]
            destination_database.execute("PRAGMA synchronous=FULL")
            destination_database.commit()
    if mode != "wal":
        fail(f"recomposition clone did not enter WAL mode: {mode}")


def database_family(path: Path) -> tuple[Path, Path, Path, Path]:
    return (
        path,
        Path(f"{path}-journal"),
        Path(f"{path}-wal"),
        Path(f"{path}-shm"),
    )


def database_semantic_digest(path: Path) -> str:
    uri = path.as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as database:
        application_id = int(
            database.execute("PRAGMA application_id").fetchone()[0]
        )
        dump = "\n".join(database.iterdump())
    material = f"application_id={application_id}\n{dump}\n".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def database_family_snapshot(path: Path) -> dict[str, tuple[Any, ...]]:
    result: dict[str, tuple[Any, ...]] = {}
    for member in database_family(path):
        if member.exists():
            status = member.stat(follow_symlinks=False)
            result[member.name] = (
                status.st_mode & 0o777,
                status.st_dev,
                status.st_ino,
                status.st_nlink,
                status.st_size,
                status.st_mtime_ns,
                status.st_ctime_ns,
                hashlib.sha256(member.read_bytes()).hexdigest(),
            )
    return result


def require_database_family_absent(path: Path, label: str) -> None:
    present = [member for member in database_family(path) if member.exists()]
    if present:
        fail(f"{label} created database-family members: {present}")


def detach_database_family(path: Path, backup_root: Path) -> list[tuple[Path, Path]]:
    backup_root.mkdir(mode=0o700)
    moved: list[tuple[Path, Path]] = []
    for member in database_family(path):
        if member.exists():
            backup = backup_root / member.name
            member.rename(backup)
            moved.append((member, backup))
    if not any(original == path for original, _ in moved):
        fail(f"database family has no main file to detach: {path}")
    return moved


def restore_database_family(moved: Sequence[tuple[Path, Path]]) -> None:
    for original, backup in moved:
        if original.exists():
            fail(f"failure path recreated detached database member: {original}")
        backup.rename(original)


def directory_snapshot(path: Path) -> list[tuple[str, str, int, str]]:
    result: list[tuple[str, str, int, str]] = []
    for entry in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
        relative = entry.relative_to(path).as_posix()
        mode = entry.lstat().st_mode & 0o777
        if entry.is_symlink():
            result.append((relative, "symlink", mode, os.readlink(entry)))
        elif entry.is_dir():
            result.append((relative, "directory", mode, ""))
        elif entry.is_file():
            result.append((
                relative,
                "file",
                mode,
                hashlib.sha256(entry.read_bytes()).hexdigest(),
            ))
        else:
            result.append((relative, "other", mode, ""))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    arguments = parser.parse_args()
    replica = arguments.replica.resolve(strict=True)
    openssl_executable = shutil.which("openssl")
    if openssl_executable is None:
        fail("openssl executable is required for the replica CLI process test")

    with tempfile.TemporaryDirectory(prefix="anonsync-replica-cli-") as temporary:
        root = Path(temporary)
        os.chmod(root, 0o700)
        database_root = root / "db"
        payload_root = root / "sender-payload"
        files_root = root / "receiver-files"
        destination_parent = files_root / "nested"
        certificates = root / "certificates"
        for directory in (
            database_root, payload_root, files_root, certificates,
        ):
            directory.mkdir(mode=0o700)

        sender_database = database_root / "sender.sqlite"
        sender_manifest = database_root / "sender-deployment.json"
        receiver_database = database_root / "receiver.sqlite"
        effect_database = database_root / "effect.sqlite"
        membership_database = database_root / "membership.sqlite"
        membership_anchor_database = database_root / "membership-anchor.sqlite"
        receiver_manifest = database_root / "receiver-deployment.json"

        payload = b"AnonSync product-spine process proof\x00\xff\n"
        source = root / "source.bin"
        source.write_bytes(payload)
        batch_payloads = (
            b"AnonSync bounded batch payload alpha\x00\n",
            b"AnonSync bounded batch payload beta\xff\n",
        )
        batch_sources = (root / "batch-alpha.bin", root / "batch-beta.bin")
        for batch_source, batch_payload in zip(batch_sources, batch_payloads):
            batch_source.write_bytes(batch_payload)
        generate_tls_fixture(certificates, openssl_executable)

        # No operational command may bootstrap from a missing configuration
        # document, even when every independently supplied work argument is valid.
        missing_manifest = database_root / "missing-deployment.json"
        run_failure([
            str(replica), "status", "--manifest", str(missing_manifest),
        ], stderr_contains="open failed")
        run_failure([
            str(replica), "enqueue-file", "--manifest", str(missing_manifest),
            "--destination-device", "receiver",
            "--canonical-path", "nested/must-not-exist.bin",
            "--source-file", str(source),
        ], stderr_contains="open failed")
        if missing_manifest.exists() or any(payload_root.iterdir()):
            fail("missing-manifest operation minted deployment or payload authority")

        # Bootstrap authority still must not adopt and rewrite an unrelated
        # persistent SQLite database. The prepared manifest is not published.
        unrelated_database = database_root / "unrelated.sqlite"
        with closing(sqlite3.connect(unrelated_database)) as unrelated:
            unrelated.execute("CREATE TABLE sentinel(value TEXT NOT NULL)")
            unrelated.execute("INSERT INTO sentinel VALUES ('unchanged')")
            journal_mode = unrelated.execute("PRAGMA journal_mode").fetchone()[0]
            unrelated.commit()
        if journal_mode != "delete":
            fail(f"unrelated SQLite fixture did not begin in DELETE mode: {journal_mode}")
        unrelated_before = database_family_snapshot(unrelated_database)
        wrong_profile_manifest = database_root / "wrong-profile-deployment.json"
        names_before = sorted(entry.name for entry in database_root.iterdir())
        run_failure([
            str(replica), "init", "--manifest", str(wrong_profile_manifest),
            "--replica-db", str(unrelated_database),
            "--folder", "product-spine", "--local-device", "sender",
            "--local-epoch", "1",
        ], stderr_contains="must be absent for fresh bootstrap")
        if database_family_snapshot(unrelated_database) != unrelated_before:
            fail("bootstrap rewrote an unrelated persistent SQLite database")
        if wrong_profile_manifest.exists():
            fail("failed wrong-profile bootstrap published a deployment manifest")
        if sorted(entry.name for entry in database_root.iterdir()) != names_before:
            fail("failed wrong-profile bootstrap leaked a prepared manifest entry")

        # Fresh bootstrap is deliberately non-adopting across the entire
        # selected namespace. A preseeded payload tree must fail before the
        # first SQLite file or manifest entry is created.
        preseeded_payload_root = root / "preseeded-payload"
        preseeded_payload_root.mkdir(mode=0o700)
        (preseeded_payload_root / "sentinel.bin").write_bytes(
            b"must-not-be-adopted"
        )
        preseeded_payload_before = directory_snapshot(preseeded_payload_root)
        preseeded_payload_database = database_root / "preseeded-payload.sqlite"
        preseeded_payload_manifest = (
            database_root / "preseeded-payload-deployment.json"
        )
        run_failure([
            str(replica), "init", "--manifest", str(preseeded_payload_manifest),
            "--replica-db", str(preseeded_payload_database),
            "--payload-root", str(preseeded_payload_root),
            "--folder", "product-spine", "--local-device", "preseeded",
            "--local-epoch", "1",
        ], stderr_contains="payload root must be empty for fresh bootstrap")
        require_database_family_absent(
            preseeded_payload_database, "preseeded-payload bootstrap"
        )
        if preseeded_payload_manifest.exists():
            fail("preseeded-payload bootstrap published a manifest")
        if directory_snapshot(preseeded_payload_root) != preseeded_payload_before:
            fail("preseeded-payload bootstrap rewrote adopted bytes")

        # An orphan SQLite sidecar is authority-bearing state too. Main-file
        # absence alone is not enough to prove a fresh database namespace.
        sidecar_payload_root = root / "sidecar-payload"
        sidecar_payload_root.mkdir(mode=0o700)
        sidecar_database = database_root / "orphan-sidecar.sqlite"
        sidecar_wal = Path(f"{sidecar_database}-wal")
        sidecar_wal.write_bytes(b"orphan-wal-must-survive")
        os.chmod(sidecar_wal, 0o600)
        sidecar_before = database_family_snapshot(sidecar_database)
        sidecar_manifest = database_root / "orphan-sidecar-deployment.json"
        run_failure([
            str(replica), "init", "--manifest", str(sidecar_manifest),
            "--replica-db", str(sidecar_database),
            "--payload-root", str(sidecar_payload_root),
            "--folder", "product-spine", "--local-device", "sidecar",
            "--local-epoch", "1",
        ], stderr_contains="SQLite sidecar -wal must be absent for fresh bootstrap")
        if database_family_snapshot(sidecar_database) != sidecar_before:
            fail("orphan-sidecar bootstrap changed the database family")
        if sidecar_manifest.exists() or any(sidecar_payload_root.iterdir()):
            fail("orphan-sidecar bootstrap mutated another authority resource")

        # Receiver delivery roots receive the same non-adoption rule before
        # any of the four selected SQLite roles is initialized.
        preseeded_files_root = root / "preseeded-files"
        preseeded_files_root.mkdir(mode=0o700)
        (preseeded_files_root / "sentinel.bin").write_bytes(
            b"must-not-be-delivery-authority"
        )
        preseeded_files_before = directory_snapshot(preseeded_files_root)
        preseeded_receiver_paths = {
            "replica": database_root / "preseeded-receiver.sqlite",
            "effect": database_root / "preseeded-effect.sqlite",
            "membership": database_root / "preseeded-membership.sqlite",
            "anchor": database_root / "preseeded-anchor.sqlite",
        }
        preseeded_receiver_manifest = (
            database_root / "preseeded-receiver-deployment.json"
        )
        run_failure([
            str(replica), "init", "--manifest", str(preseeded_receiver_manifest),
            "--replica-db", str(preseeded_receiver_paths["replica"]),
            "--effect-db", str(preseeded_receiver_paths["effect"]),
            "--files-root", str(preseeded_files_root),
            "--membership-db", str(preseeded_receiver_paths["membership"]),
            "--anchor-db", str(preseeded_receiver_paths["anchor"]),
            "--folder", "product-spine", "--local-device", "preseeded-receiver",
            "--local-epoch", "1",
        ], stderr_contains="files root must be empty for fresh bootstrap")
        for role, path in preseeded_receiver_paths.items():
            require_database_family_absent(
                path, f"preseeded receiver {role} bootstrap"
            )
        if preseeded_receiver_manifest.exists():
            fail("preseeded receiver bootstrap published a manifest")
        if directory_snapshot(preseeded_files_root) != preseeded_files_before:
            fail("preseeded receiver bootstrap rewrote delivery-root bytes")

        # The immutable marker cannot be nested under a mutable selected root.
        overlap_database = database_root / "overlap-replica.sqlite"
        overlap_manifest = payload_root / "overlap-deployment.json"
        run_failure([
            str(replica), "init", "--manifest", str(overlap_manifest),
            "--replica-db", str(overlap_database),
            "--payload-root", str(payload_root),
            "--folder", "product-spine", "--local-device", "sender",
            "--local-epoch", "1",
        ], stderr_contains="manifest_path must not be inside payload_root")
        if overlap_manifest.exists() or overlap_database.exists() or any(
            payload_root.iterdir()
        ):
            fail("overlapping init paths mutated an authority resource")

        sender_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "sender.pem"),
        ])["spki_sha256"]
        receiver_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "receiver.pem"),
        ])["spki_sha256"]

        sender_init = [
            str(replica), "init", "--manifest", str(sender_manifest),
            "--replica-db", str(sender_database),
            "--payload-root", str(payload_root),
            "--folder", "product-spine", "--local-device", "sender",
            "--local-epoch", "1",
        ]
        sender_deployment, sender_manifest_stdout = run_json_output(sender_init)
        verify_deployment_manifest(
            sender_deployment, sender_manifest_stdout, sender_manifest, {
                "format": "anonsync-replica-deployment-manifest-v2",
                "profile": "sender", "folder_id": "product-spine",
                "local_device_id": "sender", "local_epoch": 1,
                "max_payload_bytes": 4 * 1024 * 1024,
                "manifest_path": str(sender_manifest),
                "replica_db": str(sender_database),
                "payload_root": str(payload_root), "effect_db": None,
                "files_root": None, "membership_db": None,
                "anchor_db": None, "authority_resource_count": 2,
                "sqlite_journal_mode": "wal",
                "sqlite_application_id_policy": "role-specific-v1",
                "store_internal_deployment_binding": "required-v1",
                "bootstrap_store_adoption_policy": "fresh-only-v1",
                "operational_database_open_policy": "existing-only",
                "operational_payload_open_policy": "existing-only",
                "operational_configuration_source": "deployment-manifest",
                "operational_manifest_required": True,
                "manifest_is_store_set_commit_marker": True,
                "cross_resource_atomicity": False,
            }, "sender deployment")
        sender_digest = sender_deployment["manifest_digest"]

        receiver_init = [
            str(replica), "init", "--manifest", str(receiver_manifest),
            "--replica-db", str(receiver_database),
            "--effect-db", str(effect_database),
            "--files-root", str(files_root),
            "--membership-db", str(membership_database),
            "--anchor-db", str(membership_anchor_database),
            "--folder", "product-spine", "--local-device", "receiver",
            "--local-epoch", "1",
        ]
        receiver_deployment, receiver_manifest_stdout = run_json_output(
            receiver_init
        )
        verify_deployment_manifest(
            receiver_deployment, receiver_manifest_stdout, receiver_manifest, {
                "format": "anonsync-replica-deployment-manifest-v2",
                "profile": "receiver", "folder_id": "product-spine",
                "local_device_id": "receiver", "local_epoch": 1,
                "max_payload_bytes": 4 * 1024 * 1024,
                "manifest_path": str(receiver_manifest),
                "replica_db": str(receiver_database), "payload_root": None,
                "effect_db": str(effect_database),
                "files_root": str(files_root),
                "membership_db": str(membership_database),
                "anchor_db": str(membership_anchor_database),
                "authority_resource_count": 5,
                "sqlite_journal_mode": "wal",
                "sqlite_application_id_policy": "role-specific-v1",
                "store_internal_deployment_binding": "required-v1",
                "bootstrap_store_adoption_policy": "fresh-only-v1",
                "operational_database_open_policy": "existing-only",
                "operational_payload_open_policy": "existing-only",
                "operational_configuration_source": "deployment-manifest",
                "operational_manifest_required": True,
                "manifest_is_store_set_commit_marker": True,
                "cross_resource_atomicity": False,
            }, "receiver deployment")
        receiver_digest = receiver_deployment["manifest_digest"]
        sender_deployment_id = sender_deployment["deployment_id"]
        receiver_deployment_id = receiver_deployment["deployment_id"]
        if sender_deployment_id == receiver_deployment_id:
            fail("independent bootstrap repeated a deployment identifier")
        sender_authority = {
            "deployment_id": sender_deployment_id,
            "deployment_manifest_digest": sender_digest,
        }
        receiver_authority = {
            "deployment_id": receiver_deployment_id,
            "deployment_manifest_digest": receiver_digest,
        }
        verify_database_binding(
            sender_database, sender_deployment, "replica", 0x41535201,
            "sender replica database",
        )
        verify_database_binding(
            receiver_database, receiver_deployment, "replica", 0x41535201,
            "receiver replica database",
        )
        verify_database_binding(
            effect_database, receiver_deployment, "file-effect", 0x41535202,
            "receiver effect database",
        )
        verify_database_binding(
            membership_database, receiver_deployment, "tls-membership",
            0x41535203, "receiver membership database",
        )
        verify_database_binding(
            membership_anchor_database, receiver_deployment,
            "tls-membership-anchor", 0x41535204,
            "receiver membership anchor database",
        )
        verify_product_payload_identity(
            payload_root, sender_deployment, "sender"
        )
        destination_parent.mkdir(mode=0o700)

        # The final-name claim is acquired before any store creation. Reusing a
        # committed marker with a fresh target cannot create that target.
        blocked_database = database_root / "blocked-by-manifest.sqlite"
        run_failure([
            str(replica), "init", "--manifest", str(sender_manifest),
            "--replica-db", str(blocked_database),
            "--folder", "product-spine", "--local-device", "sender",
            "--local-epoch", "1",
        ], stderr_contains="must be absent for fresh bootstrap")
        require_database_family_absent(
            blocked_database, "manifest-collision bootstrap")

        # Exact bytes copied to another pathname are not a second capability.
        copied_manifest = database_root / "copied-sender-deployment.json"
        shutil.copyfile(sender_manifest, copied_manifest)
        sender_before_copy_probe = database_family_snapshot(sender_database)
        payload_before_copy_probe = directory_snapshot(payload_root)
        run_failure([
            str(replica), "status", "--manifest", str(copied_manifest),
        ], stderr_contains="manifest_path does not bind the opened file name")
        if database_family_snapshot(sender_database) != sender_before_copy_probe:
            fail("copied manifest reached the sender database")
        if directory_snapshot(payload_root) != payload_before_copy_probe:
            fail("copied manifest reached the sender payload store")

        # A forged manifest can be internally canonical and self-digested while
        # naming the original path set. Store-internal birth attestation must
        # reject that recomposition before the payload store is opened.
        sender_manifest_exact = sender_manifest.read_text(encoding="utf-8")
        forged_deployment_id = "f" * 64
        if forged_deployment_id == sender_deployment_id:
            forged_deployment_id = "e" * 64
        forged_manifest = forge_manifest_deployment_id(
            sender_manifest_exact, sender_deployment_id, forged_deployment_id
        )
        forged_database_before = database_semantic_digest(sender_database)
        forged_payload_before = directory_snapshot(payload_root)
        sender_manifest.write_text(forged_manifest, encoding="utf-8")
        os.chmod(sender_manifest, 0o600)
        try:
            run_failure([
                str(replica), "status", "--manifest", str(sender_manifest),
            ], stderr_contains=(
                "deployment binding does not match the selected manifest"
            ))
            if database_semantic_digest(sender_database) != forged_database_before:
                fail("forged canonical manifest changed sender database semantics")
            if directory_snapshot(payload_root) != forged_payload_before:
                fail("forged canonical manifest reached the sender payload store")
        finally:
            sender_manifest.write_text(sender_manifest_exact, encoding="utf-8")
            os.chmod(sender_manifest, 0o600)

        # A database from another independently initialized deployment cannot
        # be substituted even when it has the same replica role and schema.
        sender_payload_before_replica_swap = directory_snapshot(payload_root)
        detached_sender_for_swap = detach_database_family(
            sender_database, root / "detached-sender-for-replica-swap"
        )
        try:
            clone_database_for_recomposition(receiver_database, sender_database)
            run_failure([
                str(replica), "status", "--manifest", str(sender_manifest),
            ], stderr_contains=(
                "deployment binding does not match the selected manifest"
            ))
        finally:
            remove_database_family(sender_database)
            restore_database_family(detached_sender_for_swap)
        if directory_snapshot(payload_root) != sender_payload_before_replica_swap:
            fail("same-role database substitution reached the payload store")
        verify_database_binding(
            sender_database, sender_deployment, "replica", 0x41535201,
            "restored sender replica database",
        )

        # A cross-role database substitution is rejected by the role-specific
        # SQLite header before the exact binding row can be treated as authority.
        detached_membership_for_role_swap = detach_database_family(
            membership_database, root / "detached-membership-for-role-swap"
        )
        try:
            clone_database_for_recomposition(
                membership_anchor_database, membership_database
            )
            run_failure([
                str(replica), "status", "--manifest", str(receiver_manifest),
            ], stderr_contains=(
                "application_id conflicts with the store role"
            ))
        finally:
            remove_database_family(membership_database)
            restore_database_family(detached_membership_for_role_swap)
        verify_database_binding(
            membership_database, receiver_deployment, "tls-membership",
            0x41535203, "restored receiver membership database",
        )

        # A same-path field mutation with the old digest fails before any store
        # open. Use an independent deployment so the main end-to-end pair remains
        # available for the remainder of the proof.
        tamper_payload_root = root / "tamper-payload"
        tamper_payload_root.mkdir(mode=0o700)
        tamper_database = database_root / "tamper.sqlite"
        tamper_manifest = database_root / "tamper-deployment.json"
        run_json([
            str(replica), "init", "--manifest", str(tamper_manifest),
            "--replica-db", str(tamper_database),
            "--payload-root", str(tamper_payload_root),
            "--folder", "product-spine", "--local-device", "sender",
            "--local-epoch", "1",
        ])
        tamper_deployment = json.loads(
            tamper_manifest.read_text(encoding="utf-8")
        )
        tamper_payload_exact_before = directory_snapshot(tamper_payload_root)
        sender_payload_exact_before = directory_snapshot(payload_root)
        detached_sender_payload = root / "sender-payload-for-foreign-swap"
        payload_root.rename(detached_sender_payload)
        tamper_payload_root.rename(payload_root)
        try:
            run_failure([
                str(replica), "status", "--manifest", str(sender_manifest),
            ], stderr_contains="does not bind this folder")
        finally:
            payload_root.rename(tamper_payload_root)
            detached_sender_payload.rename(payload_root)
        if directory_snapshot(payload_root) != sender_payload_exact_before:
            fail("foreign payload substitution mutated the sender payload store")
        if directory_snapshot(tamper_payload_root) != tamper_payload_exact_before:
            fail("foreign payload substitution mutated the foreign payload store")
        verify_product_payload_identity(
            payload_root, sender_deployment, "restored sender"
        )
        verify_product_payload_identity(
            tamper_payload_root, tamper_deployment, "restored foreign"
        )

        tamper_database_before = database_family_snapshot(tamper_database)
        tamper_payload_before = directory_snapshot(tamper_payload_root)
        tampered_bytes = tamper_manifest.read_text(encoding="utf-8").replace(
            '"folder_id":"product-spine"',
            '"folder_id":"product-spind"',
        )
        tamper_manifest.write_text(tampered_bytes, encoding="utf-8")
        os.chmod(tamper_manifest, 0o600)
        run_failure([
            str(replica), "status", "--manifest", str(tamper_manifest),
        ], stderr_contains="canonical fields, or self-digest conflict")
        if database_family_snapshot(tamper_database) != tamper_database_before:
            fail("tampered manifest reached its replica database")
        if directory_snapshot(tamper_payload_root) != tamper_payload_before:
            fail("tampered manifest reached its payload store")

        # Raw path/identity mixing is no longer part of the operational grammar.
        run_failure([
            str(replica), "status", "--manifest", str(sender_manifest),
            "--replica-db", str(receiver_database),
        ], stderr_contains="unknown option --replica-db")

        # A valid manifest cannot recreate a missing selected database. Enqueue
        # also proves the DB before source-byte read and payload publication.
        sender_payload_before_missing_db = directory_snapshot(payload_root)
        detached_sender = detach_database_family(
            sender_database, root / "detached-sender-database"
        )
        try:
            run_failure([
                str(replica), "enqueue-file", "--manifest", str(sender_manifest),
                "--destination-device", "receiver",
                "--canonical-path", "nested/must-not-exist.bin",
                "--source-file", str(source),
            ], stderr_contains="unable to open database file")
            require_database_family_absent(
                sender_database, "existing-only enqueue")
            if directory_snapshot(payload_root) != sender_payload_before_missing_db:
                fail("missing-database enqueue mutated the payload store")
        finally:
            restore_database_family(detached_sender)

        # A valid manifest also cannot bless an empty replacement directory as
        # the configured payload store. Status, enqueue, and send all fail
        # without minting the durable folder marker.
        payload_backup = root / "sender-payload-detached"
        payload_root.rename(payload_backup)
        payload_root.mkdir(mode=0o700)
        try:
            run_failure([
                str(replica), "status", "--manifest", str(sender_manifest),
            ], stderr_contains="identity marker is absent and requires explicit bootstrap")
            run_failure([
                str(replica), "enqueue-file", "--manifest", str(sender_manifest),
                "--destination-device", "receiver",
                "--canonical-path", "nested/must-not-exist.bin",
                "--source-file", str(source),
            ], stderr_contains="identity marker is absent and requires explicit bootstrap")
            run_failure([
                str(replica), "send-one", "--manifest", str(sender_manifest),
                "--remote-device", "receiver", "--remote-epoch", "1",
                "--remote-spki", str(receiver_pin),
                "--address", "127.0.0.1", "--port", str(reserve_port()),
                "--certificate", str(certificates / "sender.pem"),
                "--private-key", str(certificates / "sender.key"),
                "--ca-file", str(certificates / "ca.pem"),
            ], stderr_contains="identity marker is absent and requires explicit bootstrap")
            if any(payload_root.iterdir()):
                fail("operational payload open minted identity into an empty replacement")
        finally:
            payload_root.rmdir()
            payload_backup.rename(payload_root)

        # Profile capabilities are selected only by the committed manifest.
        run_failure([
            str(replica), "enqueue-file", "--manifest", str(receiver_manifest),
            "--destination-device", "sender",
            "--canonical-path", "nested/wrong-role.bin",
            "--source-file", str(source),
        ], stderr_contains="requires a payload_root in the deployment manifest")
        run_failure([
            str(replica), "membership-publish", "--manifest", str(sender_manifest),
            "--policy-epoch", "1", "--peer", f"receiver:1:{receiver_pin}",
        ], stderr_contains="requires membership_db and anchor_db")

        # Receiver operation has no bootstrap authority. A missing selected
        # membership DB fails after TLS/listener preflight but before any other
        # database family is opened or created.
        receiver_before_preflight = database_family_snapshot(receiver_database)
        effect_before_preflight = database_family_snapshot(effect_database)
        anchor_before_preflight = database_family_snapshot(
            membership_anchor_database
        )
        detached_membership = detach_database_family(
            membership_database, root / "detached-membership-database"
        )
        try:
            run_failure([
                str(replica), "serve-one", "--manifest", str(receiver_manifest),
                "--bind-address", "127.0.0.1", "--port", str(reserve_port()),
                "--certificate", str(certificates / "receiver.pem"),
                "--private-key", str(certificates / "receiver.key"),
                "--ca-file", str(certificates / "ca.pem"),
            ], stderr_contains="unable to open database file")
            require_database_family_absent(
                membership_database, "existing-only receiver preflight")
            if database_family_snapshot(receiver_database) != receiver_before_preflight:
                fail("membership preflight reached the receiver replica database")
            if database_family_snapshot(effect_database) != effect_before_preflight:
                fail("membership preflight reached the receiver effect database")
            if database_family_snapshot(
                membership_anchor_database
            ) != anchor_before_preflight:
                fail("membership preflight reached the membership anchor")
        finally:
            restore_database_family(detached_membership)

        membership_base = [
            str(replica), "membership-publish", "--manifest", str(receiver_manifest),
            "--peer", f"sender:1:{sender_pin}",
        ]
        genesis_publication = run_json([
            *membership_base, "--policy-epoch", "1",
        ])
        expect_fields(genesis_publication, {
            "command": "membership-publish",
            **receiver_authority,
            "state_generation": 1, "policy_epoch": 1, "entry_count": 1,
            "durable_anchor_generation": 1,
        }, "genesis membership publication")
        second_publication = run_json([
            *membership_base, "--policy-epoch", "2",
        ])
        expect_fields(second_publication, {
            "command": "membership-publish",
            **receiver_authority,
            "state_generation": 2, "policy_epoch": 2, "entry_count": 1,
            "durable_anchor_generation": 2,
        }, "second membership publication")
        if second_publication.get("chain_digest") != second_publication.get(
            "durable_anchor_chain_digest"
        ):
            fail("published membership and independent durable anchor disagree")

        enqueue = run_json([
            str(replica), "enqueue-file", "--manifest", str(sender_manifest),
            "--destination-device", "receiver",
            "--canonical-path", "nested/product-spine.bin",
            "--source-file", str(source),
        ])
        expect_fields(enqueue, {
            "command": "enqueue-file",
            **sender_authority,
            "folder_id": "product-spine",
            "canonical_path": "nested/product-spine.bin",
            "size_bytes": len(payload), "destinations": 1,
            "payload_store_disposition": "inserted",
        }, "durable enqueue")

        sender_queued_status_before = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        sender_queued_status = run_json([
            str(replica), "status", "--manifest", str(sender_manifest),
        ])
        sender_queued_status_after = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        if sender_queued_status_after != sender_queued_status_before:
            fail("successful sender status mutated SQLite or payload authority")
        expect_fields(sender_queued_status, {
            "command": "status", **sender_authority,
            "folder_id": "product-spine", "local_device_id": "sender",
            "local_epoch": 1, "replica_evidence_operations": 1,
            "replica_active_operations": 1, "replica_pending_operations": 0,
            "replica_quarantined_operations": 0, "replica_visible_paths": 1,
            "replica_outbox_intents": 1,
            "replica_outbox_claimable_at_high_water": 0,
            "replica_outbox_time_high_water_epoch": 0,
            "replica_outbox_clock_health": "uninitialized",
            "replica_outbox_clock_anomaly": "none",
            "replica_outbox_clock_observation_generation": 0,
            "replica_outbox_clock_recovery_generation": 0,
            "payload_status_present": True, "payload_entries": 1,
            "payload_indexed_bytes": len(payload),
            "effect_status_present": False,
            "membership_status_present": False,
        }, "queued sender status")

        clock_base = [
            str(replica), "clock-observe", "--manifest", str(sender_manifest),
            "--operator-clock-uncertainty-ns", "1000000",
        ]
        initial_clock = run_json([
            *clock_base, "--operator-clock-authority-id",
            "cloudtainer-process-test-old",
        ])
        expect_fields(initial_clock, {
            "command": "clock-observe",
            **sender_authority,
            "clock_profile": "operator-trusted", "outcome": "accepted",
            "changed": True, "clock_health": "healthy",
            "clock_anomaly": "none", "clock_observation_generation": 1,
            "clock_recovery_generation": 0,
            "clock_accepted_observation_present": True,
            "clock_rejected_observation_present": False,
        }, "initial clock observation")
        if initial_clock.get("clock_high_water_epoch", 0) <= 0:
            fail("initial clock observation did not publish a positive high-water")

        quarantined_clock = run_json([
            *clock_base, "--operator-clock-authority-id",
            "cloudtainer-process-test",
        ])
        expect_fields(quarantined_clock, {
            "command": "clock-observe",
            **sender_authority,
            "clock_profile": "operator-trusted", "outcome": "quarantined",
            "changed": True, "clock_health": "quarantined",
            "clock_anomaly": "source-changed",
            "clock_observation_generation": 2,
            "clock_recovery_generation": 0,
            "clock_accepted_observation_present": True,
            "clock_rejected_observation_present": True,
        }, "source-change quarantine")

        sender_quarantined_status = run_json([
            str(replica), "status", "--manifest", str(sender_manifest),
        ])
        expect_fields(sender_quarantined_status, {
            "command": "status", **sender_authority,
            "replica_outbox_intents": 1,
            "replica_outbox_clock_health": "quarantined",
            "replica_outbox_clock_anomaly": "source-changed",
            "replica_outbox_clock_observation_generation": 2,
            "replica_outbox_clock_recovery_generation": 0,
        }, "quarantined sender status")

        recovery_command = [
            str(replica), "clock-recover", "--manifest", str(sender_manifest),
            "--expected-observation-generation", "2",
            "--operator-clock-authority-id", "cloudtainer-process-test",
            "--operator-clock-uncertainty-ns", "1000000",
        ]
        recovered_clock = run_json(recovery_command)
        expect_fields(recovered_clock, {
            "command": "clock-recover",
            **sender_authority,
            "clock_profile": "operator-trusted",
            "expected_observation_generation": 2,
            "clock_health": "healthy", "clock_anomaly": "none",
            "clock_observation_generation": 3,
            "clock_recovery_generation": 1,
            "clock_accepted_observation_present": True,
            "clock_rejected_observation_present": False,
        }, "generation-fenced clock recovery")
        run_failure(
            recovery_command,
            stderr_contains="clock is not quarantined",
        )

        # A durable sender claim must outlive every receipt and clock-policy
        # allowance that the same invocation still treats as valid. For the
        # selected five-second stage timeout the exact static minimum is 641
        # seconds. One second less fails before manifest/store/payload/TLS/socket
        # authority and leaves the deployment byte-for-byte unchanged.
        short_lease_before = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        run_failure([
            str(replica), "send-one", "--manifest", str(sender_manifest),
            "--remote-device", "receiver", "--remote-epoch", "1",
            "--remote-spki", str(receiver_pin),
            "--address", "127.0.0.1", "--port", str(reserve_port()),
            "--certificate", str(certificates / "sender.pem"),
            "--private-key", str(certificates / "sender.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", "5", "--lease-seconds", "640",
            "--operator-clock-authority-id", "cloudtainer-process-test",
            "--operator-clock-uncertainty-ns", "1000000",
        ], stderr_contains=(
            "--lease-seconds must be at least 641 seconds"
        ))
        short_lease_after = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        if short_lease_after != short_lease_before:
            fail("short sender lease reached durable or payload authority")

        port = reserve_port()
        server_command = [
            str(replica), "serve-one", "--manifest", str(receiver_manifest),
            "--bind-address", "127.0.0.1", "--port", str(port),
            "--certificate", str(certificates / "receiver.pem"),
            "--private-key", str(certificates / "receiver.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", "5",
        ]
        server = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        server_stdout = ""
        server_stderr = ""
        try:
            wait_until_listening(server, port)
            client = run_json([
                str(replica), "send-one", "--manifest", str(sender_manifest),
                "--remote-device", "receiver", "--remote-epoch", "1",
                "--remote-spki", str(receiver_pin),
                "--address", "127.0.0.1", "--port", str(port),
                "--certificate", str(certificates / "sender.pem"),
                "--private-key", str(certificates / "sender.key"),
                "--ca-file", str(certificates / "ca.pem"),
                "--timeout-seconds", "5",
                "--operator-clock-authority-id", "cloudtainer-process-test",
                "--operator-clock-uncertainty-ns", "1000000",
            ])
            server_stdout, server_stderr = server.communicate(timeout=20.0)
        finally:
            if server.poll() is None:
                server.send_signal(signal.SIGTERM)
                try:
                    server.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.communicate(timeout=2.0)

        if server.returncode != 0:
            fail(
                f"serve-one failed with status {server.returncode}\n"
                f"stdout:\n{server_stdout}\nstderr:\n{server_stderr}"
            )
        if server_stderr:
            fail(f"serve-one wrote diagnostics on success: {server_stderr}")
        try:
            server_result = json.loads(server_stdout)
        except json.JSONDecodeError as error:
            fail(f"serve-one did not return JSON: {error}: {server_stdout}")
        if not isinstance(server_result, dict):
            fail("serve-one JSON is not an object")

        expect_fields(client, {
            "command": "send-one", **sender_authority,
            "clock_profile": "operator-trusted",
            "session_timeout_seconds": 5,
            "claim_lease_seconds": 641,
            "minimum_claim_lease_seconds": 641,
            "stop_reason": "max_sessions_reached",
            "disposition": "receipt_applied", "peer_authenticated": True,
            "receipt_apply_result": "effect_settled",
            "operation_id": enqueue["operation_id"],
            "peer_spki_sha256": receiver_pin,
        }, "sender process")
        expect_fields(server_result, {
            "command": "serve-one",
            **receiver_authority,
            "session_timeout_seconds": 5,
            "stop_reason": "max_sessions_reached",
            "disposition": "receipt_sent", "handshake_complete": True,
            "membership_state_generation": 2,
            "membership_policy_epoch": 2, "peer_device_id": "sender",
            "peer_epoch": 1, "peer_spki_sha256": sender_pin,
            "receive_disposition": "receipt_sent",
            "receipt_disposition": "published",
            "operation_id": enqueue["operation_id"],
        }, "receiver process")
        if client.get("request_frame_bytes") != server_result.get(
            "request_frame_bytes"
        ):
            fail("sender and receiver disagree on exact request frame length")
        if client.get("receipt_frame_bytes") != server_result.get(
            "receipt_frame_bytes"
        ):
            fail("sender and receiver disagree on exact receipt frame length")
        published = destination_parent / "product-spine.bin"
        if published.read_bytes() != payload:
            fail("receiver filesystem publication differs from source payload")

        # Batch supervisors require both a conversation-count budget and one
        # absolute command-runtime budget. Invalid or omitted bounds fail before
        # manifest, store, socket, or TLS authority can be opened.
        for invalid_bound in ("0", "257"):
            run_failure([
                str(replica), "send-batch", "--max-sessions", invalid_bound,
            ], stderr_contains="--max-sessions must be in [1, 256]")
            run_failure([
                str(replica), "serve-batch", "--max-sessions", invalid_bound,
            ], stderr_contains="--max-sessions must be in [1, 256]")
        for command in ("send-batch", "serve-batch"):
            run_failure([
                str(replica), command, "--max-sessions", "1",
            ], stderr_contains="required option --max-runtime-seconds is missing")
            for invalid_runtime in ("0", "86401"):
                run_failure([
                    str(replica), command, "--max-sessions", "1",
                    "--max-runtime-seconds", invalid_runtime,
                ], stderr_contains=(
                    "--max-runtime-seconds must be in [1, 86400]"
                ))

        # The whole-command cutpoint begins before receiver preflight and clamps
        # the first accept deadline. No peer arrives; the invocation exits at the
        # command cutpoint without durable delivery or filesystem mutation.
        runtime_before = {
            "replica": database_family_snapshot(receiver_database),
            "effect": database_family_snapshot(effect_database),
            "membership": database_family_snapshot(membership_database),
            "anchor": database_family_snapshot(membership_anchor_database),
            "files": directory_snapshot(files_root),
        }
        runtime_port = reserve_port()
        runtime_result = run_json([
            str(replica), "serve-batch", "--manifest", str(receiver_manifest),
            "--max-sessions", "5", "--max-runtime-seconds", "3",
            "--bind-address", "127.0.0.1", "--port", str(runtime_port),
            "--certificate", str(certificates / "receiver.pem"),
            "--private-key", str(certificates / "receiver.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", "5",
        ], timeout=8.0)
        expect_fields(runtime_result, {
            "command": "serve-batch", **receiver_authority,
            "max_sessions": 5, "max_runtime_seconds": 3,
            "session_timeout_seconds": 5,
            "sessions_attempted": 1, "receipts_sent": 0,
            "stop_reason": "command_deadline_reached",
        }, "whole-command receiver runtime budget")
        runtime_sessions = runtime_result.get("sessions")
        if not isinstance(runtime_sessions, list) or len(runtime_sessions) != 1:
            fail("runtime-bounded receiver omitted its one accept session")
        expect_fields(runtime_sessions[0], {
            "session_index": 1,
            "disposition": "accept_deadline_expired",
            "accepted": False,
            "handshake_complete": False,
        }, "whole-command receiver deadline session")
        runtime_after = {
            "replica": database_family_snapshot(receiver_database),
            "effect": database_family_snapshot(effect_database),
            "membership": database_family_snapshot(membership_database),
            "anchor": database_family_snapshot(membership_anchor_database),
            "files": directory_snapshot(files_root),
        }
        if runtime_after != runtime_before:
            fail("runtime-only receiver session mutated durable authority")

        # One bounded invocation can settle multiple exact deliveries while
        # reusing only the manifest/store/TLS-context cutpoint. A deliberately
        # larger session bound proves compositional termination: after two exact
        # receipts, the sender authenticates once more, discovers no ready work,
        # emits no application bytes, and closes. The receiver recognizes only
        # that exact zero-application-byte authenticated close as nonfatal idle;
        # it does not claim evidence that the sender had no work.
        batch_enqueues: list[dict[str, Any]] = []
        batch_names = ("batch-alpha.bin", "batch-beta.bin")
        for batch_source, batch_payload, batch_name in zip(
            batch_sources, batch_payloads, batch_names
        ):
            enqueued = run_json([
                str(replica), "enqueue-file", "--manifest", str(sender_manifest),
                "--destination-device", "receiver",
                "--canonical-path", f"nested/{batch_name}",
                "--source-file", str(batch_source),
            ])
            expect_fields(enqueued, {
                "command": "enqueue-file", **sender_authority,
                "folder_id": "product-spine",
                "canonical_path": f"nested/{batch_name}",
                "size_bytes": len(batch_payload), "destinations": 1,
                "payload_store_disposition": "inserted",
            }, f"bounded batch enqueue {batch_name}")
            batch_enqueues.append(enqueued)

        batch_port = reserve_port()
        batch_server_command = [
            str(replica), "serve-batch", "--manifest", str(receiver_manifest),
            "--max-sessions", "3", "--max-runtime-seconds", "30",
            "--bind-address", "127.0.0.1", "--port", str(batch_port),
            "--certificate", str(certificates / "receiver.pem"),
            "--private-key", str(certificates / "receiver.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", "5",
        ]
        batch_server = subprocess.Popen(
            batch_server_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        batch_server_stdout = ""
        batch_server_stderr = ""
        try:
            wait_until_listening(batch_server, batch_port)
            batch_client = run_json([
                str(replica), "send-batch", "--manifest", str(sender_manifest),
                "--max-sessions", "3", "--max-runtime-seconds", "30",
                "--remote-device", "receiver", "--remote-epoch", "1",
                "--remote-spki", str(receiver_pin),
                "--address", "127.0.0.1", "--port", str(batch_port),
                "--certificate", str(certificates / "sender.pem"),
                "--private-key", str(certificates / "sender.key"),
                "--ca-file", str(certificates / "ca.pem"),
                "--timeout-seconds", "5",
                "--operator-clock-authority-id", "cloudtainer-process-test",
                "--operator-clock-uncertainty-ns", "1000000",
            ])
            batch_server_stdout, batch_server_stderr = (
                batch_server.communicate(timeout=20.0)
            )
        finally:
            if batch_server.poll() is None:
                batch_server.send_signal(signal.SIGTERM)
                try:
                    batch_server.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    batch_server.kill()
                    batch_server.communicate(timeout=2.0)

        if batch_server.returncode != 0:
            fail(
                f"serve-batch failed with status {batch_server.returncode}\n"
                f"stdout:\n{batch_server_stdout}stderr:\n{batch_server_stderr}"
            )
        if batch_server_stderr:
            fail(
                "serve-batch wrote diagnostics on success: "
                f"{batch_server_stderr}"
            )
        try:
            batch_server_result = json.loads(batch_server_stdout)
        except json.JSONDecodeError as error:
            fail(
                f"serve-batch did not return JSON: {error}: "
                f"{batch_server_stdout}"
            )
        if not isinstance(batch_server_result, dict):
            fail("serve-batch JSON is not an object")

        expect_fields(batch_client, {
            "command": "send-batch", **sender_authority,
            "clock_profile": "operator-trusted",
            "max_sessions": 3, "max_runtime_seconds": 30,
            "session_timeout_seconds": 5,
            "claim_lease_seconds": 641,
            "minimum_claim_lease_seconds": 641,
            "sessions_attempted": 3,
            "receipts_applied": 2, "deliveries_settled": 2,
            "deliveries_deferred": 0,
            "stop_reason": "no_ready_delivery",
        }, "bounded sender supervisor")
        expect_fields(batch_server_result, {
            "command": "serve-batch", **receiver_authority,
            "max_sessions": 3, "max_runtime_seconds": 30,
            "session_timeout_seconds": 5,
            "sessions_attempted": 3, "receipts_sent": 2,
            "stop_reason": "authenticated_peer_closed_idle",
        }, "bounded receiver supervisor")

        client_sessions = batch_client.get("sessions")
        server_sessions = batch_server_result.get("sessions")
        if (
            not isinstance(client_sessions, list)
            or not isinstance(server_sessions, list)
            or len(client_sessions) != 3
            or len(server_sessions) != 3
        ):
            fail("bounded supervisors did not return exactly three session records")
        operation_client_sessions = client_sessions[:2]
        operation_server_sessions = server_sessions[:2]
        idle_client_session = client_sessions[2]
        idle_server_session = server_sessions[2]

        expected_operation_ids = {
            enqueued["operation_id"] for enqueued in batch_enqueues
        }
        client_by_operation: dict[str, dict[str, Any]] = {}
        server_by_operation: dict[str, dict[str, Any]] = {}
        for index, session in enumerate(operation_client_sessions, start=1):
            if not isinstance(session, dict):
                fail("bounded sender session is not a JSON object")
            expect_fields(session, {
                "session_index": index,
                "disposition": "receipt_applied",
                "peer_authenticated": True,
                "receipt_apply_result": "effect_settled",
                "peer_spki_sha256": receiver_pin,
            }, f"bounded sender session {index}")
            operation_id = session.get("operation_id")
            if not isinstance(operation_id, str):
                fail("bounded sender session omitted operation_id")
            client_by_operation[operation_id] = session
        for index, session in enumerate(operation_server_sessions, start=1):
            if not isinstance(session, dict):
                fail("bounded receiver session is not a JSON object")
            expect_fields(session, {
                "session_index": index,
                "disposition": "receipt_sent",
                "handshake_complete": True,
                "membership_state_generation": 2,
                "membership_policy_epoch": 2,
                "peer_device_id": "sender", "peer_epoch": 1,
                "peer_spki_sha256": sender_pin,
                "receive_disposition": "receipt_sent",
                "receipt_disposition": "published",
            }, f"bounded receiver session {index}")
            operation_id = session.get("operation_id")
            if not isinstance(operation_id, str):
                fail("bounded receiver session omitted operation_id")
            server_by_operation[operation_id] = session
        if not isinstance(idle_client_session, dict):
            fail("bounded sender idle session is not a JSON object")
        expect_fields(idle_client_session, {
            "session_index": 3,
            "disposition": "no_ready_delivery",
            "shutdown_disposition": "close_notify_sent",
            "connected": True,
            "handshake_complete": True,
            "peer_authenticated": True,
            "request_frame_bytes": 0,
            "request_body_bytes_written": 0,
            "receipt_frame_bytes": 0,
            "peer_spki_sha256": receiver_pin,
        }, "bounded sender authenticated no-ready session")
        if "operation_id" in idle_client_session or "claim_id" in idle_client_session:
            fail("sender no-ready session invented durable claim identity")
        if not isinstance(idle_server_session, dict):
            fail("bounded receiver idle session is not a JSON object")
        expect_fields(idle_server_session, {
            "session_index": 3,
            "disposition": "peer_closed",
            "shutdown_disposition": "not_attempted",
            "accepted": True,
            "handshake_complete": True,
            "membership_state_generation": 2,
            "membership_policy_epoch": 2,
            "peer_device_id": "sender", "peer_epoch": 1,
            "peer_spki_sha256": sender_pin,
            "receive_disposition": "peer_closed",
            "request_frame_bytes": 0,
            "receipt_frame_bytes": 0,
        }, "bounded receiver authenticated idle close")
        if "operation_id" in idle_server_session or "receipt_disposition" in idle_server_session:
            fail("receiver idle session invented delivery evidence")

        if set(client_by_operation) != expected_operation_ids:
            fail("bounded sender settled a different operation set")
        if set(server_by_operation) != expected_operation_ids:
            fail("bounded receiver published a different operation set")
        enqueue_order = [item["operation_id"] for item in batch_enqueues]
        if [
            session.get("operation_id") for session in operation_client_sessions
        ] != enqueue_order:
            fail("bounded sender did not preserve durable enqueue chronology")
        if [
            session.get("operation_id") for session in operation_server_sessions
        ] != enqueue_order:
            fail("bounded receiver observed a different causal session order")
        for operation_id in expected_operation_ids:
            if client_by_operation[operation_id].get(
                "request_frame_bytes"
            ) != server_by_operation[operation_id].get("request_frame_bytes"):
                fail("bounded peers disagree on an exact request frame length")
            if client_by_operation[operation_id].get(
                "receipt_frame_bytes"
            ) != server_by_operation[operation_id].get("receipt_frame_bytes"):
                fail("bounded peers disagree on an exact receipt frame length")
        for batch_name, batch_payload in zip(batch_names, batch_payloads):
            if (destination_parent / batch_name).read_bytes() != batch_payload:
                fail(f"bounded receiver publication differs for {batch_name}")

        total_payload_bytes = len(payload) + sum(map(len, batch_payloads))

        sender_final_status_before = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        sender_final_status = run_json([
            str(replica), "status", "--manifest", str(sender_manifest),
        ])
        sender_final_status_after = {
            "replica": database_family_snapshot(sender_database),
            "payload": directory_snapshot(payload_root),
        }
        if sender_final_status_after != sender_final_status_before:
            fail("settled sender status mutated SQLite or payload authority")
        expect_fields(sender_final_status, {
            "command": "status", **sender_authority,
            "replica_evidence_operations": 3,
            "replica_active_operations": 3,
            "replica_outbox_intents": 0,
            "replica_outbox_dispatch_attempts": 0,
            "replica_outbox_clock_health": "healthy",
            "payload_entries": 3,
            "payload_indexed_bytes": total_payload_bytes,
        }, "settled sender status")

        receiver_status_before = {
            "replica": database_family_snapshot(receiver_database),
            "effect": database_family_snapshot(effect_database),
            "membership": database_family_snapshot(membership_database),
            "anchor": database_family_snapshot(membership_anchor_database),
            "files": directory_snapshot(files_root),
        }
        receiver_status = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ])
        receiver_status_after = {
            "replica": database_family_snapshot(receiver_database),
            "effect": database_family_snapshot(effect_database),
            "membership": database_family_snapshot(membership_database),
            "anchor": database_family_snapshot(membership_anchor_database),
            "files": directory_snapshot(files_root),
        }
        if receiver_status_after != receiver_status_before:
            fail("successful receiver status mutated database or file authority")
        expect_fields(receiver_status, {
            "command": "status", **receiver_authority,
            "replica_evidence_operations": 3,
            "replica_active_operations": 3,
            "replica_visible_paths": 3,
            "replica_outbox_intents": 0,
            "effect_status_present": True,
            "effect_total": 3, "effect_staged": 0,
            "effect_published": 3,
            "effect_retained_payload_bytes": total_payload_bytes,
            "membership_status_present": True,
            "membership_state_generation": 2,
            "membership_policy_epoch": 2,
            "membership_entry_count": 1,
            "membership_anchor_generation": 2,
            "membership_anchor_transition_sequence": 2,
            "membership_anchor_matches_current": True,
        }, "receiver status")

    print("anonsync_replica process spine checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - one diagnostic boundary.
        print(f"anonsync_replica process spine checks failed: {error}", file=sys.stderr)
        raise SystemExit(1)
