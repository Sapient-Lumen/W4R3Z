#!/usr/bin/env python3
"""Exact-current U-123 disposition and artifact-coherence gate.

Research-only. This gate distinguishes the demonstrated same-peer transfer
ownership defect, the minimal reachable-state prototype, and a stricter
fail-closed experiment whose extra precondition has not been shown reachable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from source_bundle_locator import (  # noqa: E402
    EXPECTED_SOURCE_SHA256,
    SOURCE_PREFIX,
    SourceBundleError,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = "rev0073"
LANE = "github-branch-3.3.x"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
ARTIFACTS = ROOT / "maintainer_artifacts" / "u123"
SELECTED_PATCH = (
    ROOT / "handoff" / "rev0073" / "u123" / "patches"
    / "u-123-current-3.3.x-code-only-p1.patch"
)
STRICT_PATCH = (
    ROOT / "handoff" / "rev0073" / "u123-research" / "patches"
    / "U123-RESEARCH-PROTOTYPE-REV0073.diff"
)
STATE_RUNNER = ROOT / "tools" / "run_u123_state_matrix_rev0073.py"
UNIT_DIR = "pynicotine/tests/unit"

TESTS = {
    "current-behavior-witness": "test_downloads_duplicate_transfer_token_reproducer.py",
    "collision-rejection": "test_downloads_duplicate_transfer_token_collision_rejection_regression.py",
    "identity-aware-cleanup": "test_downloads_duplicate_transfer_token_identity_guard_regression.py",
    "burst-resource-bound": "test_downloads_duplicate_transfer_token_burst_bound_regression.py",
    "fixed-composite": "test_downloads_duplicate_transfer_token_fixed_regression.py",
    "same-object-reentry-experiment": "test_downloads_duplicate_transfer_token_same_object_reentry_experiment.py",
}
EXPECTED_PASS = {
    "unpatched": {"current-behavior-witness"},
    "selected-minimal": {
        "collision-rejection",
        "identity-aware-cleanup",
        "burst-resource-bound",
        "fixed-composite",
    },
    "strict-experiment": {
        "collision-rejection",
        "identity-aware-cleanup",
        "burst-resource-bound",
        "fixed-composite",
        "same-object-reentry-experiment",
    },
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    if not fields:
        fields = ["status"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def source_lane_head(source_zip: Path) -> str:
    suffix = f"git-full/.git/worktrees/{LANE}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii", errors="strict").strip()


def safe_extract_lane(source_zip: Path, destination: Path) -> int:
    prefix = SOURCE_PREFIX + LANE + "/"
    count = 0
    with zipfile.ZipFile(source_zip) as archive:
        for info in archive.infolist():
            if not info.filename.startswith(prefix) or info.filename.endswith("/"):
                continue
            relative = Path(info.filename[len(prefix):])
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe source entry: {info.filename}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source_handle, target.open("wb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            count += 1
    return count


def isolated_env(source: Path, runtime: Path) -> tuple[dict[str, str], Path]:
    runtime.mkdir(parents=True, exist_ok=True)
    cwd = runtime / "cwd"
    cwd.mkdir(exist_ok=True)
    mapping = {
        "HOME": runtime / "home",
        "XDG_CONFIG_HOME": runtime / "xdg-config",
        "XDG_DATA_HOME": runtime / "xdg-data",
        "XDG_CACHE_HOME": runtime / "xdg-cache",
        "TMPDIR": runtime / "tmp",
    }
    for path in mapping.values():
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in mapping.items()})
    env.update({
        "PYTHONPATH": str(source),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    })
    return env, cwd


def run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 120
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=(os.name == "posix"),
    )
    try:
        stdout, _ = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, process.returncode, stdout)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        stdout, _ = process.communicate()
        return subprocess.CompletedProcess(
            command, 124, (stdout or "") + f"\n[{REVISION} timeout after {timeout}s]\n"
        )


def summary_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if line == "OK" or line.startswith("FAILED"):
            return line
        if re.search(r"\b(?:failed|passed|skipped)\b", line) and " in " in line:
            return line
    return lines[-1] if lines else ""


def outcome_counts(output: str) -> dict[str, int]:
    summary = summary_line(output)
    counts = {"failed": 0, "passed": 0, "skipped": 0}
    for count, label in re.findall(r"(\d+) (failed|passed|skipped)", summary):
        counts[label] = int(count)
    return counts


def apply_patch(source: Path, patch: Path, runtime: Path, state: str) -> dict[str, Any]:
    proc = run(
        ["patch", "--batch", "--forward", "-p1", "-i", str(patch)],
        cwd=source,
        env=os.environ.copy(),
        timeout=60,
    )
    output_path = runtime / f"patch-{state}.txt"
    output_path.write_text(proc.stdout, encoding="utf-8")
    return {
        "state": state,
        "patch": str(patch.relative_to(ROOT)),
        "sha256": sha256_path(patch),
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        "status": "pass" if proc.returncode == 0 else "fail",
    }


def source_invariants(source: Path) -> list[dict[str, Any]]:
    downloads = (source / "pynicotine/downloads.py").read_text(encoding="utf-8")
    transfers = (source / "pynicotine/transfers.py").read_text(encoding="utf-8")
    checks = [
        (
            "activation writes one-owner slot without collision guard",
            "self.active_users[transfer.username][token] = transfer" in transfers,
        ),
        (
            "deactivation deletes slot without object identity check",
            "del self.active_users[username][token]" in transfers
            and "active_transfer is transfer" not in transfers,
        ),
        (
            "download admission resolves queued or failed object before activation",
            "download = (self.queued_users.get(username, {}).get(virtual_path)" in downloads,
        ),
        (
            "file init routes by username and token",
            "download = self.active_users.get(username, {}).get(token)" in downloads,
        ),
    ]
    return [
        {"invariant": label, "observed": str(observed).lower(), "status": "pass" if observed else "fail"}
        for label, observed in checks
    ]


def syntax_checks(states: dict[str, Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state, source in states.items():
        for relative in ("pynicotine/downloads.py", "pynicotine/transfers.py"):
            path = source / relative
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
                status, error = "pass", ""
            except SyntaxError as exc:
                status, error = "fail", f"{exc.__class__.__name__}: {exc}"
            rows.append({"state": state, "path": relative, "status": status, "error": error})
    return rows


def run_state_matrices(
    states: dict[str, Path], runtime: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run all classified tests and burst metrics once per isolated source state."""
    test_rows: list[dict[str, Any]] = []
    burst_rows: list[dict[str, Any]] = []

    for state, source in states.items():
        print(f"[rev0073] state matrix: {state}", file=sys.stderr, flush=True)
        with tempfile.TemporaryDirectory(prefix=f"rev73-{state}-matrix-") as temp_runtime:
            env, cwd = isolated_env(source, Path(temp_runtime))
            proc = run(
                [sys.executable, str(STATE_RUNNER), "--burst-size", "32"],
                cwd=cwd,
                env=env,
                timeout=90,
            )
        state_output = runtime / state / "state-matrix.txt"
        state_output.parent.mkdir(parents=True, exist_ok=True)
        state_output.write_text(proc.stdout, encoding="utf-8")

        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 else {}
        except (IndexError, json.JSONDecodeError):
            payload = {}

        observed_tests = payload.get("tests", {}) if isinstance(payload, dict) else {}
        for test_id, filename in TESTS.items():
            result = observed_tests.get(test_id, {})
            tests_run = int(result.get("tests_run", 0))
            valid = proc.returncode == 0 and tests_run > 0
            observed_pass = valid and bool(result.get("passed", False))
            expected_pass = test_id in EXPECTED_PASS[state]
            test_rows.append({
                "state": state,
                "test_id": test_id,
                "test_file": filename,
                "expected": "pass" if expected_pass else "fail",
                "observed": "pass" if observed_pass else "fail",
                "tests_run": tests_run,
                "failures": int(result.get("failures", 0)),
                "errors": int(result.get("errors", 0)),
                "skipped": int(result.get("skipped", 0)),
                "runner_rc": proc.returncode,
                "summary": str(result.get("summary", summary_line(proc.stdout))),
                "expectation_status": "pass"
                if valid and observed_pass == expected_pass
                else "fail",
            })
            (runtime / state / f"{test_id}.txt").write_text(
                str(result.get("output_tail", proc.stdout)), encoding="utf-8"
            )

        result = payload.get("burst", {}) if isinstance(payload, dict) else {}
        expected = (
            {
                "allowed": 32,
                "rejected": 0,
                "open_file_handles": 32,
                "socket_owners": 32,
                "queued_remaining": 0,
            }
            if state == "unpatched"
            else {
                "allowed": 1,
                "rejected": 31,
                "open_file_handles": 1,
                "socket_owners": 1,
                "queued_remaining": 31,
            }
        )
        burst_rows.append({
            "state": state,
            "runner_rc": proc.returncode,
            **result,
            "expectation_status": "pass"
            if proc.returncode == 0
            and bool(result)
            and all(result.get(key) == value for key, value in expected.items())
            else "fail",
        })

    return test_rows, burst_rows

