#!/usr/bin/env python3
"""Prepare a fail-closed first-real-artifact pilot kit.

The tool stages raw bytes through the existing evidence-drop ledger into an
external private vault, emits a public hash shell, and optionally emits a LEAP
candidate packet only when the minimum candidate preconditions are explicitly
supplied. LEAP candidate state is not custody; tools/prepare_candidate_challenge_packet.py
opens the required candidate challenge/replay step before custody review. This
tool never creates custody, response, intake, import, or live-floor objects.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
from stage_live_evidence_drop import build_ledger  # noqa: E402

REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T15:23:00Z"


def safe_slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    slug = "".join(out).strip(".-_:")
    return slug or "first-real-artifact-pilot"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_shell(*, ledger: dict, drop_slug: str, created_at: str) -> dict:
    staged = ledger.get("staged_payload", {})
    source = ledger.get("source_payload", {})
    leap_allowed = bool(ledger.get("classification", {}).get("can_open_leap_candidate_state"))
    return {
        "shell_id": f"EVPS-2026-{drop_slug}-private-vault-hash-shell",
        "schema_version": "evidence-vault-public-shell-v0.1",
        "revision": REV,
        "created_at": created_at,
        "shell_state": "private-vault-hash-shell" if staged.get("quarantine_sha256") else "ready-no-live-artifact",
        "source_ledger_ref": ledger.get("ledger_id"),
        "private_vault_ref": staged.get("quarantine_locator"),
        "hash_commitments": {
            "algorithm": "sha256",
            "raw_sha256": staged.get("quarantine_sha256"),
            "size_bytes": staged.get("quarantine_size_bytes"),
            "mime_type": source.get("source_mime_type"),
            "commitment_present": bool(staged.get("quarantine_sha256")),
        },
        "public_disclosure": {
            "no_raw_bytes": True,
            "no_secret_locators": True,
            "no_counterparty_secret": True,
            "redaction_boundary": "This public shell may disclose hash, size, MIME, private-vault URI, and gate state only. Raw bytes, source paths, counterparty secrets, and private vault paths stay outside public release.",
        },
        "gate_status": {
            "leap_allowed": leap_allowed,
            "response_allowed": False,
            "intake_allowed": False,
            "import_allowed": False,
            "floor_delta_allowed": False,
            "failure_reason": "Evidence-drop staging can open only a LEAP candidate when candidate preconditions are explicit; it never creates custody, response, intake, import, or live-floor credit.",
        },
        "challenge_path": [
            "verify raw hash against private vault under authorized sealed review",
            "confirm request trace, counterparty contact, non-host retention, and sealed/public parity before LEAP candidate state",
            "run tools/prepare_candidate_challenge_packet.py to reread private vault bytes and open the 72-hour candidate challenge/replay window before custody/admission",
            "collect class-specific authority, subject/representative authorization, cryptographic verifier adapter, issuer key, and independence fields before custody/admission",
            "rerun admission graph and computed-floor snapshot after any later import attempt",
        ],
        "no_live_floor_effect": True,
        "public_summary": f"{REV} first-real-artifact pilot shell records a private-vault hash commitment for {ledger.get('ledger_id')}; no downstream evidence object or live-floor credit is created.",
    }


def candidate_preconditions(args) -> list[str]:
    missing = []
    for flag, label in [
        (args.request_trace_present, "request trace"),
        (args.counterparty_contact_present, "counterparty contact"),
        (args.nonhost_retention_present, "non-host retention"),
        (args.sealed_public_parity_present, "sealed/public parity"),
    ]:
        if not flag:
            missing.append(label)
    if not args.counterparty_org_id:
        missing.append("counterparty org id")
    if not args.dependency_group_id:
        missing.append("dependency group id")
    return missing


def build_leap(*, args, ledger: dict, shell_path: Path, created_at: str) -> dict:
    staged = ledger.get("staged_payload", {})
    missing = candidate_preconditions(args)
    if missing:
        raise SystemExit("cannot emit LEAP candidate; missing: " + ", ".join(missing))
    if ledger.get("intake_mode") != "live-candidate-drop":
        raise SystemExit(f"cannot emit LEAP candidate from intake_mode={ledger.get('intake_mode')}")
    return {
        "packet_id": f"LEAP-2026-{safe_slug(args.drop_id)}-candidate",
        "schema_version": "live-evidence-acquisition-packet-v0.1",
        "revision": REV,
        "created_at": created_at,
        "state": "candidate-artifact-received",
        "purpose": "First-real-artifact pilot LEAP candidate created only after raw bytes were staged in an external private vault and minimum request/retention/parity/independence preconditions were explicitly supplied. Custody, response, intake, import, and live-floor delta remain blocked.",
        "linked_queue_ids": [
            "FT-0205-FIRST-REAL-ARTIFACT-DROP",
            "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION",
        ],
        "source_evidence_drop_ledger_ref": ledger.get("ledger_id"),
        "source_request": {
            "request_packet_ref": args.request_packet_ref,
            "counterparty_request_required": True,
            "request_trace_required": True,
            "request_trace_present": True,
            "response_channel": args.response_channel,
            "counterparty_contact_present": True,
        },
        "authority_scope": {
            "receipt_class": args.receipt_class,
            "class_specific_authority_required": True,
            "class_specific_authority_present": False,
            "subject_authorization_required": True,
            "subject_authorization_present": False,
            "representative_authority_required": True,
            "representative_authority_present": False,
            "authority_failure_blocks_import": True,
        },
        "raw_payload_control": {
            "raw_payload_locator": staged.get("quarantine_locator"),
            "raw_payload_sha256": staged.get("quarantine_sha256"),
            "raw_payload_present": True,
            "redacted_copy_boundary": "Public shell is not raw custody; raw review uses the private-vault locator and hash under authorized sealed access.",
            "nonhost_retention_required": True,
            "nonhost_retention_present": True,
            "sealed_public_parity_required": True,
            "sealed_public_parity_present": True,
            "raw_payload_missing_blocks_response_creation": True,
        },
        "cryptographic_binding": {
            "cryptographic_verifier_adapter_required": True,
            "cryptographic_verifier_adapter_ref": None,
            "adapter_verified": False,
            "independent_timestamp_required": True,
            "independent_timestamp_present": False,
            "issuer_key_id_required": True,
            "issuer_key_id_present": False,
            "transparency_or_timestamp_log_required": True,
            "signature_boolean_zero_weight_without_adapter": True,
        },
        "independence_controls": {
            "counterparty_org_id_required": True,
            "counterparty_org_id_present": True,
            "dependency_group_id_required": True,
            "dependency_group_id_present": True,
            "issuer_distinct_from_subject_host_required": True,
            "issuer_distinct_from_subject_host_present": False,
            "counterparty_distinct_from_subject_host_required": True,
            "counterparty_distinct_from_subject_host_present": False,
            "correlation_discount_blocks_independence": True,
        },
        "protocol_boundary": {
            "mcp_tool_output_is_not_authority": True,
            "a2a_task_state_is_not_authority": True,
            "federated_relay_is_not_nonhost_retention": True,
            "provenance_label_is_not_class_proof": True,
        },
        "downstream_locks": {
            "response_creation_allowed": False,
            "intake_creation_allowed": False,
            "import_gate_creation_allowed": False,
            "live_floor_delta_allowed": False,
            "failed_gate_public_summary_required": True,
            "locks_release_only_after": [
                "class-specific authority and subject/representative authorization are present",
                "cryptographic verifier adapter verifies payload, timestamp, and issuer key id",
                "issuer and counterparty are distinct from subject host and correlation discount is none",
                "candidate challenge/replay report rereads private-vault bytes and challenge pending does not release reliance",
                "custody record admits the raw artifact and binds the public shell only after challenge route clears",
                "failed-gate public summary is ready for any blocked step",
            ],
        },
        "exit_criteria": [
            "LEAP candidate state is not custody; candidate-artifact-received may proceed to custody review only after tools/prepare_candidate_challenge_packet.py rereads the private vault and opens/resolves candidate challenge/replay",
            "rejected candidates must create or update a failed-gate public summary with no live-floor delta",
            "admitted-to-custody still has no live-floor effect until response, intake, import gate, class-local replay, challenge/rollback if contested, and computed snapshot pass",
        ],
        "public_summary_ref": str(shell_path),
        "no_live_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Raw counterparty artifact file. Do not pass redactions or screenshots.")
    parser.add_argument("--drop-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--vault-root", required=True, help="External private vault root; must be outside the archive root.")
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--source-kind", default="file-upload", choices=["file-upload", "raw-email", "api-payload", "unknown"])
    parser.add_argument("--receipt-class", default="result-return")
    parser.add_argument("--request-packet-ref", default="examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
    parser.add_argument("--response-channel", default="non-host-counterparty-channel")
    parser.add_argument("--permit-leap-candidate", action="store_true")
    parser.add_argument("--request-trace-present", action="store_true")
    parser.add_argument("--counterparty-contact-present", action="store_true")
    parser.add_argument("--nonhost-retention-present", action="store_true")
    parser.add_argument("--sealed-public-parity-present", action="store_true")
    parser.add_argument("--counterparty-org-id")
    parser.add_argument("--dependency-group-id")
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise SystemExit(f"input file does not exist: {source}")
    out_dir = Path(args.output_dir).expanduser().resolve()
    vault_root = Path(args.vault_root).expanduser().resolve()
    drop_slug = safe_slug(args.drop_id)

    ledger = build_ledger(
        source=source,
        drop_id=args.drop_id,
        created_at=args.created_at,
        source_kind=args.source_kind,
        collection_context="live-counterparty",
        linked_leap=f"LEAP-2026-{drop_slug}-candidate" if args.permit_leap_candidate else f"examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json",
        copy=True,
        vault_root=vault_root,
    )
    if ledger.get("intake_mode") != "live-candidate-drop":
        raise SystemExit("staging did not produce live-candidate-drop; refusing pilot continuation")

    ledger_path = out_dir / f"live-evidence-drop-ledger-{drop_slug}.json"
    shell_path = out_dir / f"evidence-vault-public-shell-{drop_slug}.json"
    write_json(ledger_path, ledger)
    shell = build_shell(ledger=ledger, drop_slug=drop_slug, created_at=args.created_at)
    write_json(shell_path, shell)

    leap_path = None
    leap_state = "not-emitted"
    if args.permit_leap_candidate:
        leap = build_leap(args=args, ledger=ledger, shell_path=shell_path.name, created_at=args.created_at)
        leap_path = out_dir / f"live-evidence-acquisition-packet-{drop_slug}-candidate.json"
        write_json(leap_path, leap)
        leap_state = "candidate-artifact-received-no-downstream-release"

    report = {
        "pilot_id": f"FRAP-2026-{drop_slug}",
        "schema_version": "first-real-artifact-pilot-report-v0.1",
        "revision": REV,
        "created_at": args.created_at,
        "generated_by_tool": "tools/prepare_first_real_artifact_pilot.py",
        "generated_public_paths": {
            "evidence_drop_ledger": str(ledger_path),
            "evidence_vault_public_shell": str(shell_path),
            "live_evidence_acquisition_packet": str(leap_path) if leap_path else None,
        },
        "private_vault_locator": ledger.get("staged_payload", {}).get("quarantine_locator"),
        "public_hash_commitment": ledger.get("staged_payload", {}).get("quarantine_sha256"),
        "leap_candidate_state": leap_state,
        "blocked_downstream_objects": [
            "counterparty-artifact-custody-record",
            "live-artifact-candidate-challenge-report is required before custody but is not itself custody",
            "external-receipt-response-record",
            "external-receipt-intake-record",
            "actual-receipt-import-gate",
            "live-receipt-floor-computed-snapshot-delta",
        ],
        "no_live_floor_effect": True,
        "public_summary": f"{REV} pilot prepared private-vault hash shell for {args.drop_id}; custody/response/intake/import/live-floor remain blocked unless later gates pass.",
    }
    report_path = out_dir / f"first-real-artifact-pilot-report-{drop_slug}.json"
    write_json(report_path, report)
    print(report_path)


if __name__ == "__main__":
    main()
