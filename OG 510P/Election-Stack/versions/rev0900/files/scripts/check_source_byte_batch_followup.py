#!/usr/bin/env python3
"""Gate the source-byte batch follow-up builder.

The network-capable fetcher can produce partial reports. This check proves the
no-network follow-up builder can turn a current attempt report into a strict next
`.sha256` handoff, and that it separates byte-fetch follow-up from receipt-only
follow-up without hand-editing governed batch files.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
SCRIPT = ROOT / "scripts" / "build_source_byte_batch_followup.py"
FETCH_PLAN = ROOT / "artifacts" / "reports" / f"source-byte-batch-fetch-plan-rev{REV}.json"
REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-followup-rev{REV}.json"
BATCH01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
FOLLOWUP = ROOT / "artifacts" / "source_byte_cache_intake" / "followups" / f"source-byte-cache-followup-rev{REV}-batch01-unresolved.sha256"

REQUIRED_BOUNDARY_PHRASES = (
    "no-network resumability handoff",
    "bundles no third-party bytes",
    "not current voter instruction",
    "not legal advice",
    "not source-byte cache completeness",
)


def run(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)


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


def fail(msg: str, proc: subprocess.CompletedProcess[str] | None = None) -> int:
    print("FAIL:", msg, file=sys.stderr)
    if proc is not None:
        if proc.stdout:
            print(proc.stdout, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    return 2


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def fixture_lock_and_batch(tmp: Path) -> tuple[Path, Path, str, str, str]:
    sha_a = sha256_text("alpha bytes\n")
    sha_b = sha256_text("bravo bytes\n")
    sha_c = sha256_text("charlie bytes\n")
    lock = tmp / "external-sources.toml"
    lock.write_text(
        f"""
[[source]]
id = "fixture_alpha"
url = "https://example.invalid/alpha.txt"
retrieved = "2026-06-13"
sha256 = "{sha_a}"
local_filename = "alpha.txt"
tags = ["eac"]
note = "temporary smoke fixture"

[[source]]
id = "fixture_bravo"
url = "https://example.invalid/bravo.txt"
retrieved = "2026-06-13"
sha256 = "{sha_b}"
local_filename = "bravo.txt"
tags = ["eac"]
note = "temporary smoke fixture"

