#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T16:58:00Z"

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

with tempfile.TemporaryDirectory(prefix="ai-personhood-first-artifact-pilot-") as td:
    tmp = Path(td)
    source = tmp / "raw-counterparty-artifact.eml"
    secret = "SYNTHETIC_FIRST_REAL_ARTIFACT_PRIVATE_BYTES_REV0213_DO_NOT_PACKAGE"
    source.write_text(secret, encoding="utf-8")
    vault = tmp / "external-vault"
    out = tmp / "public-shell-output"
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "prepare_first_real_artifact_pilot.py"),
        "--input", str(source),
        "--drop-id", "rev0233-synthetic-first-real-artifact-pilot",
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
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    report_path = Path(proc.stdout.strip())
    report = load(report_path)
    validate("schemas/first-real-artifact-pilot-report.schema.json", report_path)
    if report.get("revision") != REV or report.get("no_live_floor_effect") is not True:
        raise SystemExit("pilot report revision/no-live-floor guard mismatch")
    if report.get("leap_candidate_state") != "candidate-artifact-received-no-downstream-release":
        raise SystemExit("pilot report did not describe candidate LEAP without downstream release")
    if any("response-record" in s or "intake-record" in s for s in report.get("generated_public_paths", {}).values() if isinstance(s, str)):
        raise SystemExit("pilot report generated paths appear to include downstream response/intake artifacts")
    paths = report["generated_public_paths"]
    ledger_path = Path(paths["evidence_drop_ledger"])
    shell_path = Path(paths["evidence_vault_public_shell"])
    leap_path = Path(paths["live_evidence_acquisition_packet"])
    for schema, path in [
        ("schemas/live-evidence-drop-ledger.schema.json", ledger_path),
        ("schemas/evidence-vault-public-shell.schema.json", shell_path),
        ("schemas/live-evidence-acquisition-packet.schema.json", leap_path),
    ]:
        validate(schema, path)
    ledger = load(ledger_path)
    shell = load(shell_path)
    leap = load(leap_path)
    if ledger.get("intake_mode") != "live-candidate-drop":
        raise SystemExit("pilot did not stage a live-candidate-drop")
    if not ledger.get("staged_payload", {}).get("quarantine_locator", "").startswith("private-vault://"):
        raise SystemExit("pilot ledger did not use private-vault locator")
    if not ledger.get("source_payload", {}).get("original_locator", "").startswith("private-source-redacted:sha256:"):
        raise SystemExit("pilot ledger leaked original source locator")
    if shell.get("hash_commitments", {}).get("raw_sha256") != ledger.get("staged_payload", {}).get("quarantine_sha256"):
        raise SystemExit("pilot shell hash does not match ledger")
    if leap.get("state") != "candidate-artifact-received":
        raise SystemExit("pilot did not emit candidate LEAP state")
    if leap.get("source_evidence_drop_ledger_ref") != ledger.get("ledger_id"):
        raise SystemExit("pilot LEAP not bound to evidence-drop ledger")
    locks = leap.get("downstream_locks", {})
    for key in ["response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
        if locks.get(key) is not False:
            raise SystemExit(f"pilot LEAP incorrectly released {key}")
    forbidden_names = ["counterparty-artifact-custody-record", "external-receipt-response-record", "external-receipt-intake-record", "actual-receipt-import-gate"]
    generated_names = "\n".join(p.name for p in out.glob("*.json"))
    if any(name in generated_names for name in forbidden_names):
        raise SystemExit("pilot generated downstream object")
    public_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in out.glob("*.json"))
    if secret in public_text:
        raise SystemExit("pilot leaked raw secret into public output")
    copied = list(vault.rglob("*.eml"))
    if len(copied) != 1 or copied[0].read_text(encoding="utf-8") != secret:
        raise SystemExit("pilot did not copy raw bytes to external vault")

    # Without explicit candidate permission, the same raw staging may produce shell/report only.
    out2 = tmp / "public-shell-only-output"
    cmd2 = [
        sys.executable,
        str(ROOT / "tools" / "prepare_first_real_artifact_pilot.py"),
        "--input", str(source),
        "--drop-id", "rev0233-synthetic-first-real-artifact-shell-only",
        "--output-dir", str(out2),
        "--vault-root", str(vault / "second"),
        "--created-at", CREATED_AT,
    ]
    proc2 = subprocess.run(cmd2, check=True, capture_output=True, text=True)
    report2_path = Path(proc2.stdout.strip())
    report2 = load(report2_path)
    validate("schemas/first-real-artifact-pilot-report.schema.json", report2_path)
    if report2.get("leap_candidate_state") != "not-emitted":
        raise SystemExit("shell-only pilot report must say LEAP was not emitted")
    if report2["generated_public_paths"].get("live_evidence_acquisition_packet") is not None:
        raise SystemExit("shell-only pilot unexpectedly emitted LEAP")
    if any("live-evidence-acquisition-packet" in p.name for p in out2.glob("*.json")):
        raise SystemExit("shell-only output contains LEAP packet")

print("audit_first_real_artifact_pilot: OK")
