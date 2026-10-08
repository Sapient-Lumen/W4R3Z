#!/usr/bin/env python3
"""Audit SEARCH-RESP-01B across exact 3.3.x and a resend-capable master lane.

Research-only. The gate distinguishes recipient selection, a claimed connection
username, local share authorization, and the lifetime of a repeated search.
The historical rev0040 patch is executed as a hypothesis, not selected.
"""
from __future__ import annotations

import argparse
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
import tempfile
import tarfile
import zipfile
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

REVISION = "rev0076"
LANES = {
    "supported-3.3.x": ("github-branch-3.3.x", "98089ac233aa57786e8dbdc48123f6ac1c4767d8"),
    "bundled-master": ("github-branch-master", "f4e17d59783dbc48ea31d2e899a681e2dd1ed500"),
}
ARTIFACTS = ROOT / "maintainer_artifacts/search-resp-01"
PATCHER = ROOT / "tools/apply_search_resp_buddy_components_rev0076.py"
UNIT_TEST = "pynicotine/tests/unit"

CASES_33 = {
    "current-behavior": (
        "test_search_resp_buddy_current_behavior.py",
        (
            "test_current_buddy_search_does_not_store_recipient_snapshot",
            "test_current_handler_accepts_off_snapshot_connection_name",
            "test_current_handler_preserves_expected_connection_name",
        ),
    ),
    "rev0040-policy": (
        "test_search_resp_buddy_rev0040_policy.py",
        (
            "test_off_snapshot_connection_name_is_rejected",
            "test_expected_connection_name_is_preserved",
            "test_empty_snapshot_rejects_closed",
            "test_initial_search_captures_and_sends_same_snapshot",
        ),
    ),
    "identity-counterexample": (
        "test_search_resp_buddy_identity_counterexample.py",
        (
            "test_expected_name_claimed_in_peerinit_passes_buddy_guard",
            "test_body_username_is_discarded_in_favor_of_connection_claim",
        ),
    ),
    "snapshot-presence": (
        "test_search_resp_buddy_snapshot_presence.py",
        (
            "test_absent_snapshot_remains_broad_source_compatible",
            "test_present_empty_snapshot_is_rejected_by_rev0040_guard",
        ),
    ),
}
CASES_MASTER = {
    "resend-epoch": (
        "test_search_resp_buddy_master_resend_epoch.py",
        (
            "test_resend_uses_current_buddy_list",
            "test_rev0040_resend_reuses_initial_snapshot",
        ),
    )
}
EXPECTED_PASS = {
    "supported-3.3.x-baseline": {
        "test_current_buddy_search_does_not_store_recipient_snapshot": True,
        "test_current_handler_accepts_off_snapshot_connection_name": True,
        "test_current_handler_preserves_expected_connection_name": True,
        "test_off_snapshot_connection_name_is_rejected": False,
        "test_expected_connection_name_is_preserved": True,
        "test_empty_snapshot_rejects_closed": False,
        "test_initial_search_captures_and_sends_same_snapshot": False,
        "test_expected_name_claimed_in_peerinit_passes_buddy_guard": True,
        "test_body_username_is_discarded_in_favor_of_connection_claim": True,
        "test_absent_snapshot_remains_broad_source_compatible": True,
        "test_present_empty_snapshot_is_rejected_by_rev0040_guard": False,
    },
    "supported-3.3.x-rev0040": {
        "test_current_buddy_search_does_not_store_recipient_snapshot": False,
        "test_current_handler_accepts_off_snapshot_connection_name": False,
        "test_current_handler_preserves_expected_connection_name": True,
        "test_off_snapshot_connection_name_is_rejected": True,
        "test_expected_connection_name_is_preserved": True,
        "test_empty_snapshot_rejects_closed": True,
        "test_initial_search_captures_and_sends_same_snapshot": True,
        "test_expected_name_claimed_in_peerinit_passes_buddy_guard": True,
        "test_body_username_is_discarded_in_favor_of_connection_claim": True,
        "test_absent_snapshot_remains_broad_source_compatible": True,
        "test_present_empty_snapshot_is_rejected_by_rev0040_guard": True,
    },
    "bundled-master-baseline": {
        "test_resend_uses_current_buddy_list": True,
        "test_rev0040_resend_reuses_initial_snapshot": False,
    },
    "bundled-master-rev0040": {
        "test_resend_uses_current_buddy_list": False,
        "test_rev0040_resend_reuses_initial_snapshot": True,
    },
}


