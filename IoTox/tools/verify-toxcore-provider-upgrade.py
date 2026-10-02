#!/usr/bin/env python3
"""Qualify the exact c-toxcore 0.2.22 -> 0.2.23 savedata boundary."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


EXPECTED_OLD = "0.2.22"
EXPECTED_CURRENT = "0.2.23"
OLD_SOURCE_SHA256 = "276d447eb94e9d76e802cecc5ca7660c6c15128a83dfbe4353b678972aeb950a"
CURRENT_SOURCE_SHA256 = "b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe"
CMP_SOURCE_SHA256 = "4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0"
SNAPSHOT_FIELDS = (
    "address",
    "public-key",
    "name-hex",
    "status-message-hex",
    "status",
    "friend-count",
    "friend-0",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(*arguments: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        check=True,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def inspect(binary: Path, savedata: Path) -> dict[str, str]:
    result = run(str(binary), "inspect", str(savedata))
    fields: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        require(separator == "=" and key not in fields, "fixture emitted ambiguous inspection")
        fields[key] = value
    require(fields.get("provider-version") in {EXPECTED_OLD, EXPECTED_CURRENT}, "unexpected provider version")
    require(len(fields.get("address", "")) == 76, "invalid savedata address")
    require(len(fields.get("public-key", "")) == 64, "invalid savedata public key")
    require(fields["address"].startswith(fields["public-key"]), "address/public key mismatch")
    require(fields.get("friend-count") in {"0", "1"}, "invalid fixture friend count")
    expected_keys = {
        "provider-version",
        "address",
        "public-key",
        "name-hex",
        "status-message-hex",
        "status",
        "friend-count",
    }
    if fields["friend-count"] == "1":
        expected_keys.add("friend-0")
    require(set(fields) == expected_keys, "fixture inspection field set changed")
    return fields


def same_snapshot(left: dict[str, str], right: dict[str, str]) -> bool:
    return all(left.get(field) == right.get(field) for field in SNAPSHOT_FIELDS)


def wait_for_socket(process: subprocess.Popen[str], socket_path: Path) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if socket_path.is_socket():
            return
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise RuntimeError(
                f"IoTox exited before publishing control: {stdout}{stderr}"
            )
        time.sleep(0.025)
    raise RuntimeError("IoTox did not publish its control socket")


def start_iotox(binary: Path, root: Path) -> tuple[subprocess.Popen[str], Path]:
    runtime = root / "runtime"
    process = subprocess.Popen(
        [
            str(binary),
            "run",
            "--runtime",
            str(runtime),
            "--state",
            str(root / "device.toxsave"),
            "--identity",
            str(root / "device.identity"),
            "--authority-ledger",
            str(root / "authority.ledger"),
            "--command-store",
            str(root / "commands.store"),
            "--no-default-bootstrap",
            "--run-ms",
            "30000",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    wait_for_socket(process, runtime / "control.sock")
    return process, runtime


def stop_iotox(binary: Path, process: subprocess.Popen[str], runtime: Path) -> None:
    run(str(binary), "--runtime", str(runtime), "stop")
    stdout, stderr = process.communicate(timeout=15)
    require(process.returncode == 0, f"IoTox stop failed: {stdout}{stderr}")


def qualify_product_load(
    binary: Path,
    old_savedata: Path,
    expected: dict[str, str],
    expected_friend: str,
    root: Path,
) -> Path:
    root.mkdir(mode=0o700)
    process, runtime = start_iotox(binary, root)
    stop_iotox(binary, process, runtime)
    identity = root / "device.identity"
    require(identity.is_file() and identity.stat().st_mode & 0o777 == 0o600, "IoTox identity provisioning failed")
    shutil.rmtree(runtime)
    for path in (root / "authority.ledger", root / "commands.store"):
        if path.exists():
            path.unlink()
    shutil.copyfile(old_savedata, root / "device.toxsave")
    os.chmod(root / "device.toxsave", 0o600)

    process, runtime = start_iotox(binary, root)
    address = run(str(binary), "--runtime", str(runtime), "address").stdout.strip()
    profile = run(str(binary), "--runtime", str(runtime), "profile").stdout
    peers = run(str(binary), "--runtime", str(runtime), "peers").stdout
    require(address == expected["address"], "IoTox changed the prior-provider Tox identity")
    require("name=alpha" in profile or "name=bravo" in profile, "IoTox lost the prior-provider profile name")
    require("status-message=provider-022" in profile, "IoTox lost the prior-provider status message")
    require(expected_friend in peers and "connection=offline" in peers, "IoTox lost the prior-provider friend")
    stop_iotox(binary, process, runtime)
    return root / "device.toxsave"


def qualify(old: Path, current: Path, iotox: Path, output: Path) -> dict:
    for binary in (old, current, iotox):
        require(binary.is_file() and os.access(binary, os.X_OK), f"fixture is not executable: {binary}")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="iotox-provider-upgrade-") as directory:
        root = Path(directory)
        malformed = root / "malformed.toxsave"
        malformed.write_bytes(b"IoTox deliberately malformed provider savedata\n")
        os.chmod(malformed, 0o600)
        for fixture in (old, current):
            refused = subprocess.run(
                [str(fixture), "inspect", str(malformed)],
                text=True,
                capture_output=True,
                timeout=10,
            )
            require(refused.returncode != 0, "provider accepted malformed savedata")
        initial = {role: root / f"{role}.initial.toxsave" for role in ("a", "b")}
        for role, name in (("a", "alpha"), ("b", "bravo")):
            run(str(old), "create", str(initial[role]), name, "provider-022")
        bare = {role: inspect(old, path) for role, path in initial.items()}
        require(bare["a"]["public-key"] != bare["b"]["public-key"], "fixture peers share an identity")

        old_savedata = {role: root / f"{role}.old.toxsave" for role in ("a", "b")}
        run(str(old), "friend", str(initial["a"]), bare["b"]["public-key"], str(old_savedata["a"]))
        run(str(old), "friend", str(initial["b"]), bare["a"]["public-key"], str(old_savedata["b"]))
        old_snapshot = {role: inspect(old, path) for role, path in old_savedata.items()}
        require(old_snapshot["a"]["friend-0"] == bare["b"]["public-key"], "old provider lost peer B")
        require(old_snapshot["b"]["friend-0"] == bare["a"]["public-key"], "old provider lost peer A")

        current_from_old = {role: inspect(current, path) for role, path in old_savedata.items()}
        require(all(same_snapshot(old_snapshot[role], current_from_old[role]) for role in ("a", "b")), "current provider changed old savedata semantics")

        current_savedata = {role: root / f"{role}.current.toxsave" for role in ("a", "b")}
        for role in ("a", "b"):
            run(str(current), "rewrite", str(old_savedata[role]), str(current_savedata[role]))
        current_snapshot = {role: inspect(current, path) for role, path in current_savedata.items()}
        old_from_current = {role: inspect(old, path) for role, path in current_savedata.items()}
        require(all(same_snapshot(old_snapshot[role], current_snapshot[role]) for role in ("a", "b")), "current provider rewrite changed savedata semantics")
        require(all(same_snapshot(old_snapshot[role], old_from_current[role]) for role in ("a", "b")), "old provider cannot read current rewritten savedata")

        product_savedata = {}
        for role in ("a", "b"):
            friend = bare["b" if role == "a" else "a"]["public-key"]
            product_path = qualify_product_load(
                iotox,
                old_savedata[role],
                old_snapshot[role],
                friend,
                root / f"iotox-{role}",
            )
            product_snapshot = inspect(current, product_path)
            rollback_snapshot = inspect(old, product_path)
            require(same_snapshot(old_snapshot[role], product_snapshot), "IoTox rewrite changed provider state")
            require(same_snapshot(old_snapshot[role], rollback_snapshot), "old provider cannot read IoTox-written state")
            product_savedata[role] = {
                "bytes": product_path.stat().st_size,
            }

        receipt = {
            "schema": "iotox.toxcore-provider-upgrade.v0",
            "status": "passed",
            "old_provider": EXPECTED_OLD,
            "current_provider": EXPECTED_CURRENT,
            "old_source_sha256": OLD_SOURCE_SHA256,
            "current_source_sha256": CURRENT_SOURCE_SHA256,
            "cmp_source_sha256": CMP_SOURCE_SHA256,
            "peer_count": 2,
            "malformed_savedata_refused_by_both": True,
            "old_savedata_loaded_by_current": True,
            "identity_preserved": True,
            "profile_preserved": True,
            "friendship_preserved": True,
            "current_rewrite_loaded_by_old": True,
            "iotox_product_load_count": 2,
            "iotox_product_rewrite_loaded_by_old": True,
            "product_savedata": product_savedata,
        }
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, type=Path)
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--iotox", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(qualify(args.old, args.current, args.iotox, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"provider upgrade qualification failed: {error}", file=os.sys.stderr)
        raise SystemExit(1)
