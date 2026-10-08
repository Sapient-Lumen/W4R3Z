#!/usr/bin/env python3
"""Package-level validator for rev0644 trusted-context-separated ingress."""

import base64
import copy
import hashlib
import json
import pathlib
import re
import sqlite3
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0644" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0644-cpp-ledger-backend-capabilities.json"
OLD_CAPS = ROOT / "gateway" / "rev0643-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0644" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"

SERVICE_FORMAT = "anonsync-ingress-service-config-v6-trusted-context-separated"
REQUEST_FORMAT = "anonsync-ingress-reservation-request-v2-trusted-context-separated"
CONTEXT_FORMAT = "anonsync-ingress-transport-context-v1"
REPORT_FORMAT = "anonsync-ingress-reservation-report-v7-trusted-context-boundary"
SENDER_FORMAT = "anonsync-ingress-sender-possession-v5-lp-rs256-trusted-context"
CACHE_FORMAT = "anonsync-ingress-sender-replay-cache-v4-sqlite-trusted-context-nonce-window-unique"
REPLAY_KEY_FORMAT = "anonsync-ingress-sender-replay-key-v4-nonce-window-unique"
CALLER_KID = "rev0644-validator-caller-rsa-1"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def int_to_b64url(value: int) -> str:
    if value <= 0:
        raise AssertionError("non-positive RSA integer")
    return b64url(value.to_bytes((value.bit_length() + 7) // 8, "big"))


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def framed_tuple(domain: str, fields: List[Tuple[str, str]]) -> str:
    out = "anonsync-length-prefixed-tuple-v1"

    def append(value: str) -> None:
        nonlocal out
        raw = value.encode()
        out += f"{len(raw)}:" + value

    append(domain)
    for key, value in fields:
        append(key)
        append(value)
    return out


def write_json(path: pathlib.Path, obj: Dict[str, Any]) -> str:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha256_text(text)


def generate_sender_key(tmp: pathlib.Path, *, bits: int = 2048, label: str = "sender") -> Tuple[pathlib.Path, Dict[str, str]]:
    key = tmp / f"{label}-rsa.pem"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", f"rsa_keygen_bits:{bits}", "-out", str(key)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    text = subprocess.check_output(
        ["openssl", "rsa", "-in", str(key), "-text", "-noout"], text=True, stderr=subprocess.PIPE
    )
    modulus_hex: List[str] = []
    exponent: Optional[int] = None
    in_modulus = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "modulus:":
            in_modulus = True
            continue
        if in_modulus and stripped.startswith("publicExponent:"):
            in_modulus = False
            match = re.search(r"publicExponent:\s+(\d+)", stripped)
            if match:
                exponent = int(match.group(1))
            continue
        if in_modulus:
            modulus_hex.append(stripped.replace(":", ""))
    if exponent is None or not modulus_hex:
        raise AssertionError("could not parse generated RSA public key")
    mod_hex = "".join(modulus_hex)
    if mod_hex.startswith("00"):
        mod_hex = mod_hex[2:]
    modulus = int(mod_hex, 16)
    return key, {
        "kty": "RSA",
        "kid": CALLER_KID,
        "alg": "RS256",
        "n": int_to_b64url(modulus),
        "e": int_to_b64url(exponent),
    }


def sign_rs256(key: pathlib.Path, material: str) -> str:
    digest = sha256_text(material)[:16]
    material_path = key.parent / f"material-{digest}.bin"
    signature_path = key.parent / f"material-{digest}.sig"
    material_path.write_bytes(material.encode())
    subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(key), "-out", str(signature_path), str(material_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return b64url(signature_path.read_bytes())


def first_case() -> Dict[str, Any]:
    return json.loads(CASES.read_text().splitlines()[0])


def default_context() -> Dict[str, Any]:
    return {
        "format": CONTEXT_FORMAT,
        "transport_authenticated": True,
        "authenticator": "validator-local-transport-boundary",
        "principal": "validator-subject",
    }


def make_context(tmp: pathlib.Path, label: str, overrides: Optional[Dict[str, Any]] = None) -> pathlib.Path:
    context = default_context()
    if overrides:
        context.update(overrides)
    path = tmp / f"{label}.transport-context.json"
    write_json(path, context)
    return path


def make_profile(
    tmp: pathlib.Path,
    *,
    ledger: pathlib.Path,
    handle: str,
    caps: pathlib.Path = CAPS,
) -> Tuple[pathlib.Path, str]:
    profile = {
        "format": "anonsync-ingress-reservation-profile-v1",
        "revision_id": "rev0644-validator",
        "handles": [
            {
                "handle": handle,
                "enabled": True,
                "controls_path": str(CONTROLS),
                "controls_sha256": sha256_file(CONTROLS),
                "contracts_path": str(CONTRACTS),
                "contracts_sha256": sha256_file(CONTRACTS),
                "ledger_path": str(ledger),
                "ledger_backend": "sqlite-wal",
                "ledger_commit_mode": "immediate",
                "ledger_backend_capabilities_path": str(caps),
                "ledger_backend_capabilities_sha256": sha256_file(caps),
                "policy_envelope_key": "normal",
                "ledger_mode": "normal",
            }
        ],
        "blocked_claim": "validator profile only; not a signed operator control plane.",
    }
    path = tmp / f"{handle}.profile.json"
    return path, write_json(path, profile)


def make_service(
    tmp: pathlib.Path,
    *,
    profile: pathlib.Path,
    profile_sha: str,
    public_jwk: Dict[str, str],
    service_id: str,
    cache_instance_id: Optional[str] = None,
    replay_cache_path: Optional[pathlib.Path] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Tuple[pathlib.Path, str]:
    service = {
        "format": SERVICE_FORMAT,
        "revision_id": "rev0644-validator",
        "enabled": True,
        "service_id": service_id,
        "ingress_profile_path": str(profile),
        "ingress_profile_sha256": profile_sha,
        "caller_binding_required": True,
        "caller_binding_material_version": SENDER_FORMAT,
        "caller_binding_public_jwk": copy.deepcopy(public_jwk),
        "sender_replay_cache_path": str(replay_cache_path or (tmp / f"{service_id}.sender-replay.sqlite")),
        "sender_replay_cache_instance_id": cache_instance_id or f"{service_id}-cache-instance",
        "sender_replay_window_seconds": 300,
        "sender_replay_future_skew_seconds": 5,
        "blocked_claim": "validator config only; the context file is not a network authenticator.",
    }
    if extra:
        service.update(extra)
    path = tmp / f"{service_id}.service.json"
    return path, write_json(path, service)


def base_request(handle: str, request_id: str, case: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "format": REQUEST_FORMAT,
        "revision_id": "rev0644-validator",
        "request_id": request_id,
        "config_handle": handle,
        "case": case if case is not None else first_case(),
    }


def sender_material(
    *,
    service_id: str,
    service_sha: str,
    profile_sha: str,
    cache_instance_id: str,
    context: Dict[str, Any],
    request: Dict[str, Any],
) -> Tuple[str, str]:
    proof = request.get("sender_possession", {})
    case_sha = sha256_text(canonical_json(request["case"]))
    material = framed_tuple(
        SENDER_FORMAT,
        [
            ("service_id", service_id),
            ("service_config_sha256", service_sha),
            ("ingress_profile_sha256", profile_sha),
            ("sender_replay_cache_instance_id", cache_instance_id),
            ("sender_proof_alg", "RS256"),
            ("sender_proof_kid", CALLER_KID),
            ("request_format", request["format"]),
            ("request_revision_id", request.get("revision_id", "")),
            ("request_id", request["request_id"]),
            ("config_handle", request["config_handle"]),
            ("transport_authenticated", "true" if context.get("transport_authenticated") else "false"),
            ("authenticator", str(context.get("authenticator", ""))),
            ("principal", str(context.get("principal", ""))),
            ("sender_nonce", str(proof.get("nonce", ""))),
            ("sender_issued_at_epoch", str(proof.get("issued_at_epoch", 0))),
            ("case_sha256", case_sha),
        ],
    )
    return material, case_sha


def add_sender_proof(
    request: Dict[str, Any],
    *,
    sender_key: pathlib.Path,
    service_id: str,
    service_sha: str,
    profile_sha: str,
    cache_instance_id: str,
    context: Dict[str, Any],
    nonce: Optional[str] = None,
    issued_at_epoch: Any = None,
    bad_signature: bool = False,
) -> Dict[str, Any]:
    req = copy.deepcopy(request)
    if issued_at_epoch is None:
        issued_at_epoch = int(time.time())
    req["sender_possession"] = {
        "format": SENDER_FORMAT,
        "kid": CALLER_KID,
        "alg": "RS256",
        "nonce": nonce or f"nonce-{re.sub(r'[^A-Za-z0-9_.~-]', '-', req['request_id'])}-000000",
        "issued_at_epoch": issued_at_epoch,
        "case_sha256": sha256_text(canonical_json(req["case"])),
    }
    material, _ = sender_material(
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        cache_instance_id=cache_instance_id,
        context=context,
        request=req,
    )
    signature = sign_rs256(sender_key, material)
    if bad_signature:
        signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    req["sender_possession"]["signature_b64url"] = signature
    return req


def make_signed_request(
    tmp: pathlib.Path,
    *,
    label: str,
    handle: str,
    sender_key: pathlib.Path,
    service_id: str,
    service_sha: str,
    profile_sha: str,
    context: Dict[str, Any],
    cache_instance_id: Optional[str] = None,
    issued_at_epoch: Any = None,
    bad_signature: bool = False,
    body_extra_after_signing: Optional[Dict[str, Any]] = None,
) -> pathlib.Path:
    req = add_sender_proof(
        base_request(handle, label),
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        cache_instance_id=cache_instance_id or f"{service_id}-cache-instance",
        context=context,
        issued_at_epoch=issued_at_epoch,
        bad_signature=bad_signature,
    )
    if body_extra_after_signing:
        req.update(body_extra_after_signing)
    path = tmp / f"{label}.request.json"
    write_json(path, req)
    return path


def run_cmd(args: List[Any]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(a) for a in args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_service(
    service: pathlib.Path,
    service_sha: str,
    context: pathlib.Path,
    request: pathlib.Path,
    report: pathlib.Path,
) -> subprocess.CompletedProcess[str]:
    return run_cmd(
        [
            BIN,
            "--ingress-service-config",
            service,
            "--ingress-service-config-sha256",
            service_sha,
            "--ingress-transport-context",
            context,
            "--ingress-request",
            request,
            "--ingress-report",
            report,
        ]
    )


def sqlite_line_count(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    con = sqlite3.connect(path)
    try:
        row = con.execute("SELECT line_count FROM metadata WHERE id=1").fetchone()
        return 0 if row is None else int(row[0])
    finally:
        con.close()


def failure_reason(report: pathlib.Path) -> str:
    return json.loads(report.read_text()).get("reservation", {}).get("failure_reason", "")


def assert_fail_before_append(
    *,
    label: str,
    service: pathlib.Path,
    service_sha: str,
    context: pathlib.Path,
    request: pathlib.Path,
    ledger: pathlib.Path,
    expected: str,
) -> None:
    report = request.parent / f"{label}.report.json"
    cp = run_service(service, service_sha, context, request, report)
    if cp.returncode == 0:
        raise AssertionError(f"{label} unexpectedly succeeded")
    reason = failure_reason(report) if report.exists() else ""
    if expected not in reason and expected not in cp.stderr and expected not in cp.stdout:
        raise AssertionError(
            f"{label} did not mention {expected!r}: reason={reason!r} stdout={cp.stdout!r} stderr={cp.stderr!r}"
        )
    if sqlite_line_count(ledger) != 0:
        raise AssertionError(f"{label} appended before failing")


def assert_static_metadata() -> None:
    caps = json.loads(CAPS.read_text())
    if caps.get("format") != "anonsync-ledger-backend-capabilities-v39":
        raise AssertionError("capability format is not exact v39")
    backend = caps["backends"]["sqlite-wal"]
    expected_values = {
        "ingress_service_config_format": SERVICE_FORMAT,
        "ingress_reservation_service_report_format": REPORT_FORMAT,
        "ingress_service_request_format": REQUEST_FORMAT,
        "ingress_transport_context_format": CONTEXT_FORMAT,
        "ingress_sender_possession_material_version": SENDER_FORMAT,
        "ingress_sender_replay_cache_format": CACHE_FORMAT,
        "ingress_sender_replay_key_material_version": REPLAY_KEY_FORMAT,
        "snapshot_restore_minimum_capability_version": 39,
    }
    for key, expected in expected_values.items():
        if backend.get(key) != expected:
            raise AssertionError(f"capability {key} mismatch: {backend.get(key)!r}")
    required_true = [
        "ingress_trusted_transport_context_out_of_band_required",
        "ingress_request_trusted_identity_fields_rejected",
        "ingress_sender_replay_cache_nofollow_required",
        "ingress_sender_replay_clock_override_forbidden",
        "ingress_numeric_fields_integral_and_bounded",
        "ingress_sender_replay_cache_identity_mismatch_rejected_before_append",
        "ingress_sender_replay_cache_duplicate_nonce_rejected_before_append",
        "ingress_sender_replay_nonce_unique_within_retained_window",
        "ingress_sender_replay_rows_pruned_by_issued_at_window",
        "ingress_sender_replay_cache_clock_metadata_monotonic",
        "ingress_sender_replay_cache_wal_and_full_sync_verified",
        "ingress_public_api_digest_pinned_operator_config_handle_required",
        "ingress_ascii_casefold_duplicate_fields_rejected",
        "ingress_json_whitespace_strict_rfc8259",
        "ingress_json_raw_utf8_validation_required",
        "ingress_base64url_decoder_unsigned_accumulator_required",
        "ingress_private_workspace_permissions_fail_closed",
    ]
    missing = [key for key in required_true if backend.get(key) is not True]
    if missing:
        raise AssertionError(f"missing v39 flags: {missing}")
    expected_integers = {
        "ingress_sender_replay_cache_busy_timeout_milliseconds": 5000,
        "ingress_service_config_maximum_bytes": 262144,
        "ingress_request_maximum_bytes": 1048576,
        "ingress_transport_context_maximum_bytes": 16384,
        "ingress_rsa_public_key_minimum_bits": 2048,
    }
    for key, expected in expected_integers.items():
        if backend.get(key) != expected:
            raise AssertionError(f"capability {key} mismatch: {backend.get(key)!r}")
    if backend.get("ingress_sender_replay_cache_and_ledger_atomic_transaction") is not False:
        raise AssertionError("capability must explicitly deny a shared replay-cache/ledger transaction")
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        if manifest.get("revision_id") != "rev0644":
            raise AssertionError("manifest revision is not rev0644")
        if manifest.get("capability_manifest") != "gateway/rev0644-cpp-ledger-backend-capabilities.json":
            raise AssertionError("manifest capability path mismatch")
        entries = manifest.get("files", [])
        if manifest.get("file_count") != len(entries):
            raise AssertionError("manifest file_count mismatch")
        listed = set()
        for entry in entries:
            rel = entry.get("path", "")
            if not rel or rel in listed:
                raise AssertionError(f"manifest has empty or duplicate path: {rel!r}")
            listed.add(rel)
            path = ROOT / rel
            if not path.is_file():
                raise AssertionError(f"manifest-listed file is missing: {rel}")
            if path.stat().st_size != entry.get("size_bytes"):
                raise AssertionError(f"manifest size mismatch: {rel}")
            if sha256_file(path) != entry.get("sha256"):
                raise AssertionError(f"manifest digest mismatch: {rel}")
        excluded = set(manifest.get("excluded_mutable_evidence", []))
        excluded.add(str(MANIFEST.relative_to(ROOT)))
        present = {
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.is_file() and not path.is_symlink() and str(path.relative_to(ROOT)) not in excluded
        }
        if listed != present:
            missing = sorted(present - listed)
            extra = sorted(listed - present)
            raise AssertionError(f"manifest inventory mismatch: missing={missing[:10]} extra={extra[:10]}")
    public_header = (ROOT / "cpp" / "anonsync_core" / "include" / "anonsync_core.hpp").read_text()
    if "struct IngressReservationServiceHandle" not in public_header:
        raise AssertionError("public API lacks the digest-pinned operator service handle")
    public_config_block = public_header.split("struct IngressReservationServiceHandle", 1)[1].split("};", 1)[0]
    forbidden_mutable_fields = ["caller_binding_required", "caller_binding_public_jwk", "sender_replay_window_seconds"]
    leaked = [field for field in forbidden_mutable_fields if field in public_config_block]
    if leaked:
        raise AssertionError(f"public operator service handle leaks mutable security fields: {leaked}")


def assert_success_and_duplicate(tmp: pathlib.Path, sender_key: pathlib.Path, public_jwk: Dict[str, str]) -> Dict[str, Any]:
    handle = "success"
    service_id = "svc-success"
    ledger = tmp / "success.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle=handle)
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id=service_id)
    context_obj = default_context()
    context = make_context(tmp, "success")
    request = make_signed_request(
        tmp,
        label="success",
        handle=handle,
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        context=context_obj,
    )
    report_path = tmp / "success.report.json"
    cp = run_service(service, service_sha, context, request, report_path)
    if cp.returncode != 0:
        raise AssertionError(f"success failed: stdout={cp.stdout!r} stderr={cp.stderr!r} report={report_path.read_text() if report_path.exists() else ''}")
    report = json.loads(report_path.read_text())
    if report.get("format") != REPORT_FORMAT or report.get("revision_id") != "rev0644":
        raise AssertionError("success report format/revision mismatch")
    if report.get("reservation", {}).get("accepted") is not True or sqlite_line_count(ledger) != 1:
        raise AssertionError("success did not append exactly one reservation")
    if report.get("request", {}).get("trusted_transport_context_supplied_as_separate_argument") is not True:
        raise AssertionError("report does not attest separate context argument")
    if report.get("request", {}).get("request_body_trusted_identity_fields_rejected") is not True:
        raise AssertionError("report does not attest body identity rejection")
    service_report = report.get("service", {})
    if service_report.get("sender_replay_cache_format") != CACHE_FORMAT or service_report.get("sender_replay_cache_reserved") is not True:
        raise AssertionError("report does not bind/reserve window-scoped replay cache v4")
    if service_report.get("sender_replay_key_material_version") != REPLAY_KEY_FORMAT:
        raise AssertionError("report does not identify window-scoped replay-key material")
    if service_report.get("sender_replay_nonce_uniqueness_scope") != "retained-replay-window":
        raise AssertionError("report overstates replay nonce uniqueness beyond its retained window")
    boundary = report.get("service_boundary", {})
    if boundary.get("sender_replay_cache_and_ledger_share_one_transaction") is not False:
        raise AssertionError("report incorrectly claims one replay-cache/ledger transaction")
    cache_path = pathlib.Path(json.loads(service.read_text())["sender_replay_cache_path"])
    con = sqlite3.connect(cache_path)
    try:
        meta = dict(con.execute("SELECT meta_key, meta_value FROM sender_replay_meta").fetchall())
        journal_mode = str(con.execute("PRAGMA journal_mode").fetchone()[0]).lower()
        synchronous = int(con.execute("PRAGMA synchronous").fetchone()[0])
    finally:
        con.close()
    if meta.get("format") != CACHE_FORMAT or meta.get("instance_id") != f"{service_id}-cache-instance":
        raise AssertionError("replay cache identity metadata mismatch")
    if journal_mode != "wal" or synchronous != 2:
        raise AssertionError(f"replay cache durability settings mismatch: journal_mode={journal_mode!r} synchronous={synchronous}")

    duplicate_report = tmp / "duplicate.report.json"
    cp = run_service(service, service_sha, context, request, duplicate_report)
    if cp.returncode == 0 or "replay nonce" not in failure_reason(duplicate_report):
        raise AssertionError("duplicate nonce did not fail closed")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("duplicate nonce changed ledger count")

    # The nonce is the uniqueness identity, not the hash of the entire signed proof.
    original = json.loads(request.read_text())
    reused_nonce = original["sender_possession"]["nonce"]
    second = add_sender_proof(
        base_request(handle, "same-nonce-distinct-valid-proof"),
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        cache_instance_id=f"{service_id}-cache-instance",
        context=context_obj,
        nonce=reused_nonce,
        issued_at_epoch=int(original["sender_possession"]["issued_at_epoch"]) + 1,
    )
    second_path = tmp / "same-nonce-distinct-valid-proof.request.json"
    write_json(second_path, second)
    second_report = tmp / "same-nonce-distinct-valid-proof.report.json"
    cp = run_service(service, service_sha, context, second_path, second_report)
    if cp.returncode == 0 or "replay nonce" not in failure_reason(second_report):
        raise AssertionError("same nonce in a distinct valid proof was accepted")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("distinct valid proof with a reused nonce changed ledger count")

    # A small tolerated wall-clock rollback may not move cache metadata backward.
    future_marker = int(time.time()) + 3
    con = sqlite3.connect(cache_path)
    try:
        con.execute("UPDATE sender_replay_meta SET meta_value=? WHERE meta_key='last_seen_epoch'", (str(future_marker),))
        con.commit()
    finally:
        con.close()
    monotonic_request_obj = add_sender_proof(
        base_request(handle, "monotonic-cache-clock", json.loads(CASES.read_text().splitlines()[1])),
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        cache_instance_id=f"{service_id}-cache-instance",
        context=context_obj,
    )
    monotonic_request = tmp / "monotonic-cache-clock.request.json"
    write_json(monotonic_request, monotonic_request_obj)
    monotonic_report = tmp / "monotonic-cache-clock.report.json"
    cp = run_service(service, service_sha, context, monotonic_request, monotonic_report)
    if cp.returncode != 0 or sqlite_line_count(ledger) != 2:
        raise AssertionError(f"monotonic cache-clock request failed: stdout={cp.stdout!r} stderr={cp.stderr!r} report={monotonic_report.read_text() if monotonic_report.exists() else ''} ledger_count={sqlite_line_count(ledger)}")
    con = sqlite3.connect(cache_path)
    try:
        last_seen = int(dict(con.execute("SELECT meta_key, meta_value FROM sender_replay_meta").fetchall())["last_seen_epoch"])
    finally:
        con.close()
    if last_seen < future_marker:
        raise AssertionError("replay-cache last_seen_epoch regressed during tolerated wall-clock rollback")
    return report


def isolated_case(
    tmp: pathlib.Path,
    sender_key: pathlib.Path,
    public_jwk: Dict[str, str],
    label: str,
    *,
    caps: pathlib.Path = CAPS,
    service_extra: Optional[Dict[str, Any]] = None,
    context_overrides: Optional[Dict[str, Any]] = None,
    signing_context: Optional[Dict[str, Any]] = None,
    issued_at_epoch: Any = None,
    bad_signature: bool = False,
    body_extra_after_signing: Optional[Dict[str, Any]] = None,
    replay_cache_path: Optional[pathlib.Path] = None,
) -> Tuple[pathlib.Path, pathlib.Path, str, pathlib.Path, pathlib.Path]:
    ledger = tmp / f"{label}.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle=label, caps=caps)
    service_id = f"svc-{label}"
    service, service_sha = make_service(
        tmp,
        profile=profile,
        profile_sha=profile_sha,
        public_jwk=public_jwk,
        service_id=service_id,
        replay_cache_path=replay_cache_path,
        extra=service_extra,
    )
    actual_context_obj = default_context()
    if context_overrides:
        actual_context_obj.update(context_overrides)
    context_path = make_context(tmp, label, context_overrides)
    signed_context = signing_context if signing_context is not None else actual_context_obj
    request = make_signed_request(
        tmp,
        label=label,
        handle=label,
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        context=signed_context,
        issued_at_epoch=issued_at_epoch,
        bad_signature=bad_signature,
        body_extra_after_signing=body_extra_after_signing,
    )
    return ledger, service, service_sha, context_path, request


def assert_boundary_failures(tmp: pathlib.Path, sender_key: pathlib.Path, public_jwk: Dict[str, str]) -> None:
    # Caller-controlled body can no longer carry fields labelled authenticated.
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "body-auth-injection",
        body_extra_after_signing={
            "authenticated_context": {
                "transport_authenticated": True,
                "authenticator": "attacker-authenticator",
                "principal": "attacker-principal",
            }
        },
    )
    assert_fail_before_append(label="body-auth-injection", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="may not supply trusted transport identity field")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "body-principal-injection",
        body_extra_after_signing={"principal": "attacker-principal"},
    )
    assert_fail_before_append(label="body-principal-injection", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="may not supply trusted transport identity field")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "casefold-duplicate-request-field",
        body_extra_after_signing={"Request_ID": "ambiguous-second-request-id"},
    )
    assert_fail_before_append(label="casefold-duplicate-request-field", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="duplicate ASCII-case-insensitive field")

    # A signature made for one trusted context cannot be replayed under another.
    signed_context = default_context()
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "context-tamper",
        context_overrides={"principal": "different-principal"},
        signing_context=signed_context,
    )
    assert_fail_before_append(label="context-tamper", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="RS256 proof mismatch")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "context-not-authenticated",
        context_overrides={"transport_authenticated": False},
    )
    assert_fail_before_append(label="context-not-authenticated", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="must assert transport_authenticated")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "context-too-long",
        context_overrides={"principal": "p" * 513},
    )
    assert_fail_before_append(label="context-too-long", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="bounded control-free principal")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "fractional-issued-at",
        issued_at_epoch=time.time() + 0.5,
    )
    assert_fail_before_append(label="fractional-issued-at", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="integral JSON number")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "non-interoperable-issued-at",
        issued_at_epoch=9007199254740992,
    )
    assert_fail_before_append(label="non-interoperable-issued-at", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="integral JSON number")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "bad-signature",
        bad_signature=True,
    )
    assert_fail_before_append(label="bad-signature", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="RS256 proof mismatch")

    # The old deterministic production clock hook is now an unsupported config field.
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "clock-override",
        service_extra={"sender_replay_now_epoch": int(time.time())},
    )
    assert_fail_before_append(label="clock-override", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="unsupported field: sender_replay_now_epoch")

    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "fractional-window",
        service_extra={"sender_replay_window_seconds": 300.5},
    )
    assert_fail_before_append(label="fractional-window", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="integral JSON number")

    # Direct symlink targets remain rejected; SQLite is also opened with NOFOLLOW.
    target = tmp / "symlink-target.sqlite"
    target.touch()
    symlink = tmp / "symlink-cache.sqlite"
    symlink.symlink_to(target)
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "cache-symlink",
        replay_cache_path=symlink,
    )
    assert_fail_before_append(label="cache-symlink", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="refuses symlink path")

    # Exact capability version remains mandatory.
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        sender_key,
        public_jwk,
        "capability-downgrade",
        caps=OLD_CAPS,
    )
    assert_fail_before_append(label="capability-downgrade", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="v39 is required")

    # Body size is bounded before JSON parsing/crypto.
    ledger, service, service_sha, context, request = isolated_case(tmp, sender_key, public_jwk, "oversized-request")
    request.write_text("{" + '"padding":"' + ("x" * (1024 * 1024 + 1)) + '"}')
    assert_fail_before_append(label="oversized-request", service=service, service_sha=service_sha, context=context, request=request, ledger=ledger, expected="exceeds the maximum accepted size")

    # CLI refuses the service path unless the separate context operand is present.
    report = tmp / "missing-context.report.json"
    cp = run_cmd([
        BIN,
        "--ingress-service-config", service,
        "--ingress-service-config-sha256", service_sha,
        "--ingress-request", request,
        "--ingress-report", report,
    ])
    if cp.returncode == 0 or "--ingress-transport-context" not in cp.stderr:
        raise AssertionError("service CLI accepted a missing transport-context operand")


