#!/usr/bin/env python3
"""Build a public inbound-capture shell without releasing raw reply bytes.

A future operator can point this at raw RFC 5322/RFC 6532 message bytes or a
provider export stored outside the release tree. The tool copies live inbound
bytes only into an off-release private vault and emits a public JSON shell with
hash/size/MIME and header-assessment booleans. The shell is never response,
custody, intake, import, authority, waiver, or live-floor evidence by itself.
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
import hashlib
import json
import mimetypes
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED = "2026-06-16T22:25:00Z"
DEFAULT_PRIVATE_VAULT_DIR = ROOT.parent / "AI-Personhood-private-evidence-vault" / REV / "external-contact-inbound"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_slug(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    cleaned = "".join(ch if ch in allowed else "-" for ch in value).strip(".-")
    return cleaned or "inbound"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def private_vault_root(vault_root: Optional[Path]) -> Path:
    if vault_root is not None:
        return vault_root.expanduser().resolve()
    env_root = os.environ.get("AI_PERSONHOOD_EXTERNAL_CONTACT_INBOUND_VAULT")
    if env_root:
        return Path(env_root).expanduser().resolve() / REV / "external-contact-inbound"
    return DEFAULT_PRIVATE_VAULT_DIR.resolve()


def parse_headers(path: Path) -> dict:
    raw = path.read_bytes()
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        return {
            "parse_attempted": True,
            "message_id_present": False,
            "date_header_present": False,
            "from_header_present": False,
            "to_or_delivered_to_present": False,
            "received_or_provider_trace_present": False,
            "authentication_results_summary_present": False,
            "arc_summary_present": False,
        }
    headers = {k.lower(): msg.get_all(k, []) for k in msg.keys()}
    return {
        "parse_attempted": True,
        "message_id_present": bool(headers.get("message-id")),
        "date_header_present": bool(headers.get("date")),
        "from_header_present": bool(headers.get("from")),
        "to_or_delivered_to_present": bool(headers.get("to") or headers.get("delivered-to") or headers.get("x-original-to")),
        "received_or_provider_trace_present": bool(headers.get("received") or headers.get("x-google-smtp-source") or headers.get("x-ms-exchange-organization-network-message-id")),
        "authentication_results_summary_present": bool(headers.get("authentication-results") or headers.get("dkim-signature") or headers.get("received-spf")),
        "arc_summary_present": bool(headers.get("arc-seal") or headers.get("arc-message-signature") or headers.get("arc-authentication-results")),
    }


def build_shell(*, source: Optional[Path], output_rel: str, capture_id: str, created_at: str, source_kind: str, vault_root: Optional[Path], copy: bool) -> dict:
    raw_present = source is not None and source.exists() and source.is_file() and not source.is_symlink()
    private_locator = None
    source_locator = None
    raw_hash = None
    size = None
    mime = None
    message_format = None
    parse = {
        "parse_attempted": False,
        "message_id_present": False,
        "date_header_present": False,
        "from_header_present": False,
        "to_or_delivered_to_present": False,
        "received_or_provider_trace_present": False,
        "authentication_results_summary_present": False,
        "arc_summary_present": False,
    }
    state = "pre-dispatch-no-inbound"
    shell_created = False

    if raw_present:
        src = source.resolve()
        if is_relative_to(src, ROOT):
            raise SystemExit("external-contact inbound raw bytes must be outside the public release tree")
        raw_hash = sha256(src)
        size = src.stat().st_size
        mime = mimetypes.guess_type(src.name)[0] or "message/rfc822"
        message_format = "provider-export" if source_kind == "provider-export" else "rfc5322-rfc6532-message"
        parse = parse_headers(src)
        vault = private_vault_root(vault_root)
        if is_relative_to(vault, ROOT):
            raise SystemExit("external-contact inbound vault root must be outside the public release tree")
        target = vault / f"{safe_slug(capture_id)}{src.suffix or '.eml'}"
        if copy:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        private_locator = f"private-vault://{REV}/external-contact-inbound/{target.name}"
        source_locator = f"private-source-redacted:sha256:{raw_hash}"
        state = "candidate-provider-export-staged-public-shell-only" if source_kind == "provider-export" else "candidate-raw-email-staged-public-shell-only"
        shell_created = True

    return {
        "capture_shell_id": capture_id,
        "schema_version": "external-contact-inbound-capture-shell-v0.1",
        "revision": REV,
        "created_at": created_at,
        "capture_state": state,
        "source_inbound_vault_precommit_ref": f"examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json",
        "source_send_proof_record_ref": f"examples/external-contact-send-proof-record-{REV}-no-transport-proof.json",
        "source_response_triage_record_ref": f"examples/external-contact-response-triage-record-{REV}-pre-dispatch.json",
        "source_execution_record_ref": f"examples/external-contact-execution-record-{REV}-ready-to-dispatch.json",
        "capture_tool": {
            "tool_path": "tools/stage_external_contact_inbound_capture.py",
            "raw_input_required_outside_release_tree": True,
            "copy_to_private_vault_only": True,
            "public_shell_only": True,
            "check_output_supported": True,
            "tool_is_not_dispatch_or_response": True,
        },
        "candidate_payload": {
            "raw_payload_present_now": raw_present,
            "source_locator": source_locator,
            "private_vault_locator": private_locator,
            "raw_sha256": raw_hash,
            "size_bytes": size,
            "mime_type": mime,
            "message_format": message_format,
            "raw_payload_publicly_embedded": False,
            "screenshot_or_redacted_only": False,
            "protocol_output_only": False,
            "retention_permission_present_now": False,
            "nonhost_retention_present_now": False,
        },
        "transport_parse": {
            "rfc5322_parse_attempted": parse["parse_attempted"],
            "message_id_present": parse["message_id_present"],
            "date_header_present": parse["date_header_present"],
            "from_header_present": parse["from_header_present"],
            "to_or_delivered_to_present": parse["to_or_delivered_to_present"],
            "in_reply_to_or_references_binding_state": "not-applicable-no-sent-message",
            "received_or_provider_trace_present": parse["received_or_provider_trace_present"],
            "authentication_results_summary_present": parse["authentication_results_summary_present"],
            "arc_summary_present": parse["arc_summary_present"],
            "parse_or_authentication_may_create_authority": False,
            "parse_or_authentication_may_start_clock": False,
        },
        "public_shell": {
            "shell_created_now": shell_created,
            "allowed_public_fields": ["capture shell id", "revision", "sha256", "size bytes", "MIME/type", "message/header presence booleans", "routing decision", "failed-gate/non-effect summary"],
            "forbidden_public_fields": ["raw reply bytes", "full headers", "private vault path", "personal data", "trade secrets", "counterparty secrets", "retention permission text", "waiver inference", "adverse inference", "status recognition", "live-floor claim"],
            "shell_may_satisfy_raw_custody": False,
            "shell_may_satisfy_counterparty_authority": False,
            "shell_may_start_response_clock": False,
            "shell_may_publish_raw_bytes": False,
        },
        "routing_constraints": {
            "auto_ack_route": "Route automated acknowledgements to response triage as non-response unless later human content and raw bytes are verified.",
            "decline_route": "Route declines to a failed-gate/no-response public shell without waiver, adverse inference, custody, import, or floor effect.",
            "human_reply_route": "Route human replies first through raw-vault staging, retention/confidentiality review, authority binder, response verification, and challenge before custody.",
            "malformed_or_spoofed_route": "Route malformed, spoofed, screenshot-only, pasted-text, or redacted-only material to rejection/quarantine with no response-clock or custody effect.",
            "silence_route": "Silence can be described only after actual send proof and deadline passage; silence never creates waiver, adverse inference, custody, or live-floor evidence.",
            "routes_may_create_response_record_directly": False,
        },
        "downstream_locks": {
            "may_treat_capture_shell_as_raw_reply": False,
            "may_treat_capture_shell_as_transport_proof": False,
            "may_treat_capture_shell_as_authority": False,
            "may_start_response_clock": False,
            "may_create_response_record": False,
            "may_create_custody_record": False,
            "may_create_intake_record": False,
            "may_create_import_gate": False,
            "may_increment_live_floor": False,
            "may_claim_status_or_waiver": False,
            "may_publish_raw_payload": False,
        },
        "linked_queue_ids": [
            "FT-0205-FIRST-REAL-ARTIFACT-DROP",
            "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION",
            "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE",
            "FT-0233-VAULT-INTAKE-SHELL-BOUNDARY",
        ],
        "related_surfaces": [
            f"examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json",
            f"examples/external-contact-send-proof-record-{REV}-no-transport-proof.json",
            f"examples/external-contact-response-triage-record-{REV}-pre-dispatch.json",
            f"examples/external-contact-execution-record-{REV}-ready-to-dispatch.json",
            "schemas/external-contact-inbound-capture-shell.schema.json",
            "tools/stage_external_contact_inbound_capture.py",
            "tools/audit_external_contact_inbound_capture_shell.py",
            "fixtures/negative-tests/external-contact-inbound-capture-shell-public-raw-leak.json",
            f"docs/00-meta/{REV}-inbound-capture-shell-vaultstage-refactor.md",
        ],
        "public_summary": f"{REV} creates a public inbound-capture shell contract and staging tool for future raw email/provider exports; no inbound bytes exist now, and any future shell remains non-custodial, non-authoritative, non-response, non-intake, non-import, non-recognition, and no-floor until downstream gates pass.",
        "no_live_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input_path")
    parser.add_argument("--output", default=f"examples/external-contact-inbound-capture-shell-{REV}-no-inbound.json")
    parser.add_argument("--capture-id", default=f"ECICS-2026-{REV}-aiid-no-inbound-public-shell")
    parser.add_argument("--created-at", default=DEFAULT_CREATED)
    parser.add_argument("--source-kind", default="raw-email", choices=["raw-email", "provider-export"])
    parser.add_argument("--vault-root")
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()
    source = Path(args.input_path).expanduser().resolve() if args.input_path else None
    vault_root = Path(args.vault_root).expanduser().resolve() if args.vault_root else None
    shell = build_shell(source=source, output_rel=args.output, capture_id=args.capture_id, created_at=args.created_at, source_kind=args.source_kind, vault_root=vault_root, copy=not args.check_output)
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    text = json.dumps(shell, indent=2) + "\n"
    if args.check_output:
        existing = out.read_text(encoding="utf-8")
        if existing != text:
            raise SystemExit(f"external-contact inbound capture shell mismatch: {out.relative_to(ROOT)}")
        print("stage_external_contact_inbound_capture: OK")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(out.relative_to(ROOT) if is_relative_to(out, ROOT) else out)


if __name__ == "__main__":
    main()
