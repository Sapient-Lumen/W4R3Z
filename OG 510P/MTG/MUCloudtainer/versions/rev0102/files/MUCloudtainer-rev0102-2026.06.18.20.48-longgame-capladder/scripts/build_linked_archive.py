#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.archive_contract import audit_linked_archive, build_linked_archive, sha256_file
from src.muc5.package_contract import audit_package_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and audit an explicitly compressed linked cloudtainer archive.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compresslevel", type=int, default=9)
    parser.add_argument("--max-mib", type=float, default=64.0)
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or (root.parent / f"{root.name}.zip")).resolve()
    package = audit_package_contract(root)
    if not package.passed:
        print(json.dumps({"package_contract": package.as_dict()}, indent=2, sort_keys=True))
        raise SystemExit(1)
    build_linked_archive(root, output, compresslevel=args.compresslevel)
    archive = audit_linked_archive(
        output,
        expected_root=root.name,
        max_archive_bytes=int(args.max_mib * 1024 * 1024),
    )
    payload = {
        "archive": archive.as_dict(),
        "sha256": sha256_file(output),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not archive.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
