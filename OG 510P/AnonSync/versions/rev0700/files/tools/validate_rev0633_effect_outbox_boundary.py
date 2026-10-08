#!/usr/bin/env python3
"""Rev0633 package validator: SQLite effect outbox boundary plus inherited framed ingress and signed transition checks."""
from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0633" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0633-cpp-ledger-backend-capabilities.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
GENESIS = "GENESIS"
MATERIAL_VERSION = "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent"
PENDING_FORMAT = "anonsync-sqlite-effect-pending-report-v4-outbox"
INTENT_FORMAT = "anonsync-effect-transition-intent-v2-ledger-instance"
INTENT_PAYLOAD_FORMAT = "anonsync-effect-transition-intent-payload-v2-ledger-instance"
TRUST_PROFILE_FORMAT = "anonsync-effect-transition-trust-profile-v2"
INTENT_SUBJECT = "sqlite-wal-effect-terminal-transition"
ISSUED_AT = "2026-06-18T02:44:00Z"
VERIFY_AT = "2026-06-18T02:45:00Z"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()



def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def length_prefixed_tuple(domain: str, fields: list[tuple[str, str]]) -> bytes:
    out = bytearray(b"anonsync-length-prefixed-tuple-v1")
    for value in [domain, *[component for field in fields for component in field]]:
        encoded = value.encode("utf-8")
        out.extend(str(len(encoded)).encode("ascii"))
        out.extend(b":")
        out.extend(encoded)
    return bytes(out)


def positive_case(kind: str) -> dict[str, object]:
    for line in CASES.read_text().splitlines():
        row = json.loads(line)
        if row.get("kind") == kind and row.get("failure_injection") is None:
            return row
    raise AssertionError(f"no positive {kind} fixture case found")


def contract_for_case(case: dict[str, object]) -> dict[str, object]:
    contracts = json.loads(CONTRACTS.read_text())["rows"]
    if case["kind"] == "asyncapi":
        event = case["event_envelope"]
        file_hint = event["attributes"].get("x-anonsync-contract-file", "")
        matches = [row for row in contracts if row["kind"] == "asyncapi" and row["file"] == file_hint and row["channel"] == event["channel"] and row.get("action", "") == event["action"]]
    else:
        request = case["http_request"]
        file_hint = request["headers"].get("x-anonsync-contract-file", "")
        # The selected positive fixture path is concrete; matching the file, method, and JWT operation id is unambiguous.
        token = request["headers"]["authorization"].split(" ", 1)[1]
        payload_b64 = token.split(".")[1]
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)))
        matches = [row for row in contracts if row["kind"] == "openapi" and row["file"] == file_hint and row["method"].upper() == request["method"].upper() and row["operation_id"] == payload["operation_id"]]
    if len(matches) != 1:
        raise AssertionError(f"fixture contract lookup was not unique: {len(matches)}")
    return matches[0]


def legacy_material(case: dict[str, object], contract: dict[str, object], *, proof: bool) -> str:
    kind = case["kind"]
    envelope = case["event_envelope"] if kind == "asyncapi" else case["http_request"]
    metadata = envelope["attributes"] if kind == "asyncapi" else envelope["headers"]
    token = metadata["authorization"].split(" ", 1)[1]
    rows: list[tuple[str, str]] = [("kind", kind)]
    if proof:
        rows.extend([
            ("proof_kid", metadata["x-anonsync-proof-kid"]),
            ("tenant", metadata["x-anonsync-tenant"]),
            ("contract_file", contract["file"]),
            ("operation_id", contract["operation_id"]),
            ("contract_digest_sha256", contract["contract_digest_sha256"]),
            ("token_sha256", sha256_hex(token)),
        ])
        prefix = "anonsync-proof-binding-v1"
    else:
        rows.extend([
            ("tenant", metadata["x-anonsync-tenant"]),
            ("contract_file", contract["file"]),
            ("operation_id", contract["operation_id"]),
            ("contract_digest_sha256", contract["contract_digest_sha256"]),
        ])
        prefix = "anonsync-effect-idempotency-v1"
    if kind == "openapi":
        rows.extend([
            ("method", envelope["method"].upper()),
            ("path", envelope["path"]),
            ("body_sha256", sha256_hex(canonical_json(envelope["body"]))),
        ])
    else:
        rows.extend([
            ("channel", envelope["channel"]),
            ("action", envelope["action"]),
            ("cloud_event_source", envelope["cloud_event"]["source"]),
            ("cloud_event_id", envelope["cloud_event"]["id"]),
            ("payload_sha256", sha256_hex(canonical_json(envelope["payload"]))),
        ])
    return prefix + "\n" + "".join(f"{name}={value}\n" for name, value in rows)


def framed_material(case: dict[str, object], contract: dict[str, object], *, proof: bool) -> bytes:
    kind = case["kind"]
    envelope = case["event_envelope"] if kind == "asyncapi" else case["http_request"]
    metadata = envelope["attributes"] if kind == "asyncapi" else envelope["headers"]
    token = metadata["authorization"].split(" ", 1)[1]
    fields: list[tuple[str, str]] = [("kind", kind)]
    if proof:
        fields.extend([
            ("proof_kid", metadata["x-anonsync-proof-kid"]),
            ("tenant", metadata["x-anonsync-tenant"]),
            ("contract_file", contract["file"]),
            ("operation_id", contract["operation_id"]),
            ("contract_digest_sha256", contract["contract_digest_sha256"]),
            ("token_sha256", sha256_hex(token)),
        ])
        domain = "anonsync-proof-binding-v2"
    else:
        fields.extend([
            ("tenant", metadata["x-anonsync-tenant"]),
            ("contract_file", contract["file"]),
            ("operation_id", contract["operation_id"]),
            ("contract_digest_sha256", contract["contract_digest_sha256"]),
        ])
        domain = "anonsync-effect-idempotency-v2"
    if kind == "openapi":
        fields.extend([
            ("method", envelope["method"].upper()),
            ("path", envelope["path"]),
            ("body_sha256", sha256_hex(canonical_json(envelope["body"]))),
        ])
    else:
        fields.extend([
            ("channel", envelope["channel"]),
            ("action", envelope["action"]),
            ("cloud_event_source", envelope["cloud_event"]["source"]),
            ("cloud_event_id", envelope["cloud_event"]["id"]),
            ("payload_sha256", sha256_hex(canonical_json(envelope["payload"]))),
        ])
    return length_prefixed_tuple(domain, fields)


