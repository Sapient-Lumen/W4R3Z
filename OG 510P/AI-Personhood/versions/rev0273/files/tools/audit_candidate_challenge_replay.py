#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T04:42:00Z"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_rel, data_path):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_path} fails {schema_rel}: {errors[0].message}")

with tempfile.TemporaryDirectory(prefix="ai-personhood-candidate-challenge-") as td:
    tmp = Path(td)
    source = tmp / "raw-counterparty-artifact.eml"
    secret = "SYNTHETIC_CANDIDATE_CHALLENGE_PRIVATE_BYTES_REV0214_DO_NOT_PACKAGE"
    source.write_text(secret, encoding="utf-8")
    vault = tmp / "external-vault"
    out = tmp / "public-shell-output"
    pilot_cmd = [
        sys.executable,
        str(ROOT / "tools" / "prepare_first_real_artifact_pilot.py"),
        "--input", str(source),
        "--drop-id", "rev0214-synthetic-candidate-challenge",
        "--output-dir", str(out),
        "--vault-root", str(vault),
        "--created-at", CREATED_AT,
        "--permit-leap-candidate",
        "--request-trace-present",
        "--counterparty-contact-present",
        "--nonhost-retention-present",
        "--sealed-public-parity-present",
        "--counterparty-org-id", "org:synthetic-nonhost-counterparty",
        "--dependency-group-id", "dep:synthetic-independent-request-trace",
    ]
    pilot_proc = subprocess.run(pilot_cmd, check=True, capture_output=True, text=True)
    pilot_report = Path(pilot_proc.stdout.strip())
    challenge_out = tmp / "challenge-output"
    challenge_cmd = [
        sys.executable,
        str(ROOT / "tools" / "prepare_candidate_challenge_packet.py"),
        "--pilot-report", str(pilot_report),
        "--vault-root", str(vault),
        "--output-dir", str(challenge_out),
        "--challenge-id", "rev0214-synthetic-pending",
        "--created-at", CREATED_AT,
    ]
    challenge_proc = subprocess.run(challenge_cmd, check=True, capture_output=True, text=True)
    challenge_path = Path(challenge_proc.stdout.strip())
    validate("schemas/live-artifact-candidate-challenge-report.schema.json", challenge_path)
    report = load(challenge_path)
    if report.get("candidate_state") != "hash-reverified-challenge-pending":
        raise SystemExit("candidate challenge report should be hash-reverified-challenge-pending")
    reread = report.get("vault_reread", {})
    if not (reread.get("vault_reread_performed") and reread.get("hash_reverified") and reread.get("size_reverified") and reread.get("public_shell_bound")):
        raise SystemExit("candidate challenge did not reread and bind private-vault hash/size")
    if reread.get("raw_bytes_disclosed") is not False or secret in json.dumps(report):
        raise SystemExit("candidate challenge report leaked raw private bytes")
    window = report.get("challenge_window", {})
    if not (window.get("counterparty_silence_is_not_waiver") and window.get("challenge_pending_stays_reliance")):
        raise SystemExit("candidate challenge must treat silence as non-waiver and stay reliance")
    locks = report.get("downstream_locks", {})
    for key in ["custody_creation_allowed", "response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
        if locks.get(key) is not False:
            raise SystemExit(f"candidate challenge incorrectly released {key}")
    if report.get("decision", {}).get("custody_release_allowed") is not False or report.get("decision", {}).get("reliance_effect") != "stayed":
        raise SystemExit("candidate challenge must not release custody or reliance")
    forbidden_names = ["counterparty-artifact-custody-record", "external-receipt-response-record", "external-receipt-intake-record", "actual-receipt-import-gate"]
    generated_names = "\n".join(p.name for p in challenge_out.glob("*.json"))
    if any(name in generated_names for name in forbidden_names):
        raise SystemExit("candidate challenge generated downstream object")

    # Corrupt private vault bytes after pilot staging; challenge report must block rather than fail open.
    vault_files = list(vault.glob("*.eml"))
    if len(vault_files) != 1:
        raise SystemExit("expected one synthetic private vault artifact")
    vault_files[0].write_text("CORRUPTED_" + secret, encoding="utf-8")
    mismatch_out = tmp / "mismatch-output"
    mismatch_cmd = [
        sys.executable,
        str(ROOT / "tools" / "prepare_candidate_challenge_packet.py"),
        "--pilot-report", str(pilot_report),
        "--vault-root", str(vault),
        "--output-dir", str(mismatch_out),
        "--challenge-id", "rev0214-synthetic-mismatch",
        "--created-at", CREATED_AT,
    ]
    mismatch_proc = subprocess.run(mismatch_cmd, check=True, capture_output=True, text=True)
    mismatch_report = load(Path(mismatch_proc.stdout.strip()))
    validate("schemas/live-artifact-candidate-challenge-report.schema.json", Path(mismatch_proc.stdout.strip()))
    if mismatch_report.get("candidate_state") != "blocked-vault-hash-mismatch":
        raise SystemExit("hash mismatch must emit blocked-vault-hash-mismatch")
    if mismatch_report.get("decision", {}).get("custody_review_may_continue") is not False:
        raise SystemExit("hash mismatch must block custody review continuation")
    if mismatch_report.get("downstream_locks", {}).get("live_floor_delta_allowed") is not False:
        raise SystemExit("hash mismatch must block live-floor delta")

# Validate checked-in current example and negative fixtures.
current_example = ROOT / "examples" / f"live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json"
validate("schemas/live-artifact-candidate-challenge-report.schema.json", current_example)
example = load(current_example)
if example.get("candidate_state") != "hash-reverified-challenge-pending":
    raise SystemExit("checked-in candidate challenge example should be pending, not admitted")
if example.get("downstream_locks", {}).get("custody_creation_allowed") is not False:
    raise SystemExit("checked-in candidate challenge example releases custody")

required_fixtures = {
    "NF-CUSTODY-2026-0007": "fixtures/negative-tests/candidate-challenge-hash-trust-without-vault-read.json",
    "NF-DISCLOSURE-2026-0003": "fixtures/negative-tests/candidate-challenge-releases-custody-while-pending.json",
}
for fid, rel in required_fixtures.items():
    fixture = load(rel)
    if fixture.get("fixture_id") != fid:
        raise SystemExit(f"fixture id mismatch for {rel}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit("fixture suite missing candidate challenge fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing candidate challenge fixtures")

leap_text = (ROOT / "tools" / "prepare_first_real_artifact_pilot.py").read_text(encoding="utf-8")
for phrase in ["prepare_candidate_challenge_packet.py", "candidate challenge/replay", "LEAP candidate state is not custody"]:
    if phrase not in leap_text:
        raise SystemExit(f"pilot tool missing downstream challenge phrase: {phrase}")

print("audit_candidate_challenge_replay: OK")
