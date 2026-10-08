#!/usr/bin/env python3
"""Run exact-current 3.3.x upstream unit tests before and after the rev0062 patch stack.

Each source state receives a fresh extraction and a private HOME/XDG/TMP/cwd.
This avoids coupling the upstream suite to mutable state from the legacy witness
runner or from the other source state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import zipfile
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

LANE = "github-branch-3.3.x"
PATCH_ORDER = (
    "u-123-rev0059.patch",
    "pb-01-rev0059.patch",
    "search-resp-source-admission-rev0059.patch",
    "search-resp-parser-budget-rev0059.patch",
)


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
    fields = list(rows[0]) if rows else ["status"]
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
            with archive.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            count += 1
    return count


def run(command: list[str], *, cwd: Path, env: dict[str, str], timeout: int) -> subprocess.CompletedProcess[str]:
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
        stdout = (stdout or "") + f"\n[rev0072 process-group timeout after {timeout}s]\n"
        return subprocess.CompletedProcess(command, 124, stdout)


def summary_line(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b\d+ (?:failed|passed|skipped|error|errors)\b", line, re.I):
            return line
    return lines[-1] if lines else ""


def outcome_signature(summary: str) -> str:
    return re.sub(r"\s+in\s+[0-9.]+s$", "", summary.strip())


def isolated_environment(source_dir: Path, runtime_dir: Path) -> tuple[dict[str, str], Path]:
    paths = {
        "HOME": runtime_dir / "home",
        "XDG_CONFIG_HOME": runtime_dir / "xdg-config",
        "XDG_DATA_HOME": runtime_dir / "xdg-data",
        "XDG_CACHE_HOME": runtime_dir / "xdg-cache",
        "TMPDIR": runtime_dir / "tmp",
    }
    cwd = runtime_dir / "cwd"
    for path in (*paths.values(), cwd):
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in paths.items()})
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONPATH": str(source_dir),
    })
    env.pop("NICOTINE_NETWORK_TESTS", None)
    return env, cwd


def apply_patch_stack(checkout: Path) -> list[dict[str, Any]]:
    patch_root = ROOT / "handoff" / "rev0062" / "cleanroom-kit" / "patches" / LANE
    env = os.environ.copy()
    rows: list[dict[str, Any]] = []
    for patch_name in PATCH_ORDER:
        patch_path = patch_root / patch_name
        proc = run(
            ["patch", "--batch", "--forward", "-p0", "-i", str(patch_path)],
            cwd=checkout,
            env=env,
            timeout=60,
        )
        row = {
            "patch": patch_name,
            "sha256": sha256_path(patch_path),
            "observed_rc": proc.returncode,
            "summary": summary_line(proc.stdout),
            "status": "pass" if proc.returncode == 0 else "fail",
        }
        rows.append(row)
        if proc.returncode != 0:
            break
    return rows


def run_unit_state(source_dir: Path, runtime_dir: Path, *, msgfmt_available: bool) -> subprocess.CompletedProcess[str]:
    env, cwd = isolated_environment(source_dir, runtime_dir)
    unit_dir = source_dir / "pynicotine" / "tests" / "unit"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(unit_dir),
    ]
    if not msgfmt_available:
        command.extend(["--ignore", str(unit_dir / "test_i18n.py")])
    return run(command, cwd=cwd, env=env, timeout=180)


def main() -> int:
    parser = argparse.ArgumentParser(description="rev0072 isolated upstream unit before/after parity")
    parser.add_argument("--source-zip", default="auto", help="explicit source ZIP path or 'auto'")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0072-upstream-unit-parity-runtime"))
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    try:
        source_zip, candidates = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(json.dumps({"revision": "rev0072", "status": "fail", "errors": [str(exc)]}, indent=2))
        return 1

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    source_info = inspect_bundle(source_zip)
    snapshot = json.loads((ROOT / "data" / "rev0072_upstream_ref_snapshot.json").read_text(encoding="utf-8"))
    current_ref = snapshot["refs"]["3.3.x"]["sha"]
    lane_head = source_lane_head(source_zip)
    exact_ref = source_info.status == "pass" and lane_head == current_ref
    msgfmt_available = shutil.which("msgfmt") is not None
    errors: list[str] = []
    state_rows: list[dict[str, Any]] = []
    patch_rows: list[dict[str, Any]] = []

    if not exact_ref:
        errors.append("source lane is not the pinned exact-current 3.3.x ref")

    with tempfile.TemporaryDirectory(prefix="rev0072-upstream-unit-") as temporary:
        temp = Path(temporary)
        unpatched = temp / "unpatched-source"
        patched = temp / "patched-source"
        unpatched_entries = safe_extract_lane(source_zip, unpatched)
        patched_entries = safe_extract_lane(source_zip, patched)
        patch_rows = apply_patch_stack(patched)
        patch_ok = len(patch_rows) == len(PATCH_ORDER) and all(row["status"] == "pass" for row in patch_rows)
        if not patch_ok:
            errors.append("patch stack did not apply to isolated unit-test lane")

        for state, source_dir, entries in (
            ("unpatched", unpatched, unpatched_entries),
            ("patched", patched, patched_entries),
        ):
            if state == "patched" and not patch_ok:
                proc = subprocess.CompletedProcess([], 125, "patch stack failed; suite not run")
            else:
                proc = run_unit_state(source_dir, temp / f"{state}-runtime", msgfmt_available=msgfmt_available)
            (out_dir / f"{state}.txt").write_text(proc.stdout, encoding="utf-8")
            row = {
                "state": state,
                "lane": LANE,
                "ref": current_ref,
                "source_entries": entries,
                "observed_rc": proc.returncode,
                "summary": summary_line(proc.stdout),
                "outcome_signature": outcome_signature(summary_line(proc.stdout)),
                "msgfmt_available": str(msgfmt_available).lower(),
                "i18n_test_excluded": str(not msgfmt_available).lower(),
                "environment_isolation": "fresh extraction; private HOME/XDG_CONFIG/XDG_DATA/XDG_CACHE/TMP/cwd",
                "status": "pass" if proc.returncode == 0 else "fail",
            }
            state_rows.append(row)
            if proc.returncode != 0:
                errors.append(f"{state} upstream unit suite")

    parity = (
        len(state_rows) == 2
        and all(row["status"] == "pass" for row in state_rows)
        and state_rows[0]["outcome_signature"] == state_rows[1]["outcome_signature"]
    )
    if not parity:
        errors.append("before/after unit summary parity")

    summary = {
        "revision": "rev0072",
        "status": "pass" if not errors else "fail",
        "observed_at": snapshot["observed_at"],
        "source_zip": str(source_zip),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_contract_status": source_info.status,
        "source_candidates": [asdict(row) for row in candidates],
        "lane": LANE,
        "lane_ref": lane_head,
        "observed_current_ref": current_ref,
        "exact_current_ref_match": exact_ref,
        "msgfmt_available": msgfmt_available,
        "i18n_test_excluded_for_missing_msgfmt": not msgfmt_available,
        "state_rows": state_rows,
        "patch_rows": patch_rows,
        "summary_parity": parity,
        "errors": errors,
    }
    write_json(out_dir / "rev0072_upstream_unit_parity_summary.json", summary)
    if args.write_data:
        write_csv(ROOT / "data" / "rev0072_upstream_unit_parity.csv", state_rows)
        write_json(ROOT / "data" / "rev0072_upstream_unit_parity.json", state_rows)
        write_csv(ROOT / "data" / "rev0072_upstream_unit_patch_apply.csv", patch_rows)
        write_json(ROOT / "data" / "rev0072_upstream_unit_patch_apply.json", patch_rows)
        write_json(ROOT / "data" / "rev0072_upstream_unit_parity_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