def run_upstream_units(states: dict[str, Path], runtime: Path) -> list[dict[str, Any]]:
    """Run baseline and selected-prototype upstream units in parallel isolation."""
    msgfmt_available = shutil.which("msgfmt") is not None

    def run_state(state: str) -> dict[str, Any]:
        source = states[state]
        with tempfile.TemporaryDirectory(prefix=f"rev73-{state}-unit-") as temp_runtime:
            env, cwd = isolated_env(source, Path(temp_runtime))
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                str(source / UNIT_DIR),
            ]
            if not msgfmt_available:
                command.extend(["--ignore", str(source / UNIT_DIR / "test_i18n.py")])
            proc = run(command, cwd=cwd, env=env, timeout=180)
        output_path = runtime / state / "upstream-unit.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(proc.stdout, encoding="utf-8")
        return {
            "state": state,
            "observed_rc": proc.returncode,
            "summary": summary_line(proc.stdout),
            **outcome_counts(proc.stdout),
            "msgfmt_available": str(msgfmt_available).lower(),
            "i18n_excluded": str(not msgfmt_available).lower(),
            "status": "pass" if proc.returncode == 0 else "fail",
        }

    state_order = ("unpatched", "selected-minimal")
    with ThreadPoolExecutor(max_workers=2) as executor:
        rows = list(executor.map(run_state, state_order))
    return rows

