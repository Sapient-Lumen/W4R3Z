#!/usr/bin/env python3
"""Verify AnonSync's single reviewed bundled-SQLite trust contract.

This verifier is intentionally independent of CMake. It reads the same profile
that CMake uses, hashes every retained vendor file, and compares the semantic
SQLite identity embedded in sqlite3.h and sqlite3.c. A release can therefore
retain machine-readable evidence without trusting a prior build directory.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final

PROFILE_RELATIVE: Final = Path("cmake/AnonSyncBundledSqliteProfile.cmake")
PROFILE_PREFIX: Final = "ANONSYNC_BUNDLED_SQLITE_"
REQUIRED_KEYS: Final[tuple[str, ...]] = (
    "ANONSYNC_BUNDLED_SQLITE_VERSION",
    "ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER",
    "ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE",
    "ANONSYNC_BUNDLED_SQLITE_SOURCE_ID",
    "ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE",
    "ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE_SHA3_256",
    "ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES",
    "ANONSYNC_BUNDLED_SQLITE_C_SHA256",
    "ANONSYNC_BUNDLED_SQLITE_C_SHA3_256",
    "ANONSYNC_BUNDLED_SQLITE_H_SHA256",
    "ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256",
    "ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256",
    "ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256",
)
PROFILE_SET_RE: Final = re.compile(
    r"set\(\s*(ANONSYNC_BUNDLED_SQLITE_[A-Z0-9_]+)\s+"
    r"(?:\"([^\"]*)\"|([0-9]+))\s*\)",
    re.MULTILINE,
)
MACRO_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "version": re.compile(
        r'^\s*#\s*define\s+SQLITE_VERSION\s+"([^"]+)"', re.MULTILINE
    ),
    "version_number": re.compile(
        r"^\s*#\s*define\s+SQLITE_VERSION_NUMBER\s+([0-9]+)", re.MULTILINE
    ),
    "source_id": re.compile(
        r'^\s*#\s*define\s+SQLITE_SOURCE_ID\s+"([^"]+)"', re.MULTILINE
    ),
}


class VerificationError(RuntimeError):
    """A profile or vendor invariant failed."""


@dataclass(frozen=True)
class FileExpectation:
    relative_path: Path
    algorithm: str
    profile_key: str


FILE_EXPECTATIONS: Final[tuple[FileExpectation, ...]] = (
    FileExpectation(Path("sqlite3.c"), "sha256", "ANONSYNC_BUNDLED_SQLITE_C_SHA256"),
    FileExpectation(Path("sqlite3.c"), "sha3_256", "ANONSYNC_BUNDLED_SQLITE_C_SHA3_256"),
    FileExpectation(Path("sqlite3.h"), "sha256", "ANONSYNC_BUNDLED_SQLITE_H_SHA256"),
    FileExpectation(
        Path("sqlite3ext.h"), "sha256", "ANONSYNC_BUNDLED_SQLITE_EXT_H_SHA256"
    ),
    FileExpectation(Path("LICENSE.md"), "sha256", "ANONSYNC_BUNDLED_SQLITE_LICENSE_SHA256"),
    FileExpectation(
        Path("UPSTREAM-PROVENANCE.md"),
        "sha256",
        "ANONSYNC_BUNDLED_SQLITE_PROVENANCE_SHA256",
    ),
)


def parse_profile(profile_path: Path) -> dict[str, str]:
    try:
        text = profile_path.read_text(encoding="utf-8")
    except OSError as error:
        raise VerificationError(f"cannot read profile {profile_path}: {error}") from error

    observed: dict[str, list[str]] = {}
    for match in PROFILE_SET_RE.finditer(text):
        key = match.group(1)
        value = match.group(2) if match.group(2) is not None else match.group(3)
        assert value is not None
        observed.setdefault(key, []).append(value)

    profile_keys_in_text = set(
        re.findall(r"\bANONSYNC_BUNDLED_SQLITE_[A-Z0-9_]+\b", text)
    )
    unknown = sorted(profile_keys_in_text.difference(REQUIRED_KEYS))
    if unknown:
        raise VerificationError(
            "profile contains unreviewed bundled-SQLite keys: " + ", ".join(unknown)
        )

    missing = [key for key in REQUIRED_KEYS if key not in observed]
    if missing:
        raise VerificationError("profile is missing keys: " + ", ".join(missing))

    duplicates = [key for key, values in observed.items() if len(values) != 1]
    if duplicates:
        raise VerificationError(
            "profile assigns keys more than once: " + ", ".join(sorted(duplicates))
        )

    values = {key: entries[0] for key, entries in observed.items()}
    for key in REQUIRED_KEYS:
        if not values[key]:
            raise VerificationError(f"profile value is empty: {key}")
    version = values["ANONSYNC_BUNDLED_SQLITE_VERSION"]
    version_match = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", version)
    if version_match is None:
        raise VerificationError("profile version is not a canonical dotted release")
    major, minor, patch = (int(part) for part in version_match.groups())

    if not values["ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER"].isdigit():
        raise VerificationError("profile version number is not an unsigned decimal integer")
    expected_version_number = major * 1_000_000 + minor * 1_000 + patch
    if int(values["ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER"]) != expected_version_number:
        raise VerificationError(
            "profile version number does not encode the dotted release: "
            f"expected {expected_version_number}"
        )

    if re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
        values["ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE"],
    ) is None:
        raise VerificationError("profile release date is not canonical ISO text")
    try:
        datetime.date.fromisoformat(values["ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE"])
    except ValueError as error:
        raise VerificationError("profile release date is not an ISO calendar date") from error
    if re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9a-f]{64}",
        values["ANONSYNC_BUNDLED_SQLITE_SOURCE_ID"],
    ) is None:
        raise VerificationError("profile source ID is not canonical SQLite identity text")

    archive_code = major * 1_000_000 + minor * 10_000 + patch * 100
    expected_archive = f"sqlite-amalgamation-{archive_code}.zip"
    if values["ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE"] != expected_archive:
        raise VerificationError(
            "profile amalgamation archive does not encode the dotted release: "
            f"expected {expected_archive}"
        )

    retained_files = values["ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES"].split(";")
    if len(set(retained_files)) != len(retained_files):
        raise VerificationError("profile retained-file inventory contains duplicates")
    for retained in retained_files:
        path = PurePosixPath(retained)
        if (
            not retained
            or "\\" in retained
            or path.is_absolute()
            or len(path.parts) != 1
            or path.parts[0] in {".", ".."}
        ):
            raise VerificationError(
                "profile retained-file inventory requires flat safe basenames: "
                f"{retained!r}"
            )
    for key in REQUIRED_KEYS:
        if key.endswith(("SHA256", "SHA3_256")):
            value = values[key]
            if re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise VerificationError(
                    f"profile digest is not 64 lowercase hexadecimal characters: {key}"
                )
    return values


def digest_file(path: Path, algorithm: str) -> str:
    try:
        digest = hashlib.new(algorithm)
    except ValueError as error:  # pragma: no cover - CPython always has both algorithms.
        raise VerificationError(f"hash algorithm is unavailable: {algorithm}") from error
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise VerificationError(f"cannot hash {path}: {error}") from error
    return digest.hexdigest()


def read_identity(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise VerificationError(f"cannot read SQLite identity from {path}: {error}") from error
    identity: dict[str, str] = {}
    for field, pattern in MACRO_PATTERNS.items():
        matches = pattern.findall(text)
        if len(matches) != 1:
            raise VerificationError(
                f"{path} must define exactly one SQLITE {field} identity; found {len(matches)}"
            )
        identity[field] = matches[0]
    return identity


def verify_vendor_inventory(
    vendor_dir: Path,
    expected_files: list[str],
) -> list[dict[str, str]]:
    if vendor_dir.is_symlink():
        raise VerificationError(
            f"bundled SQLite directory must not be a symlink: {vendor_dir}"
        )

    observed_files: list[str] = []
    try:
        with os.scandir(vendor_dir) as entries:
            for entry in entries:
                if entry.is_symlink():
                    raise VerificationError(
                        "bundled SQLite retained entry must not be a symlink: "
                        f"{entry.name}"
                    )
                if not entry.is_file(follow_symlinks=False):
                    raise VerificationError(
                        "bundled SQLite retained entry must be a regular file: "
                        f"{entry.name}"
                    )
                observed_files.append(entry.name)
    except OSError as error:
        raise VerificationError(
            f"cannot inventory bundled SQLite directory {vendor_dir}: {error}"
        ) from error

    expected = sorted(expected_files)
    observed = sorted(observed_files)
    if observed != expected:
        missing = sorted(set(expected).difference(observed))
        extra = sorted(set(observed).difference(expected))
        raise VerificationError(
            "bundled SQLite retained-file inventory mismatch: "
            f"missing={missing}, extra={extra}"
        )
    return [
        {
            "check": "vendor:closed-retained-file-inventory",
            "files": ";".join(observed),
            "status": "pass",
        },
        {
            "check": "vendor:regular-nonsymlink-entry-types",
            "files": str(len(observed)),
            "status": "pass",
        },
    ]


def verify(root: Path, profile_path: Path) -> dict[str, object]:
    profile = parse_profile(profile_path)
    version = profile["ANONSYNC_BUNDLED_SQLITE_VERSION"]
    vendor_relative = Path("third_party") / f"sqlite-{version}"
    vendor_dir = root / vendor_relative
    if not vendor_dir.is_dir():
        raise VerificationError(f"bundled SQLite directory is missing: {vendor_dir}")

    retained_files = profile["ANONSYNC_BUNDLED_SQLITE_RETAINED_FILES"].split(";")
    checks: list[dict[str, str]] = verify_vendor_inventory(
        vendor_dir,
        retained_files,
    )
    for expectation in FILE_EXPECTATIONS:
        path = vendor_dir / expectation.relative_path
        actual = digest_file(path, expectation.algorithm)
        expected = profile[expectation.profile_key]
        if actual != expected:
            raise VerificationError(
                f"{expectation.relative_path} {expectation.algorithm} mismatch: "
                f"expected {expected}, observed {actual}"
            )
        checks.append(
            {
                "check": f"{expectation.relative_path}:{expectation.algorithm}",
                "digest": actual,
                "status": "pass",
            }
        )

    expected_identity = {
        "version": version,
        "version_number": profile["ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER"],
        "source_id": profile["ANONSYNC_BUNDLED_SQLITE_SOURCE_ID"],
    }
    header_identity = read_identity(vendor_dir / "sqlite3.h")
    amalgamation_identity = read_identity(vendor_dir / "sqlite3.c")
    for source_name, identity in (
        ("sqlite3.h", header_identity),
        ("sqlite3.c", amalgamation_identity),
    ):
        if identity != expected_identity:
            raise VerificationError(
                f"{source_name} semantic identity mismatch: expected "
                f"{json.dumps(expected_identity, sort_keys=True)}, observed "
                f"{json.dumps(identity, sort_keys=True)}"
            )
        checks.append(
            {
                "check": f"{source_name}:semantic-identity",
                "status": "pass",
                **identity,
            }
        )
    if header_identity != amalgamation_identity:
        raise VerificationError("sqlite3.h and sqlite3.c semantic identities diverge")

    return {
        "format": "anonsync-bundled-sqlite-profile-verification-v1",
        "status": "pass",
        "root": str(root),
        "profile": str(profile_path),
        "vendor_directory": str(vendor_relative),
        "version": version,
        "version_number": int(profile["ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER"]),
        "release_date": profile["ANONSYNC_BUNDLED_SQLITE_RELEASE_DATE"],
        "source_id": profile["ANONSYNC_BUNDLED_SQLITE_SOURCE_ID"],
        "amalgamation_archive": profile[
            "ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE"
        ],
        "amalgamation_archive_sha3_256": profile[
            "ANONSYNC_BUNDLED_SQLITE_AMALGAMATION_ARCHIVE_SHA3_256"
        ],
        "retained_files": retained_files,
        "checks_passed": len(checks),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--compact", action="store_true")
    arguments = parser.parse_args(argv)

    root = arguments.root.resolve()
    profile_path = (
        arguments.profile.resolve()
        if arguments.profile is not None
        else root / PROFILE_RELATIVE
    )
    try:
        result = verify(root, profile_path)
    except VerificationError as error:
        print(f"bundled SQLite profile verification failed: {error}", file=sys.stderr)
        return 1

    rendered = json.dumps(
        result,
        sort_keys=True,
        indent=None if arguments.compact else 2,
    ) + "\n"
    if arguments.json_output is not None:
        output_path = arguments.json_output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
