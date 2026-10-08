#!/usr/bin/env python3
import base64
import hashlib
import json
import pathlib
import re
import sqlite3
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0641" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0641-cpp-ledger-backend-capabilities.json"
OLD_CAPS = ROOT / "gateway" / "rev0640-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0641" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"
SENDER_FORMAT = "anonsync-ingress-sender-possession-v2-lp-rs256"
CALLER_KID = "rev0641-validator-caller-rsa-1"


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
    for k, v in fields:
        append(k)
        append(v)
    return out


def generate_sender_key(tmp: pathlib.Path) -> Tuple[pathlib.Path, Dict[str, str]]:
    key = tmp / "sender-rsa.pem"
    subprocess.run([
        "openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key)
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    text = subprocess.check_output(["openssl", "rsa", "-in", str(key), "-text", "-noout"], text=True, stderr=subprocess.PIPE)
    modulus_hex: List[str] = []
    in_modulus = False
    exponent = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "modulus:":
            in_modulus = True
            continue
        if in_modulus and stripped.startswith("publicExponent:"):
            in_modulus = False
            m = re.search(r"publicExponent:\s+(\d+)", stripped)
            if not m:
                raise AssertionError("could not parse public exponent")
            exponent = int(m.group(1))
            continue
        if in_modulus:
            modulus_hex.append(stripped.replace(":", ""))
    if exponent is None or not modulus_hex:
        raise AssertionError("could not parse RSA public key from OpenSSL output")
    mod_hex = "".join(modulus_hex)
    if mod_hex.startswith("00"):
        mod_hex = mod_hex[2:]
    modulus = int(mod_hex, 16)
    jwk = {
        "kty": "RSA",
        "kid": CALLER_KID,
        "alg": "RS256",
        "n": int_to_b64url(modulus),
        "e": int_to_b64url(exponent),
    }
    return key, jwk


def sign_rs256(key: pathlib.Path, material: str) -> str:
    material_path = key.parent / ("material-" + hashlib.sha256(material.encode()).hexdigest()[:16] + ".bin")
    sig_path = key.parent / (material_path.stem + ".sig")
    material_path.write_bytes(material.encode())
    subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key), "-out", str(sig_path), str(material_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return b64url(sig_path.read_bytes())


def sender_material(*, service_id: str, service_sha: str, profile_sha: str, request: Dict[str, Any]) -> Tuple[str, str]:
    ctx = request["authenticated_context"]
    case_sha = sha256_text(canonical_json(request["case"]))
    material = framed_tuple(SENDER_FORMAT, [
        ("service_id", service_id),
        ("service_config_sha256", service_sha),
        ("ingress_profile_sha256", profile_sha),
        ("sender_proof_alg", "RS256"),
        ("sender_proof_kid", CALLER_KID),
        ("request_format", request["format"]),
        ("request_revision_id", request.get("revision_id", "")),
        ("request_id", request["request_id"]),
        ("config_handle", request["config_handle"]),
        ("transport_authenticated", "true" if ctx.get("transport_authenticated") else "false"),
        ("authenticator", ctx.get("authenticator", "")),
        ("principal", ctx.get("principal", "")),
        ("case_sha256", case_sha),
    ])
    return material, case_sha


def add_sender_proof(req: Dict[str, Any], *, sender_key: pathlib.Path, service_id: str, service_sha: str, profile_sha: str, bad_sig: bool = False, bad_case_digest: bool = False, bad_alg: bool = False, bad_kid: bool = False, extra_proof: Dict[str, Any] | None = None) -> Dict[str, Any]:
    req = json.loads(json.dumps(req))
    material, case_sha = sender_material(service_id=service_id, service_sha=service_sha, profile_sha=profile_sha, request=req)
    sig = sign_rs256(sender_key, material)
    if bad_sig:
        sig = ("A" if sig[0] != "A" else "B") + sig[1:]
    proof_case_sha = ("1" * 64) if bad_case_digest else case_sha
    proof = {
        "format": SENDER_FORMAT,
        "kid": "wrong-kid" if bad_kid else CALLER_KID,
        "alg": "HS256" if bad_alg else "RS256",
        "case_sha256": proof_case_sha,
        "signature_b64url": sig,
    }
    if extra_proof:
        proof.update(extra_proof)
    req["authenticated_context"]["sender_possession"] = proof
    return req


def write_json(path: pathlib.Path, obj: Dict[str, Any]) -> str:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def first_case() -> Dict[str, Any]:
    return json.loads(CASES.read_text().splitlines()[0])


def make_profile(tmp: pathlib.Path, *, ledger: pathlib.Path, caps: pathlib.Path = CAPS, enabled: bool = True, duplicate: bool = False, handle: str = "primary") -> Tuple[pathlib.Path, str]:
    entry = {
        "handle": handle,
        "enabled": enabled,
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
    handles = [entry]
    if duplicate:
        handles.append(dict(entry))
    profile = {
        "format": "anonsync-ingress-reservation-profile-v1",
        "revision_id": "rev0641-validator",
        "handles": handles,
        "blocked_claim": "validator profile only; not a signed operator control plane.",
    }
    path = tmp / ("profile-" + handle + ".json")
    return path, write_json(path, profile)


def make_service(tmp: pathlib.Path, *, profile: pathlib.Path, profile_sha: str, public_jwk: Dict[str, str], enabled: bool = True, service_id: str = "svc-primary", caller_binding_required: bool = True, include_symmetric_secret: bool = False, invalid_jwk: bool = False) -> Tuple[pathlib.Path, str]:
    jwk = dict(public_jwk)
    if invalid_jwk:
        jwk["n"] = "not_base64url@@"
    service = {
        "format": "anonsync-ingress-service-config-v3-asymmetric-sender-possession",
        "revision_id": "rev0641-validator",
        "enabled": enabled,
        "service_id": service_id,
        "ingress_profile_path": str(profile),
        "ingress_profile_sha256": profile_sha,
        "caller_binding_required": caller_binding_required,
        "caller_binding_material_version": SENDER_FORMAT,
        "caller_binding_public_jwk": jwk,
        "blocked_claim": "validator service config only; pins public caller key but is not a deployed listener, DPoP verifier, or signed control plane.",
    }
    if include_symmetric_secret:
        service["caller_binding_secret_id"] = "should-not-exist"
        service["caller_binding_hmac_sha256_secret"] = "symmetric-secret-regression"
    path = tmp / (service_id + ".service.json")
    return path, write_json(path, service)


def base_request(*, case: Dict[str, Any] | None = None, handle: str = "primary", request_id: str = "validator-001", extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    req = {
        "format": "anonsync-ingress-reservation-request-v1",
        "revision_id": "rev0641-validator",
        "request_id": request_id,
        "config_handle": handle,
        "authenticated_context": {
            "transport_authenticated": True,
            "authenticator": "validator-local-transport-boundary",
            "principal": "validator-subject",
        },
        "case": case if case is not None else first_case(),
    }
    if extra:
        req.update(extra)
    return req


def make_request(tmp: pathlib.Path, *, sender_key: pathlib.Path, service_id: str, service_sha: str, profile_sha: str, case: Dict[str, Any] | None = None, handle: str = "primary", request_id: str = "validator-001", extra: Dict[str, Any] | None = None, bad_sig: bool = False, bad_case_digest: bool = False, bad_alg: bool = False, bad_kid: bool = False, missing_proof: bool = False, extra_proof: Dict[str, Any] | None = None) -> pathlib.Path:
    req = base_request(case=case, handle=handle, request_id=request_id, extra=extra)
    if not missing_proof:
        req = add_sender_proof(req, sender_key=sender_key, service_id=service_id, service_sha=service_sha, profile_sha=profile_sha, bad_sig=bad_sig, bad_case_digest=bad_case_digest, bad_alg=bad_alg, bad_kid=bad_kid, extra_proof=extra_proof)
    path = tmp / (request_id + ".request.json")
    write_json(path, req)
    return path


def run_cmd(args: List[Any]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(a) for a in args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_service(service: pathlib.Path, service_sha: str, request: pathlib.Path, report: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return run_cmd([BIN, "--ingress-service-config", service, "--ingress-service-config-sha256", service_sha, "--ingress-request", request, "--ingress-report", report])


def load_report(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def sqlite_line_count(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    con = sqlite3.connect(path)
    try:
        row = con.execute("SELECT line_count FROM metadata WHERE id=1").fetchone()
        return 0 if row is None else row[0]
    finally:
        con.close()


def assert_static_metadata() -> None:
    caps = json.loads(CAPS.read_text())
    if caps["format"] != "anonsync-ledger-backend-capabilities-v36":
        raise AssertionError("capability format is not v36")
    sqlite_caps = caps["backends"]["sqlite-wal"]
    required = [
        "ingress_reservation_service_api_supported",
        "ingress_reservation_service_command_supported",
        "ingress_service_config_digest_pin_required",
        "ingress_service_config_pins_profile",
        "ingress_request_no_filesystem_operands_required",
        "ingress_service_report_binds_service_profile_request_and_reservation",
        "ingress_service_sender_possession_required",
        "ingress_sender_possession_rs256_required",
        "ingress_sender_possession_public_jwk_required",
        "ingress_sender_possession_binds_service_profile_request_principal_case",
        "ingress_service_rejects_bad_sender_possession_before_append",
        "ingress_service_rejects_symmetric_caller_secret",
        "ingress_sender_possession_private_secret_absent_from_service_config",
    ]
    missing = [k for k in required if sqlite_caps.get(k) is not True]
    if missing:
        raise AssertionError(f"missing v36 ingress service capability flags: {missing}")
    if sqlite_caps.get("ingress_service_config_format") != "anonsync-ingress-service-config-v3-asymmetric-sender-possession":
        raise AssertionError("missing service config v3 asymmetric sender-possession format")
    if sqlite_caps.get("ingress_reservation_service_report_format") != "anonsync-ingress-reservation-report-v4-asymmetric-sender-boundary":
        raise AssertionError("missing service report v4 format")
    if sqlite_caps.get("ingress_sender_possession_material_version") != SENDER_FORMAT:
        raise AssertionError("missing sender possession material version")
    if sqlite_caps.get("ingress_sender_possession_hmac_sha256_required") is not False:
        raise AssertionError("v36 must not claim HMAC sender possession is required")
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        if manifest.get("revision_id") != "rev0641":
            raise AssertionError("manifest revision is not rev0641")
        if manifest.get("capability_manifest") != "gateway/rev0641-cpp-ledger-backend-capabilities.json":
            raise AssertionError("manifest does not point at rev0641 capability manifest")


def assert_successful_service_reservation(tmp: pathlib.Path, sender_key: pathlib.Path, public_jwk: Dict[str, str]) -> Tuple[pathlib.Path, pathlib.Path, Dict[str, Any], pathlib.Path, str, str, str]:
    ledger = tmp / "success.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger)
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk)
    request = make_request(tmp, sender_key=sender_key, service_id="svc-primary", service_sha=service_sha, profile_sha=profile_sha)
    report_path = tmp / "success-report.json"
    cp = run_service(service, service_sha, request, report_path)
    if cp.returncode != 0:
        raise AssertionError(f"successful service ingress failed: stdout={cp.stdout} stderr={cp.stderr} report={report_path.read_text() if report_path.exists() else ''}")
    report = load_report(report_path)
    if report["format"] != "anonsync-ingress-reservation-report-v4-asymmetric-sender-boundary" or report["revision_id"] != "rev0641":
        raise AssertionError("service report did not advance to rev0641/v4")
    if not report["reservation"].get("accepted"):
        raise AssertionError("service report did not reserve an outbox row")
    service_section = report["service"]
    if service_section.get("caller_binding_material_version") != SENDER_FORMAT:
        raise AssertionError("report did not bind v2 sender material")
    if service_section.get("caller_binding_key_id") != CALLER_KID or service_section.get("caller_binding_alg") != "RS256":
        raise AssertionError("report did not bind public JWK kid/alg")
    if service_section.get("symmetric_caller_secret_present") is not False:
        raise AssertionError("report indicates a symmetric caller secret remains present")
    if not service_section.get("sender_possession_verified"):
        raise AssertionError("sender possession was not reported verified")
    if report["request"].get("sender_proof_alg") != "RS256" or report["request"].get("sender_proof_kid") != CALLER_KID:
        raise AssertionError("request report did not bind RS256 proof metadata")
    if "RS256 signature verified" not in report["request"].get("sender_proof_verification_reason", ""):
        raise AssertionError("OpenSSL RS256 verification reason missing")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("successful service ingress did not append exactly one durable row")
    return ledger, request, report, service, service_sha, profile_sha, "svc-primary"


def assert_duplicate_rejected(tmp: pathlib.Path, sender_key: pathlib.Path, ledger: pathlib.Path, request: pathlib.Path, service: pathlib.Path, service_sha: str, profile_sha: str) -> None:
    req = json.loads(request.read_text())
    req["config_handle"] = "primary"
    req["request_id"] = "validator-duplicate"
    req["authenticated_context"].pop("sender_possession", None)
    req = add_sender_proof(req, sender_key=sender_key, service_id="svc-primary", service_sha=service_sha, profile_sha=profile_sha)
    dup_req = tmp / "duplicate.request.json"
    write_json(dup_req, req)
    report = tmp / "duplicate-report.json"
    cp = run_service(service, service_sha, dup_req, report)
    if cp.returncode == 0:
        raise AssertionError("duplicate service ingress replay unexpectedly succeeded")
    body = load_report(report)
    if body.get("reservation", {}).get("accepted"):
        raise AssertionError("duplicate service ingress produced a reservation")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("duplicate service ingress changed durable line count")


def assert_fail_before_append(tmp: pathlib.Path, label: str, service: pathlib.Path, service_sha: str, request: pathlib.Path, ledger: pathlib.Path, expected_text: str) -> None:
    report = tmp / f"{label}-report.json"
    cp = run_service(service, service_sha, request, report)
    if cp.returncode == 0:
        raise AssertionError(f"{label} unexpectedly succeeded")
    body = load_report(report)
    reason = body.get("reservation", {}).get("failure_reason", "")
    if expected_text not in reason and expected_text not in cp.stderr and expected_text not in cp.stdout:
        raise AssertionError(f"{label} failure did not mention {expected_text!r}: reason={reason!r} stdout={cp.stdout!r} stderr={cp.stderr!r}")
    if sqlite_line_count(ledger) != 0:
        raise AssertionError(f"{label} appended to ledger before failing")


def assert_failures(tmp: pathlib.Path, sender_key: pathlib.Path, public_jwk: Dict[str, str]) -> None:
    ledger = tmp / "bad-service-sha.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="badsha")
    service, _ = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-badsha")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-badsha", service_sha="0" * 64, profile_sha=profile_sha, handle="badsha", request_id="badsha")
    assert_fail_before_append(tmp, "bad-service-sha", service, "0" * 64, req, ledger, "service config digest pin mismatch")

    ledger = tmp / "disabled-service.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="disabled-service")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, enabled=False, service_id="svc-disabled")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-disabled", service_sha=service_sha, profile_sha=profile_sha, handle="disabled-service", request_id="disabled-service")
    assert_fail_before_append(tmp, "disabled-service", service, service_sha, req, ledger, "disabled")

    ledger = tmp / "profile-drift.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="profile-drift")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-profile-drift")
    profile.write_text(profile.read_text() + "\n")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-profile-drift", service_sha=service_sha, profile_sha=profile_sha, handle="profile-drift", request_id="profile-drift")
    assert_fail_before_append(tmp, "profile-drift", service, service_sha, req, ledger, "operator profile digest pin mismatch")

    ledger = tmp / "bad-signature.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="bad-signature")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-bad-signature")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-bad-signature", service_sha=service_sha, profile_sha=profile_sha, handle="bad-signature", request_id="bad-signature", bad_sig=True)
    assert_fail_before_append(tmp, "bad-signature", service, service_sha, req, ledger, "RS256 proof mismatch")

    ledger = tmp / "missing-proof.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="missing-proof")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-missing-proof")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-missing-proof", service_sha=service_sha, profile_sha=profile_sha, handle="missing-proof", request_id="missing-proof", missing_proof=True)
    assert_fail_before_append(tmp, "missing-proof", service, service_sha, req, ledger, "sender_possession")

    ledger = tmp / "case-digest.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="case-digest")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-case-digest")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-case-digest", service_sha=service_sha, profile_sha=profile_sha, handle="case-digest", request_id="case-digest", bad_case_digest=True)
    assert_fail_before_append(tmp, "case-digest", service, service_sha, req, ledger, "case digest mismatch")

    ledger = tmp / "bad-alg.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="bad-alg")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-bad-alg")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-bad-alg", service_sha=service_sha, profile_sha=profile_sha, handle="bad-alg", request_id="bad-alg", bad_alg=True)
    assert_fail_before_append(tmp, "bad-alg", service, service_sha, req, ledger, "proof alg")

    ledger = tmp / "bad-kid.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="bad-kid")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-bad-kid")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-bad-kid", service_sha=service_sha, profile_sha=profile_sha, handle="bad-kid", request_id="bad-kid", bad_kid=True)
    assert_fail_before_append(tmp, "bad-kid", service, service_sha, req, ledger, "proof kid")

    ledger = tmp / "proof-extra.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="proof-extra")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-proof-extra")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-proof-extra", service_sha=service_sha, profile_sha=profile_sha, handle="proof-extra", request_id="proof-extra", extra_proof={"hmac_sha256": "0" * 64})
    assert_fail_before_append(tmp, "proof-extra", service, service_sha, req, ledger, "unsupported field")

    ledger = tmp / "context-extra.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="context-extra")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-context-extra")
    req_obj = base_request(handle="context-extra", request_id="context-extra")
    req_obj["authenticated_context"]["ledger_path"] = str(tmp / "attacker.sqlite")
    req_obj = add_sender_proof(req_obj, sender_key=sender_key, service_id="svc-context-extra", service_sha=service_sha, profile_sha=profile_sha)
    req = tmp / "context-extra.request.json"
    write_json(req, req_obj)
    assert_fail_before_append(tmp, "context-extra", service, service_sha, req, ledger, "authenticated_context contains unsupported field")

    ledger = tmp / "symmetric-secret.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="symmetric-secret")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-symmetric-secret", include_symmetric_secret=True)
    req = make_request(tmp, sender_key=sender_key, service_id="svc-symmetric-secret", service_sha=service_sha, profile_sha=profile_sha, handle="symmetric-secret", request_id="symmetric-secret")
    assert_fail_before_append(tmp, "symmetric-secret", service, service_sha, req, ledger, "symmetric")

    ledger = tmp / "invalid-jwk.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="invalid-jwk")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-invalid-jwk", invalid_jwk=True)
    req = make_request(tmp, sender_key=sender_key, service_id="svc-invalid-jwk", service_sha=service_sha, profile_sha=profile_sha, handle="invalid-jwk", request_id="invalid-jwk")
    assert_fail_before_append(tmp, "invalid-jwk", service, service_sha, req, ledger, "public JWK")

    ledger = tmp / "operator-field.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="operator-field")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-operator-field")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-operator-field", service_sha=service_sha, profile_sha=profile_sha, handle="operator-field", request_id="operator-field", extra={"ingress_profile_path": str(tmp / "attacker-profile.json")})
    assert_fail_before_append(tmp, "operator-field", service, service_sha, req, ledger, "operator field")

    ledger = tmp / "ledger-mode.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="ledger-mode")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-ledger-mode")
    case = first_case()
    case["http_request"]["headers"]["x-anonsync-ledger-mode"] = "split_brain"
    req = make_request(tmp, sender_key=sender_key, service_id="svc-ledger-mode", service_sha=service_sha, profile_sha=profile_sha, case=case, handle="ledger-mode", request_id="ledger-mode")
    assert_fail_before_append(tmp, "ledger-mode", service, service_sha, req, ledger, "ledger mode")

    ledger = tmp / "v35-downgrade.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, caps=OLD_CAPS, handle="downgrade")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, public_jwk=public_jwk, service_id="svc-downgrade")
    req = make_request(tmp, sender_key=sender_key, service_id="svc-downgrade", service_sha=service_sha, profile_sha=profile_sha, handle="downgrade", request_id="downgrade")
    assert_fail_before_append(tmp, "downgrade", service, service_sha, req, ledger, "v36")

    combined_report = tmp / "combined-report.json"
    cp = run_cmd([
        BIN,
        "--ingress-service-config", service,
        "--ingress-service-config-sha256", service_sha,
        "--ingress-profile", profile,
        "--ingress-profile-sha256", profile_sha,
        "--ingress-request", req,
        "--ingress-report", combined_report,
    ])
    if cp.returncode == 0 or "cannot be combined" not in cp.stderr:
        raise AssertionError("combined service/profile CLI did not fail closed")
    if sqlite_line_count(ledger) != 0:
        raise AssertionError("combined service/profile CLI appended before failing")


