#!/usr/bin/env python3
"""Adversarial tests for the native CMake bundled-SQLite build gate."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from verify_bundled_sqlite_profile import parse_profile


def run(
    command: list[str],
    *,
    expect_success: bool,
    label: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    succeeded = result.returncode == 0
    if succeeded != expect_success:
        raise RuntimeError(
            f"{label}: expected success={expect_success}, rc={result.returncode}, "
            f"output={result.stdout!r}"
        )
    return result


def run_gate(cmake: Path, root: Path, *, expect_success: bool, label: str) -> None:
    run(
        [
            str(cmake),
            f"-DANONSYNC_SOURCE_ROOT:PATH={root}",
            "-P",
            str(root / "cmake/AnonSyncVerifyBundledSqliteAtBuild.cmake"),
        ],
        expect_success=expect_success,
        label=label,
    )


def replace_profile_value(profile: Path, key: str, value: str) -> None:
    text = profile.read_text(encoding="utf-8")
    pattern = re.compile(
        rf'(set\(\s*{re.escape(key)}\s+)(?:"[^"]*"|[0-9]+)(\s*\))'
    )
    changed, count = pattern.subn(rf'\g<1>"{value}"\g<2>', text)
    if count != 1:
        raise RuntimeError(f"could not update {key}; substitutions={count}")
    profile.write_text(changed, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cmake", type=Path, required=True)
    arguments = parser.parse_args()

    source_root = arguments.root.resolve()
    cmake = arguments.cmake.resolve()
    source_profile = source_root / "cmake/AnonSyncBundledSqliteProfile.cmake"
    profile_values = parse_profile(source_profile)
    version = profile_values["ANONSYNC_BUNDLED_SQLITE_VERSION"]
    source_vendor = source_root / "third_party" / f"sqlite-{version}"

    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="anonsync-native-sqlite-build-gate-"
    ) as temp:
        root = Path(temp).resolve()
        shutil.copytree(source_root / "cmake", root / "cmake")
        vendor = root / "third_party" / f"sqlite-{version}"
        vendor.parent.mkdir(parents=True)
        shutil.copytree(source_vendor, vendor)
        profile = root / "cmake/AnonSyncBundledSqliteProfile.cmake"

        run_gate(cmake, root, expect_success=True, label="clean native gate")
        checks += 1

        sqlite_c = vendor / "sqlite3.c"
        with sqlite_c.open("ab") as handle:
            handle.write(b"\n/* native gate adversarial byte */\n")
        run_gate(cmake, root, expect_success=False, label="native byte tamper")
        checks += 1
        shutil.copy2(source_vendor / "sqlite3.c", sqlite_c)

        extra = vendor / "UNREVIEWED-NATIVE-GATE.bin"
        extra.write_bytes(b"undeclared\n")
        run_gate(cmake, root, expect_success=False, label="native extra file")
        checks += 1
        extra.unlink()

        ext_h = vendor / "sqlite3ext.h"
        ext_h.unlink()
        ext_h.symlink_to(source_vendor / "sqlite3ext.h")
        run_gate(cmake, root, expect_success=False, label="native symlink substitution")
        checks += 1
        ext_h.unlink()
        shutil.copy2(source_vendor / "sqlite3ext.h", ext_h)

        replace_profile_value(
            profile,
            "ANONSYNC_BUNDLED_SQLITE_VERSION",
            f"../sqlite-{version}",
        )
        run_gate(cmake, root, expect_success=False, label="native vendor path escape")
        checks += 1
        shutil.copy2(source_profile, profile)

        replace_profile_value(
            profile,
            "ANONSYNC_BUNDLED_SQLITE_VERSION_NUMBER",
            "3053004",
        )
        run_gate(cmake, root, expect_success=False, label="native incoherent version number")
        checks += 1
        shutil.copy2(source_profile, profile)

        (root / "probe.c").write_text("int anonsync_gate_probe(void) { return 0; }\n")
        (root / "CMakeLists.txt").write_text(
            "\n".join(
                [
                    "cmake_minimum_required(VERSION 3.20)",
                    "project(anonsync_native_gate_probe LANGUAGES C)",
                    'include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AnonSyncBundledSqliteProfile.cmake")',
                    'include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AnonSyncVerifyBundledSqlite.cmake")',
                    'anonsync_verify_bundled_sqlite_profile("${CMAKE_CURRENT_SOURCE_DIR}")',
                    "add_library(anonsync_native_gate_probe STATIC probe.c)",
                    "anonsync_add_bundled_sqlite_build_gate(",
                    "  anonsync_native_gate_probe",
                    '  "${CMAKE_CURRENT_SOURCE_DIR}")',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        build = root / "build"
        run(
            [str(cmake), "-S", str(root), "-B", str(build)],
            expect_success=True,
            label="native gate probe configure",
        )
        run(
            [str(cmake), "--build", str(build), "--target", "anonsync_native_gate_probe"],
            expect_success=True,
            label="native gate probe clean build",
        )
        sqlite_h = vendor / "sqlite3.h"
        with sqlite_h.open("ab") as handle:
            handle.write(b"\n/* post-configure mutation */\n")
        run(
            [str(cmake), "--build", str(build), "--target", "anonsync_native_gate_probe"],
            expect_success=False,
            label="post-configure mutation rejected before target build",
        )
        checks += 1

    print(f"native bundled SQLite build-gate adversarial tests passed={checks}/7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
