#!/usr/bin/env python3
"""rev0073 current-3.3.x U-123 disposition and native-regression gate."""
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
TEST_FILE = "pynicotine/tests/unit/transfers/test_downloads.py"
UNIT_DIR = "pynicotine/tests/unit"
PATCH_DIR = ROOT / "handoff" / "rev0073" / "u123" / "patches"
TEST_PATCH = PATCH_DIR / "u-123-current-3.3.x-tests-only-p1.patch"
COMBINED_PATCH = PATCH_DIR / "u-123-current-3.3.x-with-tests-p1.patch"
TOUCHED = (
    "pynicotine/downloads.py",
    "pynicotine/transfers.py",
    TEST_FILE,
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
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
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
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


def isolated_environment(source: Path, runtime: Path) -> tuple[dict[str, str], Path]:
    runtime.mkdir(parents=True, exist_ok=True)
    cwd = runtime / "cwd"
    cwd.mkdir()
    env = os.environ.copy()
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "HOME": str(runtime / "home"),
        "XDG_CONFIG_HOME": str(runtime / "xdg-config"),
        "XDG_DATA_HOME": str(runtime / "xdg-data"),
        "XDG_CACHE_HOME": str(runtime / "xdg-cache"),
        "TMPDIR": str(runtime / "tmp"),
        "PYTHONPATH": str(source),
    })
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "TMPDIR"):
        Path(env[key]).mkdir(parents=True, exist_ok=True)
    return env, cwd


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 240) -> subprocess.CompletedProcess[str]:
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
        return subprocess.CompletedProcess(command, 124, (stdout or "") + f"\n[{REVISION} timeout]\n")


