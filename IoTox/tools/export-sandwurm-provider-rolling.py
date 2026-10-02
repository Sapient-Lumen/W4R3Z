#!/usr/bin/env python3
"""Export a content-free compact mixed-provider Sandwurm proof."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAIR_ROOT = (ROOT / ".sandwurm/lab/pairs").resolve()
EXPORT_ROOT = (ROOT / ".sandwurm/exports/pairs").resolve()
PAIR_NAME = re.compile(r"pair\.[A-Za-z0-9_]+")
SCHEMA = "iotox.sandwurm-provider-rolling-compact.v0"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def load_verifier():
    path = ROOT / "tools/verify-sandwurm-provider-rolling.py"
    spec = importlib.util.spec_from_file_location("iotox_provider_rolling_verifier", path)
    require(spec is not None and spec.loader is not None, "unable to load provider verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export(source: Path, destination: Path) -> dict:
    source = source.resolve()
    destination = destination.resolve()
    require(source.parent == PAIR_ROOT, "source is not an immediate pair proof root")
    require(PAIR_NAME.fullmatch(source.name) is not None, "source proof name is invalid")
    require(source.is_dir() and not source.is_symlink(), "source proof root is absent or unsafe")
    require(destination.parent == EXPORT_ROOT, "destination escaped the compact export root")
    require(PAIR_NAME.fullmatch(destination.name) is not None, "destination name is invalid")
    require(not destination.exists(), "compact export destination already exists")

    verifier = load_verifier()
    verified = verifier.verify(source)
    require(verified.get("compact_export") is False, "source is already compact")
    manifest_path = source / verifier.MANIFEST_NAME
    manifest = load(manifest_path)
    require(
        manifest.get("proof_root_contains_private_guest_disks") is True,
        "source is not an uncompacted private provider proof",
    )
    source_manifest_sha256 = digest(manifest_path)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = Path(tempfile.mkdtemp(prefix=f".{source.name}.", dir=EXPORT_ROOT))
    os.chmod(temporary, 0o700)
    try:
        for relative in verifier.evidence_paths()[1:]:
            source_path = (source / relative).resolve()
            require(source_path.is_relative_to(source), f"source evidence escaped: {relative}")
            require(source_path.is_file() and not source_path.is_symlink(), f"source evidence absent: {relative}")
            destination_path = temporary / relative
            destination_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(source_path, destination_path)
            os.chmod(destination_path, 0o600)

        compact_declaration = {
            "schema": SCHEMA,
            "source_proof_id": source.name,
            "source_manifest_sha256": source_manifest_sha256,
            "source_proof_root_contained_private_guest_disks": True,
        }
        manifest["proof_root_contains_private_guest_disks"] = False
        manifest["compact_export"] = compact_declaration
        compact_manifest_path = temporary / verifier.MANIFEST_NAME
        compact_manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.chmod(compact_manifest_path, 0o600)
        files = {
            relative: digest(temporary / relative)
            for relative in verifier.evidence_paths()
        }
        export_manifest = {
            "schema": SCHEMA,
            "status": "passed",
            "contains_secrets": False,
            "source_proof_id": source.name,
            "source_manifest_sha256": source_manifest_sha256,
            "source_private_artifacts_omitted": [
                "bootstrap-secret-key",
                "guest-disks",
                "provider-savedata",
                "rendezvous-public-keys",
                "runtime-state",
            ],
            "files": files,
        }
        export_path = temporary / "compact-export.json"
        export_path.write_text(
            json.dumps(export_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(export_path, 0o600)
        verifier.verify(temporary, manifest["route_mode"])
        temporary.rename(destination)
        temporary = Path()
        return {
            "schema": SCHEMA,
            "status": "passed",
            "source_proof_id": source.name,
            "destination": str(destination),
            "route_mode": manifest["route_mode"],
            "allocated_bytes": int(
                subprocess.run(
                    ["du", "-s", "--block-size=1", "--", str(destination)],
                    check=True,
                    text=True,
                    capture_output=True,
                ).stdout.split(maxsplit=1)[0]
            ),
        }
    finally:
        if temporary != Path() and temporary.exists():
            shutil.rmtree(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof_root", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    args = parser.parse_args()
    output = args.output or EXPORT_ROOT / args.proof_root.name
    print(json.dumps(export(args.proof_root, output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"provider rolling export refused: {error}", file=sys.stderr)
        raise SystemExit(1)
