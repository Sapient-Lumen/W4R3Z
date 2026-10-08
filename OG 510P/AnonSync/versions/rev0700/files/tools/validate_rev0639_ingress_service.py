#!/usr/bin/env python3
import hashlib
import json
import pathlib
import sqlite3
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0639" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0639-cpp-ledger-backend-capabilities.json"
OLD_CAPS = ROOT / "gateway" / "rev0638-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0639" / "slim-cube-manifest.json"
CONTROLS = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-context.json"
CONTRACTS = ROOT / "gateway" / "rev0618-cpp-slim-normalization-contract-table.json"
CASES = ROOT / "fixtures" / "rev0618" / "cpp-slim-gateway-cases.jsonl"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
        "revision_id": "rev0639-validator",
        "handles": handles,
        "blocked_claim": "validator profile only; not a signed operator control plane.",
    }
    path = tmp / ("profile-" + handle + ".json")
    return path, write_json(path, profile)


def make_service(tmp: pathlib.Path, *, profile: pathlib.Path, profile_sha: str, enabled: bool = True, service_id: str = "svc-primary") -> Tuple[pathlib.Path, str]:
    service = {
        "format": "anonsync-ingress-service-config-v1",
        "revision_id": "rev0639-validator",
        "enabled": enabled,
        "service_id": service_id,
        "ingress_profile_path": str(profile),
        "ingress_profile_sha256": profile_sha,
        "blocked_claim": "validator service config only; not a deployed listener or signed control plane.",
    }
    path = tmp / (service_id + ".service.json")
    return path, write_json(path, service)


def make_request(tmp: pathlib.Path, *, case: Dict[str, Any] | None = None, handle: str = "primary", request_id: str = "validator-001", extra: Dict[str, Any] | None = None) -> pathlib.Path:
    req = {
        "format": "anonsync-ingress-reservation-request-v1",
        "revision_id": "rev0639-validator",
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
        return con.execute("SELECT line_count FROM metadata WHERE id=1").fetchone()[0]
    finally:
        con.close()


def assert_static_metadata() -> None:
    caps = json.loads(CAPS.read_text())
    if caps["format"] != "anonsync-ledger-backend-capabilities-v34":
        raise AssertionError("capability format is not v34")
    sqlite_caps = caps["backends"]["sqlite-wal"]
    required = [
        "ingress_reservation_service_api_supported",
        "ingress_reservation_service_command_supported",
        "ingress_service_config_digest_pin_required",
        "ingress_service_config_pins_profile",
        "ingress_request_no_filesystem_operands_required",
        "ingress_service_report_binds_service_profile_request_and_reservation",
    ]
    missing = [k for k in required if sqlite_caps.get(k) is not True]
    if missing:
        raise AssertionError(f"missing v34 ingress service capability flags: {missing}")
    if sqlite_caps.get("ingress_service_config_format") != "anonsync-ingress-service-config-v1":
        raise AssertionError("missing service config format")
    if sqlite_caps.get("ingress_reservation_service_report_format") != "anonsync-ingress-reservation-report-v2-service-boundary":
        raise AssertionError("missing service report v2 format")
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        if manifest.get("revision_id") != "rev0639":
            raise AssertionError("manifest revision is not rev0639")
        if manifest.get("capability_manifest") != "gateway/rev0639-cpp-ledger-backend-capabilities.json":
            raise AssertionError("manifest does not point at rev0639 capability manifest")


def assert_successful_service_reservation(tmp: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path, Dict[str, Any], pathlib.Path, str]:
    ledger = tmp / "success.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger)
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha)
    request = make_request(tmp)
    report_path = tmp / "success-report.json"
    cp = run_service(service, service_sha, request, report_path)
    if cp.returncode != 0:
        raise AssertionError(f"ingress service reservation failed unexpectedly rc={cp.returncode}\nstdout={cp.stdout}\nstderr={cp.stderr}")
    report = load_report(report_path)
    if report["format"] != "anonsync-ingress-reservation-report-v2-service-boundary" or report["revision_id"] != "rev0639":
        raise AssertionError("service ingress report format/revision mismatch")
    if not report["service"].get("service_config_digest_pin_verified"):
        raise AssertionError("service config digest evidence absent")
    if not report["service"].get("request_cannot_select_profile_or_operator_paths"):
        raise AssertionError("service boundary evidence absent")
    if report["request"].get("request_supplied_filesystem_operands") is not False:
        raise AssertionError("request filesystem operand evidence incorrect")
    reservation = report["reservation"]
    if not reservation.get("accepted") or reservation.get("outbox_state") != "reserved":
        raise AssertionError("successful service ingress did not return a reserved outbox row")
    if reservation.get("ledger_sequence") != 1 or len(reservation.get("entry_hash", "")) != 64 or len(reservation.get("effect_idempotency_key", "")) != 64:
        raise AssertionError("reservation evidence is incomplete")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("ledger did not persist exactly one reservation")
    return ledger, request, report, service, service_sha


