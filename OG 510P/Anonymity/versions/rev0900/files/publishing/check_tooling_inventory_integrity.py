#!/usr/bin/env python3
"""Validate publishing/TOOLING_INVENTORY.json against current script bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    inventory_path = root / "publishing" / "TOOLING_INVENTORY.json"
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    inventory: dict[str, Any] = {}

    if not inventory_path.exists():
        failures.append({"category": "inventory_missing", "path": "publishing/TOOLING_INVENTORY.json"})
    else:
        inventory = load_json(inventory_path)
        if inventory.get("generated_for_revision") != release["revision"]:
            failures.append({"category": "revision_mismatch", "inventory_revision": inventory.get("generated_for_revision"), "expected": release["revision"]})
        if inventory.get("checked_bundle") != release["bundle"]:
            failures.append({"category": "bundle_mismatch", "inventory_bundle": inventory.get("checked_bundle"), "expected": release["bundle"]})

    actual_paths = sorted(p.relative_to(root).as_posix() for p in (root / "publishing").glob("*.py"))
    entries = inventory.get("scripts", []) if isinstance(inventory.get("scripts", []), list) else []
    indexed = {str(entry.get("path")): entry for entry in entries if isinstance(entry, dict) and entry.get("path")}
    missing_from_inventory = sorted(set(actual_paths) - set(indexed))
    stale_inventory_entries = sorted(set(indexed) - set(actual_paths))
    if missing_from_inventory:
        failures.append({"category": "missing_from_inventory", "paths": missing_from_inventory[:50], "count": len(missing_from_inventory)})
    if stale_inventory_entries:
        failures.append({"category": "stale_inventory_entries", "paths": stale_inventory_entries[:50], "count": len(stale_inventory_entries)})

    sha_mismatches: list[dict[str, Any]] = []
    size_mismatches: list[dict[str, Any]] = []
    missing_shebangs: list[str] = []
    missing_main_guards: list[str] = []
    checkers_without_write_report: list[str] = []
    scripts_without_root_arg: list[str] = []
    for rel in actual_paths:
        entry = indexed.get(rel)
        path = root / rel
        if not entry:
            continue
        actual_sha = sha256_file(path)
        actual_size = path.stat().st_size
        if entry.get("sha256") != actual_sha:
            sha_mismatches.append({"path": rel, "expected": entry.get("sha256"), "actual": actual_sha})
        if entry.get("size_bytes") != actual_size:
            size_mismatches.append({"path": rel, "expected": entry.get("size_bytes"), "actual": actual_size})
        text = path.read_text(encoding="utf-8", errors="replace")
        if not (text.startswith("#!/usr/bin/env python3") or text.startswith("#!/usr/bin/python3")):
            missing_shebangs.append(rel)
        if not ("if __name__" in text and "__main__" in text):
            missing_main_guards.append(rel)
        role = str(entry.get("role", ""))
        if role == "checker" and not entry.get("supports_write_report_arg"):
            checkers_without_write_report.append(rel)
        if role not in {"helper"} and not entry.get("supports_root_arg"):
            scripts_without_root_arg.append(rel)

    if sha_mismatches:
        failures.append({"category": "sha256_mismatch", "mismatches": sha_mismatches[:50], "count": len(sha_mismatches)})
    if size_mismatches:
        failures.append({"category": "size_mismatch", "mismatches": size_mismatches[:50], "count": len(size_mismatches)})
    if missing_shebangs:
        failures.append({"category": "missing_python_shebang", "paths": missing_shebangs[:50], "count": len(missing_shebangs)})
    if missing_main_guards:
        failures.append({"category": "missing_main_guard", "paths": missing_main_guards[:50], "count": len(missing_main_guards)})
    if checkers_without_write_report:
        failures.append({"category": "checker_without_write_report", "paths": checkers_without_write_report[:50], "count": len(checkers_without_write_report)})
    if scripts_without_root_arg:
        warnings.append({"category": "script_without_root_arg", "paths": scripts_without_root_arg[:50], "count": len(scripts_without_root_arg)})

    role_counts: dict[str, int] = {}
    side_effect_counts: dict[str, int] = {}
    for entry in entries:
        if isinstance(entry, dict):
            role = str(entry.get("role", ""))
            side = str(entry.get("side_effect_class", ""))
            role_counts[role] = role_counts.get(role, 0) + 1
            side_effect_counts[side] = side_effect_counts.get(side, 0) + 1

    summary = {
        "checks_failed": len(failures),
        "warning_count": len(warnings),
        "actual_script_count": len(actual_paths),
        "inventory_script_count": len(entries),
        "missing_from_inventory_count": len(missing_from_inventory),
        "stale_inventory_entry_count": len(stale_inventory_entries),
        "sha256_mismatch_count": len(sha_mismatches),
        "size_mismatch_count": len(size_mismatches),
        "missing_shebang_count": len(missing_shebangs),
        "missing_main_guard_count": len(missing_main_guards),
        "checker_without_write_report_count": len(checkers_without_write_report),
        "script_without_root_arg_warning_count": len(scripts_without_root_arg),
        "role_counts": dict(sorted(role_counts.items())),
        "side_effect_class_counts": dict(sorted(side_effect_counts.items())),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "inventory_path": "publishing/TOOLING_INVENTORY.json",
        "publication_authorized": False,
        "failures": failures[:50],
        "warnings": warnings[:50],
        "summary": summary,
        "fail_closed_rule": "If the tooling inventory does not match current publishing/*.py bytes, do not rely on stored reports until inventory and reports are regenerated.",
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