def count_tree(paths: list[Path]) -> dict[str, int]:
    existing = [path for path in paths if path.is_file()]
    lines: list[str] = []
    for path in existing:
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    return {
        "python_files": len(existing),
        "python_lines": len(lines),
        "python_nonblank_lines": sum(bool(line.strip()) for line in lines),
        "python_bytes": sum(path.stat().st_size for path in existing),
        "semicolon_statement_lines": sum(
            ";" in line and not line.lstrip().startswith("#") for line in lines
        ),
        "lines_over_100_chars": sum(len(line) > 100 for line in lines),
        "max_line_length": max((len(line) for line in lines), default=0),
    }

def refactor_metrics() -> dict[str, Any]:
    archive = ROOT / "docs" / "archive" / "rev0072-active-u123"
    archived_files = sorted(archive.glob("*.py"))
    current_files = sorted(ARTIFACTS.glob("*.py"))
    before = count_tree(archived_files)
    after = count_tree(current_files)
    line_reduction = before["python_lines"] - after["python_lines"]
    byte_reduction = before["python_bytes"] - after["python_bytes"]
    return {
        "baseline_path": str(archive.relative_to(ROOT)),
        "current_path": str(ARTIFACTS.relative_to(ROOT)),
        "baseline": before,
        "current": after,
        "shared_harness_files": 1,
        "current_test_entrypoints": len(
            [path for path in current_files if path.name.startswith("test_")]
        ),
        "copied_fixture_files_removed": max(0, before["python_files"] - 1),
        "line_reduction": line_reduction,
        "line_reduction_pct": round(
            100 * line_reduction / before["python_lines"], 2
        ) if before["python_lines"] else 0.0,
        "byte_reduction": byte_reduction,
        "interpretation": (
            "copied setup was centralized; current totals also include the new "
            "burst regression and isolated same-object experiment"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument(
        "--out-dir", default=str(ROOT / "evidence" / "rev0073-u123-runtime")
    )
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        source_zip, candidates = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(json.dumps({"revision": REVISION, "status": "fail", "errors": [str(exc)]}, indent=2))
        return 1

    source_info = inspect_bundle(source_zip)
    lane_head = source_lane_head(source_zip)
    if source_info.status != "pass":
        errors.append("source bundle contract")
    if lane_head != EXPECTED_REF:
        errors.append(f"lane head {lane_head} != {EXPECTED_REF}")

    for required in (SELECTED_PATCH, STRICT_PATCH, STATE_RUNNER):
        if not required.is_file():
            errors.append(f"missing required artifact: {required.relative_to(ROOT)}")

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    patch_rows: list[dict[str, Any]] = []
    state_roots: list[Path] = []
    try:
        # Keep each source state in an independent temporary root.  Earlier
        # versions placed all states under one parent; broad temporary cleanup
        # in a child process could then invalidate sibling lanes and the later
        # parity suite.  Independent roots make that failure mode impossible.
        states = {}
        for state, suffix in (
            ("unpatched", "unpatched"),
            ("selected-minimal", "selected"),
            ("strict-experiment", "strict"),
        ):
            destination = Path(tempfile.mkdtemp(prefix=f"rev0073-u123-{suffix}-"))
            state_roots.append(destination)
            states[state] = destination

        print("[rev0073] extracting independent source states", file=sys.stderr, flush=True)
        entry_counts = {
            state: safe_extract_lane(source_zip, destination)
            for state, destination in states.items()
        }
        invariants = source_invariants(states["unpatched"])

        print("[rev0073] applying research patches", file=sys.stderr, flush=True)
        patch_rows.append(
            apply_patch(states["selected-minimal"], SELECTED_PATCH, out_dir, "selected-minimal")
        )
        patch_rows.append(
            apply_patch(states["strict-experiment"], STRICT_PATCH, out_dir, "strict-experiment")
        )
        if any(row["status"] != "pass" for row in patch_rows):
            errors.append("patch application")

        compile_rows = syntax_checks(states)
        if any(row["status"] != "pass" for row in compile_rows):
            errors.append("syntax compile")

        # Run parity first, before any focused harness can exercise cleanup
        # behavior.  Only the selected minimal prototype participates because
        # the strict lane is explicitly an unselected reachability experiment.
        print("[rev0073] running isolated upstream units", file=sys.stderr, flush=True)
        unit_rows = run_upstream_units(states, out_dir)

        print("[rev0073] running classified artifact matrix and burst", file=sys.stderr, flush=True)
        test_rows, burst_rows = run_state_matrices(states, out_dir)
        if any(row["expectation_status"] != "pass" for row in test_rows):
            errors.append("test expectation")
        if any(row["expectation_status"] != "pass" for row in burst_rows):
            errors.append("burst expectation")
    finally:
        for state_root in state_roots:
            shutil.rmtree(state_root, ignore_errors=True)

    if any(row["status"] != "pass" for row in invariants):
        errors.append("source invariant trace")
    if any(row["status"] != "pass" for row in unit_rows):
        errors.append("upstream unit suite")
    parity_fields = ("failed", "passed", "skipped")
    unit_parity = (
        len(unit_rows) == 2
        and all(unit_rows[0][field] == unit_rows[1][field] for field in parity_fields)
    )
    if not unit_parity:
        errors.append("upstream unit outcome parity")

    metrics = refactor_metrics()
    if metrics["current"]["semicolon_statement_lines"]:
        errors.append("active U-123 artifacts contain semicolon-packed statement lines")
    if metrics["current"]["python_bytes"] >= metrics["baseline"]["python_bytes"]:
        errors.append("U-123 refactor did not reduce artifact bytes")

    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "source_zip": str(source_zip),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_contract_status": source_info.status,
        "source_candidates": [asdict(row) for row in candidates],
        "lane": LANE,
        "lane_ref": lane_head,
        "expected_ref": EXPECTED_REF,
        "exact_current_ref_match": lane_head == EXPECTED_REF,
        "source_entries": entry_counts,
        "patches": patch_rows,
        "source_invariants": invariants,
        "test_expectations_passed": sum(
            row["expectation_status"] == "pass" for row in test_rows
        ),
        "test_expectations_total": len(test_rows),
        "burst_expectations_passed": sum(
            row["expectation_status"] == "pass" for row in burst_rows
        ),
        "burst_expectations_total": len(burst_rows),
        "upstream_unit_parity": unit_parity,
        "upstream_units": unit_rows,
        "compile": compile_rows,
        "refactor": metrics,
        "decision": {
            "technical_status": "confirmed exact-current same-peer transfer ownership defect",
            "resource_evidence": (
                "bounded 32-request harness retained 32 live file handles and 32 socket-owner "
                "references unpatched versus one of each with either guard"
            ),
            "security_ceiling": (
                "durable end-to-end descriptor exhaustion, persistence, and broader security "
                "boundary impact remain unquantified"
            ),
            "selected_patch": (
                "minimal different-object collision rejection plus identity-aware stale cleanup"
            ),
            "strict_experiment": (
                "not selected; its additional same-object state was synthesized and not shown reachable"
            ),
            "routing": (
                "research-only public correctness/hardening question after independent human "
                "reproduction and authorship"
            ),
        },
    }

    write_json(out_dir / "summary.json", summary)
    if args.write_data:
        outputs: list[tuple[str, object]] = [
            ("rev0073_u123_disposition_summary.json", summary),
            ("rev0073_u123_test_matrix.json", test_rows),
            ("rev0073_u123_burst_metrics.json", burst_rows),
            ("rev0073_u123_upstream_unit_parity.json", unit_rows),
            ("rev0073_u123_refactor_metrics.json", metrics),
            ("rev0073_u123_patch_apply.json", patch_rows),
            ("rev0073_u123_source_invariants.json", invariants),
            ("rev0073_u123_compile.json", compile_rows),
        ]
        for name, value in outputs:
            write_json(ROOT / "data" / name, value)
        write_csv(ROOT / "data" / "rev0073_u123_test_matrix.csv", test_rows)
        write_csv(ROOT / "data" / "rev0073_u123_burst_metrics.csv", burst_rows)
        write_csv(ROOT / "data" / "rev0073_u123_upstream_unit_parity.csv", unit_rows)
        write_csv(ROOT / "data" / "rev0073_u123_patch_apply.csv", patch_rows)
        write_csv(ROOT / "data" / "rev0073_u123_source_invariants.csv", invariants)
        write_csv(ROOT / "data" / "rev0073_u123_compile.csv", compile_rows)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