def main() -> None:
    if not BIN.exists():
        raise SystemExit(f"packaged binary missing: {BIN}")
    assert_static_metadata()
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0641-ingress-rs256-") as td:
        tmp = pathlib.Path(td)
        sender_key, public_jwk = generate_sender_key(tmp)
        ledger, request, report, service, service_sha, profile_sha, _svc = assert_successful_service_reservation(tmp, sender_key, public_jwk)
        assert_duplicate_rejected(tmp, sender_key, ledger, request, service, service_sha, profile_sha)
        assert_failures(tmp, sender_key, public_jwk)
        audit = {
            "validator": "rev0641-service-asymmetric-sender-possession-ingress-reservation",
            "binary": str(BIN.relative_to(ROOT)),
            "binary_sha256": sha256_file(BIN),
            "capabilities_sha256": sha256_file(CAPS),
            "successful_report_digest": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest(),
            "caller_public_jwk_sha256": sha256_text(canonical_json(public_jwk)),
            "checks": [
                "successful RS256 sender-bound service durable reservation",
                "duplicate replay does not append",
                "service config digest mismatch fails before append",
                "disabled service config fails before append",
                "profile digest drift fails before append",
                "bad RS256 sender-possession signature fails before append",
                "missing sender-possession proof fails before append",
                "sender case digest mismatch fails before append",
                "sender proof alg mismatch fails before append",
                "sender proof kid mismatch fails before append",
                "sender proof HMAC regression field fails before append",
                "unsupported authenticated_context field fails before append",
                "service config symmetric caller secret fails before append",
                "invalid caller public JWK fails before append",
                "request operator field fails before append",
                "request ledger-mode selection fails before append",
                "v35 capability downgrade fails before append",
                "service and direct profile CLI combination is rejected",
            ],
            "result": "passed",
        }
    out = ROOT / "audit" / "rev0641-ingress-sender-rs256-package-validator.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
