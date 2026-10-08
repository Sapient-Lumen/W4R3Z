#!/usr/bin/env python3
"""Inspect a packaged LLMPoetry zip for member/path/mode integrity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_tree import PACKAGE_EXCLUDE, collect_files, sha256_file, verify_release_zip


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    parser.add_argument("--root")
    args = parser.parse_args()
    expected = None
    if args.root:
        expected = {rel: sha256_file(path) for path, rel in collect_files(Path(args.root), exclude=PACKAGE_EXCLUDE)}
    report = verify_release_zip(Path(args.zip), expected)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
