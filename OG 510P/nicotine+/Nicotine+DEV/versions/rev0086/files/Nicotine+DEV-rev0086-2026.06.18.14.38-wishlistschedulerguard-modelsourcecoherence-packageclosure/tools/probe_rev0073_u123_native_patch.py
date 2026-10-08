#!/usr/bin/env python3
"""Verify the U-123 native upstream-test patch without clobbering disposition data.

Research-only. This gate checks that the test-only patch exposes two failures on
unpatched exact-current source and that the combined prototype plus native tests
passes both its target file and the full isolated upstream unit suite.
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
TEST_FILE = "pynicotine/tests/unit/transfers/test_downloads.py"
UNIT_DIR = "pynicotine/tests/unit"
PATCH_DIR = ROOT / "handoff" / "rev0073" / "u123" / "patches"
TEST_PATCH = PATCH_DIR / "u-123-current-3.3.x-tests-only-p1.patch"
COMBINED_PATCH = PATCH_DIR / "u-123-current-3.3.x-with-tests-p1.patch"
TOUCHED = ("pynicotine/downloads.py", "pynicotine/transfers.py", TEST_FILE)


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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["status"])
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
    cwd = runtime / "cwd"
    mapping = {
        "HOME": runtime / "home",
        "XDG_CONFIG_HOME": runtime / "xdg-config",
        "XDG_DATA_HOME": runtime / "xdg-data",
        "XDG_CACHE_HOME": runtime / "xdg-cache",
        "TMPDIR": runtime / "tmp",
    }
    cwd.mkdir(parents=True)
    for path in mapping.values():
        path.mkdir(parents=True)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in mapping.items()})
    env.update({
        "PYTHONPATH": str(source),
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
            command,
            124,
            (stdout or "") + f"\n[{REVISION} timeout after {timeout}s]\n",
        )


def summary_line(output: str) -> str:
    for line in reversed(output.splitlines()):
        if re.search(r"\b(?:failed|passed|skipped)\b", line) and " in " in line:
            return line.strip()
    return "summary-not-found"


def outcome_counts(output: str) -> dict[str, int]:
    counts = {"failed": 0, "passed": 0, "skipped": 0}
    for count, label in re.findall(
        r"(\d+) (failed|passed|skipped)",
        summary_line(output),
    ):
        counts[label] = int(count)
    return counts


def apply_patch(source: Path, patch_path: Path) -> subprocess.CompletedProcess[str]:
    return run(
        ["patch", "--batch", "--forward", "-p1", "-i", str(patch_path)],
        cwd=source,
        env=os.environ.copy(),
        timeout=60,
    )


def run_pytest(
    state: str,
    source: Path,
    target: str,
    runtime_root: Path,
    *,
    ignore_i18n: bool,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"rev73-native-{state}-runtime-") as temp:
        env, cwd = isolated_env(source, Path(temp))
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(source / target),
        ]
        if ignore_i18n and target == UNIT_DIR:
            command.extend(["--ignore", str(source / UNIT_DIR / "test_i18n.py")])
        process = run(command, cwd=cwd, env=env, timeout=180)
    scope = "targeted" if target == TEST_FILE else "unit"
    output_path = runtime_root / f"{state}-{scope}.txt"
    output_path.write_text(process.stdout, encoding="utf-8")
    return {
        "state": state,
        "scope": scope,
        "observed_rc": process.returncode,
        "summary": summary_line(process.stdout),
        **outcome_counts(process.stdout),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "evidence" / "rev0073-u123-native-patch"),
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
    lane_ref = source_lane_head(source_zip)
    if source_info.status != "pass" or lane_ref != EXPECTED_REF:
        errors.append("source contract or exact ref mismatch")

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    state_roots: list[Path] = []
    patch_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []
    try:
        states = {}
        for state in ("unpatched-with-tests", "patched-with-tests"):
            root = Path(tempfile.mkdtemp(prefix=f"rev0073-native-{state}-"))
            state_roots.append(root)
            states[state] = root
            safe_extract_lane(source_zip, root)

        for state, patch_path in (
            ("unpatched-with-tests", TEST_PATCH),
            ("patched-with-tests", COMBINED_PATCH),
        ):
            process = apply_patch(states[state], patch_path)
            (out_dir / f"{state}-patch-apply.txt").write_text(
                process.stdout,
                encoding="utf-8",
            )
            row = {
                "state": state,
                "patch": str(patch_path.relative_to(ROOT)),
                "sha256": sha256_path(patch_path),
                "observed_rc": process.returncode,
                "status": "pass" if process.returncode == 0 else "fail",
            }
            patch_rows.append(row)
            if row["status"] != "pass":
                errors.append(f"patch application: {state}")

        compile_process = run(
            [
                sys.executable,
                "-m",
                "py_compile",
                *[str(states["patched-with-tests"] / path) for path in TOUCHED],
            ],
            cwd=states["patched-with-tests"],
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=60,
        )
        (out_dir / "patched-touched-compile.txt").write_text(
            compile_process.stdout,
            encoding="utf-8",
        )
        if compile_process.returncode != 0:
            errors.append("patched touched-file compile")

        msgfmt_available = shutil.which("msgfmt") is not None
        with ThreadPoolExecutor(max_workers=2) as executor:
            targeted = list(executor.map(
                lambda item: run_pytest(
                    item[0],
                    states[item[0]],
                    TEST_FILE,
                    out_dir,
                    ignore_i18n=False,
                ),
                (("unpatched-with-tests",), ("patched-with-tests",)),
            ))
        test_rows.extend(targeted)

        baseline_rows = json.loads(
            (ROOT / "data" / "rev0073_u123_upstream_unit_parity.json").read_text(
                encoding="utf-8"
            )
        )
        baseline = next(row for row in baseline_rows if row["state"] == "unpatched")
        patched_unit = run_pytest(
            "patched-with-tests",
            states["patched-with-tests"],
            UNIT_DIR,
            out_dir,
            ignore_i18n=not msgfmt_available,
        )
        test_rows.append(patched_unit)

        expectations = {
            ("unpatched-with-tests", "targeted"): {
                "failed": 2,
                "passed": 7,
                "skipped": 0,
                "rc_zero": False,
            },
            ("patched-with-tests", "targeted"): {
                "failed": 0,
                "passed": 9,
                "skipped": 0,
                "rc_zero": True,
            },
            ("patched-with-tests", "unit"): {
                "failed": 0,
                "passed": int(baseline["passed"]) + 2,
                "skipped": int(baseline["skipped"]),
                "rc_zero": True,
            },
        }
        for row in test_rows:
            expected = expectations[(row["state"], row["scope"])]
            matches = (
                (row["observed_rc"] == 0) == expected["rc_zero"]
                and all(row[field] == expected[field] for field in ("failed", "passed", "skipped"))
            )
            row.update({
                "expected_failed": expected["failed"],
                "expected_passed": expected["passed"],
                "expected_skipped": expected["skipped"],
                "expectation_status": "pass" if matches else "fail",
            })
            if not matches:
                errors.append(f"unexpected pytest outcome: {row['state']}/{row['scope']}")
    finally:
        for state_root in state_roots:
            shutil.rmtree(state_root, ignore_errors=True)

    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "source_zip": str(source_zip),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_contract_status": source_info.status,
        "source_candidates": [asdict(row) for row in candidates],
        "lane": LANE,
        "lane_ref": lane_ref,
        "expected_ref": EXPECTED_REF,
        "patches": patch_rows,
        "compile_status": "pass" if compile_process.returncode == 0 else "fail",
        "test_expectations_passed": sum(
            row["expectation_status"] == "pass" for row in test_rows
        ),
        "test_expectations_total": len(test_rows),
        "tests": test_rows,
        "data_namespace": "rev0073_u123_native_patch_* (does not overwrite disposition matrix)",
    }
    write_json(out_dir / "summary.json", summary)
    if args.write_data:
        write_json(ROOT / "data" / "rev0073_u123_native_patch_summary.json", summary)
        write_json(ROOT / "data" / "rev0073_u123_native_patch_matrix.json", test_rows)
        write_csv(ROOT / "data" / "rev0073_u123_native_patch_matrix.csv", test_rows)
        write_json(ROOT / "data" / "rev0073_u123_native_patch_apply.json", patch_rows)
        write_csv(ROOT / "data" / "rev0073_u123_native_patch_apply.csv", patch_rows)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
