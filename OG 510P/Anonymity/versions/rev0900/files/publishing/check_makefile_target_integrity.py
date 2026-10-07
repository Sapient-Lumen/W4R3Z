#!/usr/bin/env python3
"""Check that canonical Makefile targets remain bytecode-safe and non-bypassing."""

from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import sys
from typing import Any

REQUIRED_PHONY = {
    "rebuild-surfaces",
    "rebuild-revision-bindings",
    "rebuild-manifest",
    "rebuild-first-pass",
    "rebuild-tail",
    "queue-compile-smoke",
    "hold-compile-triage-verify",
    "unqueued-compile-triage",
    "unqueued-compile-triage-verify",
    "published-compile-triage",
    "published-compile-triage-verify",
    "auxiliary-tex-compile-triage",
    "auxiliary-tex-compile-triage-verify",
    "tooling-static-smoke",
    "live-compile-lock-self-test",
    "python-entrypoint-smoke",
    "verify-surfaces",
    "verify-surfaces-expanded",
    "package",
}
DANGEROUS_COMMAND_FRAGMENTS = ["rm -rf", "curl ", "wget ", "scp ", "rsync ", "sudo ", "python "]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_targets(text: str) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line and not line.startswith("\t") and ":" in line and not line.startswith(".PHONY") and not line.startswith("export ") and not line.startswith("OUT_DIR"):
            target = line.split(":", 1)[0].strip()
            current = target
            targets.setdefault(target, [])
            continue
        if line.startswith("\t") and current:
            targets[current].append(line.strip())
        elif line.strip() and not line.startswith("\t"):
            current = ""
    return targets


