#!/usr/bin/env python3
"""Rev0634 package validator: SQLite effect_outbox worker claim/lease boundary."""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0634" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0634-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0634" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
PENDING_FORMAT = "anonsync-sqlite-effect-pending-report-v5-outbox-claim"
CLAIM_FORMAT = "anonsync-sqlite-effect-outbox-claim-v1"


def run(args: list[object], *, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run([str(a) for a in args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if expect_ok and proc.returncode != 0:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        raise AssertionError(f"command failed with exit {proc.returncode}: {' '.join(map(str, args))}")
    if not expect_ok and proc.returncode == 0:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        raise AssertionError(f"command unexpectedly succeeded: {' '.join(map(str, args))}")
    return proc


def load_json(path: pathlib.Path) -> dict[str, object]:
    return json.loads(path.read_text())


def is_lower_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def sqlite_backup(src: pathlib.Path, dst: pathlib.Path) -> None:
    src_con = sqlite3.connect(src)
    try:
        dst_con = sqlite3.connect(dst)
        try:
            src_con.backup(dst_con)
        finally:
            dst_con.close()
    finally:
        src_con.close()



def assert_manifest_hashes() -> None:
    manifest = load_json(MANIFEST)
    if manifest["format"] != "anonsync-slim-cube-manifest-v1" or manifest["revision_id"] != "rev0634":
        raise AssertionError("active slim-cube manifest format/revision mismatch")
    if manifest["capability_manifest"] != "gateway/rev0634-cpp-ledger-backend-capabilities.json":
        raise AssertionError("active slim-cube manifest points at the wrong capability manifest")
    for row in manifest["files"]:
        path = ROOT / row["path"]
        if not path.exists():
            raise AssertionError(f"manifest file missing: {row['path']}")
        data = path.read_bytes()
        if len(data) != row["size_bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"manifest hash/size mismatch: {row['path']}")

def assert_caps() -> None:
    caps = load_json(CAPS)
    if caps["format"] != "anonsync-ledger-backend-capabilities-v29":
        raise AssertionError("capability format is not v29")
    if caps["revision_id"] != "rev0634" or caps["parent_revision"] != "rev0633":
        raise AssertionError("capability lineage mismatch")
    sw = caps["backends"]["sqlite-wal"]
    required = {
        "ledger_schema_version": 10,
        "effect_pending_report_format": PENDING_FORMAT,
        "effect_outbox_claim_material_version": CLAIM_FORMAT,
        "snapshot_restore_minimum_capability_version": 29,
    }
    for key, expected in required.items():
        if sw.get(key) != expected:
            raise AssertionError(f"capability {key} mismatch: {sw.get(key)!r}")
    for key in ["effect_outbox_inflight_lease_supported", "effect_outbox_stale_lease_reclaim_supported", "snapshot_readonly_verifier_checks_effect_outbox_claims"]:
        if sw.get(key) is not True:
            raise AssertionError(f"capability {key} is not true")


def seed_fixture_ledger(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    ledger = tmp / "rev0634-validator-ledger.sqlite"
    report = tmp / "rev0634-validator-report.json"
    run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", CASES,
        "--contracts", CONTRACTS,
        "--ledger", ledger,
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", CAPS,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", report,
    ])
    counters = load_json(report)["counters"]
    if counters["ledger_effect_outbox_reserved"] != 326 or counters["ledger_effect_outbox_inflight"] != 0 or counters["ledger_effect_outbox_terminal"] != 0:
        raise AssertionError(f"unexpected initial outbox counters: {counters}")
    return ledger, report


def assert_schema_and_initial_rows(ledger: pathlib.Path) -> None:
    con = sqlite3.connect(ledger)
    try:
        schema = con.execute("SELECT schema_version FROM backend_profile WHERE id=1").fetchone()[0]
        if schema != 10:
            raise AssertionError(f"backend schema mismatch: {schema}")
        cols = [row[1] for row in con.execute("PRAGMA table_info(effect_outbox)")]
        for col in ["dispatch_attempts", "worker_claim_id", "worker_id", "claimed_at_epoch", "lease_expires_at_epoch"]:
            if col not in cols:
                raise AssertionError(f"missing effect_outbox claim column: {col}")
        states = dict(con.execute("SELECT outbox_state, COUNT(*) FROM effect_outbox GROUP BY outbox_state"))
        if states != {"reserved": 326}:
            raise AssertionError(f"initial outbox state mismatch: {states}")
        bad_claim_metadata = con.execute("SELECT COUNT(*) FROM effect_outbox WHERE dispatch_attempts<>0 OR worker_claim_id<>'' OR worker_id<>'' OR claimed_at_epoch<>0 OR lease_expires_at_epoch<>0").fetchone()[0]
        if bad_claim_metadata:
            raise AssertionError("reserved rows unexpectedly carry claim metadata")
    finally:
        con.close()


def claim_one(ledger: pathlib.Path, tmp: pathlib.Path, name: str, worker: str, now: int, lease: int) -> dict[str, object]:
    path = tmp / f"{name}.json"
    run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-outbox-claim-report", path,
        "--ledger-effect-outbox-worker-id", worker,
        "--ledger-effect-outbox-claim-now-epoch", now,
        "--ledger-effect-outbox-lease-seconds", lease,
    ])
    report = load_json(path)
    if report["format"] != CLAIM_FORMAT or report["revision_id"] != "rev0634":
        raise AssertionError("claim report format/revision mismatch")
    return report


def assert_claim(report: dict[str, object], *, effect: str | None, worker: str, previous: str, attempts: int, claimed: bool = True) -> None:
    if report["claimed"] is not claimed or report["worker_id"] != worker:
        raise AssertionError(f"claim envelope mismatch: {report}")
    claim = report["claim"]
    if claimed:
        if effect is not None and claim["effect_idempotency_key"] != effect:
            raise AssertionError("claim effect mismatch")
        if claim["previous_outbox_state"] != previous or claim["outbox_state"] != "inflight":
            raise AssertionError(f"claim state mismatch: {claim}")
        if claim["dispatch_attempts"] != attempts or not is_lower_sha256(claim["worker_claim_id"]):
            raise AssertionError(f"claim evidence mismatch: {claim}")
        if claim["lease_expires_at_epoch"] < claim["claimed_at_epoch"]:
            raise AssertionError("claim lease window inverted")


def assert_pending(ledger: pathlib.Path, tmp: pathlib.Path, reserved: int, inflight: int, terminal: int) -> dict[str, object]:
    path = tmp / f"pending-{reserved}-{inflight}-{terminal}.json"
    run([BIN, "--ledger", ledger, "--ledger-effect-pending-report", path])
    report = load_json(path)
    if report["format"] != PENDING_FORMAT:
        raise AssertionError(f"pending report format mismatch: {report['format']}")
    got = (report["outbox_reserved_count"], report["outbox_inflight_count"], report["terminal_effect_count"])
    if got != (reserved, inflight, terminal):
        raise AssertionError(f"pending/outbox counters mismatch: got {got} expected {(reserved, inflight, terminal)}")
    return report


def assert_tamper_rejected(ledger: pathlib.Path, tmp: pathlib.Path) -> None:
    tampered = tmp / "tampered-inflight.sqlite"
    sqlite_backup(ledger, tampered)
    con = sqlite3.connect(tampered)
    try:
        con.execute("UPDATE effect_outbox SET worker_claim_id='' WHERE outbox_state='inflight' LIMIT 1")
        con.commit()
    finally:
        con.close()
    proc = run([BIN, "--ledger", tampered, "--ledger-effect-pending-report", tmp / "tampered-report.json"], expect_ok=False)
    combined = (proc.stdout + proc.stderr).lower()
    if "inflight" not in combined and "claim" not in combined and "worker" not in combined:
        raise AssertionError(f"tamper rejection did not mention claim/inflight metadata: {combined}")


def assert_downgrade_rejected(tmp: pathlib.Path) -> None:
    downgraded = tmp / "rev0634-downgraded-capabilities.json"
    caps = load_json(CAPS)
    caps["format"] = "anonsync-ledger-backend-capabilities-v28"
    caps["backends"]["sqlite-wal"]["ledger_schema_version"] = 9
    caps["backends"]["sqlite-wal"]["snapshot_restore_minimum_capability_version"] = 28
    caps["backends"]["sqlite-wal"]["effect_pending_report_format"] = "anonsync-sqlite-effect-pending-report-v4-outbox"
    downgraded.write_text(json.dumps(caps, indent=2, sort_keys=True))
    proc = run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", CASES,
        "--contracts", CONTRACTS,
        "--ledger", tmp / "downgrade.sqlite",
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", downgraded,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", tmp / "downgrade-report.json",
    ], expect_ok=False)
    if "v29" not in (proc.stdout + proc.stderr):
        raise AssertionError("downgrade rejection did not name v29 requirement")


