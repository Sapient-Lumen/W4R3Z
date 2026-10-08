#!/usr/bin/env python3
"""Audit exact public-head derivation and reject source-lane authority drift."""
from __future__ import annotations

import argparse
import copy
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, write_csv, write_json  # noqa: E402
from materialize_current_public_head import (  # noqa: E402
    load_contract,
    materialize,
    validate_contract,
)
from source_bundle_locator import locate_source_bundle  # noqa: E402


def audit(root: Path, source_zip: Path) -> dict[str, Any]:
    revision = derive_revision(root)
    contract = load_contract(root)
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    def add(check: str, passed: bool, detail: object = "") -> None:
        rows.append({"check": check, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{check}: {detail}")

    shape_errors = validate_contract(root, contract)
    add("public-head contract", not shape_errors, shape_errors)
    scratch = Path(tempfile.mkdtemp(prefix=f"{revision}-public-head-", dir="/mnt/data"))
    source = scratch / "source"
    try:
        result = materialize(source_zip, source, root=root, contract=contract)
        add("exact public-head materialization", result.get("status") == "pass", result.get("status"))
        add("target ref", result.get("target_ref") == contract.get("target_ref"), result.get("target_ref"))
        add("changed path count", len(result.get("changed_paths", [])) == 8, result.get("changed_paths"))
        target = result.get("target_tree", {})
        derivation = contract.get("derivation", {})
        add("target inventory digest", target.get("inventory_sha256") == derivation.get("target_tree_inventory_sha256"), target)
        add("target file count", target.get("files") == derivation.get("tree_file_count"), target.get("files"))
        add("target byte count", target.get("bytes") == derivation.get("tree_bytes"), target.get("bytes"))
    except Exception as exc:
        result = {"status": "fail", "error": str(exc)}
        add("exact public-head materialization", False, exc)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    add("materialization scratch removed", not scratch.exists(), scratch)

    mutants: list[tuple[str, dict[str, Any]]] = []
    wrong_patch = copy.deepcopy(contract)
    wrong_patch["derivation"]["delta_patch"]["sha256"] = "0" * 64
    mutants.append(("wrong delta digest", wrong_patch))
    duplicate_path = copy.deepcopy(contract)
    duplicate_path["derivation"]["changed_files"].append(copy.deepcopy(duplicate_path["derivation"]["changed_files"][0]))
    mutants.append(("duplicate changed path", duplicate_path))
    wrong_base = copy.deepcopy(contract)
    wrong_base["base_ref"] = "0" * 40
    mutants.append(("wrong base ref", wrong_base))
    wrong_target = copy.deepcopy(contract)
    wrong_target["target_ref"] = "1" * 40
    mutants.append(("wrong target ref", wrong_target))
    candidate_overlap = copy.deepcopy(contract)
    candidate_overlap["candidate"]["target_paths"].append(candidate_overlap["derivation"]["changed_files"][0]["path"])
    mutants.append(("candidate/delta overlap", candidate_overlap))
    stale_revision = copy.deepcopy(contract)
    stale_revision["revision"] = "rev0084"
    mutants.append(("stale revision", stale_revision))
    missing_commit = copy.deepcopy(contract)
    missing_commit["derivation"]["commit_sequence"].pop()
    mutants.append(("incomplete commit sequence", missing_commit))
    for label, mutant in mutants:
        add(f"mutation rejected: {label}", bool(validate_contract(root, mutant)), label)

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "mutation_controls": len(mutants),
        "target_ref": contract.get("target_ref"),
        "materialization": result,
        "rows": rows,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_public_head_audit.json", {k: v for k, v in result.items() if k != "rows"})
    write_csv(root / f"data/{revision}_public_head_checks.csv", result["rows"], fields=("check", "status", "detail"))
    lines = [
        f"# {revision} exact public-head materialization audit", "",
        f"Status: **{result['status']}**", "", "```text",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        f"mutation controls: {result['mutation_controls']}",
        f"target ref: {result['target_ref']}", "```", "",
        "The public source tree is materialized outside the package and deleted after validation.", "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {item}" for item in result["errors"]])
    (root / f"evidence/{revision}-public-head-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    source_zip, _rows = locate_source_bundle(args.source_zip)
    result = audit(root, source_zip)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({k: v for k, v in result.items() if k != "rows"}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
