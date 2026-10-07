#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

STATUS_ENVELOPE_ID = "worked-example-successor-status-envelope-v1"
LINEAGE_NOTICE_ID = "worked-example-successor-lineage-notice-v1"
CLOSURE_VERDICT_ID = "worked-example-publication-closure-verdict-v1"
CLOSURE_LEDGER_ID = "worked-example-release-closure-ledger-v1"
CONTINUITY_VERDICT_ID = "worked-example-successor-continuity-verdict-v1"
DERIVATION_GRAPH_ID = "worked-example-successor-derivation-graph-v1"
CLAIM_SUPPORT_MAP_ID = "worked-example-successor-claim-support-map-v1"
CITATION_MAP_ID = "worked-example-successor-citation-map-v1"
CHALLENGE_STOP_PROFILES_ID = "worked-example-successor-challenge-stop-profiles-v1"
CHALLENGE_ROUTES_ID = "worked-example-successor-challenge-routes-v1"
CHALLENGE_BRANCHES_ID = "worked-example-successor-challenge-branches-v1"
CHALLENGE_COVERAGE_ID = "worked-example-successor-challenge-coverage-v1"
CHALLENGE_SURFACE_HOOKS_ID = "worked-example-successor-challenge-surface-hooks-v1"
QUOTE_MAP_ID = "worked-example-successor-quote-map-v1"
CLAUSE_PACK_ID = "worked-example-successor-clause-pack-v1"
SENTENCE_LOCKS_ID = "worked-example-successor-sentence-locks-v1"
RELEASE_SPINE_ID = "worked-example-release-spine-v1"
RELEASE_STAGE_WALKTHROUGH_ID = "worked-example-release-stage-walkthrough-v1"
NORMAL_FORM_ID = "worked-example-successor-normal-form-v1"
ANSWER_AUDIT_TRAILS_ID = "worked-example-successor-challenge-answer-audit-trails-v1"

