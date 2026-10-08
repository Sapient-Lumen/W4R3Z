#!/usr/bin/env python3
"""Verify or materialize two exact indexed digest files embedded in patch evidence.

The cumulative patch preserves each complete ``sha256:<digest>`` value inside
an equivocation report.  Appending the line feed required by the indexed
72-byte identity produces bytes that independently match the path-specific full
SHA-256 in INDEX/files.csv.  Nothing is admitted without that exact match.
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
    from canonical_coverage import CoverageError, load_index, prepare_root, snapshot_regular_file
    from safe_materialize import MaterializationError, materialize_exact_bytes, prepare_root_anchor
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass


class RecoveryError(RuntimeError):
    pass


RECIPES: dict[str, dict[str, Any]] = {
    "sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_1.digest.txt": {
        "bytes": b"sha256:11253b6b6409e9a925e0d43fd01721ee900525ef4b044a894fdda0641daf7ba0\n",
        "sha256": "f09d3e783265ec4fd69ec77cde9807bdb3804e4f454a66d001aa59e002aa2e90",
        "embedded_value": "sha256:11253b6b6409e9a925e0d43fd01721ee900525ef4b044a894fdda0641daf7ba0",
    },
    "sources/ocf_llm/examples/pcb_equivocation_demo_v238/subject_2.digest.txt": {
        "bytes": b"sha256:875622af0b1c8944d1e068386324a89fd6e1972feda9e860a3c09eba133bc3b2\n",
        "sha256": "8eba3d4c359dc7266d3d5e791a6e0c21930abb75db1b7c78a3246ca60f26e8a3",
        "embedded_value": "sha256:875622af0b1c8944d1e068386324a89fd6e1972feda9e860a3c09eba133bc3b2",
    },
}


def verify_recipes(root: Path, *, write: bool = False) -> dict[str, Any]:
    root = prepare_root_anchor(root)
    rows = {row["path"]: row for row in load_index(root)}
    results: list[dict[str, Any]] = []
    for rel, recipe in sorted(RECIPES.items()):
        data = recipe["bytes"]
        digest = hashlib.sha256(data).hexdigest()
        if digest != recipe["sha256"]:
            raise RecoveryError(f"internal recipe digest drift: {rel}")
        row = rows.get(rel)
        if row is None or row["size"] != len(data) or row["sha256"] != digest:
            raise RecoveryError(f"recipe does not match indexed identity: {rel}")
        try:
            snap = snapshot_regular_file(root, rel, f"rev0871 embedded-evidence target {rel}")
            status = "already_exact"
        except FileNotFoundError:
            if not write:
                raise RecoveryError(f"verified target is absent; rerun with --write: {rel}")
            result = materialize_exact_bytes(
                root, rel, data, expected_sha256=digest, allow_existing_exact=True
            )
            status = result.status
            snap = snapshot_regular_file(root, rel, f"rev0871 embedded-evidence target {rel}")
        if snap["size"] != len(data) or snap["sha256"] != digest:
            raise RecoveryError(f"existing target differs; no-clobber refusal: {rel}")
        results.append(
            {
                "path": rel,
                "size": len(data),
                "sha256": digest,
                "status": status,
                "derivation": "complete embedded digest string plus LF, accepted only by exact indexed size and SHA-256",
                "evidence": [
                    "INDEX/files.csv",
                    "PATCHES/rev0826-to-rev0840-cumulative.patch (equivocation_report.json subject digest values)",
                ],
            }
        )
    return {
        "revision": "rev0871",
        "mode": "write_missing_no_clobber" if write else "verify_only",
        "status": "ok",
        "files": results,
        "recovered_files": len(results),
        "recovered_bytes": sum(item["size"] for item in results),
        "acceptance_rule": "path, exact byte length, and full SHA-256 must match INDEX/files.csv",
        "nonclaim": "hash equality proves indexed byte identity, not independent historical producer intent",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = verify_recipes(args.root, write=args.write)
    except (RecoveryError, CoverageError, MaterializationError, OSError) as exc:
        print(f"recover-indexed-embedded-evidence-rev0871: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "recover-indexed-embedded-evidence-rev0871: OK: "
            f"{report['recovered_files']} files / {report['recovered_bytes']} bytes "
            f"({report['mode']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
