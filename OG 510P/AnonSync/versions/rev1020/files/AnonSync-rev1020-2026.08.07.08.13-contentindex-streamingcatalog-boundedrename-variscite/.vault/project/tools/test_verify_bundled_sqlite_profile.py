#!/usr/bin/env python3
"""Adversarial self-test for verify_bundled_sqlite_profile.py."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from verify_bundled_sqlite_profile import parse_profile


def run(verifier: Path, root: Path, expect_success: bool, label: str) -> None:
    result = subprocess.run(
        [sys.executable, "-B", "-S", str(verifier), "--root", str(root), "--compact"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    succeeded = result.returncode == 0
    if succeeded != expect_success:
        raise RuntimeError(
            f"{label}: expected success={expect_success}, rc={result.returncode}, "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )


def replace_profile_value(profile: Path, key: str, value: str) -> None:
    text = profile.read_text(encoding="utf-8")
    pattern = re.compile(rf"(set\(\s*{re.escape(key)}\s+)(?:\"[^\"]*\"|[0-9]+)(\s*\))")
    changed, count = pattern.subn(rf'\g<1>"{value}"\g<2>', text)
    if count != 1:
        raise RuntimeError(f"could not update {key}; substitutions={count}")
    profile.write_text(changed, encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.root.resolve()
    verifier = source_root / "tools/verify_bundled_sqlite_profile.py"
    source_profile = source_root / "cmake/AnonSyncBundledSqliteProfile.cmake"
    profile_values = parse_profile(source_profile)
    version = profile_values["ANONSYNC_BUNDLED_SQLITE_VERSION"]
    source_vendor = source_root / "third_party" / f"sqlite-{version}"

    checks = 0
    run(verifier, source_root, True, "clean source")
    checks += 1

    with tempfile.TemporaryDirectory(prefix="anonsync-sqlite-profile-test-") as temp:
        root = Path(temp)
        shutil.copytree(source_root / "cmake", root / "cmake")
        shutil.copytree(source_root / "third_party", root / "third_party")
        profile = root / "cmake/AnonSyncBundledSqliteProfile.cmake"
        vendor = root / "third_party" / f"sqlite-{version}"

        sqlite_c = vendor / "sqlite3.c"
        with sqlite_c.open("ab") as handle:
            handle.write(b"\n/* adversarial byte */\n")
        run(verifier, root, False, "amalgamation byte tamper")
        checks += 1
        shutil.copy2(source_vendor / "sqlite3.c", sqlite_c)

        sqlite_h = vendor / "sqlite3.h"
        header_text = sqlite_h.read_text(encoding="utf-8").replace(
            f'#define SQLITE_VERSION        "{version}"',
            f'#define SQLITE_VERSION        "{version}-semantic-impostor"',
            1,
        )
        sqlite_h.write_text(header_text, encoding="utf-8")
        replace_profile_value(
            profile, "ANONSYNC_BUNDLED_SQLITE_H_SHA256", sha256(sqlite_h)
        )
        run(verifier, root, False, "hash-consistent header identity impostor")
        checks += 1
        shutil.copy2(source_vendor / "sqlite3.h", sqlite_h)
        replace_profile_value(
            profile, "ANONSYNC_BUNDLED_SQLITE_H_SHA256", sha256(sqlite_h)
        )

        ext_h = vendor / "sqlite3ext.h"
        with ext_h.open("ab") as handle:
            handle.write(b"\n/* adversarial extension header byte */\n")
        run(verifier, root, False, "extension header tamper")
        checks += 1
        shutil.copy2(source_vendor / "sqlite3ext.h", ext_h)

        extra = vendor / "UNREVIEWED-VENDOR-BYTE.bin"
        extra.write_bytes(b"unreviewed retained material\n")
        run(verifier, root, False, "undeclared retained vendor file")
        checks += 1
        extra.unlink()

        ext_h.unlink()
        ext_h.symlink_to(source_vendor / "sqlite3ext.h")
        run(verifier, root, False, "external symlink retained-file substitution")
        checks += 1
        ext_h.unlink()
        shutil.copy2(source_vendor / "sqlite3ext.h", ext_h)

        provenance = vendor / "UPSTREAM-PROVENANCE.md"
        with provenance.open("a", encoding="utf-8") as handle:
            handle.write("\nAdversarial provenance rewrite.\n")
        run(verifier, root, False, "provenance tamper")
        checks += 1
        shutil.copy2(
            source_vendor / "UPSTREAM-PROVENANCE.md",
            provenance,
        )

        with profile.open("a", encoding="utf-8") as handle:
            handle.write(
                f'\nset(ANONSYNC_BUNDLED_SQLITE_VERSION "{version}")\n'
            )
        run(verifier, root, False, "duplicate profile assignment")
        checks += 1
        shutil.copy2(source_root / "cmake/AnonSyncBundledSqliteProfile.cmake", profile)

        replace_profile_value(
            profile,
            "ANONSYNC_BUNDLED_SQLITE_VERSION",
            f"../sqlite-{version}",
        )
        run(verifier, root, False, "vendor-directory path escape")
        checks += 1
        shutil.copy2(source_root / "cmake/AnonSyncBundledSqliteProfile.cmake", profile)

        (vendor / "LICENSE.md").unlink()
        run(verifier, root, False, "missing retained vendor file")
        checks += 1

    print(f"bundled SQLite profile verifier adversarial tests passed={checks}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
