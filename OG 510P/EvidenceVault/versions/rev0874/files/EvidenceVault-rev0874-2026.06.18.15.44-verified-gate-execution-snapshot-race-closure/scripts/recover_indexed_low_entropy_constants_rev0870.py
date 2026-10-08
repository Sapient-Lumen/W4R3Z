#!/usr/bin/env python3
"""Verify or no-clobber materialize four exact low-entropy indexed payloads.

The recipes are intentionally narrow. A candidate is admissible only when its
exact byte length and SHA-256 match the identity already fixed by INDEX/files.csv.
Default operation is verify-only. --write creates only absent paths and refuses
to overwrite any existing bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    from canonical_coverage import (
        CoverageError,
        load_index,
        prepare_root,
        snapshot_regular_file,
    )
    from safe_materialize import MaterializationError, materialize_exact_bytes, prepare_root_anchor
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass


class RecoveryError(RuntimeError):
    pass


RECIPES: dict[str, dict[str, Any]] = {
    "sources/ocf_llm/examples/discovery_sdt_demo_v247/output.txt": {
        "bytes": b"hello SDT\n",
        "sha256": "836b37c417b56c8dfd8bf9d04f3e3e5068c73bb5949810d39501abcc5d253322",
        "derivation": "bounded semantic candidate for the SDT discovery demo, accepted solely by indexed size and SHA-256",
        "evidence": [
            "INDEX/files.csv",
            "PATCHES/rev0826-to-rev0840-cumulative.patch (receipt_836b37c417b56c8d and output path anchors)",
        ],
    },
    "sources/ocf_llm/examples/dsc_summary_v1.json": {
        "bytes": b'{"n":64,"x":0}',
        "sha256": "083e790596b55d0b157e77ac222fe3f36c8b2c27f4365582f77bb2d2a40c4eee",
        "derivation": "compact JSON encoding of surviving n_actual=64 and x_actual=0 trace values, accepted solely by indexed size and SHA-256",
        "evidence": [
            "INDEX/files.csv",
            "PATCHES/rev0826-to-rev0840-cumulative.patch (suiteCount/n_actual/x_actual anchors)",
        ],
    },
    "sources/ocf_llm/examples/dsc_buc_summary_v1.json": {
        "bytes": b'{"n":64,"x":0}',
        "sha256": "083e790596b55d0b157e77ac222fe3f36c8b2c27f4365582f77bb2d2a40c4eee",
        "derivation": "compact JSON encoding of surviving n_actual=64 and x_actual=0 trace values, accepted solely by indexed size and SHA-256",
        "evidence": [
            "INDEX/files.csv",
            "PATCHES/rev0826-to-rev0840-cumulative.patch (BUC path and suiteCount/n_actual/x_actual anchors)",
        ],
    },
    "sources/ocf_llm/examples/dsc_cbb_summary_v1.json": {
        "bytes": b'{"n":128,"x":0}',
        "sha256": "7f6e4595bed3392fb68b355ed50ba2f86823e5563e124c60eaaa187daac0c45a",
        "derivation": "compact JSON encoding of surviving n_actual=128 and x_actual=0 trace values, accepted solely by indexed size and SHA-256",
        "evidence": [
            "INDEX/files.csv",
            "PATCHES/rev0826-to-rev0840-cumulative.patch (CBB path and suiteCount/n_actual/x_actual anchors)",
        ],
    },
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_absent(root: Path, rel: str, data: bytes) -> None:
    """Compatibility wrapper around the shared exact no-clobber writer."""
    try:
        materialize_exact_bytes(
            root,
            rel,
            data,
            expected_sha256=_sha256(data),
            allow_existing_exact=False,
        )
    except MaterializationError as exc:
        raise RecoveryError(str(exc)) from exc


def verify_recipes(root: Path, *, write: bool = False) -> dict[str, Any]:
    root = prepare_root_anchor(root)
    rows = {row["path"]: row for row in load_index(root)}
    results: list[dict[str, Any]] = []
    for rel, recipe in RECIPES.items():
        data = recipe["bytes"]
        digest = _sha256(data)
        if digest != recipe["sha256"]:
            raise RecoveryError(f"internal recipe digest is inconsistent: {rel}")
        row = rows.get(rel)
        if row is None:
            raise RecoveryError(f"recipe path is absent from canonical index: {rel}")
        if row["size"] != len(data) or row["sha256"] != digest:
            raise RecoveryError(f"recipe does not match indexed identity: {rel}")
        try:
            existing = snapshot_regular_file(root, rel, f"recovery target {rel}")
        except FileNotFoundError:
            if not write:
                raise RecoveryError(f"verified recipe target is absent; rerun with --write: {rel}")
            try:
                _write_absent(root, rel, data)
            except (OSError, CoverageError) as exc:
                raise RecoveryError(f"cannot materialize {rel}: {exc}") from exc
            status = "written"
            existing = snapshot_regular_file(root, rel, f"recovery target {rel}")
        else:
            status = "already_exact"
        if existing["size"] != len(data) or existing["sha256"] != digest:
            raise RecoveryError(f"existing target differs; no-clobber refusal: {rel}")
        results.append(
            {
                "path": rel,
                "size": len(data),
                "sha256": digest,
                "status": status,
                "derivation": recipe["derivation"],
                "evidence": recipe["evidence"],
            }
        )
    return {
        "revision": "rev0870",
        "mode": "write_missing_no_clobber" if write else "verify_only",
        "status": "ok",
        "files": results,
        "recovered_files": len(results),
        "recovered_bytes": sum(item["size"] for item in results),
        "acceptance_rule": "path, exact byte length, and SHA-256 must match INDEX/files.csv",
        "nonclaim": "digest equality identifies bytes; it does not independently prove producer intent",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true", help="create only absent recipe paths")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = verify_recipes(args.root, write=args.write)
    except (RecoveryError, CoverageError, OSError) as exc:
        print(f"recover-indexed-low-entropy-constants-rev0870: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "recover-indexed-low-entropy-constants-rev0870: OK: "
            f"{report['recovered_files']} files / {report['recovered_bytes']} bytes "
            f"({report['mode']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
