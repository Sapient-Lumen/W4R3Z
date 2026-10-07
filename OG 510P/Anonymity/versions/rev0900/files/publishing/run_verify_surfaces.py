#!/usr/bin/env python3
"""Run the non-mutating and sandboxed-mutation surface-verification stack as one bounded command.

The expanded Makefile target remains available for transparency, but this driver
is the default cloudtainer path: each check gets its own process group, bytecode
suppression, timeout cleanup, and a compact JSON receipt.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any

# Most verification helpers are stdlib-only and should run with site startup
# disabled.  That avoids slow/noisy container-level site hooks and makes the
# bounded driver less likely to strand unrelated startup children.
#
# `check_surface_schemas.py` and `check_python_entrypoint_smoke.py` intentionally
# remain on normal Python startup: the former imports jsonschema, and the latter
# probes path-scoped external dependency availability.
PY_STD = ("python3", "-S", "-B")
PY_SITE = ("python3", "-B")

VERIFY_COMMANDS: list[tuple[str, ...]] = [
    (*PY_STD, "publishing/check_toolchain_fingerprint.py", "--root", "."),
    (*PY_STD, "publishing/live_compile_lock.py", "--root", ".", "--self-test"),
    (*PY_STD, "publishing/check_archive_coherence.py", "--root", "."),
    (*PY_STD, "publishing/check_archive_invariants.py", "--root", "."),
    (*PY_SITE, "publishing/check_surface_schemas.py", "--root", "."),
    (*PY_STD, "publishing/check_transient_surface.py", "--root", "."),
    (*PY_STD, "publishing/check_tooling_static_integrity.py", "--root", "."),
    (*PY_SITE, "publishing/check_python_entrypoint_smoke.py", "--root", "."),
    (*PY_STD, "publishing/check_support_manifest_integrity.py", "--root", "."),
    (*PY_STD, "publishing/check_worked_example_payload_pointers.py", "--root", "."),
    (*PY_STD, "publishing/check_worked_example_validation.py", "--root", "."),
    (*PY_STD, "publishing/check_hostile_review_vectors.py", "--root", "."),
    (*PY_STD, "publishing/check_threat_transfer_matrix.py", "--root", "."),
    (*PY_STD, "publishing/check_external_hostile_review_packet.py", "--root", "."),
    (*PY_STD, "publishing/check_queue_compile_smoke.py", "--root", ".", "--report-path", "reports/queue_compile_smoke.json", "--require-digest-receipts", "--require-reproducible-receipts"),
    (*PY_STD, "publishing/check_queue_compile_smoke.py", "--root", ".", "--report-path", "release_queue/HOLD_COMPILE_TRIAGE.json", "--states", "hold", "--require-digest-receipts", "--require-reproducible-receipts"),
    (*PY_STD, "publishing/check_unqueued_compile_triage.py", "--root", ".", "--report-path", "release_queue/UNQUEUED_COMPILE_TRIAGE.json"),
    (*PY_STD, "publishing/check_published_compile_triage.py", "--root", ".", "--report-path", "published/PUBLISHED_COMPILE_TRIAGE.json"),
    (*PY_STD, "publishing/check_auxiliary_tex_compile_triage.py", "--root", ".", "--report-path", "index/AUXILIARY_TEX_COMPILE_TRIAGE.json"),
]


def load_release(root: pathlib.Path) -> dict[str, Any]:
    return json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))


def run_one(root: pathlib.Path, command: tuple[str, ...], timeout_seconds: int, heartbeat_seconds: int) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    deadline = started + max(1, timeout_seconds)
    last_heartbeat = started
    with tempfile.TemporaryDirectory(prefix="anonymity_verify_surface.") as tmpdir:
        log_path = pathlib.Path(tmpdir) / "combined.log"
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            try:
                proc = subprocess.Popen(
                    list(command), cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                    text=True, start_new_session=True,
                )
            except FileNotFoundError as exc:
                return {"command": list(command), "status": "fail", "returncode": 127, "seconds": 0.0, "failure_category": "command_not_found", "log_tail": str(exc)}
            while True:
                rc = proc.poll()
                now = time.monotonic()
                if rc is not None:
                    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
                    return {"command": list(command), "status": "pass" if rc == 0 else "fail", "returncode": rc, "seconds": round(now - started, 3), "failure_category": "" if rc == 0 else "command_failed", "log_tail": "\n".join(log_text.splitlines()[-40:])}
                if now >= deadline:
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                    except Exception:
                        proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except Exception:
                            proc.kill()
                        proc.wait(timeout=5)
                    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
                    return {"command": list(command), "status": "fail", "returncode": 124, "seconds": round(time.monotonic() - started, 3), "failure_category": "command_timeout", "log_tail": "\n".join(log_text.splitlines()[-40:])}
                if heartbeat_seconds > 0 and now - last_heartbeat >= heartbeat_seconds:
                    print(f"verify-surfaces heartbeat: {' '.join(command)} running {int(now - started)}s", file=sys.stderr, flush=True)
                    last_heartbeat = now
                time.sleep(0.2)


def check(root: pathlib.Path, timeout_seconds: int, heartbeat_seconds: int) -> dict[str, Any]:
    release = load_release(root)
    rows: list[dict[str, Any]] = []
    for command in VERIFY_COMMANDS:
        row = run_one(root, command, timeout_seconds, heartbeat_seconds)
        rows.append(row)
        if row["status"] != "pass":
            break
    failures = [row for row in rows if row["status"] != "pass"]
    return {
        "status": "pass" if not failures and len(rows) == len(VERIFY_COMMANDS) else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "non_mutating_surface_verification_driver",
        "python_startup_policy": {"stdlib_only_commands": "python3 -S -B", "site_package_exception": "check_surface_schemas.py uses jsonschema; check_python_entrypoint_smoke.py probes allowed external dependency availability"},
        "command_count_expected": len(VERIFY_COMMANDS),
        "command_count_run": len(rows),
        "commands": rows,
        "summary": {"checks_failed": len(failures), "commands_passed": sum(1 for row in rows if row["status"] == "pass"), "commands_failed": len(failures), "timeout_seconds_per_command": timeout_seconds, "heartbeat_seconds": heartbeat_seconds},
        "failures": failures[:5],
        "fail_closed_rule": "If any existing non-mutating or sandboxed-mutation verification command fails or times out, default to no publication and inspect the command log tail before trusting the surface stack.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--heartbeat-seconds", type=int, default=15)
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root, args.timeout_seconds, args.heartbeat_seconds)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