def assert_weak_rsa_rejected(tmp: pathlib.Path) -> None:
    weak_key, weak_jwk = generate_sender_key(tmp, bits=1024, label="weak-sender")
    ledger, service, service_sha, context, request = isolated_case(
        tmp,
        weak_key,
        weak_jwk,
        "weak-rsa",
    )
    assert_fail_before_append(
        label="weak-rsa",
        service=service,
        service_sha=service_sha,
        context=context,
        request=request,
        ledger=ledger,
        expected="at least 2048-bit/112-bit security strength",
    )


def assert_dual_write_failure_visible(tmp: pathlib.Path, sender_key: pathlib.Path, public_jwk: Dict[str, str]) -> None:
    label = "dual-write-nonce-burn"
    ledger = tmp / f"{label}.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle=label)
    service_id = f"svc-{label}"
    service, service_sha = make_service(
        tmp,
        profile=profile,
        profile_sha=profile_sha,
        public_jwk=public_jwk,
        service_id=service_id,
    )
    context_obj = default_context()
    context = make_context(tmp, label)
    invalid_case = copy.deepcopy(first_case())
    invalid_case["kind"] = "invalid-after-proof-verification"
    request_obj = add_sender_proof(
        base_request(label, label, invalid_case),
        sender_key=sender_key,
        service_id=service_id,
        service_sha=service_sha,
        profile_sha=profile_sha,
        cache_instance_id=f"{service_id}-cache-instance",
        context=context_obj,
    )
    request = tmp / f"{label}.request.json"
    write_json(request, request_obj)
    report_path = tmp / f"{label}.report.json"
    cp = run_service(service, service_sha, context, request, report_path)
    if cp.returncode == 0:
        raise AssertionError("post-replay profile failure unexpectedly succeeded")
    report = json.loads(report_path.read_text())
    service_report = report.get("service", {})
    boundary = report.get("service_boundary", {})
    if service_report.get("sender_possession_verified") is not True or service_report.get("sender_replay_cache_reserved") is not True:
        raise AssertionError("failure report concealed that the verified proof and nonce were consumed")
    if boundary.get("sender_replay_cache_and_ledger_share_one_transaction") is not False:
        raise AssertionError("failure report concealed the dual-write transaction seam")
    if not (
        boundary.get("sender_replay_reservation_survived_failed_request") is True
        or boundary.get("valid_sender_proof_can_be_consumed_before_profile_or_ledger_failure") is True
    ):
        raise AssertionError("failure report did not expose the surviving replay reservation")
    if sqlite_line_count(ledger) != 0:
        raise AssertionError("post-replay profile failure unexpectedly appended to the ledger")
    retry_report = tmp / f"{label}.retry.report.json"
    retry = run_service(service, service_sha, context, request, retry_report)
    if retry.returncode == 0 or "replay nonce" not in failure_reason(retry_report):
        raise AssertionError("consumed nonce was not rejected on retry")
    if sqlite_line_count(ledger) != 0:
        raise AssertionError("dual-write retry unexpectedly changed the ledger")