def assert_duplicate_rejected(tmp: pathlib.Path, ledger: pathlib.Path, request: pathlib.Path) -> None:
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="dupe")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-dupe")
    req = json.loads(request.read_text())
    req["config_handle"] = "dupe"
    req["request_id"] = "validator-duplicate"
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


def assert_failures(tmp: pathlib.Path) -> None:
    ledger = tmp / "bad-service-sha.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="badsha")
    service, _ = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-badsha")
    req = make_request(tmp, handle="badsha", request_id="badsha")
    assert_fail_before_append(tmp, "bad-service-sha", service, "0" * 64, req, ledger, "service config digest pin mismatch")

    ledger = tmp / "disabled-service.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="disabled-service")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, enabled=False, service_id="svc-disabled")
    req = make_request(tmp, handle="disabled-service", request_id="disabled-service")
    assert_fail_before_append(tmp, "disabled-service", service, service_sha, req, ledger, "disabled")

    ledger = tmp / "profile-drift.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="profile-drift")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-profile-drift")
    profile.write_text(profile.read_text() + "\n")
    req = make_request(tmp, handle="profile-drift", request_id="profile-drift")
    assert_fail_before_append(tmp, "profile-drift", service, service_sha, req, ledger, "operator profile digest pin mismatch")

    ledger = tmp / "operator-field.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="operator-field")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-operator-field")
    req = make_request(tmp, handle="operator-field", request_id="operator-field", extra={"ingress_profile_path": str(tmp / "attacker-profile.json")})
    assert_fail_before_append(tmp, "operator-field", service, service_sha, req, ledger, "operator field")

    ledger = tmp / "ledger-mode.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="ledger-mode")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-ledger-mode")
    case = first_case()
    case["http_request"]["headers"]["x-anonsync-ledger-mode"] = "split_brain"
    req = make_request(tmp, case=case, handle="ledger-mode", request_id="ledger-mode")
    assert_fail_before_append(tmp, "ledger-mode", service, service_sha, req, ledger, "ledger mode")

    ledger = tmp / "v33-downgrade.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, caps=OLD_CAPS, handle="downgrade")
    service, service_sha = make_service(tmp, profile=profile, profile_sha=profile_sha, service_id="svc-downgrade")
    req = make_request(tmp, handle="downgrade", request_id="downgrade")
    assert_fail_before_append(tmp, "downgrade", service, service_sha, req, ledger, "v34")

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
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0639-ingress-service-") as td:
        tmp = pathlib.Path(td)
        ledger, request, report, _service, _service_sha = assert_successful_service_reservation(tmp)
        assert_duplicate_rejected(tmp, ledger, request)
        assert_failures(tmp)
        audit = {
            "validator": "rev0639-service-bound-ingress-reservation",
            "binary": str(BIN.relative_to(ROOT)),
            "binary_sha256": sha256_file(BIN),
            "capabilities_sha256": sha256_file(CAPS),
            "successful_report_digest": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest(),
            "checks": [
                "successful service-bound durable reservation",
                "duplicate replay does not append",
                "service config digest mismatch fails before append",
                "disabled service config fails before append",
                "profile digest drift fails before append",
                "request operator field fails before append",
                "request ledger-mode selection fails before append",
                "v33 capability downgrade fails before append",
                "service and direct profile CLI combination is rejected",
            ],
            "result": "passed",
        }
    out = ROOT / "audit" / "rev0639-ingress-service-package-validator.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
