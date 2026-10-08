#!/usr/bin/env python3
"""Rev0637 package validator: handle-bound relay registry boundary."""
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
BIN = ROOT / "bin" / "rev0637" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0637-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0637" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
PENDING_FORMAT = "anonsync-sqlite-effect-pending-report-v5-outbox-claim"
RELAY_FORMAT = "anonsync-sqlite-effect-relay-report-v3-handle-boundary"
DOWNSTREAM_FORMAT = "anonsync-relay-downstream-store-v1"
CONFIG_FORMAT = "anonsync-effect-relay-adapter-config-v1"
REGISTRY_FORMAT = "anonsync-effect-relay-config-registry-v1"
ADAPTER_KIND = "local-sqlite-downstream-journal"
HANDLE = "payments.primary"


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


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def is_lower_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def b64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def make_trust_and_key(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, str, str]:
    kid = "rev0637-validator-root"
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
        "revision_id": "rev0637-validator",
        "verification_time": "2026-06-18T02:56:30Z",
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
        "blocked_claim": "rev0637 validator trust profile only; not production PKI or HSM custody.",
    }
    trust_path = tmp / "relay-trust.json"
    trust_text = json.dumps(trust, indent=2, sort_keys=True) + "\n"
    trust_path.write_text(trust_text)
    return key_path, trust_path, sha_text(trust_text), kid