def sha256_path(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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
    """Extract a pinned nested tarball rather than thousands of outer-ZIP entries."""
    archive_prefix = SOURCE_PREFIX.rsplit("source-trees/", 1)[0] + "archives/"
    archive_name = archive_prefix + f"{lane}.tar.gz"
    with zipfile.ZipFile(source_zip) as outer:
        payload = outer.read(archive_name)
    count = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as inner:
        members = inner.getmembers()
        roots = {Path(member.name).parts[0] for member in members if member.name}
        if len(roots) != 1:
            raise RuntimeError(f"expected one tar root for {lane}, found {sorted(roots)}")
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
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), member.linkname))
                if not resolved.startswith(root + "/"):
                    raise RuntimeError(f"symlink escapes tar root: {member.name} -> {member.linkname}")
                source_member = inner.getmember(resolved)
            if not source_member.isfile():
                raise RuntimeError(f"unsupported tar entry: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = inner.extractfile(source_member)
            if source is None:
                raise RuntimeError(f"cannot read tar entry: {member.name}")
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


def run(command: list[str], *, cwd: Path, env=None, timeout=180) -> subprocess.CompletedProcess[str]:
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
        return subprocess.CompletedProcess(command, 124, (stdout or "") + "\n[timeout]\n")


def summary_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b(?:failed|passed|skipped)\b", line) and " in " in line:
            return line
    return lines[-1] if lines else ""


def function_slice(text: str, name: str) -> str:
    match = re.search(rf"^    def {re.escape(name)}\(.*?(?=^    def |\Z)", text, re.M | re.S)
    return match.group(0) if match else ""


def class_slice(text: str, name: str) -> str:
    match = re.search(rf"^class {re.escape(name)}\b.*?(?=^class |\Z)", text, re.M | re.S)
    return match.group(0) if match else ""


def source_invariants(source_33: Path, source_master: Path) -> list[dict[str, Any]]:
    s33 = (source_33 / "pynicotine/search.py").read_text(encoding="utf-8")
    sm = (source_master / "pynicotine/search.py").read_text(encoding="utf-8")
    gui = (source_master / "pynicotine/gtkgui/search.py").read_text(encoding="utf-8")
    proto = (source_33 / "pynicotine/slskproto.py").read_text(encoding="utf-8")
    messages = (source_33 / "pynicotine/slskmessages.py").read_text(encoding="utf-8")
    process33 = function_slice(s33, "process_search_term")
    sender33 = function_slice(s33, "do_buddies_search")
    response33 = function_slice(s33, "_file_search_response")
    process_request33 = function_slice(s33, "_process_search_request")
    sender_master = function_slice(sm, "_send_buddies_search_request")
    send_master = function_slice(sm, "send_search_request")
    response_master = function_slice(sm, "_file_search_response")
    peer_input = function_slice(proto, "_process_peer_input")
    unpacker = function_slice(proto, "_unpack_network_message")
    peer_init = class_slice(messages, "PeerInit")
    file_response = class_slice(messages, "FileSearchResponse")
    checks = [
        ("3.3.x buddy term processing leaves users unset", "users = tuple(core.buddies.users)" not in process33),
        ("3.3.x buddy sender reads live core buddy list", "for username in core.buddies.users:" in sender33),
        ("3.3.x response admission has no buddy/user-set comparison", "search.users" not in response33 and 'search.mode == "buddies"' not in response33),
        ("connection username is assigned from PeerInit target_user", "username=conn.init.target_user" in peer_input and "msg.username = username" in unpacker),
        ("incoming direct PeerInit target_user begins as wire init_user", "self.target_user = self.init_user" in peer_init),
        ("FileSearchResponse body username is not connection identity", '"search_username"' in file_response and "msg.username = username" in unpacker),
        ("incoming response handler does not authorize local buddy/trusted shares", "PermissionLevel" not in response33 and "share_dbs" not in response33),
        ("local share permission is evaluated on incoming search requests elsewhere", "check_user_permission(username)" in process_request33),
        ("master Search Again dispatch can reuse an existing search token", "self.searches.get(token)" in send_master and "self._send_buddies_search_request(search)" in send_master),
        ("master buddy sender reads live buddy list on each send", "for username in core.buddies.users:" in sender_master),
        ("master GUI Search Again calls send_search_request with existing token", "core.search.send_search_request(self.token)" in gui),
        ("master response admission also lacks buddy recipient comparison", "search.users" not in response_master and 'search.mode == "buddies"' not in response_master),
    ]
    return [{"invariant": label, "observed": bool(ok), "status": "pass" if ok else "fail"} for label, ok in checks]


def apply_patch(source: Path, runtime: Path, state: str) -> dict[str, Any]:
    proc = run([sys.executable, str(PATCHER), str(source)], cwd=ROOT, timeout=60)
    (runtime / f"apply-{state}.txt").write_text(proc.stdout, encoding="utf-8")
    return {
        "state": state,
        "artifact": str(PATCHER.relative_to(ROOT)),
        "sha256": sha256_path(PATCHER),
        "observed_rc": proc.returncode,
        "output": proc.stdout.strip(),
        "status": "pass" if proc.returncode == 0 else "fail",
        "selection": "historical hypothesis; not selected",
    }


def run_case(source: Path, runtime: Path, state: str, role: str, filename: str, test_name: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"env-{state}-{test_name}")
    test = ARTIFACTS / filename
    node = f"{test}::{test_name}"
    proc = run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", node],
        cwd=cwd,
        env=env,
        timeout=120,
    )
    (runtime / f"{state}-{test_name}.txt").write_text(proc.stdout, encoding="utf-8")
    observed_pass = proc.returncode == 0 and "1 passed" in summary_line(proc.stdout)
    observed_fail = proc.returncode == 1 and "1 failed" in summary_line(proc.stdout)
    expected_pass = EXPECTED_PASS[state][test_name]
    matched = observed_pass if expected_pass else observed_fail
    return {
        "state": state,
        "role": role,
        "test_file": str(test.relative_to(ROOT)),
        "test_name": test_name,
        "expected_outcome": "pass" if expected_pass else "fail",
        "observed_outcome": "pass" if observed_pass else "fail" if observed_fail else "error",
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        "expectation_status": "pass" if matched else "fail",
    }


