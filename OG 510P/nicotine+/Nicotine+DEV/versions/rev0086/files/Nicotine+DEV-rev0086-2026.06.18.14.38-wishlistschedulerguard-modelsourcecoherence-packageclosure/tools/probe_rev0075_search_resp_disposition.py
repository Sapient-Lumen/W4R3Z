#!/usr/bin/env python3
"""Exact-current SEARCH-RESP-01A behavior and identity-boundary gate.

Research-only. The gate separates parser/token acceptance, request-scope
consistency, the identity value supplied by PeerInit, token reachability, and
security impact. It executes the historical rev0039 guard as an experiment but
does not select it for upstream use.
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

REVISION = "rev0075"
LANE = "github-branch-3.3.x"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
ARTIFACTS = ROOT / "maintainer_artifacts/search-resp-01"
PATCHER = ROOT / "tools/apply_search_resp_user_scope_patch_rev0039.py"
TESTS = {
    "current-behavior": ARTIFACTS / "test_search_resp_current_behavior.py",
    "rev0039-policy": ARTIFACTS / "test_search_resp_rev0039_policy.py",
    "identity-counterexample": ARTIFACTS / "test_search_resp_identity_counterexample.py",
    "token-model": ARTIFACTS / "test_search_resp_token_model.py",
}
# Expected (passed, failed) for each evidentiary role in each source state.
EXPECTED = {
    "baseline": {
        "current-behavior": (2, 0),
        "rev0039-policy": (2, 2),
        "identity-counterexample": (3, 0),
        "token-model": (2, 0),
    },
    "rev0039-user-scope-guard": {
        "current-behavior": (1, 1),
        "rev0039-policy": (4, 0),
        "identity-counterexample": (3, 0),
        "token-model": (2, 0),
    },
}
UNIT_TEST = "pynicotine/tests/unit"


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
            if relative == Path(".git"):
                continue
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
    locations = {
        "HOME": runtime / "home",
        "XDG_CONFIG_HOME": runtime / "xdg-config",
        "XDG_DATA_HOME": runtime / "xdg-data",
        "XDG_CACHE_HOME": runtime / "xdg-cache",
        "TMPDIR": runtime / "tmp",
    }
    for path in locations.values():
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in locations.items()})
    env.update({
        "NICOTINE_SOURCE": str(source),
        "PYTHONPATH": os.pathsep.join((str(ARTIFACTS), str(source))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    })
    return env, cwd


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 180,
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
            command, 124, (stdout or "") + f"\n[{REVISION} timeout]\n"
        )


def summary_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b(?:failed|passed|skipped)\b", line) and " in " in line:
            return line
    return lines[-1] if lines else ""


def counts(output: str) -> dict[str, int]:
    result = {"failed": 0, "passed": 0, "skipped": 0}
    for number, label in re.findall(r"(\d+) (failed|passed|skipped)", summary_line(output)):
        result[label] = int(number)
    return result


def function_slice(text: str, function_name: str) -> str:
    match = re.search(rf"^    def {re.escape(function_name)}\(.*?(?=^    def |\Z)", text, re.M | re.S)
    return match.group(0) if match else ""


def class_slice(text: str, class_name: str) -> str:
    match = re.search(rf"^class {re.escape(class_name)}\b.*?(?=^class |\Z)", text, re.M | re.S)
    return match.group(0) if match else ""


def source_invariants(source: Path) -> list[dict[str, Any]]:
    search_code = (source / "pynicotine/search.py").read_text(encoding="utf-8")
    proto_code = (source / "pynicotine/slskproto.py").read_text(encoding="utf-8")
    messages_code = (source / "pynicotine/slskmessages.py").read_text(encoding="utf-8")
    protocol = (source / "doc/SLSKPROTOCOL.md").read_text(encoding="utf-8")
    handler = function_slice(search_code, "_file_search_response")
    peer_search = function_slice(search_code, "do_peer_search")
    peer_input = function_slice(proto_code, "_process_peer_input")
    unpacker = function_slice(proto_code, "_unpack_network_message")
    peer_init = class_slice(messages_code, "PeerInit")
    response = class_slice(messages_code, "FileSearchResponse")
    checks = [
        (
            "user-search request retains intended usernames",
            'self.users = users' in search_code and 'mode == "user"' in search_code,
        ),
        (
            "each intended username receives the same UserSearch token",
            "for username in users:" in peer_search
            and "UserSearch(username, self.token, text)" in peer_search,
        ),
        (
            "current handler admits by token/search/filter without user-set comparison",
            "msg.token not in SEARCH_TOKENS_ALLOWED" in handler
            and "self.searches.get(msg.token)" in handler
            and 'search.mode == "user"' not in handler
            and "search.users" not in handler,
        ),
        (
            "peer-message source username comes from connection PeerInit target_user",
            "username=conn.init.target_user" in peer_input
            and "msg.username = username" in unpacker,
        ),
        (
            "incoming direct PeerInit target_user defaults to wire init_user",
            "self.target_user = self.init_user" in peer_init,
        ),
        (
            "response payload username is distinct from connection source username",
            '"search_username"' in response
            and "self.pack_string(self.search_username)" in response
            and "msg.username = username" in unpacker,
        ),
        (
            "search token starts in reduced random range and then increments linearly",
            "return randint(0, UINT32_LIMIT // 1000)" in messages_code
            and "token += 1" in messages_code,
        ),
        (
            "server-bound username/token connection verification is obsolete",
            "SendConnectToken" in protocol
            and "reject spoofed connection attempts" in protocol
            and "rendered the message unusable" in protocol,
        ),
    ]
    return [
        {"invariant": label, "observed": bool(observed), "status": "pass" if observed else "fail"}
        for label, observed in checks
    ]


def apply_experiment(source: Path, runtime: Path) -> dict[str, Any]:
    proc = run([sys.executable, str(PATCHER), str(source)], cwd=ROOT, timeout=60)
    (runtime / "apply-rev0039-user-scope-guard.txt").write_text(proc.stdout, encoding="utf-8")
    return {
        "state": "rev0039-user-scope-guard",
        "artifact": str(PATCHER.relative_to(ROOT)),
        "sha256": sha256_path(PATCHER),
        "observed_rc": proc.returncode,
        "output": proc.stdout.strip(),
        "status": "pass" if proc.returncode == 0 else "fail",
        "selection": "historical-defense-in-depth-experiment-not-selected",
    }


def run_test(source: Path, test: Path, runtime: Path, state: str, role: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"env-{state}-{role}")
    proc = run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", str(test)],
        cwd=cwd,
        env=env,
        timeout=120,
    )
    (runtime / f"{state}-{role}.txt").write_text(proc.stdout, encoding="utf-8")
    observed = counts(proc.stdout)
    expected_passed, expected_failed = EXPECTED[state][role]
    expected_rc = 0 if expected_failed == 0 else 1
    ok = (
        observed["passed"] == expected_passed
        and observed["failed"] == expected_failed
        and proc.returncode == expected_rc
    )
    return {
        "state": state,
        "role": role,
        "test_file": str(test.relative_to(ROOT)),
        "expected_passed": expected_passed,
        "expected_failed": expected_failed,
        "expected_rc": expected_rc,
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        **observed,
        "expectation_status": "pass" if ok else "fail",
    }


def run_units(source: Path, runtime: Path, state: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"unit-env-{state}")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(source / UNIT_TEST),
    ]
    msgfmt_available = shutil.which("msgfmt") is not None
    if not msgfmt_available:
        command.extend(["--ignore", str(source / UNIT_TEST / "test_i18n.py")])
    proc = run(command, cwd=cwd, env=env, timeout=120)
    (runtime / f"upstream-unit-{state}.txt").write_text(proc.stdout, encoding="utf-8")
    observed = counts(proc.stdout)
    return {
        "state": state,
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        **observed,
        "status": "pass" if proc.returncode == 0 else "fail",
        "msgfmt_available": msgfmt_available,
        "i18n_excluded": not msgfmt_available,
    }


def compile_state(source: Path, state: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    paths = [source / "pynicotine/search.py", source / "pynicotine/slskmessages.py", source / "pynicotine/slskproto.py"]
    for path in paths:
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, error = "pass", ""
        except Exception as exc:  # pragma: no cover - gate reporting
            status, error = "fail", f"{type(exc).__name__}: {exc}"
        rows.append({"state": state, "path": str(path.relative_to(source)), "status": status, "error": error})
    return rows


def artifact_metrics() -> dict[str, Any]:
    archive = ROOT / "docs/archive/rev0074-active-search-resp-01"
    old = [
        archive / "test_search_response_scope_and_parse_order_reproducer.py",
        archive / "test_search_response_user_scope_fixed_regression.py",
    ]
    new = [ARTIFACTS / "search_resp_harness.py", *TESTS.values()]

    def measure(paths: list[Path]) -> dict[str, int]:
        existing = [path for path in paths if path.is_file()]
        lines = [line for path in existing for line in path.read_text(encoding="utf-8").splitlines()]
        return {
            "files": len(existing),
            "lines": len(lines),
            "bytes": sum(path.stat().st_size for path in existing),
            "lines_over_100": sum(len(line) > 100 for line in lines),
        }

    before, after = measure(old), measure(new)
    return {
        "archived_originals": before,
        "active_role_classified_harness": after,
        "byte_delta": after["bytes"] - before["bytes"],
        "line_delta": after["lines"] - before["lines"],
        "interpretation": "shared fixtures replace policy-mixed duplicate modules; evidence roles are explicit",
    }


def reachability_matrix() -> list[dict[str, Any]]:
    return [
        {
            "layer": "parser admission",
            "observed": True,
            "evidence": "FileSearchResponse token gate and exact-current role tests",
            "missing_proof": "none for token-valid parser acceptance",
            "disposition": "confirmed",
        },
        {
            "layer": "request-scope consistency",
            "observed": True,
            "evidence": "off-request connection username remains accepted for a user-mode search",
            "missing_proof": "compatibility value and user-visible harm not established",
            "disposition": "confirmed local consistency gap",
        },
        {
            "layer": "rev0039 guard mechanics",
            "observed": True,
            "evidence": "guard rejects off-set names and preserves expected names in isolated tests",
            "missing_proof": "mixed-client and username-canonicalization compatibility",
            "disposition": "plausible defense-in-depth experiment",
        },
        {
            "layer": "source identity",
            "observed": False,
            "evidence": "guard compares msg.username populated from wire PeerInit target_user",
            "missing_proof": "server-bound or cryptographic binding between socket and claimed username",
            "disposition": "not an authentication boundary",
        },
        {
            "layer": "token reachability",
            "observed": "partial",
            "evidence": "reduced initial range and sequential allocation are confirmed",
            "missing_proof": "practical observation/guessing, timing, and successful unrelated-peer injection",
            "disposition": "bounded model only; no exploit claim",
        },
        {
            "layer": "security impact",
            "observed": False,
            "evidence": "no end-to-end unauthorized result injection or durable harm demonstrated",
            "missing_proof": "capability, reliability, impact, and distinction from arbitrary results by the requested peer",
            "disposition": "private security route not supported by current evidence",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence/rev0075-search-resp-runtime"))
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
    for path in (*TESTS.values(), PATCHER, ARTIFACTS / "search_resp_harness.py"):
        if not path.is_file():
            errors.append(f"missing artifact: {path.relative_to(ROOT)}")

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    temp_roots: list[Path] = []
    states: dict[str, Path] = {}
    entry_counts: dict[str, int] = {}
    test_rows: list[dict[str, Any]] = []
    unit_rows: list[dict[str, Any]] = []
    compile_rows: list[dict[str, str]] = []
    invariants: list[dict[str, Any]] = []
    experiment: dict[str, Any] = {}
    try:
        for state in EXPECTED:
            destination = Path(tempfile.mkdtemp(prefix=f"rev0075-search-resp-{state}-"))
            temp_roots.append(destination)
            states[state] = destination
            entry_counts[state] = safe_extract_lane(source_zip, destination)

        invariants = source_invariants(states["baseline"])
        experiment = apply_experiment(states["rev0039-user-scope-guard"], out_dir)
        if experiment["status"] != "pass":
            errors.append("patch application")

        test_jobs = [
            (state, source, role, test)
            for state, source in states.items()
            for role, test in TESTS.items()
        ]
        with ThreadPoolExecutor(max_workers=8) as executor:
            test_rows = list(executor.map(
                lambda item: run_test(item[1], item[3], out_dir, item[0], item[2]),
                test_jobs,
            ))
        for row in test_rows:
            if row["expectation_status"] != "pass":
                errors.append(f"matrix mismatch: {row['state']}/{row['role']}")

        for state, source in states.items():
            compile_rows.extend(compile_state(source, state))
        if any(row["status"] != "pass" for row in compile_rows):
            errors.append("source compile")

        with ThreadPoolExecutor(max_workers=2) as executor:
            unit_rows = list(executor.map(
                lambda item: run_units(item[1], out_dir, item[0]),
                states.items(),
            ))
        if any(row["status"] != "pass" for row in unit_rows):
            errors.append("upstream units")
        unit_parity = len({(row["passed"], row["failed"], row["skipped"]) for row in unit_rows}) == 1
        if not unit_parity:
            errors.append("upstream unit parity")
    finally:
        for path in temp_roots:
            shutil.rmtree(path, ignore_errors=True)

    if any(row["status"] != "pass" for row in invariants):
        errors.append("source invariants")
    reachability_rows = reachability_matrix()
    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "source_zip": str(source_zip),
        "source_zip_sha256": source_info.sha256,
        "expected_source_zip_sha256": EXPECTED_SOURCE_SHA256,
        "source_candidates": [row.path for row in candidates],
        "lane": LANE,
        "expected_ref": EXPECTED_REF,
        "observed_ref": lane_head,
        "exact_current_ref_match": lane_head == EXPECTED_REF,
        "extracted_entries": entry_counts,
        "source_invariants_passed": sum(row["status"] == "pass" for row in invariants),
        "source_invariants_total": len(invariants),
        "test_expectations_passed": sum(row["expectation_status"] == "pass" for row in test_rows),
        "test_expectations_total": len(test_rows),
        "compile_checks_passed": sum(row["status"] == "pass" for row in compile_rows),
        "compile_checks_total": len(compile_rows),
        "upstream_units": unit_rows,
        "upstream_unit_parity": len({(row["passed"], row["failed"], row["skipped"]) for row in unit_rows}) == 1 if unit_rows else False,
        "experiment": experiment,
        "artifact_refactor": artifact_metrics(),
        "reachability_layers": reachability_rows,
        "disposition": "confirmed-local-consistency-gap; open defense-in-depth research",
        "security_route": "not supported by current evidence",
        "selected_patch": None,
        "historical_rev0039_status": "superseded as a production/security disposition; retained as an unselected experiment",
        "errors": sorted(set(errors)),
    }

    if args.write_data:
        write_json(ROOT / "data/rev0075_search_resp_disposition_summary.json", summary)
        write_csv(ROOT / "data/rev0075_search_resp_test_matrix.csv", test_rows)
        write_json(ROOT / "data/rev0075_search_resp_test_matrix.json", test_rows)
        write_csv(ROOT / "data/rev0075_search_resp_source_invariants.csv", invariants)
        write_json(ROOT / "data/rev0075_search_resp_source_invariants.json", invariants)
        write_csv(ROOT / "data/rev0075_search_resp_reachability_matrix.csv", reachability_rows)
        write_json(ROOT / "data/rev0075_search_resp_reachability_matrix.json", reachability_rows)
        write_csv(ROOT / "data/rev0075_search_resp_compile_matrix.csv", compile_rows)
        write_json(ROOT / "data/rev0075_search_resp_compile_matrix.json", compile_rows)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
