#!/usr/bin/env python3
"""Seal a finite FreeBSD host-proof handoff into a deterministic ZIP archive.

This is a transport helper, not a new proof source.  Default mode first verifies
that the handoff is strict ``real-host-proof`` and then writes an archive whose
members are exactly the checked handoff files.  Checker simulations require the
explicit non-proof flag used by release-critical Linux tests.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import host_proof_contract as contract  # noqa: E402
import import_removable_media_local_fallback_host_proof_handoff as handoff_importer  # noqa: E402
import verify_removable_media_local_fallback_host_proof_handoff as handoff_verifier  # noqa: E402

FIXED_ZIP_DATE = contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE
FIXED_FILE_MODE = contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE
ARCHIVE_FORMAT = contract.HANDOFF_ARCHIVE_FORMAT


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _present_handoff_names(handoff_dir: Path) -> list[str]:
    names: list[str] = []
    for name in sorted(contract.HANDOFF_ALLOWED_NAMES):
        if (handoff_dir / name).exists():
            names.append(name)
    return names


def _add_deterministic_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, FIXED_ZIP_DATE)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (FIXED_FILE_MODE & 0xFFFF) << 16
    zf.writestr(info, path.read_bytes())


def _replace_atomically(tmp_path: Path, output: Path, *, replace: bool) -> None:
    if output.exists() or output.is_symlink():
        if not replace:
            raise FileExistsError(f"archive already exists: {output}; pass --replace only for a deliberate rewrite")
        if output.is_symlink():
            raise ValueError(f"refusing to replace symlink archive path: {output}")
        if not output.is_file():
            raise ValueError(f"refusing to replace non-file archive path: {output}")
    os.replace(tmp_path, output)


# reject existing symlink components before host proof work
def _checked_handoff_dir(handoff_dir: Path) -> Path:
    """Return a real handoff directory path without following a final symlink."""
    raw_handoff = handoff_dir.expanduser()
    contract.require_no_existing_symlink_component(raw_handoff, "handoff directory")
    if raw_handoff.is_symlink():
        raise ValueError(f"handoff directory must not be a symlink: {raw_handoff}")
    if not raw_handoff.exists():
        raise FileNotFoundError(f"handoff directory does not exist: {raw_handoff}")
    if not raw_handoff.is_dir():
        raise ValueError(f"handoff path is not a directory: {raw_handoff}")
    return raw_handoff.resolve()


def _checked_output_path(output: Path) -> Path:
    """Return an absolute output path without following a final symlink."""
    raw_output = output.expanduser()
    contract.require_no_existing_symlink_component(raw_output, "archive output")
    if raw_output.is_symlink():
        raise ValueError(f"refusing to write archive through symlink path: {raw_output}")
    raw_parent = raw_output.parent
    raw_parent.mkdir(parents=True, exist_ok=True)
    contract.require_no_existing_symlink_component(raw_output, "archive output")
    if raw_parent.is_symlink() or not raw_parent.is_dir():
        raise ValueError(f"archive parent is not a real directory: {raw_parent}")
    checked = raw_parent.resolve() / raw_output.name
    if checked.is_symlink():
        raise ValueError(f"refusing to write archive through symlink path: {checked}")
    return checked


def _copy_handoff_for_seal(handoff_dir: Path, staging_handoff: Path, *, allow_checker_simulation: bool) -> None:
    """Copy and verify a nofollow staging snapshot before archive writes."""
    handoff_importer.copy_handoff(handoff_dir, staging_handoff)
    errors = handoff_verifier.validate_handoff_dir(staging_handoff, allow_checker_simulation=allow_checker_simulation)
    if errors:
        raise ValueError("staged handoff verification failed before sealing: " + "; ".join(errors[:10]))


def seal_handoff(
    handoff_dir: Path,
    *,
    output: Path,
    allow_checker_simulation: bool = False,
    replace: bool = False,
) -> Path:
    handoff_dir = _checked_handoff_dir(handoff_dir)
    errors = handoff_verifier.validate_handoff_dir(handoff_dir, allow_checker_simulation=allow_checker_simulation)
    if errors:
        raise ValueError("handoff verification failed before sealing: " + "; ".join(errors[:10]))

    output = _checked_output_path(output)

    work_dir = Path(tempfile.mkdtemp(prefix=f".{output.name}.seal-", dir=output.parent))
    staging_handoff = work_dir / "handoff"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.tmp-", suffix=".zip", dir=output.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        _copy_handoff_for_seal(handoff_dir, staging_handoff, allow_checker_simulation=allow_checker_simulation)
        with zipfile.ZipFile(tmp_path, mode="w", compression=zipfile.ZIP_STORED) as zf:
            for name in _present_handoff_names(staging_handoff):
                _add_deterministic_file(zf, staging_handoff / name, name)
        _replace_atomically(tmp_path, output, replace=replace)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    finally:
        if work_dir.exists():
            shutil.rmtree(work_dir)
    return output


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="seal a verified FreeBSD host-proof handoff into a deterministic ZIP archive")
    parser.add_argument("handoff_dir", type=Path, help="directory with receipt.json, bundle.json, and SHA256SUMS")
    parser.add_argument("--output", type=Path, required=True, help="deterministic handoff ZIP archive to write")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="seal checker-simulation-non-proof handoffs for release-critical tests only")
    parser.add_argument("--replace", action="store_true", help="replace an existing non-symlink regular archive file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        out = seal_handoff(
            args.handoff_dir,
            output=args.output,
            allow_checker_simulation=args.allow_checker_simulation,
            replace=args.replace,
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing archive command
        print("host-proof handoff seal FAILED", file=sys.stderr)
        print(f"- {exc}", file=sys.stderr)
        return 1
    print("host-proof handoff seal OK")
    print(f"archive_format={ARCHIVE_FORMAT}")
    print(f"seal_snapshot_policy={contract.HANDOFF_SEAL_SNAPSHOT_POLICY}")
    print(f"archive={out}")
    print(f"archive_sha256:{sha256_file(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