def run_probe_cases(tmp: pathlib.Path, cases: list[dict[str, object]], stem: str, backend: str) -> dict[str, object]:
    cases_path = tmp / f"{stem}-{backend}-cases.jsonl"
    report_path = tmp / f"{stem}-{backend}-report.json"
    ledger_suffix = ".sqlite" if backend == "sqlite-wal" else ".jsonl"
    ledger_path = tmp / f"{stem}-{backend}-ledger{ledger_suffix}"
    cases_path.write_text("".join(canonical_json(case) + "\n" for case in cases))
    run([
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", cases_path,
        "--contracts", CONTRACTS,
        "--ledger", ledger_path,
        "--ledger-backend", backend,
        "--ledger-backend-capabilities", CAPS,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", report_path,
    ])
    return json.loads(report_path.read_text())


def exercise_security_material_boundary(tmp: pathlib.Path) -> dict[str, object]:
    controls = json.loads(CONTROLS.read_text())
    secret = controls["identity_profile"]["proof_binding_hmac_sha256_secret"].encode("utf-8")
    seed = positive_case("asyncapi")
    contract = contract_for_case(seed)
    pair_a = copy.deepcopy(seed)
    pair_b = copy.deepcopy(seed)
    pair_a["case_id"] = "rev0633-newline-collision-pair-a"
    pair_b["case_id"] = "rev0633-newline-collision-pair-b"
    pair_a["expected_action"] = pair_b["expected_action"] = "quarantine"
    pair_a["failure_injection"] = "security_material_control_character_pair_a"
    pair_b["failure_injection"] = "security_material_control_character_pair_b"
    pair_a["event_envelope"]["cloud_event"] = {"source": "A\ncloud_event_id=B", "id": "C", "type": seed["event_envelope"]["cloud_event"]["type"]}
    pair_b["event_envelope"]["cloud_event"] = {"source": "A", "id": "B\ncloud_event_id=C", "type": seed["event_envelope"]["cloud_event"]["type"]}

    legacy_proof_a = legacy_material(pair_a, contract, proof=True)
    legacy_proof_b = legacy_material(pair_b, contract, proof=True)
    legacy_effect_a = legacy_material(pair_a, contract, proof=False)
    legacy_effect_b = legacy_material(pair_b, contract, proof=False)
    if legacy_proof_a != legacy_proof_b or legacy_effect_a != legacy_effect_b:
        raise AssertionError("validator failed to reproduce the rev0631 proof/effect newline collision")

    identity_a = copy.deepcopy(seed)
    identity_b = copy.deepcopy(seed)
    identity_a["case_id"] = "rev0633-event-identity-collision-pair-a"
    identity_b["case_id"] = "rev0633-event-identity-collision-pair-b"
    identity_a["expected_action"] = identity_b["expected_action"] = "quarantine"
    identity_a["failure_injection"] = "event_identity_control_character_pair_a"
    identity_b["failure_injection"] = "event_identity_control_character_pair_b"
    identity_a["event_envelope"]["cloud_event"] = {"source": "A\nB", "id": "C", "type": seed["event_envelope"]["cloud_event"]["type"]}
    identity_b["event_envelope"]["cloud_event"] = {"source": "A", "id": "B\nC", "type": seed["event_envelope"]["cloud_event"]["type"]}
    legacy_identity_a = identity_a["event_envelope"]["cloud_event"]["source"] + "\n" + identity_a["event_envelope"]["cloud_event"]["id"]
    legacy_identity_b = identity_b["event_envelope"]["cloud_event"]["source"] + "\n" + identity_b["event_envelope"]["cloud_event"]["id"]
    if legacy_identity_a != legacy_identity_b:
        raise AssertionError("validator failed to reproduce the rev0631 event-identity newline collision")

    framed_proof_a = framed_material(pair_a, contract, proof=True)
    framed_proof_b = framed_material(pair_b, contract, proof=True)
    framed_effect_a = framed_material(pair_a, contract, proof=False)
    framed_effect_b = framed_material(pair_b, contract, proof=False)
    framed_identity_a = length_prefixed_tuple("anonsync-cloud-event-identity-v2", [("source", identity_a["event_envelope"]["cloud_event"]["source"]), ("id", identity_a["event_envelope"]["cloud_event"]["id"])])
    framed_identity_b = length_prefixed_tuple("anonsync-cloud-event-identity-v2", [("source", identity_b["event_envelope"]["cloud_event"]["source"]), ("id", identity_b["event_envelope"]["cloud_event"]["id"])])
    if framed_proof_a == framed_proof_b or framed_effect_a == framed_effect_b or framed_identity_a == framed_identity_b:
        raise AssertionError("length-prefixed security tuples did not separate the reproduced collision pairs")

    legacy_digest = hmac.new(secret, legacy_proof_a.encode("utf-8"), hashlib.sha256).hexdigest()
    pair_a["event_envelope"]["attributes"]["x-anonsync-proof-binding-sha256"] = legacy_digest
    pair_b["event_envelope"]["attributes"]["x-anonsync-proof-binding-sha256"] = legacy_digest
    # These identity-collision probes are rejected on control characters before proof evaluation.
    identity_a["event_envelope"]["attributes"]["x-anonsync-proof-binding-sha256"] = "0" * 64
    identity_b["event_envelope"]["attributes"]["x-anonsync-proof-binding-sha256"] = "0" * 64

    duplicate = positive_case("openapi")
    duplicate["case_id"] = "rev0633-duplicate-case-insensitive-authorization"
    duplicate["expected_action"] = "deny"
    duplicate["failure_injection"] = "duplicate_case_insensitive_security_metadata"
    duplicate["http_request"]["headers"]["Authorization"] = duplicate["http_request"]["headers"]["authorization"]

    backend_reports: dict[str, object] = {}
    for backend in ("sqlite-wal", "local-jsonl"):
        collision_report = run_probe_cases(tmp, [pair_a, pair_b, identity_a, identity_b], "security-material-collision", backend)
        counters = collision_report["counters"]
        if counters["total_cases"] != 4 or counters["passed"] != 4 or counters["failed"] != 0 or counters["normalizer_proof_rejections"] != 4 or counters["ledger_appended_entries"] != 0:
            raise AssertionError(f"{backend} did not quarantine all control-character collision probes: {counters!r}")
        duplicate_report = run_probe_cases(tmp, [duplicate], "duplicate-security-metadata", backend)
        counters = duplicate_report["counters"]
        if counters["total_cases"] != 1 or counters["passed"] != 1 or counters["failed"] != 0 or counters["normalizer_authorization_rejections"] != 1 or counters["ledger_appended_entries"] != 0:
            raise AssertionError(f"{backend} did not reject duplicate case-insensitive metadata: {counters!r}")
        backend_reports[backend] = {
            "collision_probe_count": collision_report["counters"]["total_cases"],
            "collision_proof_rejections": collision_report["counters"]["normalizer_proof_rejections"],
            "duplicate_metadata_rejections": duplicate_report["counters"]["normalizer_authorization_rejections"],
        }

    return {
        "legacy_collision_hmac_sha256": legacy_digest,
        "legacy_proof_material_sha256": sha256_hex(legacy_proof_a),
        "legacy_effect_material_sha256": sha256_hex(legacy_effect_a),
        "legacy_event_identity_sha256": sha256_hex(legacy_identity_a),
        "framed_proof_a_sha256": sha256_hex(framed_proof_a),
        "framed_proof_b_sha256": sha256_hex(framed_proof_b),
        "framed_effect_a_sha256": sha256_hex(framed_effect_a),
        "framed_effect_b_sha256": sha256_hex(framed_effect_b),
        "framed_identity_a_sha256": sha256_hex(framed_identity_a),
        "framed_identity_b_sha256": sha256_hex(framed_identity_b),
        "backend_reports": backend_reports,
    }


