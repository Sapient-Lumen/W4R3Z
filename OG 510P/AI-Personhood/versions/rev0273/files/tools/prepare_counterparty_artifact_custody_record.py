#!/usr/bin/env python3
"""Prepare a counterparty artifact custody record from an eligible custody gate.

This tool is deliberately response-only. A valid live-candidate custody record may
permit preparation of an external-receipt-response-record, but it must not permit
intake, import, or live-floor credit. Blocked gates emit quarantined custody
records so a failed path can be documented without creating fake progress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T19:06:00Z"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out).strip(".-_:") or "custody-record"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_json_ref(ref: Optional[str], base: Path) -> Optional[Path]:
    if not ref or not isinstance(ref, str):
        return None
    p = Path(ref)
    if p.is_absolute():
        return p
    candidate = (base / p).resolve()
    if candidate.exists():
        return candidate
    candidate = (ROOT / p).resolve()
    if candidate.exists():
        return candidate
    return None


def candidate_vault_paths(locator: Optional[str], vault_root: Path) -> list[Path]:
    if not locator or not isinstance(locator, str):
        return []
    name = locator.rsplit("/", 1)[-1]
    return [
        vault_root / name,
        vault_root / REV / "live-evidence-drops" / name,
        vault_root / "live-evidence-drops" / name,
    ]


def first_existing(paths: list[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists() and p.is_file() and not p.is_symlink():
            return p.resolve()
    return None


def bool_gate(gate: dict, path: list[str], value: bool) -> bool:
    cur = gate
    for key in path:
        if not isinstance(cur, dict):
            return False
        cur = cur.get(key)
    return cur is value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody-gate", required=True)
    parser.add_argument("--vault-root", required=True, help="External private vault root. Must remain outside the release tree.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--custody-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--linked-request-packet", default="not-yet-created:external-receipt-request-packet")
    parser.add_argument("--linked-import-attempt", default="not-yet-created:live-counterparty-import-attempt")
    parser.add_argument("--linked-live-drill-packet", default="LDEP-2026-cross-critical-host-exit-witness-pack")
    parser.add_argument("--linked-artifact-envelope", default="not-yet-created:nonhost-response-artifact-envelope")
    parser.add_argument("--artifact-type", choices=["raw-email", "signed-response", "text-file", "screenshot", "api-payload", "timestamp", "public-redaction", "sealed-copy", "other"], default="raw-email")
    parser.add_argument("--mime-type", default="message/rfc822")
    args = parser.parse_args()

    gate_path = Path(args.custody_gate).expanduser().resolve()
    gate = load_json(gate_path)
    challenge_path = resolve_json_ref(gate.get("linked_candidate_challenge_report_ref"), gate_path.parent)
    challenge = load_json(challenge_path) if challenge_path and challenge_path.exists() else {}
    reread = challenge.get("vault_reread", {})
    locator = reread.get("private_vault_locator") or "private-vault://missing"
    expected_hash = reread.get("expected_sha256") or reread.get("recomputed_sha256") or ("0" * 64)
    expected_size = reread.get("expected_size_bytes") if reread.get("expected_size_bytes") is not None else reread.get("recomputed_size_bytes")
    if expected_size is None:
        expected_size = 0

    vault_root = Path(args.vault_root).expanduser().resolve()
    vault_path = first_existing(candidate_vault_paths(locator, vault_root))
    reread_ok = False
    recomputed_hash = None
    recomputed_size = None
    if vault_path:
        recomputed_hash = sha256(vault_path)
        recomputed_size = vault_path.stat().st_size
        reread_ok = (recomputed_hash == expected_hash and int(recomputed_size) == int(expected_size))

    gate_eligible = (
        gate.get("gate_state") == "eligible-for-custody-record"
        and bool_gate(gate, ["downstream_locks", "may_prepare_counterparty_artifact_custody_record"], True)
        and bool_gate(gate, ["decision", "custody_record_may_be_prepared"], True)
        and bool_gate(gate, ["downstream_locks", "response_creation_allowed"], False)
        and bool_gate(gate, ["downstream_locks", "intake_creation_allowed"], False)
        and bool_gate(gate, ["downstream_locks", "import_gate_creation_allowed"], False)
        and bool_gate(gate, ["downstream_locks", "live_floor_delta_allowed"], False)
        and gate.get("no_live_floor_effect") is True
        and gate.get("authority_evidence_binder", {}).get("may_feed_custody_authority_gate") is True
        and gate.get("authority_evidence_binder", {}).get("authority_evidence_complete") is True
    )

    eligible_for_response = gate_eligible and reread_ok
    blocked_reasons = []
    if not gate_eligible:
        blocked_reasons.append(f"custody gate is {gate.get('gate_state')} rather than eligible-for-custody-record with an evidence-backed authority binder")
    if not reread_ok:
        blocked_reasons.append("private-vault reread failed or hash/size did not match the challenge report")
    if challenge.get("candidate_state") != "hash-reverified-challenge-pending":
        blocked_reasons.append("linked candidate challenge is not hash-reverified")
    if gate.get("candidate_challenge", {}).get("challenge_status") not in {"closed-rejected", "closed-no-objection"}:
        blocked_reasons.append("challenge status is not resolved in a custody-eligible posture")

    slug = safe_slug(args.custody_id)
    artifact_state = "live-candidate-artifact" if eligible_for_response else "quarantined"
    admission = "admitted-for-live-import-review" if eligible_for_response else "quarantined"
    authority = gate.get("class_authority", {})
    receipt_class = authority.get("receipt_class", "result-return")
    dependency_group = authority.get("dependency_group_id") or "unknown-dependency-group"
    out = {
        "custody_record_id": f"CACR-2026-{slug}",
        "schema_version": "counterparty-artifact-custody-record-v0.1",
        "created_at": args.created_at,
        "linked_request_packet": args.linked_request_packet,
        "linked_import_attempt": args.linked_import_attempt,
        "linked_live_drill_packet": args.linked_live_drill_packet,
        "linked_artifact_envelope": args.linked_artifact_envelope,
        "linked_custody_gate_ref": gate.get("custody_gate_id", str(gate_path)),
        "artifact_state": artifact_state,
        "receipt_class": receipt_class,
        "counterparty_authority": {
            "role": "counterparty artifact custody reviewer",
            "identity_ref": authority.get("counterparty_org_id") or "unknown-counterparty-org",
            "external_to_host": True,
            "dependency_group": dependency_group,
            "authority_basis": authority.get("authority_basis", "not supplied"),
            "authority_limitations": authority.get("authority_limitations") or ["authority limitations not supplied; custody quarantined"],
            "authority_verified": bool(eligible_for_response and authority.get("authority_verified") is True),
            "class_scope": [receipt_class] if receipt_class else ["result-return"],
        },
        "raw_artifacts": [
            {
                "artifact_id": "CACR-A-001",
                "artifact_type": args.artifact_type,
                "path_or_locator": locator,
                "sha256": expected_hash,
                "size_bytes": int(expected_size),
                "mime_type": args.mime_type,
                "collection_context": "live-counterparty" if eligible_for_response else "unknown",
                "raw_available": bool(vault_path),
                "sealed": True,
                "public_redaction_ref": challenge.get("linked_refs", {}).get("public_shell_id") or "public-shell:pending",
                "may_be_used_for_live_import": False,
            }
        ],
        "collection_chain": [
            {
                "event_id": "CACR-EV-001",
                "event_type": "authority-checked",
                "at": args.created_at,
                "actor": "custody-authority-gate",
                "system_boundary": "neutral-infrastructure",
                "evidence_ref": gate.get("custody_gate_id", str(gate_path)),
                "can_satisfy_live_receipt": False,
            },
            {
                "event_id": "CACR-EV-002",
                "event_type": "sealed-copy-stored",
                "at": args.created_at,
                "actor": "private-vault-reread",
                "system_boundary": "sealed-channel",
                "evidence_ref": locator,
                "can_satisfy_live_receipt": False,
            },
            {
                "event_id": "CACR-EV-003",
                "event_type": "hash-recorded",
                "at": args.created_at,
                "actor": "custody-record-preparer",
                "system_boundary": "host",
                "evidence_ref": "sha256:" + expected_hash,
                "can_satisfy_live_receipt": False,
            },
            {
                "event_id": "CACR-EV-004",
                "event_type": "dependency-checked",
                "at": args.created_at,
                "actor": "custody-authority-gate",
                "system_boundary": "neutral-infrastructure",
                "evidence_ref": dependency_group,
                "can_satisfy_live_receipt": False,
            },
        ],
        "integrity_checks": {
            "raw_artifact_available": bool(vault_path),
            "sha256_verified": bool(reread_ok),
            "locator_resolvable": bool(vault_path),
            "timestamp_independent": bool(gate.get("custody_prerequisites", {}).get("independent_timestamp_bound")),
            "identity_authority_checked": bool(gate.get("custody_prerequisites", {}).get("subject_or_representative_authority_verified")),
            "dependency_group_checked": bool(gate.get("custody_prerequisites", {}).get("dependency_group_independence_checked")),
            "nonhost_storage_confirmed": bool(gate.get("custody_prerequisites", {}).get("nonhost_retention_confirmed")),
            "sealed_public_parity_checked": bool(gate.get("custody_prerequisites", {}).get("sealed_public_parity_confirmed")),
            "redaction_not_substituted_for_raw": bool(gate.get("custody_prerequisites", {}).get("redaction_boundary_confirmed")),
        },
        "redaction_and_subject_access": {
            "sealed_material_present": True,
            "public_shell_ref": challenge.get("linked_refs", {}).get("public_shell_id") or "public-shell:pending",
            "subject_readable_summary_required": True,
            "privacy_controls": [
                "do not disclose private-vault filesystem path",
                "do not disclose raw bytes in public release",
                "publish only hash/size/redaction boundary commitments until subject access is approved",
            ],
            "prohibited_inferences": [
                "custody record proves response content",
                "custody record creates intake/import/live-floor credit",
                "private-vault locator discloses source path",
                "class authority extends beyond the scoped receipt class",
            ],
        },
        "import_readiness": {
            "may_create_response_record": bool(eligible_for_response),
            "may_create_intake_record": False,
            "may_run_import_gate": False,
            "live_import_floor_delta": 0,
            "disqualification_reasons": blocked_reasons if blocked_reasons else [
                "custody permits response preparation only",
                "no external-receipt-response-record has been created",
                "no external-receipt-intake-record has accepted a response",
                "no actual-receipt-import-gate or verified live adapter has passed",
            ],
            "next_gate": "external-receipt-response-record may be prepared only from this custody record; intake, import, and computed floor remain separate later gates",
        },
        "decision": {
            "live_reliance_effect": "stayed",
            "custody_admission": admission,
            "reason": "Custody is a response-preparation gate, not an intake/import/floor gate." if eligible_for_response else "; ".join(blocked_reasons),
            "blocked_actions": [
                "external-receipt-intake-record creation from custody alone",
                "actual-receipt-import-gate creation from custody alone",
                "computed live receipt floor increment",
                "treating may_create_response_record as intake or import authorization",
            ],
            "next_actions": [
                "prepare an external-receipt-response-record only if custody_admission is admitted-for-live-import-review",
                "keep subject-readable summary and redaction boundary active",
                "run response reconciliation before intake conversion",
                "rerun admission graph and invariant report before any later import gate",
            ],
        },
    }

    out_path = Path(args.output_dir).expanduser().resolve() / f"counterparty-artifact-custody-record-{slug}.json"
    write_json(out_path, out)
    print(out_path)


if __name__ == "__main__":
    main()
