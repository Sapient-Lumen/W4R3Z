#!/usr/bin/env python3
"""Verify a FreeBSD removable-media host-proof handoff directory.

Default mode is strict import mode.  It accepts only a directory containing
``receipt.json``, ``bundle.json``, and ``SHA256SUMS`` where the bundle validates
as ``real-host-proof`` against the original receipt with no non-proof flags.

``--allow-checker-simulation`` exists only for release-critical Linux tests of
the handoff mechanics.  It must not be used to import release evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cube_digest_lib import CanonicalJsonError, canonical_digest, load_json_strict_text  # noqa: E402
import host_proof_contract as contract  # noqa: E402
import validate_removable_media_local_fallback_host_proof_bundle as bundle_validator  # noqa: E402

RECEIPT_NAME = contract.RECEIPT_NAME
BUNDLE_NAME = contract.BUNDLE_NAME
SUMS_NAME = contract.SUMS_NAME
REQUIRED_NAMES = set(contract.HANDOFF_REQUIRED_NAMES)
_ALLOWED_EXTRA_NAMES = set(contract.HANDOFF_OPTIONAL_NAMES)
_ALLOWED_NAMES = set(contract.HANDOFF_ALLOWED_NAMES)
MAX_MEMBER_BYTES = contract.MAX_HANDOFF_MEMBER_BYTES
_CHECKSUM_REQUIRED_NAMES = set(contract.HANDOFF_CHECKSUM_REQUIRED_NAMES)
_CHECKSUM_OPTIONAL_NAMES = set(contract.HANDOFF_CHECKSUM_OPTIONAL_NAMES)
_CHECKSUM_ALLOWED_NAMES = set(contract.HANDOFF_CHECKSUM_ALLOWED_NAMES)
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
BSD_RE = re.compile(r"^SHA256 \((?P<name>[^)]+)\) = (?P<hex>[0-9a-fA-F]{64})$")
COREUTILS_RE = re.compile(r"^(?P<hex>[0-9a-fA-F]{64})\s+[ *]?(?P<name>.+)$")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def _safe_name(name: str) -> bool:
    return name in _CHECKSUM_ALLOWED_NAMES


def parse_sha256sums(path: Path, present_names: set[str] | None = None) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    rows: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return rows, ["SHA256SUMS must not be empty"]
    for line_no, line in enumerate(lines, 1):
        raw = line.strip()
        if not raw:
            continue
        match = BSD_RE.match(raw)
        if match:
            name = match.group("name")
            digest_hex = match.group("hex")
        else:
            match = COREUTILS_RE.match(raw)
            if not match:
                errors.append(f"SHA256SUMS line {line_no}: unsupported checksum syntax")
                continue
            name = match.group("name")
            digest_hex = match.group("hex")
        if not _safe_name(name):
            errors.append(f"SHA256SUMS line {line_no}: unexpected or unsafe filename {name!r}")
            continue
        if not HEX64_RE.match(digest_hex):
            errors.append(f"SHA256SUMS line {line_no}: digest is not lowercase hex64")
            continue
        if name in rows:
            errors.append(f"SHA256SUMS line {line_no}: duplicate digest row for {name}")
            continue
        rows[name] = "sha256:" + digest_hex
    present_names = present_names or set()
    for required in sorted(_CHECKSUM_REQUIRED_NAMES):
        if required not in rows:
            errors.append(f"SHA256SUMS missing digest row for {required}")
    for optional in sorted(_CHECKSUM_OPTIONAL_NAMES & present_names):
        if optional not in rows:
            errors.append(f"SHA256SUMS missing digest row for present optional handoff file {optional}")
    for name in sorted(set(rows) - present_names):
        errors.append(f"SHA256SUMS has digest row for absent handoff file {name}")
    return rows, errors


def validate_handoff_dir(path: Path, *, allow_checker_simulation: bool = False) -> list[str]:
    errors: list[str] = []
    if path.is_symlink():
        return [f"handoff directory must not be a symlink: {path}"]
    if not path.exists():
        return [f"handoff directory does not exist: {path}"]
    if not path.is_dir():
        return [f"handoff path is not a directory: {path}"]

    names = {child.name for child in path.iterdir()}
    missing = sorted(REQUIRED_NAMES - names)
    unexpected = sorted(names - REQUIRED_NAMES - _ALLOWED_EXTRA_NAMES)
    if missing:
        errors.append(f"handoff directory missing required files: {missing!r}")
    if unexpected:
        errors.append(f"handoff directory contains unexpected files: {unexpected!r}")
    for name in sorted(_ALLOWED_NAMES):
        if name not in names:
            continue
        candidate = path / name
        if candidate.is_symlink():
            errors.append(f"{name} must not be a symlink")
        elif not candidate.is_file():
            errors.append(f"{name} must be a regular file")
        elif candidate.stat().st_size > MAX_MEMBER_BYTES:
            errors.append(f"{name} exceeds finite handoff member size limit: {candidate.stat().st_size} > {MAX_MEMBER_BYTES} bytes")
    if errors:
        return errors

    sums, sum_errors = parse_sha256sums(path / SUMS_NAME, names)
    errors.extend(sum_errors)
    for name in sorted(_CHECKSUM_REQUIRED_NAMES | (_CHECKSUM_OPTIONAL_NAMES & names)):
        observed = sha256_file(path / name)
        expected = sums.get(name)
        if expected != observed:
            errors.append(f"{name} digest mismatch: SHA256SUMS {expected} != observed {observed}")
    try:
        receipt = _load_json(path / RECEIPT_NAME)
    except (OSError, CanonicalJsonError) as exc:
        errors.append(f"receipt.json strict JSON load failed: {exc}")
        receipt = None
    try:
        bundle = _load_json(path / BUNDLE_NAME)
    except (OSError, CanonicalJsonError) as exc:
        errors.append(f"bundle.json strict JSON load failed: {exc}")
        bundle = None
    if not isinstance(receipt, dict):
        errors.append("receipt.json root must be a JSON object")
    if not isinstance(bundle, dict):
        errors.append("bundle.json root must be a JSON object")
    if not isinstance(receipt, dict) or not isinstance(bundle, dict):
        return errors

    status = bundle.get("proof_status")
    if allow_checker_simulation:
        if status != "checker-simulation-non-proof":
            errors.append("--allow-checker-simulation handoff must remain checker-simulation-non-proof")
    else:
        if status != "real-host-proof":
            errors.append("default handoff verification accepts only real-host-proof bundles")

    summary = bundle.get("receipt", {}) if isinstance(bundle.get("receipt"), dict) else {}
    if summary.get("canonical_sha256") != canonical_digest(receipt):
        errors.append("bundle receipt.canonical_sha256 must match receipt.json")
    if summary.get("byte_sha256") != sha256_file(path / RECEIPT_NAME):
        errors.append("bundle receipt.byte_sha256 must match receipt.json bytes")

    errors.extend(
        bundle_validator.validate_bundle(
            bundle,
            path / BUNDLE_NAME,
            receipt_path=path / RECEIPT_NAME,
            allow_checker_simulation=allow_checker_simulation,
            allow_current_tool_drift=False,
        )
    )
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff_dir", type=Path, help="directory with receipt.json, bundle.json, and SHA256SUMS")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="accept checked non-proof handoff mechanics only")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    errors = validate_handoff_dir(args.handoff_dir, allow_checker_simulation=args.allow_checker_simulation)
    if errors:
        print("host-proof handoff verification FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("host-proof handoff verification OK")
    print(f"receipt_sha256:{sha256_file(args.handoff_dir / RECEIPT_NAME)}")
    print(f"bundle_sha256:{sha256_file(args.handoff_dir / BUNDLE_NAME)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