def run(cmd: Iterable[os.PathLike[str] | str], *, expect: int = 0, cwd: pathlib.Path | None = ROOT, input_text: str | bytes | None = None) -> subprocess.CompletedProcess[str]:
    argv = [str(x) for x in cmd]
    proc = subprocess.run(argv, cwd=str(cwd) if cwd else None, text=True, input=input_text if isinstance(input_text, str) else None, capture_output=True)
    if isinstance(input_text, bytes):
        proc = subprocess.run(argv, cwd=str(cwd) if cwd else None, input=input_text, capture_output=True)
        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")
        proc = subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)
    if proc.returncode != expect:
        print("command failed:", " ".join(argv), file=sys.stderr)
        print("expected:", expect, "actual:", proc.returncode, file=sys.stderr)
        print("--- stdout ---", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print("--- stderr ---", file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(1)
    return proc


def expect_failure(cmd: Iterable[os.PathLike[str] | str], needle: str) -> subprocess.CompletedProcess[str]:
    argv = [str(x) for x in cmd]
    proc = subprocess.run(argv, cwd=str(ROOT), text=True, capture_output=True)
    if proc.returncode == 0:
        print("command unexpectedly succeeded:", " ".join(argv), file=sys.stderr)
        print(proc.stdout, proc.stderr, file=sys.stderr)
        raise SystemExit(1)
    combined = proc.stdout + proc.stderr
    if needle not in combined:
        print("failure did not contain expected text", needle, file=sys.stderr)
        print("--- combined ---", file=sys.stderr)
        print(combined, file=sys.stderr)
        raise SystemExit(1)
    return proc


def run_fixture(ledger: pathlib.Path, report: pathlib.Path, *, caps: pathlib.Path = CAPS, snapshot: pathlib.Path | None = None) -> None:
    cmd: list[os.PathLike[str] | str] = [
        BIN,
        "--controls", CONTROLS,
        "--cases-jsonl", CASES,
        "--contracts", CONTRACTS,
        "--ledger", ledger,
        "--ledger-backend", "sqlite-wal",
        "--ledger-backend-capabilities", caps,
        "--ledger-reset",
        "--ledger-commit-mode", "batch",
        "--report", report,
    ]
    if snapshot is not None:
        cmd.extend(["--ledger-snapshot", snapshot])
    run(cmd)


def inspect_clean_ledger(ledger: pathlib.Path) -> dict[str, object]:
    con = sqlite3.connect(str(ledger))
    try:
        profile = con.execute(
            "SELECT backend_name, schema_version, hash_algorithm, entry_material_version, commit_protocol FROM backend_profile WHERE id=1"
        ).fetchone()
        if profile != ("sqlite-wal", 9, "sha256", MATERIAL_VERSION, "sqlite-wal-begin-immediate-full-sync"):
            raise AssertionError(f"unexpected backend profile {profile!r}")
        metadata = con.execute("SELECT line_count, head_hash FROM metadata WHERE id=1").fetchone()
        if not metadata or metadata[0] <= 0 or metadata[1] == GENESIS:
            raise AssertionError(f"unexpected ledger metadata {metadata!r}")
        transition_metadata = con.execute("SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1").fetchone()
        if transition_metadata != (0, GENESIS):
            raise AssertionError(f"unexpected clean transition metadata {transition_metadata!r}")
        expected_tables = {"metadata", "ledger_entries", "backend_profile", "ledger_identity", "effect_transition_metadata", "effect_transitions", "effect_outbox"}
        table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if table_names != expected_tables:
            raise AssertionError(f"unexpected table set {sorted(table_names)!r}")
        transition_cols = [r[1] for r in con.execute("PRAGMA table_info(effect_transitions)")]
        for col in ("ledger_instance_id", "prepared_sequence", "prepared_entry_hash", "transition_intent_id", "transition_intent_signer_kid", "transition_intent_sha256"):
            if col not in transition_cols:
                raise AssertionError(f"effect_transitions missing {col}")
        indexes = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        if "ledger_effect_prepared_entry_evidence_unique" not in indexes:
            raise AssertionError("missing prepared-entry evidence unique index")
        entry_count, effect_count, unique_effect_count = con.execute(
            "SELECT COUNT(*), COUNT(effect_idempotency_key), COUNT(DISTINCT effect_idempotency_key) FROM ledger_entries"
        ).fetchone()
        if entry_count != effect_count or entry_count != unique_effect_count or entry_count <= 1:
            raise AssertionError("prepared-effect keys are not complete and unique")
        outbox_cols = [r[1] for r in con.execute("PRAGMA table_info(effect_outbox)")]
        for col in ("effect_idempotency_key", "prepared_sequence", "prepared_entry_hash", "outbox_state", "dispatch_attempts", "last_result_digest_sha256", "updated_at_sequence"):
            if col not in outbox_cols:
                raise AssertionError(f"effect_outbox missing {col}")
        outbox_count, reserved_count, terminal_count, mismatched_count = con.execute(
            "SELECT COUNT(*), SUM(CASE WHEN outbox_state='reserved' THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN outbox_state IN ('applied','failed','compensated') THEN 1 ELSE 0 END), "
            "SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM ledger_entries e WHERE e.effect_idempotency_key=effect_outbox.effect_idempotency_key AND e.sequence=effect_outbox.prepared_sequence AND e.entry_hash=effect_outbox.prepared_entry_hash) THEN 1 ELSE 0 END) "
            "FROM effect_outbox"
        ).fetchone()
        if outbox_count != entry_count or reserved_count != entry_count or terminal_count != 0 or mismatched_count != 0:
            raise AssertionError(f"effect_outbox did not atomically cover prepared rows: {(outbox_count, reserved_count, terminal_count, mismatched_count)!r}")
        outbox_dirty = con.execute("SELECT COUNT(*) FROM effect_outbox WHERE dispatch_attempts != 0 OR last_result_digest_sha256 != '' OR updated_at_sequence != prepared_sequence").fetchone()[0]
        if outbox_dirty != 0:
            raise AssertionError("fresh prepared effect_outbox rows were not clean reserved rows")

        identity = con.execute("SELECT ledger_instance_id FROM ledger_identity WHERE id=1").fetchone()
        if not identity or len(identity[0]) != 64:
            raise AssertionError(f"unexpected ledger_identity {identity!r}")
        row = con.execute("SELECT sequence, entry_hash, effect_idempotency_key FROM ledger_entries ORDER BY sequence LIMIT 1").fetchone()
        second = con.execute("SELECT effect_idempotency_key FROM ledger_entries ORDER BY sequence LIMIT 1 OFFSET 1").fetchone()[0]
        return {
            "ledger_instance_id": identity[0],
            "entry_count": entry_count,
            "decision_head_hash": metadata[1],
            "sequence": int(row[0]),
            "entry_hash": row[1],
            "effect_idempotency_key": row[2],
            "second_effect_idempotency_key": second,
        }
    finally:
        con.close()


def inspect_pending_report(report_path: pathlib.Path, *, expected_prepared: int, expected_terminal: int, expected_pending: int, absent_key: str | None = None, present_key: str | None = None) -> dict[str, object]:
    root = json.loads(report_path.read_text())
    if root.get("format") != PENDING_FORMAT:
        raise AssertionError("pending report format mismatch")
    if root.get("revision_id") != "rev0633":
        raise AssertionError("pending report revision mismatch")
    if not isinstance(root.get("ledger_instance_id"), str) or len(root.get("ledger_instance_id")) != 64:
        raise AssertionError("pending report missing ledger_instance_id")
    if root.get("prepared_effect_count") != expected_prepared or root.get("terminal_effect_count") != expected_terminal or root.get("pending_effect_count") != expected_pending:
        raise AssertionError(f"unexpected pending report counts {root!r}")
    if root.get("outbox_format") != "anonsync-sqlite-effect-outbox-v1":
        raise AssertionError("pending report did not declare effect outbox format")
    if root.get("outbox_reserved_count") != expected_pending or root.get("outbox_terminal_count") != expected_terminal:
        raise AssertionError(f"unexpected outbox counts {root!r}")
    keys = {row["effect_idempotency_key"] for row in root.get("pending_effects", [])}
    if len(keys) != expected_pending:
        raise AssertionError("pending report key cardinality mismatch")
    if absent_key and absent_key in keys:
        raise AssertionError("terminal effect key still appeared in pending report")
    if present_key and present_key not in keys:
        raise AssertionError("expected pending effect key absent from report")
    for row in root.get("pending_effects", []):
        if "jti" in row:
            raise AssertionError("pending report leaked JWT jti fields")
        if not isinstance(row.get("sequence"), int) or len(row.get("entry_hash", "")) != 64:
            raise AssertionError("pending row did not expose sequence and entry_hash")
        if row.get("outbox_state") != "reserved":
            raise AssertionError("pending row was not backed by a reserved outbox row")
    if root.get("verification") != "single-open read-only verifier with schema/hash-chain/effect-transition/outbox checks":
        raise AssertionError("pending report did not record read-only verification mode")
    return root


def pending_row(root: dict[str, object], effect_key: str) -> dict[str, object]:
    for row in root.get("pending_effects", []):
        if row.get("effect_idempotency_key") == effect_key:
            return row
    raise AssertionError("effect key absent from pending report")


def signing_input(payload: dict[str, object]) -> str:
    return (
        f"{INTENT_FORMAT}\n"
        f"{payload['intent_id']}\n"
        f"{payload['intent_subject']}\n"
        f"{payload['issued_at']}\n"
        f"{payload['ledger_backend']}\n"
        f"{payload['ledger_instance_id']}\n"
        f"{payload['prepared_ledger_head_hash']}\n"
        f"{payload['effect_transition_previous_hash']}\n"
        f"{payload['effect_idempotency_key']}\n"
        f"{payload['prepared_sequence']}\n"
        f"{payload['prepared_entry_hash']}\n"
        f"{payload['terminal_state']}\n"
        f"{payload['result_digest_sha256']}\n"
        f"{payload['transition_reason']}\n"
    )


def make_rsa_root(tmp: pathlib.Path) -> dict[str, object]:
    key = tmp / "transition-root.pem"
    run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", key], cwd=None)
    mod = run(["openssl", "rsa", "-in", key, "-noout", "-modulus"], cwd=None).stdout.strip()
    if not mod.startswith("Modulus="):
        raise AssertionError(f"unexpected openssl modulus output {mod!r}")
    n_bytes = bytes.fromhex(mod.split("=", 1)[1]).lstrip(b"\x00")
    return {"key": key, "kid": "rev0633-validator-transition-root", "n": b64url(n_bytes), "e": b64url(b"\x01\x00\x01")}


def make_trust_profile(root: dict[str, object]) -> str:
    return json.dumps({
        "format": TRUST_PROFILE_FORMAT,
        "revision_id": "rev0633",
        "verification_time": VERIFY_AT,
        "max_intent_age_seconds": 3600,
        "required_intent_subject": INTENT_SUBJECT,
        "allowed_terminal_states": ["applied", "failed", "compensated"],
        "trusted_signers": [{
            "kid": root["kid"],
            "alg": "RS256",
            "status": "trusted",
            "not_before": "2026-06-18T00:00:00Z",
            "not_after": "2026-06-19T00:00:00Z",
            "jwk": {"kty": "RSA", "alg": "RS256", "kid": root["kid"], "n": root["n"], "e": root["e"]},
        }],
        "blocked_claim": "Validator transition trust profile only; not production PKI or HSM custody.",
    }, indent=2, sort_keys=True) + "\n"


def make_intent(root: dict[str, object], *, intent_id: str, ledger_instance_id: str, decision_head: str, transition_head: str, row: dict[str, object], state: str, result_digest: str, reason: str) -> str:
    payload = {
        "format": INTENT_PAYLOAD_FORMAT,
        "intent_id": intent_id,
        "intent_subject": INTENT_SUBJECT,
        "issued_at": ISSUED_AT,
        "ledger_backend": "sqlite-wal",
        "ledger_instance_id": ledger_instance_id,
        "prepared_ledger_head_hash": decision_head,
        "effect_transition_previous_hash": transition_head,
        "effect_idempotency_key": row["effect_idempotency_key"],
        "prepared_sequence": row["sequence"],
        "prepared_entry_hash": row["entry_hash"],
        "terminal_state": state,
        "result_digest_sha256": result_digest,
        "transition_reason": reason,
    }
    si = signing_input(payload)
    proc = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(root["key"]), "-binary"], input=si.encode("utf-8"), capture_output=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr.decode("utf-8", "replace"))
    return json.dumps({
        "format": INTENT_FORMAT,
        "payload": payload,
        "payload_signing_input_sha256": sha256_hex(si),
        "signature": {"alg": "RS256", "kid": root["kid"], "signature_b64url": b64url(proc.stdout)},
        "blocked_claim": "Validator transition intent only; not downstream delivery proof.",
    }, indent=2, sort_keys=True) + "\n"


