#!/usr/bin/env python3
"""Package-level validator for rev0647 downstream provenance hardening."""
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
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0647" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0647-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0647" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
AUDIT_OUT = ROOT / "audit" / "rev0647-downstream-provenance-package-validator.json"

PENDING_FORMAT = "anonsync-sqlite-effect-pending-report-v5-outbox-claim"
RELAY_FORMAT = "anonsync-sqlite-effect-relay-report-v3-handle-boundary"
DOWNSTREAM_FORMAT = "anonsync-relay-downstream-store-v2-provenance-bound"
RESULT_MATERIAL = "anonsync-relay-downstream-result-v2-provenance-bound"
CONFIG_FORMAT = "anonsync-effect-relay-adapter-config-v1"
REGISTRY_FORMAT = "anonsync-effect-relay-config-registry-v1"
ADAPTER_KIND = "local-sqlite-downstream-journal"
HANDLE = "payments.primary"


def run(args: list[object], *, expect_codes: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    if expect_codes is None:
        expect_codes = {0}
    proc = subprocess.run([str(a) for a in args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode not in expect_codes:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        raise AssertionError(f"command exit {proc.returncode}, expected {sorted(expect_codes)}: {' '.join(map(str, args))}")
    return proc


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def b64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def write_json(path: pathlib.Path, obj: dict[str, Any]) -> str:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha_text(text)


def is_lower_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def assert_manifest_hashes() -> None:
    if not MANIFEST.exists():
        return
    manifest = load_json(MANIFEST)
    if manifest.get("revision_id") != "rev0647":
        raise AssertionError("active slim-cube manifest revision mismatch")
    if manifest.get("capability_manifest") != "gateway/rev0647-cpp-ledger-backend-capabilities.json":
        raise AssertionError("active slim-cube manifest points at the wrong capability manifest")
    if manifest.get("active_binary") != "bin/rev0647/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3":
        raise AssertionError("active slim-cube manifest points at the wrong binary")
    for row in manifest.get("files", []):
        rel = row["path"]
        path = ROOT / rel
        if not path.exists():
            raise AssertionError(f"manifest file missing: {rel}")
        data = path.read_bytes()
        if len(data) != row["size_bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"manifest hash/size mismatch: {rel}")


def assert_caps() -> None:
    caps = load_json(CAPS)
    if caps.get("format") != "anonsync-ledger-backend-capabilities-v41":
        raise AssertionError("capability format is not v41")
    if caps.get("revision_id") != "rev0647" or caps.get("parent_revision") != "rev0646":
        raise AssertionError("capability lineage mismatch")
    sw = caps["backends"]["sqlite-wal"]
    required_values = {
        "ledger_schema_version": 10,
        "effect_relay_report_format": RELAY_FORMAT,
        "effect_relay_downstream_store_format": DOWNSTREAM_FORMAT,
        "effect_relay_downstream_result_material_version": RESULT_MATERIAL,
        "effect_relay_adapter_config_format": CONFIG_FORMAT,
        "effect_relay_config_registry_format": REGISTRY_FORMAT,
        "effect_relay_adapter_kind": ADAPTER_KIND,
        "snapshot_restore_minimum_capability_version": 41,
        "effect_relay_downstream_store_schema_version": 2,
    }
    for key_name, expected in required_values.items():
        if sw.get(key_name) != expected:
            raise AssertionError(f"capability {key_name} mismatch: {sw.get(key_name)!r}")
    required_flags = [
        "effect_relay_once_command_supported",
        "effect_relay_configured_command_supported",
        "effect_relay_handle_command_supported",
        "effect_relay_config_registry_digest_pin_required",
        "effect_relay_config_handle_required",
        "effect_relay_request_selects_handle_only",
        "effect_relay_handle_report_binds_registry_handle_registry_sha256_and_adapter_config_sha256",
        "effect_relay_downstream_store_nofollow_required",
        "effect_relay_downstream_store_symlink_family_rejected",
        "effect_relay_downstream_store_wal_and_full_sync_verified",
        "effect_relay_downstream_result_digest_binds_adapter_provenance",
        "effect_relay_downstream_existing_row_provenance_mismatch_rejected",
        "effect_relay_downstream_existing_row_result_digest_binds_prepared_evidence_and_adapter_provenance",
        "ingress_sender_replay_ledger_integrated_transaction",
    ]
    for key_name in required_flags:
        if sw.get(key_name) is not True:
            raise AssertionError(f"capability {key_name} is not true")
    if caps.get("rev0647_downstream_provenance_bound_result_digest") is not True:
        raise AssertionError("top-level rev0647 provenance claim missing")
    if caps.get("rev0647_downstream_nofollow_wal_full_verified") is not True:
        raise AssertionError("top-level rev0647 downstream hardening claim missing")


def make_trust_and_key(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, str, str]:
    kid = "rev0647-validator-root"
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
        "revision_id": "rev0647-validator",
        "verification_time": "2026-06-18T03:03:00Z",
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
        "blocked_claim": "rev0647 validator trust profile only; not production PKI or HSM custody.",
    }
    trust_path = tmp / "relay-trust.json"
    return key_path, trust_path, write_json(trust_path, trust), kid


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
        "revision_id": "rev0647-validator",
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
        "blocked_claim": "rev0647 validator adapter config only; caller-facing relay must select only a handle.",
    }
    return write_json(path, cfg)


def write_registry(
    path: pathlib.Path,
    config: pathlib.Path,
    config_sha: str,
    *,
    handle: str = HANDLE,
    enabled: bool = True,
    adapter_id: str = "validator-handle-A",
) -> str:
    registry = {
        "format": REGISTRY_FORMAT,
        "revision_id": "rev0647-validator",
        "entries": [{
            "handle": handle,
            "enabled": enabled,
            "adapter_id": adapter_id,
            "adapter_kind": ADAPTER_KIND,
            "adapter_config_path": str(config),
            "adapter_config_sha256": config_sha,
        }],
        "blocked_claim": "rev0647 validator registry only; not signed control plane or distributed configuration.",
    }
    return write_json(path, registry)


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


def relay_once_handle(
    ledger: pathlib.Path,
    registry: pathlib.Path,
    registry_sha: str,
    handle: str,
    report: pathlib.Path,
    now: int,
    *,
    crash: bool = False,
    expect_codes: set[int] = {0},
) -> dict[str, Any]:
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
    proc = run(args, expect_codes=expect_codes)
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


def downstream_profile(downstream: pathlib.Path) -> tuple[str, int]:
    con = sqlite3.connect(downstream)
    try:
        return con.execute("SELECT store_format, schema_version FROM downstream_profile WHERE id=1").fetchone()
    finally:
        con.close()


def downstream_row(downstream: pathlib.Path, effect_key: str | None = None) -> dict[str, Any]:
    con = sqlite3.connect(downstream)
    con.row_factory = sqlite3.Row
    try:
        if effect_key is None:
            row = con.execute("SELECT * FROM downstream_effects").fetchone()
        else:
            row = con.execute("SELECT * FROM downstream_effects WHERE effect_idempotency_key=?", (effect_key,)).fetchone()
        if row is None:
            raise AssertionError("missing downstream_effects row")
        return dict(row)
    finally:
        con.close()


def assert_report_downstream_provenance(report: dict[str, Any], *, config_sha: str, registry_sha: str, adapter_id: str = "validator-handle-A") -> str:
    if report["format"] != RELAY_FORMAT or report["revision_id"] != "rev0647":
        raise AssertionError("relay report identity mismatch")
    registry_report = report["relay_config_registry"]
    if registry_report["format"] != REGISTRY_FORMAT or registry_report["config_handle"] != HANDLE or registry_report["registry_sha256"] != registry_sha:
        raise AssertionError(f"relay report did not bind registry handle: {registry_report}")
    if registry_report["digest_pin_verified"] is not True:
        raise AssertionError("registry digest pin was not marked verified")
    relay_cfg = report["relay_adapter_config"]
    if relay_cfg["format"] != CONFIG_FORMAT or relay_cfg["adapter_id"] != adapter_id or relay_cfg["adapter_kind"] != ADAPTER_KIND:
        raise AssertionError(f"relay report did not bind adapter identity: {relay_cfg}")
    if relay_cfg["config_sha256"] != config_sha or relay_cfg["digest_pin_verified"] is not True:
        raise AssertionError(f"relay report did not bind adapter config digest pin: {relay_cfg}")
    downstream = report["downstream"]
    expected = {
        "result_material_version": RESULT_MATERIAL,
        "adapter_id": adapter_id,
        "adapter_kind": ADAPTER_KIND,
        "adapter_config_sha256": config_sha,
        "config_handle": HANDLE,
        "registry_sha256": registry_sha,
    }
    for key_name, expected_value in expected.items():
        if downstream.get(key_name) != expected_value:
            raise AssertionError(f"downstream report {key_name} mismatch: {downstream.get(key_name)!r}")
    digest = downstream.get("result_digest_sha256")
    if not is_lower_sha256(digest):
        raise AssertionError("downstream result digest is not a lowercase sha256")
    return digest


def assert_relay_downstream_provenance(tmp: pathlib.Path) -> None:
    key, trust, trust_sha, kid = make_trust_and_key(tmp)
    ledger = seed_single_effect_ledger(tmp, "provenance-ledger")
    downstream = tmp / "downstream.sqlite"
    config = tmp / "relay-config.json"
    registry = tmp / "relay-registry.json"
    config_sha = write_relay_config(config, downstream, key, trust, trust_sha, kid)
    registry_sha = write_registry(registry, config, config_sha)

    crash = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-crash.json", 1781751300, crash=True, expect_codes={75})
    if crash["claimed"] is not True or crash["downstream_touched"] is not True or crash["transition_closed"] is not False:
        raise AssertionError(f"unexpected crash booleans: {crash}")
    digest = assert_report_downstream_provenance(crash, config_sha=config_sha, registry_sha=registry_sha)
    if crash["downstream"]["inserted"] is not True or crash["downstream"]["replayed_existing"] is not False or crash["downstream"]["observation_count"] != 1:
        raise AssertionError(f"unexpected inserted downstream report: {crash['downstream']}")
    if pending_counts(ledger, tmp, "after-crash") != (0, 1, 0):
        raise AssertionError("crash left unexpected outbox state")

    profile_format, schema_version = downstream_profile(downstream)
    if profile_format != DOWNSTREAM_FORMAT or schema_version != 2:
        raise AssertionError(f"downstream profile mismatch: {(profile_format, schema_version)}")
    row = downstream_row(downstream, crash["claim"]["effect_idempotency_key"])
    row_expected = {
        "result_material_version": RESULT_MATERIAL,
        "adapter_id": "validator-handle-A",
        "adapter_kind": ADAPTER_KIND,
        "adapter_config_sha256": config_sha,
        "config_handle": HANDLE,
        "registry_sha256": registry_sha,
        "result_digest_sha256": digest,
        "observation_count": 1,
    }
    for key_name, expected in row_expected.items():
        if row.get(key_name) != expected:
            raise AssertionError(f"downstream row {key_name} mismatch: {row.get(key_name)!r}")

    early = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-early.json", 1781751330)
    if early["claimed"] is not False or early["downstream_touched"] is not False:
        raise AssertionError("fresh inflight lease was incorrectly claimed")

    recovered = relay_once_handle(ledger, registry, registry_sha, HANDLE, tmp / "relay-recovered.json", 1781751361)
    assert_report_downstream_provenance(recovered, config_sha=config_sha, registry_sha=registry_sha)
    if recovered["claimed"] is not True or recovered["transition_closed"] is not True:
        raise AssertionError(f"recovery did not close terminally: {recovered}")
    if recovered["downstream"]["replayed_existing"] is not True or recovered["downstream"]["observation_count"] != 2:
        raise AssertionError(f"recovery did not replay existing downstream evidence: {recovered['downstream']}")
    if recovered["downstream"]["result_digest_sha256"] != digest:
        raise AssertionError("recovery changed provenance-bound downstream result digest")
    if pending_counts(ledger, tmp, "after-recovery") != (0, 0, 1):
        raise AssertionError("recovery left unexpected outbox state")


def assert_downstream_symlink_rejected_before_claim(tmp: pathlib.Path) -> None:
    key, trust, trust_sha, kid = make_trust_and_key(tmp)
    ledger = seed_single_effect_ledger(tmp, "symlink-ledger")
    real_downstream = tmp / "real-downstream.sqlite"
    real_downstream.write_bytes(b"")
    symlink_downstream = tmp / "downstream-link.sqlite"
    symlink_downstream.symlink_to(real_downstream)
    config = tmp / "relay-symlink-config.json"
    registry = tmp / "relay-symlink-registry.json"
    config_sha = write_relay_config(config, symlink_downstream, key, trust, trust_sha, kid, adapter_id="validator-symlink")
    registry_sha = write_registry(registry, config, config_sha, adapter_id="validator-symlink")
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "relay-symlink.json",
        "--ledger-effect-relay-registry", registry,
        "--ledger-effect-relay-registry-sha256", registry_sha,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751500,
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "symbolic-link" not in msg and "symlink" not in msg and "nofollow" not in msg:
        raise AssertionError(f"downstream symlink rejection was not clear: {msg}")
    if pending_counts(ledger, tmp, "after-symlink-rejection") != (1, 0, 0):
        raise AssertionError("downstream symlink rejection mutated outbox before claim")


def assert_existing_downstream_provenance_mismatch_rejected(tmp: pathlib.Path) -> None:
    key, trust, trust_sha, kid = make_trust_and_key(tmp)
    ledger = seed_single_effect_ledger(tmp, "mismatch-ledger")
    downstream = tmp / "mismatch-downstream.sqlite"
    config_a = tmp / "relay-config-a.json"
    registry_a = tmp / "relay-registry-a.json"
    config_sha_a = write_relay_config(config_a, downstream, key, trust, trust_sha, kid, adapter_id="validator-A", worker="validator-worker-A")
    registry_sha_a = write_registry(registry_a, config_a, config_sha_a, adapter_id="validator-A")
    crash = relay_once_handle(ledger, registry_a, registry_sha_a, HANDLE, tmp / "mismatch-crash.json", 1781751600, crash=True, expect_codes={75})
    assert_report_downstream_provenance(crash, config_sha=config_sha_a, registry_sha=registry_sha_a, adapter_id="validator-A")
    effect_key = crash["claim"]["effect_idempotency_key"]
    before = downstream_row(downstream, effect_key)
    if before["observation_count"] != 1:
        raise AssertionError("baseline downstream row was not inserted exactly once")

    config_b = tmp / "relay-config-b.json"
    registry_b = tmp / "relay-registry-b.json"
    config_sha_b = write_relay_config(config_b, downstream, key, trust, trust_sha, kid, adapter_id="validator-B", worker="validator-worker-B")
    registry_sha_b = write_registry(registry_b, config_b, config_sha_b, adapter_id="validator-B")
    proc = run([
        BIN,
        "--ledger", ledger,
        "--ledger-effect-relay-report", tmp / "mismatch-recover-b.json",
        "--ledger-effect-relay-registry", registry_b,
        "--ledger-effect-relay-registry-sha256", registry_sha_b,
        "--ledger-effect-relay-config-handle", HANDLE,
        "--ledger-effect-relay-now-epoch", 1781751661,
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "provenance" not in msg and "adapter" not in msg:
        raise AssertionError(f"provenance mismatch rejection was not clear: {msg}")
    after = downstream_row(downstream, effect_key)
    if after["observation_count"] != 1 or after["adapter_id"] != "validator-A" or after["adapter_config_sha256"] != config_sha_a:
        raise AssertionError("provenance mismatch mutated the existing downstream row")

    recovered = relay_once_handle(ledger, registry_a, registry_sha_a, HANDLE, tmp / "mismatch-recover-a.json", 1781751722)
    if recovered["transition_closed"] is not True or recovered["downstream"]["replayed_existing"] is not True:
        raise AssertionError("original provenance could not recover after mismatched retry failure")
    row = downstream_row(downstream, effect_key)
    if row["observation_count"] != 2 or row["adapter_id"] != "validator-A":
        raise AssertionError("original provenance recovery did not replay the original downstream row")


def assert_v40_downstream_capability_downgrade_rejected(tmp: pathlib.Path) -> None:
    downgraded = tmp / "rev0647-downgraded-capabilities.json"
    caps = load_json(CAPS)
    caps["format"] = "anonsync-ledger-backend-capabilities-v40"
    caps["revision_id"] = "rev0646-forged"
    sw = caps["backends"]["sqlite-wal"]
    sw["snapshot_restore_minimum_capability_version"] = 40
    sw["effect_relay_downstream_store_format"] = "anonsync-relay-downstream-store-v1"
    sw.pop("effect_relay_downstream_result_material_version", None)
    write_json(downgraded, caps)
    one_case = tmp / "downgrade-one-case.jsonl"
    one_case.write_text(CASES.read_text().splitlines()[0] + "\n")
    proc = run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", one_case,
        "--contracts", CONTRACTS,
        "--ledger", tmp / "downgrade.sqlite",
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", downgraded,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", tmp / "downgrade-report.json",
    ], expect_codes=set(range(1, 256)))
    msg = (proc.stdout + proc.stderr).lower()
    if "v41" not in msg and "capability" not in msg:
        raise AssertionError("v40 downstream downgrade rejection was not clearly capability-related")


def write_audit(summary: dict[str, Any]) -> None:
    AUDIT_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


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
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0647-validator-") as td:
        tmp = pathlib.Path(td)
        assert_relay_downstream_provenance(tmp)
        assert_downstream_symlink_rejected_before_claim(tmp)
        assert_existing_downstream_provenance_mismatch_rejected(tmp)
        assert_v40_downstream_capability_downgrade_rejected(tmp)
    summary = {
        "validator": "rev0647-downstream-provenance-boundary",
        "status": "passed",
        "binary": str(BIN.relative_to(ROOT)),
        "binary_sha256": sha_file(BIN),
        "capabilities": str(CAPS.relative_to(ROOT)),
        "capabilities_sha256": sha_file(CAPS),
        "downstream_store_format": DOWNSTREAM_FORMAT,
        "downstream_result_material_version": RESULT_MATERIAL,
        "checked": [
            "v41 capability exactness and downgrade rejection",
            "provenance-bound downstream result report and SQLite row",
            "crash-after-downstream replay with stable provenance-bound digest",
            "downstream symlink-family rejection before outbox claim",
            "existing-row adapter/config/handle provenance mismatch rejection",
            "original provenance recovery after mismatched retry failure",
        ],
    }
    write_audit(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
