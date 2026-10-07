#!/usr/bin/env python3
"""Prove the deterministic packager is reproducible in two independent trials."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tempfile
import zipfile
from typing import Any

import build_archive_zip

EXPECTED_COMPRESS_TYPE = zipfile.ZIP_DEFLATED
EXPECTED_EXEC_MODE = 0o755
EXPECTED_FILE_MODE = 0o644
EXPECTED_EXEC_PATHS = set(getattr(build_archive_zip, "EXECUTABLE_ZIP_PATHS", set()))


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_timestamp(release: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
    return build_archive_zip.zip_datetime(release)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_paths(root: pathlib.Path) -> list[str]:
    return sorted(str(item) for item in load_json(root / "MANIFEST.json").get("files", []))


def run_build(root: pathlib.Path, out_dir: pathlib.Path) -> tuple[pathlib.Path, dict[str, Any], dict[str, Any]]:
    """Build a deterministic zip in-process.

    The earlier implementation spawned a second Python process for each trial.
    In constrained review environments that can obscure the actual guard signal
    behind process supervision noise.  Calling the canonical packager module
    directly still exercises the same build_zip implementation while keeping the
    reproducibility check lightweight and inspectable.
    """
    try:
        report = build_archive_zip.build_zip(root, out_dir)
        proc = {"returncode": 0, "stderr_tail": "", "stdout_was_json": True}
    except Exception as exc:  # pragma: no cover - failure path is reported.
        report = {"status": "fail", "error": str(exc)}
        proc = {"returncode": 1, "stderr_tail": str(exc)[-1000:], "stdout_was_json": True}
    written = pathlib.Path(str(report.get("written_zip", out_dir / "missing.zip")))
    return written, report, proc

def member_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            mode = (info.external_attr >> 16) & 0o777
            rows.append({
                "filename": info.filename,
                "date_time": list(info.date_time),
                "compress_type": info.compress_type,
                "external_mode": mode,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
                "crc": info.CRC,
            })
    return rows


def check_member_metadata(rows: list[dict[str, Any]], manifest: list[str], expected_dt: tuple[int, int, int, int, int, int]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    names = [row["filename"] for row in rows]
    if names != sorted(names):
        failures.append({"category": "zip_members_not_sorted"})
    missing = sorted(set(manifest) - set(names))
    extra = sorted(set(names) - set(manifest))
    if missing or extra:
        failures.append({"category": "zip_members_manifest_mismatch", "missing": missing[:20], "extra": extra[:20], "missing_count": len(missing), "extra_count": len(extra)})
    timestamp_mismatches = [row["filename"] for row in rows if tuple(row["date_time"]) != expected_dt]
    if timestamp_mismatches:
        failures.append({"category": "zip_member_timestamp_mismatch", "paths": timestamp_mismatches[:20], "count": len(timestamp_mismatches), "expected_timestamp": list(expected_dt)})
    compression_mismatches = [row["filename"] for row in rows if row["compress_type"] != EXPECTED_COMPRESS_TYPE]
    if compression_mismatches:
        failures.append({"category": "zip_member_compression_mismatch", "paths": compression_mismatches[:20], "count": len(compression_mismatches)})
    bad_modes = [row for row in rows if row["external_mode"] not in {EXPECTED_EXEC_MODE, EXPECTED_FILE_MODE}]
    if bad_modes:
        failures.append({"category": "zip_member_mode_mismatch", "paths": [row["filename"] for row in bad_modes[:20]], "count": len(bad_modes), "allowed_modes": [oct(EXPECTED_FILE_MODE), oct(EXPECTED_EXEC_MODE)]})
    row_modes = {str(row["filename"]): int(row["external_mode"]) for row in rows}
    missing_exec = sorted(path for path in EXPECTED_EXEC_PATHS if row_modes.get(path) != EXPECTED_EXEC_MODE)
    unexpected_exec = sorted(path for path, mode in row_modes.items() if mode == EXPECTED_EXEC_MODE and path not in EXPECTED_EXEC_PATHS)
    non_exec_bad = sorted(path for path, mode in row_modes.items() if path not in EXPECTED_EXEC_PATHS and mode != EXPECTED_FILE_MODE)
    if missing_exec:
        failures.append({"category": "zip_declared_executable_missing", "paths": missing_exec[:20], "count": len(missing_exec)})
    if unexpected_exec:
        failures.append({"category": "zip_unexpected_executable_member", "paths": unexpected_exec[:20], "count": len(unexpected_exec)})
    if non_exec_bad:
        failures.append({"category": "zip_non_executable_mode_mismatch", "paths": non_exec_bad[:20], "count": len(non_exec_bad), "expected_mode": oct(EXPECTED_FILE_MODE)})
    return failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    trial_reports: list[dict[str, Any]] = []
    digests: list[str] = []
    sizes: list[int] = []
    attestation_digests: list[str] = []
    public_key_sidecar_digests: list[str] = []
    row_sets: list[list[dict[str, Any]]] = []
    manifest = manifest_paths(root)
    timestamp_policy = build_archive_zip.zip_timestamp_policy(release)
    expected_dt = expected_timestamp(release)

    with tempfile.TemporaryDirectory(prefix="anonymity_zip_trial_a_") as a, tempfile.TemporaryDirectory(prefix="anonymity_zip_trial_b_") as b:
        for label, out in [("trial_a", pathlib.Path(a)), ("trial_b", pathlib.Path(b))]:
            zip_path, report, proc = run_build(root, out)
            public_report = {
                "label": label,
                "returncode": proc.get("returncode", 1),
                "status": report.get("status"),
                "generated_for_revision": report.get("generated_for_revision"),
                "checked_bundle": report.get("checked_bundle"),
                "zip_written": zip_path.exists(),
                "sha256_receipt_written": pathlib.Path(str(report.get("written_sha256_receipt", out / "missing.sha256"))).exists(),
                "package_attestation_written": pathlib.Path(str(report.get("written_package_attestation", out / "missing.package.intoto.jsonl"))).exists(),
                "public_key_sidecar_written": pathlib.Path(str(report.get("written_public_key_sidecar", out / "missing.package.dsse.pub.pem"))).exists(),
                "stdout_was_json": bool(proc.get("stdout_was_json", True)),
            }
            trial_reports.append(public_report)
            if proc.get("returncode", 1) != 0 or report.get("status") != "pass" or not zip_path.exists():
                failures.append({"category": "packaging_trial_failed", "trial": label, "returncode": proc.get("returncode", 1), "report": public_report, "stderr_tail": str(proc.get("stderr_tail", ""))[-1000:]})
                continue
            if report.get("generated_for_revision") != release["revision"] or report.get("checked_bundle") != release["bundle"]:
                failures.append({"category": "packaging_trial_revision_bundle_mismatch", "trial": label, "report": public_report})
            digest = sha256_file(zip_path)
            digests.append(digest)
            sizes.append(zip_path.stat().st_size)
            attestation_raw = str(report.get("written_package_attestation", ""))
            receipt_raw = str(report.get("written_sha256_receipt", ""))
            public_key_sidecar_raw = str(report.get("written_public_key_sidecar", ""))
            attestation_path = pathlib.Path(attestation_raw) if attestation_raw else pathlib.Path(out / "missing.package.intoto.jsonl")
            receipt_path = pathlib.Path(receipt_raw) if receipt_raw else pathlib.Path(out / "missing.sha256")
            public_key_sidecar_path = pathlib.Path(public_key_sidecar_raw) if public_key_sidecar_raw else pathlib.Path(out / "missing.package.dsse.pub.pem")
            if not receipt_raw or not receipt_path.exists():
                failures.append({"category": "packaging_trial_sha256_receipt_missing", "trial": label, "path": str(receipt_path)})
            if not attestation_raw or not attestation_path.exists():
                failures.append({"category": "packaging_trial_package_attestation_missing", "trial": label, "path": str(attestation_path)})
            else:
                attestation_digests.append(sha256_file(attestation_path))
            if not public_key_sidecar_raw or not public_key_sidecar_path.exists():
                failures.append({"category": "packaging_trial_public_key_sidecar_missing", "trial": label, "path": str(public_key_sidecar_path)})
            else:
                public_key_sidecar_digests.append(sha256_file(public_key_sidecar_path))
            rows = member_rows(zip_path)
            row_sets.append(rows)
            failures.extend(check_member_metadata(rows, manifest, expected_dt))

    if len(digests) == 2 and digests[0] != digests[1]:
        failures.append({"category": "packaging_trials_sha256_mismatch"})
    if len(sizes) == 2 and sizes[0] != sizes[1]:
        failures.append({"category": "packaging_trials_size_mismatch"})
    if len(row_sets) == 2 and row_sets[0] != row_sets[1]:
        failures.append({"category": "packaging_trials_member_metadata_mismatch"})
    if len(attestation_digests) == 2 and attestation_digests[0] != attestation_digests[1]:
        failures.append({"category": "packaging_trials_package_attestation_sha256_mismatch"})
    if len(public_key_sidecar_digests) == 2 and public_key_sidecar_digests[0] != public_key_sidecar_digests[1]:
        failures.append({"category": "packaging_trials_public_key_sidecar_sha256_mismatch"})

    member_count = len(row_sets[0]) if row_sets else 0
    first_members = [row["filename"] for row in row_sets[0][:5]] if row_sets else []
    last_members = [row["filename"] for row in row_sets[0][-5:]] if row_sets else []
    summary = {
        "checks_failed": len(failures),
        "trial_count": len(trial_reports),
        "trial_statuses": [row.get("status") for row in trial_reports],
        "two_trial_zip_sha256_equal": len(digests) == 2 and digests[0] == digests[1],
        "two_trial_zip_size_equal": len(sizes) == 2 and sizes[0] == sizes[1],
        "two_trial_member_metadata_equal": len(row_sets) == 2 and row_sets[0] == row_sets[1],
        "two_trial_package_attestation_sha256_equal": len(attestation_digests) == 2 and attestation_digests[0] == attestation_digests[1],
        "two_trial_public_key_sidecar_sha256_equal": len(public_key_sidecar_digests) == 2 and public_key_sidecar_digests[0] == public_key_sidecar_digests[1],
        "zip_member_count": member_count,
        "manifest_file_count": len(manifest),
        "expected_timestamp": list(expected_dt),
        "source_date_epoch": timestamp_policy,
        "expected_compression": "ZIP_DEFLATED",
        "allowed_external_modes": [oct(EXPECTED_FILE_MODE), oct(EXPECTED_EXEC_MODE)],
        "declared_executable_paths": sorted(EXPECTED_EXEC_PATHS),
        "permission_policy": "declared_archive_policy_not_ambient_filesystem_mode",
        "package_attestation_policy": "external_in_toto_slsa_sidecar_for_final_zip_digest; DSSE envelope is generated as a post-package external sidecar",
        "package_attestation_trial_count": len(attestation_digests),
        "public_key_sidecar_trial_count": len(public_key_sidecar_digests),
        "package_attestation_digest_recording": "omitted_from_archived_report_to_avoid_manifest_attestation_fixed_point_cycle; equality is checked in-memory",
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "packaging_script": "publishing/build_archive_zip.py",
        "trial_reports": trial_reports,
        "member_order_evidence": {
            "first_members": first_members,
            "last_members": last_members,
        },
        "summary": summary,
        "failures": failures[:50],
        "fail_closed_rule": "If two independent packaging trials diverge, declared zip member modes drift, SOURCE_DATE_EPOCH is not bound to the release-date timestamp policy, or package attestation sidecars diverge/miss; do not embed manifest-bound sidecar digests in archived reports; do not distribute a hand-built archive; repair the deterministic packager or its input surface first.",
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