def script_argparse_flags(root: pathlib.Path, rel_script: str) -> set[str]:
    script = root / rel_script
    if not script.exists():
        return set()
    try:
        tree = __import__("ast").parse(script.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    import ast
    flags: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("--"):
                flags.add(arg.value)
    return flags


def makefile_python_argument_mismatches(root: pathlib.Path, commands: list[tuple[str, str]]) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    flag_cache: dict[str, set[str]] = {}
    for target, command in commands:
        if "python3" not in command or ".py" not in command:
            continue
        try:
            parts = shlex.split(command)
        except ValueError as exc:
            mismatches.append({"category": "makefile_command_parse_error", "target": target, "command": command, "error": str(exc)})
            continue
        script = next((part for part in parts if part.endswith(".py") and part.startswith("publishing/")), "")
        if not script:
            continue
        supported = flag_cache.setdefault(script, script_argparse_flags(root, script))
        used_flags = [part.split("=", 1)[0] for part in parts if part.startswith("--")]
        for flag in used_flags:
            if flag not in supported:
                mismatches.append({"category": "makefile_python_flag_not_supported", "target": target, "script": script, "flag": flag, "command": command})
    return mismatches


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    makefile_path = root / "Makefile"
    text = makefile_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    targets = parse_targets(text)
    failures: list[dict[str, Any]] = []

    phony: set[str] = set()
    for line in lines:
        if line.startswith(".PHONY:"):
            phony.update(part.strip() for part in line.split(":", 1)[1].split() if part.strip())

    if "export PYTHONDONTWRITEBYTECODE=1" not in lines:
        failures.append({"category": "missing_bytecode_suppression_export", "path": "Makefile"})
    if "OUT_DIR ?= .." not in lines:
        failures.append({"category": "missing_default_out_dir", "path": "Makefile"})

    missing_phony = sorted(REQUIRED_PHONY - phony)
    missing_targets = sorted(REQUIRED_PHONY - set(targets))
    for name in missing_phony:
        failures.append({"category": "missing_phony_target", "target": name})
    for name in missing_targets:
        failures.append({"category": "missing_target_body", "target": name})

    all_commands = [(target, command) for target, commands in targets.items() for command in commands]
    python_arg_mismatches = makefile_python_argument_mismatches(root, all_commands)
    failures.extend(python_arg_mismatches)
    for target, command in all_commands:
        if "python3" in command and " -B " not in f" {command} ":
            failures.append({"category": "python_command_not_bytecode_safe", "target": target, "command": command})
        for fragment in DANGEROUS_COMMAND_FRAGMENTS:
            if fragment in command:
                failures.append({"category": "dangerous_command_fragment", "target": target, "fragment": fragment.strip(), "command": command})

    verify_commands = targets.get("verify-surfaces", [])
    expanded_commands = targets.get("verify-surfaces-expanded", [])
    if verify_commands != ["python3 -S -B publishing/run_verify_surfaces.py --root ."]:
        failures.append({"category": "verify_surface_driver_not_canonical", "target": "verify-surfaces", "commands": verify_commands})
    if any("--write-report" in command for command in verify_commands):
        failures.append({"category": "verify_surface_mutates_report", "target": "verify-surfaces"})
    if any("rebuild_archive_surfaces.py" in command or "build_archive_zip.py" in command for command in verify_commands):
        failures.append({"category": "verify_surface_invokes_mutating_builder", "target": "verify-surfaces"})

    expected_commands = {
        "rebuild-surfaces": "python3 -B publishing/rebuild_archive_surfaces.py --root .",
        "rebuild-revision-bindings": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase revision-bindings",
        "rebuild-manifest": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase manifest",
        "rebuild-first-pass": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase first-pass",
        "rebuild-tail": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase tail",
        "queue-compile-smoke": "bash publishing/run_queue_compile_smoke.sh --root . --write-report reports/queue_compile_smoke.json --timeout-seconds 20 --passes 3 --jobs 1",
        "hold-compile-triage-verify": "python3 -B publishing/check_queue_compile_smoke.py --root . --report-path release_queue/HOLD_COMPILE_TRIAGE.json --states hold --require-digest-receipts --require-reproducible-receipts",
        "unqueued-compile-triage": "python3 -B publishing/check_unqueued_compile_triage.py --root . --run-live --write-report release_queue/UNQUEUED_COMPILE_TRIAGE.json --write-md release_queue/UNQUEUED_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3",
        "unqueued-compile-triage-verify": "python3 -B publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json",
        "published-compile-triage": "python3 -B publishing/check_published_compile_triage.py --root . --run-live --write-report published/PUBLISHED_COMPILE_TRIAGE.json --write-md published/PUBLISHED_COMPILE_TRIAGE.md --timeout-seconds 60 --passes 3",
        "published-compile-triage-verify": "python3 -B publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json",
        "auxiliary-tex-compile-triage": "python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --run-live --write-report index/AUXILIARY_TEX_COMPILE_TRIAGE.json --write-md index/AUXILIARY_TEX_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3",
        "auxiliary-tex-compile-triage-verify": "python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json",
        "tooling-static-smoke": "python3 -B publishing/check_tooling_static_integrity.py --root .",
        "live-compile-lock-self-test": "python3 -B publishing/live_compile_lock.py --root . --self-test",
        "python-entrypoint-smoke": "python3 -B publishing/check_python_entrypoint_smoke.py --root . --write-report reports/python_entrypoint_smoke.json",
        "verify-surfaces": "python3 -S -B publishing/run_verify_surfaces.py --root .",
        "package": "python3 -B publishing/build_archive_zip.py --root . --out-dir $(OUT_DIR)",
    }
    for target, command in expected_commands.items():
        if command not in targets.get(target, []):
            failures.append({"category": f"{target.replace('-', '_')}_target_not_canonical", "target": target, "expected_command": command, "commands": targets.get(target, [])})

    verify_required = [
        "python3 -B publishing/check_toolchain_fingerprint.py --root .",
        "python3 -B publishing/live_compile_lock.py --root . --self-test",
        "python3 -B publishing/check_archive_coherence.py --root .",
        "python3 -B publishing/check_archive_invariants.py --root .",
        "python3 -B publishing/check_surface_schemas.py --root .",
        "python3 -B publishing/check_transient_surface.py --root .",
        "python3 -B publishing/check_tooling_static_integrity.py --root .",
        "python3 -B publishing/check_python_entrypoint_smoke.py --root .",
        "python3 -B publishing/check_support_manifest_integrity.py --root .",
        "python3 -B publishing/check_queue_compile_smoke.py --root . --report-path reports/queue_compile_smoke.json --require-digest-receipts --require-reproducible-receipts",
        "python3 -B publishing/check_queue_compile_smoke.py --root . --report-path release_queue/HOLD_COMPILE_TRIAGE.json --states hold --require-digest-receipts --require-reproducible-receipts",
        "python3 -B publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json",
        "python3 -B publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json",
        "python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json",
    ]
    for command in verify_required:
        if command not in expanded_commands:
            failures.append({"category": "verify_surface_missing_required_command", "target": "verify-surfaces", "expected_command": command})

    driver_text = (root / "publishing" / "run_verify_surfaces.py").read_text(encoding="utf-8") if (root / "publishing" / "run_verify_surfaces.py").exists() else ""
    if not all(token in driver_text for token in ["VERIFY_COMMANDS", "start_new_session", "os.killpg", "publishing/check_toolchain_fingerprint.py", "publishing/live_compile_lock.py", "publishing/check_unqueued_compile_triage.py", "publishing/check_published_compile_triage.py", "publishing/check_auxiliary_tex_compile_triage.py", "release_queue/HOLD_COMPILE_TRIAGE.json", "--require-digest-receipts", "--require-reproducible-receipts", "published/PUBLISHED_COMPILE_TRIAGE.json", "index/AUXILIARY_TEX_COMPILE_TRIAGE.json"]):
        failures.append({"category": "verify_driver_missing_cloudtainer_safety", "path": "publishing/run_verify_surfaces.py"})

    package_line = next((line for line in lines if line.startswith("package:")), "")
    if "verify-surfaces" not in package_line:
        failures.append({"category": "package_target_not_verify_gated", "target": "package", "line": package_line})

    summary = {
        "checks_failed": len(failures),
        "phony_target_count": len(phony),
        "parsed_target_count": len(targets),
        "command_count": len(all_commands),
        "required_phony_count": len(REQUIRED_PHONY),
        "missing_phony_count": len(missing_phony),
        "missing_target_count": len(missing_targets),
        "dangerous_command_count": sum(1 for item in failures if item["category"] == "dangerous_command_fragment"),
        "unsafe_python_command_count": sum(1 for item in failures if item["category"] == "python_command_not_bytecode_safe"),
        "makefile_python_arg_mismatch_count": len(python_arg_mismatches),
        "verify_required_command_count": len(verify_required),
        "verify_surface_driver_gated": verify_commands == ["python3 -S -B publishing/run_verify_surfaces.py --root ."],
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_root": ".",
        "makefile": "Makefile",
        "required_phony_targets": sorted(REQUIRED_PHONY),
        "parsed_targets": {name: targets[name] for name in sorted(targets)},
        "failures": failures[:100],
        "summary": summary,
        "fail_closed_rule": "If the Makefile command surface drifts from bytecode-safe verification, arg-incompatible Python command lines, bounded verify driver, live compile lock self-test, Python smoke, queue/Hold/unqueued/published/auxiliary compile evidence, or deterministic packaging, default to no publication and repair the target before relying on make-based operations.",
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
