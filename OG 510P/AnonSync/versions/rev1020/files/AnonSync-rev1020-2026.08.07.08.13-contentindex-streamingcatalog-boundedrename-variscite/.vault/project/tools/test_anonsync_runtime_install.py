#!/usr/bin/env python3
"""Prove the deliberately narrow AnonSync runtime install component.

The test stages only the runtime component under DESTDIR, verifies its exact
four-file inventory and the semantics of the native Type=notify user unit,
executes all three staged binaries, proves replacement of a stale binary, and
removes the manifest inventory without leaving an untracked product file.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from typing import NoReturn


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def logical_install_path(prefix: Path, destination: Path, name: str) -> Path:
    base = destination if destination.is_absolute() else prefix / destination
    return base / name


def staged_path(destdir: Path, logical: Path) -> Path:
    if not logical.is_absolute():
        fail(f"logical install path is not absolute: {logical}")
    return destdir / str(logical).lstrip("/")


def run_install(cmake: Path, build_dir: Path, destdir: Path) -> None:
    environment = os.environ.copy()
    environment["DESTDIR"] = str(destdir)
    completed = subprocess.run(
        [str(cmake), "--install", str(build_dir), "--component", "anonsync_runtime"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        timeout=20.0,
        check=False,
    )
    if completed.returncode != 0:
        fail(
            "runtime component install failed\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def assert_unit(
    path: Path,
    *,
    configured_bindir: Path,
    stop_timeout_seconds: int,
) -> None:
    text = path.read_text(encoding="utf-8")
    expected_exec = (
        f"ExecStart={configured_bindir}/anonsync_sync run --config "
        "%h/.config/anonsync/linked-peers/%i.json"
    )
    required_once = [
        "[Unit]",
        "Description=AnonSync linked peer %i",
        "[Service]",
        "Type=notify",
        "NotifyAccess=main",
        expected_exec,
        "RuntimeDirectory=anonsync-%i",
        "RuntimeDirectoryMode=0700",
        "KillSignal=SIGTERM",
        "TimeoutStartSec=infinity",
        f"TimeoutStopSec={stop_timeout_seconds}s",
        "Restart=on-failure",
        "RestartSec=5s",
        "[Install]",
        "WantedBy=default.target",
    ]
    for line in required_once:
        if text.count(line) != 1:
            fail(f"installed unit did not contain exactly one {line!r}")
    forbidden = [
        "ExecStop=",
        "/bin/sh",
        " daemon",
        "--daemon",
        "network-online.target",
        "UMask=",
        "PrivateTmp=",
        "ProtectSystem=",
        "ProtectHome=",
        "ReadWritePaths=",
        "BindPaths=",
        "BindReadOnlyPaths=",
        "--transport direct",
        "--transport tor",
        "--transport i2p",
    ]
    for fragment in forbidden:
        if fragment in text:
            fail(f"installed unit contains forbidden policy {fragment!r}")
    if "@" in text:
        fail("installed unit retained an unsubstituted CMake token")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmake", required=True, type=Path)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    parser.add_argument("--install-prefix", required=True, type=Path)
    parser.add_argument("--bindir", required=True, type=Path)
    parser.add_argument("--unit-install-dir", required=True, type=Path)
    parser.add_argument("--configured-bindir", required=True, type=Path)
    parser.add_argument("--stop-timeout-seconds", required=True, type=int)
    args = parser.parse_args()

    cmake = args.cmake.resolve(strict=True)
    build_dir = args.build_dir.resolve(strict=True)
    source_binaries = {
        "anonsync_replica": args.replica.resolve(strict=True),
        "anonsync_folder": args.folder.resolve(strict=True),
        "anonsync_sync": args.sync.resolve(strict=True),
    }
    prefix = args.install_prefix
    if not prefix.is_absolute():
        fail("configured install prefix must be absolute")
    if args.stop_timeout_seconds <= 0:
        fail("stop timeout must be positive")

    logical = {
        name: logical_install_path(prefix, args.bindir, name)
        for name in source_binaries
    }
    logical["anonsync-linked-peer@.service"] = logical_install_path(
        prefix, args.unit_install_dir, "anonsync-linked-peer@.service"
    )

    with tempfile.TemporaryDirectory(prefix="anonsync-runtime-install-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        destdir = root / "destdir"
        destdir.mkdir(mode=0o700)
        run_install(cmake, build_dir, destdir)

        expected = {staged_path(destdir, path) for path in logical.values()}
        observed = {
            path
            for path in destdir.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        if observed != expected:
            fail(
                "runtime install inventory was not exact: "
                f"expected={sorted(map(str, expected))}, "
                f"observed={sorted(map(str, observed))}"
            )
        for path in expected:
            if path.is_symlink() or not path.is_file():
                fail(f"runtime install member is not a regular file: {path}")

        for name, source in source_binaries.items():
            installed = staged_path(destdir, logical[name])
            mode = stat.S_IMODE(installed.stat().st_mode)
            if mode & 0o111 == 0:
                fail(f"installed binary is not executable: {installed}")
            if sha256(installed) != sha256(source):
                fail(f"installed binary differs from built target: {name}")
            completed = subprocess.run(
                [str(installed), "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5.0,
                check=False,
            )
            if completed.returncode != 0 or "AnonSync" not in completed.stdout:
                fail(
                    f"staged {name} help failed with {completed.returncode}\n"
                    f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
                )

        unit = staged_path(destdir, logical["anonsync-linked-peer@.service"])
        if stat.S_IMODE(unit.stat().st_mode) != 0o644:
            fail("installed systemd unit mode is not exactly 0644")
        assert_unit(
            unit,
            configured_bindir=args.configured_bindir,
            stop_timeout_seconds=args.stop_timeout_seconds,
        )

        # A package upgrade must replace stale bytes, not leave an executable
        # merely because its pathname and mode already exist.
        installed_sync = staged_path(destdir, logical["anonsync_sync"])
        installed_sync.write_bytes(b"stale-anonsync-sync\n")
        os.chmod(installed_sync, 0o755)
        os.utime(installed_sync, (1, 1))
        run_install(cmake, build_dir, destdir)
        if sha256(installed_sync) != sha256(source_binaries["anonsync_sync"]):
            fail("runtime reinstall did not replace a stale anonsync_sync binary")

        manifests = sorted(build_dir.glob("install_manifest*.txt"))
        expected_logical = {str(path) for path in logical.values()}
        if not any(
            {line for line in manifest.read_text(encoding="utf-8").splitlines() if line}
            == expected_logical
            for manifest in manifests
        ):
            fail("no CMake install manifest described the exact runtime component")

        # Simulate package-manager removal from the exact manifest and prove no
        # untracked product file was introduced by the component.
        for path in expected:
            path.unlink()
        for directory in sorted(
            (path for path in destdir.rglob("*") if path.is_dir()),
            key=lambda value: len(value.parts),
            reverse=True,
        ):
            directory.rmdir()
        if any(destdir.iterdir()):
            fail("runtime component removal left untracked staged content")

    print("anonsync runtime install process test passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - test frontier reports all failures
        print(f"anonsync runtime install process test failure: {error}")
        raise SystemExit(1)
