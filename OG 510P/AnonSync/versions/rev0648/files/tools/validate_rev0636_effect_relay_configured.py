#!/usr/bin/env python3
"""Rev0636 package validator: configured effect relay boundary."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0636" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0636-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0636" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
PENDING_FORMAT = "anonsync-sqlite-effect-pending-report-v5-outbox-claim"
RELAY_FORMAT = "anonsync-sqlite-effect-relay-report-v2-configured-boundary"
DOWNSTREAM_FORMAT = "anonsync-relay-downstream-store-v1"
CONFIG_FORMAT = "anonsync-effect-relay-adapter-config-v1"
ADAPTER_KIND = "local-sqlite-downstream-journal"


def run(args: list[object], *, expect_codes: set[int] | None = None, expect_ok: bool | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run([str(a) for a in args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if expect_codes is None:
        expect_codes = {0} if expect_ok is not False else set(range(1, 256))
    if proc.returncode not in expect_codes:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        raise AssertionError(f"command exit {proc.returncode}, expected {sorted(expect_codes)}: {' '.join(map(str, args))}")
    return proc


def load_json(path: pathlib.Path) -> dict[str, object]:
    return json.loads(path.read_text())


def is_lower_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def b64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def make_trust_and_key(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, str, str]:
    kid = "rev0636-validator-root"
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub = key.public_key().public_numbers()
    key_path = tmp / "relay-signer.pem"
    key_path.write_bytes(private_pem)
    trust = {
        "format": "anonsync-effect-transition-trust-profile-v2",
        "revision_id": "rev0636-validator",
        "verification_time": "2026-06-18T02:46:30Z",
        "max_intent_age_seconds": 600,
        "required_intent_subject": "sqlite-wal-effect-terminal-transition",
        "allowed_terminal_states": ["applied", "failed", "compensated"],
        "trusted_signers": [{
            "kid": kid,
            "alg": "RS256",
            "status": "trusted",
            "not_before": "2026-06-18T00:00:00Z",
            "not_after": "2026-06-19T00:00:00Z",
            "jwk": {
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": b64url_uint(pub.n),
                "e": b64url_uint(pub.e),
            },
        }],
        "blocked_claim": "rev0636 validator trust profile only; not production PKI or HSM custody.",
    }
    trust_path = tmp / "relay-trust.json"
    trust_text = json.dumps(trust, indent=2, sort_keys=True) + "\n"
    trust_path.write_text(trust_text)
    return key_path, trust_path, hashlib.sha256(trust_text.encode()).hexdigest(), kid


def write_relay_config(
    path: pathlib.Path,
    downstream: pathlib.Path,
    key: pathlib.Path,
    trust: pathlib.Path,
    trust_sha: str,
    kid: str,
    *,
    adapter_id: str = "validator-configured-A",
    worker: str = "validator-configured-worker",
    lease: int = 60,
    terminal: str = "applied",
    allow_crash: bool = True,
) -> str:
    cfg = {
        "format": CONFIG_FORMAT,
        "revision_id": "rev0636-validator",
        "adapter_id": adapter_id,
        "adapter_kind": ADAPTER_KIND,
        "downstream_store_path": str(downstream),
        "worker_id": worker,
        "lease_seconds": lease,
        "terminal_state": terminal,
        "signer_private_key_pem_path": str(key),
        "signer_kid": kid,
        "transition_trust_profile_path": str(trust),
        "transition_trust_profile_sha256": trust_sha,
        "debug_inject_crash_after_downstream_allowed": allow_crash,
        "blocked_claim": "validator adapter config only; request paths must not select signer/trust/downstream in production.",
    }
    text = json.dumps(cfg, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def assert_manifest_hashes() -> None:
    manifest = load_json(MANIFEST)
    if manifest["format"] != "anonsync-slim-cube-manifest-v1" or manifest["revision_id"] != "rev0636":
        raise AssertionError("active slim-cube manifest format/revision mismatch")
    if manifest["capability_manifest"] != "gateway/rev0636-cpp-ledger-backend-capabilities.json":
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
    if caps["format"] != "anonsync-ledger-backend-capabilities-v31":
        raise AssertionError("capability format is not v31")
    if caps["revision_id"] != "rev0636" or caps["parent_revision"] != "rev0635":
        raise AssertionError("capability lineage mismatch")
    sw = caps["backends"]["sqlite-wal"]
    required = {
        "ledger_schema_version": 10,
        "effect_pending_report_format": PENDING_FORMAT,
        "effect_relay_report_format": RELAY_FORMAT,
        "effect_relay_downstream_store_format": DOWNSTREAM_FORMAT,
        "effect_relay_adapter_config_format": CONFIG_FORMAT,
        "effect_relay_adapter_kind": ADAPTER_KIND,
        "snapshot_restore_minimum_capability_version": 31,
    }
    for key_name, expected in required.items():
        if sw.get(key_name) != expected:
            raise AssertionError(f"capability {key_name} mismatch: {sw.get(key_name)!r}")
    for key_name in [
        "effect_relay_once_command_supported",
        "effect_relay_signed_transition_intent_required",
        "effect_relay_transition_trust_profile_digest_pin_required",
        "effect_relay_reconciliation_after_downstream_apply_gap_supported",
        "effect_relay_injected_crash_after_downstream_selftest_required",
        "effect_relay_downstream_prepared_evidence_mismatch_rejected",
        "effect_relay_adapter_config_digest_pin_required",
        "effect_relay_operator_configured_boundary_required",
        "effect_relay_config_binds_adapter_worker_lease_terminal_signer_trust_downstream",
        "effect_relay_legacy_cli_marked_nonproduction",
        "effect_relay_configured_command_supported",
        "effect_relay_config_digest_mismatch_rejected_before_claim",
        "effect_relay_config_report_binds_adapter_identity_and_config_sha256",
    ]:
        if sw.get(key_name) is not True:
            raise AssertionError(f"capability {key_name} is not true")


def seed_single_effect_ledger(tmp: pathlib.Path, name: str) -> pathlib.Path:
    ledger = tmp / f"{name}.sqlite"
    report = tmp / f"{name}-report.json"
    one_case = tmp / f"{name}-one-case.jsonl"
    one_case.write_text(CASES.read_text().splitlines()[0] + "\n")
    run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", one_case,
        "--contracts", CONTRACTS,
        "--ledger", ledger,
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", CAPS,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", report,
    ])
    counters = load_json(report)["counters"]
    if counters["ledger_effect_outbox_reserved"] != 1 or counters["ledger_effect_outbox_inflight"] != 0 or counters["ledger_effect_outbox_terminal"] != 0:
        raise AssertionError(f"unexpected initial single-effect outbox counters: {counters}")
    return ledger


def relay_once_configured(ledger: pathlib.Path, config: pathlib.Path, config_sha: str, report: pathlib.Path, now: int, *, crash: bool = False, expect: set[int] = {0}) -> dict[str, object]:
    args: list[object] = [
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", report,
        "--ledger-effect-relay-config", config,
        "--ledger-effect-relay-config-sha256", config_sha,
        "--ledger-effect-relay-now-epoch", now,
    ]
    if crash:
        args.append("--ledger-effect-relay-inject-crash-after-downstream")
    proc = run(args, expect_codes=expect)
    if report.exists():
        return load_json(report)
    return {"stdout": proc.stdout, "stderr": proc.stderr}


def pending_counts(ledger: pathlib.Path, tmp: pathlib.Path, suffix: str) -> tuple[int, int, int]:
    report = tmp / f"pending-{suffix}.json"
    run([BIN, "--ledger", ledger, "--ledger-effect-pending-report", report])
    got = load_json(report)
    if got["format"] != PENDING_FORMAT:
        raise AssertionError("pending report format mismatch")
    return (got["outbox_reserved_count"], got["outbox_inflight_count"], got["terminal_effect_count"])


def assert_relay_recovery(tmp: pathlib.Path) -> None:
    key, trust, trust_sha, kid = make_trust_and_key(tmp)
    ledger = seed_single_effect_ledger(tmp, "recovery-ledger")
    downstream = tmp / "downstream.sqlite"
    config = tmp / "relay-config.json"
    config_sha = write_relay_config(config, downstream, key, trust, trust_sha, kid, adapter_id="validator-configured-A", worker="validator-A")

    crash = relay_once_configured(ledger, config, config_sha, tmp / "relay-crash.json", 1781750700, crash=True, expect={75})
    if crash["format"] != RELAY_FORMAT or crash["revision_id"] != "rev0636":
        raise AssertionError("crash relay report identity mismatch")
    relay_cfg = crash["relay_adapter_config"]
    if relay_cfg["format"] != CONFIG_FORMAT or relay_cfg["adapter_id"] != "validator-configured-A" or relay_cfg["adapter_kind"] != ADAPTER_KIND:
        raise AssertionError(f"relay report did not bind adapter identity: {relay_cfg}")
    if relay_cfg["config_sha256"] != config_sha or relay_cfg["digest_pin_verified"] is not True:
        raise AssertionError(f"relay report did not bind digest pin: {relay_cfg}")
    if crash["claimed"] is not True or crash["downstream_touched"] is not True or crash["transition_closed"] is not False:
        raise AssertionError(f"unexpected crash report booleans: {crash}")
    if crash["downstream"]["inserted"] is not True or crash["downstream"]["replayed_existing"] is not False or crash["downstream"]["observation_count"] != 1:
        raise AssertionError(f"unexpected downstream crash report: {crash['downstream']}")
    if pending_counts(ledger, tmp, "after-crash") != (0, 1, 0):
        raise AssertionError("crash left unexpected pending/outbox counts")

    early = relay_once_configured(ledger, config, config_sha, tmp / "relay-early.json", 1781750730)
    if early["claimed"] is not False or early["downstream_touched"] is not False:
        raise AssertionError("fresh inflight lease was incorrectly claimed")

    recovered = relay_once_configured(ledger, config, config_sha, tmp / "relay-recovered.json", 1781750761)
    if recovered["claimed"] is not True or recovered["transition_closed"] is not True:
        raise AssertionError(f"recovery did not close terminally: {recovered}")
    if recovered["claim"]["previous_outbox_state"] != "inflight" or recovered["claim"]["dispatch_attempts"] != 2:
        raise AssertionError("recovery did not stale-reclaim the inflight row")
    if recovered["downstream"]["replayed_existing"] is not True or recovered["downstream"]["observation_count"] != 2:
        raise AssertionError("recovery did not replay existing downstream evidence")
    if recovered["downstream"]["result_digest_sha256"] != crash["downstream"]["result_digest_sha256"]:
        raise AssertionError("recovery changed downstream result digest")
    if not is_lower_sha256(recovered["transition"]["transition_intent_id"]):
        raise AssertionError("missing signed relay transition evidence")
    if config_sha not in recovered["transition"].get("transition_reason", ""):
        raise AssertionError("signed transition reason did not include adapter config digest")
    if pending_counts(ledger, tmp, "after-recovery") != (0, 0, 1):
        raise AssertionError("recovery left unexpected pending/outbox counts")

    # The configured boundary must reject content drift before claiming any work.
    config.write_text(config.read_text() + "\n")
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-config-tamper.json",
        "--ledger-effect-relay-config", config,
        "--ledger-effect-relay-config-sha256", config_sha,
        "--ledger-effect-relay-now-epoch", 1781750762,
    ], expect_codes=set(range(1, 256)))
    if "digest pin" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("adapter config digest mismatch was not clearly rejected")

    # Start a separate crash gap, then tamper with the downstream journal. The configured relay must refuse to sign terminal evidence.
    tamper_ledger = seed_single_effect_ledger(tmp, "tamper-ledger")
    tamper_downstream = tmp / "tamper-downstream.sqlite"
    tamper_config = tmp / "tamper-config.json"
    tamper_sha = write_relay_config(tamper_config, tamper_downstream, key, trust, trust_sha, kid, adapter_id="validator-configured-B", worker="validator-B")
    tamper_crash = relay_once_configured(tamper_ledger, tamper_config, tamper_sha, tmp / "relay-tamper-crash.json", 1781750800, crash=True, expect={75})
    tampered_effect = tamper_crash["claim"]["effect_idempotency_key"]
    con = sqlite3.connect(tamper_downstream)
    try:
        con.execute("UPDATE downstream_effects SET result_digest_sha256=? WHERE effect_idempotency_key=?", ("0" * 64, tampered_effect))
        con.commit()
    finally:
        con.close()
    proc = run([
        BIN,
        "--ledger", tamper_ledger,
        "--ledger-effect-relay-report", tmp / "relay-tamper-recover.json",
        "--ledger-effect-relay-config", tamper_config,
        "--ledger-effect-relay-config-sha256", tamper_sha,
        "--ledger-effect-relay-now-epoch", 1781750861,
    ], expect_codes=set(range(1, 256)))
    if "result digest" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("tampered downstream result digest was not clearly rejected")


def assert_downgrade_rejected(tmp: pathlib.Path) -> None:
    downgraded = tmp / "rev0636-downgraded-capabilities.json"
    caps = load_json(CAPS)
    caps["format"] = "anonsync-ledger-backend-capabilities-v30"
    caps["revision_id"] = "rev0635-forged"
    caps["backends"]["sqlite-wal"]["snapshot_restore_minimum_capability_version"] = 30
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
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "v31" not in msg and "unsupported relay report format" not in msg and "capability" not in msg:
        raise AssertionError("downgrade rejection was not clearly capability-related")


def assert_v31_missing_config_field_rejected(tmp: pathlib.Path) -> None:
    bad_caps = tmp / "rev0636-missing-config-capabilities.json"
    caps = load_json(CAPS)
    caps["backends"]["sqlite-wal"]["effect_relay_adapter_config_digest_pin_required"] = False
    bad_caps.write_text(json.dumps(caps, indent=2, sort_keys=True))
    one_case = tmp / "cap-one-case.jsonl"
    one_case.write_text(CASES.read_text().splitlines()[0] + "\n")
    proc = run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", one_case,
        "--contracts", CONTRACTS,
        "--ledger", tmp / "bad-v31.sqlite",
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", bad_caps,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", tmp / "bad-v31-report.json",
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "v31" not in msg and "configured" not in msg and "capability" not in msg:
        raise AssertionError("v31 missing config-boundary field rejection was not clearly capability-related")


def main() -> int:
    if not BIN.exists():
        raise AssertionError(f"missing packaged binary: {BIN}")
    if not os.access(BIN, os.X_OK):
        raise AssertionError(f"packaged binary is not executable: {BIN}")
    assert_manifest_hashes()
    assert_caps()
    help_text = run([BIN, "--help"]).stdout
    for needle in [
        "--ledger-effect-relay-config",
        "--ledger-effect-relay-config-sha256",
        "--selftest-ledger-sqlite-effect-relay-configured",
    ]:
        if needle not in help_text:
            raise AssertionError(f"configured relay CLI/help surface missing: {needle}")
    run([BIN, "--selftest-ledger-sqlite-effect-relay-configured"])
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0636-validator-") as td:
        tmp = pathlib.Path(td)
        assert_relay_recovery(tmp)
        assert_downgrade_rejected(tmp)
        assert_v31_missing_config_field_rejected(tmp)
    print(json.dumps({
        "validator": "rev0636-effect-relay-configured-boundary",
        "status": "passed",
        "binary": str(BIN.relative_to(ROOT)),
        "capabilities": str(CAPS.relative_to(ROOT)),
        "adapter_config_format": CONFIG_FORMAT,
        "relay_report_format": RELAY_FORMAT,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