RELEASE_STAGE_ORDER_FIELDS = ["stage", "question", "artifact", "companion_artifact", "object_id", "release_stage_vocabulary_mode", "stop_when", "widen_only_if", "why"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(name: str):
    with open(ART / name, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_candidate_paths(binding: str):
    return re.findall(r"[A-Za-z0-9_./-]+\.json", binding or "")


def resolve_required_outputs(required_outputs, manifest_paths, inventory_paths):
    provided_publication_outputs = []
    role_bindings = []
    missing_roles = []
    for entry in required_outputs:
        role = entry.get("role")
        binding = entry.get("binding")
        candidates = extract_candidate_paths(binding)
        bound = [path for path in candidates if path in manifest_paths and path in inventory_paths]
        if bound:
            provided_publication_outputs.append({"role": role, "path": bound[0]})
        else:
            missing_roles.append(role)
        role_bindings.append({
            "role": role,
            "required_binding": binding,
            "candidate_paths": candidates,
            "bound_artifacts": bound,
        })
    return provided_publication_outputs, role_bindings, missing_roles


def ensure_inventory_entry(artifact_inventory, path: str, role: str, consumed_by):
    for group in artifact_inventory.get("groups", []):
        for entry in group.get("entries", []):
            if entry.get("path") == path:
                entry["role"] = role
                entry["consumed_by"] = consumed_by
                return
    target_group = next((g for g in artifact_inventory.get("groups", []) if g.get("group") == "guard_and_compare_adjuncts"), None)
    if target_group is not None:
        target_group.setdefault("entries", []).append({"path": path, "role": role, "consumed_by": consumed_by})
        target_group["entries"] = sorted(target_group["entries"], key=lambda x: x["path"])


def main() -> None:
    compare_profile = load("example_compare_profile.json")
    compare_walkthrough = load("example_compare_walkthrough.json")
    change_control = load("example_change_control.json")
    release_obligation_profile = load("example_release_obligation_profile.json")
    support_manifest = load("support_manifest.json")
    artifact_inventory = load("example_artifact_inventory.json")

    report = {
        "report_id": "worked-example-compare-report-v1",
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "support_manifest_id": support_manifest["manifest_id"],
        "artifact_inventory_id": artifact_inventory["inventory_id"],
        "note_version": artifact_inventory.get("note_version"),
        "classification": compare_walkthrough["classification_result"],
        "continuity_decision": compare_walkthrough.get("continuity_decision"),
        "required_action": compare_walkthrough["required_action"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "required_publication_roles": compare_walkthrough.get("required_publication_roles", []),
        "publication_closure_verdict_id": CLOSURE_VERDICT_ID,
        "successor_lineage_notice_id": LINEAGE_NOTICE_ID,
        "successor_derivation_graph_id": DERIVATION_GRAPH_ID,
        "successor_claim_support_map_id": CLAIM_SUPPORT_MAP_ID,
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_sentence_locks_id": SENTENCE_LOCKS_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "successor_normal_form_id": NORMAL_FORM_ID,
        "successor_challenge_answer_audit_trails_id": ANSWER_AUDIT_TRAILS_ID,
        "user_fast_diff": {
            "base": compare_walkthrough["base_fields"]["user_fast_diff"],
            "successor": compare_walkthrough["successor_fields"]["user_fast_diff"],
            "first_fields": compare_profile["diff_views"]["user_fast_diff"],
            "first_alarm": compare_walkthrough["user_first_alarm"],
        },
        "auditor_fast_diff": {
            "base": compare_walkthrough["base_fields"]["auditor_fast_diff"],
            "successor": compare_walkthrough["successor_fields"]["auditor_fast_diff"],
            "first_fields": compare_profile["diff_views"]["auditor_fast_diff"],
            "first_alarm": compare_walkthrough["auditor_first_alarm"],
            "guard_reference": change_control["interface_guard"],
        },
        "stable_guard_fields": compare_walkthrough["successor_fields"]["auditor_fast_diff"],
        "observed_diffs": compare_walkthrough["observed_diffs"],
        "replay_scope": {
            "changed_line_items": compare_walkthrough.get("changed_line_items", []),
            "replay_plan_ids": compare_walkthrough.get("replay_plan_ids", []),
        },
        "note": "Maintenance compare report generated from the compare profile, compare walk-through, and change-control adjunct. It is not a new receipt or UVI primitive.",
    }
    out = ART / "example_compare_report.json"
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")
    digest = sha256_bytes(payload.encode("utf-8"))

    continuity_verdict = {
        "verdict_id": CONTINUITY_VERDICT_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "release_action_matrix_id": compare_walkthrough["release_action_matrix_id"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "publication_closure_verdict_id": CLOSURE_VERDICT_ID,
        "successor_lineage_notice_id": LINEAGE_NOTICE_ID,
        "successor_derivation_graph_id": DERIVATION_GRAPH_ID,
        "successor_claim_support_map_id": CLAIM_SUPPORT_MAP_ID,
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_sentence_locks_id": SENTENCE_LOCKS_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "note_version": artifact_inventory.get("note_version"),
        "classification": compare_walkthrough["classification_result"],
        "matched_rule_ids": compare_walkthrough.get("matched_rule_ids", []),
        "continuity_decision": compare_walkthrough.get("continuity_decision"),
        "continuity_basis": compare_walkthrough.get("continuity_basis", []),
        "changed_line_items": compare_walkthrough.get("changed_line_items", []),
        "replay_plan_ids": compare_walkthrough.get("replay_plan_ids", []),
        "stable_guard_fields": change_control["interface_guard"],
        "budget_delta_summary": {
            "base_fallback_summary_bits": compare_walkthrough["base_fields"]["user_fast_diff"]["budget_value"],
            "successor_fallback_summary_bits": compare_walkthrough["successor_fields"]["user_fast_diff"]["budget_value"],
            "base_total_summary_bits_per_lookup": compare_walkthrough["base_fields"]["user_fast_diff"]["total_summary_bits_per_lookup"],
            "successor_total_summary_bits_per_lookup": compare_walkthrough["successor_fields"]["user_fast_diff"]["total_summary_bits_per_lookup"],
        },
        "successor_receipt_digest": compare_walkthrough["successor_fields"]["user_fast_diff"]["receipt_digest"],
        "required_publication_step": compare_walkthrough["required_action"],
        "required_publication_roles": compare_walkthrough.get("required_publication_roles", []),
        "expected_continuity_status": next((entry.get("continuity_status") for entry in release_obligation_profile.get("classes", []) if entry.get("action_class") == compare_walkthrough.get("classification_result")), None),
        "note": "Derived base-to-successor continuity verdict adjunct for one concrete release comparison. It packages the classification result, replay scope, and continuity decision without introducing a new receipt primitive.",
    }
    verdict_out = ART / "example_successor_continuity_verdict.json"
    verdict_payload = json.dumps(continuity_verdict, indent=2, sort_keys=True) + "\n"
    verdict_out.write_text(verdict_payload, encoding="utf-8")
    verdict_digest = sha256_bytes(verdict_payload.encode("utf-8"))

    manifest_paths = {entry.get("path"): entry.get("sha256") for entry in support_manifest.get("files", [])}
    manifest_paths.update({"example_compare_report.json": digest, "example_successor_continuity_verdict.json": verdict_digest})
    inventory_paths = {entry.get("path") for group in artifact_inventory.get("groups", []) for entry in group.get("entries", [])}
    inventory_paths.add("example_release_closure_ledger.json")
    inventory_paths.add("example_publication_closure_verdict.json")
    inventory_paths.add("example_successor_lineage_notice.json")
    inventory_paths.add("example_successor_claim_support_map.json")
    inventory_paths.add("example_successor_citation_map.json")
    inventory_paths.add("example_successor_challenge_stop_profiles.json")
    inventory_paths.add("example_successor_challenge_routes.json")
    inventory_paths.add("example_successor_challenge_branches.json")
    inventory_paths.add("example_successor_challenge_coverage.json")
    inventory_paths.add("example_successor_challenge_surface_hooks.json")
    inventory_paths.add("example_successor_quote_map.json")
    inventory_paths.add("example_release_spine.json")
    inventory_paths.add("example_successor_normal_form.json")
    inventory_paths.add("example_successor_sentence_locks.json")
    obligation_classes = {entry.get("action_class"): entry for entry in release_obligation_profile.get("classes", [])}
    winning_class = compare_walkthrough.get("classification_result")
    required_outputs = obligation_classes.get(winning_class, {}).get("minimum_output_roles", [])
    provided_publication_outputs, role_bindings, missing_roles = resolve_required_outputs(required_outputs, manifest_paths, inventory_paths)

    closure_ledger = {
        "closure_ledger_id": CLOSURE_LEDGER_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "support_manifest_id": support_manifest.get("manifest_id"),
        "artifact_inventory_id": artifact_inventory.get("inventory_id"),
        "note_version": artifact_inventory.get("note_version"),
        "classification": winning_class,
        "matched_rule_ids": compare_walkthrough.get("matched_rule_ids", []),
        "role_row_fields": ["role", "required_binding", "candidate_paths", "bound_artifacts", "status", "why"],
        "required_publication_roles": [entry.get("role") for entry in required_outputs],
        "role_rows": [
            {
                "role": entry.get("role"),
                "required_binding": entry.get("required_binding"),
                "candidate_paths": entry.get("candidate_paths", []),
                "bound_artifacts": entry.get("bound_artifacts", []),
                "status": "satisfied" if entry.get("bound_artifacts") else "missing",
                "why": "At least one allowed shipped artifact is bound for this required publication role." if entry.get("bound_artifacts") else "No allowed shipped artifact from the obligation profile is present for this required publication role."
            }
            for entry in role_bindings
        ],
        "missing_publication_roles": missing_roles,
        "completeness": "complete" if not missing_roles else "incomplete",
        "note": "Derived role-by-role bridge from the winning obligation class to the concrete shipped package. It owns row satisfaction, not the final compressed closure token.",
    }
    closure_ledger_out = ART / "example_release_closure_ledger.json"
    closure_ledger_payload = json.dumps(closure_ledger, indent=2, sort_keys=True) + "\n"
    closure_ledger_out.write_text(closure_ledger_payload, encoding="utf-8")
    closure_ledger_digest = sha256_bytes(closure_ledger_payload.encode("utf-8"))

    closure_verdict = {
        "closure_verdict_id": CLOSURE_VERDICT_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "successor_lineage_notice_id": LINEAGE_NOTICE_ID,
        "successor_derivation_graph_id": DERIVATION_GRAPH_ID,
        "successor_claim_support_map_id": CLAIM_SUPPORT_MAP_ID,
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_sentence_locks_id": SENTENCE_LOCKS_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "support_manifest_id": support_manifest.get("manifest_id"),
        "artifact_inventory_id": artifact_inventory.get("inventory_id"),
        "note_version": artifact_inventory.get("note_version"),
        "classification": winning_class,
        "matched_rule_ids": compare_walkthrough.get("matched_rule_ids", []),
        "required_publication_roles": [entry.get("role") for entry in required_outputs],
        "provided_publication_outputs": provided_publication_outputs,
        "role_bindings": role_bindings,
        "missing_publication_roles": missing_roles,
        "closure_status": "complete" if not missing_roles else "incomplete",
        "note": "Derived successor-package closure verdict for one concrete release comparison. It compresses the release-closure ledger to a package-completeness token and bound output list without replacing the row-level role checks.",
    }
    closure_out = ART / "example_publication_closure_verdict.json"
    closure_payload = json.dumps(closure_verdict, indent=2, sort_keys=True) + "\n"
    closure_out.write_text(closure_payload, encoding="utf-8")
    closure_digest = sha256_bytes(closure_payload.encode("utf-8"))

    lineage_notice = {
        "notice_id": LINEAGE_NOTICE_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": STATUS_ENVELOPE_ID,
        "successor_derivation_graph_id": DERIVATION_GRAPH_ID,
        "successor_claim_support_map_id": CLAIM_SUPPORT_MAP_ID,
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_sentence_locks_id": SENTENCE_LOCKS_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "classification": winning_class,
        "continuity_decision": continuity_verdict.get("continuity_decision"),
        "closure_status": closure_verdict.get("closure_status"),
        "replay_scope": {
            "changed_line_items": compare_walkthrough.get("changed_line_items", []),
            "replay_plan_ids": compare_walkthrough.get("replay_plan_ids", []),
        },
        "public_status": "same_interface_replayed_surfaces_complete_package" if winning_class == "replay_changed_surfaces" and closure_verdict.get("closure_status") == "complete" else "see_linked_verdicts",
        "status_summary": "Successor remains on the same certified interface after replaying the changed fallback surfaces; required successor publication outputs are complete." if winning_class == "replay_changed_surfaces" and closure_verdict.get("closure_status") == "complete" else "See linked compare/continuity/closure verdicts.",
        "publication_roles_satisfied": closure_verdict.get("required_publication_roles", []),
        "reader_pointer_order": [
            {"path": "example_successor_status_envelope.json", "why": "narrow public-status token for this concrete release pair"},
            {"path": "example_compare_report.json", "why": "numeric diff summary and first-alarm fields"},
            {"path": "example_successor_continuity_verdict.json", "why": "continuity basis and replay scope"},
            {"path": "example_release_closure_ledger.json", "why": "role-by-role package-closure bindings for the winning obligation class"},
            {"path": "example_publication_closure_verdict.json", "why": "package-completeness check"},
            {"path": "example_successor_derivation_graph.json", "why": "dependency order for the maintenance verdicts"},
            {"path": "example_release_spine.json", "why": "stable stage map for successor maintenance"},
            {"path": "example_release_stage_walkthrough.json", "why": "concrete stage-by-stage walk for the maintained successor comparison"},
            {"path": "example_successor_normal_form.json", "why": "downstream sentence-normalization suffix for one successor comparison"},
            {"path": "example_successor_sentence_locks.json", "why": "pair-anchored reuse policy and visible-provenance modes for the shipped status and compact-diff sentences"},
            {"path": "example_successor_claim_support_map.json", "why": "claim-by-claim support bindings for the public status sentence"},
            {"path": "example_successor_citation_map.json", "why": "smallest sufficient citations for downstream notes"},
            {"path": "example_successor_challenge_routes.json", "why": "audience-keyed start-here and escalate-here routes for common downstream questions"},
            {"path": "example_successor_challenge_stop_profiles.json", "why": "question-keyed semantic pieces and approved terminal fields for those downstream questions"},
            {"path": "example_successor_challenge_branches.json", "why": "piece-keyed escalation branches once one semantic piece of a route is actually contested"},
            {"path": "example_successor_challenge_coverage.json", "why": "sentence-family coverage certificate linking audience obligations and support-only hooks"},
            {"path": "example_successor_challenge_surface_hooks.json", "why": "piece-to-segment surface-hook ledger showing exactly where each covered piece appears on the emitted sentence surface"},
            {"path": "example_successor_quote_map.json", "why": "exact fields to quote once the downstream citation target is known"},
        ],
        "note": "Derived outward-facing status wrapper for one concrete base-to-successor comparison. It compresses the companion status envelope into one public sentence and pointer order without introducing a new receipt primitive.",
    }
    lineage_out = ART / "example_successor_lineage_notice.json"
    lineage_payload = json.dumps(lineage_notice, indent=2, sort_keys=True) + "\n"
    lineage_out.write_text(lineage_payload, encoding="utf-8")
    lineage_digest = sha256_bytes(lineage_payload.encode("utf-8"))

    manifest_paths["example_successor_lineage_notice.json"] = lineage_digest
    provided_publication_outputs, role_bindings, missing_roles = resolve_required_outputs(required_outputs, manifest_paths, inventory_paths)
    closure_ledger["role_rows"] = [
        {
            "role": entry.get("role"),
            "required_binding": entry.get("required_binding"),
            "candidate_paths": entry.get("candidate_paths", []),
            "bound_artifacts": entry.get("bound_artifacts", []),
            "status": "satisfied" if entry.get("bound_artifacts") else "missing",
            "why": "At least one allowed shipped artifact is bound for this required publication role." if entry.get("bound_artifacts") else "No allowed shipped artifact from the obligation profile is present for this required publication role."
        }
        for entry in role_bindings
    ]
    closure_ledger["missing_publication_roles"] = missing_roles
    closure_ledger["completeness"] = "complete" if not missing_roles else "incomplete"
    closure_ledger_payload = json.dumps(closure_ledger, indent=2, sort_keys=True) + "\n"
    closure_ledger_out.write_text(closure_ledger_payload, encoding="utf-8")
    closure_ledger_digest = sha256_bytes(closure_ledger_payload.encode("utf-8"))

    closure_verdict["provided_publication_outputs"] = provided_publication_outputs
    closure_verdict["role_bindings"] = role_bindings
    closure_verdict["missing_publication_roles"] = missing_roles
    closure_verdict["closure_status"] = "complete" if not missing_roles else "incomplete"
    closure_payload = json.dumps(closure_verdict, indent=2, sort_keys=True) + "\n"
    closure_out.write_text(closure_payload, encoding="utf-8")
    closure_digest = sha256_bytes(closure_payload.encode("utf-8"))

    status_envelope = {
        "status_envelope_id": STATUS_ENVELOPE_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "classification": winning_class,
        "continuity_decision": continuity_verdict.get("continuity_decision"),
        "closure_status": closure_verdict.get("closure_status"),
        "public_status": "same_interface_replayed_surfaces_complete_package" if winning_class == "replay_changed_surfaces" and closure_verdict.get("closure_status") == "complete" else "see_linked_verdicts",
        "summary_basis": [
            {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why": "Owns the continuity token compressed by the public wrapper."},
            {"path": "example_publication_closure_verdict.json", "field": "closure_status", "why": "Owns the package-completeness token compressed by the public wrapper."},
        ],
        "note": "Derived narrow summary-stage status envelope for one concrete base-to-successor comparison. It owns the release-pair anchor and the public-status token that the outward-facing lineage notice compresses, without replacing the narrower continuity or closure owners.",
    }
    status_out = ART / "example_successor_status_envelope.json"
    status_payload = json.dumps(status_envelope, indent=2, sort_keys=True) + "\n"
    status_out.write_text(status_payload, encoding="utf-8")
    status_digest = sha256_bytes(status_payload.encode("utf-8"))

    lineage_notice["closure_status"] = closure_verdict.get("closure_status")
    lineage_notice["publication_roles_satisfied"] = [entry.get("role") for entry in closure_verdict.get("provided_publication_outputs", [])]
    lineage_notice["public_status"] = status_envelope.get("public_status")
    lineage_notice["status_summary"] = "Successor remains on the same certified interface after replaying the changed fallback surfaces; required successor publication outputs are complete." if winning_class == "replay_changed_surfaces" and closure_verdict.get("closure_status") == "complete" else "See linked compare/continuity/closure verdicts."
    lineage_payload = json.dumps(lineage_notice, indent=2, sort_keys=True) + "\n"
    lineage_out.write_text(lineage_payload, encoding="utf-8")
    lineage_digest = sha256_bytes(lineage_payload.encode("utf-8"))

    derivation_graph = {
        "graph_id": DERIVATION_GRAPH_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_claim_support_map_id": CLAIM_SUPPORT_MAP_ID,
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "topological_order": [
            "example_compare_report.json",
            "example_verifier_report.json",
            "example_release_obligation_profile.json",
            "example_release_closure_ledger.json",
            "example_successor_continuity_verdict.json",
            "example_publication_closure_verdict.json",
            "example_successor_status_envelope.json",
            "example_successor_lineage_notice.json",
            "example_successor_claim_support_map.json",
            "example_successor_citation_map.json",
            "example_successor_challenge_stop_profiles.json",
            "example_successor_challenge_routes.json",
            "example_successor_challenge_branches.json",
            "example_successor_challenge_coverage.json",
            "example_successor_challenge_surface_hooks.json",
            "example_successor_quote_map.json",
            "example_successor_clause_pack.json",
            "example_release_spine.json",
            "example_release_stage_walkthrough.json",
            "example_successor_sentence_locks.json",
            "example_successor_normal_form.json",
        ],
        "nodes": [
            {"path": "example_compare_report.json", "kind": "diff_summary", "object_id": report["report_id"]},
            {"path": "example_verifier_report.json", "kind": "replay_verdict", "object_id": "worked-example-verifier-report-v1"},
            {"path": "example_release_obligation_profile.json", "kind": "publication_policy", "object_id": compare_walkthrough.get("release_obligation_profile_id")},
            {"path": "example_release_closure_ledger.json", "kind": "closure_role_ledger", "object_id": CLOSURE_LEDGER_ID},
            {"path": "example_successor_continuity_verdict.json", "kind": "continuity_verdict", "object_id": continuity_verdict["verdict_id"]},
            {"path": "example_publication_closure_verdict.json", "kind": "package_closure_verdict", "object_id": closure_verdict["closure_verdict_id"]},
            {"path": "example_successor_status_envelope.json", "kind": "status_envelope", "object_id": status_envelope["status_envelope_id"]},
            {"path": "example_successor_lineage_notice.json", "kind": "public_status_wrapper", "object_id": lineage_notice["notice_id"]},
            {"path": "example_successor_claim_support_map.json", "kind": "statement_support_map", "object_id": CLAIM_SUPPORT_MAP_ID},
            {"path": "example_successor_citation_map.json", "kind": "minimal_citation_map", "object_id": CITATION_MAP_ID},
            {"path": "example_successor_challenge_stop_profiles.json", "kind": "challenge_stop_profiles", "object_id": CHALLENGE_STOP_PROFILES_ID},
            {"path": "example_successor_challenge_routes.json", "kind": "audience_challenge_routes", "object_id": CHALLENGE_ROUTES_ID},
            {"path": "example_successor_challenge_branches.json", "kind": "piece_challenge_branches", "object_id": CHALLENGE_BRANCHES_ID},
            {"path": "example_successor_challenge_coverage.json", "kind": "sentence_family_coverage", "object_id": CHALLENGE_COVERAGE_ID},
            {"path": "example_successor_challenge_surface_hooks.json", "kind": "sentence_surface_hooks", "object_id": CHALLENGE_SURFACE_HOOKS_ID},
            {"path": "example_successor_quote_map.json", "kind": "exact_quote_map", "object_id": QUOTE_MAP_ID},
            {"path": "example_successor_clause_pack.json", "kind": "canonical_clause_pack", "object_id": CLAUSE_PACK_ID},
            {"path": "example_release_spine.json", "kind": "release_stage_map", "object_id": RELEASE_SPINE_ID},
            {"path": "example_release_stage_walkthrough.json", "kind": "release_stage_walkthrough", "object_id": RELEASE_STAGE_WALKTHROUGH_ID},
            {"path": "example_successor_sentence_locks.json", "kind": "sentence_lock_ledger", "object_id": SENTENCE_LOCKS_ID},
            {"path": "example_successor_normal_form.json", "kind": "downstream_normal_form", "object_id": NORMAL_FORM_ID},
        ],
        "edges": [
            {"from": "example_compare_report.json", "to": "example_successor_continuity_verdict.json", "why": "classification and replay scope feed the continuity decision"},
            {"from": "example_verifier_report.json", "to": "example_successor_continuity_verdict.json", "why": "replayed evidence backs the continuity claim"},
            {"from": "example_compare_report.json", "to": "example_release_closure_ledger.json", "why": "winning class and required-action context identify which obligation rows must be checked"},
            {"from": "example_release_obligation_profile.json", "to": "example_release_closure_ledger.json", "why": "obligation profile supplies the required publication roles and allowed artifact candidates"},
            {"from": "example_release_closure_ledger.json", "to": "example_publication_closure_verdict.json", "why": "closure verdict compresses the satisfied/missing role rows to one completion token"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_lineage_notice.json", "why": "lineage notice quotes the continuity decision and replay scope"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_status_envelope.json", "why": "status envelope binds the continuity token used by the public-status wrapper"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_status_envelope.json", "why": "status envelope binds the package-completeness token used by the public-status wrapper"},
            {"from": "example_successor_status_envelope.json", "to": "example_successor_lineage_notice.json", "why": "lineage notice compresses the narrow status envelope into outward-facing prose"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_lineage_notice.json", "why": "lineage notice quotes package-completeness status"},
            {"from": "example_compare_report.json", "to": "example_successor_lineage_notice.json", "why": "lineage notice points readers to the compact numeric diff summary"},
            {"from": "example_compare_report.json", "to": "example_successor_claim_support_map.json", "why": "claim map quotes the compact numeric diff and replay-trigger summary"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_claim_support_map.json", "why": "claim map binds interface-continuity and replay-scope claims to the narrower verdict"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_claim_support_map.json", "why": "claim map binds package-completeness claims to the closure verdict"},
            {"from": "example_successor_lineage_notice.json", "to": "example_successor_claim_support_map.json", "why": "claim map records the outward-facing sentence actually presented to readers"},
            {"from": "example_successor_derivation_graph.json", "to": "example_successor_claim_support_map.json", "why": "claim map cites the maintenance order that justifies its support chain"},
            {"from": "example_successor_lineage_notice.json", "to": "example_successor_citation_map.json", "why": "citation map names the smallest public-status wrapper to cite when a downstream note only needs the outward-facing answer"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_citation_map.json", "why": "citation map names the smallest package-completeness object to cite"},
            {"from": "example_successor_derivation_graph.json", "to": "example_successor_citation_map.json", "why": "citation map names the smallest maintenance-order object to cite"},
            {"from": "example_successor_claim_support_map.json", "to": "example_successor_citation_map.json", "why": "citation map names the smallest sentence-level support object to cite"},
            {"from": "example_compare_report.json", "to": "example_successor_citation_map.json", "why": "citation map names the smallest compact diff object to cite"},
            {"from": "example_successor_citation_map.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map imports the minimal start objects for each downstream question"},
            {"from": "example_successor_challenge_stop_profiles.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map imports the question-keyed stop profiles rather than redefining approved terminal fields inline"},
            {"from": "example_successor_claim_support_map.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map records when a referee should start one layer left of the public wrapper"},
            {"from": "example_release_closure_ledger.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map records row-level package-completeness entry points for referee review"},
            {"from": "example_successor_status_envelope.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map records the narrow public-status token entry path for auditor review"},
            {"from": "example_verifier_report.json", "to": "example_successor_challenge_routes.json", "why": "challenge-route map records replay-first escalation for auditor diff review"},
            {"from": "example_compare_report.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name the numeric diff stop fields for the compact-diff question family"},
            {"from": "example_verifier_report.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name replay recomputation as an approved stop field for auditor diff review"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name continuity-side terminal fields for status and changed-family questions"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name closure-side terminal fields for wrapper and token questions"},
            {"from": "example_release_closure_ledger.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name role-row stopping points for package-completeness questions"},
            {"from": "example_successor_status_envelope.json", "to": "example_successor_challenge_stop_profiles.json", "why": "challenge-stop profiles name the narrow public-status token owner for auditor review"},
            {"from": "example_successor_normal_form.json", "to": "example_successor_challenge_coverage.json", "why": "coverage certificate imports emitted sentence families, segment bindings, and terminal targets from the downstream normal form"},
            {"from": "example_successor_challenge_routes.json", "to": "example_successor_challenge_coverage.json", "why": "coverage certificate binds sentence families to concrete audience routes"},
            {"from": "example_successor_challenge_stop_profiles.json", "to": "example_successor_challenge_coverage.json", "why": "coverage certificate reuses the question-keyed semantic piece vocabulary"},
            {"from": "example_successor_challenge_branches.json", "to": "example_successor_challenge_coverage.json", "why": "coverage certificate binds each covered piece to its route-plus-piece escalation witnesses"},
            {"from": "example_successor_challenge_coverage.json", "to": "example_successor_challenge_surface_hooks.json", "why": "surface-hook ledger instantiates only the sentence-family/piece pairs the coverage certificate says count as surface-carried"},
            {"from": "example_successor_normal_form.json", "to": "example_successor_challenge_surface_hooks.json", "why": "surface-hook ledger imports the emitted segments and terminal-target keys from the downstream normal form"},
            {"from": "example_successor_challenge_stop_profiles.json", "to": "example_successor_challenge_surface_hooks.json", "why": "surface-hook ledger reuses the question-keyed piece vocabulary while keeping exact surface realization separate"},
            {"from": "example_successor_challenge_routes.json", "to": "example_successor_quote_map.json", "why": "quote map keeps its exact-field choices synchronized with the declared audience/question routes"},
            {"from": "example_successor_citation_map.json", "to": "example_successor_quote_map.json", "why": "quote map refines each minimal citation choice to the exact field(s) worth quoting"},
            {"from": "example_successor_lineage_notice.json", "to": "example_successor_quote_map.json", "why": "quote map points at the exact outward-facing sentence field when a later note wants to quote status text"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_quote_map.json", "why": "quote map points at the exact continuity token when a later note wants the narrower verdict field"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_quote_map.json", "why": "quote map points at the exact closure-status field when package completeness is the claim"},
            {"from": "example_successor_derivation_graph.json", "to": "example_successor_quote_map.json", "why": "quote map points at the declared maintenance-order field when dependency order is quoted"},
            {"from": "example_compare_report.json", "to": "example_successor_quote_map.json", "why": "quote map points at the compact diff fields when a later note wants numeric deltas rather than the wrapper sentence"},
            {"from": "example_successor_quote_map.json", "to": "example_successor_clause_pack.json", "why": "clause pack materializes the declared quote targets as short reusable downstream sentences"},
            {"from": "example_successor_lineage_notice.json", "to": "example_successor_clause_pack.json", "why": "clause pack reuses the checked outward-facing status sentence rather than inventing a new public wrapper"},
            {"from": "example_compare_report.json", "to": "example_successor_clause_pack.json", "why": "clause pack reuses the compact numeric diff sentence from the checked compare summary"},
            {"from": "example_compare_report.json", "to": "example_release_spine.json", "why": "release spine names diff as the first maintenance stage"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_release_spine.json", "why": "release spine names classification and replay scope as the second maintenance stage"},
            {"from": "example_release_obligation_profile.json", "to": "example_release_spine.json", "why": "release spine names publication duties as the third maintenance stage"},
            {"from": "example_release_closure_ledger.json", "to": "example_release_spine.json", "why": "release spine points at the role-row bridge inside the close-stage handoff"},
            {"from": "example_publication_closure_verdict.json", "to": "example_release_spine.json", "why": "release spine names package closure as a separate maintenance stage"},
            {"from": "example_successor_lineage_notice.json", "to": "example_release_spine.json", "why": "release spine names the outward-facing summary stage"},
            {"from": "example_successor_claim_support_map.json", "to": "example_release_spine.json", "why": "release spine names sentence-level support as a later stage rather than primary evidence"},
            {"from": "example_successor_citation_map.json", "to": "example_release_spine.json", "why": "release spine names citation choice as a downstream stage"},
            {"from": "example_successor_quote_map.json", "to": "example_release_spine.json", "why": "release spine names exact-field selection as a downstream stage"},
            {"from": "example_successor_clause_pack.json", "to": "example_release_spine.json", "why": "release spine names reusable clause text as the final downstream stage"},
            {"from": "example_release_spine.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough instantiates each spine contract with one concrete artifact path and ownership boundary"},
            {"from": "example_compare_report.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough binds the diff stage to the concrete compare-report cut"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough binds the classify stage to the concrete continuity-verdict cut"},
            {"from": "example_release_closure_ledger.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough names the role-row bridge used inside the close-stage handoff"},
            {"from": "example_publication_closure_verdict.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough binds the close stage to the concrete closure-verdict cut"},
            {"from": "example_successor_lineage_notice.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough binds the summarize stage to the outward-facing status wrapper"},
            {"from": "example_successor_clause_pack.json", "to": "example_release_stage_walkthrough.json", "why": "stage walkthrough binds the final clause stage to the reusable sentence layer"},
            {"from": "example_successor_lineage_notice.json", "to": "example_successor_normal_form.json", "why": "normal form owns the downstream summary/support/citation/quote/clause suffix"},
            {"from": "example_successor_claim_support_map.json", "to": "example_successor_normal_form.json", "why": "normal form names sentence-level support as a suffix stage rather than primary evidence"},
            {"from": "example_successor_citation_map.json", "to": "example_successor_normal_form.json", "why": "normal form names the smallest sufficient citation target for each clause family"},
            {"from": "example_successor_quote_map.json", "to": "example_successor_sentence_locks.json", "why": "sentence locks inherit the exact fields whose wording is being reused"},
            {"from": "example_successor_clause_pack.json", "to": "example_successor_sentence_locks.json", "why": "sentence locks apply to concrete reusable clause texts"},
            {"from": "example_compare_report.json", "to": "example_successor_sentence_locks.json", "why": "sentence locks are pair-anchored to the compare-report cut and its diff witness"},
            {"from": "example_successor_continuity_verdict.json", "to": "example_successor_sentence_locks.json", "why": "sentence locks inherit one class of terminal targets and object-cut witnesses"},
            {"from": "example_publication_closure_verdict.json", "to": "example_successor_sentence_locks.json", "why": "sentence locks inherit closure-side terminal targets and object-cut witnesses"},
            {"from": "example_successor_sentence_locks.json", "to": "example_successor_normal_form.json", "why": "normal form points at the separate sentence-lock ledger for reuse policy rather than re-owning it in theory"},
            {"from": "example_successor_quote_map.json", "to": "example_successor_normal_form.json", "why": "normal form names the exact field selected for each downstream sentence"},
            {"from": "example_successor_clause_pack.json", "to": "example_successor_normal_form.json", "why": "normal form ends in the reusable clause layer"},
            {"from": "example_release_spine.json", "to": "example_successor_normal_form.json", "why": "normal form is explicitly the downstream suffix of the broader release spine"},
        ],
        "note": "Derived maintenance DAG for one concrete successor comparison. It states the dependency order among compare, replay, continuity, obligation rows, closure, and public-status artifacts without making that order another receipt primitive.",
    }
    derivation_out = ART / "example_successor_derivation_graph.json"
    derivation_payload = json.dumps(derivation_graph, indent=2, sort_keys=True) + "\n"
    derivation_out.write_text(derivation_payload, encoding="utf-8")
    derivation_digest = sha256_bytes(derivation_payload.encode("utf-8"))

    claim_support_map = {
        "map_id": CLAIM_SUPPORT_MAP_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "claims": [
            {
                "claim_key": "same_certified_interface",
                "statement": "Successor remains on the same certified interface.",
                "status": "supported",
                "support": [
                    {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "expected": "same_certified_interface_replayed_surfaces"},
                    {"path": "example_compare_report.json", "field": "classification", "expected": winning_class},
                ],
            },
            {
                "claim_key": "replayed_fallback_contact_vector_slice",
                "statement": "Only the fallback contact/vector slice was replayed for the successor comparison.",
                "status": "supported",
                "support": [
                    {"path": "example_compare_report.json", "field": "replay_scope.changed_line_items", "expected": compare_walkthrough.get("changed_line_items", [])},
                    {"path": "example_successor_continuity_verdict.json", "field": "changed_line_items", "expected": continuity_verdict.get("changed_line_items", [])},
                ],
            },
            {
                "claim_key": "required_successor_outputs_complete",
                "statement": "The successor package ships the outputs required by the replay-changed-surfaces obligation class.",
                "status": "supported",
                "support": [
                    {"path": "example_publication_closure_verdict.json", "field": "closure_status", "expected": closure_verdict.get("closure_status")},
                    {"path": "example_publication_closure_verdict.json", "field": "required_publication_roles", "expected": closure_verdict.get("required_publication_roles", [])},
                ],
            },
            {
                "claim_key": "public_status_sentence_is_traceable",
                "statement": "The outward-facing status sentence is traceable to narrower maintenance verdicts in a declared order.",
                "status": "supported",
                "support": [
                    {"path": "example_successor_status_envelope.json", "field": "public_status", "expected": status_envelope.get("public_status")},
                    {"path": "example_successor_lineage_notice.json", "field": "status_summary", "expected": lineage_notice.get("status_summary")},
                    {"path": "example_successor_derivation_graph.json", "field": "topological_order", "expected": derivation_graph.get("topological_order", [])},
                ],
            },
        ],
        "successor_citation_map_id": CITATION_MAP_ID,
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "note": "Derived statement-to-evidence support map for one concrete successor comparison. It binds each outward-facing maintenance claim to the narrower artifacts and fields that justify it without turning those claims into new receipt primitives.",
    }
    claim_map_out = ART / "example_successor_claim_support_map.json"
    claim_map_payload = json.dumps(claim_support_map, indent=2, sort_keys=True) + "\n"
    claim_map_out.write_text(claim_map_payload, encoding="utf-8")
    claim_map_digest = sha256_bytes(claim_map_payload.encode("utf-8"))

    citation_map = {
        "citation_map_id": CITATION_MAP_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "successor_challenge_routes_id": CHALLENGE_ROUTES_ID,
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "queries": [
            {
                "question_key": "public_status_token",
                "when": "Need the narrow public-status token for this concrete release pair rather than the full outward-facing sentence.",
                "minimal_path": "example_successor_status_envelope.json",
            },
            {
                "question_key": "public_status_sentence",
                "when": "Need one outward-facing successor status sentence for a downstream note or release wrapper.",
                "minimal_path": "example_successor_lineage_notice.json",
            },
            {
                "question_key": "package_completeness",
                "when": "Need to show that the successor package shipped every output required by the winning obligation class.",
                "minimal_path": "example_publication_closure_verdict.json",
            },
            {
                "question_key": "maintenance_order",
                "when": "Need the dependency order among compare, replay, continuity, closure, and public-status artifacts.",
                "minimal_path": "example_successor_derivation_graph.json",
            },
            {
                "question_key": "sentence_level_support",
                "when": "Need clause-by-clause support bindings for the public successor status sentence.",
                "minimal_path": "example_successor_claim_support_map.json",
            },
            {
                "question_key": "compact_diff_summary",
                "when": "Need the compact numeric diff and replay trigger rather than the public wrapper.",
                "minimal_path": "example_compare_report.json",
            },
        ],
        "resolution_rule": "Cite the smallest object that directly answers the downstream question. Audience-specific starting points and escalation ladders live in the companion challenge-route map.",
        "note": "Derived minimal-citation map for one concrete successor comparison. It owns only the smallest sufficient citation target for each recurring downstream question; audience-specific start points and escalation order live in the companion challenge-route map.",
    }
    citation_map_out = ART / "example_successor_citation_map.json"
    citation_map_payload = json.dumps(citation_map, indent=2, sort_keys=True) + "\n"
    citation_map_out.write_text(citation_map_payload, encoding="utf-8")
    citation_map_digest = sha256_bytes(citation_map_payload.encode("utf-8"))

    challenge_stop_profiles = {
        "challenge_stop_profiles_id": CHALLENGE_STOP_PROFILES_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "stop_contract": {
            "profile_fields": ["stop_profile_key", "question_key", "semantic_pieces", "approved_stop_fields", "why"],
            "semantic_piece_fields": ["piece_key", "question", "why"],
            "approved_stop_field_fields": ["piece_key", "path", "field", "why"],
            "stop_profile_rule": "A stop profile names the semantic pieces carried by one question_key and the exact narrow fields where escalation may terminate for each piece.",
            "route_link_rule": "A companion audience-keyed challenge route may cite stop_profile_key but may not redefine approved_stop_fields inline.",
            "branch_link_rule": "A companion piece-keyed challenge-branch map may cite stop_profile_key and piece_key but may not invent new approved terminal fields.",
        },
        "profiles": [
            {
                "stop_profile_key": "public_status_sentence",
                "question_key": "public_status_sentence",
                "semantic_pieces": [
                    {"piece_key": "continuity_piece", "question": "Does the successor remain continuous with the base claim?", "why": "The wrapper sentence compresses a continuity decision."},
                    {"piece_key": "closure_piece", "question": "Did the successor ship the required publication outputs?", "why": "The wrapper sentence also compresses publication closure."},
                ],
                "approved_stop_fields": [
                    {"piece_key": "continuity_piece", "path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why": "This is the narrow continuity owner that the public wrapper compresses."},
                    {"piece_key": "closure_piece", "path": "example_publication_closure_verdict.json", "field": "closure_status", "why": "This is the narrow closure owner that the public wrapper compresses."},
                ],
                "why": "The public status sentence is a two-piece wrapper claim; do not stop at wrapper prose when one half is contested.",
            },
            {
                "stop_profile_key": "package_completeness",
                "question_key": "package_completeness",
                "semantic_pieces": [
                    {"piece_key": "role_rows_piece", "question": "Which required publication roles were actually satisfied?", "why": "Referee review often starts from the role-row bridge rather than the compressed closure token."},
                    {"piece_key": "closure_token_piece", "question": "What is the compressed package-closure status token?", "why": "Some later notes need only the narrow closure answer once the role rows are known."},
                ],
                "approved_stop_fields": [
                    {"piece_key": "role_rows_piece", "path": "example_release_closure_ledger.json", "field": "role_rows", "why": "This is the row-level bridge from obligation profile to closure verdict."},
                    {"piece_key": "closure_token_piece", "path": "example_publication_closure_verdict.json", "field": "closure_status", "why": "This is the compressed closure token that later papers may cite once the role rows are understood."},
                ],
                "why": "Package completeness has both a row-level and a compressed-token stopping point; the question decides which is enough.",
            },
            {
                "stop_profile_key": "public_status_token",
                "question_key": "public_status_token",
                "semantic_pieces": [
                    {"piece_key": "status_token_piece", "question": "What narrow public-status token was emitted?", "why": "The envelope owns the token itself."},
                    {"piece_key": "continuity_piece", "question": "Which continuity decision makes that token true?", "why": "A challenged token may force inspection of the continuity verdict it compresses."},
                    {"piece_key": "closure_piece", "question": "Which closure decision makes that token true?", "why": "A challenged token may also force inspection of publication closure."},
                ],
                "approved_stop_fields": [
                    {"piece_key": "status_token_piece", "path": "example_successor_status_envelope.json", "field": "public_status", "why": "The status envelope owns the narrow public-status token directly."},
                    {"piece_key": "continuity_piece", "path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why": "This is the continuity-side owner compressed into the public-status token."},
                    {"piece_key": "closure_piece", "path": "example_publication_closure_verdict.json", "field": "closure_status", "why": "This is the closure-side owner compressed into the public-status token."},
                ],
                "why": "Auditor review may stop at the token itself or continue to the narrower verdict owners if the token is challenged.",
            },
            {
                "stop_profile_key": "compact_diff_summary",
                "question_key": "compact_diff_summary",
                "semantic_pieces": [
                    {"piece_key": "diff_delta_piece", "question": "What numeric diff was observed across the release pair?", "why": "The compact diff sentence compresses compare-report deltas."},
                    {"piece_key": "recompute_piece", "question": "What recomputed replay totals support that diff if challenged?", "why": "Auditor review may escalate to the replay-facing recomputation object."},
                    {"piece_key": "changed_family_piece", "question": "Which line-item families actually changed?", "why": "The compact diff sentence also implies a narrow changed-family slice."},
                ],
                "approved_stop_fields": [
                    {"piece_key": "diff_delta_piece", "path": "example_compare_report.json", "field": "observed_diffs", "why": "This is the smallest numeric diff owner."},
                    {"piece_key": "recompute_piece", "path": "example_verifier_report.json", "field": "recomputed", "why": "This is the replay-facing recomputation witness for the numeric delta."},
                    {"piece_key": "changed_family_piece", "path": "example_successor_continuity_verdict.json", "field": "changed_line_items", "why": "This is the narrow changed-family owner used by downstream maintenance notes."},
                ],
                "why": "Compact diff questions split naturally into numeric delta, replay recomputation, and changed-family pieces.",
            },
        ],
        "resolution_rule": "Pick the stop profile keyed by question family and stop only at one of its approved_stop_fields for the contested semantic piece.",
        "note": "Derived question-keyed stop-profile map for one concrete successor comparison. It keeps semantic stopping points separate from audience-specific start paths and escalation order so later notes can cite one home for approved terminal fields.",
    }
    challenge_stop_profiles_out = ART / "example_successor_challenge_stop_profiles.json"
    challenge_stop_profiles_payload = json.dumps(challenge_stop_profiles, indent=2, sort_keys=True) + "\n"
    challenge_stop_profiles_out.write_text(challenge_stop_profiles_payload, encoding="utf-8")
    challenge_stop_profiles_digest = sha256_bytes(challenge_stop_profiles_payload.encode("utf-8"))

    challenge_routes = {
        "challenge_routes_id": CHALLENGE_ROUTES_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_stop_profiles_id": challenge_stop_profiles["challenge_stop_profiles_id"],
        "successor_challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "successor_quote_map_id": QUOTE_MAP_ID,
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "route_contract": {
            "audience_profile_fields": ["audience", "default_route_keys", "why"],
            "route_fields": ["route_key", "audience", "question_key", "minimal_path", "start_path", "escalate_if_challenged", "stop_profile_key", "why"],
            "minimal_start_rule": "minimal_path must agree with the companion citation map for the named question_key; start_path may equal it or may begin at a declared stricter audience-specific entry point.",
            "stop_profile_rule": "stop_profile_key must name the companion challenge-stop profile that owns the approved terminal fields for this question family.",
            "branch_rule": "Once one semantic piece is actually challenged, follow the companion branch map keyed by route_key and piece_key rather than treating the coarse escalate_if_challenged list as the final proof trace.",
        },
        "audience_profiles": [
            {"audience": "release_note", "default_route_keys": ["release_note_public_status_sentence", "release_note_compact_diff"], "why": "A release note starts from the smallest outward-facing public object unless challenged."},
            {"audience": "referee", "default_route_keys": ["referee_public_status_sentence", "referee_package_completeness"], "why": "A referee often starts one layer left of the public wrapper so clause-by-clause support is visible immediately."},
            {"audience": "auditor", "default_route_keys": ["auditor_public_status_token", "auditor_compact_diff"], "why": "An auditor starts at the narrow token or numeric diff object that can already be replayed or row-checked."},
        ],
        "routes": [
            {
                "route_key": "release_note_public_status_sentence",
                "audience": "release_note",
                "question_key": "public_status_sentence",
                "minimal_path": "example_successor_lineage_notice.json",
                "start_path": "example_successor_lineage_notice.json",
                "escalate_if_challenged": ["example_successor_claim_support_map.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json"],
                "stop_profile_key": "public_status_sentence",
                "why": "Start at the outward-facing sentence, then escalate leftward only if a reader disputes one half of the wrapper claim.",
            },
            {
                "route_key": "release_note_compact_diff",
                "audience": "release_note",
                "question_key": "compact_diff_summary",
                "minimal_path": "example_compare_report.json",
                "start_path": "example_compare_report.json",
                "escalate_if_challenged": ["example_successor_continuity_verdict.json"],
                "stop_profile_key": "compact_diff_summary",
                "why": "A compact diff wrapper may start from the compare report because that is already the smallest sufficient numeric object.",
            },
            {
                "route_key": "referee_public_status_sentence",
                "audience": "referee",
                "question_key": "public_status_sentence",
                "minimal_path": "example_successor_lineage_notice.json",
                "start_path": "example_successor_claim_support_map.json",
                "escalate_if_challenged": ["example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_successor_lineage_notice.json"],
                "stop_profile_key": "public_status_sentence",
                "why": "A referee route skips the public wrapper and starts at the sentence-support layer.",
            },
            {
                "route_key": "referee_package_completeness",
                "audience": "referee",
                "question_key": "package_completeness",
                "minimal_path": "example_publication_closure_verdict.json",
                "start_path": "example_release_closure_ledger.json",
                "escalate_if_challenged": ["example_publication_closure_verdict.json", "example_release_obligation_profile.json"],
                "stop_profile_key": "package_completeness",
                "why": "A referee asking about package completeness usually wants the satisfied role rows before the compressed token.",
            },
            {
                "route_key": "auditor_public_status_token",
                "audience": "auditor",
                "question_key": "public_status_token",
                "minimal_path": "example_successor_status_envelope.json",
                "start_path": "example_successor_status_envelope.json",
                "escalate_if_challenged": ["example_successor_continuity_verdict.json", "example_publication_closure_verdict.json"],
                "stop_profile_key": "public_status_token",
                "why": "An auditor can start at the narrow token owner, then inspect the two narrower verdicts that make it true.",
            },
            {
                "route_key": "auditor_compact_diff",
                "audience": "auditor",
                "question_key": "compact_diff_summary",
                "minimal_path": "example_compare_report.json",
                "start_path": "example_compare_report.json",
                "escalate_if_challenged": ["example_verifier_report.json", "example_successor_continuity_verdict.json"],
                "stop_profile_key": "compact_diff_summary",
                "why": "An auditor route starts at the numeric diff summary, then escalates to recomputed replay totals and the changed-family slice if needed.",
            },
        ],
        "resolution_rule": "Pick the route keyed by audience and question; start at its declared start_path, escalate leftward only as needed, and consult the companion stop profile for the approved terminal fields for that question family.",
        "note": "Derived audience-keyed challenge-route map for one concrete successor comparison. It separates audience start-here / escalate-here guidance from both the minimal-citation object and the question-keyed stop profiles.",
    }
    challenge_routes_out = ART / "example_successor_challenge_routes.json"
    challenge_routes_payload = json.dumps(challenge_routes, indent=2, sort_keys=True) + "\n"
    challenge_routes_out.write_text(challenge_routes_payload, encoding="utf-8")
    challenge_routes_digest = sha256_bytes(challenge_routes_payload.encode("utf-8"))


    challenge_branches = {
        "challenge_branches_id": CHALLENGE_BRANCHES_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_stop_profiles_id": challenge_stop_profiles["challenge_stop_profiles_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "branch_contract": {
            "branch_fields": ["branch_key", "route_key", "question_key", "stop_profile_key", "piece_key", "start_path", "escalation_sequence", "terminal_stop_field", "why"],
            "escalation_step_fields": ["path", "why"],
            "terminal_stop_field_fields": ["path", "field", "why_stop_here"],
            "route_link_rule": "A challenge branch must begin at the start_path declared by its companion audience-keyed route.",
            "piece_link_rule": "A challenge branch must use a piece_key and terminal_stop_field already approved by the companion stop profile for the same question family.",
            "branch_rule": "Once one semantic piece is actually contested, follow the branch keyed by route_key and piece_key to one approved terminal field instead of treating the route's coarse escalation list as the final proof trace.",
        },
        "branches": [
            {
                "branch_key": "release_note_public_status_sentence_continuity_piece",
                "route_key": "release_note_public_status_sentence",
                "question_key": "public_status_sentence",
                "stop_profile_key": "public_status_sentence",
                "piece_key": "continuity_piece",
                "start_path": "example_successor_lineage_notice.json",
                "escalation_sequence": [
                    {"path": "example_successor_lineage_notice.json", "why": "start from the public wrapper sentence"},
                    {"path": "example_successor_claim_support_map.json", "why": "split the wrapper sentence into its narrower supported claims"},
                    {"path": "example_successor_continuity_verdict.json", "why": "this verdict owns the continuity half of the wrapper claim"},
                ],
                "terminal_stop_field": {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why_stop_here": "This is the approved continuity owner for the contested piece."},
                "why": "If the continuity half of the public wrapper sentence is challenged, do not stop at the wrapper or at the coarse route list; end at the continuity decision token."
            },
            {
                "branch_key": "release_note_public_status_sentence_closure_piece",
                "route_key": "release_note_public_status_sentence",
                "question_key": "public_status_sentence",
                "stop_profile_key": "public_status_sentence",
                "piece_key": "closure_piece",
                "start_path": "example_successor_lineage_notice.json",
                "escalation_sequence": [
                    {"path": "example_successor_lineage_notice.json", "why": "start from the public wrapper sentence"},
                    {"path": "example_successor_claim_support_map.json", "why": "split the wrapper sentence into its narrower supported claims"},
                    {"path": "example_publication_closure_verdict.json", "why": "this verdict owns the package-closure half of the wrapper claim"},
                ],
                "terminal_stop_field": {"path": "example_publication_closure_verdict.json", "field": "closure_status", "why_stop_here": "This is the approved closure owner for the contested piece."},
                "why": "Closure disputes on the public wrapper sentence end at the closure-status token, not at the wrapper prose."
            },
            {
                "branch_key": "release_note_compact_diff_diff_delta_piece",
                "route_key": "release_note_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "diff_delta_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "the compare report already owns the compact numeric delta"},
                ],
                "terminal_stop_field": {"path": "example_compare_report.json", "field": "observed_diffs", "why_stop_here": "This is the smallest numeric diff owner."},
                "why": "Some compact-diff challenges stop immediately because the compare report already owns the contested numeric delta."
            },
            {
                "branch_key": "release_note_compact_diff_recompute_piece",
                "route_key": "release_note_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "recompute_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "start at the shipped compact diff object"},
                    {"path": "example_verifier_report.json", "why": "move left to the replay-facing recomputation witness"},
                ],
                "terminal_stop_field": {"path": "example_verifier_report.json", "field": "recomputed", "why_stop_here": "This is the approved replay-facing witness for the recompute piece."},
                "why": "When the numeric delta itself is not enough, the branch continues to the recomputed replay totals."
            },
            {
                "branch_key": "release_note_compact_diff_changed_family_piece",
                "route_key": "release_note_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "changed_family_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "start at the shipped compact diff object"},
                    {"path": "example_successor_continuity_verdict.json", "why": "move left to the changed-family owner"},
                ],
                "terminal_stop_field": {"path": "example_successor_continuity_verdict.json", "field": "changed_line_items", "why_stop_here": "This verdict owns the narrow changed-family slice."},
                "why": "Changed-family disputes end at the continuity verdict's changed-line-items slice."
            },
            {
                "branch_key": "referee_public_status_sentence_continuity_piece",
                "route_key": "referee_public_status_sentence",
                "question_key": "public_status_sentence",
                "stop_profile_key": "public_status_sentence",
                "piece_key": "continuity_piece",
                "start_path": "example_successor_claim_support_map.json",
                "escalation_sequence": [
                    {"path": "example_successor_claim_support_map.json", "why": "the referee starts one layer left at the support map"},
                    {"path": "example_successor_continuity_verdict.json", "why": "follow the continuity support edge to the owning verdict"},
                ],
                "terminal_stop_field": {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why_stop_here": "This is the approved continuity owner."},
                "why": "The referee continuity branch starts from support, then ends at the continuity token."
            },
            {
                "branch_key": "referee_public_status_sentence_closure_piece",
                "route_key": "referee_public_status_sentence",
                "question_key": "public_status_sentence",
                "stop_profile_key": "public_status_sentence",
                "piece_key": "closure_piece",
                "start_path": "example_successor_claim_support_map.json",
                "escalation_sequence": [
                    {"path": "example_successor_claim_support_map.json", "why": "the referee starts one layer left at the support map"},
                    {"path": "example_publication_closure_verdict.json", "why": "follow the closure support edge to the owning verdict"},
                ],
                "terminal_stop_field": {"path": "example_publication_closure_verdict.json", "field": "closure_status", "why_stop_here": "This is the approved closure owner."},
                "why": "The referee closure branch ends at the closure-status token."
            },
            {
                "branch_key": "referee_package_completeness_role_rows_piece",
                "route_key": "referee_package_completeness",
                "question_key": "package_completeness",
                "stop_profile_key": "package_completeness",
                "piece_key": "role_rows_piece",
                "start_path": "example_release_closure_ledger.json",
                "escalation_sequence": [
                    {"path": "example_release_closure_ledger.json", "why": "the referee starts at the role-row bridge"},
                ],
                "terminal_stop_field": {"path": "example_release_closure_ledger.json", "field": "role_rows", "why_stop_here": "The stop profile approves the row ledger as the owner of satisfied-publication-role rows."},
                "why": "Package-completeness questions often terminate at the row ledger, before any compressed closure token."
            },
            {
                "branch_key": "referee_package_completeness_closure_token_piece",
                "route_key": "referee_package_completeness",
                "question_key": "package_completeness",
                "stop_profile_key": "package_completeness",
                "piece_key": "closure_token_piece",
                "start_path": "example_release_closure_ledger.json",
                "escalation_sequence": [
                    {"path": "example_release_closure_ledger.json", "why": "start at the role-row bridge"},
                    {"path": "example_publication_closure_verdict.json", "why": "continue to the compressed closure token once the row bindings are understood"},
                ],
                "terminal_stop_field": {"path": "example_publication_closure_verdict.json", "field": "closure_status", "why_stop_here": "The stop profile approves this token as the narrow closure answer."},
                "why": "Once the row ledger is understood, the compressed closure token can discharge the token piece."
            },
            {
                "branch_key": "auditor_public_status_token_status_token_piece",
                "route_key": "auditor_public_status_token",
                "question_key": "public_status_token",
                "stop_profile_key": "public_status_token",
                "piece_key": "status_token_piece",
                "start_path": "example_successor_status_envelope.json",
                "escalation_sequence": [
                    {"path": "example_successor_status_envelope.json", "why": "the auditor starts at the narrow token owner"},
                ],
                "terminal_stop_field": {"path": "example_successor_status_envelope.json", "field": "public_status", "why_stop_here": "The status envelope owns the narrow public-status token directly."},
                "why": "A token-only challenge may stop immediately at the status envelope."
            },
            {
                "branch_key": "auditor_public_status_token_continuity_piece",
                "route_key": "auditor_public_status_token",
                "question_key": "public_status_token",
                "stop_profile_key": "public_status_token",
                "piece_key": "continuity_piece",
                "start_path": "example_successor_status_envelope.json",
                "escalation_sequence": [
                    {"path": "example_successor_status_envelope.json", "why": "start at the narrow token owner"},
                    {"path": "example_successor_continuity_verdict.json", "why": "continue to the continuity owner compressed into that token"},
                ],
                "terminal_stop_field": {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "why_stop_here": "This is the approved continuity owner for the token's continuity piece."},
                "why": "A continuity challenge on the public-status token ends at the continuity verdict."
            },
            {
                "branch_key": "auditor_public_status_token_closure_piece",
                "route_key": "auditor_public_status_token",
                "question_key": "public_status_token",
                "stop_profile_key": "public_status_token",
                "piece_key": "closure_piece",
                "start_path": "example_successor_status_envelope.json",
                "escalation_sequence": [
                    {"path": "example_successor_status_envelope.json", "why": "start at the narrow token owner"},
                    {"path": "example_publication_closure_verdict.json", "why": "continue to the closure owner compressed into that token"},
                ],
                "terminal_stop_field": {"path": "example_publication_closure_verdict.json", "field": "closure_status", "why_stop_here": "This is the approved closure owner for the token's closure piece."},
                "why": "A closure challenge on the public-status token ends at the closure verdict."
            },
            {
                "branch_key": "auditor_compact_diff_diff_delta_piece",
                "route_key": "auditor_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "diff_delta_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "the auditor starts at the numeric diff owner"},
                ],
                "terminal_stop_field": {"path": "example_compare_report.json", "field": "observed_diffs", "why_stop_here": "The compare report is the approved numeric diff owner."},
                "why": "Delta-only compact-diff challenges may stop immediately at the compare report."
            },
            {
                "branch_key": "auditor_compact_diff_recompute_piece",
                "route_key": "auditor_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "recompute_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "start at the numeric diff owner"},
                    {"path": "example_verifier_report.json", "why": "continue to the replay-facing recomputation witness"},
                ],
                "terminal_stop_field": {"path": "example_verifier_report.json", "field": "recomputed", "why_stop_here": "The stop profile approves the verifier recomputation slice for this piece."},
                "why": "Auditor recomputation challenges end at the replay-facing verifier output."
            },
            {
                "branch_key": "auditor_compact_diff_changed_family_piece",
                "route_key": "auditor_compact_diff",
                "question_key": "compact_diff_summary",
                "stop_profile_key": "compact_diff_summary",
                "piece_key": "changed_family_piece",
                "start_path": "example_compare_report.json",
                "escalation_sequence": [
                    {"path": "example_compare_report.json", "why": "start at the numeric diff owner"},
                    {"path": "example_successor_continuity_verdict.json", "why": "continue to the changed-family owner"},
                ],
                "terminal_stop_field": {"path": "example_successor_continuity_verdict.json", "field": "changed_line_items", "why_stop_here": "The stop profile approves the changed-line-items slice for this piece."},
                "why": "Changed-family disputes end at the continuity verdict's changed-line-items slice."
            },
        ],
        "resolution_rule": "Pick the audience route first; once a concrete semantic piece is contested, follow the branch keyed by route_key and piece_key to one approved terminal field.",
        "note": "Derived piece-keyed challenge-branch map for one concrete successor comparison. It separates route-level audience navigation from the exact piece-specific escalation walk once one semantic piece is actually challenged.",
    }
    challenge_branches_out = ART / "example_successor_challenge_branches.json"
    challenge_branches_payload = json.dumps(challenge_branches, indent=2, sort_keys=True) + "\n"
    challenge_branches_out.write_text(challenge_branches_payload, encoding="utf-8")
    challenge_branches_digest = sha256_bytes(challenge_branches_payload.encode("utf-8"))

    quote_map = {
        "quote_map_id": QUOTE_MAP_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_stop_profiles_id": challenge_stop_profiles["challenge_stop_profiles_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "quote_targets": [
            {
                "quote_key": "public_status_token",
                "when": "Need the exact public-status token for the concrete release pair rather than the outward-facing sentence.",
                "target": {"path": "example_successor_status_envelope.json", "field": "public_status", "value": status_envelope.get("public_status")},
                "cite_path": "example_successor_status_envelope.json",
                "support_if_challenged": [
                    {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision"},
                    {"path": "example_publication_closure_verdict.json", "field": "closure_status"},
                ],
            },
            {
                "quote_key": "public_status_sentence",
                "when": "Need the exact outward-facing successor status sentence rather than a paraphrase.",
                "target": {"path": "example_successor_lineage_notice.json", "field": "status_summary", "value": lineage_notice.get("status_summary")},
                "cite_path": "example_successor_lineage_notice.json",
                "support_if_challenged": [
                    {"path": "example_successor_claim_support_map.json", "field": "claims"},
                    {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision"},
                    {"path": "example_publication_closure_verdict.json", "field": "closure_status"},
                ],
            },
            {
                "quote_key": "continuity_decision_token",
                "when": "Need the exact continuity token rather than the outward-facing prose sentence.",
                "target": {"path": "example_successor_continuity_verdict.json", "field": "continuity_decision", "value": continuity_verdict.get("continuity_decision")},
                "cite_path": "example_successor_continuity_verdict.json",
                "support_if_challenged": [
                    {"path": "example_compare_report.json", "field": "classification"},
                    {"path": "example_successor_claim_support_map.json", "field": "claims[0]"},
                ],
            },
            {
                "quote_key": "closure_status_token",
                "when": "Need the exact package-completeness token for the successor package.",
                "target": {"path": "example_publication_closure_verdict.json", "field": "closure_status", "value": closure_verdict.get("closure_status")},
                "cite_path": "example_publication_closure_verdict.json",
                "support_if_challenged": [
                    {"path": "example_publication_closure_verdict.json", "field": "required_publication_roles"},
                    {"path": "example_release_obligation_profile.json", "field": "classes"},
                ],
            },
            {
                "quote_key": "maintenance_order",
                "when": "Need the exact declared dependency order rather than a prose description of the maintenance stack.",
                "target": {"path": "example_successor_derivation_graph.json", "field": "topological_order", "value": derivation_graph.get("topological_order", [])},
                "cite_path": "example_successor_derivation_graph.json",
                "support_if_challenged": [
                    {"path": "example_successor_derivation_graph.json", "field": "edges"},
                ],
            },
            {
                "quote_key": "compact_numeric_diff",
                "when": "Need the compact numeric diff or replay trigger rather than the wrapper sentence.",
                "target": {"path": "example_compare_report.json", "field": "observed_diffs", "value": report.get("observed_diffs", [])},
                "cite_path": "example_compare_report.json",
                "support_if_challenged": [
                    {"path": "example_compare_report.json", "field": "user_fast_diff"},
                    {"path": "example_successor_continuity_verdict.json", "field": "changed_line_items"},
                ],
            },
        ],
        "resolution_rule": "Once the minimal citation target is known, quote the declared target field from that object instead of copying ad hoc prose; escalate to the listed support fields only if a narrower justification is demanded.",
        "note": "Derived exact-field quote map for one concrete successor comparison. It refines the minimal-citation choice to the exact field or field-list worth quoting, so later notes can reuse checked maintenance language without inventing a second wrapper sentence.",
    }
    quote_map_out = ART / "example_successor_quote_map.json"
    quote_map_payload = json.dumps(quote_map, indent=2, sort_keys=True) + "\n"
    quote_map_out.write_text(quote_map_payload, encoding="utf-8")
    quote_map_digest = sha256_bytes(quote_map_payload.encode("utf-8"))

    base_user = report.get("user_fast_diff", {}).get("base", {})
    successor_user = report.get("user_fast_diff", {}).get("successor", {})
    maintenance_order_text = " -> ".join(derivation_graph.get("topological_order", []))
    compact_diff_text = (
        f"Compact diff: fallback p_obs_upper 0.02 -> 0.015; "
        f"fallback summary bits {base_user.get('budget_value', 0.0):.6f} -> {successor_user.get('budget_value', 0.0):.6f}; "
        f"total summary bits per lookup {base_user.get('total_summary_bits_per_lookup', 0.0):.6f} -> {successor_user.get('total_summary_bits_per_lookup', 0.0):.6f}."
    )
    clause_pack = {
        "clause_pack_id": CLAUSE_PACK_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_quote_map_id": quote_map["quote_map_id"],
        "successor_clause_pack_id": CLAUSE_PACK_ID,
        "successor_release_spine_id": RELEASE_SPINE_ID,
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "note_version": artifact_inventory.get("note_version"),
        "clauses": [
            {
                "clause_key": "public_status_sentence",
                "when": "Need a ready-to-reuse public status sentence for a downstream note.",
                "text": lineage_notice.get("status_summary"),
                "cite_path": "example_successor_lineage_notice.json",
                "cite_field": "status_summary",
                "derived_from_quote_key": "public_status_sentence",
            },
            {
                "clause_key": "continuity_clause",
                "when": "Need a short continuity clause instead of the full public wrapper.",
                "text": f"Continuity decision: {continuity_verdict.get('continuity_decision')}.",
                "cite_path": "example_successor_continuity_verdict.json",
                "cite_field": "continuity_decision",
                "derived_from_quote_key": "continuity_decision_token",
            },
            {
                "clause_key": "closure_clause",
                "when": "Need a short package-completeness clause.",
                "text": f"Package closure status: {closure_verdict.get('closure_status')}.",
                "cite_path": "example_publication_closure_verdict.json",
                "cite_field": "closure_status",
                "derived_from_quote_key": "closure_status_token",
            },
            {
                "clause_key": "maintenance_order_clause",
                "when": "Need one sentence naming the declared maintenance order.",
                "text": f"Maintenance order: {maintenance_order_text}.",
                "cite_path": "example_successor_derivation_graph.json",
                "cite_field": "topological_order",
                "derived_from_quote_key": "maintenance_order",
            },
            {
                "clause_key": "compact_diff_clause",
                "when": "Need one sentence summarizing the compact numeric drift.",
                "text": compact_diff_text,
                "cite_path": "example_compare_report.json",
                "cite_field": "observed_diffs",
                "derived_from_quote_key": "compact_numeric_diff",
            },
        ],
        "resolution_rule": "Reuse the declared clause text verbatim when it fits the downstream note; otherwise fall back to the linked quote-map target and keep the declared cite_path.",
        "note": "Derived canonical clause pack for one concrete successor comparison. It packages short reusable maintenance clauses from already-checked fields so later notes can reuse wording without inventing another wrapper sentence.",
    }
    clause_pack_out = ART / "example_successor_clause_pack.json"
    clause_pack_payload = json.dumps(clause_pack, indent=2, sort_keys=True) + "\n"
    clause_pack_out.write_text(clause_pack_payload, encoding="utf-8")
    clause_pack_digest = sha256_bytes(clause_pack_payload.encode("utf-8"))

    release_spine = {
        "spine_id": RELEASE_SPINE_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "release_action_matrix_id": compare_walkthrough["release_action_matrix_id"],
        "release_obligation_profile_id": compare_walkthrough.get("release_obligation_profile_id"),
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_quote_map_id": quote_map["quote_map_id"],
        "successor_clause_pack_id": clause_pack["clause_pack_id"],
        "note_version": artifact_inventory.get("note_version"),
        "stage_order_fields": RELEASE_STAGE_ORDER_FIELDS,
        "stage_order": [
            {"stage": "diff", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "What changed?", "artifact": "example_compare_report.json", "object_id": report["report_id"], "stop_when": "The task is identifying which field families changed and which compact classification bucket won for the concrete base->successor pair.", "widen_only_if": "Widen only if the question becomes what replay scope, continuity class, or publication duty follows from that diff.", "why": "This is the earliest sufficient cut for drift identification; later wrappers may summarize it but do not re-own the numeric or family-level delta."},
            {"stage": "classify", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Which replay scope and continuity class follow from the diff?", "artifact": "example_successor_continuity_verdict.json", "object_id": continuity_verdict["verdict_id"], "stop_when": "The task is deciding replay scope, continuity status, or whether the certified interface survived the observed drift.", "widen_only_if": "Widen only if the question becomes which public outputs must now be refreshed or whether the shipped successor package actually closed.", "why": "Continuity tokens and replay-plan scope belong here, not in the later closure or wrapper stages that cite them."},
            {"stage": "obligate", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Which public outputs must now be refreshed?", "artifact": "example_release_obligation_profile.json", "companion_artifact": "example_release_action_matrix.json", "object_id": compare_walkthrough.get("release_obligation_profile_id"), "stop_when": "The task is naming the minimal publication roles required by the winning action class.", "widen_only_if": "Widen only if the question becomes whether those roles were actually satisfied by the shipped successor package.", "why": "This is the earliest sufficient publication-duty cut; closure and lineage objects depend on these duties but do not define them."},
            {"stage": "close", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Were the required successor outputs actually shipped?", "artifact": "example_publication_closure_verdict.json", "companion_artifact": "example_release_closure_ledger.json", "object_id": closure_verdict["closure_verdict_id"], "stop_when": "The task is package completeness: whether the required role rows were satisfied and the successor package is closed for release purposes.", "widen_only_if": "Widen only if the question becomes outward-facing status wording, clause support, or downstream reuse rather than package completeness itself.", "why": "This is the last release-validity cut before public wording; later wrapper stages may compress completeness but do not replace the role rows or closure token."},
            {"stage": "summarize", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "What is the outward-facing successor status sentence?", "artifact": "example_successor_lineage_notice.json", "object_id": lineage_notice["notice_id"], "stop_when": "One outward-facing successor-status sentence and pointer order are enough for the downstream task.", "widen_only_if": "Widen only if the task becomes clause-by-clause support, citation minimization, exact-field quotation, or reusable checked wording.", "why": "This stage owns the public wrapper sentence, but not the narrower continuity, closure, or diff fields it compresses."},
            {"stage": "support", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Which narrower object supports each public clause?", "artifact": "example_successor_claim_support_map.json", "object_id": claim_support_map["map_id"], "stop_when": "The task is clause-level traceability for the outward-facing successor wording.", "widen_only_if": "Widen only if the task becomes choosing the smallest sufficient citation target, exact quoted fields, or reusable clause text.", "why": "This is the first sufficient cut for clause-to-evidence bindings once the wrapper sentence alone is no longer enough."},
            {"stage": "cite", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "What is the smallest sufficient downstream citation target?", "artifact": "example_successor_citation_map.json", "companion_artifact": "example_successor_challenge_branches.json", "object_id": citation_map["citation_map_id"], "stop_when": "The task is citation minimization for a recurring downstream use rather than field quotation or sentence reuse.", "widen_only_if": "Widen only if the task becomes exact-field selection or reuse of already-checked clause text.", "why": "The citation map chooses the target family; it does not yet select exact fields inside that target."},
            {"stage": "quote", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Which exact field should later notes quote?", "artifact": "example_successor_quote_map.json", "object_id": quote_map["quote_map_id"], "stop_when": "The task is quoting one exact token, number, or field after the citation target is already known.", "widen_only_if": "Widen only if the task becomes reusing a checked short clause instead of quoting the narrow field directly.", "why": "Exact-field selection is the last narrow cut before clause-level compression."},
            {"stage": "clause", "release_stage_vocabulary_mode": "owned_vocabulary_release_spine_stage_order", "question": "Which short reusable clause is already checked?", "artifact": "example_successor_clause_pack.json", "object_id": clause_pack["clause_pack_id"], "stop_when": "The task is reusing one already-checked short clause rather than re-deriving wording from the narrower fields.", "widen_only_if": "Do not widen rightward: any challenge should resolve leftward through quote/support to the narrower owners.", "why": "This is the final presentation layer; it is convenient for terse papers but never re-owns the checked maintenance facts beneath it."},
        ],
        "stage_tokens": ["diff", "classify", "obligate", "close", "summarize", "support", "cite", "quote", "clause"],
        "stage_contract_fields": ["stage", "input_artifacts", "output_artifact", "output_field_family", "assertion_scope", "handoff_rule"],
        "stage_contracts": [
            {"stage": "diff", "input_artifacts": ["example_compare_profile.json", "example_compare_walkthrough.json", "example_change_control.json"], "output_artifact": "example_compare_report.json", "output_field_family": ["observed_diffs", "classification", "required_publication_roles"], "assertion_scope": "Owns the compact diff slice and classification context for the concrete base->successor comparison.", "handoff_rule": "Later notes may summarize this stage for status prose, but numeric deltas, changed-family slices, and required-publication-role context should still cite the compare report directly."},
            {"stage": "classify", "input_artifacts": ["example_compare_report.json", "example_verifier_report.json", "example_release_action_matrix.json", "example_release_obligation_profile.json"], "output_artifact": "example_successor_continuity_verdict.json", "output_field_family": ["continuity_decision", "changed_line_items", "replay_plan_ids"], "assertion_scope": "Owns the continuity decision and replay scope implied by the diff under the declared action matrix.", "handoff_rule": "Later notes may compress this stage into a status sentence, but continuity tokens and replay-scope slices still belong to the continuity verdict."},
            {"stage": "obligate", "input_artifacts": ["example_compare_report.json", "example_release_action_matrix.json"], "output_artifact": "example_release_obligation_profile.json", "output_field_family": ["classes", "required_outputs"], "assertion_scope": "Owns which publication roles are required for each action class.", "handoff_rule": "When a note asserts which outputs must be republished, cite the obligation profile (and action matrix companion) rather than a later wrapper object."},
            {"stage": "close", "input_artifacts": ["example_compare_report.json", "example_release_obligation_profile.json", "support_manifest.json", "example_artifact_inventory.json"], "output_artifact": "example_publication_closure_verdict.json", "output_field_family": ["closure_status", "provided_publication_outputs"], "assertion_scope": "Owns whether the concrete successor package actually ships the outputs the obligation class requires, with row-level satisfaction carried by the companion closure ledger.", "handoff_rule": "Later notes may summarize package completeness, but role rows belong to the closure ledger and closure tokens and bound publication outputs still belong to the closure verdict."},
            {"stage": "summarize", "input_artifacts": ["example_successor_status_envelope.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_compare_report.json"], "output_artifact": "example_successor_lineage_notice.json", "output_field_family": ["status_summary", "reader_pointer_order"], "assertion_scope": "Owns the outward-facing successor-status sentence and reader-pointer order; the companion status envelope owns the narrow public-status token.", "handoff_rule": "Cite this stage when one public sentence is enough; cite the status envelope or continue leftward to support, quote, or the narrower verdict objects when the narrow status token matters."},
            {"stage": "support", "input_artifacts": ["example_successor_lineage_notice.json", "example_compare_report.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json"], "output_artifact": "example_successor_claim_support_map.json", "output_field_family": ["claims"], "assertion_scope": "Owns clause-to-evidence bindings for outward-facing successor claims.", "handoff_rule": "Use this stage when a referee needs clause-by-clause traceability rather than only the wrapper sentence."},
            {"stage": "cite", "input_artifacts": ["example_successor_lineage_notice.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json", "example_successor_claim_support_map.json", "example_compare_report.json"], "output_artifact": "example_successor_citation_map.json", "companion_artifact": "example_successor_challenge_branches.json", "output_field_family": ["queries"], "assertion_scope": "Owns the smallest-sufficient citation choice for recurring downstream use cases; the companion branch map owns the piece-specific escalation walk once one route/piece pair is actually challenged.", "handoff_rule": "Use this stage when the problem is citation minimization; consult the companion branch map once a concrete piece-specific escalation trace is required."},
            {"stage": "quote", "input_artifacts": ["example_successor_citation_map.json", "example_successor_lineage_notice.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json", "example_compare_report.json"], "output_artifact": "example_successor_quote_map.json", "output_field_family": ["quote_targets"], "assertion_scope": "Owns exact-field selection once the correct citation target is known.", "handoff_rule": "When a later note asserts a token or numeric value verbatim, it should cite the quote target or continue leftward to the owning narrow field."},
            {"stage": "clause", "input_artifacts": ["example_successor_quote_map.json", "example_successor_lineage_notice.json", "example_compare_report.json"], "output_artifact": "example_successor_clause_pack.json", "output_field_family": ["clauses"], "assertion_scope": "Owns short reusable downstream wording, but only for already-checked claims.", "handoff_rule": "Clause text may compress presentation, but any challenge must still resolve leftward through quote/support to the narrower maintenance objects."},
        ],
        "derivation_anchor": {"artifact": "example_successor_derivation_graph.json", "object_id": derivation_graph["graph_id"], "field": "topological_order"},
        "status_chain": {
            "continuity_decision": continuity_verdict.get("continuity_decision"),
            "closure_status": closure_verdict.get("closure_status"),
            "status_summary": lineage_notice.get("status_summary"),
        },
        "stage_cut_rule": "Stop at the earliest sufficient release-local stage for the question actually being asked, and widen rightward only when the question changes family rather than merely because later wrapper objects exist.",
        "resolution_rule": "Move strictly left-to-right: later stages may compress earlier results for readability, but they never replace the narrower maintenance objects they cite.",
        "contract_rule": "Each stage contract names the inputs it may read and the output field family it owns; later stages may compress those outputs, but they do not silently overwrite ownership of tokens, numbers, or sentences.",
        "downstream_rule": "Cite the spine when a paper only needs the stable maintenance order; cite the owning stage contract or the narrower maintenance object whenever a numeric delta, token, or sentence is actually asserted.",
        "note": "Derived release-evolution spine for one concrete successor comparison. It states the stable maintenance stages and their tiny handoff contracts without replacing the concrete dependency DAG or the narrower verdict objects.",
    }
    release_spine_out = ART / "example_release_spine.json"
    release_spine_payload = json.dumps(release_spine, indent=2, sort_keys=True) + "\n"
    release_spine_out.write_text(release_spine_payload, encoding="utf-8")
    release_spine_digest = sha256_bytes(release_spine_payload.encode("utf-8"))

    release_stage_walkthrough = {
        "walkthrough_id": RELEASE_STAGE_WALKTHROUGH_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_continuity_verdict_id": continuity_verdict["verdict_id"],
        "release_closure_ledger_id": CLOSURE_LEDGER_ID,
        "publication_closure_verdict_id": closure_verdict["closure_verdict_id"],
        "successor_status_envelope_id": status_envelope["status_envelope_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_derivation_graph_id": derivation_graph["graph_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_quote_map_id": quote_map["quote_map_id"],
        "successor_clause_pack_id": clause_pack["clause_pack_id"],
        "successor_sentence_locks_id": SENTENCE_LOCKS_ID,
        "successor_release_spine_id": release_spine["spine_id"],
        "note_version": artifact_inventory.get("note_version"),
        "stage_walk_fields": ["stage", "output_artifact", "owned_field_family", "resolved_inputs", "assertion_scope", "handoff_rule", "stage_summary", "why_not_later"],
        "stage_walk": [
            {"stage": "diff", "output_artifact": "example_compare_report.json", "owned_field_family": ["observed_diffs", "classification", "required_publication_roles"], "resolved_inputs": ["example_compare_profile.json", "example_compare_walkthrough.json", "example_change_control.json"], "assertion_scope": "Owns the compact diff slice and classification context for the concrete base->successor comparison.", "handoff_rule": "Later notes may summarize this stage for status prose, but numeric deltas, changed-family slices, and required-publication-role context should still cite the compare report directly.", "stage_summary": "Case B changes only the fallback contact/vector slice and lands in replay_changed_surfaces.", "why_not_later": "Later wrappers may summarize these deltas, but they do not re-own the numeric diff or winning class."},
            {"stage": "classify", "output_artifact": "example_successor_continuity_verdict.json", "owned_field_family": ["continuity_decision", "changed_line_items", "replay_plan_ids"], "resolved_inputs": ["example_compare_report.json", "example_verifier_report.json", "example_release_action_matrix.json", "example_release_obligation_profile.json"], "assertion_scope": "Owns the continuity decision and replay scope implied by the diff under the declared action matrix.", "handoff_rule": "Later notes may compress this stage into a status sentence, but continuity tokens and replay-scope slices still belong to the continuity verdict.", "stage_summary": "The successor remains on the same certified interface after replaying the changed fallback surfaces.", "why_not_later": "The lineage notice may quote this decision, but it does not replace the continuity token or replay scope."},
            {"stage": "obligate", "output_artifact": "example_release_obligation_profile.json", "owned_field_family": ["classes", "required_outputs"], "resolved_inputs": ["example_compare_report.json", "example_release_action_matrix.json"], "assertion_scope": "Owns which publication roles are required for each action class.", "handoff_rule": "When a note asserts which outputs must be republished, cite the obligation profile (and action matrix companion) rather than a later wrapper object.", "stage_summary": "The winning replay_changed_surfaces class requires a fresh release binding, compare report, replay verdict, continuity verdict, and lineage notice.", "why_not_later": "Closure and lineage objects depend on these duties; they do not define them."},
            {"stage": "close", "output_artifact": "example_publication_closure_verdict.json", "owned_field_family": ["closure_status", "provided_publication_outputs"], "resolved_inputs": ["example_compare_report.json", "example_release_obligation_profile.json", "support_manifest.json", "example_artifact_inventory.json"], "assertion_scope": "Owns whether the concrete successor package actually ships the outputs the obligation class requires, with row-level satisfaction carried by the companion closure ledger.", "handoff_rule": "Later notes may summarize package completeness, but role rows belong to the closure ledger and closure tokens and bound publication outputs still belong to the closure verdict.", "stage_summary": "The close-stage bridge first checks the required role rows in the companion closure ledger, then emits the compressed completeness token for the canned successor package.", "why_not_later": "The lineage notice may repeat package completeness, but it does not re-own either the role rows or the final closure token."},
            {"stage": "summarize", "output_artifact": "example_successor_lineage_notice.json", "owned_field_family": ["status_summary", "reader_pointer_order"], "resolved_inputs": ["example_successor_status_envelope.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_compare_report.json"], "assertion_scope": "Owns the outward-facing successor-status sentence and reader-pointer order; the companion status envelope owns the narrow public-status token.", "handoff_rule": "Cite this stage when one public sentence is enough; cite the status envelope or continue leftward to support, quote, or the narrower verdict objects when the narrow status token matters.", "stage_summary": "The public wrapper compresses the summary-stage status envelope into one sentence saying the successor remains on the same interface after replaying changed fallback surfaces and that required outputs are complete.", "why_not_later": "This stage is the wrapper sentence and pointer order, not the owner of the public-status token, continuity token, closure token, or numeric deltas it compresses."},
            {"stage": "support", "output_artifact": "example_successor_claim_support_map.json", "owned_field_family": ["claims"], "resolved_inputs": ["example_successor_lineage_notice.json", "example_compare_report.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json"], "assertion_scope": "Owns clause-to-evidence bindings for outward-facing successor claims.", "handoff_rule": "Use this stage when a referee needs clause-by-clause traceability rather than only the wrapper sentence.", "stage_summary": "Each outward-facing clause is bound back to the narrower compare, continuity, or closure object that discharges it.", "why_not_later": "Citation and quote stages refine reuse; they do not create new support families."},
            {"stage": "cite", "output_artifact": "example_successor_citation_map.json", "owned_field_family": ["queries"], "resolved_inputs": ["example_successor_lineage_notice.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json", "example_successor_claim_support_map.json", "example_compare_report.json"], "assertion_scope": "Owns the smallest-sufficient citation choice for recurring downstream use cases; the companion branch map owns the piece-specific escalation walk once one route/piece pair is actually challenged.", "handoff_rule": "Use this stage when the problem is citation minimization; consult the companion branch map once a concrete piece-specific escalation trace is required.", "stage_summary": "The map chooses the smallest sufficient artifact for status, package completeness, maintenance order, and compact diff uses.", "why_not_later": "The quote map narrows fields inside a chosen citation target; it does not choose the target family itself."},
            {"stage": "quote", "output_artifact": "example_successor_quote_map.json", "owned_field_family": ["quote_targets"], "resolved_inputs": ["example_successor_citation_map.json", "example_successor_lineage_notice.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json", "example_successor_derivation_graph.json", "example_compare_report.json"], "assertion_scope": "Owns exact-field selection once the correct citation target is known.", "handoff_rule": "When a later note asserts a token or numeric value verbatim, it should cite the quote target or continue leftward to the owning narrow field.", "stage_summary": "Exact fields are fixed for the public-status sentence, continuity token, closure token, maintenance order, and compact numeric diff.", "why_not_later": "The clause pack may compress those fields into prose, but it does not replace the exact field selection."},
            {"stage": "clause", "output_artifact": "example_successor_clause_pack.json", "owned_field_family": ["clauses"], "resolved_inputs": ["example_successor_quote_map.json", "example_successor_lineage_notice.json", "example_compare_report.json"], "assertion_scope": "Owns short reusable downstream wording, but only for already-checked claims.", "handoff_rule": "Clause text may compress presentation, but any challenge must still resolve leftward through quote/support to the narrower maintenance objects.", "stage_summary": "The final stage turns checked fields into reusable short status and compact-diff sentences.", "why_not_later": "There is no later maintenance stage that can re-own the sentence once the clause layer is reached; reuse stays anchored by the downstream normal form."}
        ],
        "walk_rule": "Read this object top-to-bottom: each row instantiates one release-spine contract for the same successor pair, names the concrete artifact that owns the stage output, and states why later notes must not let that field family drift into a later wrapper.",
        "note": "Derived stage-by-stage worked release walk for one concrete successor comparison. It instantiates the stable release spine with concrete artifacts, owned field families, resolved inputs, and citation boundaries so the release-evolution backbone is auditable rather than decorative."
    }
    release_stage_walkthrough_out = ART / "example_release_stage_walkthrough.json"
    release_stage_walkthrough_payload = json.dumps(release_stage_walkthrough, indent=2, sort_keys=True) + "\n"
    release_stage_walkthrough_out.write_text(release_stage_walkthrough_payload, encoding="utf-8")
    release_stage_walkthrough_digest = sha256_bytes(release_stage_walkthrough_payload.encode("utf-8"))

    public_status_surface = lineage_notice.get("status_summary")

    public_sentence_lock = {
        "lock_key": "public_status_sentence",
        "family": "public_status_sentence",
        "surface_text": public_status_surface,
        "cite_path": "example_successor_lineage_notice.json",
        "clause_key": "public_status_sentence",
        "comparison_anchor": {
            "base_release_id": compare_walkthrough["base_release_id"],
            "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
            "compare_report_id": report["report_id"],
            "object_digests": [
                {"artifact": "example_compare_report.json", "sha256": digest},
                {"artifact": "example_successor_continuity_verdict.json", "sha256": verdict_digest},
                {"artifact": "example_publication_closure_verdict.json", "sha256": closure_digest},
            ],
            "anchor_fields": [
                {"artifact": "example_successor_continuity_verdict.json", "field_or_key": "continuity_decision"},
                {"artifact": "example_publication_closure_verdict.json", "field_or_key": "closure_status"},
            ],
            "witness_capsule": [
                {"field_or_key": "base_release_id", "why": "Names the certified base release cut for this sentence."},
                {"field_or_key": "successor_release_id", "why": "Names the certified successor release cut for this sentence."},
                {"field_or_key": "compare_report_id", "why": "Names the compare-report cut that owns the comparison."},
                {"field_or_key": "object_digests", "why": "Carries the exact shipped object-cut digest witness for the anchored maintenance objects."}
            ],
            "witness_floor": [
                {"field_or_key": "base_release_id", "why": "Minimal visible provenance should still name which certified base release this sentence compares from."},
                {"field_or_key": "successor_release_id", "why": "Minimal visible provenance should still name which certified successor release this sentence compares to."},
                {"field_or_key": "compare_report_id", "why": "Minimal visible provenance should still name the compare-report cut that owns the sentence comparison."}
            ],
            "witness_omittable": [
                {"field_or_key": "object_digests", "why": "Digest witnesses are optional visible provenance beyond the witness floor and may be omitted when a later note prints only the minimal inline provenance bundle."}
            ],
            "maintenance_posture": {
                "current_status": "carryforward",
                "recheck_status": "refresh_only_after_recheck",
                "regenerate_status": "retire_and_reissue",
                "why": "For the current maintained bundle cut, the release pair, anchored digests, and terminal targets still match the checked sentence, so the wording is carryforward-clean; digest drift would demote it to refresh-only after recheck, while pair or target drift would retire it."
            },
            "inline_provenance_profiles": [
                {"profile_key": "silent", "visible_fields": [], "why": "Reuse the checked sentence with no inline provenance shown; the sentence stays anchor-bound, but visible provenance is intentionally absent at the reuse site."},
                {"profile_key": "floor", "visible_fields": ["base_release_id", "successor_release_id", "compare_report_id"], "why": "Reuse the checked sentence with only the minimum visible provenance bundle required once any inline provenance is shown."},
                {"profile_key": "capsule", "visible_fields": ["base_release_id", "successor_release_id", "compare_report_id", "object_digests"], "why": "Reuse the checked sentence with the full declared visible-provenance capsule."}
            ],
            "default_inline_profile": {"profile_key": "floor", "why": "The archive-default inline provenance mode for terse reuse keeps the checked sentence visible together with the minimal release-pair-plus-compare-report bundle unless a later note explicitly chooses silent or capsule."},
            "recheck_if": [
                {"kind": "object_digest_change", "release_fields": [], "artifacts": ["example_compare_report.json", "example_successor_continuity_verdict.json", "example_publication_closure_verdict.json"], "target_keys": [], "why": "If any anchored compare/continuity/closure digest changes, the sentence must be revalidated against the new shipped object cut before verbatim reuse."}
            ],
            "regenerate_if": [
                {"kind": "release_pair_change", "release_fields": ["base_release_id", "successor_release_id"], "artifacts": [], "target_keys": [], "why": "A public-status sentence certified for one base->successor pair must be regenerated for a different pair."},
                {"kind": "terminal_target_change", "release_fields": [], "artifacts": [], "target_keys": ["continuity_decision_target", "closure_status_target"], "why": "If either terminal status token changes, the emitted public-status sentence must be reissued."}
            ],
            "refresh_in_place": [
                {"field_or_key": "object_digests", "why": "If recheck passes under the same release pair and terminal targets, refresh only the anchored digest witness to match the new shipped object cut."}
            ],
            "why_locked": "This sentence is only certified for the declared base->successor pair, the concrete continuity/closure tokens it compresses, and the exact shipped compare/verdict objects that carry those tokens."
        }
    }

    compact_sentence_lock = {
        "lock_key": "compact_numeric_diff",
        "family": "compact_numeric_diff",
        "surface_text": compact_diff_text,
        "cite_path": "example_compare_report.json",
        "clause_key": "compact_diff_clause",
        "comparison_anchor": {
            "base_release_id": compare_walkthrough["base_release_id"],
            "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
            "compare_report_id": report["report_id"],
            "object_digests": [
                {"artifact": "example_compare_report.json", "sha256": digest},
                {"artifact": "example_successor_continuity_verdict.json", "sha256": verdict_digest},
            ],
            "anchor_fields": [
                {"artifact": "example_compare_report.json", "field_or_key": "observed_diffs"},
                {"artifact": "example_successor_continuity_verdict.json", "field_or_key": "changed_line_items"},
            ],
            "witness_capsule": [
                {"field_or_key": "base_release_id", "why": "Names the certified base release cut for this sentence."},
                {"field_or_key": "successor_release_id", "why": "Names the certified successor release cut for this sentence."},
                {"field_or_key": "compare_report_id", "why": "Names the compare-report cut that owns the comparison."},
                {"field_or_key": "object_digests", "why": "Carries the exact shipped object-cut digest witness for the anchored maintenance objects."}
            ],
            "witness_floor": [
                {"field_or_key": "base_release_id", "why": "Minimal visible provenance should still name which certified base release this sentence compares from."},
                {"field_or_key": "successor_release_id", "why": "Minimal visible provenance should still name which certified successor release this sentence compares to."},
                {"field_or_key": "compare_report_id", "why": "Minimal visible provenance should still name the compare-report cut that owns the sentence comparison."}
            ],
            "witness_omittable": [
                {"field_or_key": "object_digests", "why": "Digest witnesses are optional visible provenance beyond the witness floor and may be omitted when a later note prints only the minimal inline provenance bundle."}
            ],
            "maintenance_posture": {
                "current_status": "carryforward",
                "recheck_status": "refresh_only_after_recheck",
                "regenerate_status": "retire_and_reissue",
                "why": "For the current maintained bundle cut, the release pair, anchored digests, and terminal targets still match the checked sentence, so the wording is carryforward-clean; digest drift would demote it to refresh-only after recheck, while pair or target drift would retire it."
            },
            "inline_provenance_profiles": [
                {"profile_key": "silent", "visible_fields": [], "why": "Reuse the checked sentence with no inline provenance shown; the sentence stays anchor-bound, but visible provenance is intentionally absent at the reuse site."},
                {"profile_key": "floor", "visible_fields": ["base_release_id", "successor_release_id", "compare_report_id"], "why": "Reuse the checked sentence with only the minimum visible provenance bundle required once any inline provenance is shown."},
                {"profile_key": "capsule", "visible_fields": ["base_release_id", "successor_release_id", "compare_report_id", "object_digests"], "why": "Reuse the checked sentence with the full declared visible-provenance capsule."}
            ],
            "default_inline_profile": {"profile_key": "floor", "why": "The archive-default inline provenance mode for terse reuse keeps the checked sentence visible together with the minimal release-pair-plus-compare-report bundle unless a later note explicitly chooses silent or capsule."},
            "recheck_if": [
                {"kind": "object_digest_change", "release_fields": [], "artifacts": ["example_compare_report.json", "example_successor_continuity_verdict.json"], "target_keys": [], "why": "If the anchored compare-report or continuity-verdict digest changes, the sentence must be revalidated against the new shipped object cut before verbatim reuse."}
            ],
            "regenerate_if": [
                {"kind": "release_pair_change", "release_fields": ["base_release_id", "successor_release_id"], "artifacts": [], "target_keys": [], "why": "A compact diff sentence certified for one base->successor pair must be regenerated for a different pair."},
                {"kind": "terminal_target_change", "release_fields": [], "artifacts": [], "target_keys": ["numeric_delta_target", "changed_family_target"], "why": "If the numeric-delta field or changed-family slice changes, the emitted compact diff sentence must be reissued."}
            ],
            "refresh_in_place": [
                {"field_or_key": "object_digests", "why": "If recheck passes under the same release pair and terminal targets, refresh only the anchored digest witness to match the new shipped object cut."}
            ],
            "why_locked": "This sentence is only certified for the declared base->successor pair, the concrete diff slice it summarizes, and the exact shipped compare/verdict objects that carry that slice."
        }
    }

    sentence_locks = {
        "sentence_locks_id": SENTENCE_LOCKS_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_quote_map_id": quote_map["quote_map_id"],
        "successor_clause_pack_id": clause_pack["clause_pack_id"],
        "successor_normal_form_id": NORMAL_FORM_ID,
        "note_version": artifact_inventory.get("note_version"),
        "lock_contract": {
            "lock_fields": ["lock_key", "family", "surface_text", "cite_path", "clause_key", "comparison_anchor"],
            "comparison_anchor_fields": ["base_release_id", "successor_release_id", "compare_report_id", "object_digests", "anchor_fields", "witness_capsule", "witness_floor", "witness_omittable", "maintenance_posture", "inline_provenance_profiles", "default_inline_profile", "recheck_if", "regenerate_if", "refresh_in_place", "why_locked"],
            "maintenance_posture_fields": ["current_status", "recheck_status", "regenerate_status", "why"],
            "comparison_anchor_digest_fields": ["artifact", "sha256"],
            "anchor_field_fields": ["artifact", "field_or_key"],
            "witness_capsule_fields": ["field_or_key", "why"],
            "witness_floor_fields": ["field_or_key", "why"],
            "witness_omittable_fields": ["field_or_key", "why"],
            "inline_provenance_profile_fields": ["profile_key", "visible_fields", "why"],
            "default_inline_profile_fields": ["profile_key", "why"],
            "recheck_guard_fields": ["kind", "release_fields", "artifacts", "target_keys", "why"],
            "regeneration_guard_fields": ["kind", "release_fields", "artifacts", "target_keys", "why"],
            "refresh_field_fields": ["field_or_key", "why"],
            "lock_rule": "A sentence may be reused verbatim only while its comparison anchor still names the same release pair, compare-report cut, and truth-bearing terminal targets.",
            "recheck_rule": "If only recheck_if guards fire, revalidate against the new shipped object cut before reusing the sentence.",
            "regeneration_rule": "If any regenerate_if guard fires, retire the wording and emit a new sentence for the new pair or target cut.",
            "refresh_rule": "After successful recheck, refresh only the declared witness fields in place; do not mutate the emitted text, release-pair anchor, or terminal targets.",
            "inline_profile_rule": "Visible inline provenance must be one of the declared modes: silent, floor, or capsule.",
            "default_inline_profile_rule": "If a later note does not choose a visible-provenance mode explicitly, inherit default_inline_profile.",
            "maintenance_posture_rule": "Current sentence reuse posture must be mirrored exactly by later answer-card / publication-profile / route / spine owners rather than reconstructed ad hoc from lock guards."
        },
        "locks": [public_sentence_lock, compact_sentence_lock],
        "note": "Derived sentence-lock ledger for one concrete successor comparison. It projects pair-anchored reuse policy, explicit current sentence-reuse posture, recheck-vs-regenerate guards, refresh-in-place boundaries, and visible inline-provenance modes into a citeable adjunct separate from the wording suffix itself."
    }
    sentence_locks_out = ART / "example_successor_sentence_locks.json"
    sentence_locks_payload = json.dumps(sentence_locks, indent=2, sort_keys=True) + "\n"
    sentence_locks_out.write_text(sentence_locks_payload, encoding="utf-8")
    sentence_locks_digest = sha256_bytes(sentence_locks_payload.encode("utf-8"))

    normal_form = {
        "normal_form_id": NORMAL_FORM_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_lineage_notice_id": lineage_notice["notice_id"],
        "successor_claim_support_map_id": claim_support_map["map_id"],
        "successor_citation_map_id": citation_map["citation_map_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "successor_quote_map_id": quote_map["quote_map_id"],
        "successor_clause_pack_id": clause_pack["clause_pack_id"],
        "successor_sentence_locks_id": sentence_locks["sentence_locks_id"],
        "successor_release_spine_id": release_spine["spine_id"],
        "note_version": artifact_inventory.get("note_version"),
        "stage_suffix": [
            {"stage": "summarize", "artifact": "example_successor_lineage_notice.json", "role": "public successor-status sentence"},
            {"stage": "support", "artifact": "example_successor_claim_support_map.json", "role": "clause-to-evidence bindings"},
            {"stage": "cite", "artifact": "example_successor_citation_map.json", "role": "smallest sufficient citation targets"},
            {"stage": "quote", "artifact": "example_successor_quote_map.json", "role": "exact fields to quote"},
            {"stage": "clause", "artifact": "example_successor_clause_pack.json", "role": "short reusable checked sentences"},
        ],
        "clause_families": [
            {"family": "public_status_sentence", "summary_field": {"artifact": "example_successor_lineage_notice.json", "field": "status_summary", "value": public_status_surface}, "citation_question_key": "public_status_sentence", "quote_key": "public_status_sentence", "clause_key": "public_status_sentence"},
            {"family": "continuity_decision", "summary_field": {"artifact": "example_successor_continuity_verdict.json", "field": "continuity_decision", "value": continuity_verdict.get("continuity_decision")}, "citation_question_key": "public_status_token", "quote_key": "continuity_decision_token", "clause_key": "continuity_clause"},
            {"family": "package_completeness", "summary_field": {"artifact": "example_publication_closure_verdict.json", "field": "closure_status", "value": closure_verdict.get("closure_status")}, "citation_question_key": "package_completeness", "quote_key": "closure_status_token", "clause_key": "closure_clause"},
            {"family": "maintenance_order", "summary_field": {"artifact": "example_successor_derivation_graph.json", "field": "topological_order", "value": derivation_graph.get("topological_order", [])}, "citation_question_key": "maintenance_order", "quote_key": "maintenance_order", "clause_key": "maintenance_order_clause"},
            {"family": "compact_numeric_diff", "summary_field": {"artifact": "example_compare_report.json", "field": "observed_diffs", "value": report.get("observed_diffs", [])}, "citation_question_key": "compact_diff_summary", "quote_key": "compact_numeric_diff", "clause_key": "compact_diff_clause"},
        ],
        "resolution_contract": {
            "trace_order": ["emit", "clause", "quote", "cite", "support", "narrow"],
            "required_step_fields": ["step", "artifact", "field_or_key", "why"],
            "terminal_target_fields": ["target_key", "artifact", "field_or_key", "role", "claim_classes", "why_stop_here"],
            "covered_claim_class_fields": ["covered_claim_classes"],
            "segment_fields": ["segment_key", "surface_span", "claim_classes", "terminal_target_keys", "why"],
            "surface_assembly_fields": ["kind", "value"],
            "sentence_lock_binding_fields": ["path", "lock_key"],
            "challenge_rule": "A challenge follows a typed leftward trace from emitted sentence to clause, quote, citation, support, and finally to narrower maintenance fields, with any piece-specific escalation beyond the coarse audience route imported from the companion challenge-branch map.",
            "terminal_target_rule": "For every contested semantic piece, audit must stop at one declared narrow terminal target rather than at the wrapper sentence.",
            "coverage_rule": "Every covered claim class named by an emitted sentence must be discharged by at least one declared terminal target.",
            "segment_rule": "Segment bindings expose which auditable surface spans are discharged by which target families.",
            "assembly_rule": "The declared surface-assembly witness is valid only when its concatenation exactly reconstructs the emitted sentence.",
            "sentence_lock_rule": "Pair-anchored reuse policy for any emitted sentence is imported from the separate sentence-lock ledger via a path-plus-lock-key binding rather than re-owned here."
        },
        "resolution_examples": [
            {
                "example_key": "public_status_sentence",
                "surface_text": public_status_surface,
                "family": "public_status_sentence",
                "citation": {"artifact": "example_successor_citation_map.json", "question_key": "public_status_sentence", "target_path": "example_successor_lineage_notice.json"},
                "quote": {"artifact": "example_successor_quote_map.json", "quote_key": "public_status_sentence", "target_path": "example_successor_lineage_notice.json", "target_field": "status_summary"},
                "clause": {"artifact": "example_successor_clause_pack.json", "clause_key": "public_status_sentence", "cite_path": "example_successor_lineage_notice.json"},
                "sentence_lock": {"path": "example_successor_sentence_locks.json", "lock_key": "public_status_sentence"},
                "covered_claim_classes": ["continuity_decision", "closure_status"],
                "terminal_targets": [
                    {"target_key": "continuity_decision_target", "artifact": "example_successor_continuity_verdict.json", "field_or_key": "continuity_decision", "role": "continuity_token", "claim_classes": ["continuity_decision"], "why_stop_here": "Wrapper status wording compresses this certified-interface decision token."},
                    {"target_key": "closure_status_target", "artifact": "example_publication_closure_verdict.json", "field_or_key": "closure_status", "role": "closure_token", "claim_classes": ["closure_status"], "why_stop_here": "Package-completeness wording compresses this closure token rather than replacing it."}
                ],
                "segments": [
                    {"segment_key": "status_continuity_half", "surface_span": "Successor remains on the same certified interface after replaying the changed fallback surfaces", "claim_classes": ["continuity_decision"], "terminal_target_keys": ["continuity_decision_target"], "why": "This span carries the certified-interface continuity decision."},
                    {"segment_key": "status_closure_half", "surface_span": "required successor publication outputs are complete", "claim_classes": ["closure_status"], "terminal_target_keys": ["closure_status_target"], "why": "This span carries the publication-package closure status."}
                ],
                "surface_assembly": [
                    {"kind": "segment", "value": "status_continuity_half"},
                    {"kind": "literal", "value": "; "},
                    {"kind": "segment", "value": "status_closure_half"},
                    {"kind": "literal", "value": "."}
                ],
                "trace_steps": [
                    {"step": "emit", "artifact": "example_successor_normal_form.json", "field_or_key": "resolution_examples[public_status_sentence].surface_text", "why": "Reusable downstream sentence exactly as emitted."},
                    {"step": "clause", "artifact": "example_successor_clause_pack.json", "field_or_key": "clauses[public_status_sentence]", "why": "Declared reusable clause and cite path."},
                    {"step": "quote", "artifact": "example_successor_quote_map.json", "field_or_key": "quote_targets[public_status_sentence]", "why": "Pins the exact quoted field for the emitted sentence."},
                    {"step": "cite", "artifact": "example_successor_citation_map.json", "field_or_key": "queries[public_status_sentence]", "why": "Names the smallest sufficient cited object."},
                    {"step": "support", "artifact": "example_successor_claim_support_map.json", "field_or_key": "claims[public_status_sentence_is_traceable]", "why": "Binds the wrapper sentence back to narrower verdict fields."},
                    {"step": "narrow", "artifact": "example_successor_continuity_verdict.json", "field_or_key": "continuity_decision", "why": "One terminal maintenance token supporting the first half of the sentence."},
                    {"step": "narrow", "artifact": "example_publication_closure_verdict.json", "field_or_key": "closure_status", "why": "One terminal maintenance token supporting the package-completeness half of the sentence."}
                ]
            },
            {
                "example_key": "compact_numeric_diff",
                "surface_text": compact_diff_text,
                "family": "compact_numeric_diff",
                "citation": {"artifact": "example_successor_citation_map.json", "question_key": "compact_diff_summary", "target_path": "example_compare_report.json"},
                "quote": {"artifact": "example_successor_quote_map.json", "quote_key": "compact_numeric_diff", "target_path": "example_compare_report.json", "target_field": "observed_diffs"},
                "clause": {"artifact": "example_successor_clause_pack.json", "clause_key": "compact_diff_clause", "cite_path": "example_compare_report.json"},
                "sentence_lock": {"path": "example_successor_sentence_locks.json", "lock_key": "compact_numeric_diff"},
                "covered_claim_classes": ["numeric_delta", "changed_family_identity"],
                "terminal_targets": [
                    {"target_key": "numeric_delta_target", "artifact": "example_compare_report.json", "field_or_key": "observed_diffs", "role": "numeric_delta_field", "claim_classes": ["numeric_delta"], "why_stop_here": "The emitted compact diff sentence compresses these exact numeric deltas."},
                    {"target_key": "changed_family_target", "artifact": "example_successor_continuity_verdict.json", "field_or_key": "changed_line_items", "role": "changed_family_slice", "claim_classes": ["changed_family_identity"], "why_stop_here": "The emitted compact diff sentence also names which changed family the deltas belong to."}
                ],
                "segments": [
                    {"segment_key": "fallback_obs_delta", "surface_span": "fallback p_obs_upper 0.02 -> 0.015", "claim_classes": ["numeric_delta", "changed_family_identity"], "terminal_target_keys": ["numeric_delta_target", "changed_family_target"], "why": "This span asserts one fallback numeric change and identifies the changed family as fallback."},
                    {"segment_key": "fallback_summary_delta", "surface_span": "fallback summary bits 0.056346 -> 0.042403", "claim_classes": ["numeric_delta", "changed_family_identity"], "terminal_target_keys": ["numeric_delta_target", "changed_family_target"], "why": "This span asserts the fallback-summary delta and still belongs to the changed fallback family."},
                    {"segment_key": "total_summary_delta", "surface_span": "total summary bits per lookup 0.265905 -> 0.265184", "claim_classes": ["numeric_delta"], "terminal_target_keys": ["numeric_delta_target"], "why": "This span carries only the aggregate numeric delta; changed-family identity is already discharged earlier."}
                ],
                "surface_assembly": [
                    {"kind": "literal", "value": "Compact diff: "},
                    {"kind": "segment", "value": "fallback_obs_delta"},
                    {"kind": "literal", "value": "; "},
                    {"kind": "segment", "value": "fallback_summary_delta"},
                    {"kind": "literal", "value": "; "},
                    {"kind": "segment", "value": "total_summary_delta"},
                    {"kind": "literal", "value": "."}
                ],
                "trace_steps": [
                    {"step": "emit", "artifact": "example_successor_normal_form.json", "field_or_key": "resolution_examples[compact_numeric_diff].surface_text", "why": "Reusable compact diff sentence as emitted downstream."},
                    {"step": "clause", "artifact": "example_successor_clause_pack.json", "field_or_key": "clauses[compact_diff_clause]", "why": "Declared compact diff clause and cite path."},
                    {"step": "quote", "artifact": "example_successor_quote_map.json", "field_or_key": "quote_targets[compact_numeric_diff]", "why": "Pins the exact diff field to quote."},
                    {"step": "cite", "artifact": "example_successor_citation_map.json", "field_or_key": "queries[compact_diff_summary]", "why": "Names the smallest sufficient citation target for the diff sentence."},
                    {"step": "narrow", "artifact": "example_compare_report.json", "field_or_key": "observed_diffs", "why": "Terminal numeric diff field used by the wrapper sentence."},
                    {"step": "narrow", "artifact": "example_successor_continuity_verdict.json", "field_or_key": "changed_line_items", "why": "Names the exact replayed surface slice referred to by the compact diff sentence."}
                ]
            },
        ],
        "resolution_rule": "Move rightward only to compress downstream prose. If any clause is challenged, follow the typed leftward trace from emitted text to clause, quote, citation, support, and then to the narrower compare, continuity, or closure objects.",
        "boundary_rule": "This object owns only the auditable downstream suffix of the release spine. It never replaces compare, replay, continuity, closure, or the derivation graph.",
        "note": "Derived downstream normal form for one concrete successor comparison. It freezes the summarize->support->cite->quote->clause suffix so later notes can reuse one stable sentence-normalization object without hiding the narrower maintenance evidence, while the companion sentence-lock ledger separately owns pair-anchored reuse policy, object-cut recheck, regeneration boundaries, and visible inline-provenance modes."
    }
    normal_form_out = ART / "example_successor_normal_form.json"
    normal_form_payload = json.dumps(normal_form, indent=2, sort_keys=True) + "\n"
    normal_form_out.write_text(normal_form_payload, encoding="utf-8")
    normal_form_digest = sha256_bytes(normal_form_payload.encode("utf-8"))

    challenge_surface_hooks = {
        "challenge_surface_hooks_id": CHALLENGE_SURFACE_HOOKS_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_normal_form_id": normal_form["normal_form_id"],
        "successor_challenge_stop_profiles_id": challenge_stop_profiles["challenge_stop_profiles_id"],
        "successor_challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "note_version": artifact_inventory.get("note_version"),
        "surface_hook_contract": {
            "surface_hook_fields": ["surface_hook_key", "sentence_family", "normal_form_example_key", "piece_key", "binding_kind", "segment_keys", "carried_claim_classes", "terminal_target_keys", "why"],
            "binding_kind_values": ["exclusive", "shared", "mixed"],
            "hook_lookup_rule": "Every surface hook key named by the companion coverage certificate must resolve to one unique sentence-family/piece binding in this ledger.",
            "segment_rule": "Every listed segment key must exist in the companion downstream normal form for the same sentence family.",
            "claim_class_rule": "Every carried claim class must be a claim class carried by at least one listed segment.",
            "terminal_target_rule": "Every listed terminal target key must exist in the companion downstream normal form and discharge the claim classes attributed to the hook.",
            "binding_kind_rule": "exclusive means the listed segments realize only this piece in the worked sentence; shared means all listed segments are also reused by another piece hook; mixed means some listed segments are shared while others are piece-exclusive."
        },
        "surface_hooks": [
            {
                "surface_hook_key": "public_status_sentence_continuity_piece_surface",
                "sentence_family": "public_status_sentence",
                "normal_form_example_key": "public_status_sentence",
                "piece_key": "continuity_piece",
                "binding_kind": "exclusive",
                "segment_keys": ["status_continuity_half"],
                "carried_claim_classes": ["continuity_decision"],
                "terminal_target_keys": ["continuity_decision_target"],
                "why": "The continuity half is carried by one sentence segment that is exclusive to that piece in the public wrapper."
            },
            {
                "surface_hook_key": "public_status_sentence_closure_piece_surface",
                "sentence_family": "public_status_sentence",
                "normal_form_example_key": "public_status_sentence",
                "piece_key": "closure_piece",
                "binding_kind": "exclusive",
                "segment_keys": ["status_closure_half"],
                "carried_claim_classes": ["closure_status"],
                "terminal_target_keys": ["closure_status_target"],
                "why": "The closure half is carried by one sentence segment that is exclusive to that piece in the public wrapper."
            },
            {
                "surface_hook_key": "compact_numeric_diff_diff_delta_piece_surface",
                "sentence_family": "compact_numeric_diff",
                "normal_form_example_key": "compact_numeric_diff",
                "piece_key": "diff_delta_piece",
                "binding_kind": "mixed",
                "segment_keys": ["fallback_obs_delta", "fallback_summary_delta", "total_summary_delta"],
                "carried_claim_classes": ["numeric_delta"],
                "terminal_target_keys": ["numeric_delta_target"],
                "why": "The numeric-delta piece uses two shared fallback spans plus one aggregate span that is exclusive to the numeric total."
            },
            {
                "surface_hook_key": "compact_numeric_diff_changed_family_piece_surface",
                "sentence_family": "compact_numeric_diff",
                "normal_form_example_key": "compact_numeric_diff",
                "piece_key": "changed_family_piece",
                "binding_kind": "shared",
                "segment_keys": ["fallback_obs_delta", "fallback_summary_delta"],
                "carried_claim_classes": ["changed_family_identity"],
                "terminal_target_keys": ["changed_family_target"],
                "why": "Changed-family identity is carried only by the two fallback spans, both of which are shared with the numeric-delta piece."
            }
        ],
        "note": "Derived sentence-family surface-hook ledger for one concrete successor comparison. It says exactly which emitted segments realize each covered semantic piece, including when the same segment family is shared across multiple pieces."
    }
    challenge_surface_hooks_out = ART / "example_successor_challenge_surface_hooks.json"
    challenge_surface_hooks_payload = json.dumps(challenge_surface_hooks, indent=2, sort_keys=True) + "\n"
    challenge_surface_hooks_out.write_text(challenge_surface_hooks_payload, encoding="utf-8")
    challenge_surface_hooks_digest = sha256_bytes(challenge_surface_hooks_payload.encode("utf-8"))

    challenge_coverage = {
        "challenge_coverage_id": CHALLENGE_COVERAGE_ID,
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "compare_report_id": report["report_id"],
        "successor_normal_form_id": normal_form["normal_form_id"],
        "successor_challenge_stop_profiles_id": challenge_stop_profiles["challenge_stop_profiles_id"],
        "successor_challenge_routes_id": challenge_routes["challenge_routes_id"],
        "successor_challenge_branches_id": challenge_branches["challenge_branches_id"],
        "successor_challenge_surface_hooks_id": challenge_surface_hooks["challenge_surface_hooks_id"],
        "note_version": artifact_inventory.get("note_version"),
        "coverage_contract": {
            "sentence_family_fields": ["sentence_family", "normal_form_example_key", "question_key", "required_audiences", "coverage_entries", "why"],
            "coverage_entry_fields": ["piece_key", "coverage_mode", "required_surface_hook_keys", "required_route_keys", "required_branch_keys", "approved_terminal_fields", "why"],
            "surface_hook_rule": "If coverage_mode is surface, every listed surface hook key must exist in the companion surface-hook ledger for the same sentence family and piece.",
            "support_only_rule": "If coverage_mode is support_only, the piece remains auditable through declared routes and branches even though no surface hook is claimed for it.",
            "audience_route_rule": "Every required route key must belong to one of the required audiences, and every required branch key must witness the same route-plus-piece pair.",
            "terminal_rule": "Approved terminal fields named here must agree with the terminal stop fields reached by the declared branches."
        },
        "sentence_families": [
            {
                "sentence_family": "public_status_sentence",
                "normal_form_example_key": "public_status_sentence",
                "question_key": "public_status_sentence",
                "required_audiences": ["release_note", "referee"],
                "coverage_entries": [
                    {
                        "piece_key": "continuity_piece",
                        "coverage_mode": "surface",
                        "required_surface_hook_keys": ["public_status_sentence_continuity_piece_surface"],
                        "required_route_keys": ["release_note_public_status_sentence", "referee_public_status_sentence"],
                        "required_branch_keys": ["release_note_public_status_sentence_continuity_piece", "referee_public_status_sentence_continuity_piece"],
                        "approved_terminal_fields": [{"path": "example_successor_continuity_verdict.json", "field": "continuity_decision"}],
                        "why": "The public wrapper counts as carrying the continuity piece for release-note and referee readers."
                    },
                    {
                        "piece_key": "closure_piece",
                        "coverage_mode": "surface",
                        "required_surface_hook_keys": ["public_status_sentence_closure_piece_surface"],
                        "required_route_keys": ["release_note_public_status_sentence", "referee_public_status_sentence"],
                        "required_branch_keys": ["release_note_public_status_sentence_closure_piece", "referee_public_status_sentence_closure_piece"],
                        "approved_terminal_fields": [{"path": "example_publication_closure_verdict.json", "field": "closure_status"}],
                        "why": "The public wrapper counts as carrying the package-closure piece for release-note and referee readers."
                    }
                ],
                "why": "This sentence family is the outward-facing public-status carrier, so coverage is limited to the audiences that actually start from that sentence family."
            },
            {
                "sentence_family": "compact_numeric_diff",
                "normal_form_example_key": "compact_numeric_diff",
                "question_key": "compact_diff_summary",
                "required_audiences": ["release_note", "auditor"],
                "coverage_entries": [
                    {
                        "piece_key": "diff_delta_piece",
                        "coverage_mode": "surface",
                        "required_surface_hook_keys": ["compact_numeric_diff_diff_delta_piece_surface"],
                        "required_route_keys": ["release_note_compact_diff", "auditor_compact_diff"],
                        "required_branch_keys": ["release_note_compact_diff_diff_delta_piece", "auditor_compact_diff_diff_delta_piece"],
                        "approved_terminal_fields": [{"path": "example_compare_report.json", "field": "observed_diffs"}],
                        "why": "The compact diff sentence counts as carrying the numeric deltas for release-note and auditor readers."
                    },
                    {
                        "piece_key": "changed_family_piece",
                        "coverage_mode": "surface",
                        "required_surface_hook_keys": ["compact_numeric_diff_changed_family_piece_surface"],
                        "required_route_keys": ["release_note_compact_diff", "auditor_compact_diff"],
                        "required_branch_keys": ["release_note_compact_diff_changed_family_piece", "auditor_compact_diff_changed_family_piece"],
                        "approved_terminal_fields": [{"path": "example_successor_continuity_verdict.json", "field": "changed_line_items"}],
                        "why": "The compact diff sentence also counts as carrying changed-family identity, but only through the shared fallback spans named in the companion surface-hook ledger."
                    },
                    {
                        "piece_key": "recompute_piece",
                        "coverage_mode": "support_only",
                        "required_surface_hook_keys": [],
                        "required_route_keys": ["release_note_compact_diff", "auditor_compact_diff"],
                        "required_branch_keys": ["release_note_compact_diff_recompute_piece", "auditor_compact_diff_recompute_piece"],
                        "approved_terminal_fields": [{"path": "example_verifier_report.json", "field": "recomputed"}],
                        "why": "The compact diff sentence does not surface the recomputation witness, but both audiences must still be able to escalate to it if challenged."
                    }
                ],
                "why": "This sentence family is the terse numeric diff carrier, so coverage is limited to the audiences that begin from the compact diff path."
            }
        ],
        "note": "Derived sentence-family challenge-coverage certificate for one concrete successor comparison. It says which semantic pieces count as covered for which audiences and which support-only hooks remain auditable through route-plus-piece branches; exact piece-to-segment realization lives in the companion surface-hook ledger."
    }
    challenge_coverage_out = ART / "example_successor_challenge_coverage.json"
    challenge_coverage_payload = json.dumps(challenge_coverage, indent=2, sort_keys=True) + "\n"
    challenge_coverage_out.write_text(challenge_coverage_payload, encoding="utf-8")
    challenge_coverage_digest = sha256_bytes(challenge_coverage_payload.encode("utf-8"))


    files = support_manifest.get("files", [])

    def manifest_row(path, sha):
        if path.startswith("../"):
            base = "paper_root"
            repo_rel = (ROOT / path[3:]).relative_to(ROOT.parents[2]).as_posix()
        else:
            base = "artifact_root"
            repo_rel = (ART / path).relative_to(ROOT.parents[2]).as_posix()
        return {"path": path, "base": base, "repo_relative_path": repo_rel, "sha256": sha}

    def upsert(path, sha):
        row = manifest_row(path, sha)
        for entry in files:
            if entry.get("path") == path:
                entry.update(row)
                return
        files.append(row)

    upsert("example_compare_report.json", digest)
    upsert("example_successor_continuity_verdict.json", verdict_digest)
    upsert("example_release_closure_ledger.json", closure_ledger_digest)
    upsert("example_publication_closure_verdict.json", closure_digest)
    upsert("example_successor_status_envelope.json", status_digest)
    upsert("example_successor_lineage_notice.json", lineage_digest)
    upsert("example_successor_derivation_graph.json", derivation_digest)
    upsert("example_successor_claim_support_map.json", claim_map_digest)
    upsert("example_successor_citation_map.json", citation_map_digest)
    upsert("example_successor_challenge_stop_profiles.json", challenge_stop_profiles_digest)
    upsert("example_successor_challenge_routes.json", challenge_routes_digest)
    upsert("example_successor_challenge_branches.json", challenge_branches_digest)
    upsert("example_successor_challenge_coverage.json", challenge_coverage_digest)
    upsert("example_successor_challenge_surface_hooks.json", challenge_surface_hooks_digest)
    upsert("example_successor_quote_map.json", quote_map_digest)
    upsert("example_successor_clause_pack.json", clause_pack_digest)
    upsert("example_release_spine.json", release_spine_digest)
    upsert("example_release_stage_walkthrough.json", release_stage_walkthrough_digest)
    upsert("example_successor_sentence_locks.json", sentence_locks_digest)
    upsert("example_successor_normal_form.json", normal_form_digest)
    support_manifest["files"] = sorted(files, key=lambda x: x["path"])
    (ART / "support_manifest.json").write_text(json.dumps(support_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ensure_inventory_entry(artifact_inventory, "example_release_closure_ledger.json", "role-by-role closure ledger for one successor package", ["auditor", "maintainer", "referee"])
    ensure_inventory_entry(artifact_inventory, "example_publication_closure_verdict.json", "successor publication-package closure verdict adjunct", ["user", "auditor", "maintainer"])
    ensure_inventory_entry(artifact_inventory, "example_successor_status_envelope.json", "narrow summary-stage status envelope for one successor comparison", ["user", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_lineage_notice.json", "outward-facing successor lineage notice adjunct", ["user", "maintainer", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_derivation_graph.json", "maintenance DAG for one successor comparison", ["maintainer", "referee", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_claim_support_map.json", "statement-to-evidence support map for one successor comparison", ["user", "referee", "maintainer"])
    ensure_inventory_entry(artifact_inventory, "example_successor_citation_map.json", "minimal-citation map for one successor comparison", ["maintainer", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_challenge_stop_profiles.json", "question-keyed challenge stop profiles for one successor comparison", ["maintainer", "referee", "release_note", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_challenge_routes.json", "audience-keyed challenge routes for one successor comparison", ["maintainer", "referee", "release_note", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_challenge_branches.json", "piece-keyed challenge branches for one successor comparison", ["maintainer", "referee", "release_note", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_challenge_coverage.json", "sentence-family challenge-coverage certificate for one successor comparison", ["maintainer", "referee", "release_note", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_challenge_surface_hooks.json", "piece-to-segment surface-hook ledger for one successor comparison", ["maintainer", "referee", "release_note", "auditor"])
    ensure_inventory_entry(artifact_inventory, "example_successor_quote_map.json", "exact-field quote map for one successor comparison", ["maintainer", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_clause_pack.json", "canonical clause pack for one successor comparison", ["maintainer", "release_note", "referee"])
    ensure_inventory_entry(artifact_inventory, "example_release_spine.json", "stable stage map for successor maintenance", ["maintainer", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_release_stage_walkthrough.json", "stage-by-stage worked release walk for one successor comparison", ["maintainer", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_sentence_locks.json", "pair-anchored sentence-lock ledger for one successor comparison", ["maintainer", "referee", "release_note"])
    ensure_inventory_entry(artifact_inventory, "example_successor_normal_form.json", "downstream sentence-normalization suffix for one successor comparison", ["maintainer", "referee", "release_note"])
    # de-duplicate in case either path was already present
    seen_paths = set()
    for group in artifact_inventory.get("groups", []):
        deduped = []
        for entry in group.get("entries", []):
            path = entry.get("path")
            if path in {"example_release_closure_ledger.json", "example_publication_closure_verdict.json", "example_successor_status_envelope.json", "example_successor_lineage_notice.json", "example_successor_derivation_graph.json", "example_successor_claim_support_map.json", "example_successor_citation_map.json", "example_successor_challenge_stop_profiles.json", "example_successor_challenge_routes.json", "example_successor_challenge_branches.json", "example_successor_challenge_coverage.json", "example_successor_challenge_surface_hooks.json", "example_successor_quote_map.json", "example_successor_clause_pack.json", "example_release_spine.json", "example_release_stage_walkthrough.json", "example_successor_normal_form.json"}:
                if path in seen_paths:
                    continue
                seen_paths.add(path)
            deduped.append(entry)
        group["entries"] = deduped
    (ART / "example_artifact_inventory.json").write_text(json.dumps(artifact_inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(out)
    print(verdict_out)
    print(closure_ledger_out)
    print(closure_out)
    print(status_out)
    print(lineage_out)
    print(derivation_out)
    print(claim_map_out)
    print(citation_map_out)
    print(challenge_stop_profiles_out)
    print(challenge_routes_out)
    print(challenge_branches_out)
    print(challenge_coverage_out)
    print(challenge_surface_hooks_out)
    print(quote_map_out)
    print(clause_pack_out)
    print(release_spine_out)
    print(release_stage_walkthrough_out)
    print(sentence_locks_out)
    print(normal_form_out)


if __name__ == "__main__":
    main()
