#!/usr/bin/env python3
"""Gate classified source-byte attempt workpacks.

The workpack report is a no-network accounting layer over DNS/fetch attempts. It
must reconstruct the current batch01 unresolved line set without turning failed
network observations into source-byte completion claims.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "build_source_byte_batch_attempt_workpacks.py"
FETCHER = ROOT / "scripts" / "fetch_source_byte_batch.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-attempt-workpacks-rev{REV}.json"
BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
REQUIRED_BOUNDARY_PHRASES = (
    "no-network retry/accounting handoffs",
    "write no receipts",
    "bundle no third-party bytes",
    "not source-byte cache completeness",
    "not current voter instruction",
    "not legal advice",
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def run(cmd: list[str], *, timeout: int = 40) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path: Path) -> list[str]:
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    if not REPORT.exists():
        return fail(f"missing current attempt-workpack report: {rel(REPORT)}")
    if not BATCH01.exists():
        return fail(f"missing current batch01 file: {rel(BATCH01)}")

    proc = run([sys.executable, str(SCRIPT), "--json"])
    if proc.returncode != 0:
        return fail("attempt-workpack builder failed", proc)
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        return fail(f"attempt-workpack builder emitted non-json: {exc}", proc)
    shipped = load_json(REPORT)
    if generated != shipped:
        return fail("attempt-workpack report is stale; run scripts/build_source_byte_batch_attempt_workpacks.py --write")

    errors: list[str] = []
    if shipped.get("archive_version") != VERSION:
        errors.append("archive_version does not match VERSION")
    if shipped.get("network_io") is not False:
        errors.append("attempt-workpack report must be no-network")
    if shipped.get("third_party_bytes_bundled") is not False:
        errors.append("attempt-workpack report must not bundle third-party bytes")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            errors.append(f"boundary missing phrase: {phrase}")
    batch_lines = lines(BATCH01)
    if int(shipped.get("batch_file_entry_count") or -1) != len(batch_lines):
        errors.append("batch_file_entry_count does not match batch01")
    rows = shipped.get("rows") or []
    if len(rows) != len(batch_lines):
        errors.append("rows must cover exactly batch01")
    class_counts = shipped.get("action_class_counts") or {}
    if sum(int(v) for v in class_counts.values()) != len(rows):
        errors.append("action_class_counts do not sum to rows")
    if int(shipped.get("unresolved_workpack_source_count") or 0) <= 0:
        errors.append("attempt-workpack report must retain unresolved source-byte work")

    reconstructed: list[str] = []
    for w in shipped.get("workpacks") or []:
        if not isinstance(w, dict):
            errors.append("workpack row is not an object")
            continue
        path = ROOT / str(w.get("path") or "")
        if not path.exists():
            errors.append(f"missing workpack file: {rel(path)}")
            continue
        wlines = lines(path)
        if len(wlines) != int(w.get("line_count") or -1):
            errors.append(f"workpack line_count mismatch: {rel(path)}")
        reconstructed.extend(wlines)
        fproc = run([sys.executable, str(FETCHER), "--batch-file", str(path), "--print-plan", "--json"], timeout=60)
        if fproc.returncode != 0:
            return fail(f"fetcher rejected attempt workpack {rel(path)}", fproc)
        try:
            plan = json.loads(fproc.stdout)
        except Exception as exc:
            return fail(f"fetcher emitted non-json for workpack {rel(path)}: {exc}", fproc)
        if plan.get("network_io") is not False or plan.get("write_receipts_requested") is not False:
            errors.append(f"plan-only fetcher unexpectedly requested network/writes for {rel(path)}")
    row_workpack_lines = [f"{r['expected_sha256']}  {r['local_filename']}" for r in rows if r.get("workpack_required") is True]
    if sorted(reconstructed) != sorted(row_workpack_lines):
        errors.append("workpack files do not reconstruct the workpack_required row line set")
    if len(reconstructed) != len(set(reconstructed)):
        errors.append("workpack files contain duplicate sha256sum lines")

    if errors:
        for err in errors:
            print("ERROR:", err, file=sys.stderr)
        return 2
    print(
        "PASS: source-byte attempt workpacks "
        f"({VERSION}, workpacks={shipped.get('workpack_count')}, classes={shipped.get('action_class_counts')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
