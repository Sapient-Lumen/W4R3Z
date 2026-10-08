#!/usr/bin/env python3
"""Release-gate smoke check for strict release control-file parsing.

MANIFEST.sha256 and VERSION are control files, not tolerant prose files.  This
check keeps the shared parser and both verifier-facing expectations fail-closed
for CRLF, missing final LF, duplicate/unsorted manifest records, uppercase
hashes, and non-canonical VERSION bytes.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

import release_control_files
import verify_manifest

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expect_manifest_bad(raw: bytes, needle: str) -> None:
    _entries, problems = release_control_files.parse_manifest_bytes(raw)
    if not problems:
        fail(f"manifest negative probe unexpectedly passed: {raw!r}")
    joined = "\n".join(problems)
    if needle not in joined:
        fail(f"manifest negative probe did not report {needle!r}; problems={problems!r}")


def expect_version_bad(raw: bytes, needle: str) -> None:
    _version, problems = release_control_files.parse_version_bytes(raw)
    if not problems:
        fail(f"VERSION negative probe unexpectedly passed: {raw!r}")
    joined = "\n".join(problems)
    if needle not in joined:
        fail(f"VERSION negative probe did not report {needle!r}; problems={problems!r}")


def write_file(root: Path, rel: str, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def make_good_tree(root: Path) -> bytes:
    readme = b"minimal control-file tree\n"
    version = b"v999\n"
    write_file(root, "README.md", readme)
    write_file(root, "VERSION", version)
    entries = {
        "README.md": digest(readme),
        "VERSION": digest(version),
    }
    manifest = release_control_files.format_manifest_text(entries).encode("utf-8")
    write_file(root, release_control_files.MANIFEST_NAME, manifest)
    return manifest


def main() -> int:
    version_raw = (ROOT / release_control_files.VERSION_NAME).read_bytes()
    version, version_problems = release_control_files.parse_version_bytes(version_raw)
    if version_problems or version is None:
        fail("checked-in VERSION is not canonical: " + "; ".join(version_problems))

    manifest_raw = (ROOT / release_control_files.MANIFEST_NAME).read_bytes()
    _entries, manifest_problems = release_control_files.parse_manifest_bytes(manifest_raw)
    if manifest_problems:
        fail("checked-in MANIFEST.sha256 is not canonical: " + "; ".join(manifest_problems[:10]))

    good_entries = {
        "README.md": digest(b"ok\n"),
        "VERSION": digest(b"v999\n"),
    }
    good_manifest = release_control_files.format_manifest_text(good_entries).encode("utf-8")
    entries, problems = release_control_files.parse_manifest_bytes(good_manifest)
    if problems or entries != good_entries:
        fail(f"canonical manifest probe failed: entries={entries!r} problems={problems!r}")
    parsed_version, problems = release_control_files.parse_version_bytes(b"v999\n")
    if parsed_version != "v999" or problems:
        fail(f"canonical VERSION probe failed: version={parsed_version!r} problems={problems!r}")

    expect_manifest_bad(good_manifest.replace(b"\n", b"\r\n"), "CR bytes")
    expect_manifest_bad(good_manifest.rstrip(b"\n"), "end with a newline")
    expect_manifest_bad(good_manifest.upper(), "lowercase 64-hex")
    expect_manifest_bad(b"\n" + good_manifest, "blank lines")
    expect_manifest_bad(
        good_manifest + f"{good_entries['VERSION']}  VERSION\n".encode("utf-8"),
        "duplicate path",
    )
    expect_manifest_bad(
        f"{good_entries['VERSION']}  VERSION\n{good_entries['README.md']}  README.md\n".encode("utf-8"),
        "sorted by path",
    )

    prefix_digest = digest(b"prefix\n")
    child_digest = digest(b"child\n")
    expect_manifest_bad(
        (
            f"{good_entries['README.md']}  README.md\n"
            f"{good_entries['VERSION']}  VERSION\n"
            f"{prefix_digest}  docs/prefix\n"
            f"{child_digest}  docs/prefix/child.md\n"
        ).encode("utf-8"),
        "extraction shape conflict",
    )

    expect_version_bad(b"v999\r\n", "CR bytes")
    expect_version_bad(b"v999", "exactly one LF")
    expect_version_bad(b" v999\n", "surrounding whitespace")
    expect_version_bad(b"v999 \n", "surrounding whitespace")
    expect_version_bad(b"v999\n\n", "extra blank lines")
    expect_version_bad(b"version-999\n", "canonical bytes")
    expect_version_bad(b"v0999\n", "no leading zeroes")

    with tempfile.TemporaryDirectory(prefix="tes_control_files_") as td:
        base = Path(td)
        good = base / "good"
        good.mkdir()
        good_manifest = make_good_tree(good)
        result = verify_manifest.verify_tree(good)
        if not result.ok:
            fail("good synthetic tree failed manifest verification: " + "; ".join(result.problems[:10]))

        crlf_manifest = base / "crlf_manifest"
        shutil.copytree(good, crlf_manifest)
        (crlf_manifest / release_control_files.MANIFEST_NAME).write_bytes(good_manifest.replace(b"\n", b"\r\n"))
        result = verify_manifest.verify_tree(crlf_manifest)
        if result.ok or "CR bytes" not in "\n".join(result.problems):
            fail(f"CRLF manifest tree probe did not fail closed: {result.problems!r}")

        crlf_version = base / "crlf_version"
        shutil.copytree(good, crlf_version)
        write_file(crlf_version, "VERSION", b"v999\r\n")
        entries = {
            "README.md": digest(b"minimal control-file tree\n"),
            "VERSION": digest(b"v999\r\n"),
        }
        write_file(
            crlf_version,
            release_control_files.MANIFEST_NAME,
            release_control_files.format_manifest_text(entries).encode("utf-8"),
        )
        result = verify_manifest.verify_tree(crlf_version)
        if result.ok or "VERSION must use LF" not in "\n".join(result.problems):
            fail(f"CRLF VERSION tree probe did not fail closed: {result.problems!r}")

    print("PASS: release control files are canonical and CRLF/whitespace/ordering probes fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
