#!/usr/bin/env python3
"""Prepare a live receipt late-change notice dispatch record.

Late-change ingress proves that a revocation/supersession/challenge/correction
signal was captured. This tool proves the next thing: affected parties receive a
redacted freeze/remedy notice through retained, accessible channels. The notice
record does not continue publication, waive silence, upgrade reliance, or change
the live floor.
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
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "late-change-notice"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _contains_private_locator(values) -> bool:
    return any("private-vault://" in str(v) for v in values)


def build(
    *,
    late_change_ingress: dict,
    late_change_ingress_ref: str,
    receipt_id: str,
    created_at: str,
    revision: str,
    affected_party_refs: list[str] | None = None,
    notice_channels: list[str] | None = None,
    public_freeze_notice_ref: str = "none",
    nonhost_delivery_proof_ref: str = "none",
    remedy_or_appeal_window_ref: str = "none",
    accessible_notice_profile_ref: str = "none",
    redaction_boundary_ref: str = "none",
    dispatch_artifact: str = "none",
    private_locator_leak: bool = False,
) -> dict:
    affected_party_refs = affected_party_refs or []
    notice_channels = notice_channels or []
    signal = late_change_ingress.get("signal_summary", {})
    decision = late_change_ingress.get("decision", {})
    locks = late_change_ingress.get("publication_freeze_locks", {})
    live_signal = bool(signal.get("live_late_signal_present"))
    ingress_state = decision.get("late_change_state", "missing")
    signal_ready = (not live_signal) or ingress_state == "opened-publication-rollback-required"
    publication_ref = late_change_ingress.get("linked_publication_adjudication_ref", "missing")
    recompute_ref = late_change_ingress.get("linked_floor_recompute_receipt_ref", "missing")
    target_ref = signal.get("target_receipt_or_publication_ref", publication_ref)

    affected_ok = (not live_signal) or len([p for p in affected_party_refs if p]) >= 2
    counterparty_notice = (not live_signal) or any("counterparty" in p for p in affected_party_refs)
    subject_notice = (not live_signal) or any(("subject" in p or "representative" in p or "advocate" in p) for p in affected_party_refs)
    freeze_notice = (not live_signal) or public_freeze_notice_ref not in {"", "none"}
    delivery_ok = (not live_signal) or (nonhost_delivery_proof_ref not in {"", "none"} and not nonhost_delivery_proof_ref.startswith("private-vault://"))
    remedy_ok = (not live_signal) or remedy_or_appeal_window_ref not in {"", "none"}
    accessible_ok = (not live_signal) or bool(notice_channels) and accessible_notice_profile_ref not in {"", "none"}
    redaction_ok = (not live_signal) or redaction_boundary_ref not in {"", "none"}
    private_safe = not private_locator_leak and not _contains_private_locator([
        late_change_ingress_ref,
        publication_ref,
        recompute_ref,
        target_ref,
        public_freeze_notice_ref,
        nonhost_delivery_proof_ref,
        remedy_or_appeal_window_ref,
        accessible_notice_profile_ref,
        redaction_boundary_ref,
        *affected_party_refs,
        *notice_channels,
    ])
    checks = {
        "ingress_replayed": bool(late_change_ingress.get("late_change_ingress_id")) and late_change_ingress.get("no_direct_floor_effect") is True,
        "signal_requires_notice": live_signal,
        "affected_parties_identified": affected_ok,
        "counterparty_notice_prepared": counterparty_notice,
        "subject_or_representative_notice_prepared": subject_notice,
        "public_freeze_notice_prepared": freeze_notice,
        "nonhost_delivery_proof_present": delivery_ok,
        "remedy_window_opened": remedy_ok,
        "accessible_notice_channel_used": accessible_ok,
        "redaction_boundary_recorded": redaction_ok,
        "private_material_not_in_public_release": private_safe,
        "publication_continuation_stayed": (not live_signal) or locks.get("may_continue_published_snapshot_from_ingress") is False,
        "no_silence_as_waiver": True,
    }
    if not live_signal:
        state = "monitoring-no-signal-no-notice-required"
    elif not signal_ready:
        state = "blocked-ingress-not-opened-or-unrouted"
    elif not private_safe:
        state = "blocked-private-material-in-public-notice"
    elif not (affected_ok and counterparty_notice and subject_notice and freeze_notice):
        state = "blocked-affected-party-notice-missing"
    elif not delivery_ok or not accessible_ok or not redaction_ok:
        state = "blocked-delivery-proof-missing"
    elif not remedy_ok:
        state = "blocked-remedy-window-missing"
    else:
        state = "dispatch-ready-publication-stayed"
    ready = state == "dispatch-ready-publication-stayed"
    if state == "monitoring-no-signal-no-notice-required":
        reason = "No live late-change signal exists; the notice dispatch control has no publication, reliance, or floor effect."
    elif ready:
        reason = "The late signal has affected-party notice, public freeze notice, retained delivery proof, accessibility, remedy window, and redaction boundaries; publication remains stayed until recompute/adjudication rerun."
    else:
        reason = "Late-change notice dispatch blocked: " + "; ".join(k for k, v in checks.items() if v is not True)
    return {
        "late_change_notice_dispatch_id": f"LRLCND-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-late-change-notice-dispatch-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_late_change_ingress_ref": late_change_ingress_ref,
        "linked_publication_adjudication_ref": publication_ref,
        "linked_floor_recompute_receipt_ref": recompute_ref,
        "notice_context": {
            "live_late_signal_present": live_signal,
            "signal_type": signal.get("signal_type", "none"),
            "target_receipt_or_publication_ref": target_ref,
            "affected_party_refs": affected_party_refs,
            "notice_channels": notice_channels,
            "public_freeze_notice_ref": public_freeze_notice_ref,
            "nonhost_delivery_proof_ref": nonhost_delivery_proof_ref,
            "remedy_or_appeal_window_ref": remedy_or_appeal_window_ref,
            "accessible_notice_profile_ref": accessible_notice_profile_ref,
            "redaction_boundary_ref": redaction_boundary_ref,
            "private_material_locator_redacted": not private_locator_leak,
            "dispatch_artifact_sha256": "none" if dispatch_artifact == "none" else sha256_text(dispatch_artifact),
        },
        "dispatch_checks": checks,
        "notice_freeze_locks": {
            "may_continue_published_snapshot_from_notice": False,
            "may_continue_reliance_from_notice": False,
            "may_upgrade_reliance_from_notice": False,
            "may_increment_live_floor_from_notice": False,
            "manual_publication_override_allowed": False,
            "notice_silence_counts_as_waiver": False,
            "must_rerun_publication_rollback_adjudication_after_dispatch": live_signal,
        },
        "decision": {
            "notice_dispatch_state": state,
            "may_mark_notice_dispatch_ready": ready,
            "may_publish_or_continue_snapshot": False,
            "may_upgrade_reliance": False,
            "reason": reason,
            "blocked_actions": [
                "continuing a published floor/reliance posture from a notice dispatch record",
                "treating notice silence as waiver or acceptance",
                "routing revocation, supersession, challenge, or correction without affected-party remedy notice",
                "publishing private-vault locators or raw late-signal material",
            ],
            "next_actions": [
                "serve affected counterparty and subject/representative channels with a redacted freeze notice before any adjudication rerun",
                "retain delivery proof outside the public release tree and publish only public-shell/hash references",
                "rerun floor recompute receipt plus publication rollback adjudication after dispatch is ready or blocked",
            ],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--late-change-ingress", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--affected-party-ref", action="append", default=[])
    parser.add_argument("--notice-channel", action="append", default=[])
    parser.add_argument("--public-freeze-notice-ref", default="none")
    parser.add_argument("--nonhost-delivery-proof-ref", default="none")
    parser.add_argument("--remedy-or-appeal-window-ref", default="none")
    parser.add_argument("--accessible-notice-profile-ref", default="none")
    parser.add_argument("--redaction-boundary-ref", default="none")
    parser.add_argument("--dispatch-artifact", default="none")
    parser.add_argument("--private-locator-leak", action="store_true")
    args = parser.parse_args()
    revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    path = Path(args.late_change_ingress)
    if not path.is_absolute():
        path = ROOT / path
    ingress = load(path)
    record = build(
        late_change_ingress=ingress,
        late_change_ingress_ref=_rel(path),
        receipt_id=args.receipt_id,
        created_at=args.created_at,
        revision=revision,
        affected_party_refs=args.affected_party_ref,
        notice_channels=args.notice_channel,
        public_freeze_notice_ref=args.public_freeze_notice_ref,
        nonhost_delivery_proof_ref=args.nonhost_delivery_proof_ref,
        remedy_or_appeal_window_ref=args.remedy_or_appeal_window_ref,
        accessible_notice_profile_ref=args.accessible_notice_profile_ref,
        redaction_boundary_ref=args.redaction_boundary_ref,
        dispatch_artifact=args.dispatch_artifact,
        private_locator_leak=args.private_locator_leak,
    )
    out = Path(args.output_dir)
    if not out.is_absolute():
        out = ROOT / out
    write_json(out / f"live-receipt-late-change-notice-dispatch-record-{safe_slug(args.receipt_id)}.json", record)


if __name__ == "__main__":
    main()