[[source]]
id = "fixture_charlie"
url = "https://example.invalid/charlie.txt"
retrieved = "2026-06-13"
sha256 = "{sha_c}"
local_filename = "charlie.txt"
tags = ["eac"]
note = "temporary smoke fixture"
""".lstrip(),
        encoding="utf-8",
    )
    batch = tmp / "batch01.sha256"
    batch.write_text(f"{sha_a}  alpha.txt\n{sha_b}  bravo.txt\n{sha_c}  charlie.txt\n", encoding="utf-8")
    return lock, batch, sha_a, sha_b, sha_c


def main() -> int:
    for path, label in ((SCRIPT, "follow-up builder"), (FETCH_PLAN, "fetch plan report"), (REPORT, "follow-up report"), (BATCH01, "current batch01"), (FOLLOWUP, "current follow-up sha256sum")):
        if not path.exists():
            return fail(f"missing {label}: {path.relative_to(ROOT)}")

    generated = run_json([sys.executable, str(SCRIPT), "--json"])
    shipped = load_json(REPORT)
    if generated != shipped:
        return fail("current source-byte batch follow-up report is stale; run scripts/build_source_byte_batch_followup.py --write")

    if shipped.get("archive_version") != VERSION:
        return fail("follow-up report archive_version does not match VERSION")
    if shipped.get("network_io") is not False or shipped.get("third_party_bytes_bundled") is not False:
        return fail("follow-up report must be no-network and no bundled third-party bytes")
    boundary = str(shipped.get("boundary") or "").lower()
    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in boundary:
            return fail(f"follow-up boundary missing phrase: {phrase}")
    if shipped.get("attempt_report") != f"artifacts/reports/source-byte-batch-fetch-plan-rev{REV}.json":
        return fail("follow-up report does not point at the current fetch plan report")
    if int(shipped.get("original_batch_entry_count") or 0) <= 0:
        return fail("follow-up original batch entry count must be positive")
    if int(shipped.get("followup_entry_count") or -1) != int(shipped.get("original_batch_entry_count") or -2):
        return fail("plan-only current follow-up should preserve all unresolved batch entries")
    if int(shipped.get("receipt_action_required_count", -1)) != 0:
        return fail("plan-only current follow-up should not require receipt-only actions")
    if FOLLOWUP.read_text(encoding="utf-8") != BATCH01.read_text(encoding="utf-8"):
        return fail("plan-only current follow-up sha256sum must equal current batch01")

    with tempfile.TemporaryDirectory(prefix="tes_source_followup_") as td:
        tmp = Path(td)
        lock, batch, sha_a, sha_b, sha_c = fixture_lock_and_batch(tmp)
        attempt = tmp / "attempt.json"
        write_json(
            attempt,
            {
                "archive_version": VERSION,
                "status_counts": {"cache_hit_match": 1, "error": 1, "fetched_match": 1},
                "rows": [
                    {
                        "source_id": "fixture_alpha",
                        "expected_sha256": sha_a,
                        "local_filename": "alpha.txt",
                        "status": "fetched_match",
                        "receipt_written": True,
                        "receipt_preexisting": False,
                    },
                    {
                        "source_id": "fixture_bravo",
                        "expected_sha256": sha_b,
                        "local_filename": "bravo.txt",
                        "status": "cache_hit_match",
                        "receipt_written": False,
                        "receipt_preexisting": False,
                    },
                    {
                        "source_id": "fixture_charlie",
                        "expected_sha256": sha_c,
                        "local_filename": "charlie.txt",
                        "status": "error",
                        "receipt_written": False,
                        "receipt_preexisting": False,
                    },
                ],
            },
        )
        out_sha = tmp / "followup.sha256"
        out_report = tmp / "followup.json"
        report = run_json([
            sys.executable,
            str(SCRIPT),
            "--batch-file",
            str(batch),
            "--attempt-report",
            str(attempt),
            "--lockfile",
            str(lock),
            "--followup-sha256sum-path",
            str(out_sha),
            "--report-path",
            str(out_report),
            "--write",
            "--json",
        ])
        if int(report.get("followup_entry_count") or -1) != 1:
            return fail("fixture follow-up should contain exactly one unresolved fetch row")
        if int(report.get("receipt_action_required_count") or -1) != 1:
            return fail("fixture follow-up should identify exactly one receipt-only action")
        if report.get("completed_source_ids") != ["fixture_alpha"]:
            return fail("fixture completed source ids should contain only fixture_alpha")
        if report.get("receipt_action_required_source_ids") != ["fixture_bravo"]:
            return fail("fixture receipt-only source ids should contain only fixture_bravo")
        if out_sha.read_text(encoding="utf-8") != f"{sha_c}  charlie.txt\n":
            return fail("fixture follow-up sha256sum did not contain only unresolved charlie row")

        stale = tmp / "stale.json"
        stale_obj = load_json(attempt)
        stale_obj["archive_version"] = "v000"
        write_json(stale, stale_obj)
        proc = run([
            sys.executable,
            str(SCRIPT),
            "--batch-file",
            str(batch),
            "--attempt-report",
            str(stale),
            "--lockfile",
            str(lock),
            "--followup-sha256sum-path",
            str(tmp / "stale.sha256"),
            "--report-path",
            str(tmp / "stale-out.json"),
        ])
        if proc.returncode == 0:
            return fail("follow-up builder accepted a stale attempt report without --allow-version-mismatch", proc)

    print(f"PASS: source-byte batch follow-up ({VERSION}, unresolved={shipped.get('followup_entry_count')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