def inspect_transition(ledger: pathlib.Path, effect_key: str, expected: dict[str, object]) -> str:
    con = sqlite3.connect(str(ledger))
    try:
        rows = con.execute(
            "SELECT sequence, previous_hash, transition_hash, ledger_instance_id, effect_idempotency_key, prepared_sequence, prepared_entry_hash, terminal_state, result_digest_sha256, transition_reason, transition_intent_id, transition_intent_signer_kid, transition_intent_sha256 FROM effect_transitions"
        ).fetchall()
        if len(rows) != 1:
            raise AssertionError(f"expected one transition row, saw {len(rows)}")
        sequence, previous_hash, transition_hash, ledger_instance_id, key, pseq, phash, state, digest, reason, intent_id, signer, intent_sha = rows[0]
        if sequence != 1 or previous_hash != GENESIS or key != effect_key or ledger_instance_id != expected["ledger_instance_id"]:
            raise AssertionError(f"unexpected transition row identity {rows[0]!r}")
        if pseq != expected["prepared_sequence"] or phash != expected["prepared_entry_hash"] or state != expected["terminal_state"] or digest != expected["result_digest_sha256"]:
            raise AssertionError(f"unexpected transition row evidence {rows[0]!r}")
        if intent_id != expected["intent_id"] or signer != expected["signer_kid"] or intent_sha != expected["intent_sha256"]:
            raise AssertionError(f"transition did not persist signed intent metadata {rows[0]!r}")
        meta = con.execute("SELECT line_count, head_hash FROM effect_transition_metadata WHERE id=1").fetchone()
        if meta != (1, transition_hash) or transition_hash == GENESIS:
            raise AssertionError(f"unexpected transition metadata {meta!r}")
        outbox = con.execute("SELECT outbox_state, last_result_digest_sha256, updated_at_sequence FROM effect_outbox WHERE effect_idempotency_key=?", (effect_key,)).fetchone()
        if outbox != (expected["terminal_state"], expected["result_digest_sha256"], sequence):
            raise AssertionError(f"terminal transition did not atomically update effect_outbox {outbox!r}")
        return transition_hash
    finally:
        con.close()


