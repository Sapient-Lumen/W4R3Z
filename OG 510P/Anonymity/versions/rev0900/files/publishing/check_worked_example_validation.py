#!/usr/bin/env python3
"""Run the worked-example validator in an isolated copy.

The worked-example support validator is intentionally allowed to rewrite its own
validation report.  This wrapper makes it safe for the main surface verifier by
copying the archive to a temporary directory, running the validator there, and
checking the resulting report without mutating the live tree.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

WORKED_DIR = pathlib.Path("series/synthesis/paper17_worked_example_receipt_interlock")
VALIDATOR = WORKED_DIR / "tools/validate_example.py"
REPORT = WORKED_DIR / "artifacts/example_validation_report.json"

SKIP_DIR_NAMES = {".git", "__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ignore_transients(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in SKIP_DIR_NAMES or pathlib.Path(name).suffix in SKIP_SUFFIXES:
            ignored.add(name)
    return ignored


def run_validator_on_copy(root: pathlib.Path, timeout_seconds: int) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="anonymity_worked_example_validation.") as tmpdir:
        tmp_root = pathlib.Path(tmpdir) / "root"
        shutil.copytree(root, tmp_root, ignore=ignore_transients)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cmd = [sys.executable, "-B", str(VALIDATOR.relative_to(WORKED_DIR))]
        proc = subprocess.run(
            cmd,
            cwd=tmp_root / WORKED_DIR,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        report_path = tmp_root / REPORT
        report: dict[str, Any] = {}
        report_load_error = ""
        if report_path.exists():
            try:
                loaded = load_json(report_path)
                if isinstance(loaded, dict):
                    report = loaded
                else:
                    report_load_error = "validation report is not a JSON object"
            except Exception as exc:  # noqa: BLE001
                report_load_error = str(exc)
        else:
            report_load_error = "validation report was not written in the isolated copy"

        failed_checks = []
        checks = report.get("checks", []) if isinstance(report, dict) else []
        if isinstance(checks, list):
            failed_checks = [row for row in checks if isinstance(row, dict) and not row.get("ok")]

        failures: list[dict[str, Any]] = []
        if proc.returncode != 0:
            failures.append({"category": "validator_exit_nonzero", "returncode": proc.returncode})
        if report_load_error:
            failures.append({"category": "validation_report_unreadable", "error": report_load_error})
        if report and report.get("ok") is not True:
            failures.append({"category": "validation_report_not_ok"})
        if failed_checks:
            failures.append({"category": "worked_example_validation_check_failed", "failed_check_count": len(failed_checks), "failed_checks": failed_checks[:20]})

        return {
            "status": "pass" if not failures else "fail",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "report_kind": "worked_example_validation_sandbox",
            "validator": VALIDATOR.as_posix(),
            "sandbox_policy": "copy the archive byte-for-byte except transient caches, add no compatibility aliases, and run the validator there so its report rewrite cannot mutate the live tree",
            "returncode": proc.returncode,
            "seconds": round(time.monotonic() - started, 3),
            "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
            "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
            "summary": {
                "checks_failed": len(failures),
                "validator_report_ok": report.get("ok") if report else False,
                "validator_check_count": len(checks) if isinstance(checks, list) else 0,
                "validator_failed_check_count": len(failed_checks),
            },
            "failures": failures,
            "fail_closed_rule": "If the worked-example validator fails in the isolated copy, treat the public/on-request packet, support-bundle map, and route-spine examples as stale even if the broader archive surface checks still pass.",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = run_validator_on_copy(root, max(1, args.timeout_seconds))
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
