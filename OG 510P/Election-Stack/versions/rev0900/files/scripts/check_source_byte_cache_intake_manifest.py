#!/usr/bin/env python3
"""Check the source-byte cache intake manifest.

This gate makes the remaining source-byte work more executable without claiming
that byte acquisition has happened.  A clean release must ship a current JSON
manifest and a sha256sum-ready expectation file for every receipt-missing pinned
source.  The checker proves that the file is current, safe-basename-only, aligned
with the acquisition queue/receipt report, and usable as an external cache
verification target.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
BUILDER = ROOT / "scripts" / "build_source_byte_cache_intake_manifest.py"
BATCH = ROOT / "scripts" / "source_byte_receipts_from_cache_batch.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-intake-manifest-rev{REV}.json"
SHA256SUM = ROOT / "artifacts" / "source_byte_cache_intake" / f"source-byte-cache-missing-receipts-rev{REV}.sha256"
QUEUE_REPORT = ROOT / "artifacts" / "reports" / "source-byte-acquisition-queue.json"
RECEIPT_REPORT = ROOT / "artifacts" / "reports" / "source-byte-receipt-validation-report.json"
BATCH_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-ingest-rev{REV}.json"

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
REQUIRED_BOUNDARY_PHRASES = (
    "not current voter instruction",
    "not legal advice",
    "does not prove source-byte cache completeness",
    "bundles no third-party bytes",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_capture(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print("ERROR: command failed:", " ".join(cmd), file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)
    return proc.stdout


def main() -> int:
    errors: list[str] = []
    for path, label in (
        (BUILDER, "intake manifest builder"),
        (BATCH, "batch ingest script"),
        (REPORT, "intake manifest report"),
        (SHA256SUM, "intake sha256sum file"),
        (QUEUE_REPORT, "source-byte queue report"),
        (RECEIPT_REPORT, "source-byte receipt report"),
        (BATCH_REPORT, "current source-byte batch report"),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    generated_json = run_capture([sys.executable, str(BUILDER), "--json"])
    generated_sha = run_capture([sys.executable, str(BUILDER), "--sha256sum"])
    shipped = load_json(REPORT)
    if json.loads(generated_json) != shipped:
        errors.append("source-byte cache intake manifest report is stale; run scripts/build_source_byte_cache_intake_manifest.py --write")
    if SHA256SUM.read_text(encoding="utf-8") != generated_sha:
        errors.append("source-byte cache intake sha256sum file is stale; run scripts/build_source_byte_cache_intake_manifest.py --write")

    queue = load_json(QUEUE_REPORT)
    receipt = load_json(RECEIPT_REPORT)
    batch = load_json(BATCH_REPORT)

    if shipped.get("archive_version") != VERSION:
        errors.append("intake manifest archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True:
        errors.append("intake manifest must carry synthetic_only=true")
    if shipped.get("network_io") is not False:
        errors.append("intake manifest must state network_io=false")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("intake manifest must state third_party_bytes_bundled=false")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"intake manifest boundary missing phrase: {phrase}")

    if int(shipped.get("pinned_source_count") or -1) != int(queue.get("pinned_source_count") or -2):
        errors.append("intake pinned_source_count must match acquisition queue")
    if int(shipped.get("receipt_present_count") or -1) != int(receipt.get("valid_receipt_count") or -2):
        errors.append("intake receipt_present_count must match valid receipt count")
    missing = int(shipped.get("receipt_missing_count") or -1)
    if missing != int(queue.get("receipt_missing_count") or -2):
        errors.append("intake receipt_missing_count must match acquisition queue")
    if missing != int(batch.get("candidate_source_count") or -2):
        errors.append("intake receipt_missing_count must match current batch-ingest candidates")
    if int(shipped.get("manifest_entry_count") or -1) != missing:
        errors.append("intake manifest_entry_count must equal receipt_missing_count")
    if shipped.get("queue_next_batch_matches") is not True:
        errors.append("intake next batch must match acquisition queue next_operator_batch_source_ids")
    if int(shipped.get("error_count", -1)) != 0 or shipped.get("errors"):
        errors.append("intake manifest must have zero row errors")

    rows = shipped.get("rows") or []
    if len(rows) != missing:
        errors.append("intake row count must equal receipt_missing_count")
    lines = SHA256SUM.read_text(encoding="utf-8").splitlines()
    if len(lines) != missing:
        errors.append("sha256sum line count must equal receipt_missing_count")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    seen_lines: set[str] = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("intake row is not an object")
            continue
        sid = str(row.get("source_id") or "")
        name = str(row.get("local_filename") or "")
        sha = str(row.get("expected_sha256") or "")
        entry = f"{sha}  {name}"
        if not sid:
            errors.append("intake row missing source_id")
        elif sid in seen_ids:
            errors.append(f"duplicate intake source_id: {sid}")
        seen_ids.add(sid)
        if not HEX64_RE.fullmatch(sha):
            errors.append(f"invalid expected sha256 for {sid}")
        if not name or name.startswith(".") or "/" in name or "\\" in name or ".." in name or not SAFE_RE.fullmatch(name):
            errors.append(f"unsafe local_filename for {sid}: {name!r}")
        elif name in seen_names:
            errors.append(f"duplicate local_filename in intake manifest: {name}")
        seen_names.add(name)
        expected_entry = f"{sha}  {name}"
        if idx < len(lines) and lines[idx] != expected_entry:
            errors.append(f"sha256sum file line {idx + 1} does not match row {sid}")
        if entry in seen_lines:
            errors.append(f"duplicate sha256sum entry: {entry}")
        seen_lines.add(entry)

    # Actual sha256sum file should be usable by standard tooling from a cache dir.
    # With an empty cache it should report missing files rather than silently pass.
    if rows:
        with tempfile.TemporaryDirectory(prefix="source-byte-intake-sha256sum-") as td:
            tmp = Path(td)
            proc = subprocess.run(
                ["sha256sum", "-c", str(SHA256SUM)],
                cwd=tmp,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if proc.returncode == 0:
                errors.append("sha256sum -c unexpectedly passed against an empty cache")
            if "No such file" not in proc.stderr and "FAILED open or read" not in proc.stdout + proc.stderr:
                errors.append("sha256sum -c empty-cache failure did not look like missing external bytes")

            # Use the first real intake filename with wrong bytes and prove batch ingest blocks it.
            first = rows[0]
            (tmp / str(first["local_filename"])).write_text("definitely wrong source bytes\n", encoding="utf-8")
            report = json.loads(run_capture([
                sys.executable,
                str(BATCH),
                "--cache-dir",
                str(tmp),
                "--scope",
                "missing-receipts",
                "--json",
            ]))
            if int(report.get("mismatched_cache_file_count") or 0) != 1:
                errors.append("actual intake filename wrong-byte smoke did not report one mismatch")
            if int(report.get("would_write_receipt_count") or 0) != 0:
                errors.append("actual intake filename wrong-byte smoke would write a receipt")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: source-byte cache intake manifest ({VERSION}, entries={missing}, sha256sum={SHA256SUM.relative_to(ROOT)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
