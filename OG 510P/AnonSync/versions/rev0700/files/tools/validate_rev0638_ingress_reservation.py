#!/usr/bin/env python3
import hashlib
import json
import pathlib
import shutil
import sqlite3
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "rev0638" / "anonsync_core-linux-x86_64-gcc-openssl3-sqlite3"
CAPS = ROOT / "gateway" / "rev0638-cpp-ledger-backend-capabilities.json"
OLD_CAPS = ROOT / "gateway" / "rev0637-cpp-ledger-backend-capabilities.json"
MANIFEST = ROOT / "schema" / "rev0638" / "slim-cube-manifest.json"
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
        "revision_id": "rev0638-validator",
        "handles": handles,
        "blocked_claim": "validator profile only; not a signed operator control plane.",
    }
    path = tmp / ("profile-" + handle + ".json")
    return path, write_json(path, profile)


def make_request(tmp: pathlib.Path, *, case: Dict[str, Any] | None = None, handle: str = "primary", request_id: str = "validator-001", extra: Dict[str, Any] | None = None) -> pathlib.Path:
    req = {
        "format": "anonsync-ingress-reservation-request-v1",
        "revision_id": "rev0638-validator",
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


def run_ingress(profile: pathlib.Path, profile_sha: str, request: pathlib.Path, report: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return run_cmd([BIN, "--ingress-profile", profile, "--ingress-profile-sha256", profile_sha, "--ingress-request", request, "--ingress-report", report])


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
    if caps["format"] != "anonsync-ledger-backend-capabilities-v33":
        raise AssertionError("capability format is not v33")
    sqlite_caps = caps["backends"]["sqlite-wal"]
    required = [
        "ingress_reservation_command_supported",
        "ingress_profile_digest_pin_required",
        "ingress_request_selects_handle_only",
        "ingress_operator_paths_loaded_from_profile",
        "ingress_request_forbidden_operator_field_rejection_required",
        "ingress_controls_contracts_capability_digest_pins_required",
        "ingress_report_binds_profile_request_and_reserved_outbox",
    ]
    missing = [k for k in required if sqlite_caps.get(k) is not True]
    if missing:
        raise AssertionError(f"missing v33 ingress capability flags: {missing}")
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        if manifest.get("revision_id") != "rev0638":
            raise AssertionError("manifest revision is not rev0638")
        if manifest.get("capability_manifest") != "gateway/rev0638-cpp-ledger-backend-capabilities.json":
            raise AssertionError("manifest does not point at rev0638 capability manifest")


def assert_successful_reservation(tmp: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path, Dict[str, Any]]:
    ledger = tmp / "success.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger)
    request = make_request(tmp)
    report_path = tmp / "success-report.json"
    cp = run_ingress(profile, profile_sha, request, report_path)
    if cp.returncode != 0:
        raise AssertionError(f"ingress reservation failed unexpectedly rc={cp.returncode}\nstdout={cp.stdout}\nstderr={cp.stderr}")
    report = load_report(report_path)
    if report["format"] != "anonsync-ingress-reservation-report-v1" or report["revision_id"] != "rev0638":
        raise AssertionError("ingress report format/revision mismatch")
    if not report["profile"].get("operator_paths_loaded_from_profile"):
        raise AssertionError("profile-bound operator path evidence absent")
    if not report["request"].get("request_selects_handle_only"):
        raise AssertionError("request handle-only evidence absent")
    reservation = report["reservation"]
    if not reservation.get("accepted") or reservation.get("outbox_state") != "reserved":
        raise AssertionError("successful ingress did not return a reserved outbox row")
    if reservation.get("ledger_sequence") != 1 or len(reservation.get("entry_hash", "")) != 64 or len(reservation.get("effect_idempotency_key", "")) != 64:
        raise AssertionError("reservation evidence is incomplete")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("ledger did not persist exactly one reservation")
    return ledger, request, report


def assert_duplicate_rejected(tmp: pathlib.Path, ledger: pathlib.Path, request: pathlib.Path) -> None:
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="dupe")
    # Retarget request to the duplicate profile handle while retaining the same token/effect evidence.
    req = json.loads(request.read_text())
    req["config_handle"] = "dupe"
    req["request_id"] = "validator-duplicate"
    dup_req = tmp / "duplicate.request.json"
    write_json(dup_req, req)
    report = tmp / "duplicate-report.json"
    cp = run_ingress(profile, profile_sha, dup_req, report)
    if cp.returncode == 0:
        raise AssertionError("duplicate ingress replay unexpectedly succeeded")
    body = load_report(report)
    if body.get("reservation", {}).get("accepted"):
        raise AssertionError("duplicate ingress produced a reservation")
    if sqlite_line_count(ledger) != 1:
        raise AssertionError("duplicate ingress changed durable line count")


def assert_fail_before_append(tmp: pathlib.Path, label: str, profile: pathlib.Path, profile_sha: str, request: pathlib.Path, ledger: pathlib.Path, expected_text: str) -> None:
    report = tmp / f"{label}-report.json"
    cp = run_ingress(profile, profile_sha, request, report)
    if cp.returncode == 0:
        raise AssertionError(f"{label} unexpectedly succeeded")
    body = load_report(report)
    reason = body.get("reservation", {}).get("failure_reason", "")
    if expected_text not in reason and expected_text not in cp.stderr and expected_text not in cp.stdout:
        raise AssertionError(f"{label} failure did not mention {expected_text!r}: reason={reason!r} stdout={cp.stdout!r} stderr={cp.stderr!r}")
    if sqlite_line_count(ledger) != 0:
        raise AssertionError(f"{label} appended to ledger before failing")


def assert_failures(tmp: pathlib.Path) -> None:
    # Profile digest pin mismatch.
    ledger = tmp / "bad-profile-sha.sqlite"
    profile, _ = make_profile(tmp, ledger=ledger, handle="badsha")
    req = make_request(tmp, handle="badsha", request_id="badsha")
    assert_fail_before_append(tmp, "bad-profile-sha", profile, "0" * 64, req, ledger, "digest pin mismatch")

    # Disabled handle.
    ledger = tmp / "disabled.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, enabled=False, handle="disabled")
    req = make_request(tmp, handle="disabled", request_id="disabled")
    assert_fail_before_append(tmp, "disabled", profile, profile_sha, req, ledger, "disabled")

    # Duplicate handle.
    ledger = tmp / "duplicate-handle.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, duplicate=True, handle="dup-handle")
    req = make_request(tmp, handle="dup-handle", request_id="dup-handle")
    assert_fail_before_append(tmp, "duplicate-handle", profile, profile_sha, req, ledger, "duplicate handle")

    # Request tries to choose an operator-controlled ledger path.
    ledger = tmp / "operator-field.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="operator-field")
    req = make_request(tmp, handle="operator-field", request_id="operator-field", extra={"ledger_path": str(tmp / "attacker.sqlite")})
    assert_fail_before_append(tmp, "operator-field", profile, profile_sha, req, ledger, "operator field")

    # Request metadata tries to select a failure ledger mode.
    ledger = tmp / "ledger-mode.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, handle="ledger-mode")
    case = first_case()
    case["http_request"]["headers"]["x-anonsync-ledger-mode"] = "split_brain"
    req = make_request(tmp, case=case, handle="ledger-mode", request_id="ledger-mode")
    assert_fail_before_append(tmp, "ledger-mode", profile, profile_sha, req, ledger, "ledger mode")

    # v32 downgrade through the profile's capability pin is rejected by the kernel before append.
    ledger = tmp / "v32-downgrade.sqlite"
    profile, profile_sha = make_profile(tmp, ledger=ledger, caps=OLD_CAPS, handle="downgrade")
    req = make_request(tmp, handle="downgrade", request_id="downgrade")
    assert_fail_before_append(tmp, "downgrade", profile, profile_sha, req, ledger, "v33")


def main() -> None:
    if not BIN.exists():
        raise SystemExit(f"packaged binary missing: {BIN}")
    assert_static_metadata()
    with tempfile.TemporaryDirectory(prefix="anonsync-rev0638-ingress-") as td:
        tmp = pathlib.Path(td)
        ledger, request, report = assert_successful_reservation(tmp)
        assert_duplicate_rejected(tmp, ledger, request)
        assert_failures(tmp)
        audit = {
            "validator": "rev0638-profile-bound-ingress-reservation",
            "binary": str(BIN.relative_to(ROOT)),
            "binary_sha256": sha256_file(BIN),
            "capabilities_sha256": sha256_file(CAPS),
            "successful_report_digest": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest(),
            "checks": [
                "successful profile-bound durable reservation",
                "duplicate replay does not append",
                "profile digest mismatch fails before append",
                "disabled handle fails before append",
                "duplicate handle fails before append",
                "request operator field fails before append",
                "request ledger-mode selection fails before append",
                "v32 capability downgrade fails before append",
            ],
            "result": "passed",
        }
    out = ROOT / "audit" / "rev0638-ingress-reservation-package-validator.json"
    out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
