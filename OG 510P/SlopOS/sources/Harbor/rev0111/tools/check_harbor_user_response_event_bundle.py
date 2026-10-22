#!/usr/bin/env python3
"""Check Harbor user-response / reliance-event bundle v0."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from harbor_bundle_common import check_digest_string, digest, expect, file_digest, unguarded_confidence_phrases  # noqa: E402
import harbor_user_response_event_harness as harness  # noqa: E402


def check_case(case: dict[str, Any]) -> None:
    case_id = case["id"]
    candidate = case["candidate"]
    plan = next(plan for plan in harness.CASE_PLAN if plan["id"] == case_id)
    expected = plan["expected"]

    explanation = case["explanation.input"]
    event = case["response.event"]
    capture = case["capture.context"]
    guard = case["interpretation.guard"]
    followup = case["followup.action"]
    privacy = case["privacy.retention"]
    history = case["history.trace"]
    verdict = case["verdict.summary"]

    expect(case["row_digest"] == digest({label: case[label] for label in harness.MEMBER_LABELS}), f"{case_id}: row digest drift")
    if explanation["parent_bundle_digest_present"]:
        check_digest_string(explanation["parent_bundle_digest"], f"{case_id}: parent explanation digest malformed")
        check_digest_string(explanation["explanation_digest"], f"{case_id}: explanation digest malformed")
        expect(explanation["parent_bundle_digest"] == history["parent_explanation_bundle_digest"], f"{case_id}: parent digest mismatch")
    else:
        expect(explanation["parent_bundle_digest"] is None and explanation["explanation_digest"] is None, f"{case_id}: missing-parent case still carries digest")
        expect(history["parent_explanation_bundle_digest"] is None, f"{case_id}: missing-parent history drift")
    for path, label in [
        (event["event_digest"], "event"),
        (capture["capture_digest"], "capture"),
        (guard["guard_digest"], "guard"),
        (followup["followup_digest"], "followup"),
        (privacy["privacy_digest"], "privacy"),
        (history["history_digest"], "history"),
    ]:
        check_digest_string(path, f"{case_id}: {label} digest malformed")

    expect(case["event_kind"] == plan["event_kind"], f"{case_id}: event kind drift")
    expect(case["surface"] == plan["surface"], f"{case_id}: surface drift")
    expect(event["event_kind"] == plan["event_kind"], f"{case_id}: event payload kind drift")
    expect(capture["surface_kind"] == plan["surface"], f"{case_id}: capture surface drift")
    expect("not user comprehension proof" in explanation["source_non_promises"], f"{case_id}: explanation non-promise missing")
    expect("response event is not comprehension" in guard["guard_language"], f"{case_id}: guard language missing")
    expect(verdict["comprehension_claim_allowed"] is False, f"{case_id}: comprehension claim cannot be allowed")
    expect(verdict["consent_claim_allowed"] is False, f"{case_id}: consent claim cannot be allowed")
    expect(verdict["reliance_claim_allowed"] is False, f"{case_id}: reliance claim cannot be allowed")
    expect(verdict["repair_claim_allowed"] is False, f"{case_id}: repair claim cannot be allowed")
    expect(verdict["compliance_claim_allowed"] is False, f"{case_id}: compliance claim cannot be allowed")
    expect(verdict["legal_posture_claim_allowed"] is False, f"{case_id}: legal posture cannot be allowed")
    expect(verdict["all_recipient_read_claim_allowed"] is False, f"{case_id}: all-recipient read cannot be allowed")
    expect(verdict["user_identity_registry_allowed"] is False, f"{case_id}: identity registry cannot be allowed")
    expect(verdict["analytics_product_allowed"] is False, f"{case_id}: analytics product cannot be allowed")
    for non_promise in harness.NON_PROMOTION:
        expect(non_promise in verdict["non_promises"], f"{case_id}: missing non-promise {non_promise}")

    if expected == "accepted":
        expect(verdict["expected"] == "accepted", f"{case_id}: accepted expectation drift")
        expect(verdict["verdict_class"] == "accepted_scoped_response_event", f"{case_id}: accepted verdict class drift")
        expect(verdict["failure_reasons"] == [], f"{case_id}: accepted case has failure reasons")
        expect(explanation["parent_bundle_digest_present"] is True, f"{case_id}: accepted case missing parent explanation digest")
        expect(privacy["personal_data_minimized"] is True, f"{case_id}: accepted case lacks minimization")
        expect(privacy["retention_has_expiry"] is True, f"{case_id}: accepted case lacks retention expiry")
        expect(privacy["raw_person_identifier_stored"] is False, f"{case_id}: accepted case stores direct identifier")
        expect(event["agent_action_claimed_as_user"] is False, f"{case_id}: accepted case claims agent as user")
        expect(capture["scope_map_carried"] is True, f"{case_id}: accepted case lacks scope map")
        expect(capture["undo_available"] is True, f"{case_id}: accepted case lacks undo/escape")
        expect(not any(guard[key] for key in ["comprehension_claimed", "consent_claimed", "reliance_claimed", "repair_claimed", "compliance_claimed", "all_recipient_read_claimed", "permission_claimed_from_request", "recheck_passed_claimed", "currentness_claimed_from_response"]), f"{case_id}: accepted case promotes response signal")
    else:
        expect(verdict["expected"] == "rejected", f"{case_id}: rejected expectation drift")
        expect(verdict["verdict_class"] == "refused_response_status_collapse", f"{case_id}: rejected verdict class drift")
        expect(verdict["failure_reasons"] == [harness.FAILURE_REASONS[candidate]], f"{case_id}: failure reason drift")

    flags = verdict["flags"]
    if candidate == "inspect_opened_evidence_panel":
        expect("Evidence panel opened" in event["event_text"], f"{case_id}: inspect wording missing")
    elif candidate == "recheck_requested_not_completed":
        expect("not yet been observed" in event["event_text"] and followup["recheck_result_observed"] is False, f"{case_id}: recheck pending posture drift")
    elif candidate == "export_scope_note_not_reliance":
        expect(followup["third_party_reliance_recorded"] is False and "include parent digest" in followup["allowed_followups"], f"{case_id}: export reliance posture drift")
    elif candidate == "dismiss_card_without_acceptance":
        expect("preserve warning history" in followup["allowed_followups"], f"{case_id}: dismiss history posture missing")
    elif candidate == "appeal_started_not_granted":
        expect(followup["appeal_outcome_recorded"] is False and "wait for outcome" in followup["allowed_followups"], f"{case_id}: appeal outcome posture drift")
    elif candidate == "share_link_copied_not_external_read":
        expect(guard["all_recipient_read_claimed"] is False and "recipient delivery and read state remain unknown" in event["event_text"], f"{case_id}: share read posture drift")
    elif candidate == "acknowledge_receipt_not_understanding":
        expect(guard["comprehension_claimed"] is False and privacy["consent_record_created"] is False, f"{case_id}: acknowledgement upgraded")
    elif candidate == "localized_ack_bound_to_locale":
        expect(capture["localized_scope_widened"] is False, f"{case_id}: localization scope drift")
    elif candidate == "sealed_detail_request_denied_logged":
        expect(guard["permission_claimed_from_request"] is False and "deny sealed detail by default" in followup["allowed_followups"], f"{case_id}: sealed request permission drift")
    elif candidate == "agent_summary_followup_carries_caveats":
        expect(event["generated_by_agent"] is False and "preserve parent digest" in followup["allowed_followups"], f"{case_id}: agent summary caveat posture drift")
    elif candidate == "problem_detail_automated_retry_not_human_reliance":
        expect(guard["reliance_claimed"] is False and followup["repair_result_observed"] is False, f"{case_id}: automated retry overclaim")
    elif candidate == "click_as_comprehension":
        expect(guard["comprehension_claimed"] is True, f"{case_id}: comprehension flag absent")
    elif candidate == "checkbox_as_consent_without_terms":
        expect(guard["consent_claimed"] is True and privacy["consent_record_created"] is True, f"{case_id}: consent flag absent")
    elif candidate == "export_as_thirdparty_reliance":
        expect(guard["reliance_claimed"] is True and followup["third_party_reliance_recorded"] is True, f"{case_id}: reliance flag absent")
    elif candidate == "notification_delivery_as_user_action":
        expect(flags["delivery_promoted"] is True, f"{case_id}: delivery promotion flag absent")
    elif candidate == "response_without_parent_explanation_digest":
        expect(flags["missing_parent_explanation_digest"] is True, f"{case_id}: missing parent flag absent")
    elif candidate == "aggregated_metrics_identify_person":
        expect(flags["reidentification_risk"] is True and privacy["raw_person_identifier_stored"] is True, f"{case_id}: analytics privacy flag absent")
    elif candidate == "retention_forever_by_default":
        expect(flags["unbounded_retention"] is True and privacy["retention_has_expiry"] is False, f"{case_id}: retention flag absent")


def check_bundle(bundle: dict[str, Any]) -> None:
    expect(bundle.get("schema") == harness.SCHEMA, "Schema drift")
    expect(bundle.get("version") == harness.VERSION, "Version drift")
    expect(bundle.get("source_revision") == harness.REVISION, "Source revision drift")
    expect(bundle.get("member_labels") == harness.MEMBER_LABELS, "Member label drift")
    expect(bundle.get("prior_explanation_bundle_digest") == harness.prior_f105_digest(), "Prior F105 digest drift")
    expect(bundle.get("bundle_common_helper_digest") == file_digest(ROOT / "tools" / "harbor_bundle_common.py"), "Bundle helper digest drift")
    expect(bundle.get("executable_surface_registry_digest") == file_digest(ROOT / "tools" / "harbor_executable_surface_registry.py"), "Executable registry digest drift")
    expected_digest = digest({key: bundle[key] for key in ["schema", "version", "source_revision", "member_labels", "prior_explanation_bundle_digest", "bundle_common_helper_digest", "executable_surface_registry_digest", "cases", "audit_refactor_note", "global"]})
    expect(bundle.get("bundle_digest") == expected_digest, "Bundle digest drift")
    check_digest_string(bundle["bundle_digest"], "Bundle digest malformed")
    expect(not unguarded_confidence_phrases(bundle), "Bundle contains unguarded confidence/status phrase")

    cases = bundle.get("cases", [])
    expect(len(cases) == len(harness.CASE_PLAN), "Case count drift")
    expect([case["index"] for case in cases] == list(range(1, len(cases) + 1)), "Case indexes not gapless")
    expect([case["id"] for case in cases] == [plan["id"] for plan in harness.CASE_PLAN], "Case id order drift")
    expect([case["candidate"] for case in cases] == [plan["candidate"] for plan in harness.CASE_PLAN], "Candidate order drift")
    for case in cases:
        check_case(case)
    expected_cases = [case for case in cases if case["expected"] == "accepted"]
    rejected_cases = [case for case in cases if case["expected"] == "rejected"]
    expect(len(expected_cases) == 14, "Accepted case count drift")
    expect(len(rejected_cases) == 20, "Rejected case count drift")
    global_ = bundle.get("global", {})
    for non_promise in harness.NON_PROMOTION:
        expect(non_promise in global_.get("non_promotion", []), f"Global non-promotion missing: {non_promise}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Harbor user-response event bundle")
    parser.add_argument("fixture", nargs="?", type=Path, default=ROOT / "fixtures" / "harbor-user-response-event-bundle-v0.json")
    args = parser.parse_args()
    check_bundle(json.loads(args.fixture.read_text(encoding="utf-8")))
    print("Harbor user-response event bundle check passed")


if __name__ == "__main__":
    main()