def write_relay_config(
    path: pathlib.Path,
    downstream: pathlib.Path,
    key: pathlib.Path,
    trust: pathlib.Path,
    trust_sha: str,
    kid: str,
    *,
    adapter_id: str = "validator-handle-A",
    worker: str = "validator-handle-worker",
    lease: int = 60,
    terminal: str = "applied",
    allow_crash: bool = True,
) -> str:
    cfg = {
        "format": CONFIG_FORMAT,
        "revision_id": "rev0637-validator",
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
        "blocked_claim": "validator adapter config only; caller-facing relay must select only a handle.",
    }
    text = json.dumps(cfg, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha_text(text)


def write_registry(path: pathlib.Path, config: pathlib.Path, config_sha: str, *, handle: str = HANDLE, enabled: bool = True, duplicate: bool = False, adapter_id: str = "validator-handle-A") -> str:
    entries: list[dict[str, object]] = [{
        "handle": handle,
        "enabled": enabled,
        "adapter_id": adapter_id,
        "adapter_kind": ADAPTER_KIND,
        "adapter_config_path": str(config),
        "adapter_config_sha256": config_sha,
    }]
    if duplicate:
        entries.append({
            "handle": handle,
            "enabled": True,
            "adapter_config_path": str(config),
            "adapter_config_sha256": config_sha,
        })
    registry = {
        "format": REGISTRY_FORMAT,
        "revision_id": "rev0637-validator",
        "entries": entries,
        "blocked_claim": "validator registry only; not signed control plane or distributed configuration.",
    }
    text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha_text(text)


def assert_manifest_hashes() -> None:
    manifest = load_json(MANIFEST)
    if manifest["format"] != "anonsync-slim-cube-manifest-v1" or manifest["revision_id"] != "rev0637":
        raise AssertionError("active slim-cube manifest format/revision mismatch")
    if manifest["capability_manifest"] != "gateway/rev0637-cpp-ledger-backend-capabilities.json":
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
    if caps["format"] != "anonsync-ledger-backend-capabilities-v32":
        raise AssertionError("capability format is not v32")
    if caps["revision_id"] != "rev0637" or caps["parent_revision"] != "rev0636":
        raise AssertionError("capability lineage mismatch")
    sw = caps["backends"]["sqlite-wal"]
    required = {
        "ledger_schema_version": 10,
        "effect_pending_report_format": PENDING_FORMAT,
        "effect_relay_report_format": RELAY_FORMAT,
        "effect_relay_downstream_store_format": DOWNSTREAM_FORMAT,
        "effect_relay_adapter_config_format": CONFIG_FORMAT,
        "effect_relay_config_registry_format": REGISTRY_FORMAT,
        "effect_relay_adapter_kind": ADAPTER_KIND,
        "snapshot_restore_minimum_capability_version": 32,
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
        "effect_relay_config_registry_digest_pin_required",
        "effect_relay_handle_command_supported",
        "effect_relay_config_handle_required",
        "effect_relay_request_selects_handle_only",
        "effect_relay_registry_resolves_adapter_config_digest",
        "effect_relay_registry_rejects_missing_disabled_or_duplicate_handle",
        "effect_relay_registry_digest_mismatch_rejected_before_claim",
        "effect_relay_handle_report_binds_registry_handle_registry_sha256_and_adapter_config_sha256",
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


def relay_once_handle(ledger: pathlib.Path, registry: pathlib.Path, registry_sha: str, handle: str, report: pathlib.Path, now: int, *, crash: bool = False, expect: set[int] = {0}) -> dict[str, object]:
    args: list[object] = [
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", report,
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", handle,
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
    registry = tmp / "relay-registry.json"
    config_sha = write_relay_config(config, downstream, key, trust, trust_sha, kid)
    registry_sha = write_registry(registry, config, config_sha)

    mismatch = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-registry-mismatch.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", "0" * 64,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751300,
    ], expect_codes=set(range(1, 256)))
    if "registry digest pin" not in (mismatch.stdout + mismatch.stderr).lower():
        raise AssertionError("registry digest mismatch was not clearly rejected")
    if pending_counts(ledger, tmp, "after-registry-mismatch") != (1, 0, 0):
        raise AssertionError("registry digest mismatch changed outbox state before claim")

    crash = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-crash.json", 1781751300, crash=True, expect={75})
    if crash["format"] != RELAY_FORMAT or crash["revision_id"] != "rev0637":
        raise AssertionError("crash relay report identity mismatch")
    registry_report = crash["relay_config_registry"]
    if registry_report["format"] != REGISTRY_FORMAT or registry_report["config_handle"] != HANDLE or registry_report["registry_sha256"] != registry_sha:
        raise AssertionError(f"relay report did not bind registry handle: {registry_report}")
    if registry_report["digest_pin_verified"] is not True:
        raise AssertionError("registry digest pin was not marked verified in report")
    relay_cfg = crash["relay_adapter_config"]
    if relay_cfg["format"] != CONFIG_FORMAT or relay_cfg["adapter_id"] != "validator-handle-A" or relay_cfg["adapter_kind"] != ADAPTER_KIND:
        raise AssertionError(f"relay report did not bind adapter identity: {relay_cfg}")
    if relay_cfg["config_sha256"] != config_sha or relay_cfg["digest_pin_verified"] is not True:
        raise AssertionError(f"relay report did not bind adapter config digest pin: {relay_cfg}")
    if crash["claimed"] is not True or crash["downstream_touched"] is not True or crash["transition_closed"] is not False:
        raise AssertionError(f"unexpected crash report booleans: {crash}")
    if crash["downstream"]["inserted"] is not True or crash["downstream"]["replayed_existing"] is not False or crash["downstream"]["observation_count"] != 1:
        raise AssertionError(f"unexpected downstream crash report: {crash['downstream']}")
    if pending_counts(ledger, tmp, "after-crash") != (0, 1, 0):
        raise AssertionError("crash left unexpected pending/outbox counts")

    early = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-early.json", 1781751330)
    if early["claimed"] is not False or early["downstream_touched"] is not False:
        raise AssertionError("fresh inflight lease was incorrectly claimed")

    recovered = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-recovered.json", 1781751361)
    if recovered["claimed"] is not True or recovered["transition_closed"] is not True:
        raise AssertionError(f"recovery did not close terminally: {recovered}")
    if recovered["claim"]["previous_outbox_state"] != "inflight" or recovered["claim"]["dispatch_attempts"] != 2:
        raise AssertionError("recovery did not stale-reclaim the inflight row")
    if recovered["downstream"]["replayed_existing"] is not True or recovered["downstream"]["observation_count"] != 2:
        raise AssertionError("recovery did not replay existing downstream evidence")
    if recovered["downstream"]["result_digest_sha256"] != crash["downstream"]["result_digest_sha256"]:
        raise AssertionError("recovery changed downstream result digest")
    reason = recovered["transition"].get("transition_reason", "")
    if HANDLE not in reason or registry_sha not in reason or config_sha not in reason:
        raise AssertionError("signed transition reason did not bind handle, registry digest, and adapter config digest")
    if not is_lower_sha256(recovered["transition"]["transition_intent_id"]):
        raise AssertionError("missing signed relay transition evidence")
    if pending_counts(ledger, tmp, "after-recovery") != (0, 0, 1):
        raise AssertionError("recovery left unexpected pending/outbox counts")

    registry.write_text(registry.read_text() + "\n")
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-registry-tamper.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751362,
    ], expect_codes=set(range(1, 256)))
    if "registry digest pin" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("registry content drift was not clearly rejected")

    registry_sha = write_registry(registry, config, config_sha, enabled=False)
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-disabled.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751363,
    ], expect_codes=set(range(1, 256)))
    if "disabled" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("disabled handle was not clearly rejected")

    registry_sha = write_registry(registry, config, config_sha, duplicate=True)
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-duplicate.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751364,
    ], expect_codes=set(range(1, 256)))
    if "duplicate" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("duplicate handle was not clearly rejected")

    registry_sha = write_registry(registry, config, config_sha, handle="other.handle")
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-missing.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751365,
    ], expect_codes=set(range(1, 256)))
    if "requested handle" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("missing handle was not clearly rejected")

    tamper_ledger = seed_single_effect_ledger(tmp, "tamper-ledger")
    tamper_downstream = tmp / "tamper-downstream.sqlite"
    tamper_config = tmp / "tamper-config.json"
    tamper_registry = tmp / "tamper-registry.json"
    tamper_sha = write_relay_config(tamper_config, tamper_downstream, key, trust, trust_sha, kid, adapter_id="validator-handle-B", worker="validator-B")
    tamper_reg_sha = write_registry(tamper_registry, tamper_config, tamper_sha, adapter_id="validator-handle-B")
    tamper_crash = relay_once_handle(tamper_ledger, tamper_registry, tamper_reg_sha, HANDLE, tmp / "relay-tamper-crash.json", 1781751400, crash=True, expect={75})
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
        "--ledger-effect-relay-registry", tamper_registry,
        "--ledger-effect-relay-registry-sha256", tamper_reg_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751461,
    ], expect_codes=set(range(1, 256)))
    if "result digest" not in (proc.stdout + proc.stderr).lower():
        raise AssertionError("tampered downstream result digest was not clearly rejected")