def result_counts(output: str) -> dict[str, int]:
    counts = {"passed": 0, "failed": 0, "skipped": 0}
    for number, label in re.findall(r"(\d+) (passed|failed|skipped)", summary_line(output)):
        counts[label] = int(number)
    return counts


def run_units(source: Path, runtime: Path, state: str) -> dict[str, Any]:
    env, cwd = isolated_env(source, runtime / f"unit-{state}")
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(source / UNIT_TEST)]
    msgfmt_available = shutil.which("msgfmt") is not None
    if not msgfmt_available:
        command.extend(["--ignore", str(source / UNIT_TEST / "test_i18n.py")])
    proc = run(command, cwd=cwd, env=env, timeout=180)
    (runtime / f"upstream-unit-{state}.txt").write_text(proc.stdout, encoding="utf-8")
    return {
        "state": state,
        "observed_rc": proc.returncode,
        "summary": summary_line(proc.stdout),
        **result_counts(proc.stdout),
        "status": "pass" if proc.returncode == 0 else "fail",
        "msgfmt_available": msgfmt_available,
        "i18n_excluded": not msgfmt_available,
    }


def compile_rows(states: dict[str, Path]) -> list[dict[str, str]]:
    rows = []
    for state, source in states.items():
        path = source / "pynicotine/search.py"
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, error = "pass", ""
        except Exception as exc:
            status, error = "fail", f"{type(exc).__name__}: {exc}"
        rows.append({"state": state, "path": "pynicotine/search.py", "status": status, "error": error})
    for path in sorted(ARTIFACTS.glob("*buddy*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            status, error = "pass", ""
        except Exception as exc:
            status, error = "fail", f"{type(exc).__name__}: {exc}"
        rows.append({"state": "revision-artifact", "path": str(path.relative_to(ROOT)), "status": status, "error": error})
    return rows


def artifact_metrics() -> dict[str, Any]:
    old = [ROOT / "docs/archive/rev0075-active-search-resp-buddy/test_search_response_buddy_scope_fixed_regression.py"]
    new = [ARTIFACTS / "buddy_search_harness.py", *sorted(ARTIFACTS.glob("test_search_resp_buddy_*.py"))]
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
        "archived_monolith": before,
        "active_role_classified_suite": after,
        "line_delta": after["lines"] - before["lines"],
        "byte_delta": after["bytes"] - before["bytes"],
        "archive_sha256": sha256_path(old[0]) if old[0].is_file() else "",
        "interpretation": "fixtures are shared; current behavior, policy, identity, and resend epoch have separate roles",
    }


def claim_matrix() -> list[dict[str, Any]]:
    return [
        {"layer": "supported-branch behavior", "observed": True, "disposition": "confirmed", "evidence": "3.3.x source invariants and current-behavior tests"},
        {"layer": "rev0040 claimed-name filtering", "observed": True, "disposition": "mechanically effective only for present snapshots", "evidence": "off-snapshot, absent-snapshot, and empty-snapshot policy tests"},
        {"layer": "peer identity", "observed": False, "disposition": "not an authentication boundary", "evidence": "expected username supplied in wire PeerInit passes"},
        {"layer": "local buddy/trusted share authorization", "observed": False, "disposition": "different incoming-request path", "evidence": "response handler never evaluates PermissionLevel or local share databases"},
        {"layer": "repeated-search epoch compatibility", "observed": True, "disposition": "rev0040 snapshot policy contradicted", "evidence": "master resend polarity test after buddy-list mutation"},
        {"layer": "practical unrelated-peer injection", "observed": False, "disposition": "not established", "evidence": "no token capability or end-to-end injection witness"},
        {"layer": "security impact", "observed": False, "disposition": "private security route unsupported", "evidence": "no authorization bypass, reliability, or material harm demonstrated"},
        {"layer": "patch selection", "observed": False, "disposition": "none selected", "evidence": "request-epoch semantics unresolved"},
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence/rev0076-search-resp-buddy-runtime"))
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        source_zip, candidates = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(json.dumps({"revision": REVISION, "status": "fail", "errors": [str(exc)]}, indent=2))
        return 1
    source_info = inspect_bundle(source_zip)
    observed_heads = {label: lane_head(source_zip, lane) for label, (lane, _ref) in LANES.items()}
    for label, (_lane, expected) in LANES.items():
        if observed_heads[label] != expected:
            errors.append(f"{label} head mismatch")
    if source_info.status != "pass":
        errors.append("source bundle contract")

    required = [PATCHER, ARTIFACTS / "buddy_search_harness.py"]
    for _role, (filename, _tests) in {**CASES_33, **CASES_MASTER}.items():
        required.append(ARTIFACTS / filename)
    for path in required:
        if not path.is_file():
            errors.append(f"missing artifact: {path.relative_to(ROOT)}")

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    temp_root = Path(tempfile.mkdtemp(prefix="rev0076-search-buddy-"))
    states: dict[str, Path] = {}
    entry_counts: dict[str, int] = {}
    experiments: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []
    units: list[dict[str, Any]] = []
    invariants: list[dict[str, Any]] = []
    compiles: list[dict[str, str]] = []
    try:
        for label, (lane, _ref) in LANES.items():
            baseline = temp_root / f"{label}-baseline"
            patched = temp_root / f"{label}-rev0040"
            baseline.mkdir()
            entry_counts[label] = safe_extract_lane(source_zip, lane, baseline)
            shutil.copytree(baseline, patched, dirs_exist_ok=True)
            states[f"{label}-baseline"] = baseline
            states[f"{label}-rev0040"] = patched
            experiments.append(apply_patch(patched, out_dir, f"{label}-rev0040"))

        invariants = source_invariants(states["supported-3.3.x-baseline"], states["bundled-master-baseline"])
        jobs = []
        for state in ("supported-3.3.x-baseline", "supported-3.3.x-rev0040"):
            for role, (filename, tests) in CASES_33.items():
                jobs.extend((states[state], out_dir, state, role, filename, test) for test in tests)
        for state in ("bundled-master-baseline", "bundled-master-rev0040"):
            for role, (filename, tests) in CASES_MASTER.items():
                jobs.extend((states[state], out_dir, state, role, filename, test) for test in tests)
        test_rows = [run_case(*item) for item in jobs]
        if any(row["expectation_status"] != "pass" for row in test_rows):
            errors.append("classified test matrix")

        compiles = compile_rows(states)
        if any(row["status"] != "pass" for row in compiles):
            errors.append("compile matrix")
        if any(row["status"] != "pass" for row in experiments):
            errors.append("patch application")

        units = [
            run_units(states[state], out_dir, state)
            for state in ("supported-3.3.x-baseline", "supported-3.3.x-rev0040")
        ]
        if any(row["status"] != "pass" for row in units):
            errors.append("upstream units")
        if len({(row["passed"], row["failed"], row["skipped"]) for row in units}) != 1:
            errors.append("upstream unit parity")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    if any(row["status"] != "pass" for row in invariants):
        errors.append("source invariants")
    claims = claim_matrix()
    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "source_zip": str(source_zip),
        "source_zip_sha256": source_info.sha256,
        "expected_source_zip_sha256": EXPECTED_SOURCE_SHA256,
        "source_candidates": [row.path for row in candidates],
        "lane_heads": observed_heads,
        "expected_lane_heads": {label: ref for label, (_lane, ref) in LANES.items()},
        "extracted_entries": entry_counts,
        "source_invariants_passed": sum(row["status"] == "pass" for row in invariants),
        "source_invariants_total": len(invariants),
        "test_expectations_passed": sum(row["expectation_status"] == "pass" for row in test_rows),
        "test_expectations_total": len(test_rows),
        "compile_checks_passed": sum(row["status"] == "pass" for row in compiles),
        "compile_checks_total": len(compiles),
        "upstream_units": units,
        "experiments": experiments,
        "artifact_refactor": artifact_metrics(),
        "claim_layers": claims,
        "disposition": "confirmed consistency gap; request-epoch policy unresolved",
        "security_route": "not supported by current evidence",
        "selected_patch": None,
        "historical_rev0040_status": "production-ready/selected-patch decision superseded",
        "errors": sorted(set(errors)),
    }
    if args.write_data:
        write_json(ROOT / "data/rev0076_search_resp_buddy_summary.json", summary)
        write_csv(ROOT / "data/rev0076_search_resp_buddy_test_matrix.csv", test_rows)
        write_json(ROOT / "data/rev0076_search_resp_buddy_test_matrix.json", test_rows)
        write_csv(ROOT / "data/rev0076_search_resp_buddy_source_invariants.csv", invariants)
        write_json(ROOT / "data/rev0076_search_resp_buddy_source_invariants.json", invariants)
        write_csv(ROOT / "data/rev0076_search_resp_buddy_claim_matrix.csv", claims)
        write_json(ROOT / "data/rev0076_search_resp_buddy_claim_matrix.json", claims)
        write_csv(ROOT / "data/rev0076_search_resp_buddy_compile_matrix.csv", compiles)
        write_json(ROOT / "data/rev0076_search_resp_buddy_compile_matrix.json", compiles)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
