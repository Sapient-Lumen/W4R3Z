#!/usr/bin/env python3
"""Report IoTox synchronization storage-readiness gates without overclaiming."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATRIX_ROOT = ROOT / ".sandwurm/exports/sync-dishonest-storage"
DEFAULT_PREFIX_ROOT = ROOT / ".sandwurm/exports/sync-log-writes-prefix"
DEFAULT_PRODUCTION_PREFIX_ROOT = ROOT / ".sandwurm/exports/sync-production-prefix"
DEFAULT_BACKUP_CUSTODY_ROOT = ROOT / ".sandwurm/exports/sync-backup-custody"
MATRIX_RECEIPT = "matrix.json"
PREFIX_RECEIPT = "prefix-replay.json"
PRODUCTION_PREFIX_RECEIPT = "production-prefix-replay.json"
BACKUP_CUSTODY_RECEIPT = "backup-custody.json"


class ReadinessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision() -> str:
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"], check=False, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def latest_proof(root: Path, receipt_name: str) -> Path | None:
    if not root.is_dir():
        return None
    candidates = [path for path in root.iterdir() if path.is_dir() and (path / receipt_name).is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path / receipt_name).stat().st_mtime)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source)
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def proof_report(
    *,
    label: str,
    proof_path: Path | None,
    receipt_name: str,
    verifier_path: Path,
    module_name: str,
) -> dict[str, Any]:
    if proof_path is None:
        return {
            "label": label,
            "status": "absent",
            "accepted": False,
            "blockers": [f"no {label} proof found"],
        }
    receipt = proof_path / receipt_name if proof_path.is_dir() else proof_path
    if not receipt.is_file():
        return {
            "label": label,
            "status": "absent",
            "accepted": False,
            "path": str(proof_path),
            "blockers": [f"{receipt_name} is missing"],
        }
    verifier = load_module(verifier_path, module_name)
    record = load_json(receipt)
    try:
        verification = verifier.verify_record(record)
    except Exception as error:  # verifier exception type is tool-local
        return {
            "label": label,
            "status": "rejected",
            "accepted": False,
            "path": str(proof_path),
            "receipt": str(receipt),
            "blockers": [str(error)],
        }
    return {
        "label": label,
        "status": "accepted",
        "accepted": True,
        "path": str(proof_path),
        "receipt": str(receipt),
        "receipt_sha256": sha256_file(receipt),
        "run_id": verification.get("run_id"),
        "cell_count": verification.get("cell_count"),
        "filesystems": verification.get("filesystems"),
        "marks": verification.get("marks"),
        "scenarios": verification.get("scenarios"),
        "contains_secrets": verification.get("contains_secrets") is not False,
    }


def command_path(name: str) -> str | None:
    return shutil.which(name)


def target_present(name: str) -> bool | None:
    dmsetup = command_path("dmsetup")
    if dmsetup is None:
        return None
    argv = ["dmsetup", "targets"]
    if command_path("sudo") is not None:
        argv = ["sudo", *argv]
    result = subprocess.run(argv, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        return None
    return any(line.split(maxsplit=1)[0] == name for line in result.stdout.splitlines())


def find_replay_log() -> str | None:
    direct = command_path("replay-log")
    if direct is not None:
        return direct
    store = Path("/nix/store")
    if store.is_dir():
        candidates = sorted(store.glob("*-xfstests-*/lib/xfstests/src/log-writes/replay-log"))
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    return None


def build_report(
    matrix_proof: Path | None,
    prefix_proof: Path | None,
    production_prefix_proof: Path | None,
    backup_custody_proof: Path | None,
) -> dict[str, Any]:
    matrix = proof_report(
        label="same-host dishonest-storage matrix",
        proof_path=matrix_proof,
        receipt_name=MATRIX_RECEIPT,
        verifier_path=ROOT / "tools/verify-sync-dishonest-storage-matrix.py",
        module_name="iotox_matrix_verify_for_readiness",
    )
    prefix = proof_report(
        label="dm-log-writes prefix replay",
        proof_path=prefix_proof,
        receipt_name=PREFIX_RECEIPT,
        verifier_path=ROOT / "tools/verify-sync-log-writes-prefix-replay.py",
        module_name="iotox_prefix_verify_for_readiness",
    )
    production_prefix = proof_report(
        label="live-Agent production transaction-prefix replay",
        proof_path=production_prefix_proof,
        receipt_name=PRODUCTION_PREFIX_RECEIPT,
        verifier_path=ROOT / "tools/verify-sync-production-prefix-replay.py",
        module_name="iotox_production_prefix_verify_for_readiness",
    )
    backup_custody = proof_report(
        label="versioned recovery custody",
        proof_path=backup_custody_proof,
        receipt_name=BACKUP_CUSTODY_RECEIPT,
        verifier_path=ROOT / "tools/verify-sync-backup-custody.py",
        module_name="iotox_backup_custody_verify_for_readiness",
    )
    capabilities = {
        "dmsetup": command_path("dmsetup"),
        "dm_log_writes_target": target_present("log-writes"),
        "dm_flakey_target": target_present("flakey"),
        "dm_snapshot_target": target_present("snapshot"),
        "replay_log": find_replay_log(),
        "mkfs_ext4": command_path("mkfs.ext4"),
        "mkfs_btrfs": command_path("mkfs.btrfs"),
        "qemu_nbd": command_path("qemu-nbd"),
    }
    exact_substrate_accepted = matrix["accepted"] and prefix["accepted"]
    production_prefix_accepted = production_prefix["accepted"]
    local_storage_science_accepted = exact_substrate_accepted and production_prefix_accepted
    backup_custody_accepted = backup_custody["accepted"]
    live_agent_blockers = [] if production_prefix_accepted else [
        "dm-log-writes substrate replay is accepted, but no live Agent production transaction-prefix adapter receipt exists",
        "no receipt names actual Agent namespace class, binary SHA-256, transaction boundary, and replayed block prefix",
    ]
    backup_blockers = [] if backup_custody_accepted else [
        "no versioned recovery-custody receipt is accepted",
        "a receipt must prove a restored tree matched a versioned or immutable recovery source outside normal IoTox sync mutation",
        "this gate does not claim disk-loss, host-compromise, or filesystem-wide corruption protection",
    ]
    precious_blockers = []
    if not exact_substrate_accepted:
        precious_blockers.append("same-host storage substrate gates are incomplete")
    if not production_prefix_accepted:
        precious_blockers.append("live-Agent production transaction-prefix replay is incomplete")
    precious_blockers.extend(live_agent_blockers)
    if not backup_custody_accepted:
        precious_blockers.extend(backup_blockers)
    ready_for_precious_data = (
        local_storage_science_accepted
        and backup_custody_accepted
    )
    report = {
        "schema": "iotox.storage-readiness.v1",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_revision": git_revision(),
        "status": "ready" if ready_for_precious_data else "not-ready",
        "ready_for_precious_data": ready_for_precious_data,
        "contains_secrets": False,
        "accepted_local_storage_science": local_storage_science_accepted,
        "evidence": {
            "dishonest_storage_matrix": matrix,
            "dm_log_writes_prefix_replay": prefix,
            "live_agent_production_transaction_prefix_replay": production_prefix,
            "sync_recovery_custody": backup_custody,
        },
        "capabilities": capabilities,
        "gates": {
            "same_host_storage_substrate": {
                "status": "accepted" if exact_substrate_accepted else "blocked",
                "accepted": exact_substrate_accepted,
                "requires": [
                    "ext4+btrfs dishonest-storage matrix",
                    "ext4+btrfs dm-log-writes marked-prefix replay",
                ],
            },
            "live_agent_production_transaction_prefix_replay": {
                "status": "accepted" if production_prefix_accepted else "blocked",
                "accepted": production_prefix_accepted,
                "requires": [
                    "actual IoTox Agent with sync enabled",
                    "sync-create generation-1 transaction mark",
                    "sync-publish generation-2 transaction mark",
                    "ext4+btrfs dm-log-writes replay of those marks",
                ],
                **({"blockers": live_agent_blockers} if live_agent_blockers else {}),
                "nonclaim": "does not cover every internal subtransaction interleaving",
            },
            "sync_recovery_custody": {
                "status": "accepted" if backup_custody_accepted else "blocked",
                "accepted": backup_custody_accepted,
                **({"blockers": backup_blockers} if backup_blockers else {}),
                "scope": "sync-layer-recovery-custody",
                "nonclaims": [
                    "not-disk-loss-protection",
                    "not-host-compromise-protection",
                    "not-filesystem-wide-corruption-protection",
                ],
            },
            "precious_data_readiness": {
                "status": "accepted" if ready_for_precious_data else "blocked",
                "accepted": ready_for_precious_data,
                **({"blockers": precious_blockers} if precious_blockers else {}),
            },
        },
        "next_gate_commands": [
            "tools/iotox-repo.sh sync-dishonest-storage-matrix",
            "tools/iotox-repo.sh sync-log-writes-prefix-replay",
            "tools/iotox-repo.sh sync-production-prefix-replay",
            "python3 tools/verify-sync-backup-custody.py PATH/backup-custody.json",
            "tools/iotox-repo.sh storage-readiness",
        ],
        "nonclaims": [
            "does-not-qualify-or-certify-storage-media",
            "does-not-claim-disk-loss-host-compromise-or-filesystem-wide-corruption-protection",
        ],
    }
    return report


def sample_proof_tree(root: Path) -> tuple[Path, Path, Path, Path]:
    matrix_verifier = load_module(ROOT / "tools/verify-sync-dishonest-storage-matrix.py", "iotox_matrix_sample")
    prefix_verifier = load_module(ROOT / "tools/verify-sync-log-writes-prefix-replay.py", "iotox_prefix_sample")
    production_prefix_verifier = load_module(
        ROOT / "tools/verify-sync-production-prefix-replay.py",
        "iotox_production_prefix_sample",
    )
    backup_custody_verifier = load_module(ROOT / "tools/verify-sync-backup-custody.py", "iotox_backup_custody_sample")
    matrix_dir = root / "matrix" / "run.SELFtest"
    prefix_dir = root / "prefix" / "run.SELFtest"
    production_prefix_dir = root / "production-prefix" / "run.SELFtest"
    backup_custody_dir = root / "backup-custody" / "run.SELFtest"
    matrix_dir.mkdir(parents=True)
    prefix_dir.mkdir(parents=True)
    production_prefix_dir.mkdir(parents=True)
    backup_custody_dir.mkdir(parents=True)
    (matrix_dir / MATRIX_RECEIPT).write_text(
        json.dumps(matrix_verifier.sample_receipt(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (prefix_dir / PREFIX_RECEIPT).write_text(
        json.dumps(prefix_verifier.sample_receipt(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (production_prefix_dir / PRODUCTION_PREFIX_RECEIPT).write_text(
        json.dumps(production_prefix_verifier.sample_receipt(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (backup_custody_dir / BACKUP_CUSTODY_RECEIPT).write_text(
        json.dumps(backup_custody_verifier.sample_receipt(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return matrix_dir, prefix_dir, production_prefix_dir, backup_custody_dir


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-storage-readiness-") as raw:
        matrix_dir, prefix_dir, production_prefix_dir, backup_custody_dir = sample_proof_tree(Path(raw))
        report = build_report(matrix_dir, prefix_dir, production_prefix_dir, None)
        require(report["accepted_local_storage_science"] is True, "self-test did not accept local storage science")
        require(report["ready_for_precious_data"] is False, "self-test promoted precious-data readiness")
        require(report["gates"]["precious_data_readiness"]["status"] == "blocked", "self-test did not block precious data")
        complete = build_report(matrix_dir, prefix_dir, production_prefix_dir, backup_custody_dir)
        require(complete["gates"]["sync_recovery_custody"]["accepted"] is True, "self-test did not accept backup custody receipt")
        require(complete["ready_for_precious_data"] is True, "self-test did not accept complete synthetic readiness")
    print("iotox-storage-readiness-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-proof", type=Path)
    parser.add_argument("--prefix-proof", type=Path)
    parser.add_argument("--production-prefix-proof", type=Path)
    parser.add_argument("--backup-custody-proof", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    matrix_proof = args.matrix_proof or latest_proof(DEFAULT_MATRIX_ROOT, MATRIX_RECEIPT)
    prefix_proof = args.prefix_proof or latest_proof(DEFAULT_PREFIX_ROOT, PREFIX_RECEIPT)
    production_prefix_proof = args.production_prefix_proof or latest_proof(
        DEFAULT_PRODUCTION_PREFIX_ROOT,
        PRODUCTION_PREFIX_RECEIPT,
    )
    backup_custody_proof = args.backup_custody_proof or latest_proof(
        DEFAULT_BACKUP_CUSTODY_ROOT,
        BACKUP_CUSTODY_RECEIPT,
    )
    report = build_report(
        matrix_proof,
        prefix_proof,
        production_prefix_proof,
        backup_custody_proof,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReadinessError, OSError, json.JSONDecodeError) as error:
        print(f"storage readiness qualification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
