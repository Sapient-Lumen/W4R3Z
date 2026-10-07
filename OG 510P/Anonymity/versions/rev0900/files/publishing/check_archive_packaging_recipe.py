#!/usr/bin/env python3
"""Check that the archive has a deterministic, digest-locked packaging recipe."""

from __future__ import annotations

import argparse
import calendar
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any



def link_or_copy(src: str, dst: str) -> str:
    """Hardlink unchanged files for the stale-digest negative control when possible.

    The control mutates one copied VERSION file and must not spend cloudtainer
    time duplicating the whole archive byte-for-byte.  Cross-device or
    permission-limited filesystems fall back to copy2 without weakening the
    digest-lock assertion.
    """
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return dst

def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def release_date_midnight_epoch(release: dict[str, Any]) -> int:
    year, month, day = (int(part) for part in str(release["timestamp"]).split(".")[:3])
    return calendar.timegm((year, month, day, 0, 0, 0))


def run_packager(root: pathlib.Path, env_overrides: dict[str, str] | None = None) -> tuple[int, dict[str, Any], str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env_overrides:
        env.update(env_overrides)
    proc = subprocess.run(
        [sys.executable, "-S", "-B", "publishing/build_archive_zip.py", "--root", ".", "--out-dir", "..", "--dry-run", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=45,
        env=env,
    )
    try:
        return proc.returncode, json.loads(proc.stdout), proc.stderr
    except json.JSONDecodeError:
        return proc.returncode, {"status": "fail", "stdout_tail": proc.stdout[-1000:]}, proc.stderr


def source_date_epoch_controls(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    expected = release_date_midnight_epoch(release)
    good_rc, good_report, good_stderr = run_packager(root, {"SOURCE_DATE_EPOCH": str(expected)})
    bad_rc, bad_report, bad_stderr = run_packager(root, {"SOURCE_DATE_EPOCH": str(expected + 60)})
    good_policy = good_report.get("source_date_epoch", {}) if isinstance(good_report, dict) else {}
    good_ok = (
        good_rc == 0
        and good_report.get("status") == "pass"
        and good_policy.get("status") == "set_matches_release_date_midnight_utc"
        and good_policy.get("effective_epoch_utc") == expected
    )
    bad_ok = (
        bad_rc != 0
        and bad_report.get("status") == "fail"
        and "SOURCE_DATE_EPOCH" in str(bad_report.get("error", "") + bad_stderr)
    )
    return {
        "status": "pass" if good_ok and bad_ok else "fail",
        "expected_epoch_utc": expected,
        "good_control": {
            "returncode": good_rc,
            "status": good_report.get("status"),
            "source_date_epoch": good_policy,
            "stderr_tail": good_stderr[-1000:],
        },
        "bad_control": {
            "returncode": bad_rc,
            "status": bad_report.get("status"),
            "error": str(bad_report.get("error", ""))[:1000],
            "stderr_tail": bad_stderr[-1000:],
        },
    }


def negative_control_digest_lock(root: pathlib.Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="anonymity_packager_digest_negative_") as tmp_s:
        tmp = pathlib.Path(tmp_s) / "tree"
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git")
        shutil.copytree(root, tmp, ignore=ignore, copy_function=link_or_copy)
        victim = tmp / "VERSION"
        before_bytes = victim.read_bytes()
        # copytree may hardlink files for speed; break this one link before
        # mutating the negative-control tree so the source archive is never
        # modified by its own stale-digest test.
        victim.unlink()
        victim.write_bytes(before_bytes + b"# digest-lock negative control mutation\n")
        rc, report, stderr = run_packager(tmp)
        digest = report.get("manifest_digest_check", {}) if isinstance(report, dict) else {}
        summary = report.get("summary", {}) if isinstance(report, dict) else {}
        failures = digest.get("failures", []) if isinstance(digest, dict) else []
        mismatches = []
        for failure in failures:
            if isinstance(failure, dict) and failure.get("category") == "manifest_sha256_digest_mismatch":
                mismatches.extend(failure.get("mismatches", []))
        mismatch_paths = sorted(m.get("path") for m in mismatches if isinstance(m, dict) and m.get("path"))
        mismatch_count = digest.get("digest_mismatch_count", summary.get("manifest_digest_mismatch_count")) if isinstance(digest, dict) else None
        ok = (
            rc != 0
            and report.get("status") == "fail"
            and digest.get("status") == "fail"
            and isinstance(mismatch_count, int)
            and mismatch_count >= 1
            and "VERSION" in mismatch_paths
        )
        return {
            "status": "pass" if ok else "fail",
            "mutated_path": "VERSION",
            "packager_returncode": rc,
            "packager_status": report.get("status"),
            "manifest_digest_status": digest.get("status") if isinstance(digest, dict) else None,
            "manifest_digest_mismatch_count": mismatch_count,
            "manifest_digest_mismatch_paths_sample": mismatch_paths[:20],
            "stderr_tail": stderr[-1000:],
        }


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    script = root / "publishing" / "build_archive_zip.py"
    makefile = root / "Makefile"
    dry_run: dict[str, Any] = {}
    negative_control: dict[str, Any] = {"status": "not_run"}
    source_date_control: dict[str, Any] = {"status": "not_run"}
    if not script.exists():
        failures.append({"category": "packaging_script_missing", "path": "publishing/build_archive_zip.py"})
    else:
        rc, dry_run, stderr = run_packager(root)
        if rc != 0 or dry_run.get("status") != "pass":
            failures.append({"category": "packaging_dry_run_not_pass", "returncode": rc, "dry_run": dry_run, "stderr_tail": stderr[-1000:]})
        else:
            digest = dry_run.get("manifest_digest_check", {}) if isinstance(dry_run.get("manifest_digest_check"), dict) else {}
            if digest.get("status") != "pass" or dry_run.get("summary", {}).get("manifest_digest_status") != "pass":
                failures.append({"category": "packaging_dry_run_digest_lock_not_pass", "digest": digest})
        if dry_run.get("generated_for_revision") != release["revision"] or dry_run.get("checked_bundle") != release["bundle"]:
            failures.append({"category": "packaging_dry_run_revision_bundle_mismatch", "dry_run_revision": dry_run.get("generated_for_revision"), "dry_run_bundle": dry_run.get("checked_bundle")})
        if dry_run.get("publication_authorized") is not False:
            failures.append({"category": "packaging_dry_run_publication_authorized_not_false"})
        source_date_control = source_date_epoch_controls(root)
        if source_date_control.get("status") != "pass":
            failures.append({"category": "source_date_epoch_control_failed", "source_date_epoch_control": source_date_control})
        negative_control = negative_control_digest_lock(root)
        if negative_control.get("status") != "pass":
            failures.append({"category": "packaging_digest_negative_control_failed", "negative_control": negative_control})
    if not makefile.exists() or "build_archive_zip.py" not in makefile.read_text(encoding="utf-8", errors="replace"):
        failures.append({"category": "makefile_package_target_missing"})

    summary = {
        "checks_failed": len(failures),
        "packaging_script_present": script.exists(),
        "makefile_package_target_present": makefile.exists() and "build_archive_zip.py" in makefile.read_text(encoding="utf-8", errors="replace"),
        "dry_run_status": dry_run.get("status", "not_run"),
        "input_file_count": dry_run.get("input_file_count", 0),
        "manifest_file_count": dry_run.get("manifest_file_count", 0),
        "manifest_digest_status": dry_run.get("summary", {}).get("manifest_digest_status"),
        "manifest_digest_mismatch_count": dry_run.get("summary", {}).get("manifest_digest_mismatch_count"),
        "source_date_epoch_status": dry_run.get("source_date_epoch", {}).get("status") if isinstance(dry_run.get("source_date_epoch"), dict) else None,
        "source_date_epoch_control_status": source_date_control.get("status"),
        "digest_negative_control_status": negative_control.get("status"),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "packaging_script": "publishing/build_archive_zip.py",
        "dry_run": dry_run,
        "source_date_epoch_control": source_date_control,
        "digest_lock_negative_control": negative_control,
        "summary": summary,
        "failures": failures[:50],
        "fail_closed_rule": "If deterministic packaging or manifest-digest lock checks fail, do not hand-package a zip as the canonical next version.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
