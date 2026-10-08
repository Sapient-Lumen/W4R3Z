#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, prune_cold_evidence, validate_core_tiering
from src.muc5.package_contract import audit_package_contract, write_checksum_manifest


def prune_generated(root: Path) -> list[str]:
    removed: list[str] = []
    build = root / "build"
    if build.exists():
        shutil.rmtree(build)
        removed.append("build/")
    for directory in sorted(root.rglob("__pycache__")):
        if directory.is_dir():
            relative = directory.relative_to(root).as_posix() + "/"
            shutil.rmtree(directory)
            removed.append(relative)
    for directory in sorted(root.rglob(".pytest_cache")):
        if directory.is_dir():
            relative = directory.relative_to(root).as_posix() + "/"
            shutil.rmtree(directory)
            removed.append(relative)
    for suffix in ("*.pyc", "*.pyo"):
        for path in root.rglob(suffix):
            if path.is_file():
                removed.append(path.relative_to(root).as_posix())
                path.unlink()
    return sorted(set(removed))


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune generated/cold files, write checksums, and audit a cloudtainer.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--no-prune", action="store_true")
    parser.add_argument("--keep-cold-evidence", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    removed = [] if args.no_prune else prune_generated(root)
    cold_result: dict[str, object] = {"removed": [], "removed_count": 0, "removed_bytes": 0}
    catalog_path = find_tiering_catalog(root)
    tier_validation: dict[str, object] | None = None
    if catalog_path is not None and not args.keep_cold_evidence:
        catalog = load_tiering_catalog(catalog_path)
        cold_result = prune_cold_evidence(root, catalog)
        tier_validation = validate_core_tiering(root, catalog)
        if not tier_validation["passed"]:
            print(json.dumps({"cold_evidence": cold_result, "tier_validation": tier_validation}, indent=2, sort_keys=True))
            raise SystemExit(1)
    write_checksum_manifest(root)
    report = audit_package_contract(root)
    payload = {
        "removed_generated": removed,
        "cold_evidence": cold_result,
        "tier_validation": tier_validation,
        "contract": report.as_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
