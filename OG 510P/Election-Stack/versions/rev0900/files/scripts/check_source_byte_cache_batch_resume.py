#!/usr/bin/env python3
"""Check source-byte cache batch resume mode.

The batch sha256sum files made the source-byte queue operator-sized, but the
receipt writer still needed an explicit guard to process exactly one selected
batch.  This gate keeps that resume path deterministic: the current report must
be generated from batch01 with an empty-cache assumption, and a temp smoke proves
that a populated cache file outside the selected batch does not become a
receipt.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "source_byte_receipts_from_cache_batch.py"
BATCH_FILE = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-resume-rev{REV}.json"
BATCH_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"

REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "not source-byte cache completeness",
    "bundles no third-party bytes",
)


def run_proc(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(cmd: list[str], *, cwd: Path = ROOT) -> dict:
    proc = run_proc(cmd, cwd=cwd)
    if proc.returncode != 0:
        print("ERROR: command failed:", " ".join(cmd), file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)
    try:
        return json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: could not parse JSON from {' '.join(cmd)}: {exc}", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def smoke_selected_batch_only() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="source-cache-batch-resume-") as td:
        tmp = Path(td)
        lock = tmp / "external-sources.toml"
        cache = tmp / "cache"
        receipts = tmp / "receipts"
        batch = tmp / "selected.sha256"
        bad_batch = tmp / "bad-selected.sha256"
        unsafe_batch = tmp / "unsafe-selected.sha256"
        cache.mkdir()

        selected_good_payload = "selected good bytes\n"
        selected_bad_payload = "selected wrong bytes\n"
        out_of_batch_payload = "out of batch but valid bytes\n"
        selected_good_sha = sha256_text(selected_good_payload)
        out_of_batch_sha = sha256_text(out_of_batch_payload)
        write_text(cache / "selected-good.txt", selected_good_payload)
        write_text(cache / "selected-bad.txt", selected_bad_payload)
        write_text(cache / "out-of-batch.txt", out_of_batch_payload)
        write_text(
            lock,
            f"""
[[source]]
id = "selected_good"
url = "https://example.invalid/selected-good.txt"
retrieved = "2026-06-13"
sha256 = "{selected_good_sha}"
local_filename = "selected-good.txt"
tags = ["eac"]
note = "temporary smoke fixture only"

[[source]]
id = "selected_bad"
url = "https://example.invalid/selected-bad.txt"
retrieved = "2026-06-13"
sha256 = "{selected_good_sha}"
local_filename = "selected-bad.txt"
tags = ["eac"]
note = "temporary smoke fixture only"

[[source]]
id = "out_of_batch"
url = "https://example.invalid/out-of-batch.txt"
retrieved = "2026-06-13"
sha256 = "{out_of_batch_sha}"
local_filename = "out-of-batch.txt"
tags = ["eac"]
note = "temporary smoke fixture only"
""".lstrip(),
        )
        write_text(batch, f"{selected_good_sha}  selected-good.txt\n{selected_good_sha}  selected-bad.txt\n")
        report = run_json([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--scope",
            "all-pinned",
            "--batch-file",
            str(batch),
            "--write-receipts",
            "--retrieved-at-utc",
            "2026-06-13T05:30:00Z",
            "--json",
        ])
        if int(report.get("batch_file_entry_count") or 0) != 2:
            errors.append("resume smoke expected exactly two selected batch entries")
        if int(report.get("candidate_source_count") or 0) != 2:
            errors.append("resume smoke must scan only the selected batch, not all pinned rows")
        if int(report.get("matched_cache_file_count") or 0) != 1:
            errors.append("resume smoke expected one selected cache match")
        if int(report.get("mismatched_cache_file_count") or 0) != 1:
            errors.append("resume smoke expected one selected cache mismatch")
        if int(report.get("written_receipt_count") or 0) != 1:
            errors.append("resume smoke expected one written selected receipt")
        if not (receipts / "selected_good.receipt.json").exists():
            errors.append("resume smoke did not write selected matching receipt")
        if (receipts / "selected_bad.receipt.json").exists():
            errors.append("resume smoke wrote a receipt for selected mismatched bytes")
        if (receipts / "out_of_batch.receipt.json").exists():
            errors.append("resume smoke wrote a receipt for a valid cache file outside the selected batch")

        write_text(bad_batch, f"{'0'*64}  selected-good.txt\n")
        bad = run_proc([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--scope",
            "all-pinned",
            "--batch-file",
            str(bad_batch),
            "--json",
        ])
        if bad.returncode == 0:
            errors.append("resume smoke accepted a batch file whose expected hash does not match the lockfile")

        write_text(unsafe_batch, f"{selected_good_sha}  ../selected-good.txt\n")
        unsafe = run_proc([
            sys.executable,
            str(SCRIPT),
            "--lockfile",
            str(lock),
            "--cache-dir",
            str(cache),
            "--receipt-dir",
            str(receipts),
            "--scope",
            "all-pinned",
            "--batch-file",
            str(unsafe_batch),
            "--json",
        ])
        if unsafe.returncode == 0:
            errors.append("resume smoke accepted an unsafe batch filename")
    return errors


def main() -> int:
    errors: list[str] = []
    for path, label in (
        (SCRIPT, "batch ingest script"),
        (BATCH_FILE, "current batch01 sha256sum file"),
        (REPORT, "current batch resume report"),
        (BATCH_REPORT, "current batch manifest report"),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    generated = run_json([
        sys.executable,
        str(SCRIPT),
        "--assume-empty-cache",
        "--scope",
        "all-pinned",
        "--batch-file",
        str(BATCH_FILE),
        "--json",
    ])
    shipped = load_json(REPORT)
    if generated != shipped:
        errors.append("source-byte batch resume report is stale; rerun source_byte_receipts_from_cache_batch.py with --batch-file batch01 --assume-empty-cache")

    batch_report = load_json(BATCH_REPORT)
    first_batch = (batch_report.get("batch_files") or [{}])[0]
    if shipped.get("archive_version") != VERSION:
        errors.append("batch resume report archive_version does not match VERSION")
    if shipped.get("batch_file") != str(BATCH_FILE.relative_to(ROOT)):
        errors.append("batch resume report must point at current batch01")
    if int(shipped.get("batch_file_entry_count") or -1) != int(first_batch.get("line_count") or -2):
        errors.append("batch resume entry count must equal batch01 line_count")
    if int(shipped.get("candidate_source_count") or -1) != int(first_batch.get("line_count") or -2):
        errors.append("batch resume candidate count must equal batch01 line_count under all-pinned scope")
    if shipped.get("assume_empty_cache") is not True:
        errors.append("release batch resume report must be generated with assume_empty_cache=true")
    if shipped.get("network_io") is not False:
        errors.append("batch resume report must state network_io=false")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("batch resume report must not bundle third-party bytes")
    if int(shipped.get("matched_cache_file_count", -1)) != 0:
        errors.append("release batch resume report must not claim matched cache files")
    if int(shipped.get("written_receipt_count", -1)) != 0:
        errors.append("release batch resume report must not claim written receipts")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"batch resume boundary missing phrase: {phrase}")
    rows = shipped.get("rows") or []
    if len(rows) != int(shipped.get("candidate_source_count") or -1):
        errors.append("batch resume rows length does not match candidate_source_count")
    for row in rows[:5]:
        if row.get("cache_status") != "cache_not_inspected_assumed_empty":
            errors.append("batch resume current report must not inspect release-local cache bytes")

    errors.extend(smoke_selected_batch_only())

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: source-byte batch resume ({VERSION}, batch01_entries={shipped['candidate_source_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
