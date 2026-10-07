#!/usr/bin/env python3
"""Compile-smoke shipped Python, guarded entrypoints, and import policy.

The entrypoint smoke used to prove only that files byte-compiled and publishing
helpers had guarded main() calls.  That misses a different supply-chain/build-rot
risk: a helper can silently gain an undeclared external dependency and still pass
py_compile on a developer machine.  This checker now records a compact import
profile, permits external modules only for path-scoped helpers, probes their
availability in the live toolchain, and carries synthetic negative controls so a
clean report is not confused with an untested detector.
"""

from __future__ import annotations

import argparse
import ast
import importlib.metadata
import importlib.util
import json
import pathlib
import py_compile
import re
import sys
import tempfile
from typing import Any, Iterable

CLI_SCRIPT_PREFIXES = ("publishing/",)
EXCLUDED_PATH_PARTS = {"__pycache__", ".git"}

# External imports are deliberately path-scoped.  Most archive automation should
# stay stdlib/local; schema validation is the one current routine path that
# requires jsonschema.  Optional support tools may use PyYAML if present, but only
# in the worked-example support-tree path.
ALLOWED_EXTERNAL_IMPORTS: dict[str, tuple[str, ...]] = {
    "jsonschema": (
        "publishing/check_surface_schemas.py",
        "publishing/check_schema_catalog_integrity.py",
        "publishing/check_json_surface_catalog.py",
    ),
    "matplotlib": (
        "published/2026-01-23_spectral_anonymity/supplement/",
    ),
    "numpy": (
        "published/2026-01-23_spectral_anonymity/supplement/",
    ),
    "scipy": (
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/",
    ),
    "yaml": (
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/",
    ),
}

# The import allowlist must be backed by a concrete install surface rather than
# operator memory.  Import names and distribution names differ for PyYAML, so the
# checker keeps the mapping explicit and validates the exact pinned versions in
# requirements.txt against the live Python environment.
REQUIREMENTS_PATH = "requirements.txt"
EXTERNAL_DISTRIBUTIONS: dict[str, str] = {
    "jsonschema": "jsonschema",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "scipy": "scipy",
    "yaml": "PyYAML",
}
REQUIREMENT_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s#]+)$")