def assert_downgrade_rejected(tmp: pathlib.Path) -> None:
    downgraded = tmp / "rev0637-downgraded-capabilities.json"
    caps = load_json(CAPS)
    caps["format"] = "anonsync-ledger-backend-capabilities-v31"
    caps["revision_id"] = "rev0636-forged"
    caps["backends"]["sqlite-wal"]["snapshot_restore_minimum_capability_version"] = 31
    caps["backends"]["sqlite-wal"]["effect_relay_report_format"] = "anonsync-sqlite-effect-relay-report-v2-configured-boundary"
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
    if "v32" not in msg and "capability" not in msg:
        raise AssertionError("downgrade rejection was not clearly capability-related")


def assert_v32_missing_registry_field_rejected(tmp: pathlib.Path) -> None:
    bad_caps = tmp / "rev0637-missing-registry-capabilities.json"
    caps = load_json(CAPS)
    caps["backends"]["sqlite-wal"]["effect_relay_config_registry_digest_pin_required"] = False
    bad_caps.write_text(json.dumps(caps, indent=2, sort_keys=True))
    one_case = tmp / "cap-one-case.jsonl"
    one_case.write_text(CASES.read_text().splitlines()[0] + "\n")
    proc = run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", one_case,
        "--contracts", CONTRACTS,
        "--ledger", tmp / "bad-v32.sqlite",
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", bad_caps,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", tmp / "bad-v32-report.json",
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "v32" not in msg and "registry" not in msg and "capability" not in msg:
        raise AssertionError("v32 missing registry-boundary field rejection was not clearly capability-related")


def main() -> int:
    if not BIN.exists():
        raise AssertionError(f"missing packaged binary: {BIN}")
    if not os.access(BIN, os.X_OK):
        raise AssertionError(f"packaged binary is not executable: {BIN}")
    assert_manifest_hashes()
    assert_caps()
    help_text = run([BIN, "--help"]).stdout
    for needle in [
        "--ledger-effect-relay-registry",
        "--ledger-effect-relay-registry-sha256",
        "--ledger-effect-relay-config-handle",
        "--selftest-ledger-sqlite-effect-relay-handle",
    ]:
        if needle not in help_text:
            raise AssertionError(f"handle-bound relay CLI/help surface missing: {needle}")
    run([BIN, "--selftest-ledger-sqlite-effect-relay-handle"])
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0637-validator-") as td:
        tmp = pathlib.Path(td)
        assert_relay_recovery(tmp)
        assert_downgrade_rejected(tmp)
        assert_v32_missing_registry_field_rejected(tmp)
    print(json.dumps({
        "validator": "rev0637-effect-relay-handle-boundary",
        "status": "passed",
        "binary": str(BIN.relative_to(ROOT)),
        "capabilities": str(CAPS.relative_to(ROOT)),
        "registry_format": REGISTRY_FORMAT,
        "adapter_config_format": CONFIG_FORMAT,
        "relay_report_format": RELAY_FORMAT,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
