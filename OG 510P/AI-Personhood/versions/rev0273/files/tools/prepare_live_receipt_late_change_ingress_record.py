#!/usr/bin/env python3
"""Prepare a live receipt late-change ingress record.

This is the post-publication intake gate for revocation, supersession,
challenge, rollback evidence, counterparty correction, authority withdrawal, or
hash-mismatch signals. It captures the signal, proves it is retained and public-
shell safe, and routes it back into publication rollback adjudication. The ingress
record never continues publication, upgrades reliance, or increments the floor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CREATED_AT = "2026-06-16T19:06:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "late-change-ingress"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def build(*, publication_adjudication: dict, publication_adjudication_ref: str, receipt_id: str, created_at: str, revision: str, signal_type: str = "none", source_actor_class: str = "none", source_identity_ref: str = "none", target_ref: str | None = None, nonhost_retention_ref: str = "none", public_summary_ref: str = "none", signal_artifact: str = "none", supersedes_or_revokes_refs: list[str] | None = None, signature_or_contact_channel_captured: bool | None = None, independent_timestamp_present: bool | None = None, route_supersession: bool = True, private_locator_leak: bool = False) -> dict:
    live_signal = signal_type != "none"
    recompute_ref = publication_adjudication.get("linked_floor_recompute_receipt_ref", "missing")
    snapshot_ref = publication_adjudication.get("linked_computed_snapshot_ref", "missing")
    target = target_ref or publication_adjudication_ref
    supersedes_or_revokes_refs = supersedes_or_revokes_refs or []
    source_identified = (not live_signal) or (source_actor_class != "none" and source_identity_ref not in {"", "none"})
    nonhost_retained = (not live_signal) or (nonhost_retention_ref not in {"", "none"} and not nonhost_retention_ref.startswith("private-vault://"))
    public_summary_ready = (not live_signal) or public_summary_ref not in {"", "none"}
    contact_captured = (not live_signal) or (signature_or_contact_channel_captured is True)
    timestamp_present = (not live_signal) or (independent_timestamp_present is True)
    scope_recorded = signal_type not in {"supersession", "revocation", "authority-withdrawal"} or bool(supersedes_or_revokes_refs)
    if signal_type == "supersession" and not route_supersession:
        scope_recorded = False
    rollback_trigger = (not live_signal) or signal_type in {"challenge", "revocation", "supersession", "rollback-evidence", "counterparty-correction", "hash-mismatch", "authority-withdrawal"}
    private_safe = not private_locator_leak and all("private-vault://" not in str(v) for v in [publication_adjudication_ref, recompute_ref, snapshot_ref, target, nonhost_retention_ref, public_summary_ref])
    checks = {
        "signal_source_identified": source_identified,
        "binds_to_existing_publication_or_receipt": bool(target and target != "missing"),
        "nonhost_retention_present": nonhost_retained,
        "independent_timestamp_present": timestamp_present,
        "signature_or_contact_channel_captured": contact_captured,
        "supersession_scope_recorded": scope_recorded,
        "rollback_trigger_classified": rollback_trigger,
        "public_notice_required": live_signal,
        "public_notice_prepared": public_summary_ready,
        "recompute_required_after_signal": live_signal,
        "publication_continuation_stayed": live_signal,
        "private_material_not_in_public_release": private_safe,
    }
    if not live_signal:
        state = "monitoring-no-signal"
    elif not source_identified:
        state = "blocked-unknown-source"
    elif not nonhost_retained:
        state = "blocked-unretained-signal"
    elif not private_safe:
        state = "blocked-private-material-in-public-ingress"
    elif not scope_recorded:
        state = "blocked-supersession-unrouted"
    else:
        state = "opened-publication-rollback-required"
    may_trigger = state == "opened-publication-rollback-required"
    if state == "monitoring-no-signal":
        reason = "No live late-change signal is present in this control record; the record has no publication, reliance, or floor effect."
    elif may_trigger:
        reason = "A live late-change signal was retained and public-shell summarized; publication must be re-adjudicated and cannot continue from the ingress record."
    else:
        reason = "Late-change signal ingress is blocked: " + "; ".join(k for k, v in checks.items() if v is not True)
    return {
        "late_change_ingress_id": f"LRLCI-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-late-change-ingress-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_publication_adjudication_ref": publication_adjudication_ref,
        "linked_floor_recompute_receipt_ref": recompute_ref,
        "linked_computed_snapshot_ref": snapshot_ref,
        "signal_summary": {
            "live_late_signal_present": live_signal,
            "signal_type": signal_type,
            "source_actor_class": source_actor_class,
            "source_identity_ref": source_identity_ref,
            "target_receipt_or_publication_ref": target,
            "received_at": created_at,
            "nonhost_retention_ref": nonhost_retention_ref,
            "public_summary_ref": public_summary_ref,
            "private_material_locator_redacted": not private_locator_leak,
            "supersedes_or_revokes_refs": supersedes_or_revokes_refs,
            "signal_artifact_sha256": "none" if signal_artifact == "none" else sha256_text(signal_artifact),
            "receipt_class": publication_adjudication.get("observed_publication_summary", {}).get("receipt_class", "unknown"),
            "dependency_group": "unknown-until-real-signal" if not live_signal else f"late-signal:{safe_slug(source_identity_ref)}",
        },
        "ingress_checks": checks,
        "publication_freeze_locks": {
            "may_continue_published_snapshot_from_ingress": False,
            "may_continue_reliance_from_ingress": False,
            "may_upgrade_reliance_from_ingress": False,
            "may_increment_live_floor_from_ingress": False,
            "manual_publication_override_allowed": False,
            "must_rerun_publication_rollback_adjudication_if_signal_present": True,
            "late_signal_reopens_publication": live_signal,
        },
        "decision": {
            "late_change_state": state,
            "may_trigger_publication_rollback_adjudication": may_trigger,
            "may_publish_or_continue_snapshot": False,
            "may_upgrade_reliance": False,
            "reason": reason,
            "blocked_actions": [
                "continuing a published snapshot from a late-change ingress record",
                "treating a revocation, supersession, or correction as an informal note",
                "upgrading reliance or incrementing the floor before recompute plus publication rollback adjudication rerun",
                "publishing private-vault locators or raw signal material",
            ],
            "next_actions": [
                "retain signal outside the public release tree and publish only a hash/public-shell summary",
                "rerun floor recompute receipt and publication rollback adjudication after any live late-change signal",
                "issue failed-gate or rollback notice if the signal blocks continued publication",
            ],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publication-adjudication", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--signal-type", default="none", choices=["none", "challenge", "revocation", "supersession", "rollback-evidence", "counterparty-correction", "hash-mismatch", "authority-withdrawal"])
    parser.add_argument("--source-actor-class", default="none")
    parser.add_argument("--source-identity-ref", default="none")
    parser.add_argument("--target-ref")
    parser.add_argument("--nonhost-retention-ref", default="none")
    parser.add_argument("--public-summary-ref", default="none")
    parser.add_argument("--signal-artifact", default="none")
    parser.add_argument("--supersedes-or-revokes-ref", action="append", default=[])
    parser.add_argument("--signature-or-contact-channel-captured", action="store_true")
    parser.add_argument("--independent-timestamp-present", action="store_true")
    parser.add_argument("--route-supersession", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--private-locator-leak", action="store_true")
    args = parser.parse_args()
    revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    path = Path(args.publication_adjudication)
    if not path.is_absolute():
        path = ROOT / path
    publication_adjudication = load(path)
    record = build(
        publication_adjudication=publication_adjudication,
        publication_adjudication_ref=_rel(path),
        receipt_id=args.receipt_id,
        created_at=args.created_at,
        revision=revision,
        signal_type=args.signal_type,
        source_actor_class=args.source_actor_class,
        source_identity_ref=args.source_identity_ref,
        target_ref=args.target_ref,
        nonhost_retention_ref=args.nonhost_retention_ref,
        public_summary_ref=args.public_summary_ref,
        signal_artifact=args.signal_artifact,
        supersedes_or_revokes_refs=args.supersedes_or_revokes_ref,
        signature_or_contact_channel_captured=args.signature_or_contact_channel_captured,
        independent_timestamp_present=args.independent_timestamp_present,
        route_supersession=args.route_supersession,
        private_locator_leak=args.private_locator_leak,
    )
    out = Path(args.output_dir) / f"live-receipt-late-change-ingress-record-{safe_slug(args.receipt_id)}.json"
    if not out.is_absolute():
        out = ROOT / out
    write_json(out, record)
    print(out)


if __name__ == "__main__":
    main()
