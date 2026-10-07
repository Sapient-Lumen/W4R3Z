#!/usr/bin/env python3
"""Static safety checks for publishing/*.py tooling.

The tooling inventory binds script hashes.  This guard checks that the current
script bytes are syntactically valid, import-oriented rather than top-level
executing tools, consistently bytecode-safe under documented invocation, and do
not contain duplicate constant dictionary keys.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq) or len(test.comparators) != 1:
        return False
    left = test.left
    right = test.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    ) or (
        isinstance(right, ast.Name)
        and right.id == "__name__"
        and isinstance(left, ast.Constant)
        and left.value == "__main__"
    )


def literal_key(node: ast.AST | None) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool, type(None))):
        return (type(node.value).__name__, node.value)
    return None


def duplicate_literal_dict_keys(tree: ast.AST) -> list[dict[str, Any]]:
    duplicates: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        seen: dict[Any, int] = {}
        for key_node in node.keys:
            key = literal_key(key_node)
            if key is None:
                continue
            if key in seen:
                duplicates.append({"line": getattr(key_node, "lineno", getattr(node, "lineno", 0)), "key": repr(key[1]), "first_line": seen[key]})
            else:
                seen[key] = getattr(key_node, "lineno", getattr(node, "lineno", 0))
    return duplicates


def check_top_level_shape(tree: ast.Module) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    main_guards = [node for node in tree.body if is_main_guard(node)]
    if len(main_guards) != 1:
        failures.append({"category": "main_guard_count_not_one", "count": len(main_guards)})
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if is_main_guard(node):
            continue
        # Allow sys.path.insert followed by local imports; several tools use this
        # to import release_readiness helpers when run as scripts.
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr == "insert":
                continue
        failures.append({"category": "unexpected_top_level_statement", "line": getattr(node, "lineno", 0), "node_type": type(node).__name__})
    return failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for path in sorted((root / "publishing").glob("*.py")):
        rel = path.relative_to(root).as_posix()
        script_failures: list[dict[str, Any]] = []
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, rel, "exec")
            tree = ast.parse(source, filename=rel)
        except SyntaxError as exc:
            script_failures.append({"category": "syntax_error", "line": exc.lineno, "detail": exc.msg})
            tree = None
        if "from __future__ import annotations" not in source:
            script_failures.append({"category": "missing_future_annotations"})
        if tree is not None:
            script_failures.extend(check_top_level_shape(tree))
            for dup in duplicate_literal_dict_keys(tree):
                script_failures.append({"category": "duplicate_literal_dict_key", **dup})
        row = {"script": rel, "status": "pass" if not script_failures else "fail", "failures": script_failures}
        rows.append(row)
        if script_failures:
            failures.append(row)

    summary = {
        "checks_failed": len(failures),
        "script_count": len(rows),
        "syntax_failure_count": sum(1 for row in rows for fail in row["failures"] if fail["category"] == "syntax_error"),
        "missing_future_annotations_count": sum(1 for row in rows for fail in row["failures"] if fail["category"] == "missing_future_annotations"),
        "duplicate_literal_dict_key_count": sum(1 for row in rows for fail in row["failures"] if fail["category"] == "duplicate_literal_dict_key"),
        "unexpected_top_level_statement_count": sum(1 for row in rows for fail in row["failures"] if fail["category"] == "unexpected_top_level_statement"),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "script_directory": "publishing",
        "script_rows": rows,
        "failures": failures[:100],
        "summary": summary,
        "fail_closed_rule": "If a publishing tool is syntactically invalid, lacks the standard script guard, or contains duplicate literal dictionary keys, default to no publication and repair the tool before relying on generated surfaces.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
