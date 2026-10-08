#!/usr/bin/env python3
"""Exact-current PB-01 behavior, compatibility, and policy-disposition gate.

Research-only.  The gate distinguishes observed behavior from desired policy,
runs the superseded rev0038 blanket guard as a counterexample, and runs a
narrower origin-aware experiment without selecting it for upstream use.
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

REVISION = "rev0074"
LANE = "github-branch-3.3.x"
EXPECTED_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
ARTIFACTS = ROOT / "maintainer_artifacts/pb01"
TESTS = {
    "current-behavior": ARTIFACTS / "test_pb01_current_behavior_witness.py",
    "race-compatibility": ARTIFACTS / "test_pb01_race_compatibility_controls.py",
    "rev0038-split-counterexample": ARTIFACTS / "test_pb01_rev0038_split_counterexample.py",
    "origin-aware-experiment": ARTIFACTS / "test_pb01_origin_aware_experiment.py",
}
PATCHERS = {
    "rev0038-blanket-guard": ROOT / "tools/apply_pb01_primary_guard_patch_rev0038.py",
    "origin-aware-experiment": ROOT / "tools/apply_pb01_origin_aware_patch_rev0074.py",
}
# expected (passed, failed) by source state and role
EXPECTED = {
    "baseline": {
        "current-behavior": (2, 0),
        "race-compatibility": (1, 0),
        "rev0038-split-counterexample": (0, 1),
        "origin-aware-experiment": (2, 1),
    },
    "rev0038-blanket-guard": {
        "current-behavior": (0, 2),
        "race-compatibility": (0, 1),
        "rev0038-split-counterexample": (1, 0),
        "origin-aware-experiment": (1, 2),
    },
    "origin-aware-experiment": {
        "current-behavior": (1, 1),
        "race-compatibility": (1, 0),
        "rev0038-split-counterexample": (0, 1),
        "origin-aware-experiment": (3, 0),
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


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command, cwd=cwd, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True,
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
        return subprocess.CompletedProcess(command, 124, (stdout or "") + f"\n[{REVISION} timeout]\n")


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


def source_invariants(source: Path) -> list[dict[str, Any]]:
    code = (source / "pynicotine/slskproto.py").read_text(encoding="utf-8")
    protocol = (source / "doc/SLSKPROTOCOL.md").read_text(encoding="utf-8")
    news = (source / "NEWS.md").read_text(encoding="utf-8")
    checks = [
        ("direct PeerInit invokes replacement", "self._replace_existing_connection(init)" in code),
        ("replacement migrates outgoing queue", "init.outgoing_msgs = prev_init.outgoing_msgs" in code),
        ("valid indirect secondary may coexist with direct primary", "some clients may send a message over" in code),
        ("post-init data promotes its socket", "promoting to primary connection" in code and "init.sock = conn.sock" in code),
        ("modern protocol documents direct and indirect race", "Modern Peer Connection Message Order" in protocol and "ConnectToPeer" in protocol and "GetPeerAddress" in protocol),
        ("PeerInit token is currently ignored", bool(re.search(r"token\s+is always zero and ignored today", protocol, re.I))),
        ("issue 2829 is in release history", "#2829" in news and "Browse Files" in news),
    ]
    return [{"invariant": label, "observed": observed, "status": "pass" if observed else "fail"} for label, observed in checks]


def apply_experiment(source: Path, patcher: Path, runtime: Path, state: str) -> dict[str, Any]:
    proc = run([sys.executable, str(patcher), str(source)], cwd=ROOT, timeout=60)
    (runtime / f"apply-{state}.txt").write_text(proc.stdout, encoding="utf-8")
    return {
        "state": state,
        "artifact": str(patcher.relative_to(ROOT)),
        "sha256": sha256_path(patcher),
        "observed_rc": proc.returncode,
        "status": "pass" if proc.returncode == 0 else "fail",
        "selection": "superseded-experiment" if state.startswith("rev0038") else "narrow-research-experiment-not-selected",
    }


def run_test(source: Path, test: Path, runtime: Path, state: str, role: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"env-{state}-{role}")
    proc = run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", str(test)],
        cwd=cwd, env=env, timeout=120,
    )
    (runtime / f"{state}-{role}.txt").write_text(proc.stdout, encoding="utf-8")
    observed = counts(proc.stdout)
    expected_passed, expected_failed = EXPECTED[state][role]
    ok = observed["passed"] == expected_passed and observed["failed"] == expected_failed
    return {
        "state": state,
        "role": role,
        "test_file": str(test.relative_to(ROOT)),
        "expected_passed": expected_passed,
        "expected_failed": expected_failed,
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        **observed,
        "expectation_status": "pass" if ok else "fail",
    }


def run_units(source: Path, runtime: Path, state: str) -> dict[str, Any]:
    """Run the native unit suite without the process-group wrapper.

    Pytest's own teardown occasionally left the generic pipe wrapper waiting after
    the child had exited.  A direct, bounded subprocess keeps this validation lane
    independent from the role-matrix runner and avoids misclassifying harness
    lifecycle noise as an upstream test failure.
    """
    env, cwd = isolated_env(source, runtime / f"unit-env-{state}")
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(source / UNIT_TEST)]
    msgfmt_available = shutil.which("msgfmt") is not None
    if not msgfmt_available:
        command.extend(["--ignore", str(source / UNIT_TEST / "test_i18n.py")])
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=90,
            check=False,
        )
        output = proc.stdout or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        output += f"\n[{REVISION} upstream-unit timeout]\n"
        returncode = 124
    (runtime / f"upstream-unit-{state}.txt").write_text(output, encoding="utf-8")
    return {
        "state": state,
        "observed_rc": returncode,
        "summary": summary_line(output),
        **counts(output),
        "status": "pass" if returncode == 0 else "fail",
        "msgfmt_available": msgfmt_available,
        "i18n_excluded": not msgfmt_available,
    }


def artifact_metrics() -> dict[str, Any]:
    archive = ROOT / "docs/archive/rev0073-active-pb01"
    old = [archive / "test_peer_connection_primary_election_reproducer.py", archive / "test_peer_connection_primary_election_fixed_regression.py"]
    new = sorted(ARTIFACTS.glob("*.py"))
    def measure(paths: list[Path]) -> dict[str, int]:
        paths = [path for path in paths if path.is_file()]
        lines = [line for path in paths for line in path.read_text(encoding="utf-8").splitlines()]
        return {"files": len(paths), "lines": len(lines), "bytes": sum(path.stat().st_size for path in paths), "lines_over_100": sum(len(line) > 100 for line in lines)}
    before, after = measure(old), measure(new)
    return {
        "archived_originals": before,
        "active_classified_harness": after,
        "byte_delta": after["bytes"] - before["bytes"],
        "line_delta": after["lines"] - before["lines"],
        "interpretation": "duplicated fixtures were centralized while four test roles became explicit",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence/rev0074-pb01-runtime"))
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
    if source_info.status != "pass": errors.append("source bundle contract")
    if lane_head != EXPECTED_REF: errors.append(f"lane head {lane_head} != {EXPECTED_REF}")
    for path in (*TESTS.values(), *PATCHERS.values(), ARTIFACTS / "pb01_harness.py"):
        if not path.is_file(): errors.append(f"missing artifact: {path.relative_to(ROOT)}")

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    temp_roots: list[Path] = []
    states: dict[str, Path] = {}
    patch_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []
    unit_rows: list[dict[str, Any]] = []
    compile_rows: list[dict[str, Any]] = []
    invariants: list[dict[str, Any]] = []
    entry_counts: dict[str, int] = {}
    try:
        for state in EXPECTED:
            destination = Path(tempfile.mkdtemp(prefix=f"rev0074-pb01-{state}-"))
            temp_roots.append(destination)
            states[state] = destination
            entry_counts[state] = safe_extract_lane(source_zip, destination)
        invariants = source_invariants(states["baseline"])
        patch_rows = [
            apply_experiment(states["rev0038-blanket-guard"], PATCHERS["rev0038-blanket-guard"], out_dir, "rev0038-blanket-guard"),
            apply_experiment(states["origin-aware-experiment"], PATCHERS["origin-aware-experiment"], out_dir, "origin-aware-experiment"),
        ]
        if any(row["status"] != "pass" for row in patch_rows): errors.append("patch application")

        test_jobs = [
            (state, source, role, test)
            for state, source in states.items()
            for role, test in TESTS.items()
        ]
        with ThreadPoolExecutor(max_workers=6) as executor:
            test_rows = list(executor.map(
                lambda item: run_test(
                    item[1], item[3], out_dir, item[0], item[2]
                ),
                test_jobs,
            ))
        for row in test_rows:
            if row["expectation_status"] != "pass":
                errors.append(
                    f"matrix mismatch: {row['state']}/{row['role']}"
                )

        for state, source in states.items():
            path = source / "pynicotine/slskproto.py"
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
                compile_rows.append({"state": state, "status": "pass", "error": ""})
            except SyntaxError as exc:
                compile_rows.append({"state": state, "status": "fail", "error": str(exc)})
                errors.append(f"compile: {state}")

        with ThreadPoolExecutor(max_workers=3) as executor:
            unit_rows = list(executor.map(
                lambda item: run_units(item[1], out_dir, item[0]),
                states.items(),
            ))
        if any(row["status"] != "pass" for row in unit_rows): errors.append("upstream units")
        unit_parity = len({(row["passed"], row["skipped"]) for row in unit_rows}) == 1
        if not unit_parity: errors.append("upstream unit parity")
    finally:
        for path in temp_roots: shutil.rmtree(path, ignore_errors=True)

    if any(row["status"] != "pass" for row in invariants): errors.append("source invariants")
    reachability_rows = [
        {"claim": "PB-01A/U-168 direct replacement", "observed": True, "reachable_input": "incoming PeerInit claims existing username/type", "missing_proof": "no authenticated identity or safe generation/election policy", "disposition": "open-correctness-and-protocol-hardening-research"},
        {"claim": "PB-01B/U-176 secondary promotion", "observed": True, "reachable_input": "valid locally-tokened direct/indirect race", "missing_proof": "arbitrary attacker-created shared-init secondary not demonstrated", "disposition": "retired-as-defect-on-current-evidence"},
        {"claim": "rev0038 blanket first-established-wins guard", "observed": True, "reachable_input": "prototype policy", "missing_proof": "can split peers across opposite race legs and suppress documented failover", "disposition": "superseded-not-selected"},
        {"claim": "rev0074 origin-aware guard", "observed": True, "reachable_input": "prototype distinguishes outgoing indirect response from other primaries", "missing_proof": "first claimant remains unauthenticated; stale/reconnect behavior lacks integration proof", "disposition": "narrow-research-experiment-not-selected"},
    ]
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
        "upstream_units": unit_rows,
        "upstream_unit_parity": len({(row["passed"], row["skipped"]) for row in unit_rows}) == 1 if unit_rows else False,
        "experiments": patch_rows,
        "artifact_refactor": artifact_metrics(),
        "pb01a_u168_disposition": "behavior confirmed; keep as public correctness/protocol-hardening research with no selected patch",
        "pb01b_u176_disposition": "retired as a defect; current reachable path is intentional compatibility/failover behavior",
        "selected_patch": None,
        "private_security_route": "not supported by current evidence",
        "errors": errors,
    }
    if args.write_data:
        write_json(ROOT / "data/rev0074_pb01_disposition_summary.json", summary)
        write_json(ROOT / "data/rev0074_pb01_test_matrix.json", test_rows)
        write_csv(ROOT / "data/rev0074_pb01_test_matrix.csv", test_rows)
        write_json(ROOT / "data/rev0074_pb01_source_invariants.json", invariants)
        write_csv(ROOT / "data/rev0074_pb01_source_invariants.csv", invariants)
        write_json(ROOT / "data/rev0074_pb01_reachability_matrix.json", reachability_rows)
        write_csv(ROOT / "data/rev0074_pb01_reachability_matrix.csv", reachability_rows)
        write_json(ROOT / "data/rev0074_pb01_compile_matrix.json", compile_rows)
        write_csv(ROOT / "data/rev0074_pb01_compile_matrix.csv", compile_rows)
        write_json(ROOT / "data/rev0074_pb01_artifact_refactor.json", summary["artifact_refactor"])
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
