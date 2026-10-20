#!/usr/bin/env python3
"""Run live-Agent sync production transaction replay through dm-log-writes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_ROOT = ROOT / ".sandwurm/lab/sync-production-prefix"
DEFAULT_EXPORT_ROOT = ROOT / ".sandwurm/exports/sync-production-prefix"
SCHEMA = "iotox.sync-production-prefix-replay.v1"
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
FILESYSTEMS = ("ext4", "btrfs")
NAMESPACE = "prodprefix"
PHRASE = "abacus abdomen abdominal abide abiding ability ablaze able\n"
BOOTSTRAP_KEY = "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F"
MARKS = {
    "sync-create-generation-1": "valid-old-production-namespace",
    "sync-publish-generation-2": "accepted-current-production-namespace",
}
FAMILY_PATTERNS = {
    "namespace": re.compile(r"^namespaces/[^/]+\.namespace$"),
    "automation": re.compile(r"^automation/[^/]+\.automation$"),
    "branch-pointer": re.compile(r"^data/[^/]+/tree-v2/branches/[^/]+\.branch$"),
    "immutable-branch-record": re.compile(r"^data/[^/]+/tree-v2/records/[^/]+\.branch$"),
    "manifest": re.compile(r"^data/[^/]+/tree-v2/manifests/[^/]+\.manifest$"),
    "object": re.compile(r"^data/[^/]+/tree-v2/objects/[0-9a-f][0-9a-f]/[0-9a-f]+$"),
    "workspace": re.compile(r"^data/[^/]+/tree-v2/workspace\.state$"),
    "maintenance": re.compile(r"^data/[^/]+/tree-v2/maintenance/.*$"),
    "transaction-lock": re.compile(r"^data/[^/]+/transactions/[^/]+\.transaction\.lock$"),
}


class ProductionPrefixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionPrefixError(message)


def load_log_writes_helpers():
    path = ROOT / "tools/run-sync-log-writes-prefix-replay.py"
    spec = importlib.util.spec_from_file_location("iotox_log_writes_helpers", path)
    require(spec is not None and spec.loader is not None, "unable to load log-writes helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lw = load_log_writes_helpers()


def run(argv: list[str], *, capture_output: bool = False, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=True, text=True, capture_output=capture_output, input=input_text)


def run_checked_output(argv: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        argv,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input_text,
    )
    return result.stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def random_run_id() -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    return "run." + "".join(secrets.choice(alphabet) for _ in range(8))


def validate_under(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve()
    allowed = parent.resolve()
    require(resolved == allowed or resolved.is_relative_to(allowed), f"{label} must be under {parent}")
    require(not resolved.is_symlink(), f"{label} may not be a symlink")
    return resolved


def dm_name(run_id: str, index: int, kind: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "_" for character in run_id.removeprefix("run."))
    return f"iotox_prod_lw_{safe}_{index}_{kind}"


def mark_log_writes(name: str, mark: str) -> None:
    require(mark in MARKS or mark == "mkfs", f"unsupported mark: {mark}")
    run(["sudo", "dmsetup", "message", name, "0", "mark", mark])


def fsync_file(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def chmod_private(path: Path) -> None:
    os.chmod(path, 0o700)


def write_fixture_source(source_root: Path, content: str) -> None:
    source_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    chmod_private(source_root)
    file_path = source_root / "note.txt"
    with file_path.open("w", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    fsync_directory(source_root)


def parse_key_values(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for token in output.replace("\n", " ").split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        parsed[key] = value
    return parsed


def repair_summary(output: str, exit_code: int = 0) -> dict[str, Any]:
    fields = parse_key_values(output)

    def integer(name: str) -> int:
        value = fields.get(name)
        if value is None:
            return 0
        try:
            return int(value)
        except ValueError:
            return 0

    return {
        "exit_code": exit_code,
        "metadata": fields.get("metadata", "unknown"),
        "branches": integer("branches"),
        "rollback_witness": integer("rollback-witness"),
        "workspace": fields.get("workspace", "unknown"),
        "maintenance": fields.get("maintenance", "unknown"),
        "custody": fields.get("custody", "unknown"),
        "manifest_file_objects": integer("manifest-file-objects"),
        "selected_objects": integer("selected-objects"),
        "skipped_objects": integer("skipped-objects"),
        "selected_bytes": integer("selected-bytes"),
        "verified": integer("verified"),
        "stdout_sha256": sha256_text(output),
    }


def classify_policy_path(relative_path: str) -> str:
    for family, pattern in FAMILY_PATTERNS.items():
        if pattern.fullmatch(relative_path):
            return family
    return "other"


def walk_regular_files(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        files.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def observe_state(mount_root: Path) -> dict[str, Any]:
    policy_root = mount_root / "sync-policy"
    source_root = mount_root / "source"
    policy_files = walk_regular_files(policy_root)
    source_files = walk_regular_files(source_root)
    family_counts = {family: 0 for family in (*FAMILY_PATTERNS.keys(), "source-file", "other")}
    family_bytes = {family: 0 for family in family_counts}
    inventory_entries: list[dict[str, Any]] = []
    for file_record in policy_files:
        family = classify_policy_path(str(file_record["path"]))
        family_counts[family] += 1
        family_bytes[family] += int(file_record["size"])
        inventory_entries.append(
            {
                "root": "sync-policy",
                "family": family,
                "path": file_record["path"],
                "size": file_record["size"],
                "sha256": file_record["sha256"],
            }
        )
    for file_record in source_files:
        family_counts["source-file"] += 1
        family_bytes["source-file"] += int(file_record["size"])
        inventory_entries.append(
            {
                "root": "source",
                "family": "source-file",
                "path": file_record["path"],
                "size": file_record["size"],
                "sha256": file_record["sha256"],
            }
        )
    inventory_sha256 = sha256_text(canonical_json(inventory_entries))
    return {
        "inventory_sha256": inventory_sha256,
        "file_count": len(inventory_entries),
        "total_bytes": sum(int(item["size"]) for item in inventory_entries),
        "family_counts": {family: family_counts[family] for family in sorted(family_counts)},
        "family_bytes": {family: family_bytes[family] for family in sorted(family_bytes)},
    }


def state_digest(state: dict[str, Any]) -> str:
    return sha256_text(canonical_json(state))


class LiveAgent:
    def __init__(
        self,
        *,
        iotox: Path,
        toxcore: Path,
        runtime: Path,
        state_root: Path,
        policy_root: Path,
    ) -> None:
        self.iotox = iotox
        self.toxcore = toxcore
        self.runtime = runtime
        self.state_root = state_root
        self.policy_root = policy_root
        self.process: subprocess.Popen[str] | None = None

    def __enter__(self) -> "LiveAgent":
        self.runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
        chmod_private(self.runtime)
        self.state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        chmod_private(self.state_root)
        argv = [
            str(self.iotox),
            "run",
            "--library",
            str(self.toxcore),
            "--runtime",
            str(self.runtime),
            "--state",
            str(self.state_root / "device.toxsave"),
            "--identity",
            str(self.state_root / "device.identity"),
            "--authority-ledger",
            str(self.state_root / "authority.ledger"),
            "--command-store",
            str(self.state_root / "commands.store"),
            "--no-default-bootstrap",
            "--no-default-relays",
            "--bootstrap",
            f"bootstrap.test:33445:{BOOTSTRAP_KEY}",
            "--enable-sync",
            "--sync-policy-root",
            str(self.policy_root),
        ]
        self.process = subprocess.Popen(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        socket_path = self.runtime / "control.sock"
        for _ in range(2400):
            if socket_path.exists():
                return self
            if self.process.poll() is not None:
                stderr = self.process.stderr.read() if self.process.stderr else ""
                raise ProductionPrefixError(f"Agent exited before control socket became ready: {stderr.strip()}")
            time.sleep(0.05)
        self.stop()
        raise ProductionPrefixError("Agent control socket did not become ready")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.stop()

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None

    def control(self, command: list[str], *, input_text: str | None = None) -> str:
        argv = [str(self.iotox), "--runtime", str(self.runtime), *command]
        result = subprocess.run(
            argv,
            text=True,
            input=input_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise ProductionPrefixError(
                f"control command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
            )
        return result.stdout


def owner_public_key(output: str) -> str:
    match = re.search(r"owner-public-key=([0-9A-Fa-f]{64})", output)
    require(match is not None, "owner public key was not present")
    return match.group(1).upper()


def initialize_authority(agent: LiveAgent) -> None:
    agent.control(["status"])
    agent.control(["authority-bootstrap-recall-stdin"], input_text=PHRASE)
    agent.control(["authority-migrate-v2-recall-stdin"], input_text=PHRASE)
    agent.control(["authority-migrate-v3-recall-stdin", "all"], input_text=PHRASE)
    owner = owner_public_key(agent.control(["recall-owner-public-key-stdin"], input_text=PHRASE))
    agent.control(["authority-grant-recall-stdin", owner, "owner", "all-v3"], input_text=PHRASE)


def replay_prefix(
    *,
    replay_tool: Path,
    log_device: str,
    cell_root: Path,
    filesystem: str,
    mark: str,
    expected_state: dict[str, Any],
    acknowledged_state: dict[str, Any],
    origin_size_mib: int,
    index: int,
) -> dict[str, Any]:
    replay_image = cell_root / f"replay-{mark}.{filesystem}.img"
    replay_mount = cell_root / f"replay-{index:02d}-{mark}-mnt"
    replay_mount.mkdir(mode=0o700)
    replay_device: str | None = None
    mounted = False
    try:
        lw.make_sparse(replay_image, origin_size_mib)
        replay_device = lw.losetup(replay_image)
        mark_entry, _find_output, find_output_sha256 = lw.replay_find_entry(replay_tool, log_device, mark)
        lw.replay_to_mark(replay_tool, log_device, replay_device, mark)
        lw.mount(replay_device, replay_mount, lw.mount_options(filesystem, readonly=True))
        mounted = True
        replayed_state = observe_state(replay_mount)
        lw.umount(replay_mount)
        mounted = False
        replayed_digest = state_digest(replayed_state)
        expected_digest = state_digest(expected_state)
        acknowledged_digest = state_digest(acknowledged_state)
        require(replayed_digest == expected_digest, f"{filesystem}/{mark} replayed unexpected production state")
        complete_current = mark == "sync-publish-generation-2"
        if complete_current:
            require(replayed_digest == acknowledged_digest, f"{filesystem}/{mark} did not replay acknowledged current")
        else:
            require(replayed_digest != acknowledged_digest, f"{filesystem}/{mark} unexpectedly replayed acknowledged current")
        return {
            "mark": mark,
            "production_boundary": MARKS[mark],
            "mark_entry": mark_entry,
            "find_output_sha256": find_output_sha256,
            "replayed_state_sha256": replayed_digest,
            "expected_state_sha256": expected_digest,
            "external_floor_state_sha256": acknowledged_digest,
            "replayed_equals_expected_prefix": True,
            "rollback_detected_against_ack_floor": not complete_current,
            "mutation_refused": not complete_current,
            "accepted_current": complete_current,
            "contains_secrets": False,
            "expected_summary": expected_state,
            "replayed_summary": replayed_state,
        }
    finally:
        if mounted:
            lw.cleanup_umount(replay_mount)
        lw.detach_loop(replay_device)


def run_cell(
    *,
    run_id: str,
    raw_root: Path,
    cell_index: int,
    filesystem: str,
    origin_size_mib: int,
    log_size_mib: int,
    replay_tool: Path,
    iotox: Path,
    toxcore: Path,
    keep_raw: bool,
) -> dict[str, Any]:
    cell_root = raw_root / f"cell-{cell_index:02d}-{filesystem}-production-prefix"
    cell_root.mkdir(mode=0o700)
    origin_image = cell_root / f"origin.{filesystem}.img"
    log_image = cell_root / "log-writes.bin"
    live_mount = cell_root / "live-mnt"
    safe_runtime = "".join(character.lower() if character.isalnum() else "_" for character in run_id.removeprefix("run."))
    runtime = Path(tempfile.mkdtemp(prefix=f"iotox-ppr-{safe_runtime}-{cell_index}-", dir="/tmp"))
    live_mount.mkdir(mode=0o700)
    origin_device: str | None = None
    log_device: str | None = None
    dm_live_name: str | None = None
    mounted_live = False
    try:
        lw.make_sparse(origin_image, origin_size_mib)
        lw.make_sparse(log_image, log_size_mib)
        origin_device = lw.losetup(origin_image)
        log_device = lw.losetup(log_image)
        dm_live_name = dm_name(run_id, cell_index, "log")
        live_device = lw.create_log_writes(dm_live_name, origin_device, log_device)
        lw.mkfs(live_device, filesystem)
        mark_log_writes(dm_live_name, "mkfs")
        lw.mount(live_device, live_mount, lw.mount_options(filesystem))
        mounted_live = True
        lw.chown_mount(live_mount)

        source_root = live_mount / "source"
        policy_root = live_mount / "sync-policy"
        agent_state = live_mount / "agent-state"
        policy_root.mkdir(mode=0o700)
        agent_state.mkdir(mode=0o700)
        chmod_private(policy_root)
        chmod_private(agent_state)
        write_fixture_source(source_root, "gen1\n")
        with LiveAgent(
            iotox=iotox,
            toxcore=toxcore,
            runtime=runtime,
            state_root=agent_state,
            policy_root=policy_root,
        ) as agent:
            initialize_authority(agent)
            create_output = agent.control(["sync-create", NAMESPACE, str(source_root), "read-write", "86400"])
            create_fields = parse_key_values(create_output)
            require(create_fields.get("decision") == "created", "sync-create did not create the namespace")
            gen1_repair = repair_summary(agent.control(["sync-repair", NAMESPACE]))
            require(gen1_repair["metadata"] == "verified", "generation-1 repair did not verify metadata")
            os.sync()
            mark_log_writes(dm_live_name, "sync-create-generation-1")
            gen1_state = observe_state(live_mount)

            write_fixture_source(source_root, "gen2 changed\n")
            publish_output = agent.control(["sync-publish", NAMESPACE, str(source_root)])
            publish_fields = parse_key_values(publish_output)
            require(publish_fields.get("engine") == "tree-v2", "sync-publish did not use tree-v2")
            gen2_repair = repair_summary(agent.control(["sync-repair", NAMESPACE]))
            require(gen2_repair["metadata"] == "verified", "generation-2 repair did not verify metadata")
            require(gen2_repair["selected_bytes"] > gen1_repair["selected_bytes"], "generation-2 repair did not observe larger selected bytes")
            os.sync()
            mark_log_writes(dm_live_name, "sync-publish-generation-2")
            gen2_state = observe_state(live_mount)

        lw.umount(live_mount)
        mounted_live = False
        os.sync()
        time.sleep(1.0)
        lw.dm_remove(dm_live_name, strict=True)
        dm_live_name = None
        lw.detach_loop(origin_device)
        origin_device = None

        expected = {
            "sync-create-generation-1": (gen1_state, gen1_repair),
            "sync-publish-generation-2": (gen2_state, gen2_repair),
        }
        prefix_results = []
        for prefix_index, mark in enumerate(MARKS):
            state, repair = expected[mark]
            result = replay_prefix(
                replay_tool=replay_tool,
                log_device=log_device,
                cell_root=cell_root,
                filesystem=filesystem,
                mark=mark,
                expected_state=state,
                acknowledged_state=gen2_state,
                origin_size_mib=origin_size_mib,
                index=prefix_index,
            )
            result["production_repair_result"] = repair
            prefix_results.append(result)

        return {
            "cell": cell_index,
            "filesystem": filesystem,
            "block_interposer": "device-mapper-log-writes",
            "claim_boundary": "live-agent-production-transaction-prefix-replay",
            "namespace_class": "fixture-single-directory-read-write",
            "replay_tool": str(replay_tool),
            "replay_tool_sha256": sha256_file(replay_tool),
            "iotox_binary_sha256": sha256_file(iotox),
            "toxcore_provider_sha256": sha256_file(toxcore),
            "origin_size_mib": origin_size_mib,
            "log_size_mib": log_size_mib,
            "contains_secrets": False,
            "raw_retained": keep_raw,
            "acknowledged_state_sha256": state_digest(gen2_state),
            "prefix_results": prefix_results,
        }
    finally:
        if mounted_live:
            lw.cleanup_umount(live_mount)
        lw.dm_remove(dm_live_name)
        lw.detach_loop(origin_device)
        lw.detach_loop(log_device)
        if runtime.exists() and runtime.parent == Path("/tmp") and runtime.name.startswith(f"iotox-ppr-{safe_runtime}-{cell_index}-"):
            shutil.rmtree(runtime)


def git_revision() -> str:
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"], check=False, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_verifier():
    verifier = ROOT / "tools/verify-sync-production-prefix-replay.py"
    spec = importlib.util.spec_from_file_location("iotox_production_prefix_verify", verifier)
    require(spec is not None and spec.loader is not None, "unable to load production prefix replay verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_test() -> int:
    verifier = load_verifier()
    summary = verifier.verify_record(verifier.sample_receipt())
    require(summary["cell_count"] == 2, "production prefix runner self-test verification failed")
    print("sync-production-prefix-replay-runner-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--origin-size-mib", type=int, default=512)
    parser.add_argument("--log-size-mib", type=int, default=2048)
    parser.add_argument("--filesystem", action="append", choices=FILESYSTEMS)
    parser.add_argument("--replay-log", type=Path)
    parser.add_argument("--iotox", type=Path, default=ROOT / "build/gcc-debug/iotox")
    parser.add_argument("--toxcore", type=Path, default=ROOT / "build/gcc-debug/libtoxcore-iotox-mock.so")
    parser.add_argument("--keep-raw", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    for tool in ("sudo", "dmsetup", "losetup", "mkfs.ext4", "mkfs.btrfs", "blockdev"):
        require(shutil.which(tool) is not None, f"{tool} is required")
    require(lw.target_present("log-writes"), "device-mapper log-writes target is unavailable")
    require(args.iotox.is_file() and os.access(args.iotox, os.X_OK), f"IoTox binary is not executable: {args.iotox}")
    require(args.toxcore.is_file(), f"toxcore mock provider is missing: {args.toxcore}")
    require(256 <= args.origin_size_mib <= 4096, "origin size must be 256..4096 MiB")
    require(512 <= args.log_size_mib <= 8192, "log size must be 512..8192 MiB")
    replay_tool = lw.find_replay_log(args.replay_log)

    run_id = args.run_id or random_run_id()
    require(RUN_ID.fullmatch(run_id) is not None, "run id must look like run.XXXXXXXX")
    state_root = validate_under(args.state_root, ROOT / ".sandwurm/lab", "state root")
    export_root = validate_under(args.export_root, ROOT / ".sandwurm/exports", "export root")
    raw_root = state_root / run_id
    evidence_root = export_root / run_id
    require(not raw_root.exists(), "raw run root already exists")
    require(not evidence_root.exists(), "export run root already exists")
    state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    export_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw_root.mkdir(mode=0o700)
    evidence_root.mkdir(mode=0o700)
    receipt_written = False
    try:
        filesystems = tuple(args.filesystem or FILESYSTEMS)
        cells = []
        for index, filesystem in enumerate(filesystems):
            cells.append(
                run_cell(
                    run_id=run_id,
                    raw_root=raw_root,
                    cell_index=index,
                    filesystem=filesystem,
                    origin_size_mib=args.origin_size_mib,
                    log_size_mib=args.log_size_mib,
                    replay_tool=replay_tool,
                    iotox=args.iotox.resolve(),
                    toxcore=args.toxcore.resolve(),
                    keep_raw=args.keep_raw,
                )
            )
        receipt = {
            "schema": SCHEMA,
            "status": "passed",
            "run_id": run_id,
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "tool": "tools/run-sync-production-prefix-replay.py",
            "verifier": "tools/verify-sync-production-prefix-replay.py",
            "git_revision": git_revision(),
            "contains_secrets": False,
            "filesystems": list(filesystems),
            "cells": cells,
            "nonclaims": [
                "not-storage-media-certification",
                "not-independent-backup-custody",
                "not-precious-data-readiness",
                "not-physical-power-removal",
                "not-internal-subtransaction-prefix-coverage",
                "not-backup",
            ],
        }
        receipt_path = evidence_root / "production-prefix-replay.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verifier = load_verifier()
        try:
            verification = verifier.verify_record(receipt)
        except Exception as error:  # verifier exception type is module-local
            raise ProductionPrefixError(f"production prefix verifier rejected the receipt: {error}") from error
        receipt_written = True
        verification_path = evidence_root / "production-prefix-replay-verification.json"
        verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema": "iotox.sync-production-prefix-replay-summary.v1",
            "status": "passed",
            "run_id": run_id,
            "receipt": str(receipt_path.relative_to(ROOT)),
            "receipt_sha256": sha256_file(receipt_path),
            "verification": str(verification_path.relative_to(ROOT)),
            "verification_sha256": sha256_file(verification_path),
            "cell_count": len(cells),
            "filesystems": list(filesystems),
            "marks": list(MARKS),
            "contains_secrets": False,
            "raw_retained": bool(args.keep_raw),
            "replay_tool": str(replay_tool),
            "replay_tool_sha256": sha256_file(replay_tool),
        }
        summary_path = evidence_root / "production-prefix-replay-summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    finally:
        if not args.keep_raw and raw_root.exists():
            lw.remove_raw_root(raw_root, state_root)
        if not receipt_written and evidence_root.exists():
            shutil.rmtree(evidence_root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProductionPrefixError, subprocess.CalledProcessError, OSError, json.JSONDecodeError) as error:
        print(f"sync production prefix replay failed: {error}", file=sys.stderr)
        raise SystemExit(1)
