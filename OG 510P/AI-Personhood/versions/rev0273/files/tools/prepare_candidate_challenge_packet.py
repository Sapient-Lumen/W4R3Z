#!/usr/bin/env python3
"""Prepare a pre-custody challenge/replay report for a first-artifact pilot.

This tool consumes a pilot report emitted by prepare_first_real_artifact_pilot.py,
rereads the external private vault bytes, recomputes hash/size, and writes a
public challenge report. The report is deliberately not custody, response,
intake, import, or live-floor evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T04:42:00Z"


def safe_slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    slug = "".join(out).strip(".-_:")
    return slug or "candidate-challenge"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def resolve_ref(ref: Optional[str], base: Path) -> Optional[Path]:
    if not ref:
        return None
    p = Path(ref)
    if p.is_absolute():
        return p
    # Pilot reports generated in temp dirs tend to carry absolute paths, but if
    # a caller has made a portable report, first resolve relative to the report
    # directory and then to the archive root.
    candidate = (base / p).resolve()
    if candidate.exists():
        return candidate
    return (ROOT / p).resolve()


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-report", required=True)
    parser.add_argument("--vault-root", required=True, help="External private vault root used for the pilot. Do not put this inside the archive release tree.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--challenge-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--challenge-duration-hours", type=int, default=72)
    args = parser.parse_args()

    pilot_report_path = Path(args.pilot_report).expanduser().resolve()
    pilot = load_json(pilot_report_path)
    base = pilot_report_path.parent
    paths = pilot.get("generated_public_paths", {})
    ledger_path = resolve_ref(paths.get("evidence_drop_ledger"), base)
    shell_path = resolve_ref(paths.get("evidence_vault_public_shell"), base)
    leap_path = resolve_ref(paths.get("live_evidence_acquisition_packet"), base)

    ledger = load_json(ledger_path) if ledger_path and ledger_path.exists() else {}
    shell = load_json(shell_path) if shell_path and shell_path.exists() else {}
    leap = load_json(leap_path) if leap_path and leap_path.exists() else {}

    staged = ledger.get("staged_payload", {})
    commitments = shell.get("hash_commitments", {})
    locator = staged.get("quarantine_locator") or pilot.get("private_vault_locator")
    expected_hash = commitments.get("raw_sha256") or staged.get("quarantine_sha256") or pilot.get("public_hash_commitment")
    expected_size = commitments.get("size_bytes") if commitments.get("size_bytes") is not None else staged.get("quarantine_size_bytes")
    vault_root = Path(args.vault_root).expanduser().resolve()
    vault_path = first_existing(candidate_vault_paths(locator, vault_root))

    reread_performed = vault_path is not None
    recomputed_hash = sha256(vault_path) if vault_path else None
    recomputed_size = vault_path.stat().st_size if vault_path else None
    hash_ok = bool(expected_hash and recomputed_hash and expected_hash == recomputed_hash)
    size_ok = bool(expected_size is not None and recomputed_size is not None and int(expected_size) == int(recomputed_size))
    shell_bound = bool(shell.get("source_ledger_ref") == ledger.get("ledger_id") and commitments.get("raw_sha256") == staged.get("quarantine_sha256"))
    has_leap = bool(leap and leap.get("state") == "candidate-artifact-received")

    if not has_leap:
        state = "blocked-no-leap-candidate"
    elif not reread_performed:
        state = "blocked-vault-unreadable"
    elif not (hash_ok and size_ok and shell_bound):
        state = "blocked-vault-hash-mismatch"
    else:
        state = "hash-reverified-challenge-pending"

    out_dir = Path(args.output_dir).expanduser().resolve()
    slug = safe_slug(args.challenge_id)
    report_path = out_dir / f"live-artifact-candidate-challenge-report-{slug}.json"
    custody_review_may_continue = state == "hash-reverified-challenge-pending"
    report = {
        "challenge_report_id": f"LACR-2026-{slug}",
        "schema_version": "live-artifact-candidate-challenge-report-v0.1",
        "revision": REV,
        "created_at": args.created_at,
        "generated_by_tool": "tools/prepare_candidate_challenge_packet.py",
        "source_pilot_report_ref": str(pilot_report_path),
        "candidate_state": state,
        "linked_refs": {
            "evidence_drop_ledger_ref": str(ledger_path) if ledger_path else None,
            "public_shell_ref": str(shell_path) if shell_path else None,
            "live_evidence_acquisition_packet_ref": str(leap_path) if leap_path else None,
            "source_evidence_drop_ledger_id": ledger.get("ledger_id"),
            "public_shell_id": shell.get("shell_id"),
            "leap_packet_id": leap.get("packet_id"),
        },
        "vault_reread": {
            "private_vault_locator": locator,
            "vault_reread_performed": reread_performed,
            "vault_path_disclosed": False,
            "expected_sha256": expected_hash,
            "recomputed_sha256": recomputed_hash,
            "expected_size_bytes": expected_size,
            "recomputed_size_bytes": recomputed_size,
            "hash_reverified": hash_ok,
            "size_reverified": size_ok,
            "public_shell_bound": shell_bound,
            "raw_bytes_disclosed": False,
        },
        "challenge_window": {
            "status": "open" if custody_review_may_continue else "blocked",
            "duration_hours": args.challenge_duration_hours,
            "opened_at": args.created_at,
            "manual_counterparty_contact_required": True,
            "counterparty_silence_is_not_waiver": True,
            "challenge_pending_stays_reliance": True,
            "challenge_routes": [
                "counterparty identity and contact confirmation",
                "request trace and response-channel confirmation",
                "subject or representative authority challenge",
                "sealed/public parity and redaction-boundary challenge",
                "host-correlation and dependency-group challenge",
            ],
            "prohibited_inferences": [
                "hash shell proves custody",
                "vault reread proves receipt class authority",
                "counterparty silence waives challenge",
                "challenge pending permits response, intake, import, or live-floor credit",
            ],
        },
        "downstream_locks": {
            "custody_creation_allowed": False,
            "response_creation_allowed": False,
            "intake_creation_allowed": False,
            "import_gate_creation_allowed": False,
            "live_floor_delta_allowed": False,
            "locks_release_only_after": [
                "candidate challenge window is resolved without upheld challenge",
                "class-specific authority and subject/representative authority pass",
                "cryptographic verifier adapter, issuer key, and independent timestamp/log pass",
                "custody handoff object binds raw private-vault hash without leaking source path",
                "later response, intake, import, class-local replay, and computed-floor gates pass independently",
            ],
        },
        "decision": {
            "custody_review_may_continue": custody_review_may_continue,
            "custody_release_allowed": False,
            "reliance_effect": "stayed",
            "blocked_actions": [
                "create counterparty-artifact-custody-record from pilot hash shell alone",
                "create external-receipt-response-record while challenge is pending or blocked",
                "create external-receipt-intake-record before response and authority gates",
                "run actual-receipt-import-gate from a candidate challenge report",
                "increment computed live receipt floor",
            ],
            "next_actions": [
                "complete manual counterparty contact and request-trace challenge route",
                "resolve or publish any challenge without retaliation or reliance upgrade",
                "only then consider custody handoff with verifier, authority, issuer, timestamp, and independence evidence",
            ],
            "reason": "candidate challenge/replay is a pre-custody stay: it proves challengeability or blocks the candidate, but never creates a live receipt.",
        },
        "public_summary": f"{REV} candidate challenge report for {ledger.get('ledger_id') or 'unknown-ledger'} is {state}; custody, response, intake, import, and live-floor effects remain locked.",
        "no_live_floor_effect": True,
    }
    write_json(report_path, report)
    print(report_path)


if __name__ == "__main__":
    main()
