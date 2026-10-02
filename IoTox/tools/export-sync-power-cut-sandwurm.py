#!/usr/bin/env python3
"""Export the exact content-free surface of a synchronization power-cut proof."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


FILES = (
    "campaign.json",
    "epoch-1/live/workspace-export/power-cut/armed.json",
    "epoch-1/direct-cloud-hypervisor-live-chain.json",
    "epoch-1/live/cloud-hypervisor-launch.json",
    "epoch-1/prelaunch/runtime-root/direct-nixos-runtime-root.json",
    "epoch-2/live/workspace-export/guest-receipts/iotox/sync-power-cut.json",
    "epoch-2/live/workspace-export/guest-receipts/iotox/vm-smoke.json",
    "epoch-2/direct-cloud-hypervisor-live-chain.json",
    "epoch-2/live/cloud-hypervisor-launch.json",
    "epoch-2/prelaunch/runtime-root/direct-nixos-runtime-root.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, record: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    encoded = json.dumps(record, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    try:
        view = memoryview(encoded.encode("utf-8"))
        offset = 0
        while offset < len(view):
            offset += os.write(descriptor, view[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def export_proof(source: Path, output: Path, verifier: Path) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    verifier = verifier.resolve()
    if source.is_symlink() or not source.is_dir():
        raise RuntimeError("power-cut proof root is absent or unsafe")
    if output == source or output.is_relative_to(source) or source.is_relative_to(
        output
    ):
        raise RuntimeError("source and output roots must not contain one another")
    before = subprocess.run(
        [sys.executable, str(verifier), str(source)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=120,
    )
    if before.returncode != 0:
        raise RuntimeError(
            f"source proof did not verify: {(before.stderr or before.stdout).strip()}"
        )
    campaign = json.loads((source / "campaign.json").read_text(encoding="utf-8"))
    campaign_schema = campaign.get("schema") if isinstance(campaign, dict) else None
    if campaign_schema == "iotox.sync-power-cut-sandwurm.v2":
        proof_version = 2
    elif campaign_schema == "iotox.sync-power-cut-sandwurm.v3":
        proof_version = 3
    elif campaign_schema == "iotox.sync-power-cut-sandwurm.v4":
        proof_version = 4
    elif campaign_schema == "iotox.sync-power-cut-sandwurm.v5":
        proof_version = 5
    elif campaign_schema == "iotox.sync-power-cut-sandwurm.v6":
        proof_version = 6
    else:
        raise RuntimeError("source proof campaign schema is unsupported")

    if output.exists() or output.is_symlink():
        raise RuntimeError(f"compact output already exists: {output}")
    output.mkdir(mode=0o700, parents=True)

    entries: list[dict[str, object]] = []
    try:
        for relative in FILES:
            source_path = source / relative
            if source_path.is_symlink() or not source_path.is_file():
                raise RuntimeError(f"source evidence is absent or unsafe: {relative}")
            if source_path.stat().st_size > 4 * 1024 * 1024:
                raise RuntimeError(f"source evidence is oversized: {relative}")
            target = output / relative
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            shutil.copyfile(source_path, target, follow_symlinks=False)
            target.chmod(0o600)
            entries.append(
                {
                    "path": relative,
                    "bytes": target.stat().st_size,
                    "sha256": sha256_file(target),
                }
            )
        manifest = {
            "schema": f"iotox.sync-power-cut-sandwurm-compact.v{proof_version}",
            "status": "passed",
            "source_proof_root": str(source),
            "proof_root": str(output),
            "file_count": len(entries),
            "total_bytes": sum(int(entry["bytes"]) for entry in entries),
            "files": entries,
            "contains_secrets": False,
        }
        write_json_atomic(output / "compact-export.json", manifest)
        after = subprocess.run(
            [sys.executable, str(verifier), str(output)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=120,
        )
        if after.returncode != 0:
            raise RuntimeError(
                f"compact proof did not verify: {(after.stderr or after.stdout).strip()}"
            )
    except Exception:
        # The output is new and wholly owned by this invocation. Preserve a
        # failed export for diagnosis rather than recursively deleting it.
        raise

    return {
        **manifest,
        "manifest_sha256": sha256_file(output / "compact-export.json"),
    }


def load_verifier(path: Path) -> object:
    spec = importlib.util.spec_from_file_location("iotox_power_cut_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load the power-cut verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def self_test(verifier: Path) -> int:
    module = load_verifier(verifier)
    with tempfile.TemporaryDirectory(prefix="iotox-power-cut-exporter-") as raw:
        base = Path(raw)
        pairs = (
            (base / "source-v3", base / "compact-v3", 3, "pre-exchange-pending"),
            (base / "source-v4", base / "compact-v4", 4, "receive-staging-partial"),
            (
                base / "source-v5",
                base / "compact-v5",
                5,
                "manifest-install-temporary",
            ),
            (
                base / "source-v6",
                base / "compact-v6",
                6,
                "manifest-install-directory-fsync",
            ),
        )
        for source, output, version, boundary in pairs:
            module.write_fixture(source, version=version, boundary=boundary)
            report = export_proof(source, output, verifier)
            if report.get("file_count") != len(FILES):
                raise RuntimeError("compact exporter retained the wrong file count")
            if not (output / "compact-export.json").is_file():
                raise RuntimeError("compact exporter omitted its manifest")
        source, output, _, _ = pairs[0]
        try:
            export_proof(source, output, verifier)
        except RuntimeError as error:
            if "already exists" not in str(error):
                raise
        else:
            raise RuntimeError("compact exporter overwrote an existing proof")
    print("sync-power-cut-sandwurm-exporter-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof_root", nargs="?", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--verifier",
        type=Path,
        default=Path(__file__).resolve().with_name(
            "verify-sync-power-cut-sandwurm.py"
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    verifier = args.verifier.resolve()
    if args.self_test:
        if args.proof_root is not None or args.output_root is not None:
            raise RuntimeError("self-test accepts no proof roots")
        return self_test(verifier)
    if args.proof_root is None:
        parser.error("proof_root is required")
    source = args.proof_root.resolve()
    if args.output_root is None:
        output_parent = (
            Path(__file__).resolve().parent.parent
            / ".sandwurm/exports/sync-power-cut"
        )
        output = output_parent / source.name
    else:
        output = args.output_root.resolve()
    report = export_proof(source, output, verifier)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"sync power-cut export failed: {error}", file=sys.stderr)
        raise SystemExit(1)
