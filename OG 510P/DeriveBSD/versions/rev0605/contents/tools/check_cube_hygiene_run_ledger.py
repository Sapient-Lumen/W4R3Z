#!/usr/bin/env python3
"""Validate the cube hygiene run ledger schema, example, docs, and wrapper wiring."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from typing import Any
import tempfile


from cube_check_lib import fail, require_text_tokens, validation_errors
from cube_digest_lib import load_json
from cube_check_lib import release_token

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-06-18r630"
SCHEMA = "spec/cube.hygiene.run.ledger.schema.json"
EXAMPLE = "spec/examples/cube.hygiene.run.ledger.json"
REQUIRED_TEXT_TOKENS = {
    "CHANGELOG.md": [VERSION, "cube.hygiene.run.ledger", "spec/cube.hygiene.run.ledger.schema.json"],
    "README.md": [VERSION, "cube.hygiene.run.ledger", "tools/hygiene.py --ledger"],
    "docs/00-index.md": [VERSION, "docs/current/hygiene-run-ledger.md"],
    "docs/98-archive-hygiene.md": ["cube.hygiene.run.ledger", "--ledger"],
    "docs/99-llm-runbook.md": ["cube.hygiene.run.ledger", "--ledger"],
    "docs/current/hygiene-run-ledger.md": ["cube.hygiene.run.ledger", "timed-out", "run_complete", "partial ledger", "hygiene_wrapper_sha256", "cube_input_sha256", "runner_environment_sha256", "run_budget_status", "--max-run-seconds", "check_budget_status", "--max-checks", "exit code 2"],
}


def sha256_file(rel: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append(f"generated_for_version must be {VERSION}")
    expected_ledger_id = f"cube-hygiene-run-ledger-{release_token(VERSION)}-release-critical"
    if obj.get("ledger_id") != expected_ledger_id:
        errors.append(f"ledger_id must bind {release_token(VERSION)} and release-critical")
    if obj.get("hygiene_wrapper") != "tools/hygiene.py":
        errors.append("hygiene_wrapper must be tools/hygiene.py")
    expected_wrapper_sha = sha256_file("tools/hygiene.py")
    if obj.get("hygiene_wrapper_sha256") != expected_wrapper_sha:
        errors.append("hygiene_wrapper_sha256 must match current tools/hygiene.py")
    import hygiene
    expected_cube_input_sha = hygiene._cube_input_sha256()
    expected_cube_input_scope = hygiene._cube_input_fingerprint_scope()
    expected_cube_input_file_count = hygiene._cube_input_fingerprint_file_count()
    if obj.get("cube_input_sha256") != expected_cube_input_sha:
        errors.append("cube_input_sha256 must match current source/docs/spec/tools/fixtures fingerprint")
    if obj.get("cube_input_fingerprint_scope") != expected_cube_input_scope:
        errors.append("cube_input_fingerprint_scope must match hygiene scope")
    if obj.get("cube_input_file_count") != expected_cube_input_file_count:
        errors.append("cube_input_file_count must match current fingerprint file count")
    if obj.get("runner_environment_sha256") != hygiene._runner_environment_sha256():
        errors.append("runner_environment_sha256 must match current Python/jsonschema runner environment")
    if obj.get("runner_environment_scope") != hygiene._runner_environment_scope():
        errors.append("runner_environment_scope must match hygiene runner environment scope")
    results = obj.get("results")
    if not isinstance(results, list):
        return errors + ["results must be a list"]
    counts = {
        "passed": sum(1 for row in results if isinstance(row, dict) and row.get("status") == "passed"),
        "failed": sum(1 for row in results if isinstance(row, dict) and row.get("status") == "failed"),
        "timed_out": sum(1 for row in results if isinstance(row, dict) and row.get("status") == "timed-out"),
    }
    if obj.get("counts") != counts:
        errors.append(f"counts {obj.get('counts')!r} do not match result rows {counts!r}")
    if obj.get("checks_completed") != len(results):
        errors.append("checks_completed must equal len(results)")
    checks_total = obj.get("checks_total")
    if not isinstance(checks_total, int) or checks_total < len(results):
        errors.append("checks_total must be the planned total and must be >= len(results)")
    run_complete = checks_total == len(results) if isinstance(checks_total, int) else False
    if obj.get("run_complete") is not run_complete:
        errors.append("run_complete must equal checks_completed == checks_total")
    expected_result = "passed" if run_complete and counts["failed"] == 0 and counts["timed_out"] == 0 else "failed"
    if obj.get("result") != expected_result:
        errors.append(f"result must be {expected_result!r} from completeness and counts")

    run_budget_seconds = obj.get("run_budget_seconds")
    run_budget_status = obj.get("run_budget_status")
    if run_budget_seconds is None:
        if run_budget_status != "not-enforced":
            errors.append("run_budget_status must be not-enforced when run_budget_seconds is null")
    elif not isinstance(run_budget_seconds, (int, float)) or run_budget_seconds <= 0:
        errors.append("run_budget_seconds must be null or a positive number")
    elif run_budget_status not in {"within-budget", "stopped-before-budget", "completed-within-budget"}:
        errors.append("run_budget_status must describe the enforced wrapper run budget")

    check_budget_limit = obj.get("check_budget_limit")
    check_budget_status = obj.get("check_budget_status")
    if check_budget_limit is None:
        if check_budget_status != "not-enforced":
            errors.append("check_budget_status must be not-enforced when check_budget_limit is null")
    elif not isinstance(check_budget_limit, int) or check_budget_limit < 0:
        errors.append("check_budget_limit must be null or a non-negative integer")
    elif check_budget_status not in {"within-check-budget", "stopped-before-check-budget", "completed-within-check-budget"}:
        errors.append("check_budget_status must describe the enforced ledger chunk check budget")
    elif run_complete and check_budget_status != "completed-within-check-budget":
        errors.append("complete check-budgeted ledgers must record completed-within-check-budget")

    for row in results:
        if not isinstance(row, dict):
            continue
        status = row.get("status")
        if row.get("cube_input_sha256") != obj.get("cube_input_sha256"):
            errors.append(f"{row.get('tool')}: row cube_input_sha256 must match ledger root")
        if row.get("cube_input_fingerprint_scope") != obj.get("cube_input_fingerprint_scope"):
            errors.append(f"{row.get('tool')}: row cube_input_fingerprint_scope must match ledger root")
        if row.get("cube_input_file_count") != obj.get("cube_input_file_count"):
            errors.append(f"{row.get('tool')}: row cube_input_file_count must match ledger root")
        if row.get("runner_environment_sha256") != obj.get("runner_environment_sha256"):
            errors.append(f"{row.get('tool')}: row runner_environment_sha256 must match ledger root")
        if row.get("runner_environment_scope") != obj.get("runner_environment_scope"):
            errors.append(f"{row.get('tool')}: row runner_environment_scope must match ledger root")
        rc = row.get("return_code")
        failure_class = row.get("failure_class")
        terminated_by_signal = row.get("terminated_by_signal")
        signal_name = row.get("signal_name")
        if status == "passed" and rc != 0:
            errors.append(f"{row.get('tool')}: passed row must have return_code 0")
        if status == "passed" and failure_class != "none":
            errors.append(f"{row.get('tool')}: passed row must have failure_class none")
        if status == "timed-out" and (rc != 124 or row.get("timed_out") is not True or failure_class != "timed-out"):
            errors.append(f"{row.get('tool')}: timed-out row must use return_code 124, timed_out true, and failure_class timed-out")
        if row.get("process_group_isolated") is not True:
            errors.append(f"{row.get('tool')}: ledger row must prove process_group_isolated true")
        if status == "timed-out":
            if row.get("timeout_kill_scope") not in {"process-group", "child-process", "already-exited"}:
                errors.append(f"{row.get('tool')}: timed-out row must record timeout_kill_scope")
            if row.get("timeout_termination_signal") not in {"SIGTERM", "SIGKILL", "SIGKILL-unreaped", "none"}:
                errors.append(f"{row.get('tool')}: timed-out row must record timeout_termination_signal")
            if not isinstance(row.get("timeout_grace_seconds"), (int, float)) or row.get("timeout_grace_seconds") <= 0:
                errors.append(f"{row.get('tool')}: timed-out row must record positive timeout_grace_seconds")
        elif (
            row.get("timeout_kill_scope") != "not-needed"
            or row.get("timeout_termination_signal") is not None
            or row.get("timeout_grace_seconds") is not None
        ):
            errors.append(f"{row.get('tool')}: completed row must not carry timeout kill evidence")
        if isinstance(rc, int) and rc < 0:
            if terminated_by_signal is not True or failure_class != "terminated-by-signal" or not isinstance(signal_name, str):
                errors.append(f"{row.get('tool')}: negative return_code must be classified as terminated-by-signal with a signal_name")
        elif terminated_by_signal is not False or signal_name is not None:
            errors.append(f"{row.get('tool')}: non-signal return must not carry signal termination")
        if status == "failed" and isinstance(rc, int) and rc > 0 and failure_class != "exit-nonzero":
            errors.append(f"{row.get('tool')}: positive failed return_code must be exit-nonzero")
        if row.get("selected_profile") != obj.get("selected_profile"):
            errors.append(f"{row.get('tool')}: selected_profile must match ledger selected_profile")
        tool = row.get("tool")
        if not isinstance(tool, str) or not tool:
            errors.append("ledger row must carry a non-empty tool name")
        else:
            tool_path = ROOT / "tools" / tool
            if not tool_path.is_file():
                errors.append(f"{tool}: ledger tool does not exist under tools/")
            else:
                expected_tool_sha = "sha256:" + hashlib.sha256(tool_path.read_bytes()).hexdigest()
                if row.get("tool_sha256") != expected_tool_sha:
                    errors.append(f"{tool}: tool_sha256 does not match current checker file")
    return errors


def check_runner_environment_regression() -> list[str]:
    """Keep proof identity stable across launcher aliases and ``-S``."""
    import hygiene

    material = hygiene._runner_environment_material()
    if "python_executable" in material:
        return ["runner material must not bind the literal interpreter launcher path"]
    executable_sha = material.get("python_executable_sha256")
    if executable_sha != hygiene._python_executable_sha256():
        return ["runner material must bind the current interpreter binary digest"]
    if material.get("jsonschema_version") == "unavailable":
        return ["runner material must discover the installed jsonschema version"]

    with tempfile.TemporaryDirectory(prefix="derivebsd-python-alias-") as td:
        alias = Path(td) / "renamed-python-launcher"
        shutil.copyfile(sys.executable, alias)
        if hygiene._python_executable_sha256(alias) != executable_sha:
            return ["identical interpreter bytes at another path must keep one runner identity"]

    script = (
        "import json,sys; "
        f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
        "import hygiene; "
        "print(json.dumps(hygiene._runner_environment_material(), sort_keys=True))"
    )
    completed = subprocess.run(
        [sys.executable, "-S", "-c", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if completed.returncode != 0:
        return [f"no-site runner probe failed: {completed.stderr.strip()!r}"]
    try:
        no_site_material = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return [f"no-site runner probe emitted invalid JSON: {exc}"]
    if no_site_material != material:
        return [
            "runner material changed under -S: "
            f"normal={material!r}, no_site={no_site_material!r}"
        ]
    return []


def check_resume_merge_regression() -> list[str]:
    """Make interrupted/resumed ledger writes monotonic for passed rows."""
    import hygiene

    checks = hygiene.selected_checks("release-critical")[:3]
    if len(checks) < 3:
        return ["release-critical profile must expose at least three checks for merge regression"]

    def row(cmd: list[str]) -> dict[str, Any]:
        tool = hygiene.tool_name(cmd)
        command = [hygiene._repo_arg(str(part)) for part in hygiene.child_cmd(cmd)]
        return {
            "tool": tool,
            "profile": "release-critical",
            "selected_profile": "release-critical",
            "command": command,
            "tool_sha256": "sha256:" + hashlib.sha256((ROOT / "tools" / tool).read_bytes()).hexdigest(),
            "cube_input_sha256": hygiene._cube_input_sha256(),
            "cube_input_fingerprint_scope": hygiene._cube_input_fingerprint_scope(),
            "cube_input_file_count": hygiene._cube_input_fingerprint_file_count(),
            "runner_environment_sha256": hygiene._runner_environment_sha256(),
            "runner_environment_scope": hygiene._runner_environment_scope(),
            "status": "passed",
            "return_code": 0,
            "failure_class": "none",
            "terminated_by_signal": False,
            "signal_name": None,
            "timed_out": False,
            "timeout_seconds": 120.0,
            "timeout_status": "completed",
            "process_group_isolated": True,
            "timeout_kill_scope": "not-needed",
            "timeout_termination_signal": None,
            "timeout_grace_seconds": None,
            "started_at_utc": "2026-06-04T00:00:00Z",
            "finished_at_utc": "2026-06-04T00:00:01Z",
            "elapsed_seconds": 0.001,
            "stdout_sha256": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stdout_bytes": 0,
            "stdout_lines": 0,
            "stderr_sha256": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stderr_bytes": 0,
            "stderr_lines": 0,
            "child_max_rss_kib_best_effort": None,
            "child_max_rss_kib_scope": "unavailable",
            "child_max_rss_kib_before": None,
        }

    rows = [row(cmd) for cmd in checks]
    with tempfile.TemporaryDirectory(prefix="derivebsd-hygiene-ledger-merge-") as td:
        ledger = Path(td) / "ledger.json"
        hygiene.write_ledger(ledger, "release-critical", 120.0, rows, "2026-06-04T00:00:00Z", len(checks), checks)
        seeded = load_json(Path(td), "ledger.json")
        seeded["hygiene_wrapper_sha256"] = "sha256:" + "0" * 64
        ledger.write_text(json.dumps(seeded, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_records, _ = hygiene.resume_records(ledger, "release-critical", checks)
        if stale_records:
            return ["resume_records reused rows from a ledger with a stale hygiene_wrapper_sha256"]
        hygiene.write_ledger(ledger, "release-critical", 120.0, rows, "2026-06-04T00:00:00Z", len(checks), checks)
        seeded = load_json(Path(td), "ledger.json")
        seeded["generated_for_version"] = "2026-06-05r000"
        seeded["ledger_id"] = "cube-hygiene-run-ledger-20260605-r000-release-critical"
        ledger.write_text(json.dumps(seeded, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_records, _ = hygiene.resume_records(ledger, "release-critical", checks)
        if stale_records:
            return ["resume_records reused rows from a stale release-token ledger"]
        hygiene.write_ledger(ledger, "release-critical", 120.0, rows, "2026-06-04T00:00:00Z", len(checks), checks)
        seeded = load_json(Path(td), "ledger.json")
        seeded["cube_input_sha256"] = "sha256:" + "1" * 64
        for row_obj in seeded.get("results", []):
            row_obj["cube_input_sha256"] = seeded["cube_input_sha256"]
        ledger.write_text(json.dumps(seeded, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_records, _ = hygiene.resume_records(ledger, "release-critical", checks)
        if stale_records:
            return ["resume_records reused rows from a ledger with a stale cube_input_sha256"]
        hygiene.write_ledger(ledger, "release-critical", 120.0, rows, "2026-06-04T00:00:00Z", len(checks), checks)
        seeded = load_json(Path(td), "ledger.json")
        seeded["runner_environment_sha256"] = "sha256:" + "2" * 64
        for row_obj in seeded.get("results", []):
            row_obj["runner_environment_sha256"] = seeded["runner_environment_sha256"]
        ledger.write_text(json.dumps(seeded, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale_records, _ = hygiene.resume_records(ledger, "release-critical", checks)
        if stale_records:
            return ["resume_records reused rows from a ledger with a stale runner_environment_sha256"]
        hygiene.write_ledger(ledger, "release-critical", 120.0, rows, "2026-06-04T00:00:00Z", len(checks), checks)
        hygiene.write_ledger(
            ledger,
            "release-critical",
            120.0,
            [rows[0]],
            "2026-06-04T00:00:00Z",
            len(checks),
            checks,
            preserve_existing_passed=True,
        )
        merged = load_json(Path(td), "ledger.json")
        hygiene.write_ledger(ledger, "release-critical", 120.0, [rows[0]], "2026-06-04T00:00:00Z", len(checks), checks)
        fresh = load_json(Path(td), "ledger.json")
        if fresh.get("checks_completed") != 1:
            return ["fresh ledger write reused existing passed rows without --resume-ledger"]
        hygiene.write_ledger(
            ledger,
            "release-critical",
            120.0,
            [],
            "2026-06-04T00:00:00Z",
            len(checks),
            checks,
            run_budget_seconds=10.0,
            stopped_by_run_budget=True,
        )
        budgeted = load_json(Path(td), "ledger.json")
        if budgeted.get("run_budget_status") != "stopped-before-budget" or budgeted.get("run_budget_seconds") != 10.0:
            return ["run-budgeted ledger stop did not record stopped-before-budget evidence"]
        hygiene.write_ledger(
            ledger,
            "release-critical",
            120.0,
            [],
            "2026-06-04T00:00:00Z",
            len(checks),
            checks,
            check_budget_limit=0,
            stopped_by_check_budget=True,
        )
        check_budgeted = load_json(Path(td), "ledger.json")
        if check_budgeted.get("check_budget_status") != "stopped-before-check-budget" or check_budgeted.get("check_budget_limit") != 0:
            return ["check-budgeted ledger stop did not record stopped-before-check-budget evidence"]
        if hygiene._ledger_exit_code([], len(checks)) != hygiene.LEDGER_PARTIAL_EXIT_CODE:
            return ["empty partial ledger should return the explicit partial exit code"]
        if hygiene._ledger_exit_code([rows[0]], len(checks)) != hygiene.LEDGER_PARTIAL_EXIT_CODE:
            return ["clean partial ledger should not return success"]
        failed_row = dict(rows[0])
        failed_row["status"] = "failed"
        failed_row["return_code"] = 1
        failed_row["failure_class"] = "exit-nonzero"
        if hygiene._ledger_exit_code([failed_row], len(checks)) != 1:
            return ["failed partial ledger should prefer failure exit code 1"]
        if hygiene._ledger_exit_code(rows, len(checks)) != 0:
            return ["complete passed ledger should return success"]
    tools = [r.get("tool") for r in merged.get("results", []) if isinstance(r, dict)]
    expected = [hygiene.tool_name(cmd) for cmd in checks]
    if tools[:3] != expected:
        return [f"resume ledger merge lost passed rows: {tools!r} != {expected!r}"]
    if merged.get("checks_completed") != 3 or merged.get("run_complete") is not True:
        return ["resume ledger merge should preserve completed row count and run_complete"]
    return []


def main() -> int:
    observed = load_json(ROOT, EXAMPLE)
    errs = validation_errors(ROOT, SCHEMA, observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(observed)
    if sem:
        fail("cube hygiene run ledger semantic check failed: " + "; ".join(sem[:10]))
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8", errors="replace")
    for token in [
        "--ledger-json",
        "--ledger",
        "--timeout-seconds",
        "stdout_sha256",
        "child_max_rss_kib_best_effort",
        "timed-out",
        "--resume-ledger",
        "--max-checks",
        "--max-run-seconds",
        "run_budget_status",
        "_run_budget_status",
        "check_budget_status",
        "_check_budget_status",
        "run_complete",
        "checks_completed",
        "failure_class",
        "terminated_by_signal",
        "merge_existing_passed_rows",
        "preserve_existing_passed",
        "atomic_write_text",
        "NamedTemporaryFile",
        "os.fsync",
        "hygiene_wrapper_sha256",
        "cube_input_sha256",
        "_cube_input_sha256",
        "_ledger_cube_input_matches",
        "_runner_environment_sha256",
        "_runner_environment_material",
        "_python_executable_sha256",
        "python_executable_sha256",
        "_installed_distribution_version",
        "python-binary-version-platform-jsonschema",
        "_ledger_runner_environment_matches",
        "runner_environment_sha256",
        "_ledger_wrapper_digest_matches",
        "_ledger_release_metadata_matches",
        "_expected_ledger_id",
        "_terminate_timed_out_process",
        "start_new_session=True",
        "timeout_kill_scope",
        "process_group_isolated",
        "LEDGER_PARTIAL_EXIT_CODE",
        "_ledger_exit_code",
    ]:
        if token not in hygiene:
            fail(f"tools/hygiene.py missing ledger implementation token {token!r}")
    merge_errs = check_resume_merge_regression()
    if merge_errs:
        fail("cube hygiene run ledger resume merge regression failed: " + "; ".join(merge_errs))
    if "check_cube_hygiene_run_ledger.py" not in hygiene:
        fail("tools/hygiene.py missing check_cube_hygiene_run_ledger.py")
    require_text_tokens(ROOT, REQUIRED_TEXT_TOKENS, label="hygiene run ledger")
    print("cube hygiene run ledger check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
