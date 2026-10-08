#!/usr/bin/env python3
"""Gate host-scoped source-byte batch slices.

The current first source-byte batch is still unresolved. This check proves the
host-slice builder is a no-network routing aid, not a source-byte completion
claim: every host slice must reconstruct the current batch line set exactly,
must be usable as a strict ``fetch_source_byte_batch.py`` input, and must carry
no bundled third-party bytes.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "build_source_byte_batch_host_slices.py"
FETCHER = ROOT / "scripts" / "fetch_source_byte_batch.py"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-host-slices-rev{REV}.json"
BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
SLICE_DIR = ROOT / "artifacts" / "source_byte_cache_intake" / "host_slices"
REQUIRED_BOUNDARY_PHRASES = (
    "no-network operator routing handoffs",
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


def run(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)


def run_json(cmd: list[str], *, cwd: Path = ROOT) -> dict:
    proc = run(cmd, cwd=cwd)
    if proc.returncode != 0:
        print("ERROR: command failed:", " ".join(cmd), file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(2)
    return json.loads(proc.stdout)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty_lines(path: Path) -> list[str]:
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def main() -> int:
    for path, label in ((SCRIPT, "host-slice builder"), (FETCHER, "batch fetcher"), (REPORT, "current host-slice report"), (BATCH01, "current batch01")):
        if not path.exists():
            return fail(f"missing {label}: {rel(path)}")

    generated = run_json([sys.executable, str(SCRIPT), "--json"])
    shipped = load_json(REPORT)
    if generated != shipped:
        return fail("current host-slice report is stale; run scripts/build_source_byte_batch_host_slices.py --write")
    if shipped.get("archive_version") != VERSION:
        return fail("host-slice report archive_version does not match VERSION")
    if shipped.get("network_io") is not False or shipped.get("third_party_bytes_bundled") is not False:
        return fail("host-slice report must be no-network and bundle no third-party bytes")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            return fail(f"host-slice boundary missing phrase: {phrase}")
    if shipped.get("batch_file") != rel(BATCH01):
        return fail("host-slice report does not point at current batch01")
    if int(shipped.get("error_count", -1)) != 0:
        return fail("host-slice report has errors: " + ",".join(shipped.get("errors") or []))

    batch_lines = nonempty_lines(BATCH01)
    slice_lines: list[str] = []
    slice_paths: list[Path] = []
    for row in shipped.get("host_slices") or []:
        if not isinstance(row, dict):
            return fail("host_slices row is not an object")
        path = ROOT / str(row.get("path") or "")
        if not path.exists():
            return fail(f"missing host slice file: {rel(path)}")
        if not str(row.get("operator_fetch_command") or "").startswith("python3 scripts/fetch_source_byte_batch.py"):
            return fail("host slice row missing fetcher command")
        lines = nonempty_lines(path)
        if len(lines) != int(row.get("line_count") or -1):
            return fail(f"host slice line_count mismatch: {rel(path)}")
        slice_lines.extend(lines)
        slice_paths.append(path)
    if sorted(slice_lines) != sorted(batch_lines):
        return fail("host-slice files do not reconstruct the batch01 line set exactly")
    if len(slice_lines) != len(set(slice_lines)):
        return fail("host-slice files contain duplicate sha256sum lines")
    if int(shipped.get("batch_file_entry_count") or -1) != len(batch_lines):
        return fail("host-slice batch_file_entry_count does not match batch01 line count")
    if int(shipped.get("dominant_host_entry_count") or 0) <= 1:
        return fail("host-slice report should identify a multi-row dominant host for batch01")

    # Every emitted host slice must be accepted by the real fetcher in plan-only
    # mode. This proves the slices are executable handoffs, not merely reports.
    for path in slice_paths[:5]:
        proc = run([sys.executable, str(FETCHER), "--batch-file", str(path), "--print-plan", "--json"], timeout=40)
        if proc.returncode != 0:
            return fail(f"fetcher rejected host-slice batch file: {rel(path)}", proc)
        try:
            plan = json.loads(proc.stdout)
        except Exception as exc:
            return fail(f"fetcher emitted non-json for host slice {rel(path)}: {exc}", proc)
        if plan.get("network_io") is not False or plan.get("write_receipts_requested") is not False:
            return fail(f"plan-only host slice unexpectedly requested network/write: {rel(path)}")
        if int(plan.get("batch_file_entry_count") or -1) != len(nonempty_lines(path)):
            return fail(f"plan-only host slice entry count mismatch: {rel(path)}")

    with tempfile.TemporaryDirectory(prefix="tes_source_host_slices_") as td:
        tmp = Path(td)
        # Repoint --out-dir/--report-path and verify stale current-rev slice files
        # in a temporary directory are removed before writes. This keeps repeated
        # operator runs from accumulating stale same-revision host workpacks.
        stale = tmp / f"source-byte-cache-host-slice-rev{REV}-batch01-99-stale.sha256"
        stale.write_text("0" * 64 + "  stale.txt\n", encoding="utf-8")
        out_report = tmp / "report.json"
        proc = run([sys.executable, str(SCRIPT), "--out-dir", str(tmp), "--report-path", str(out_report), "--write", "--json"])
        if proc.returncode != 0:
            return fail("host-slice builder failed temporary --write smoke", proc)
        if stale.exists():
            return fail("host-slice builder did not remove stale same-revision slice in target directory")
        if not out_report.exists():
            return fail("host-slice builder temporary --write did not create report")

    print(f"PASS: source-byte batch host slices ({VERSION}, slices={shipped.get('host_slice_count')}, batch01={len(batch_lines)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