def sqlite_backup(src: pathlib.Path, dst: pathlib.Path) -> None:
    src_con = sqlite3.connect(str(src))
    dst_con = sqlite3.connect(str(dst))
    try:
        src_con.backup(dst_con)
    finally:
        dst_con.close()
        src_con.close()


def optional_source_build() -> None:
    if not os.environ.get("ANONSYNC_REV0633_SOURCE_BUILD"):
        return
    build = ROOT / ".rev0633-source-build"
    if build.exists():
        shutil.rmtree(build)
    run(["cmake", "-S", ROOT / "cpp" / "anonsync_core", "-B", build])
    run(["cmake", "--build", build, "--target", "anonsync_core", "-j2"])
    run(["ctest", "--test-dir", build, "--output-on-failure"])


def main() -> int:
    if not BIN.exists():
        print(f"missing packaged binary: {BIN}", file=sys.stderr)
        return 1
    if (ROOT / "bin" / "rev0632").exists():
        raise AssertionError("stale rev0632 packaged binary directory should not remain in rev0633")
    optional_source_build()
    caps_root = json.loads(CAPS.read_text())
    if caps_root.get("format") != "anonsync-ledger-backend-capabilities-v28":
        raise AssertionError("rev0633 capability manifest must be exact v28")
    if caps_root.get("revision_id") != "rev0633" or caps_root.get("parent_revision") != "rev0632":
        raise AssertionError("rev0633 capability manifest revision lineage mismatch")
    sqlite_caps = caps_root["backends"]["sqlite-wal"]
    local_caps = caps_root["backends"]["local-jsonl"]
    if sqlite_caps["ledger_schema_version"] != 9 or sqlite_caps["ledger_entry_material_version"] != MATERIAL_VERSION:
        raise AssertionError("sqlite-wal capability manifest is not schema v9/material v7")
    for backend_name, backend_caps in (("sqlite-wal", sqlite_caps), ("local-jsonl", local_caps)):
        expected = {
            "security_tuple_framing": "anonsync-length-prefixed-tuple-v1",
            "proof_binding_material_version": "anonsync-proof-binding-v2-lp-hmac-sha256",
            "cloud_event_identity_material_version": "anonsync-cloud-event-identity-v2",
            "effect_idempotency_material_version": "anonsync-effect-idempotency-v2",
            "legacy_effect_idempotency_fallback_material_version": "anonsync-effect-idempotency-legacy-v1",
            "case_insensitive_security_metadata_duplicate_rejection_required": True,
            "security_metadata_control_character_rejection_required": True,
        }
        for key, value in expected.items():
            if backend_caps.get(key) != value:
                raise AssertionError(f"{backend_name} rev0633 capability mismatch for {key}: {backend_caps.get(key)!r}")
    if sqlite_caps.get("ledger_instance_id_generation") != "anonsync-sqlite-ledger-instance-v2-openssl-rand":
        raise AssertionError("rev0633 sqlite-wal capability must use OpenSSL-random ledger instance ids")
    if sqlite_caps.get("ledger_instance_id_csprng_failure_fails_closed") is not True:
        raise AssertionError("rev0633 sqlite-wal capability must fail closed on CSPRNG failure")
    if sqlite_caps.get("effect_outbox_material_version") != "anonsync-sqlite-effect-outbox-v1":
        raise AssertionError("rev0633 sqlite-wal capability must declare effect outbox material v1")
    for key in (
        "effect_outbox_inserted_atomically_with_prepared_entry",
        "effect_outbox_terminal_update_bound_to_signed_transition",
        "snapshot_readonly_verifier_checks_effect_outbox",
    ):
        if sqlite_caps.get(key) is not True:
            raise AssertionError(f"rev0633 capability manifest missing {key}")
    if sqlite_caps.get("effect_pending_report_format") != PENDING_FORMAT:
        raise AssertionError("rev0633 capability manifest must declare pending report v4 outbox format")
    for key in (
        "ledger_effect_transition_signed_intent_required",
        "ledger_effect_transition_intent_digest_pin_required",
        "ledger_effect_transition_intent_binds_prepared_ledger_head",
        "ledger_effect_transition_intent_binds_transition_head",
        "ledger_effect_transition_cli_raw_parameters_rejected",
        "snapshot_readonly_verifier_checks_effect_transition_intent_metadata",
        "ledger_effect_transition_raw_public_api_disabled",
        "ledger_instance_id_required",
        "ledger_effect_transition_intent_binds_ledger_instance_id",
        "ledger_effect_transition_row_binds_ledger_instance_id",
        "ledger_effect_transition_intent_id_unique",
        "ledger_effect_pending_report_includes_ledger_instance_id",
        "snapshot_readonly_verifier_checks_ledger_instance_binding",
    ):
        if not sqlite_caps.get(key):
            raise AssertionError(f"rev0633 capability manifest missing {key}")

    for selftest in (
        "--selftest-ledger-sqlite-effect-signed-transition",
        "--selftest-ledger-sqlite-effect-pending-recovery",
        "--selftest-ledger-sqlite-effect-transition",
        "--selftest-ledger-effect-idempotency",
        "--selftest-ledger-sqlite-readonly-snapshot-verifier",
        "--selftest-fuzz-route-event-ledger",
    ):
        run([BIN, selftest])

    with tempfile.TemporaryDirectory(prefix="anonsync-rev0633-validator-") as tmp_s:
        tmp = pathlib.Path(tmp_s)
        ledger = tmp / "rev0633-validator-ledger.sqlite"
        report = tmp / "rev0633-validator-report.json"
        pending_report = tmp / "rev0633-pending-effects.json"
        snapshot = tmp / "rev0633-validator-snapshot.sqlite"
        run_fixture(ledger, report, snapshot=snapshot)
        report_root = json.loads(report.read_text())
        counters = report_root["counters"]
        if counters["failed"] != 0 or counters["passed"] != counters["total_cases"] or counters["total_cases"] <= 0:
            raise AssertionError("fixture stream did not fully pass")
        clean = inspect_clean_ledger(ledger)
        inspect_clean_ledger(snapshot)
        security_material = exercise_security_material_boundary(tmp)

        run([BIN, "--ledger", ledger, "--ledger-effect-pending-report", pending_report])
        before = inspect_pending_report(pending_report, expected_prepared=clean["entry_count"], expected_terminal=0, expected_pending=clean["entry_count"], present_key=clean["effect_idempotency_key"])
        row = pending_row(before, clean["effect_idempotency_key"])
        if before["ledger_instance_id"] != clean["ledger_instance_id"]:
            raise AssertionError("pending report ledger_instance_id did not match ledger_identity")
        if row["sequence"] != clean["sequence"] or row["entry_hash"] != clean["entry_hash"]:
            raise AssertionError("pending report evidence did not match ledger row")

        result_digest = sha256_hex("rev0633 validator downstream applied")
        raw_cmd = [
            BIN,
            "--ledger", ledger,
            "--ledger-effect-idempotency-key", clean["effect_idempotency_key"],
            "--ledger-effect-prepared-sequence", clean["sequence"],
            "--ledger-effect-prepared-entry-hash", clean["entry_hash"],
            "--ledger-effect-terminal-state", "applied",
            "--ledger-effect-result-sha256", result_digest,
            "--ledger-effect-transition-reason", "raw cli must fail",
        ]
        expect_failure(raw_cmd, "requires signed intent")

        root = make_rsa_root(tmp)
        trust = make_trust_profile(root)
        trust_path = tmp / "transition-trust.json"
        trust_path.write_text(trust)
        trust_sha = sha256_hex(trust)
        intent_path = tmp / "transition-intent.json"
        valid_intent = make_intent(root, intent_id="rev0633-validator-intent-a", ledger_instance_id=before["ledger_instance_id"], decision_head=before["decision_head_hash"], transition_head=before["effect_transition_head_hash"], row=row, state="applied", result_digest=result_digest, reason="rev0633 validator downstream applied")
        intent_path.write_text(valid_intent)

        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", intent_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", "0" * 64], "digest pin")

        wrong_ledger_path = tmp / "transition-intent-wrong-ledger.json"
        wrong_ledger_path.write_text(make_intent(root, intent_id="rev0633-validator-wrong-ledger", ledger_instance_id="0" * 64, decision_head=before["decision_head_hash"], transition_head=before["effect_transition_head_hash"], row=row, state="applied", result_digest=result_digest, reason="wrong ledger instance should fail"))
        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", wrong_ledger_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha], "ledger instance")

        tampered = json.loads(valid_intent)
        tampered["payload"]["result_digest_sha256"] = sha256_hex("tampered result digest")
        tampered_path = tmp / "transition-intent-tampered.json"
        tampered_path.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n")
        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", tampered_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha], "signing-input")

        stale_head_path = tmp / "transition-intent-stale-head.json"
        stale_head_path.write_text(make_intent(root, intent_id="rev0633-validator-stale-head", ledger_instance_id=before["ledger_instance_id"], decision_head="0" * 64, transition_head=before["effect_transition_head_hash"], row=row, state="applied", result_digest=result_digest, reason="stale decision head should fail"))
        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", stale_head_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha], "stale")

        stale_transition_path = tmp / "transition-intent-stale-transition.json"
        stale_transition_path.write_text(make_intent(root, intent_id="rev0633-validator-stale-transition", ledger_instance_id=before["ledger_instance_id"], decision_head=before["decision_head_hash"], transition_head="0" * 64, row=row, state="applied", result_digest=result_digest, reason="stale transition head should fail"))
        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", stale_transition_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha], "stale")

        run([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", intent_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha])
        expected = {
            "ledger_instance_id": before["ledger_instance_id"],
            "prepared_sequence": row["sequence"],
            "prepared_entry_hash": row["entry_hash"],
            "terminal_state": "applied",
            "result_digest_sha256": result_digest,
            "intent_id": "rev0633-validator-intent-a",
            "signer_kid": root["kid"],
            "intent_sha256": sha256_hex(valid_intent),
        }
        transition_head = inspect_transition(ledger, clean["effect_idempotency_key"], expected)
        run([BIN, "--ledger", ledger, "--ledger-effect-pending-report", pending_report])
        after = inspect_pending_report(
            pending_report,
            expected_prepared=clean["entry_count"],
            expected_terminal=1,
            expected_pending=clean["entry_count"] - 1,
            absent_key=clean["effect_idempotency_key"],
            present_key=clean["second_effect_idempotency_key"],
        )
        if after["effect_transition_head_hash"] != transition_head:
            raise AssertionError("pending report did not bind transition head hash")

        duplicate_intent_path = tmp / "transition-intent-duplicate.json"
        duplicate_intent_path.write_text(make_intent(root, intent_id="rev0633-validator-duplicate", ledger_instance_id=after["ledger_instance_id"], decision_head=after["decision_head_hash"], transition_head=after["effect_transition_head_hash"], row=row, state="failed", result_digest=sha256_hex("duplicate terminal attempt"), reason="duplicate terminal should fail"))
        expect_failure([BIN, "--ledger", ledger, "--ledger-effect-transition-intent", duplicate_intent_path, "--ledger-effect-transition-trust-profile", trust_path, "--ledger-effect-transition-trust-profile-sha256", trust_sha], "duplicate")

        tampered_db = tmp / "rev0633-transition-intent-tampered.sqlite"
        sqlite_backup(ledger, tampered_db)
        con = sqlite3.connect(str(tampered_db))
        try:
            con.execute("UPDATE effect_transitions SET ledger_instance_id=? WHERE sequence=1", ("1" * 64,))
            con.commit()
        finally:
            con.close()
        expect_failure([BIN, "--ledger", tampered_db, "--ledger-effect-pending-report", tmp / "bad-pending.json"], "ledger_instance_id")

        tampered_outbox = tmp / "rev0633-outbox-tampered.sqlite"
        sqlite_backup(ledger, tampered_outbox)
        con = sqlite3.connect(str(tampered_outbox))
        try:
            con.execute("DELETE FROM effect_outbox WHERE effect_idempotency_key=?", (clean["second_effect_idempotency_key"],))
            con.commit()
        finally:
            con.close()
        expect_failure([BIN, "--ledger", tampered_outbox, "--ledger-effect-pending-report", tmp / "bad-outbox-pending.json"], "outbox")

        bad_caps = tmp / "bad-v27-capability.json"
        bad_root = json.loads(CAPS.read_text())
        bad_root["format"] = "anonsync-ledger-backend-capabilities-v27"
        bad_root["backends"]["sqlite-wal"]["ledger_schema_version"] = 8
        bad_root["backends"]["sqlite-wal"].pop("effect_outbox_material_version", None)
        bad_root["backends"]["sqlite-wal"]["snapshot_restore_minimum_capability_version"] = 27
        bad_caps.write_text(json.dumps(bad_root, indent=2, sort_keys=True) + "\n")
        expect_failure([
            BIN,
            "--controls", CONTROLS,
            "--cases-jsonl", CASES,
            "--contracts", CONTRACTS,
            "--ledger", tmp / "bad-ledger.sqlite",
            "--ledger-backend", "sqlite-wal",
            "--ledger-backend-capabilities", bad_caps,
            "--ledger-reset",
            "--ledger-commit-mode", "batch",
            "--report", tmp / "bad-report.json",
        ], "v28 is required")

        summary = {
            "revision_id": "rev0633",
            "validator": "validate_rev0633_effect_outbox_boundary.py",
            "fixture_entries": clean["entry_count"],
            "pending_after_terminal": after["pending_effect_count"],
            "transition_head_hash": transition_head,
            "capability_format": caps_root["format"],
            "sqlite_schema_version": sqlite_caps["ledger_schema_version"],
            "signed_intent_sha256": sha256_hex(valid_intent),
            "security_material_boundary": security_material,
            "checks": [
                "packaged selftests include collision, duplicate metadata, and inherited signed transition coverage",
                "fixture sqlite-wal stream with v28 capability manifest, schema v9 effect_outbox, and regenerated v2 proof digests",
                "rev0631 proof/effect/event-identity newline collision reproduced in validator",
                "v2 length-prefixed proof/effect/event-identity tuples separate the collision pair",
                "control-character collision pair quarantined before ledger append on sqlite-wal and local-jsonl",
                "duplicate case-insensitive Authorization metadata denied before ledger append on both backends",
                "raw terminal transition CLI rejected",
                "raw terminal transition public API selftest rejected",
                "trust-profile digest pin mismatch rejected",
                "wrong ledger_instance_id signed intent rejected",
                "tampered signed intent rejected",
                "stale prepared ledger head rejected",
                "stale transition head rejected",
                "valid signed transition persisted intent id/signer/digest",
                "read-only verifier rejects tampered transition ledger_instance_id",
                "read-only verifier rejects missing effect_outbox coverage",
                "signed terminal transition atomically updates effect_outbox terminal state/result/sequence",
                "downgraded v27 capability mutation rejected",
            ],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