def main() -> None:
    if not BIN.exists():
        raise SystemExit(f"packaged binary missing: {BIN}")
    assert_static_metadata()
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0644-trusted-context-") as td:
        tmp = pathlib.Path(td)
        sender_key, public_jwk = generate_sender_key(tmp)
        success_report = assert_success_and_duplicate(tmp, sender_key, public_jwk)
        assert_boundary_failures(tmp, sender_key, public_jwk)
        assert_weak_rsa_rejected(tmp)
        assert_dual_write_failure_visible(tmp, sender_key, public_jwk)
        audit = {
            "validator": "rev0644-trusted-context-boundary",
            "binary": str(BIN.relative_to(ROOT)),
            "binary_sha256": sha256_file(BIN),
            "capabilities_sha256": sha256_file(CAPS),
            "successful_report_digest": sha256_text(canonical_json(success_report)),
            "caller_public_jwk_sha256": sha256_text(canonical_json(public_jwk)),
            "checks": [
                "successful RS256 reservation with separately supplied trusted transport context",
                "nonce uniqueness within the retained window across exact replay and distinct valid proofs",
                "replay-cache WAL/FULL settings and monotonic last-seen clock metadata",
                "request-side authenticated_context and principal injection rejection",
                "ASCII-case-insensitive duplicate security-field rejection",
                "trusted-context tamper causes signature mismatch",
                "unauthenticated and oversized context rejection",
                "fractional and non-interoperable issued_at plus fractional replay-window numeric rejection",
                "service-config replay clock override rejection",
                "replay-cache symlink rejection and capability declaration of SQLite NOFOLLOW",
                "public API exposes only a digest-pinned operator config handle, not mutable security fields",
                "minimum 2048-bit RSA public key enforcement",
                "post-replay profile failure visibly consumes the nonce without a ledger append",
                "bad RS256 signature rejection",
                "exact v39 capability downgrade rejection",
                "one-megabyte request-body ceiling enforcement",
                "missing separate CLI transport-context operand rejection",
            ],
            "result": "passed",
        }
    out = ROOT / "audit" / "rev0644-trusted-context-boundary-package-validator.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
