#!/usr/bin/env python3
"""Run one rev0083 upstream-unit lane in a disposable source extraction.

The bounded lane runner validates the mode-owned Search Again prototype in a
disposable source extraction. Its result is content-bound to the source bundle,
lane head, candidate patch, and JUnit report.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    file_inventory,
    isolated_environment,
    parse_junit_report,
    purge_isolated_environment,
    run_bounded,
    safe_extract_tar_gz_member,
    sha256_path,
    write_json,
)
from source_bundle_locator import (  # noqa: E402
    LANE_HEADS,
    archive_member_name,
    inspect_bundle,
    locate_source_bundle,
)

REVISION = derive_revision(ROOT)
SOURCE_LANE = "github-branch-master"
PATCH = ROOT / "maintainer_artifacts/search-rekey-01/search_again_mode_owned_rekey_rev0083.patch"
EVIDENCE_ROOT = ROOT / f"evidence/{REVISION}-search-mode-ownership-runtime/upstream-units"


def changed_inventory(
    before: dict[Path, tuple[str, int]], after: dict[Path, tuple[str, int]]
) -> list[str]:
    return sorted(
        path.as_posix()
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def run_lane(label: str, source_zip: Path) -> dict[str, Any]:
    lane_root = EVIDENCE_ROOT / label
    if lane_root.exists():
        shutil.rmtree(lane_root)
    lane_root.mkdir(parents=True)

    scratch = Path(tempfile.mkdtemp(prefix=f"{REVISION}-{label}-", dir="/mnt/data"))
    source = scratch / "source"
    source.mkdir()
    environment_root = scratch / "environment"
    patch_digest = sha256_path(PATCH) if label == "patched" else None
    patch_applied = False
    errors: list[str] = []
    result: dict[str, Any] | None = None
    source_cleaned = False

    try:
        extracted_files = safe_extract_tar_gz_member(
            source_zip, archive_member_name(SOURCE_LANE), source
        )
        expected = source / "pynicotine/tests/unit"
        if not expected.is_dir():
            raise RuntimeError(f"incomplete source extraction: {expected}")

        if label == "patched":
            check = run_bounded(
                ["git", "apply", "--check", str(PATCH)],
                cwd=source,
                timeout=60,
                output_path=lane_root / "patch-check.log",
            )
            if check.returncode != 0:
                errors.append(f"patch check returncode={check.returncode}")
            else:
                apply = run_bounded(
                    ["git", "apply", str(PATCH)],
                    cwd=source,
                    timeout=60,
                    output_path=lane_root / "patch-apply.log",
                )
                patch_applied = apply.returncode == 0
                if not patch_applied:
                    errors.append(f"patch apply returncode={apply.returncode}")

        before = file_inventory(source)
        env, _cwd = isolated_environment(environment_root, python_paths=(source,))
        junit = lane_root / "junit.xml"
        command = [
            sys.executable,
            str(ROOT / "tools/run_pytest_forced_exit.py"),
            "-q",
            "-p",
            "no:cacheprovider",
            str(source / "pynicotine/tests/unit"),
        ]
        exclusions: list[str] = []
        if shutil.which("msgfmt") is None:
            i18n = source / "pynicotine/tests/unit/test_i18n.py"
            command.append(f"--ignore={i18n}")
            exclusions.append("pynicotine/tests/unit/test_i18n.py (msgfmt unavailable)")
        command.append(f"--junitxml={junit}")

        try:
            run = run_bounded(
                command,
                cwd=source,
                env=env,
                timeout=300,
                output_path=lane_root / "pytest.log",
            )
            rows = parse_junit_report(junit) if junit.is_file() else []
        finally:
            environment_cleanup = purge_isolated_environment(environment_root)

        after = file_inventory(source)
        writes = changed_inventory(before, after)
        outcomes = {
            outcome: sum(row["outcome"] == outcome for row in rows)
            for outcome in ("passed", "skipped", "failed", "error")
        }
        if run.returncode != 0:
            errors.append(f"pytest returncode={run.returncode}")
        if outcomes["failed"] or outcomes["error"]:
            errors.append(
                f"unit failures={outcomes['failed']}, errors={outcomes['error']}"
            )
        if len(rows) != 61:
            errors.append(f"unit row count={len(rows)}, expected=61")
        if label == "patched" and not patch_applied:
            errors.append("patched lane did not apply candidate patch")
        if environment_cleanup["residual_directories"]:
            errors.append(
                "isolated environment cleanup left residual directories: "
                f"{environment_cleanup['residual_directories']}"
            )

        inspection = inspect_bundle(source_zip)
        result = {
            "revision": REVISION,
            "status": "pending-cleanup",
            "lane": label,
            "evidence_mode": "bounded-disposable-source-lane",
            "source": {
                "bundle": source_zip.name,
                "bundle_sha256": inspection.sha256,
                "lane": SOURCE_LANE,
                "executable_source_ref": LANE_HEADS[SOURCE_LANE],
                "extracted_files": extracted_files,
            },
            "candidate_patch": {
                "path": PATCH.relative_to(ROOT).as_posix() if label == "patched" else None,
                "sha256": patch_digest,
                "applied": patch_applied,
            },
            "command": [
                "python",
                "tools/run_pytest_forced_exit.py",
                "-q",
                "-p",
                "no:cacheprovider",
                "<disposable-source>/pynicotine/tests/unit",
                *[f"--ignore=<disposable-source>/{item.split(' (', 1)[0]}" for item in exclusions],
                "--junitxml=<evidence>/junit.xml",
            ],
            "excluded": exclusions,
            "tests": {
                **outcomes,
                "total": len(rows),
                "returncode": run.returncode,
            },
            "junit": {
                "path": junit.relative_to(ROOT).as_posix(),
                "sha256": sha256_path(junit) if junit.is_file() else None,
            },
            "source_tree_final_writes": writes,
            "runtime_environment_cleanup": environment_cleanup,
            "source_isolation": {
                "dedicated_extraction": True,
                "shared_with_other_test_lanes": False,
                "source_extraction_cleaned_after_run": False,
                "isolated_environment_cleaned_after_run": not environment_cleanup["residual_directories"],
                "cleaned_after_run": False,
            },
            "errors": errors,
        }
    finally:
        if environment_root.exists():
            # Fail closed on interrupted lanes, while keeping all mutable runtime
            # state outside the package evidence tree.
            purge_isolated_environment(environment_root)
        shutil.rmtree(scratch, ignore_errors=True)
        source_cleaned = not scratch.exists()

    if result is None:
        raise RuntimeError(f"unit lane {label} produced no result")
    if not source_cleaned:
        errors.append("disposable source extraction cleanup failed")

    isolation = result["source_isolation"]
    isolation["source_extraction_cleaned_after_run"] = source_cleaned
    isolation["cleaned_after_run"] = (
        source_cleaned and isolation["isolated_environment_cleaned_after_run"]
    )
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(ROOT / f"data/{REVISION}_search_mode_unit_{label}.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("baseline", "patched"), required=True)
    parser.add_argument("--source-zip", default="auto")
    args = parser.parse_args()
    source_zip, _inspections = locate_source_bundle(args.source_zip)
    result = run_lane(args.lane, source_zip)
    print(canonical_json(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
