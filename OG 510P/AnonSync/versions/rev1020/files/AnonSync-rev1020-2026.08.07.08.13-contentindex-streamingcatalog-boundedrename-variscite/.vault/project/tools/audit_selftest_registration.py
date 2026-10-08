#!/usr/bin/env python3
"""Fail when a public anonsync_core selftest is not registered with CTest."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

SELFTEST_PATTERN = re.compile(r"--selftest-[a-z0-9-]+")
REGISTERED_PATTERN = re.compile(
    r"COMMAND\s+anonsync_core\s+(--selftest-[a-z0-9-]+)",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=pathlib.Path)
    parser.add_argument("--binary", required=True, type=pathlib.Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    binary = args.binary.resolve()
    cmake_path = root / "CMakeLists.txt"

    if not binary.is_file():
        print(f"selftest registration audit: binary not found: {binary}", file=sys.stderr)
        return 2
    if not cmake_path.is_file():
        print(f"selftest registration audit: CMakeLists.txt not found: {cmake_path}", file=sys.stderr)
        return 2

    completed = subprocess.run(
        [str(binary), "--help"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    help_text = completed.stdout + completed.stderr
    advertised = sorted(set(SELFTEST_PATTERN.findall(help_text)))
    registered = sorted(set(REGISTERED_PATTERN.findall(cmake_path.read_text())))
    missing = sorted(set(advertised) - set(registered))
    unadvertised = sorted(set(registered) - set(advertised))
    passed = completed.returncode == 0 and bool(advertised) and not missing and not unadvertised

    result = {
        "format": "anonsync-selftest-registration-audit-v1",
        "binary_help_exit_code": completed.returncode,
        "advertised_count": len(advertised),
        "registered_count": len(registered),
        "advertised": advertised,
        "registered": registered,
        "missing_from_ctest": missing,
        "registered_but_unadvertised": unadvertised,
        "passed": passed,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
