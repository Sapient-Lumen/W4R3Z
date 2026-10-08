#!/usr/bin/env python3
"""Verify SEARCH-AGAIN-SELF-01 and map unresolved refresh epochs.

Research-only. The selected change is limited to recording the same token that
is sent on the wire for a repeated self-user search. The broader Search Again
refresh model remains unselected.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import xml.etree.ElementTree as ET
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

REVISION = "rev0077"
LANE = "github-branch-master"
SOURCE_REF = "f4e17d59783dbc48ea31d2e899a681e2dd1ed500"
VISIBLE_HEAD = "a96406e7aa285a3fb2a3e35900686d164a22bf02"
ARTIFACTS = ROOT / "maintainer_artifacts/search-again-01"
PATCH = ARTIFACTS / "master-search-again-self-token.patch"
UNIT_TESTS = Path("pynicotine/tests/unit")
OUTPUT_JSON = ROOT / "data/rev0077_search_again_summary.json"
OUTPUT_INVARIANTS = ROOT / "data/rev0077_search_again_source_invariants.csv"
OUTPUT_TESTS = ROOT / "data/rev0077_search_again_test_matrix.csv"
OUTPUT_COMPILE = ROOT / "data/rev0077_search_again_compile_matrix.csv"
RUNTIME = ROOT / "evidence/rev0077-search-again-runtime"

TESTS = {
    "current-defect-witness": (
        "test_search_again_self_token_current_behavior.py",
        (
            "test_current_resend_records_latest_token_but_sends_search_token",
            "test_current_divergence_suppresses_local_request",
            "test_initial_self_search_still_uses_matching_token",
        ),
    ),
    "selected-token-policy": (
        "test_search_again_self_token_selected_policy.py",
        (
            "test_older_self_search_records_requested_search_token",
            "test_matching_local_request_consumes_requested_token",
            "test_nonself_user_search_does_not_open_local_response_gate",
        ),
    ),
    "current-epoch-source": (
        "test_search_again_epoch_source_semantics.py",
        (
            "test_search_again_reuses_page_token_without_clearing_results",
            "test_result_handler_deduplicates_username_for_page_lifetime",
            "test_clear_model_is_the_path_that_resets_username_deduplication",
        ),
    ),
    "epoch-policy-models": (
        "test_search_again_epoch_models.py",
        (
            "test_current_same_token_keeps_first_response_from_each_user",
            "test_clear_with_same_token_cannot_distinguish_late_old_response",
            "test_new_token_clear_and_retire_old_is_a_true_replace_epoch",
            "test_new_token_without_clear_is_union_not_refresh",
        ),
    ),
}

EXPECTED = {
    "bundled-master-baseline": {
        "test_current_resend_records_latest_token_but_sends_search_token": True,
        "test_current_divergence_suppresses_local_request": True,
        "test_initial_self_search_still_uses_matching_token": True,
        "test_older_self_search_records_requested_search_token": False,
        "test_matching_local_request_consumes_requested_token": False,
        "test_nonself_user_search_does_not_open_local_response_gate": True,
        "test_search_again_reuses_page_token_without_clearing_results": True,
        "test_result_handler_deduplicates_username_for_page_lifetime": True,
        "test_clear_model_is_the_path_that_resets_username_deduplication": True,
        "test_current_same_token_keeps_first_response_from_each_user": True,
        "test_clear_with_same_token_cannot_distinguish_late_old_response": True,
        "test_new_token_clear_and_retire_old_is_a_true_replace_epoch": True,
        "test_new_token_without_clear_is_union_not_refresh": True,
    },
    "bundled-master-selected": {
        "test_current_resend_records_latest_token_but_sends_search_token": False,
        "test_current_divergence_suppresses_local_request": False,
        "test_initial_self_search_still_uses_matching_token": True,
        "test_older_self_search_records_requested_search_token": True,
        "test_matching_local_request_consumes_requested_token": True,
        "test_nonself_user_search_does_not_open_local_response_gate": True,
        "test_search_again_reuses_page_token_without_clearing_results": True,
        "test_result_handler_deduplicates_username_for_page_lifetime": True,
        "test_clear_model_is_the_path_that_resets_username_deduplication": True,
        "test_current_same_token_keeps_first_response_from_each_user": True,
        "test_clear_with_same_token_cannot_distinguish_late_old_response": True,
        "test_new_token_clear_and_retire_old_is_a_true_replace_epoch": True,
        "test_new_token_without_clear_is_union_not_refresh": True,
    },
}


def sha256_path(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["status"])
        writer.writeheader()
        writer.writerows(rows)


def lane_head(source_zip: Path, lane: str) -> str:
    suffix = f"git-full/.git/worktrees/{lane}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii").strip()


def safe_extract_lane(source_zip: Path, lane: str, destination: Path) -> int:
    archive_prefix = SOURCE_PREFIX.rsplit("source-trees/", 1)[0] + "archives/"
    archive_name = archive_prefix + f"{lane}.tar.gz"
    with zipfile.ZipFile(source_zip) as outer:
        payload = outer.read(archive_name)

    count = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as inner:
        members = inner.getmembers()
        roots = {Path(member.name).parts[0] for member in members if member.name}
        if len(roots) != 1:
            raise RuntimeError(f"expected one tar root, found {sorted(roots)}")
        root = next(iter(roots))

        for member in members:
            path = Path(member.name)
            if not path.parts or path.parts[0] != root:
                raise RuntimeError(f"entry escapes tar root: {member.name}")
            relative = Path(*path.parts[1:])
            if not relative.parts:
                continue
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe tar entry: {member.name}")

            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            source_member = member
            if member.issym() or member.islnk():
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(member.name), member.linkname)
                )
                if not resolved.startswith(root + "/"):
                    raise RuntimeError(
                        f"symlink escapes tar root: {member.name} -> {member.linkname}"
                    )
                source_member = inner.getmember(resolved)

            if not source_member.isfile():
                raise RuntimeError(f"unsupported tar entry: {member.name}")
            source = inner.extractfile(source_member)
            if source is None:
                raise RuntimeError(f"cannot read tar entry: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            count += 1

    return count


def isolated_env(source: Path, runtime: Path) -> tuple[dict[str, str], Path]:
    runtime.mkdir(parents=True, exist_ok=True)
    cwd = runtime / "cwd"
    cwd.mkdir(exist_ok=True)
    paths = {
        "HOME": runtime / "home",
        "XDG_CONFIG_HOME": runtime / "xdg-config",
        "XDG_DATA_HOME": runtime / "xdg-data",
        "XDG_CACHE_HOME": runtime / "xdg-cache",
        "TMPDIR": runtime / "tmp",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in paths.items()})
    env.update({
        "PYTHONPATH": os.pathsep.join((str(ARTIFACTS), str(source))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    })
    return env, cwd


def run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 180
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
            command, 124, (stdout or "") + "\n[timeout]\n"
        )


def run_logged(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    output_path: Path,
    timeout: int = 240,
) -> subprocess.CompletedProcess[str]:
    """Run multiprocessing tests with regular-file output, never a PIPE.

    A descendant can inherit a captured pipe and delay communicate() after
    pytest exits. GNU timeout supplies bounded process cleanup; the regular
    file makes the pytest parent's completion observable immediately.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrapped = command
    if shutil.which("timeout"):
        wrapped = [
            "timeout",
            "--signal=TERM",
            "--kill-after=3",
            str(timeout),
            *command,
        ]
    with output_path.open("w", encoding="utf-8") as output:
        try:
            completed = subprocess.run(
                wrapped,
                cwd=cwd,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=None if wrapped is not command else timeout,
                check=False,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            output.write("\n[timeout]\n")
            returncode = 124
    stdout = output_path.read_text(encoding="utf-8", errors="replace")
    return subprocess.CompletedProcess(command, returncode, stdout)


def normalize_pytest(output: str) -> str:
    return re.sub(r" in [0-9.]+s(?=\n|$)", " in <elapsed>s", output)


def pytest_summary(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b(passed|failed|skipped|error)s?\b", line):
            return re.sub(r" in [0-9.]+s$", "", line)
    return lines[-1] if lines else ""


def function_text(path: Path, class_name: str, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == function_name:
                text = ast.get_source_segment(source, child)
                if text is None:
                    break
                return text
    raise RuntimeError(f"missing {class_name}.{function_name} in {path}")


def source_invariants(source: Path, selected: Path) -> list[dict[str, Any]]:
    core_path = source / "pynicotine/search.py"
    gui_path = source / "pynicotine/gtkgui/search.py"
    test_path = source / "pynicotine/tests/unit/search/test_search.py"
    peer = function_text(core_path, "Search", "_send_peer_search_request")
    incoming = function_text(core_path, "Search", "_process_search_request")
    resend = function_text(gui_path, "Search", "on_search_again")
    response = function_text(gui_path, "Search", "file_search_response")
    clear_model = function_text(gui_path, "Search", "clear_model")
    selected_peer = function_text(
        selected / "pynicotine/search.py", "Search", "_send_peer_search_request"
    )
    unit_source = test_path.read_text(encoding="utf-8")

    checks = (
        ("baseline records component-global token", "self._own_tokens.add(self.token)" in peer),
        ("baseline wire request uses search token", "UserSearch(username, search.token" in peer),
        ("incoming gate checks supplied token", "token not in self._own_tokens" in incoming),
        ("incoming gate consumes supplied token", "self._own_tokens.discard(token)" in incoming),
        ("Search Again reuses page token", "send_search_request(self.token)" in resend),
        ("Search Again does not clear model", "clear(" not in resend and "clear_model(" not in resend),
        ("page rejects existing username", "if user in self.users:" in response),
        ("clear model resets username map", "self.users.clear()" in clear_model),
        ("upstream units lack own-token resend regression", "_own_tokens" not in unit_source),
        ("selected records request token", "self._own_tokens.add(search.token)" in selected_peer),
        ("selected removes global-token write", "self._own_tokens.add(self.token)" not in selected_peer),
        ("selected preserves wire request", "UserSearch(username, search.token" in selected_peer),
    )
    return [
        {"check": name, "status": "pass" if passed else "fail"}
        for name, passed in checks
    ]


def apply_patch(source: Path, runtime: Path) -> dict[str, Any]:
    dry = run(
        ["patch", "-p1", "--dry-run", "--forward", "-i", str(PATCH)],
        cwd=source,
        timeout=30,
    )
    actual = run(
        ["patch", "-p1", "--forward", "-i", str(PATCH)],
        cwd=source,
        timeout=30,
    )
    (runtime / "patch-dry-run.txt").write_text(dry.stdout, encoding="utf-8")
    (runtime / "patch-apply.txt").write_text(actual.stdout, encoding="utf-8")
    return {
        "dry_run_status": "pass" if dry.returncode == 0 else "fail",
        "apply_status": "pass" if actual.returncode == 0 else "fail",
        "dry_run_returncode": dry.returncode,
        "apply_returncode": actual.returncode,
    }


def run_state_tests(
    source: Path,
    runtime: Path,
    state: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the classified suite once and recover each test polarity from JUnit.

    Expected-failure polarity is evidence here, so pytest's aggregate return code
    is not itself a state failure. Collection integrity and the per-test matrix
    determine the result. This avoids one interpreter startup per assertion.
    """
    state_runtime = runtime / f"classified-{state}"
    env, cwd = isolated_env(source, state_runtime)
    junit_path = state_runtime / "classified-results.xml"
    paths = [str(ARTIFACTS / filename) for filename, _ in TESTS.values()]
    proc = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--tb=short",
            f"--junitxml={junit_path}",
            *paths,
        ],
        cwd=cwd,
        env=env,
        timeout=150,
    )
    normalized = normalize_pytest(proc.stdout)
    (RUNTIME / f"classified-tests-{state}.txt").write_text(
        normalized, encoding="utf-8"
    )

    role_by_test = {
        test_name: role
        for role, (_, test_names) in TESTS.items()
        for test_name in test_names
    }
    outcomes: dict[str, dict[str, Any]] = {}
    parse_error = ""
    if junit_path.is_file():
        try:
            root = ET.parse(junit_path).getroot()
            for case in root.iter("testcase"):
                name = case.attrib.get("name", "")
                if name not in role_by_test:
                    continue
                failure = case.find("failure")
                error = case.find("error")
                skipped = case.find("skipped")
                outcomes[name] = {
                    "actual_pass": failure is None and error is None and skipped is None,
                    "junit_failure": failure is not None,
                    "junit_error": error is not None,
                    "junit_skipped": skipped is not None,
                }
        except (ET.ParseError, OSError) as exc:
            parse_error = str(exc)
    else:
        parse_error = "JUnit output missing"

    rows: list[dict[str, Any]] = []
    for test_name, expected_pass in EXPECTED[state].items():
        outcome = outcomes.get(test_name)
        actual_pass = None if outcome is None else outcome["actual_pass"]
        rows.append({
            "source_state": state,
            "role": role_by_test[test_name],
            "test": test_name,
            "expected_pass": expected_pass,
            "actual_pass": actual_pass,
            "expectation_match": actual_pass is not None and actual_pass == expected_pass,
            "collected": outcome is not None,
            "summary": pytest_summary(proc.stdout),
        })

    metadata = {
        "source_state": state,
        "returncode": proc.returncode,
        "summary": pytest_summary(proc.stdout),
        "expected_tests": len(EXPECTED[state]),
        "collected_tests": len(outcomes),
        "parse_error": parse_error,
        "collection_complete": set(outcomes) == set(EXPECTED[state]),
    }
    return rows, metadata


def result_counts(output: str) -> dict[str, int]:
    values = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    for key in values:
        matches = re.findall(rf"(\d+) {key[:-1] if key.endswith('s') else key}s?", output)
        if matches:
            values[key] = int(matches[-1])
    return values


def run_units(source: Path, runtime: Path, state: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"units-{state}")
    unit_root = source / UNIT_TESTS
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(unit_root),
    ]
    i18n = unit_root / "test_i18n.py"
    msgfmt_available = shutil.which("msgfmt") is not None
    if i18n.exists() and not msgfmt_available:
        command.extend(["--ignore", str(i18n)])
    raw_log = runtime / f"upstream-units-{state}.raw.txt"
    proc = run_logged(
        command, cwd=cwd, env=env, output_path=raw_log, timeout=240
    )
    normalized = normalize_pytest(proc.stdout)
    (RUNTIME / f"upstream-units-{state}.txt").write_text(
        normalized, encoding="utf-8"
    )
    counts = result_counts(proc.stdout)
    return {
        "source_state": state,
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "summary": pytest_summary(proc.stdout),
        "msgfmt_available": msgfmt_available,
        **counts,
    }


def compile_rows(states: dict[str, Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    paths = sorted(ARTIFACTS.glob("*.py"))
    for state, source in states.items():
        for path in paths + [
            source / "pynicotine/search.py",
            source / "pynicotine/gtkgui/search.py",
        ]:
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
                status = "pass"
                detail = ""
            except Exception as exc:
                status = "fail"
                detail = str(exc)
            rows.append({
                "source_state": state,
                "path": path.name,
                "status": status,
                "detail": detail,
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        source_zip, inspections = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(canonical({"revision": REVISION, "status": "fail", "errors": [str(exc)]}), end="")
        return 1

    inspection = inspect_bundle(source_zip)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME.iterdir():
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

    with tempfile.TemporaryDirectory(prefix="nicotine-rev0077-") as temp_name:
        temp = Path(temp_name)
        baseline = temp / "baseline"
        selected = temp / "selected"
        baseline.mkdir()
        extracted_files = safe_extract_lane(source_zip, LANE, baseline)
        shutil.copytree(baseline, selected, dirs_exist_ok=True)

        head = lane_head(source_zip, LANE)
        if head != SOURCE_REF:
            errors.append(f"source ref: {head}")

        patch_result = apply_patch(selected, RUNTIME)
        if patch_result["dry_run_status"] != "pass" or patch_result["apply_status"] != "pass":
            errors.append("patch application")

        invariants = source_invariants(baseline, selected)
        if any(row["status"] != "pass" for row in invariants):
            errors.append("source invariants")

        states = {
            "bundled-master-baseline": baseline,
            "bundled-master-selected": selected,
        }
        test_rows: list[dict[str, Any]] = []
        classified_runs: list[dict[str, Any]] = []
        for state, source in states.items():
            state_rows, state_run = run_state_tests(
                source, temp / "runtime", state
            )
            test_rows.extend(state_rows)
            classified_runs.append(state_run)
        if any(not row["expectation_match"] for row in test_rows):
            errors.append("classified test expectations")
        if any(not row["collection_complete"] for row in classified_runs):
            errors.append("classified test collection")

        compile_matrix = compile_rows(states)
        if any(row["status"] != "pass" for row in compile_matrix):
            errors.append("compile checks")

        units = [
            run_units(baseline, temp / "runtime", "bundled-master-baseline"),
            run_units(selected, temp / "runtime", "bundled-master-selected"),
        ]
        if any(row["status"] != "pass" for row in units):
            errors.append("upstream units")
        unit_shapes = {
            (row["passed"], row["failed"], row["skipped"], row["errors"])
            for row in units
        }
        if len(unit_shapes) != 1:
            errors.append("upstream unit parity")

        critical_hashes = {
            "baseline_search_py": sha256_path(baseline / "pynicotine/search.py"),
            "selected_search_py": sha256_path(selected / "pynicotine/search.py"),
            "baseline_gui_search_py": sha256_path(
                baseline / "pynicotine/gtkgui/search.py"
            ),
            "selected_gui_search_py": sha256_path(
                selected / "pynicotine/gtkgui/search.py"
            ),
            "research_patch": sha256_path(PATCH),
        }

    expectation_passed = sum(bool(row["expectation_match"]) for row in test_rows)
    compile_passed = sum(row["status"] == "pass" for row in compile_matrix)
    invariant_passed = sum(row["status"] == "pass" for row in invariants)
    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "source_bundle": {
            "selected_basename": source_zip.name,
            "sha256": inspection.sha256,
            "expected_sha256": EXPECTED_SOURCE_SHA256,
            "status": inspection.status,
            "candidate_count": len(inspections),
        },
        "executable_source": {
            "lane": LANE,
            "ref": SOURCE_REF,
            "files_extracted": extracted_files,
        },
        "visible_master_context": {
            "head": VISIBLE_HEAD,
            "relation": (
                "visible head is six commits and eight changed files beyond the "
                "executable proxy; official current-source review confirms the "
                "same relevant token and GUI flow"
            ),
            "executable": False,
        },
        "source_invariants_passed": invariant_passed,
        "source_invariants_total": len(invariants),
        "test_expectations_passed": expectation_passed,
        "test_expectations_total": len(test_rows),
        "classified_runs": classified_runs,
        "compile_checks_passed": compile_passed,
        "compile_checks_total": len(compile_matrix),
        "upstream_units": units,
        "patch_application": patch_result,
        "critical_hashes": critical_hashes,
        "selected_patch": (
            "maintainer_artifacts/search-again-01/"
            "master-search-again-self-token.patch"
        ),
        "selected_scope": "self-user resend token bookkeeping only",
        "unselected_scope": "Search Again refresh and request-epoch redesign",
        "security_route": "not applicable; ordinary low-severity correctness",
        "errors": errors,
    }

    if args.write_data:
        OUTPUT_JSON.parent.mkdir(exist_ok=True)
        OUTPUT_JSON.write_text(canonical(result), encoding="utf-8")
        write_csv(OUTPUT_INVARIANTS, invariants)
        write_csv(OUTPUT_TESTS, test_rows)
        write_csv(OUTPUT_COMPILE, compile_matrix)

    print(canonical(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