def apply_patch(source: Path, patch_path: Path, *, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["patch", "-p1", "--batch", "--forward"]
    if dry_run:
        command.append("--dry-run")
    command.extend(["-i", str(patch_path)])
    return run(command, cwd=source, timeout=60)


def pytest_summary(output: str) -> str:
    for line in reversed(output.splitlines()):
        if re.search(r"\b(?:failed|passed|skipped)\b", line) and " in " in line:
            return line.strip()
    return "summary-not-found"


def outcome_counts(output: str) -> dict[str, int]:
    summary = pytest_summary(output)
    counts: dict[str, int] = {"failed": 0, "passed": 0, "skipped": 0}
    for count, label in re.findall(r"(\d+) (failed|passed|skipped)", summary):
        counts[label] = int(count)
    return counts


def run_pytest(source: Path, runtime: Path, target: str, *, ignore_i18n: bool) -> subprocess.CompletedProcess[str]:
    env, cwd = isolated_environment(source, runtime)
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(source / target)]
    if ignore_i18n and target == UNIT_DIR:
        command.extend(["--ignore", str(source / UNIT_DIR / "test_i18n.py")])
    return run(command, cwd=cwd, env=env, timeout=240)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0073-u123-current-runtime"))
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    errors: list[str] = []
    checks: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    try:
        source_zip, candidates = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(json.dumps({"revision": REVISION, "status": "fail", "errors": [str(exc)]}, indent=2))
        return 1

    source_info = inspect_bundle(source_zip)
    snapshot = json.loads((ROOT / "data" / "rev0072_upstream_ref_snapshot.json").read_text(encoding="utf-8"))
    pinned_ref = snapshot["refs"]["3.3.x"]["sha"]
    lane_head = source_lane_head(source_zip)
    exact_ref = source_info.status == "pass" and lane_head == pinned_ref
    checks.append({
        "check": "source contract and exact current 3.3.x ref",
        "status": "pass" if exact_ref else "fail",
        "source_sha256": source_info.sha256,
        "lane_head": lane_head,
        "pinned_ref": pinned_ref,
    })
    if not exact_ref:
        errors.append("source contract/current ref mismatch")

    for patch in (TEST_PATCH, COMBINED_PATCH):
        exists = patch.is_file()
        checks.append({
            "check": f"patch present: {patch.name}",
            "status": "pass" if exists else "fail",
            "sha256": sha256_path(patch) if exists else "",
        })
        if not exists:
            errors.append(f"missing patch {patch.name}")

    msgfmt_available = shutil.which("msgfmt") is not None

    with tempfile.TemporaryDirectory(prefix="rev0073-u123-") as temporary:
        temp = Path(temporary)
        states = {
            "unpatched-with-tests": temp / "unpatched",
            "patched-with-tests": temp / "patched",
        }
        for source in states.values():
            safe_extract_lane(source_zip, source)

        dry_run = apply_patch(states["patched-with-tests"], COMBINED_PATCH, dry_run=True)
        (out_dir / "combined-patch-dry-run.txt").write_text(dry_run.stdout, encoding="utf-8")
        checks.append({"check": "combined patch dry-run", "status": "pass" if dry_run.returncode == 0 else "fail", "observed_rc": dry_run.returncode})
        if dry_run.returncode != 0:
            errors.append("combined patch dry-run")

        patch_un = apply_patch(states["unpatched-with-tests"], TEST_PATCH)
        patch_fixed = apply_patch(states["patched-with-tests"], COMBINED_PATCH)
        (out_dir / "test-only-patch-apply.txt").write_text(patch_un.stdout, encoding="utf-8")
        (out_dir / "combined-patch-apply.txt").write_text(patch_fixed.stdout, encoding="utf-8")
        for name, proc in (("test-only patch apply", patch_un), ("combined patch apply", patch_fixed)):
            checks.append({"check": name, "status": "pass" if proc.returncode == 0 else "fail", "observed_rc": proc.returncode})
            if proc.returncode != 0:
                errors.append(name)

        expectations = {
            ("unpatched-with-tests", "targeted"): {"rc_nonzero": True, "failed": 2, "passed": 7, "skipped": 0},
            ("unpatched-with-tests", "unit"): {"rc_nonzero": True, "failed": 2, "passed": 58, "skipped": 1},
            ("patched-with-tests", "targeted"): {"rc_nonzero": False, "failed": 0, "passed": 9, "skipped": 0},
            ("patched-with-tests", "unit"): {"rc_nonzero": False, "failed": 0, "passed": 60, "skipped": 1},
        }

        for state, source in states.items():
            if (state == "unpatched-with-tests" and patch_un.returncode != 0) or (state == "patched-with-tests" and patch_fixed.returncode != 0):
                continue
            for scope, target in (("targeted", TEST_FILE), ("unit", UNIT_DIR)):
                proc = run_pytest(source, temp / f"runtime-{state}-{scope}", target, ignore_i18n=not msgfmt_available)
                output_path = out_dir / f"{state}-{scope}.txt"
                output_path.write_text(proc.stdout, encoding="utf-8")
                counts = outcome_counts(proc.stdout)
                expected = expectations[(state, scope)]
                observed_nonzero = proc.returncode != 0
                expected_ok = (
                    observed_nonzero == expected["rc_nonzero"]
                    and all(counts[key] == expected[key] for key in ("failed", "passed", "skipped"))
                )
                row = {
                    "state": state,
                    "scope": scope,
                    "observed_rc": proc.returncode,
                    "summary": pytest_summary(proc.stdout),
                    **counts,
                    "expected_failed": expected["failed"],
                    "expected_passed": expected["passed"],
                    "expected_skipped": expected["skipped"],
                    "i18n_excluded": str(scope == "unit" and not msgfmt_available).lower(),
                    "status": "pass" if expected_ok else "fail",
                }
                test_rows.append(row)
                if not expected_ok:
                    errors.append(f"unexpected pytest outcome: {state}/{scope}")

        compile_proc = run(
            [sys.executable, "-m", "py_compile", *[str(states["patched-with-tests"] / path) for path in TOUCHED]],
            cwd=states["patched-with-tests"],
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=60,
        )
        (out_dir / "patched-py-compile.txt").write_text(compile_proc.stdout, encoding="utf-8")
        checks.append({"check": "patched touched-file compile", "status": "pass" if compile_proc.returncode == 0 else "fail", "observed_rc": compile_proc.returncode})
        if compile_proc.returncode != 0:
            errors.append("patched touched-file compile")

        touched_rows: list[dict[str, Any]] = []
        for relative in TOUCHED:
            before = states["unpatched-with-tests"] / relative
            after = states["patched-with-tests"] / relative
            touched_rows.append({
                "path": relative,
                "unpatched_with_test_sha256": sha256_path(before),
                "patched_sha256": sha256_path(after),
                "changed": before.read_bytes() != after.read_bytes(),
            })
        write_csv(out_dir / "touched-file-hashes.csv", touched_rows)

    disposition = {
        "packet": "U-123",
        "current_applicability": "confirmed on exact 3.3.x ref",
        "recommended_filing": "ordinary public bug / defensive hardening",
        "severity": "low",
        "cve_or_embargo_recommended": False,
        "impact": "same-peer download session state confusion, orphaned transfer state, availability/integrity of transfer bookkeeping",
        "not_claimed": ["cross-user impact", "arbitrary path write", "code execution", "credential exposure", "file disclosure"],
        "public_overlap": "no exact duplicate-token report found; issue #653 is protocol-adjacent only",
    }
    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "observed_at": "2026-06-17",
        "source_zip": str(source_zip),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_candidates": [asdict(row) for row in candidates],
        "lane": LANE,
        "lane_head": lane_head,
        "pinned_ref": pinned_ref,
        "exact_ref_match": exact_ref,
        "msgfmt_available": msgfmt_available,
        "checks": checks,
        "test_rows": test_rows,
        "disposition": disposition,
        "errors": errors,
    }
    write_json(out_dir / "rev0073_u123_current_summary.json", summary)
    if args.write_data:
        write_csv(ROOT / "data" / "rev0073_u123_test_matrix.csv", test_rows)
        write_json(ROOT / "data" / "rev0073_u123_test_matrix.json", test_rows)
        write_csv(ROOT / "data" / "rev0073_u123_gate_checks.csv", checks)
        write_json(ROOT / "data" / "rev0073_u123_gate_checks.json", checks)
        write_json(ROOT / "data" / "rev0073_u123_disposition.json", disposition)
        write_json(ROOT / "data" / "rev0073_u123_current_summary.json", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
