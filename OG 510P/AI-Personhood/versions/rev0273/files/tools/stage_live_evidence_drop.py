#!/usr/bin/env python3
"""Stage an evidence drop without letting live raw payloads enter releases.

Controls and synthetic dry-runs may still be copied under
examples/artifacts/live-evidence-drops/ so regression tests remain reproducible.
A real live-counterparty source is copied to a private vault outside the archive
root by default, and the public ledger receives only hash/size/MIME data plus a
private-vault:// locator. The ledger still has zero live-floor effect; LEAP,
custody, verifier, authority, retention, response, intake, import, and computed
floor checks remain separate gates.
"""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
import json
import mimetypes
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PUBLIC_CONTROL_QUARANTINE_DIR = ROOT / "examples" / "artifacts" / "live-evidence-drops"
DEFAULT_PRIVATE_VAULT_DIR = ROOT.parent / "AI-Personhood-private-evidence-vault" / REV / "live-evidence-drops"
PROTOCOL_SOURCE_KINDS = {"mcp-tool-output", "a2a-task-artifact", "federated-relay"}
PUBLIC_CONTEXTS = {"institutional-dry-run", "controlled-fixture", "host-generated", "unknown"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_slug(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    cleaned = "".join(ch if ch in allowed else "-" for ch in value)
    cleaned = cleaned.strip(".-")
    return cleaned or "drop"


def scan_zip(path: Path) -> Tuple[bool, bool, bool]:
    """Return contains_archive, nested_archive_detected, path_traversal_detected."""
    if not zipfile.is_zipfile(path):
        return False, False, False
    nested = False
    traversal = False
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            name = info.filename
            parts = Path(name).parts
            if name.startswith("/") or ".." in parts:
                traversal = True
            if name.lower().endswith((".zip", ".jar", ".war", ".egg", ".whl")):
                nested = True
    return True, nested, traversal


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _private_vault_root(vault_root: Optional[Path]) -> Path:
    if vault_root is not None:
        return vault_root.expanduser().resolve()
    env_root = os.environ.get("AI_PERSONHOOD_PRIVATE_EVIDENCE_VAULT")
    if env_root:
        return Path(env_root).expanduser().resolve() / REV / "live-evidence-drops"
    return DEFAULT_PRIVATE_VAULT_DIR.resolve()


def _target_for(*, drop_slug: str, suffix: str, collection_context: str, vault_root: Optional[Path]) -> Tuple[Path, bool]:
    if collection_context == "live-counterparty":
        target_dir = _private_vault_root(vault_root)
        return target_dir / f"{drop_slug}{suffix}", True
    return PUBLIC_CONTROL_QUARANTINE_DIR / f"{drop_slug}{suffix}", False


def _public_locator_for(path: Path, *, is_private: bool) -> str:
    if is_private:
        return f"private-vault://{REV}/live-evidence-drops/{path.name}"
    return path.relative_to(ROOT).as_posix()


def _source_locator_for(source: Optional[Path], *, source_hash: Optional[str], private: bool) -> Optional[str]:
    if source is None:
        return None
    if private:
        return f"private-source-redacted:sha256:{source_hash}"
    if _is_relative_to(source, ROOT):
        return source.resolve().relative_to(ROOT.resolve()).as_posix()
    return str(source)


def build_ledger(
    *,
    source: Optional[Path],
    drop_id: str,
    created_at: str,
    source_kind: str,
    collection_context: str,
    linked_leap: str,
    copy: bool,
    vault_root: Optional[Path] = None,
) -> dict:
    drop_slug = safe_slug(drop_id)
    ledger_id = f"LEDL-2026-{drop_slug}"
    locator_resolved = source is not None and source.exists() and source.is_file() and not source.is_symlink()

    source_hash = None
    source_size = None
    source_mime = "application/octet-stream"
    quarantine_ref = None
    quarantine_hash = None
    quarantine_size = None
    immutable_copy_present = False
    contains_archive = False
    nested_archive_detected = False
    path_traversal_detected = False
    private_target = collection_context == "live-counterparty"

    if locator_resolved:
        source = source.resolve()
        source_hash = sha256(source)
        source_size = source.stat().st_size
        source_mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        contains_archive, nested_archive_detected, path_traversal_detected = scan_zip(source)
        suffix = source.suffix if source.suffix else ".bin"
        target, private_target = _target_for(drop_slug=drop_slug, suffix=suffix, collection_context=collection_context, vault_root=vault_root)
        if private_target and _is_relative_to(target, ROOT):
            raise SystemExit("live-counterparty evidence vault must be outside the archive release tree")
        if copy:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != target.resolve():
                shutil.copyfile(source, target)
        if target.exists():
            quarantine_ref = _public_locator_for(target, is_private=private_target)
            quarantine_hash = sha256(target)
            quarantine_size = target.stat().st_size
            immutable_copy_present = quarantine_hash == source_hash and quarantine_size == source_size
    else:
        target = None

    protocol_source = source_kind in PROTOCOL_SOURCE_KINDS
    redacted_only = source_kind == "public-redaction"
    live_candidate = (
        collection_context == "live-counterparty"
        and not protocol_source
        and not redacted_only
        and locator_resolved
        and immutable_copy_present
        and not nested_archive_detected
        and not path_traversal_detected
        and private_target
    )
    control = collection_context in PUBLIC_CONTEXTS and locator_resolved and immutable_copy_present

    if live_candidate:
        intake_mode = "live-candidate-drop"
        artifact_state = "live-candidate-unverified"
        admission = "candidate-staged-not-admitted"
        can_open_leap = True
        reason = "Raw candidate was copied to an external private evidence vault and represented publicly only by hash/size/MIME and private-vault locator; LEAP may move to candidate-artifact-received only after authority, verifier, timestamp/log, non-host retention, and independence fields are supplied."
    elif control:
        intake_mode = "quarantine-control"
        artifact_state = "quarantine-control-not-live"
        admission = "no-live-control-staged"
        can_open_leap = False
        reason = "Control or non-live source was staged to verify hashing/copying without opening the live path."
    elif source is None:
        intake_mode = "ready-no-drop"
        artifact_state = "no-drop"
        admission = "ready"
        can_open_leap = False
        reason = "No source payload has been supplied."
    else:
        intake_mode = "rejected"
        artifact_state = "rejected"
        admission = "rejected"
        can_open_leap = False
        reason = "Source is absent, redacted-only, protocol-only, path-unsafe, nested-archive-bearing, not copied into the proper quarantine/vault, or attempted to place a live payload inside the release tree."

    source_display = _source_locator_for(source, source_hash=source_hash, private=private_target)
    events = [
        {"event_id": "LEDL-EV-001", "event_type": "source-resolved" if locator_resolved else "ready", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": source_display or "no-source", "can_satisfy_live_receipt": False},
    ]
    if source_hash:
        events.append({"event_id": "LEDL-EV-002", "event_type": "hash-recorded", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": f"sha256:{source_hash}", "can_satisfy_live_receipt": False})
    if quarantine_ref:
        events.append({"event_id": "LEDL-EV-003", "event_type": "quarantine-copy-staged", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": quarantine_ref, "can_satisfy_live_receipt": False})
    events.append({"event_id": "LEDL-EV-004", "event_type": "archive-scan", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": f"contains_archive={contains_archive};nested_archive={nested_archive_detected};path_traversal={path_traversal_detected}", "can_satisfy_live_receipt": False})
    events.append({"event_id": "LEDL-EV-005", "event_type": "classification", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": f"intake_mode={intake_mode};artifact_state={artifact_state}", "can_satisfy_live_receipt": False})
    events.append({"event_id": "LEDL-EV-006", "event_type": "blocked-before-leap", "at": created_at, "actor": "stage_live_evidence_drop.py", "evidence_ref": "quarantine ledger has no live-floor effect and cannot create response/intake/import records", "can_satisfy_live_receipt": False})

    return {
        "ledger_id": ledger_id,
        "schema_version": "live-evidence-drop-ledger-v0.1",
        "created_at": created_at,
        "revision": REV,
        "generated_by_tool": "tools/stage_live_evidence_drop.py",
        "intake_mode": intake_mode,
        "source_payload": {
            "original_locator": source_display,
            "source_kind": source_kind,
            "locator_resolved": locator_resolved,
            "source_sha256": source_hash,
            "source_size_bytes": source_size,
            "source_mime_type": source_mime,
            "copy_performed": bool(locator_resolved and quarantine_ref and immutable_copy_present),
        },
        "staged_payload": {
            "quarantine_locator": quarantine_ref,
            "quarantine_sha256": quarantine_hash,
            "quarantine_size_bytes": quarantine_size,
            "immutable_copy_present": immutable_copy_present,
            "raw_payload_retained": immutable_copy_present and not redacted_only and not protocol_source,
            "redacted_copy_only": redacted_only,
            "contains_archive": contains_archive,
            "nested_archive_detected": nested_archive_detected,
            "path_traversal_detected": path_traversal_detected,
        },
        "classification": {
            "collection_context": "protocol-output" if protocol_source else collection_context,
            "artifact_state": artifact_state,
            "protocol_or_transport_source": protocol_source,
            "authority_claim_present": False,
            "subject_authorization_present": False,
            "nonhost_retention_present": False,
            "independent_timestamp_present": False,
            "can_open_leap_candidate_state": can_open_leap,
            "can_create_response_record": False,
        },
        "mandatory_blocks": {
            "redacted_only_blocked": True,
            "tool_output_blocked": True,
            "protocol_transport_blocked": True,
            "archive_nested_zip_requires_manual_review": True,
            "path_traversal_blocked": True,
            "live_floor_delta_blocked": True,
            "downstream_objects_blocked": True,
        },
        "admission_refs": {
            "linked_leap_packet_ref": linked_leap,
            "linked_custody_record_ref": None,
            "failed_gate_public_summary_ref": "failed-gate-public-summary:live-evidence-drop-quarantine-required",
        },
        "audit_trace": events,
        "decision": {
            "quarantine_admission": admission,
            "reason": reason,
            "blocked_actions": [
                "create external receipt response record",
                "create external receipt intake record",
                "run actual receipt import gate",
                "increment live receipt floor",
                "treat protocol/tool/redaction provenance as authority",
                "package private raw payload bytes in the public release bundle",
            ],
            "next_actions": [
                "bind the quarantined raw payload into LEAP before custody",
                "collect class-specific authority and subject/representative authorization",
                "run cryptographic verifier adapter and independent timestamp/log checks",
                "verify non-host retention and independence fields before any downstream object creation",
                "publish only a hash/failed-gate public shell unless raw disclosure is explicitly authorized",
            ],
        },
        "public_summary": f"{REV} staged an evidence drop quarantine ledger in {intake_mode}; no response, intake, import, or live-floor action is permitted from this ledger alone.",
        "no_live_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input_path")
    parser.add_argument("--output", required=True)
    parser.add_argument("--drop-id", required=True)
    parser.add_argument("--created-at", help="ISO-8601 timestamp for the ledger; defaults to current UTC time when omitted")
    parser.add_argument("--source-kind", default="file-upload", choices=["file-upload", "raw-email", "api-payload", "mcp-tool-output", "a2a-task-artifact", "federated-relay", "public-redaction", "unknown"])
    parser.add_argument("--collection-context", default="unknown", choices=["live-counterparty", "institutional-dry-run", "controlled-fixture", "host-generated", "unknown"])
    parser.add_argument("--linked-leap", default=f"examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json")
    parser.add_argument("--vault-root", help="External private vault root for live-counterparty payload copies. Must not be inside the archive root.")
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()

    source = Path(args.input_path) if args.input_path else None
    if source is not None and not source.is_absolute():
        source = (ROOT / source).resolve()
    vault_root = Path(args.vault_root).resolve() if args.vault_root else None
    ledger = build_ledger(
        source=source,
        drop_id=args.drop_id,
        created_at=args.created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        source_kind=args.source_kind,
        collection_context=args.collection_context,
        linked_leap=args.linked_leap,
        copy=not args.check_output,
        vault_root=vault_root,
    )
    out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    text = json.dumps(ledger, indent=2) + "\n"
    if args.check_output:
        existing = out.read_text(encoding="utf-8")
        if existing != text:
            label = out.relative_to(ROOT).as_posix() if _is_relative_to(out, ROOT) else str(out)
            raise SystemExit(f"evidence drop ledger mismatch: {label}")
        print("stage_live_evidence_drop: OK")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out.relative_to(ROOT).as_posix() if _is_relative_to(out, ROOT) else str(out))


if __name__ == "__main__":
    main()
