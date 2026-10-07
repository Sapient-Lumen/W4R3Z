#!/usr/bin/env python3
"""Build a digest inventory for publishing/*.py tooling.

The archive treats validators, builders, and publication helpers as trusted
surfaces.  This inventory makes the script set visible by path, role, byte size,
SHA-256, CLI affordances, rebuild participation, and side-effect class so tool
changes cannot hide behind otherwise passing report JSON.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_role(name: str) -> str:
    if name == "create_published_entry.py":
        return "guarded_publication_executor"
    if name == "release_preflight.py":
        return "release_preflight"
    if name == "rebuild_archive_surfaces.py":
        return "surface_rebuilder"
    if name == "build_archive_zip.py":
        return "deterministic_packager"
    if name.startswith("check_") or name.startswith("verify_"):
        return "checker"
    if name.startswith("build_"):
        return "builder"
    if name.startswith("render_"):
        return "renderer"
    if name.startswith("update_") or name.startswith("refresh_"):
        return "updater"
    return "helper"


def side_effect_class(name: str, text: str) -> str:
    if name == "create_published_entry.py":
        return "publication_boundary_mutator_requires_explicit_authorization"
    if name == "build_archive_zip.py":
        return "writes_external_zip_sha256_receipt_and_package_attestation"
    if name == "rebuild_archive_surfaces.py":
        return "mutates_generated_surfaces"
    if "--write-report" in text or "--write-json" in text or "--write-md" in text or "--write" in text or ".write_text" in text:
        return "may_write_named_output_when_requested_or_building"
    return "read_only_default"


def local_imports(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.name.startswith(("argparse", "hashlib", "json", "pathlib", "sys", "os", "re", "subprocess", "typing", "datetime", "collections", "shutil", "tempfile", "zipfile", "stat", "textwrap")):
                    out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level == 0 and not node.module.startswith(("typing", "collections", "datetime", "jsonschema")):
                out.add(node.module)
    return sorted(out)


def declared_cli_args(text: str) -> list[str]:
    # This intentionally detects literal long options.  It is a static inventory,
    # not a parser emulator.
    args = re.findall(r"['\"](--[A-Za-z0-9_-]+)['\"]", text)
    return sorted(set(args))


def script_entry(root: pathlib.Path, path: pathlib.Path, rebuild_text: str, make_text: str) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    args = declared_cli_args(text)
    name = path.name
    return {
        "path": rel,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "role": classify_role(name),
        "side_effect_class": side_effect_class(name, text),
        "has_python_shebang": text.startswith("#!/usr/bin/env python3") or text.startswith("#!/usr/bin/python3"),
        "has_main_guard": "if __name__" in text and "__main__" in text,
        "imports_argparse": "import argparse" in text,
        "supports_root_arg": "--root" in args,
        "supports_write_report_arg": "--write-report" in args,
        "declared_cli_args": args,
        "local_imports": local_imports(text),
        "appears_in_rebuild_script": rel in rebuild_text,
        "appears_in_makefile": rel in make_text,
    }


def build(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    scripts = sorted((root / "publishing").glob("*.py"), key=lambda p: p.name)
    rebuild_text = (root / "publishing" / "rebuild_archive_surfaces.py").read_text(encoding="utf-8", errors="replace")
    make_text = (root / "Makefile").read_text(encoding="utf-8", errors="replace") if (root / "Makefile").exists() else ""
    entries = [script_entry(root, path, rebuild_text, make_text) for path in scripts]

    role_counts: dict[str, int] = {}
    side_effect_counts: dict[str, int] = {}
    for entry in entries:
        role_counts[entry["role"]] = role_counts.get(entry["role"], 0) + 1
        side_effect_counts[entry["side_effect_class"]] = side_effect_counts.get(entry["side_effect_class"], 0) + 1

    return {
        "version": 1,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "inventory_scope": "publishing/*.py",
        "script_count": len(entries),
        "scripts": entries,
        "summary": {
            "script_count": len(entries),
            "role_counts": dict(sorted(role_counts.items())),
            "side_effect_class_counts": dict(sorted(side_effect_counts.items())),
            "scripts_in_rebuild_count": sum(1 for e in entries if e["appears_in_rebuild_script"]),
            "scripts_in_makefile_count": sum(1 for e in entries if e["appears_in_makefile"]),
            "checker_count": role_counts.get("checker", 0),
            "publication_executor_count": role_counts.get("guarded_publication_executor", 0),
        },
        "fail_closed_rule": "If tooling inventory hashes drift, regenerate surfaces before relying on stored reports or executing publication helpers.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", default="publishing/TOOLING_INVENTORY.json")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    inventory = build(root)
    out = root / args.write
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "written": args.write, "script_count": inventory["script_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