def main() -> int:
    if not BIN.exists():
        raise AssertionError(f"missing packaged binary: {BIN}")
    if not os.access(BIN, os.X_OK):
        raise AssertionError(f"packaged binary is not executable: {BIN}")
    assert_manifest_hashes()
    assert_caps()
    run([BIN, "--selftest-ledger-sqlite-effect-outbox-claim"])
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0634-validator-") as td:
        tmp = pathlib.Path(td)
        ledger, _ = seed_fixture_ledger(tmp)
        assert_schema_and_initial_rows(ledger)
        first = claim_one(ledger, tmp, "claim-a", "validator-A", 1800000000, 60)
        first_effect = first["claim"]["effect_idempotency_key"]
        assert_claim(first, effect=None, worker="validator-A", previous="reserved", attempts=1)
        assert_pending(ledger, tmp, 325, 1, 0)
        second = claim_one(ledger, tmp, "claim-b", "validator-B", 1800000001, 60)
        assert_claim(second, effect=None, worker="validator-B", previous="reserved", attempts=1)
        if second["claim"]["effect_idempotency_key"] == first_effect:
            raise AssertionError("second worker claimed the same unexpired outbox row")
        reclaim = claim_one(ledger, tmp, "reclaim", "validator-C", 1800000061, 120)
        assert_claim(reclaim, effect=first_effect, worker="validator-C", previous="inflight", attempts=2)
        if reclaim["claim"]["worker_claim_id"] == first["claim"]["worker_claim_id"]:
            raise AssertionError("stale lease reclaim reused the previous worker_claim_id")
        assert_pending(ledger, tmp, 324, 2, 0)
        bad = run([
            BIN,
            "--ledger", ledger,
            "--ledger-effect-outbox-claim-report", tmp / "bad.json",
            "--ledger-effect-outbox-worker-id", "bad\nworker",
            "--ledger-effect-outbox-claim-now-epoch", 1800000100,
            "--ledger-effect-outbox-lease-seconds", 60,
        ], expect_ok=False)
        if "control" not in (bad.stdout + bad.stderr).lower():
            raise AssertionError("bad worker id rejection did not mention control characters")
        assert_tamper_rejected(ledger, tmp)
        assert_downgrade_rejected(tmp)
    print(json.dumps({
        "validator": "rev0634-effect-outbox-claim",
        "status": "passed",
        "binary": str(BIN.relative_to(ROOT)),
        "capabilities": str(CAPS.relative_to(ROOT)),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    import os
    raise SystemExit(main())