IMPORT_NEGATIVE_CONTROLS = [
    {
        "name": "unexpected_external_import",
        "path": "publishing/fake_unexpected_dependency.py",
        "source": "import requests\n",
        "expect_category": "unexpected_external_import",
    },
    {
        "name": "external_import_path_violation",
        "path": "publishing/fake_schema_drift.py",
        "source": "import jsonschema\n",
        "expect_category": "external_import_path_violation",
    },
    {
        "name": "missing_external_dependency",
        "path": "publishing/fake_missing_dependency.py",
        "source": "import definitely_missing_anonymity_dependency_zzzz\n",
        "expect_category": "unexpected_external_import",
    },
    {
        "name": "allowed_external_path",
        "path": "publishing/check_surface_schemas.py",
        "source": "import jsonschema\n",
        "expect_category": None,
    },
    {
        "name": "local_import_allowed",
        "path": "publishing/fake_local_import.py",
        "source": "import render_queue_surfaces\n",
        "expect_category": None,
    },
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements_lock(root: pathlib.Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Parse the exact-version requirements contract.

    The file intentionally accepts only comment/blank lines and ``Name==version``
    rows.  That keeps the contract auditable by the stdlib smoke checker and
    avoids resolver options whose semantics depend on pip version/network state.
    """
    path = root / REQUIREMENTS_PATH
    failures: list[dict[str, Any]] = []
    entries: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return entries, [{"category": "requirements_contract_missing", "path": REQUIREMENTS_PATH}]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = REQUIREMENT_RE.match(stripped)
        if not match:
            failures.append({"category": "requirements_contract_malformed_line", "path": REQUIREMENTS_PATH, "line": lineno, "text": stripped[:120]})
            continue
        distribution, version = match.groups()
        key = normalized_distribution_name(distribution)
        if key in entries:
            failures.append({"category": "requirements_contract_duplicate_distribution", "path": REQUIREMENTS_PATH, "line": lineno, "distribution": distribution})
            continue
        entries[key] = {"distribution": distribution, "version": version, "line": lineno}
    return entries, failures


def rel(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def python_sources(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file() and not any(part in EXCLUDED_PATH_PARTS for part in p.parts))


def module_root(name: str) -> str:
    return name.split(".", 1)[0]


def local_module_roots(root: pathlib.Path) -> set[str]:
    roots: set[str] = set()
    for path in python_sources(root):
        r = rel(path, root)
        if r.endswith("__init__.py"):
            roots.add(r.split("/", 1)[0])
        roots.add(path.stem)
        if "/" in r:
            roots.add(r.split("/", 1)[0])
    return roots


def imported_modules(tree: ast.Module) -> sorted:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    modules.add(module_root(alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module is None:
                continue
            if node.level:
                # Relative imports are local by construction.
                continue
            if node.module:
                modules.add(module_root(node.module))
    return sorted(modules)


def import_categories(modules: Iterable[str], path: str, local_roots: set[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    stdlib = getattr(sys, "stdlib_module_names", set())
    builtin = set(sys.builtin_module_names)
    for name in sorted(set(modules)):
        root = module_root(name)
        if root in local_roots:
            category = "local"
        elif root in stdlib or root in builtin:
            category = "stdlib"
        elif root in ALLOWED_EXTERNAL_IMPORTS:
            allowed_prefixes = ALLOWED_EXTERNAL_IMPORTS[root]
            if any(path == prefix or path.startswith(prefix) for prefix in allowed_prefixes):
                category = "allowed_external"
            else:
                category = "external_path_violation"
                failures.append({"category": "external_import_path_violation", "path": path, "module": root, "allowed_path_prefixes": list(allowed_prefixes)})
        else:
            category = "unexpected_external"
            failures.append({"category": "unexpected_external_import", "path": path, "module": root})
        rows.append({"module": root, "category": category})
    return rows, failures


def external_dependency_status(requirements: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in sorted(ALLOWED_EXTERNAL_IMPORTS):
        distribution = EXTERNAL_DISTRIBUTIONS[name]
        normalized = normalized_distribution_name(distribution)
        locked = requirements.get(normalized, {})
        spec = importlib.util.find_spec(name)
        try:
            installed_version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            installed_version = ""
        lock_status = "match" if locked and installed_version == locked.get("version") else "missing_lock" if not locked else "version_mismatch"
        rows.append({
            "module": name,
            "distribution": distribution,
            "status": "available" if spec is not None else "missing",
            "installed_version": installed_version,
            "locked_version": locked.get("version", ""),
            "lock_status": lock_status,
            "path_prefixes": list(ALLOWED_EXTERNAL_IMPORTS[name]),
        })
    return rows


def is_main_name_test(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare) or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq) or len(node.comparators) != 1:
        return False
    left = node.left
    right = node.comparators[0]

    def is_name(x: ast.AST) -> bool:
        return isinstance(x, ast.Name) and x.id == "__name__"

    def is_main(x: ast.AST) -> bool:
        return isinstance(x, ast.Constant) and x.value == "__main__"

    return (is_name(left) and is_main(right)) or (is_main(left) and is_name(right))


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        return call_name(node.func)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def has_main_function(tree: ast.Module) -> bool:
    return any(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body)


def main_guard_style(tree: ast.Module) -> tuple[bool, str]:
    for node in tree.body:
        if not isinstance(node, ast.If) or not is_main_name_test(node.test):
            continue
        calls = [call_name(child) for child in ast.walk(node)]
        if "main" in calls and "SystemExit" in calls:
            return True, "raise SystemExit(main())"
        if "main" in calls:
            return True, "main() under __main__ guard"
        return False, "__main__ guard present without main() call"
    return False, "missing __main__ guard"


def is_cli_script(rel_path: str) -> bool:
    return rel_path.endswith(".py") and any(rel_path.startswith(prefix) for prefix in CLI_SCRIPT_PREFIXES)


def run_negative_controls(local_roots: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for control in IMPORT_NEGATIVE_CONTROLS:
        tree = ast.parse(control["source"], filename=control["path"])
        modules = imported_modules(tree)
        imports, detected = import_categories(modules, control["path"], local_roots)
        categories = sorted({item["category"] for item in detected})
        expected = control["expect_category"]
        ok = (not detected) if expected is None else expected in categories
        row = {
            "name": control["name"],
            "path": control["path"],
            "expected_category": expected or "none",
            "detected_categories": categories,
            "status": "pass" if ok else "fail",
            "imports": imports,
        }
        if not ok:
            failures.append({"category": "import_negative_control_failed", **row})
        rows.append(row)
    return rows, failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    compile_failed = 0
    entrypoint_failed = 0
    cli_count = 0
    non_cli_count = 0
    import_rows: list[dict[str, Any]] = []
    unexpected_external_count = 0
    external_path_violation_count = 0
    stdlib_modules: set[str] = set()
    local_modules: set[str] = set()
    allowed_external_modules: set[str] = set()
    local_roots = local_module_roots(root)
    sources = python_sources(root)
    requirements, requirement_failures = parse_requirements_lock(root)
    failures.extend(requirement_failures)
    expected_distributions = {normalized_distribution_name(dist) for dist in EXTERNAL_DISTRIBUTIONS.values()}
    locked_distributions = set(requirements)
    missing_locked_distributions = sorted(expected_distributions - locked_distributions)
    extra_locked_distributions = sorted(locked_distributions - expected_distributions)
    if missing_locked_distributions:
        failures.append({"category": "requirements_contract_missing_external_dependencies", "distributions": missing_locked_distributions})
    if extra_locked_distributions:
        failures.append({"category": "requirements_contract_extra_external_dependencies", "distributions": extra_locked_distributions})
    with tempfile.TemporaryDirectory(prefix="anonymity_pycompile_") as tmpdir:
        tmp = pathlib.Path(tmpdir)
        for path in sources:
            r = rel(path, root)
            row: dict[str, Any] = {"path": r, "status": "pass", "compile_status": "pass"}
            cfile = tmp / (r.replace("/", "__") + ".pyc")
            try:
                py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            except Exception as exc:  # noqa: BLE001
                compile_failed += 1
                row.update({"status": "fail", "compile_status": "fail", "error": str(exc)})
                failures.append({"category": "py_compile_failed", "path": r, "error": str(exc)})
                rows.append(row)
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=r)
            imports, import_failures = import_categories(imported_modules(tree), r, local_roots)
            row["imports"] = imports
            for item in imports:
                if item["category"] == "stdlib":
                    stdlib_modules.add(item["module"])
                elif item["category"] == "local":
                    local_modules.add(item["module"])
                elif item["category"] == "allowed_external":
                    allowed_external_modules.add(item["module"])
            if import_failures:
                row["status"] = "fail"
                for failure in import_failures:
                    failures.append(failure)
                    if failure["category"] == "unexpected_external_import":
                        unexpected_external_count += 1
                    elif failure["category"] == "external_import_path_violation":
                        external_path_violation_count += 1
            import_rows.append({"path": r, "imports": imports})
            if is_cli_script(r):
                cli_count += 1
                guard_ok, style = main_guard_style(tree)
                main_ok = has_main_function(tree)
                row.update({"entrypoint_expected": True, "has_main_function": main_ok, "main_guard_style": style, "entrypoint_status": "pass" if guard_ok and main_ok else "fail"})
                if row["entrypoint_status"] != "pass":
                    entrypoint_failed += 1
                    row["status"] = "fail"
                    failures.append({"category": "cli_entrypoint_not_main_guarded", "path": r, "has_main_function": main_ok, "main_guard_style": style})
            else:
                non_cli_count += 1
                row.update({"entrypoint_expected": False, "entrypoint_status": "not_expected"})
            rows.append(row)

    dependency_rows = external_dependency_status(requirements)
    unavailable = [row for row in dependency_rows if row["status"] != "available"]
    version_mismatches = [row for row in dependency_rows if row["lock_status"] != "match"]
    for row in unavailable:
        failures.append({"category": "allowed_external_dependency_unavailable", "module": row["module"], "distribution": row["distribution"], "path_prefixes": row["path_prefixes"]})
    for row in version_mismatches:
        failures.append({"category": "allowed_external_dependency_not_locked_to_live_version", "module": row["module"], "distribution": row["distribution"], "installed_version": row["installed_version"], "locked_version": row["locked_version"], "lock_status": row["lock_status"]})

    negative_rows, negative_failures = run_negative_controls(local_roots)
    failures.extend(negative_failures)

    summary = {
        "checks_failed": len(failures),
        "python_source_count": len(sources),
        "compile_checked": len(sources),
        "compile_failed": compile_failed,
        "entrypoint_checked": cli_count,
        "entrypoint_failed": entrypoint_failed,
        "non_cli_python_source_count": non_cli_count,
        "cli_script_prefixes": list(CLI_SCRIPT_PREFIXES),
        "stdlib_import_module_count": len(stdlib_modules),
        "local_import_module_count": len(local_modules),
        "allowed_external_import_module_count": len(allowed_external_modules),
        "unexpected_external_import_count": unexpected_external_count,
        "external_import_path_violation_count": external_path_violation_count,
        "external_dependency_checked": len(dependency_rows),
        "external_dependency_unavailable_count": len(unavailable),
        "requirements_contract_path": REQUIREMENTS_PATH,
        "requirements_contract_present": (root / REQUIREMENTS_PATH).exists(),
        "requirements_locked_dependency_count": len(requirements),
        "requirements_missing_external_dependency_count": len(missing_locked_distributions),
        "requirements_extra_dependency_count": len(extra_locked_distributions),
        "requirements_parse_failure_count": len(requirement_failures),
        "external_dependency_lock_mismatch_count": len(version_mismatches),
        "import_negative_control_count": len(negative_rows),
        "import_negative_control_failed_count": len(negative_failures),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "python_entrypoint_smoke",
        "scope": {
            "python_source_glob": "**/*.py",
            "compile_method": "py_compile.compile(..., doraise=True) into a temporary directory",
            "entrypoint_policy": "publishing/*.py helpers must define main() and invoke main under a __name__ == '__main__' guard; worked-example tools are compile-smoked here and hash-governed by support_manifest_integrity.",
            "import_policy": "stdlib and local imports are allowed. External imports are allowed only when listed in ALLOWED_EXTERNAL_IMPORTS for the exact helper path or path prefix; availability is probed, exact pinned versions must match requirements.txt, and detector negative controls must pass.",
            "requirements_contract": REQUIREMENTS_PATH,
            "allowed_external_imports": {k: list(v) for k, v in sorted(ALLOWED_EXTERNAL_IMPORTS.items())},
            "external_import_to_distribution": {k: EXTERNAL_DISTRIBUTIONS[k] for k in sorted(EXTERNAL_DISTRIBUTIONS)},
        },
        "summary": summary,
        "requirements_contract": {
            "path": REQUIREMENTS_PATH,
            "expected_distributions": sorted(EXTERNAL_DISTRIBUTIONS.values(), key=normalized_distribution_name),
            "locked_distributions": [requirements[key] for key in sorted(requirements)],
            "missing_distributions": missing_locked_distributions,
            "extra_distributions": extra_locked_distributions,
        },
        "external_dependencies": dependency_rows,
        "import_negative_controls": negative_rows,
        "failures": failures[:100],
        "results": rows,
        "fail_closed_rule": "If any shipped Python source fails py_compile, any publishing command helper lacks a guarded main entrypoint, any unexpected/unavailable/path-divergent external import appears, or requirements.txt does not exactly lock the allowed live external dependency set, do not trust stored automation reports until repaired.",
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
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
