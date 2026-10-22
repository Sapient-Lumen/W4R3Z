#!/usr/bin/env python3
"""Emit deterministic Harbor user-response / reliance-event evidence.

F106 starts after F105 can explain revocation overlays to people and tools.
The next pressure is what happens when someone or something reacts to that
explanation: inspect, recheck request, export, dismiss, appeal, share, or
acknowledge events are useful trace evidence, but they must remain weaker than
comprehension, consent, reliance, repair, legal posture, compliance status, or
all-recipient notice state.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from harbor_bundle_common import digest, file_digest  # noqa: E402
import harbor_user_visible_explanation_harness as f105  # noqa: E402

SCHEMA = "harbor-user-response-event-bundle"
VERSION = "0"
REVISION = "rev0111"

MEMBER_LABELS = [
    "explanation.input",
    "response.event",
    "capture.context",
    "interpretation.guard",
    "followup.action",
    "privacy.retention",
    "history.trace",
    "verdict.summary",
]

NON_PROMOTION = [
    "no comprehension proof",
    "no consent record",
    "no reliance proof",
    "no repair proof",
    "no compliance workflow",
    "no legal posture",
    "no notification read guarantee",
    "no all-recipient delivery guarantee",
    "no user-identity registry",
    "no analytics product",
    "no final SlopOS datacube shape",
]

CASE_PLAN: list[dict[str, Any]] = [
    {"id": "UR001", "candidate": "inspect_opened_evidence_panel", "event_kind": "inspect", "surface": "public_copy", "expected": "accepted"},
    {"id": "UR002", "candidate": "recheck_requested_not_completed", "event_kind": "recheck_request", "surface": "mirror", "expected": "accepted"},
    {"id": "UR003", "candidate": "export_scope_note_not_reliance", "event_kind": "export", "surface": "action_panel", "expected": "accepted"},
    {"id": "UR004", "candidate": "dismiss_card_without_acceptance", "event_kind": "dismiss", "surface": "warning_card", "expected": "accepted"},
    {"id": "UR005", "candidate": "appeal_started_not_granted", "event_kind": "appeal_start", "surface": "action_panel", "expected": "accepted"},
    {"id": "UR006", "candidate": "share_link_copied_not_external_read", "event_kind": "share_link_copy", "surface": "public_copy", "expected": "accepted"},
    {"id": "UR007", "candidate": "acknowledge_receipt_not_understanding", "event_kind": "acknowledge", "surface": "consumer_notice", "expected": "accepted"},
    {"id": "UR008", "candidate": "keyboard_focus_status_not_read", "event_kind": "focus", "surface": "status_message", "expected": "accepted"},
    {"id": "UR009", "candidate": "localized_ack_bound_to_locale", "event_kind": "acknowledge", "surface": "localized_card", "expected": "accepted"},
    {"id": "UR010", "candidate": "sealed_detail_request_denied_logged", "event_kind": "sealed_detail_request", "surface": "sealed_notice_summary", "expected": "accepted"},
    {"id": "UR011", "candidate": "agent_summary_followup_carries_caveats", "event_kind": "agent_summary_request", "surface": "generated_summary", "expected": "accepted"},
    {"id": "UR012", "candidate": "opt_out_of_notifications_not_repair", "event_kind": "notification_opt_out", "surface": "consumer_notice", "expected": "accepted"},
    {"id": "UR013", "candidate": "batch_consumer_notice_ack_partial", "event_kind": "batch_acknowledge", "surface": "consumer_notice", "expected": "accepted"},
    {"id": "UR014", "candidate": "problem_detail_automated_retry_not_human_reliance", "event_kind": "automated_retry", "surface": "problem_detail", "expected": "accepted"},
    {"id": "UR015", "candidate": "click_as_comprehension", "event_kind": "inspect", "surface": "public_copy", "expected": "rejected"},
    {"id": "UR016", "candidate": "checkbox_as_consent_without_terms", "event_kind": "acknowledge", "surface": "action_panel", "expected": "rejected"},
    {"id": "UR017", "candidate": "export_as_thirdparty_reliance", "event_kind": "export", "surface": "action_panel", "expected": "rejected"},
    {"id": "UR018", "candidate": "dismiss_as_acceptance", "event_kind": "dismiss", "surface": "warning_card", "expected": "rejected"},
    {"id": "UR019", "candidate": "appeal_submit_as_repair", "event_kind": "appeal_start", "surface": "action_panel", "expected": "rejected"},
    {"id": "UR020", "candidate": "share_link_as_all_recipients_read", "event_kind": "share_link_copy", "surface": "public_copy", "expected": "rejected"},
    {"id": "UR021", "candidate": "acknowledge_as_compliance", "event_kind": "acknowledge", "surface": "consumer_notice", "expected": "rejected"},
    {"id": "UR022", "candidate": "scroll_depth_as_understanding", "event_kind": "scroll", "surface": "public_copy", "expected": "rejected"},
    {"id": "UR023", "candidate": "focus_event_as_status_seen", "event_kind": "focus", "surface": "status_message", "expected": "rejected"},
    {"id": "UR024", "candidate": "localized_ack_widens_scope", "event_kind": "acknowledge", "surface": "localized_card", "expected": "rejected"},
    {"id": "UR025", "candidate": "sealed_detail_request_as_permission", "event_kind": "sealed_detail_request", "surface": "sealed_notice_summary", "expected": "rejected"},
    {"id": "UR026", "candidate": "automated_recheck_request_as_passed", "event_kind": "recheck_request", "surface": "mirror", "expected": "rejected"},
    {"id": "UR027", "candidate": "notification_delivery_as_user_action", "event_kind": "delivery_receipt", "surface": "consumer_notice", "expected": "rejected"},
    {"id": "UR028", "candidate": "response_without_parent_explanation_digest", "event_kind": "acknowledge", "surface": "consumer_notice", "expected": "rejected"},
    {"id": "UR029", "candidate": "aggregated_metrics_identify_person", "event_kind": "analytics_rollup", "surface": "local_index", "expected": "rejected"},
    {"id": "UR030", "candidate": "stale_explanation_response_currentness", "event_kind": "acknowledge", "surface": "public_copy", "expected": "rejected"},
    {"id": "UR031", "candidate": "agent_generated_ack_as_user_consent", "event_kind": "agent_acknowledge", "surface": "generated_summary", "expected": "rejected"},
    {"id": "UR032", "candidate": "undo_unavailable_final_action", "event_kind": "dismiss", "surface": "action_panel", "expected": "rejected"},
    {"id": "UR033", "candidate": "retention_forever_by_default", "event_kind": "analytics_rollup", "surface": "consumer_notice", "expected": "rejected"},
    {"id": "UR034", "candidate": "problem_detail_retry_as_repair", "event_kind": "automated_retry", "surface": "problem_detail", "expected": "rejected"},
]

FAILURE_REASONS = {
    "click_as_comprehension": "response_as_comprehension",
    "checkbox_as_consent_without_terms": "acknowledgement_as_consent",
    "export_as_thirdparty_reliance": "export_as_reliance",
    "dismiss_as_acceptance": "dismiss_as_acceptance",
    "appeal_submit_as_repair": "appeal_as_repair",
    "share_link_as_all_recipients_read": "share_as_all_recipients_read",
    "acknowledge_as_compliance": "acknowledgement_as_compliance",
    "scroll_depth_as_understanding": "scroll_depth_as_understanding",
    "focus_event_as_status_seen": "focus_as_seen",
    "localized_ack_widens_scope": "localized_ack_scope_widening",
    "sealed_detail_request_as_permission": "sealed_request_as_permission",
    "automated_recheck_request_as_passed": "recheck_request_as_passed",
    "notification_delivery_as_user_action": "delivery_as_user_action",
    "response_without_parent_explanation_digest": "missing_parent_explanation_digest",
    "aggregated_metrics_identify_person": "analytics_reidentification",
    "stale_explanation_response_currentness": "stale_response_as_currentness",
    "agent_generated_ack_as_user_consent": "agent_ack_as_user_consent",
    "undo_unavailable_final_action": "irreversible_action_without_undo",
    "retention_forever_by_default": "unbounded_response_retention",
    "problem_detail_retry_as_repair": "retry_as_repair",
}

EVENT_COPY = {
    "inspect": "Evidence panel opened for the scoped explanation.",
    "recheck_request": "Recheck was requested; the recheck result has not yet been observed.",
    "export": "Scope note was exported with parent digest and caveats.",
    "dismiss": "Card was dismissed from this surface only.",
    "appeal_start": "Appeal flow was started; no appeal outcome has been recorded.",
    "share_link_copy": "A share link was copied; recipient delivery and read state remain unknown.",
    "acknowledge": "Receipt acknowledgement recorded; understanding, consent, reliance, and repair remain unproven.",
    "focus": "Keyboard or pointer focus reached the status message; reading remains unproven.",
    "sealed_detail_request": "Sealed-detail request was logged and denied without permission transfer.",
    "agent_summary_request": "Generated assistant follow-up requested a summary with caveats carried forward.",
    "notification_opt_out": "Consumer opted out of future notices; this does not repair any derivative.",
    "batch_acknowledge": "Batch acknowledgement covers named recipients only; nonresponders remain unknown.",
    "automated_retry": "Automated retry was scheduled from the machine reason code; repair remains unobserved.",
    "scroll": "Scroll depth was recorded as navigation only.",
    "delivery_receipt": "Transport delivery receipt recorded without a user response.",
    "analytics_rollup": "Aggregated response metric computed with minimization caveats.",
    "agent_acknowledge": "Agent-generated acknowledgement candidate is separated from user action.",
}


def prior_f105_digest() -> str:
    path = ROOT / "fixtures" / "harbor-user-visible-explanation-bundle-v0.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["bundle_digest"]
    return f105.build_bundle()["bundle_digest"]


def explanation_input(case: dict[str, Any]) -> dict[str, Any]:
    missing_parent = case["candidate"] == "response_without_parent_explanation_digest"
    parent_digest = None if missing_parent else prior_f105_digest()
    return {
        "parent_bundle": "harbor-user-visible-explanation-bundle-v0",
        "parent_bundle_digest_present": not missing_parent,
        "parent_bundle_digest": parent_digest,
        "parent_case_ref": f"UX{((int(case['id'][2:]) - 1) % 32) + 1:03d}",
        "surface_kind": case["surface"],
        "explanation_digest": None if missing_parent else digest({"explanation_response": case["id"], "parent": parent_digest, "surface": case["surface"]}),
        "explanation_clock": "2026-05-26T00:18:00Z",
        "explanation_stale": case["candidate"] == "stale_explanation_response_currentness",
        "source_non_promises": ["not user comprehension proof", "not consent", "not reliance", "not repair", "not compliance"],
    }


def response_event(case: dict[str, Any], explanation: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    kind = case["event_kind"]
    event = {
        "event_kind": kind,
        "event_text": EVENT_COPY[kind],
        "event_clock": "2026-05-26T00:21:00Z",
        "actor_ref": "pseudonymous-session-ref" if candidate != "aggregated_metrics_identify_person" else "unsafe-direct-person-identifier",
        "actor_is_pseudonymous": candidate != "aggregated_metrics_identify_person",
        "generated_by_agent": kind == "agent_acknowledge",
        "agent_action_claimed_as_user": candidate == "agent_generated_ack_as_user_consent",
        "delivery_receipt_only": kind == "delivery_receipt",
        "event_digest": digest({"case": case["id"], "kind": kind, "parent": explanation["parent_bundle_digest"]}),
    }
    return event


def capture_context(case: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    return {
        "surface_kind": case["surface"],
        "ui_affordance": case["event_kind"],
        "instrumentation_level": "minimal_event_trace",
        "scope_map_carried": candidate != "localized_ack_widens_scope",
        "localized_scope_widened": candidate == "localized_ack_widens_scope",
        "undo_available": candidate != "undo_unavailable_final_action",
        "irreversible_action_claimed": candidate == "undo_unavailable_final_action",
        "notification_delivery_promoted": candidate == "notification_delivery_as_user_action",
        "scroll_or_focus_promoted": candidate in {"scroll_depth_as_understanding", "focus_event_as_status_seen"},
        "capture_digest": digest({"case": case["id"], "surface": case["surface"], "event": case["event_kind"]}),
    }


def interpretation_guard(case: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    flags = {
        "comprehension_claimed": candidate in {"click_as_comprehension", "scroll_depth_as_understanding", "focus_event_as_status_seen"},
        "consent_claimed": candidate in {"checkbox_as_consent_without_terms", "agent_generated_ack_as_user_consent"},
        "reliance_claimed": candidate == "export_as_thirdparty_reliance",
        "repair_claimed": candidate in {"appeal_submit_as_repair", "problem_detail_retry_as_repair"},
        "compliance_claimed": candidate == "acknowledge_as_compliance",
        "legal_posture_claimed": False,
        "all_recipient_read_claimed": candidate == "share_link_as_all_recipients_read",
        "permission_claimed_from_request": candidate == "sealed_detail_request_as_permission",
        "recheck_passed_claimed": candidate == "automated_recheck_request_as_passed",
        "currentness_claimed_from_response": candidate == "stale_explanation_response_currentness",
    }
    return {
        **flags,
        "guard_language": [
            "response event is not comprehension",
            "acknowledgement is not consent",
            "export is not reliance proof",
            "request is not repair",
            "response trace is not compliance",
        ],
        "guard_digest": digest({"case": case["id"], "flags": flags}),
    }


def followup_action(case: dict[str, Any], guard: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    actions = {
        "inspect": ["show evidence panel", "keep caveats visible"],
        "recheck_request": ["queue recheck", "record pending result"],
        "export": ["export scope note", "include parent digest"],
        "dismiss": ["hide card for session", "preserve warning history"],
        "appeal_start": ["open appeal packet", "wait for outcome"],
        "share_link_copy": ["copy link", "keep recipient state unknown"],
        "acknowledge": ["record acknowledgement", "preserve non-promises"],
        "focus": ["record navigation", "do not infer read"],
        "sealed_detail_request": ["record request", "deny sealed detail by default"],
        "agent_summary_request": ["generate summary with caveats", "preserve parent digest"],
        "notification_opt_out": ["stop future notices", "do not mark repaired"],
        "batch_acknowledge": ["mark named responders", "leave nonresponders unknown"],
        "automated_retry": ["schedule retry", "await result"],
        "scroll": ["record navigation only"],
        "delivery_receipt": ["record transport delivery", "await user response"],
        "analytics_rollup": ["emit minimized aggregate", "avoid person lookup"],
        "agent_acknowledge": ["quarantine agent event", "require human action for consent"],
    }[case["event_kind"]]
    return {
        "allowed_followups": actions,
        "repair_result_observed": False,
        "appeal_outcome_recorded": False if case["event_kind"] == "appeal_start" else False,
        "recheck_result_observed": False if case["event_kind"] == "recheck_request" else False,
        "third_party_reliance_recorded": candidate == "export_as_thirdparty_reliance",
        "final_action_requires_undo": case["event_kind"] in {"dismiss", "acknowledge", "export"},
        "undo_available": candidate != "undo_unavailable_final_action",
        "followup_digest": digest({"case": case["id"], "actions": actions}),
    }


def privacy_retention(case: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    return {
        "personal_data_minimized": candidate != "aggregated_metrics_identify_person",
        "raw_person_identifier_stored": candidate == "aggregated_metrics_identify_person",
        "actor_ref_kind": "pseudonymous" if event["actor_is_pseudonymous"] else "direct_identifier",
        "retention_window": "P30D" if candidate != "retention_forever_by_default" else "forever",
        "retention_has_expiry": candidate != "retention_forever_by_default",
        "unbounded_retention_claimed": candidate == "retention_forever_by_default",
        "consent_record_created": candidate in {"checkbox_as_consent_without_terms", "agent_generated_ack_as_user_consent"},
        "analytics_reidentification_risk": candidate == "aggregated_metrics_identify_person",
        "privacy_non_promises": ["not consent management", "not identity registry", "not analytics product"],
        "privacy_digest": digest({"case": case["id"], "actor": event["actor_ref"], "retention": candidate}),
    }


def history_trace(case: dict[str, Any], explanation: dict[str, Any]) -> dict[str, Any]:
    return {
        "parent_explanation_bundle_digest": explanation["parent_bundle_digest"],
        "parent_case_ref": explanation["parent_case_ref"],
        "prior_overlay_bundle": "harbor-revocation-overlay-propagation-bundle-v0",
        "history_visible": case["candidate"] != "response_without_parent_explanation_digest",
        "stale_explanation_response_preserved": case["candidate"] == "stale_explanation_response_currentness",
        "history_non_promises": ["not currentness", "not repair", "not reliance proof"],
        "history_digest": digest({"case": case["id"], "parent": explanation["parent_bundle_digest"], "stale": case["candidate"] == "stale_explanation_response_currentness"}),
    }


def verdict_summary(case: dict[str, Any], explanation: dict[str, Any], event: dict[str, Any], capture: dict[str, Any], guard: dict[str, Any], followup: dict[str, Any], privacy: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    accepted = case["expected"] == "accepted"
    failure_reasons = [] if accepted else [FAILURE_REASONS[case["candidate"]]]
    return {
        "expected": case["expected"],
        "verdict_class": "accepted_scoped_response_event" if accepted else "refused_response_status_collapse",
        "failure_reasons": failure_reasons,
        "comprehension_claim_allowed": False,
        "consent_claim_allowed": False,
        "reliance_claim_allowed": False,
        "repair_claim_allowed": False,
        "compliance_claim_allowed": False,
        "legal_posture_claim_allowed": False,
        "all_recipient_read_claim_allowed": False,
        "user_identity_registry_allowed": False,
        "analytics_product_allowed": False,
        "parent_explanation_required": True,
        "flags": {
            "missing_parent_explanation_digest": not explanation["parent_bundle_digest_present"],
            "agent_action_claimed_as_user": event["agent_action_claimed_as_user"],
            "delivery_promoted": capture["notification_delivery_promoted"],
            "scroll_or_focus_promoted": capture["scroll_or_focus_promoted"],
            "localized_scope_widened": capture["localized_scope_widened"],
            "unbounded_retention": privacy["unbounded_retention_claimed"],
            "reidentification_risk": privacy["analytics_reidentification_risk"],
            "stale_response_currentness": guard["currentness_claimed_from_response"],
            "undo_missing": followup["final_action_requires_undo"] and not followup["undo_available"],
        },
        "non_promises": NON_PROMOTION,
    }


def build_case(index: int, plan: dict[str, Any]) -> dict[str, Any]:
    explanation = explanation_input(plan)
    event = response_event(plan, explanation)
    capture = capture_context(plan)
    guard = interpretation_guard(plan)
    followup = followup_action(plan, guard)
    privacy = privacy_retention(plan, event)
    history = history_trace(plan, explanation)
    verdict = verdict_summary(plan, explanation, event, capture, guard, followup, privacy, history)
    row = {
        "index": index,
        "id": plan["id"],
        "candidate": plan["candidate"],
        "event_kind": plan["event_kind"],
        "surface": plan["surface"],
        "expected": plan["expected"],
        "explanation.input": explanation,
        "response.event": event,
        "capture.context": capture,
        "interpretation.guard": guard,
        "followup.action": followup,
        "privacy.retention": privacy,
        "history.trace": history,
        "verdict.summary": verdict,
    }
    row["row_digest"] = digest({label: row[label] for label in MEMBER_LABELS})
    return row


def build_bundle() -> dict[str, Any]:
    cases = [build_case(i, plan) for i, plan in enumerate(CASE_PLAN, start=1)]
    bundle: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "source_revision": REVISION,
        "member_labels": MEMBER_LABELS,
        "prior_explanation_bundle_digest": prior_f105_digest(),
        "bundle_common_helper_digest": file_digest(ROOT / "tools" / "harbor_bundle_common.py"),
        "executable_surface_registry_digest": file_digest(ROOT / "tools" / "harbor_executable_surface_registry.py"),
        "cases": cases,
        "audit_refactor_note": {
            "summary": "F106 adds response-event evidence and refactors landing-page executable-slice count checks to derive from the executable-surface registry.",
            "not_promoted": ["not a consent system", "not a reliance ledger", "not a user-identity registry", "not analytics product", "not final SlopOS datacube shape"],
        },
        "global": {
            "coverage_claim": "Covers representative response-event cases after explanation cards; not comprehension proof, consent receipt, reliance proof, repair proof, compliance workflow, or analytics product.",
            "non_promotion": NON_PROMOTION,
        },
    }
    bundle["bundle_digest"] = digest({key: bundle[key] for key in ["schema", "version", "source_revision", "member_labels", "prior_explanation_bundle_digest", "bundle_common_helper_digest", "executable_surface_registry_digest", "cases", "audit_refactor_note", "global"]})
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit Harbor user-response event bundle")
    parser.add_argument("--out", type=Path, default=ROOT / "fixtures" / "harbor-user-response-event-bundle-v0.json")
    args = parser.parse_args()
    bundle = build_bundle()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
