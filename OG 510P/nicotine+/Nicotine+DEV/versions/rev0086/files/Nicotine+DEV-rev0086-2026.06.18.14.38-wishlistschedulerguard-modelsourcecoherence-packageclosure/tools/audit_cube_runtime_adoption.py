#!/usr/bin/env python3
"""Measure helper duplication and enforce shared runtime use in current tools."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    write_csv,
    write_json,
)

CONTRACT = Path("data/current_runtime_adoption_contract.json")
HELPER_NAME_FAMILIES = {
    "canonical", "canonical_json", "cleanup_caches", "digest", "digest_file",
    "digest_stream", "isolated_env", "isolated_environment", "read_csv", "run",
    "purge_isolated_environment", "run_bounded", "run_logged", "safe_extract_lane", "safe_relative", "sha256",
    "sha256_path", "sha_bytes", "sha_path", "source_lane_head", "write_csv",
    "write_json",
}


def function_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((root / "tools").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            records.append({
                "path": path.relative_to(root).as_posix(),
                "name": "<syntax-error>",
                "line": exc.lineno or 0,
                "bytes": 0,
                "ast_sha256": "",
            })
            continue
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            segment = ast.get_source_segment(source, node) or ""
            normalized = ast.dump(node, include_attributes=False)
            records.append({
                "path": path.relative_to(root).as_posix(),
                "name": node.name,
                "line": node.lineno,
                "bytes": len(segment.encode("utf-8")),
                "ast_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
            })
    return records


def imports_runtime(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    return any(
        isinstance(node, ast.ImportFrom) and node.module == "cube_runtime"
        for node in tree.body
    )


def top_level_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def audit(root: Path) -> dict[str, Any]:
    revision = derive_revision(root)
    contract = json.loads((root / CONTRACT).read_text(encoding="utf-8"))
    records = function_records(root)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_name[str(row["name"])].append(row)
        if row["ast_sha256"]:
            by_hash[str(row["ast_sha256"])].append(row)

    helper_rows: list[dict[str, Any]] = []
    for name in sorted(HELPER_NAME_FAMILIES):
        rows = by_name.get(name, [])
        if not rows:
            continue
        helper_rows.append({
            "name": name,
            "definitions": len(rows),
            "files": len({row["path"] for row in rows}),
            "exact_variants": len({row["ast_sha256"] for row in rows}),
            "definition_bytes": sum(int(row["bytes"]) for row in rows),
            "paths": ";".join(sorted({str(row["path"]) for row in rows})),
        })

    exact_groups = [rows for rows in by_hash.values() if len(rows) > 1]
    exact_redundant_bytes = sum(
        (len(rows) - 1) * min(int(row["bytes"]) for row in rows)
        for rows in exact_groups
    )

    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("contract version", contract.get("version") == 3, contract.get("version"))
    runtime_path = root / str(contract.get("runtime_module", ""))
    add("runtime module exists", runtime_path.is_file(), runtime_path)
    revision_contract_relative = contract.get("revision_contract", "")
    add(
        "revision contract path",
        isinstance(revision_contract_relative, str) and bool(revision_contract_relative),
        revision_contract_relative,
    )
    try:
        revision_contract = json.loads(
            (root / str(revision_contract_relative)).read_text(encoding="utf-8")
        )
    except Exception as exc:
        revision_contract = {}
        add("revision contract readable", False, exc)
    else:
        add("revision contract readable", True, revision_contract_relative)
        add("revision contract version", revision_contract.get("version") == 2, revision_contract.get("version"))
        add("revision contract matches", revision_contract.get("revision") == revision, revision_contract.get("revision"))
    current_scripts = revision_contract.get("current_scripts", [])
    add(
        "current scripts list",
        isinstance(current_scripts, list) and all(isinstance(item, str) for item in current_scripts),
        current_scripts,
    )
    forbidden = set(contract.get("forbidden_redefinitions", []))
    for relative in current_scripts if isinstance(current_scripts, list) else []:
        path = root / relative
        add(f"current script exists: {relative}", path.is_file())
        if not path.is_file():
            continue
        add(f"imports cube_runtime: {relative}", imports_runtime(path))
        collisions = sorted(top_level_names(path) & forbidden)
        add(f"no shared helper redefinition: {relative}", not collisions, collisions)

    add("historical duplicate evidence present", len(helper_rows) >= 8, len(helper_rows))
    add("exact duplicate groups measured", len(exact_groups) > 0, len(exact_groups))

    result = {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "tool_files": len(list((root / "tools").glob("*.py"))),
        "top_level_functions": len(records),
        "helper_name_families_measured": len(helper_rows),
        "helper_definitions": sum(int(row["definitions"]) for row in helper_rows),
        "helper_definition_bytes": sum(int(row["definition_bytes"]) for row in helper_rows),
        "exact_duplicate_function_groups": len(exact_groups),
        "exact_redundant_function_bytes_lower_bound": exact_redundant_bytes,
        "current_scripts": current_scripts,
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "errors": errors,
        "helper_rows": helper_rows,
    }
    return result


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = str(result["revision"])
    write_json(root / f"data/{revision}_runtime_helper_audit.json", result)
    write_csv(
        root / f"data/{revision}_runtime_helper_inventory.csv",
        result["helper_rows"],
        fields=("name", "definitions", "files", "exact_variants", "definition_bytes", "paths"),
    )
    lines = [
        f"# {revision} shared-runtime adoption audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"tool files: {result['tool_files']}",
        f"top-level functions: {result['top_level_functions']}",
        f"helper families measured: {result['helper_name_families_measured']}",
        f"helper definitions: {result['helper_definitions']}",
        f"helper definition bytes: {result['helper_definition_bytes']}",
        f"exact duplicate function groups: {result['exact_duplicate_function_groups']}",
        f"exact redundant bytes lower bound: {result['exact_redundant_function_bytes_lower_bound']}",
        f"contract checks: {result['checks_passed']}/{result['checks_total']}",
        "```",
        "",
        "Historical scripts are retained as evidence. The contract applies to current tooling only.",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (root / f"evidence/{revision}-runtime-helper-audit.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({key: value for key, value in result.items() if key != "helper_rows"}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
