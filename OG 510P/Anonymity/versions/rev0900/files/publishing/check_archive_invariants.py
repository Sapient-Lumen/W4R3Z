#!/usr/bin/env python3
"""Check semantic archive invariants that should survive future refactors."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def record(checks: list[dict], invariant_id: str, ok: bool, details: str):
    checks.append({"id": invariant_id, "status": "pass" if ok else "fail", "details": details})


def check(root: pathlib.Path) -> dict:
    canonical = load_json(root / "publishing/CANONICAL_POLICY.json")
    citation_heads = load_json(root / "published/citation_heads.json")
    legacy_links = load_json(root / "published/legacy_published_links.json")
    public_surface = load_json(root / "published/PUBLIC_SURFACE.json")
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    revision_receipt = load_json(root / "REVISION_RECEIPT.json")
    archive_index = load_json(root / "ARCHIVE_INDEX.json")
    queue_index = load_json(root / "release_queue/QUEUE_INDEX.json")
    surface_schema = load_json(root / "reports/surface_schema_validation.json")
    transient = load_json(root / "reports/transient_surface_audit.json")
    manifest_verify = load_json(root / "reports/manifest_sha256_verification.json")
    manifest_coverage = load_json(root / "reports/manifest_coverage_audit.json")
    context_budget_path = root / "reports/context_pack_budget.json"
    context_budget = load_json(context_budget_path) if context_budget_path.exists() else {"status": "missing", "summary": {"checks_failed": 1}}
    transfer_source_receipt = load_json(root / "reports/transfer_source_receipt.json")
    support_manifest_integrity = load_json(root / "reports/support_manifest_integrity.json")
    review_inventory_coverage = load_json(root / "reports/review_inventory_coverage.json")
    citation_closure = load_json(root / "reports/citation_closure_audit.json")
    release_readiness = load_json(root / "reports/release_readiness_audit.json")
    evidence_pack_audit = load_json(root / "reports/evidence_pack_audit.json")
    evidence_pack_integrity = load_json(root / "reports/evidence_pack_integrity.json")
    freeze_compile_witness = load_json(root / "reports/freeze_compile_witness.json")
    freeze_packet_integrity = load_json(root / "reports/freeze_packet_integrity.json")
    publication_boundary = load_json(root / "reports/publication_boundary.json")
    release_freeze_plan = load_json(root / "release_queue/NEXT_RELEASE_FREEZE_PLAN.json")
    review_inventory_integrity = load_json(root / "reports/review_inventory_integrity.json")
    operator_command_hygiene = load_json(root / "reports/operator_command_hygiene.json")
    assurance_catalog_integrity = load_json(root / "reports/assurance_catalog_integrity.json")
    tooling_inventory = load_json(root / "publishing/TOOLING_INVENTORY.json")
    tooling_inventory_integrity = load_json(root / "reports/tooling_inventory_integrity.json")
    report_schema_coverage = load_json(root / "reports/report_schema_coverage.json")
    rebuild_fixed_point_coverage = load_json(root / "reports/rebuild_fixed_point_coverage.json")
    publication_decision_template = load_json(root / "reports/publication_decision_template.json")
    publication_decision_authorization = load_json(root / "reports/publication_decision_authorization.json")
    archive_index_integrity = load_json(root / "reports/archive_index_integrity.json")
    report_identity_coverage = load_json(root / "reports/report_identity_coverage.json")
    report_warning_policy = load_json(root / "reports/report_warning_policy.json")
    publication_artifact_quarantine = load_json(root / "reports/publication_artifact_quarantine.json")
    publication_target_portability = load_json(root / "reports/publication_target_portability.json")
    path_portability = load_json(root / "reports/path_portability.json")
    archive_packaging_reproducibility = load_json(root / "reports/archive_packaging_reproducibility.json")
    archive_entry_security = load_json(root / "reports/archive_entry_security.json")
    bundle_identity_consistency = load_json(root / "reports/bundle_identity_consistency.json")
    control_surface_path_integrity = load_json(root / "reports/control_surface_path_integrity.json")
    duplicate_content_policy = load_json(root / "reports/duplicate_content_policy.json")
    tex_source_safety = load_json(root / "reports/tex_source_safety.json")
    secret_material_quarantine = load_json(root / "reports/secret_material_quarantine.json")
    makefile_target_integrity = load_json(root / "reports/makefile_target_integrity.json")
    manifest_canonicality = load_json(root / "reports/manifest_canonicality.json")
    freeze_warning_resolution = load_json(root / "reports/freeze_warning_resolution.json")
    toolchain_fingerprint = load_json(root / "reports/toolchain_fingerprint.json")
    json_surface_catalog = load_json(root / "reports/json_surface_catalog.json")
    queue_note_source_binding = load_json(root / "reports/queue_note_source_binding.json")
    queue_compile_smoke = load_json(root / "reports/queue_compile_smoke.json")
    hold_compile_triage = load_json(root / "release_queue/HOLD_COMPILE_TRIAGE.json")
    unqueued_compile_triage = load_json(root / "release_queue/UNQUEUED_COMPILE_TRIAGE.json")
    published_compile_triage = load_json(root / "published/PUBLISHED_COMPILE_TRIAGE.json")
    auxiliary_tex_compile_triage = load_json(root / "index/AUXILIARY_TEX_COMPILE_TRIAGE.json")
    content_leakage = load_json(root / "reports/content_leakage.json")
    decision_note_integrity = load_json(root / "reports/decision_note_integrity.json")
    schema_catalog_integrity = load_json(root / "reports/schema_catalog_integrity.json")
    tooling_static_integrity = load_json(root / "reports/tooling_static_integrity.json")
    python_entrypoint_smoke = load_json(root / "reports/python_entrypoint_smoke.json")
    json_key_integrity = load_json(root / "reports/json_key_integrity.json")
    text_surface_normalization = load_json(root / "reports/text_surface_normalization.json")
    unicode_control_hygiene = load_json(root / "reports/unicode_control_hygiene.json")
    archive_packaging_recipe = load_json(root / "reports/archive_packaging_recipe.json")
    freeze_toolchain = load_json(root / "reports/freeze_toolchain.json")
    publication_rehearsal = load_json(root / "reports/publication_rehearsal.json")
    research_metadata_integrity = load_json(root / "reports/research_metadata_integrity.json")
    assurance_artifacts = load_json(root / "ASSURANCE_ARTIFACTS.json")
    version_text = (root / "VERSION").read_text(encoding="utf-8").strip()
    latest_decision_md = (root / "release_queue/LATEST_DECISION.md").read_text(encoding="utf-8")
    latest_decision_json = load_json(root / "release_queue/LATEST_DECISION.json")
    invariants = load_json(root / "publishing/archive_invariants.json")

    checks: list[dict] = []

    latest_publication_action = latest_decision_json.get("publication_action")
    publish_decision_count = publication_decision_authorization.get("summary", {}).get("valid_publish_decision_count", 0)
    latest_publication_posture_ok = (
        (latest_publication_action == "none" and "no publication" in latest_decision_md.lower())
        or (latest_publication_action == "publish" and "Publication action: publish" in latest_decision_md and publish_decision_count >= 1)
    )
    record(
        checks,
        "INV-0001",
        canonical.get("default_release_posture") == "hold"
        and canonical.get("allow_zero_publications_in_turn") is True
        and latest_publication_posture_ok,
        f"default_release_posture={canonical.get('default_release_posture')} allow_zero={canonical.get('allow_zero_publications_in_turn')} publication_action={latest_publication_action} valid_publish_decisions={publish_decision_count}",
    )

    record(
        checks,
        "INV-0002",
        citation_heads["summary"]["legacy_public_head_count"] == len(legacy_links.get("canonical_legacy_links", [])) == 5
        and len(citation_heads["current_public_citation_heads"]) == citation_heads["summary"]["legacy_public_head_count"] + citation_heads["summary"].get("new_post_policy_anonymity_head_count", 0),
        f"citation_legacy_count={citation_heads['summary']['legacy_public_head_count']} new_heads={citation_heads['summary'].get('new_post_policy_anonymity_head_count', 0)} current_heads={len(citation_heads['current_public_citation_heads'])} legacy_links={len(legacy_links.get('canonical_legacy_links', []))}",
    )

    frozen = {item["path"] if isinstance(item, dict) else item for item in citation_heads["repo_frozen_noncanonical_entries"]}
    current = {item["path"] if isinstance(item, dict) else item for item in citation_heads["current_public_citation_heads"]}
    public_frozen = set(public_surface["repo_frozen_noncanonical_entries"])
    record(
        checks,
        "INV-0003",
        frozen.isdisjoint(current) and frozen == public_frozen and citation_heads["summary"]["repo_frozen_noncanonical_entry_count"] == len(frozen),
        f"frozen_count={len(frozen)} current_overlap={sorted(frozen & current)} public_surface_frozen_count={len(public_frozen)}",
    )

    published_artifact_policy = canonical.get("published_artifact")
    allowed_published_artifact_policies = {"tex", "tex_plus_evidence_pack_when_artifact_governance_claims_are_made"}
    current_heads_are_tex = all(path.endswith("/paper.tex") for path in current) and all(path.endswith("/paper.tex") for path in public_surface["current_public_citation_heads"])
    artifact_policy_ok = published_artifact_policy in allowed_published_artifact_policies and current_heads_are_tex
    record(checks, "INV-0004", artifact_policy_ok, f"published_artifact={published_artifact_policy} current_head_count={len(current)} current_heads_are_tex={current_heads_are_tex}")

    fail_closed_reports = [
        surface_schema,
        transient,
        manifest_verify,
        manifest_coverage,
        support_manifest_integrity,
        review_inventory_coverage,
        citation_closure,
        release_readiness,
        evidence_pack_audit,
        evidence_pack_integrity,
        freeze_compile_witness,
        review_inventory_integrity,
        operator_command_hygiene,
        assurance_catalog_integrity,
        tooling_inventory_integrity,
        report_schema_coverage,
        rebuild_fixed_point_coverage,
        publication_decision_template,
        publication_decision_authorization,
        archive_index_integrity,
        report_identity_coverage,
        report_warning_policy,
        publication_artifact_quarantine,
        publication_target_portability,
        path_portability,
        archive_packaging_reproducibility,
        archive_entry_security,
        bundle_identity_consistency,
        control_surface_path_integrity,
        duplicate_content_policy,
        tex_source_safety,
        secret_material_quarantine,
        makefile_target_integrity,
        json_surface_catalog,
        queue_note_source_binding,
        queue_compile_smoke,
        hold_compile_triage,
        unqueued_compile_triage,
        published_compile_triage,
        auxiliary_tex_compile_triage,
        content_leakage,
        decision_note_integrity,
        schema_catalog_integrity,
        json_key_integrity,
        text_surface_normalization,
        unicode_control_hygiene,
        tooling_static_integrity,
        python_entrypoint_smoke,
        archive_packaging_recipe,
        freeze_toolchain,
        publication_rehearsal,
        research_metadata_integrity,
    ]
    ok_reports = all(r.get("status") == "pass" for r in fail_closed_reports)
    if context_budget.get("status") != "missing":
        ok_reports = ok_reports and context_budget.get("status") == "pass"
        fail_closed_reports = fail_closed_reports + [context_budget]
    record(checks, "INV-0005", ok_reports, "report_statuses=" + ", ".join(r.get("status", "?") for r in fail_closed_reports))

    transient_ok = transient.get("status") == "pass" and transient.get("summary", {}).get("disallowed_file_count") == 0 and (root / "PRUNING_POLICY.md").exists() and (root / "PRUNED_TRANSIENT.paths").exists()
    record(checks, "INV-0006", transient_ok, f"transient_status={transient.get('status')} disallowed={transient.get('summary', {}).get('disallowed_file_count')}")

    receipt_revision = f"rev{int(revision_receipt['revision']):04d}"
    singular = version_text == release_manifest["revision"] == receipt_revision == archive_index["latest_revision"] == queue_index["generated_for_revision"]
    record(checks, "INV-0007", singular, f"version={version_text} manifest={release_manifest['revision']} receipt={receipt_revision} archive={archive_index['latest_revision']} queue={queue_index['generated_for_revision']}")

    transfer_ok = transfer_source_receipt.get("status") == "pass" and transfer_source_receipt.get("summary", {}).get("checks_failed") == 0 and (root / "TRANSFER_SOURCES.json").exists() and (root / "TRANSFER_INPUTS.sha256").exists()
    record(checks, "INV-0008", transfer_ok, f"transfer_source_receipt_status={transfer_source_receipt.get('status')} failed={transfer_source_receipt.get('summary', {}).get('checks_failed')}")

    support_ok = support_manifest_integrity.get("status") == "pass" and support_manifest_integrity.get("summary", {}).get("checks_failed") == 0
    record(checks, "INV-0009", support_ok, f"support_manifest_integrity_status={support_manifest_integrity.get('status')} failed={support_manifest_integrity.get('summary', {}).get('checks_failed')} file_rows={support_manifest_integrity.get('summary', {}).get('file_rows_checked')}")

    research_paths = list(canonical.get("research_object_metadata", {}).values())
    research_missing = sorted(path for path in research_paths if not (root / path).exists())
    assurance_paths = {path for group in assurance_artifacts.get("groups", []) for path in group.get("paths", [])}
    research_unassured = sorted(path for path in research_paths if path not in assurance_paths)
    research_ok = (
        bool(research_paths)
        and not research_missing
        and not research_unassured
        and research_metadata_integrity.get("status") == "pass"
        and research_metadata_integrity.get("generated_for_revision") == release_manifest["revision"]
        and research_metadata_integrity.get("checked_bundle") == release_manifest["bundle"]
        and research_metadata_integrity.get("summary", {}).get("checks_failed") == 0
    )
    record(checks, "INV-0010", research_ok, f"research_metadata_count={len(research_paths)} missing={research_missing} unassured={research_unassured} integrity_status={research_metadata_integrity.get('status')} integrity_failed={research_metadata_integrity.get('summary', {}).get('checks_failed')}")

    citation_summary = citation_closure.get("summary", {})
    citation_graph = citation_closure.get("global_citation_graph", {})
    malformed_count = citation_summary.get("malformed_bibliography_command_count", citation_summary.get("malformed_bibliography_fragment_count"))
    citation_ok = (
        citation_closure.get("status") == "pass"
        and citation_closure.get("generated_for_revision") == release_manifest["revision"]
        and citation_closure.get("checked_bundle") == release_manifest["bundle"]
        and citation_summary.get("papers_failed") == 0
        and citation_summary.get("globally_undefined_citation_count") == 0
        and malformed_count == 0
        and citation_graph.get("globally_undefined_citation_count") == 0
    )
    record(checks, "INV-0011", citation_ok, f"citation_closure_status={citation_closure.get('status')} papers={citation_summary.get('papers_checked')} failed={citation_summary.get('papers_failed')} global_undefined={citation_summary.get('globally_undefined_citation_count')} malformed={malformed_count}")

    readiness_summary = release_readiness.get("summary", {})
    readiness_counts = readiness_summary.get("release_readiness_counts", {})
    state_counts = readiness_summary.get("state_counts", {})
    published_ready_total = queue_index["summary"]["published_ready"]
    candidate_total = queue_index["summary"]["candidate"]
    published_ready_items = [item for item in release_readiness.get("items", []) if item.get("queue_state") == "published_ready"]
    candidate_items = [item for item in release_readiness.get("items", []) if item.get("queue_state") == "candidate"]
    readiness_ok = (
        release_readiness.get("status") == "pass"
        and release_readiness.get("generated_for_revision") == release_manifest["revision"]
        and release_readiness.get("publication_authorized") is False
        and state_counts.get("published_ready") == published_ready_total
        and state_counts.get("candidate") == candidate_total
        and readiness_counts.get("static_preflight_pass", 0) == published_ready_total
        and readiness_counts.get("not_a_release_target", 0) == candidate_total
        and readiness_counts.get("blocked", 0) == 0
        and readiness_summary.get("duplicate_source_binding_count", 1) == 0
        and readiness_summary.get("expected_counts_match_queue_index") is True
        and readiness_summary.get("malformed_bibliography_command_count", 1) == 0
        and readiness_summary.get("source_hash_missing_count", 1) == 0
        and readiness_summary.get("source_hash_mismatch_count", 1) == 0
        and readiness_summary.get("source_hash_bound_count", 0) == (published_ready_total + candidate_total)
        and not readiness_summary.get("blocker_category_counts")
        and all(item.get("release_readiness") == "static_preflight_pass" and item.get("blocker_count") == 0 for item in published_ready_items)
        and all(item.get("release_readiness") == "not_a_release_target" and item.get("blocker_count") == 0 for item in candidate_items)
    )
    record(checks, "INV-0012", readiness_ok, f"release_readiness_status={release_readiness.get('status')} published_ready={published_ready_total} static_pass={readiness_counts.get('static_preflight_pass', 0)} candidate={candidate_total} not_targets={readiness_counts.get('not_a_release_target', 0)} source_hash_bound={readiness_summary.get('source_hash_bound_count')} missing={readiness_summary.get('source_hash_missing_count')} mismatch={readiness_summary.get('source_hash_mismatch_count')} publication_authorized={release_readiness.get('publication_authorized')}")

    review_summary = review_inventory_integrity.get("summary", {})
    review_inventory_ok = (
        review_inventory_integrity.get("status") == "pass"
        and review_inventory_integrity.get("generated_for_revision") == release_manifest["revision"]
        and review_summary.get("checks_failed") == 0
        and review_summary.get("sha256_prefix_mismatch_count") == 0
        and review_summary.get("duplicate_source_tex_count") == 0
        and review_summary.get("inventory_entry_count") == queue_index["summary"].get("reviewable_unpublished_papers")
    )
    record(checks, "INV-0013", review_inventory_ok, f"review_inventory_status={review_inventory_integrity.get('status')} entries={review_summary.get('inventory_entry_count')} sha_mismatches={review_summary.get('sha256_prefix_mismatch_count')} duplicates={review_summary.get('duplicate_source_tex_count')} unqueued={review_summary.get('unqueued_inventory_entry_count')}")

    command_summary = operator_command_hygiene.get("summary", {})
    command_hygiene_ok = (
        operator_command_hygiene.get("status") == "pass"
        and operator_command_hygiene.get("generated_for_revision") == release_manifest["revision"]
        and command_summary.get("unsafe_command_line_count") == 0
    )
    record(checks, "INV-0014", command_hygiene_ok, f"operator_command_hygiene_status={operator_command_hygiene.get('status')} unsafe_lines={command_summary.get('unsafe_command_line_count')} checked_files={command_summary.get('checked_file_count')}")

    evidence_summary = evidence_pack_audit.get("summary", {})
    evidence_gate = evidence_pack_audit.get("next_release_evidence_gate", {})
    recommended_source = release_readiness.get("next_release_recommendation", {}).get("source_tex")
    evidence_ok = (
        evidence_pack_audit.get("status") == "pass"
        and evidence_pack_audit.get("generated_for_revision") == release_manifest["revision"]
        and evidence_pack_audit.get("publication_authorized") is False
        and evidence_summary.get("checked_item_count") == (published_ready_total + candidate_total)
        and evidence_summary.get("missing_evidence_warning_count") == 0
        and evidence_summary.get("freeze_gate_required_if_selected_count", 0) >= evidence_summary.get("artifact_governance_likely_count", 0)
        and evidence_summary.get("evidence_pack_integrity_status") == "pass"
        and evidence_gate.get("source_tex") == recommended_source
        and evidence_gate.get("status") in {"pending_attach_or_waive", "attached_evidence_pack"}
        and (evidence_gate.get("publication_blocking_until_resolved") is True or bool(evidence_gate.get("evidence_pack_manifest")))
    )
    record(checks, "INV-0015", evidence_ok, f"evidence_status={evidence_pack_audit.get('status')} checked={evidence_summary.get('checked_item_count')} likely={evidence_summary.get('artifact_governance_likely_count')} attached={evidence_summary.get('evidence_pack_attached_count')} next_gate={evidence_gate.get('status')} publication_authorized={evidence_pack_audit.get('publication_authorized')}")

    freeze_summary = release_freeze_plan.get("summary", {})
    selected_source = release_freeze_plan.get("selected_source", {}) or {}
    direct_preflight = release_freeze_plan.get("direct_preflight", {}) or {}
    freeze_gates = {row.get("name"): row for row in release_freeze_plan.get("gates", []) if isinstance(row, dict)}
    evidence_resolution_gate = freeze_gates.get("evidence_pack_resolution", {})
    evidence_resolution_pending = (
        evidence_resolution_gate.get("status") == "pending"
        and evidence_resolution_gate.get("blocking") is True
        and release_freeze_plan.get("evidence_gate", {}).get("status") == "pending_attach_or_waive"
        and release_freeze_plan.get("evidence_gate", {}).get("publication_blocking_until_resolved") is True
    )
    freeze_ok = (
        release_freeze_plan.get("status") in {"dry_run_pass_pending_manual_gates", "ready_for_explicit_publication_decision"}
        and release_freeze_plan.get("generated_for_revision") == release_manifest["revision"]
        and release_freeze_plan.get("checked_bundle") == release_manifest["bundle"]
        and release_freeze_plan.get("publication_authorized") is False
        and selected_source.get("source_tex") == recommended_source
        and selected_source.get("source_sha256") == release_readiness.get("next_release_recommendation", {}).get("source_sha256")
        and direct_preflight.get("status") == "pass"
        and (evidence_resolution_gate.get("status") == "pass" or evidence_resolution_pending)
        and freeze_gates.get("manual_clean_latex_compile", {}).get("status") in {"pass", "pending"}
        and freeze_summary.get("failed_gates") == 0
        and freeze_summary.get("pending_gates", 0) >= 1
    )
    record(checks, "INV-0016", freeze_ok, f"freeze_status={release_freeze_plan.get('status')} selected={selected_source.get('source_tex')} passed={freeze_summary.get('passed_gates')} pending={freeze_summary.get('pending_gates')} failed={freeze_summary.get('failed_gates')} evidence_gate={freeze_gates.get('evidence_pack_resolution', {}).get('status')} compile_gate={freeze_gates.get('manual_clean_latex_compile', {}).get('status')} publication_authorized={release_freeze_plan.get('publication_authorized')}")

    epi_summary = evidence_pack_integrity.get("summary", {})
    epi_ok = (
        evidence_pack_integrity.get("status") == "pass"
        and evidence_pack_integrity.get("generated_for_revision") == release_manifest["revision"]
        and evidence_pack_integrity.get("checked_bundle") == release_manifest["bundle"]
        and evidence_pack_integrity.get("publication_authorized") is False
        and epi_summary.get("checks_failed") == 0
        and epi_summary.get("attached_entry_count", 0) >= 1
    )
    record(checks, "INV-0017", epi_ok, f"evidence_pack_integrity_status={evidence_pack_integrity.get('status')} registry_entries={epi_summary.get('registry_entry_count')} attached={epi_summary.get('attached_entry_count')} failed={epi_summary.get('checks_failed')}")

    compile_summary = freeze_compile_witness.get("summary", {})
    compile_gate_status = freeze_compile_witness.get("compile_gate_status")
    compile_gate_closed = (
        compile_gate_status == "pass"
        and compile_summary.get("clean_final_compile") is True
        and compile_summary.get("deterministic_compile_evidence") is True
        and compile_summary.get("compile_gate_closed") is True
    )
    compile_gate_refresh_pending = (
        compile_gate_status == "pending_current_toolchain_refresh"
        and compile_summary.get("clean_final_compile") is True
        and freeze_compile_witness.get("publication_blocking_until_refreshed") is True
    )
    compile_gate_evidence_pending = (
        compile_gate_status == "pending_evidence_pack_attachment"
        and freeze_compile_witness.get("witness_type") == "pending_unstaged_source_no_compile_attempt"
        and compile_summary.get("pending_unstaged_source") is True
        and compile_summary.get("clean_final_compile") is False
        and compile_summary.get("deterministic_compile_evidence") is False
        and compile_summary.get("compile_run_count") == 0
        and compile_summary.get("pending_items", 0) >= 1
        and freeze_compile_witness.get("publication_blocking_until_refreshed") is True
    )
    compile_ok = (
        freeze_compile_witness.get("status") == "pass"
        and freeze_compile_witness.get("generated_for_revision") == release_manifest["revision"]
        and freeze_compile_witness.get("checked_bundle") == release_manifest["bundle"]
        and freeze_compile_witness.get("publication_authorized") is False
        and freeze_compile_witness.get("selected_source") == recommended_source
        and compile_summary.get("checks_failed") == 0
        and compile_summary.get("witness_present") is True
        and compile_summary.get("witness_current_revision") is True
        and compile_summary.get("source_bound") is True
        and (compile_gate_closed or compile_gate_refresh_pending or compile_gate_evidence_pending)
    )
    record(checks, "INV-0018", compile_ok, f"compile_witness_status={freeze_compile_witness.get('status')} gate={compile_gate_status} source={freeze_compile_witness.get('selected_source')} current_revision={compile_summary.get('witness_current_revision')} clean_final_compile={compile_summary.get('clean_final_compile')} deterministic={compile_summary.get('deterministic_compile_evidence')} failed={compile_summary.get('checks_failed')}")

    freeze_packet_summary = freeze_packet_integrity.get("summary", {})
    freeze_packet_ok = (
        freeze_packet_integrity.get("status") == "pass"
        and freeze_packet_integrity.get("generated_for_revision") == release_manifest["revision"]
        and freeze_packet_integrity.get("checked_bundle") == release_manifest["bundle"]
        and freeze_packet_integrity.get("publication_authorized") is False
        and freeze_packet_summary.get("checks_failed") == 0
        and freeze_packet_summary.get("materialized_entry_count", 0) >= 1
        and freeze_packet_summary.get("unregistered_packet_dir_count", 1) == 0
    )
    record(checks, "INV-0019", freeze_packet_ok, f"freeze_packet_status={freeze_packet_integrity.get('status')} materialized={freeze_packet_summary.get('materialized_entry_count')} unregistered={freeze_packet_summary.get('unregistered_packet_dir_count')} failed={freeze_packet_summary.get('checks_failed')}")

    publication_boundary_summary = publication_boundary.get("summary", {})
    publication_boundary_ok = (
        publication_boundary.get("status") == "pass"
        and publication_boundary.get("generated_for_revision") == release_manifest["revision"]
        and publication_boundary.get("checked_bundle") == release_manifest["bundle"]
        and publication_boundary.get("publication_authorized") is False
        and publication_boundary_summary.get("checks_failed") == 0
        and publication_boundary_summary.get("legacy_public_head_count") == 5
        and publication_boundary_summary.get("repo_frozen_noncanonical_entry_count") == 1
        and publication_boundary_summary.get("unknown_published_tex_count") == 0
        and publication_boundary_summary.get("new_post_policy_anonymity_head_count") == citation_heads.get("summary", {}).get("new_post_policy_anonymity_head_count", 0)
    )
    record(checks, "INV-0020", publication_boundary_ok, f"publication_boundary_status={publication_boundary.get('status')} legacy={publication_boundary_summary.get('legacy_public_head_count')} frozen={publication_boundary_summary.get('repo_frozen_noncanonical_entry_count')} new={publication_boundary_summary.get('new_post_policy_anonymity_head_count')} unknown_tex={publication_boundary_summary.get('unknown_published_tex_count')} failed={publication_boundary_summary.get('checks_failed')}")

    decision_template_summary = publication_decision_template.get("summary", {})
    decision_template_ok = (
        publication_decision_template.get("status") == "pass"
        and publication_decision_template.get("generated_for_revision") == release_manifest["revision"]
        and publication_decision_template.get("checked_bundle") == release_manifest["bundle"]
        and publication_decision_template.get("publication_authorized") is False
        and decision_template_summary.get("checks_failed") == 0
        and decision_template_summary.get("required_fragments_present", 0) >= 13
    )
    record(checks, "INV-0021", decision_template_ok, f"publication_decision_template_status={publication_decision_template.get('status')} required_present={decision_template_summary.get('required_fragments_present')} placeholders={decision_template_summary.get('placeholder_count')} publication_authorized={publication_decision_template.get('publication_authorized')}")

    packaging_summary = archive_packaging_recipe.get("summary", {})
    packaging_ok = (
        archive_packaging_recipe.get("status") == "pass"
        and archive_packaging_recipe.get("generated_for_revision") == release_manifest["revision"]
        and archive_packaging_recipe.get("checked_bundle") == release_manifest["bundle"]
        and archive_packaging_recipe.get("publication_authorized") is False
        and packaging_summary.get("checks_failed") == 0
        and packaging_summary.get("packaging_script_present") is True
        and packaging_summary.get("makefile_package_target_present") is True
        and packaging_summary.get("dry_run_status") == "pass"
    )
    record(checks, "INV-0022", packaging_ok, f"archive_packaging_recipe_status={archive_packaging_recipe.get('status')} dry_run={packaging_summary.get('dry_run_status')} input_files={packaging_summary.get('input_file_count')} manifest_files={packaging_summary.get('manifest_file_count')} failed={packaging_summary.get('checks_failed')}")

    toolchain_summary = freeze_toolchain.get("summary", {})
    toolchain_ok = (
        freeze_toolchain.get("status") == "pass"
        and freeze_toolchain.get("generated_for_revision") == release_manifest["revision"]
        and freeze_toolchain.get("checked_bundle") == release_manifest["bundle"]
        and freeze_toolchain.get("publication_authorized") is False
        and freeze_toolchain.get("toolchain_gate_status") in {"available", "unavailable"}
    )
    record(checks, "INV-0023", toolchain_ok, f"toolchain_status={freeze_toolchain.get('toolchain_gate_status')} available={toolchain_summary.get('available_command_count')} publication_blocking={toolchain_summary.get('publication_blocking_when_compile_witness_not_current')}")

    rehearsal_summary = publication_rehearsal.get("summary", {})
    rehearsal_ok = (
        publication_rehearsal.get("status") == "pass"
        and publication_rehearsal.get("generated_for_revision") == release_manifest["revision"]
        and publication_rehearsal.get("checked_bundle") == release_manifest["bundle"]
        and publication_rehearsal.get("publication_authorized") is False
        and rehearsal_summary.get("surface_failures") == 0
        and publication_rehearsal.get("source_binding", {}).get("source_tex") == recommended_source
    )
    record(checks, "INV-0024", rehearsal_ok, f"rehearsal_status={publication_rehearsal.get('readiness_status')} blockers={rehearsal_summary.get('blocking_gate_count')} surface_failures={rehearsal_summary.get('surface_failures')} publication_authorized={publication_rehearsal.get('publication_authorized')}")

    assurance_summary = assurance_catalog_integrity.get("summary", {})
    assurance_catalog_ok = (
        assurance_catalog_integrity.get("status") == "pass"
        and assurance_catalog_integrity.get("generated_for_revision") == release_manifest["revision"]
        and assurance_catalog_integrity.get("checked_bundle") == release_manifest["bundle"]
        and assurance_catalog_integrity.get("publication_authorized") is False
        and assurance_summary.get("checks_failed") == 0
        and assurance_summary.get("markdown_matches_json") is True
        and assurance_summary.get("missing_path_count") == 0
    )
    record(checks, "INV-0025", assurance_catalog_ok, f"assurance_catalog_status={assurance_catalog_integrity.get('status')} paths={assurance_summary.get('catalog_path_count')} missing={assurance_summary.get('missing_path_count')} markdown_matches_json={assurance_summary.get('markdown_matches_json')} failed={assurance_summary.get('checks_failed')}")

    tooling_summary = tooling_inventory_integrity.get("summary", {})
    actual_tooling_count = len(list((root / "publishing").glob("*.py")))
    tooling_ok = (
        tooling_inventory_integrity.get("status") == "pass"
        and tooling_inventory_integrity.get("generated_for_revision") == release_manifest["revision"]
        and tooling_inventory_integrity.get("checked_bundle") == release_manifest["bundle"]
        and tooling_inventory_integrity.get("publication_authorized") is False
        and tooling_summary.get("checks_failed") == 0
        and tooling_summary.get("actual_script_count") == tooling_summary.get("inventory_script_count") == tooling_inventory.get("script_count") == actual_tooling_count
        and tooling_summary.get("sha256_mismatch_count") == 0
    )
    record(checks, "INV-0026", tooling_ok, f"tooling_inventory_status={tooling_inventory_integrity.get('status')} scripts={tooling_summary.get('actual_script_count')} inventory={tooling_summary.get('inventory_script_count')} sha_mismatches={tooling_summary.get('sha256_mismatch_count')} failed={tooling_summary.get('checks_failed')}")

    report_schema_summary = report_schema_coverage.get("summary", {})
    report_schema_ok = (
        report_schema_coverage.get("status") == "pass"
        and report_schema_coverage.get("generated_for_revision") == release_manifest["revision"]
        and report_schema_coverage.get("checked_bundle") == release_manifest["bundle"]
        and report_schema_coverage.get("publication_authorized") is False
        and report_schema_summary.get("checks_failed") == 0
        and report_schema_summary.get("missing_report_schema_count") == 0
        and report_schema_summary.get("failed_report_schema_count") == 0
        and report_schema_summary.get("report_json_schema_checked_count") == report_schema_summary.get("report_json_count")
    )
    record(checks, "INV-0027", report_schema_ok, f"report_schema_coverage_status={report_schema_coverage.get('status')} reports={report_schema_summary.get('report_json_count')} checked={report_schema_summary.get('report_json_schema_checked_count')} generic={report_schema_summary.get('generic_report_schema_count')} failed={report_schema_summary.get('failed_report_schema_count')}")

    rebuild_fixed_point_summary = rebuild_fixed_point_coverage.get("summary", {})
    rebuild_fixed_point_ok = (
        rebuild_fixed_point_coverage.get("status") == "pass"
        and rebuild_fixed_point_coverage.get("generated_for_revision") == release_manifest["revision"]
        and rebuild_fixed_point_coverage.get("checked_bundle") == release_manifest["bundle"]
        and rebuild_fixed_point_coverage.get("publication_authorized") is False
        and rebuild_fixed_point_summary.get("checks_failed") == 0
        and rebuild_fixed_point_summary.get("missing_tail_target_count") == 0
        and rebuild_fixed_point_summary.get("missing_tail_target_file_count") == 0
        and rebuild_fixed_point_summary.get("duplicate_tail_target_count") == 0
    )
    record(checks, "INV-0028", rebuild_fixed_point_ok, f"rebuild_fixed_point_status={rebuild_fixed_point_coverage.get('status')} tail_outputs={rebuild_fixed_point_summary.get('tail_output_count')} tail_targets={rebuild_fixed_point_summary.get('tail_target_count')} missing={rebuild_fixed_point_summary.get('missing_tail_target_count')} failed={rebuild_fixed_point_summary.get('checks_failed')}")

    decision_auth_summary = publication_decision_authorization.get("summary", {})
    decision_auth_ok = (
        publication_decision_authorization.get("status") == "pass"
        and publication_decision_authorization.get("generated_for_revision") == release_manifest["revision"]
        and publication_decision_authorization.get("checked_bundle") == release_manifest["bundle"]
        and publication_decision_authorization.get("publication_authorized") is False
        and decision_auth_summary.get("checks_failed") == 0
        and decision_auth_summary.get("publish_decision_count") == decision_auth_summary.get("valid_publish_decision_count")
        and decision_auth_summary.get("ready_to_execute_guarded_publication_helper") is False
    )
    record(checks, "INV-0029", decision_auth_ok, f"publication_decision_authorization_status={publication_decision_authorization.get('status')} decisions={decision_auth_summary.get('decision_note_count')} publish_decisions={decision_auth_summary.get('publish_decision_count')} failed={decision_auth_summary.get('checks_failed')} ready_to_execute={decision_auth_summary.get('ready_to_execute_guarded_publication_helper')}")

    archive_index_summary = archive_index_integrity.get("summary", {})
    archive_index_ok = (
        archive_index_integrity.get("status") == "pass"
        and archive_index_integrity.get("generated_for_revision") == release_manifest["revision"]
        and archive_index_integrity.get("checked_bundle") == release_manifest["bundle"]
        and archive_index_integrity.get("publication_authorized") is False
        and archive_index_summary.get("checks_failed") == 0
    )
    record(checks, "INV-0030", archive_index_ok, f"archive_index_integrity_status={archive_index_integrity.get('status')} latest={archive_index.get('latest_revision')} recent_rows={len(archive_index_integrity.get('recent_revision_rows_checked', []))} failed={archive_index_summary.get('checks_failed')}")

    report_identity_summary = report_identity_coverage.get("summary", {})
    report_identity_ok = (
        report_identity_coverage.get("status") == "pass"
        and report_identity_coverage.get("generated_for_revision") == release_manifest["revision"]
        and report_identity_coverage.get("checked_bundle") == release_manifest["bundle"]
        and report_identity_coverage.get("publication_authorized") is False
        and report_identity_summary.get("checks_failed") == 0
        and report_identity_summary.get("identity_bound_report_count") == report_identity_summary.get("report_json_count")
    )
    record(checks, "INV-0031", report_identity_ok, f"report_identity_status={report_identity_coverage.get('status')} reports={report_identity_summary.get('report_json_count')} bound={report_identity_summary.get('identity_bound_report_count')} failed={report_identity_summary.get('checks_failed')}")

    quarantine_summary = publication_artifact_quarantine.get("summary", {})
    quarantine_ok = (
        publication_artifact_quarantine.get("status") == "pass"
        and publication_artifact_quarantine.get("generated_for_revision") == release_manifest["revision"]
        and publication_artifact_quarantine.get("checked_bundle") == release_manifest["bundle"]
        and publication_artifact_quarantine.get("publication_authorized") is False
        and quarantine_summary.get("checks_failed") == 0
        and quarantine_summary.get("disallowed_artifact_count") == 0
        and quarantine_summary.get("shipped_compile_output_digest_hit_count") == 0
    )
    record(checks, "INV-0032", quarantine_ok, f"publication_artifact_quarantine_status={publication_artifact_quarantine.get('status')} disallowed={quarantine_summary.get('disallowed_artifact_count')} compile_digest_hits={quarantine_summary.get('shipped_compile_output_digest_hit_count')} failed={quarantine_summary.get('checks_failed')}")



    path_summary = path_portability.get("summary", {})
    path_portability_ok = (
        path_portability.get("status") == "pass"
        and path_portability.get("generated_for_revision") == release_manifest["revision"]
        and path_portability.get("checked_bundle") == release_manifest["bundle"]
        and path_portability.get("publication_authorized") is False
        and path_summary.get("checks_failed") == 0
        and path_summary.get("nfc_collision_count") == 0
        and path_summary.get("casefold_collision_count") == 0
        and path_summary.get("max_path_bytes", 9999) <= path_summary.get("policy", {}).get("max_path_bytes", 0)
    )
    record(checks, "INV-0033", path_portability_ok, f"path_portability_status={path_portability.get('status')} paths={path_summary.get('path_count')} max_path_bytes={path_summary.get('max_path_bytes')} nfc_collisions={path_summary.get('nfc_collision_count')} casefold_collisions={path_summary.get('casefold_collision_count')} failed={path_summary.get('checks_failed')}")

    reproducibility_summary = archive_packaging_reproducibility.get("summary", {})
    reproducibility_ok = (
        archive_packaging_reproducibility.get("status") == "pass"
        and archive_packaging_reproducibility.get("generated_for_revision") == release_manifest["revision"]
        and archive_packaging_reproducibility.get("checked_bundle") == release_manifest["bundle"]
        and archive_packaging_reproducibility.get("publication_authorized") is False
        and reproducibility_summary.get("checks_failed") == 0
        and reproducibility_summary.get("two_trial_zip_sha256_equal") is True
        and reproducibility_summary.get("two_trial_zip_size_equal") is True
        and reproducibility_summary.get("two_trial_member_metadata_equal") is True
        and reproducibility_summary.get("zip_member_count") == reproducibility_summary.get("manifest_file_count")
    )
    record(checks, "INV-0034", reproducibility_ok, f"packaging_reproducibility_status={archive_packaging_reproducibility.get('status')} trials={reproducibility_summary.get('trial_count')} sha_equal={reproducibility_summary.get('two_trial_zip_sha256_equal')} member_count={reproducibility_summary.get('zip_member_count')} manifest_files={reproducibility_summary.get('manifest_file_count')} failed={reproducibility_summary.get('checks_failed')}")

    json_catalog_summary = json_surface_catalog.get("summary", {})
    json_catalog_ok = (
        json_surface_catalog.get("status") == "pass"
        and json_surface_catalog.get("generated_for_revision") == release_manifest["revision"]
        and json_surface_catalog.get("checked_bundle") == release_manifest["bundle"]
        and json_surface_catalog.get("publication_authorized") is False
        and json_catalog_summary.get("checks_failed") == 0
        and json_catalog_summary.get("unclassified_json_count") == 0
    )
    record(checks, "INV-0035", json_catalog_ok, f"json_surface_catalog_status={json_surface_catalog.get('status')} json_files={json_catalog_summary.get('json_file_count')} schema_checked={json_catalog_summary.get('schema_checked_json_count')} unclassified={json_catalog_summary.get('unclassified_json_count')} failed={json_catalog_summary.get('checks_failed')}")

    queue_binding_summary = queue_note_source_binding.get("summary", {})
    queue_binding_ok = (
        queue_note_source_binding.get("status") == "pass"
        and queue_note_source_binding.get("generated_for_revision") == release_manifest["revision"]
        and queue_note_source_binding.get("checked_bundle") == release_manifest["bundle"]
        and queue_note_source_binding.get("publication_authorized") is False
        and queue_binding_summary.get("failure_count") == 0
        and queue_binding_summary.get("queue_note_pass_count") == queue_binding_summary.get("queue_note_count")
        and queue_binding_summary.get("duplicate_source_binding_count") == 0
        and queue_binding_summary.get("missing_from_queue_index_count") == 0
        and queue_binding_summary.get("missing_from_directory_count") == 0
    )
    record(checks, "INV-0036", queue_binding_ok, f"queue_binding_status={queue_note_source_binding.get('status')} notes={queue_binding_summary.get('queue_note_count')} pass={queue_binding_summary.get('queue_note_pass_count')} failures={queue_binding_summary.get('failure_count')} duplicates={queue_binding_summary.get('duplicate_source_binding_count')}")

    declared_ids_for_catalog = [str(inv.get("id", "")) for inv in invariants.get("invariants", [])]
    declared_counts = collections.Counter(declared_ids_for_catalog)
    declared_duplicates = sorted([inv_id for inv_id, count in declared_counts.items() if count > 1])
    existing_check_ids = [str(c.get("id", "")) for c in checks]
    existing_counts = collections.Counter(existing_check_ids)
    existing_duplicates = sorted([inv_id for inv_id, count in existing_counts.items() if count > 1])
    inv_re = re.compile(r"^INV-(\d{4})$")
    declared_nums = [int(m.group(1)) for inv_id in declared_ids_for_catalog if (m := inv_re.match(inv_id))]
    expected_nums = list(range(1, max(declared_nums or [0]) + 1))
    expected_implemented = set(existing_check_ids) | {"INV-0037", "INV-0038", "INV-0039", "INV-0040", "INV-0041", "INV-0042", "INV-0043", "INV-0044", "INV-0045", "INV-0046", "INV-0047", "INV-0048", "INV-0049", "INV-0050", "INV-0051", "INV-0052", "INV-0053", "INV-0054", "INV-0055", "INV-0056"}
    catalog_ok = (
        not declared_duplicates
        and not existing_duplicates
        and all(inv_re.match(inv_id) for inv_id in declared_ids_for_catalog)
        and declared_nums == expected_nums
        and set(declared_ids_for_catalog) == expected_implemented
    )
    record(checks, "INV-0037", catalog_ok, f"declared={len(declared_ids_for_catalog)} implemented_expected={len(expected_implemented)} declared_duplicates={declared_duplicates} implemented_duplicates={existing_duplicates} missing_from_catalog={sorted(expected_implemented - set(declared_ids_for_catalog))} unimplemented_declared={sorted(set(declared_ids_for_catalog) - expected_implemented)}")

    content_leakage_summary = content_leakage.get("summary", {})
    content_leakage_ok = (
        content_leakage.get("status") == "pass"
        and content_leakage.get("generated_for_revision") == release_manifest["revision"]
        and content_leakage.get("checked_bundle") == release_manifest["bundle"]
        and content_leakage.get("publication_authorized") is False
        and content_leakage_summary.get("finding_count") == 0
        and content_leakage_summary.get("checks_failed") == 0
    )
    record(checks, "INV-0038", content_leakage_ok, f"content_leakage_status={content_leakage.get('status')} text_files={content_leakage_summary.get('text_file_count')} findings={content_leakage_summary.get('finding_count')} failed={content_leakage_summary.get('checks_failed')}")

    schema_catalog_summary = schema_catalog_integrity.get("summary", {})
    schema_catalog_ok = (
        schema_catalog_integrity.get("status") == "pass"
        and schema_catalog_integrity.get("generated_for_revision") == release_manifest["revision"]
        and schema_catalog_integrity.get("checked_bundle") == release_manifest["bundle"]
        and schema_catalog_integrity.get("publication_authorized") is False
        and schema_catalog_summary.get("checks_failed") == 0
        and schema_catalog_summary.get("missing_referenced_schema_count") == 0
        and schema_catalog_summary.get("generic_report_schema_present") is True
    )
    record(checks, "INV-0039", schema_catalog_ok, f"schema_catalog_status={schema_catalog_integrity.get('status')} schemas={schema_catalog_summary.get('schema_document_count')} referenced={schema_catalog_summary.get('referenced_schema_count')} missing={schema_catalog_summary.get('missing_referenced_schema_count')} failed={schema_catalog_summary.get('checks_failed')}")

    json_key_summary = json_key_integrity.get("summary", {})
    json_key_ok = (
        json_key_integrity.get("status") == "pass"
        and json_key_integrity.get("generated_for_revision") == release_manifest["revision"]
        and json_key_integrity.get("checked_bundle") == release_manifest["bundle"]
        and json_key_integrity.get("publication_authorized") is False
        and json_key_summary.get("checks_failed") == 0
        and json_key_summary.get("duplicate_key_failure_count") == 0
        and json_key_summary.get("non_finite_numeric_literal_failure_count") == 0
        and json_key_summary.get("checked_with_duplicate_rejecting_parser") is True
        and json_key_summary.get("checked_with_nonfinite_rejecting_parser") is True
    )
    record(checks, "INV-0040", json_key_ok, f"json_key_status={json_key_integrity.get('status')} json_files={json_key_summary.get('json_file_count')} duplicate_key_failures={json_key_summary.get('duplicate_key_failure_count')} nonfinite_failures={json_key_summary.get('non_finite_numeric_literal_failure_count')} failed={json_key_summary.get('checks_failed')}")

    text_norm_summary = text_surface_normalization.get("summary", {})
    text_norm_ok = (
        text_surface_normalization.get("status") == "pass"
        and text_surface_normalization.get("generated_for_revision") == release_manifest["revision"]
        and text_surface_normalization.get("checked_bundle") == release_manifest["bundle"]
        and text_surface_normalization.get("publication_authorized") is False
        and text_norm_summary.get("checks_failed") == 0
        and text_norm_summary.get("nul_byte_failure_count") == 0
        and text_norm_summary.get("carriage_return_failure_count") == 0
        and text_norm_summary.get("utf8_failure_count") == 0
        and text_norm_summary.get("missing_final_lf_failure_count") == 0
        and text_norm_summary.get("warning_count") == 0
    )
    record(checks, "INV-0041", text_norm_ok, f"text_surface_status={text_surface_normalization.get('status')} text_files={text_norm_summary.get('text_surface_count')} missing_final_lf={text_norm_summary.get('missing_final_lf_failure_count')} warnings={text_norm_summary.get('warning_count')} failed={text_norm_summary.get('checks_failed')}")

    tooling_static_summary = tooling_static_integrity.get("summary", {})
    py_smoke_summary = python_entrypoint_smoke.get("summary", {})
    tooling_static_ok = (
        tooling_static_integrity.get("status") == "pass"
        and tooling_static_integrity.get("generated_for_revision") == release_manifest["revision"]
        and tooling_static_integrity.get("checked_bundle") == release_manifest["bundle"]
        and tooling_static_integrity.get("publication_authorized") is False
        and tooling_static_summary.get("checks_failed") == 0
        and tooling_static_summary.get("syntax_failure_count") == 0
        and tooling_static_summary.get("duplicate_literal_dict_key_count") == 0
        and tooling_static_summary.get("unexpected_top_level_statement_count") == 0
        and python_entrypoint_smoke.get("status") == "pass"
        and python_entrypoint_smoke.get("generated_for_revision") == release_manifest["revision"]
        and python_entrypoint_smoke.get("checked_bundle") == release_manifest["bundle"]
        and python_entrypoint_smoke.get("publication_authorized") is False
        and py_smoke_summary.get("checks_failed") == 0
        and py_smoke_summary.get("compile_failed") == 0
        and py_smoke_summary.get("entrypoint_failed") == 0
        and py_smoke_summary.get("compile_checked") == py_smoke_summary.get("python_source_count")
        and py_smoke_summary.get("unexpected_external_import_count") == 0
        and py_smoke_summary.get("external_import_path_violation_count") == 0
        and py_smoke_summary.get("external_dependency_unavailable_count") == 0
        and py_smoke_summary.get("import_negative_control_count", 0) >= 5
        and py_smoke_summary.get("import_negative_control_failed_count") == 0
    )
    record(checks, "INV-0042", tooling_static_ok, f"tooling_static_status={tooling_static_integrity.get('status')} scripts={tooling_static_summary.get('script_count')} syntax_failures={tooling_static_summary.get('syntax_failure_count')} duplicate_keys={tooling_static_summary.get('duplicate_literal_dict_key_count')} py_smoke_status={python_entrypoint_smoke.get('status')} py_sources={py_smoke_summary.get('python_source_count')} py_compile_failed={py_smoke_summary.get('compile_failed')} py_entrypoint_failed={py_smoke_summary.get('entrypoint_failed')} unexpected_external={py_smoke_summary.get('unexpected_external_import_count')} path_violations={py_smoke_summary.get('external_import_path_violation_count')} unavailable_external={py_smoke_summary.get('external_dependency_unavailable_count')} import_negative_failures={py_smoke_summary.get('import_negative_control_failed_count')} failed={tooling_static_summary.get('checks_failed')}/{py_smoke_summary.get('checks_failed')}")

    decision_note_summary = decision_note_integrity.get("summary", {})
    action_counts = decision_note_summary.get("publication_action_counts", {}) if isinstance(decision_note_summary.get("publication_action_counts", {}), dict) else {}
    decision_note_ok = (
        decision_note_integrity.get("status") == "pass"
        and decision_note_integrity.get("generated_for_revision") == release_manifest["revision"]
        and decision_note_integrity.get("checked_bundle") == release_manifest["bundle"]
        and decision_note_integrity.get("publication_authorized") is False
        and decision_note_summary.get("checks_failed") == 0
        and decision_note_summary.get("decision_note_count") == decision_note_summary.get("decision_index_count")
        and (int(action_counts.get("none", 0)) + int(action_counts.get("publish", 0))) == decision_note_summary.get("decision_note_count")
        and decision_note_summary.get("subject_path_missing_count") == 0
    )
    record(checks, "INV-0043", decision_note_ok, f"decision_note_status={decision_note_integrity.get('status')} notes={decision_note_summary.get('decision_note_count')} action_counts={action_counts} subject_missing={decision_note_summary.get('subject_path_missing_count')} failed={decision_note_summary.get('checks_failed')}")

    report_warning_summary = report_warning_policy.get("summary", {})
    report_warning_ok = (
        report_warning_policy.get("status") == "pass"
        and report_warning_policy.get("generated_for_revision") == release_manifest["revision"]
        and report_warning_policy.get("checked_bundle") == release_manifest["bundle"]
        and report_warning_policy.get("publication_authorized") is False
        and report_warning_summary.get("checks_failed") == 0
        and report_warning_summary.get("reports_with_warnings") == 0
        and report_warning_summary.get("total_top_level_warning_count") == 0
        and report_warning_summary.get("positive_warning_count_field_count") == 0
    )
    record(checks, "INV-0044", report_warning_ok, f"report_warning_status={report_warning_policy.get('status')} reports={report_warning_summary.get('report_json_count')} with_warnings={report_warning_summary.get('reports_with_warnings')} warning_count_fields={report_warning_summary.get('positive_warning_count_field_count')}")

    target_port_summary = publication_target_portability.get("summary", {})
    target_port_ok = (
        publication_target_portability.get("status") == "pass"
        and publication_target_portability.get("generated_for_revision") == release_manifest["revision"]
        and publication_target_portability.get("checked_bundle") == release_manifest["bundle"]
        and publication_target_portability.get("publication_authorized") is False
        and target_port_summary.get("checks_failed") == 0
        and target_port_summary.get("nonportable_count") == 0
        and target_port_summary.get("already_exists_count") == 0
    )
    record(checks, "INV-0045", target_port_ok, f"publication_target_portability_status={publication_target_portability.get('status')} rows={target_port_summary.get('target_row_count')} nonportable={target_port_summary.get('nonportable_count')} already_exists={target_port_summary.get('already_exists_count')}")

    entry_security_summary = archive_entry_security.get("summary", {})
    entry_security_ok = (
        archive_entry_security.get("status") == "pass"
        and archive_entry_security.get("generated_for_revision") == release_manifest["revision"]
        and archive_entry_security.get("checked_bundle") == release_manifest["bundle"]
        and archive_entry_security.get("publication_authorized") is False
        and entry_security_summary.get("checks_failed") == 0
        and entry_security_summary.get("symlink_or_special_count") == 0
        and entry_security_summary.get("unexpected_executable_count") == 0
        and entry_security_summary.get("zip_duplicate_member_count") == 0
    )
    record(checks, "INV-0046", entry_security_ok, f"archive_entry_security_status={archive_entry_security.get('status')} tree_files={entry_security_summary.get('tree_file_count')} zip_members={entry_security_summary.get('zip_member_count')} symlink_or_special={entry_security_summary.get('symlink_or_special_count')} unexpected_executable={entry_security_summary.get('unexpected_executable_count')} failed={entry_security_summary.get('checks_failed')}")

    bundle_identity_summary = bundle_identity_consistency.get("summary", {})
    bundle_identity_ok = (
        bundle_identity_consistency.get("status") == "pass"
        and bundle_identity_consistency.get("generated_for_revision") == release_manifest["revision"]
        and bundle_identity_consistency.get("checked_bundle") == release_manifest["bundle"]
        and bundle_identity_consistency.get("publication_authorized") is False
        and bundle_identity_summary.get("checks_failed") == 0
    )
    record(checks, "INV-0047", bundle_identity_ok, f"bundle_identity_status={bundle_identity_consistency.get('status')} surfaces={bundle_identity_summary.get('identity_surface_count')} failed={bundle_identity_summary.get('checks_failed')}")

    control_path_summary = control_surface_path_integrity.get("summary", {})
    control_path_ok = (
        control_surface_path_integrity.get("status") == "pass"
        and control_surface_path_integrity.get("generated_for_revision") == release_manifest["revision"]
        and control_surface_path_integrity.get("checked_bundle") == release_manifest["bundle"]
        and control_surface_path_integrity.get("publication_authorized") is False
        and control_path_summary.get("checks_failed") == 0
        and control_path_summary.get("missing_reference_count") == 0
        and control_path_summary.get("nonportable_reference_count") == 0
        and control_path_summary.get("unsafe_reference_count") == 0
    )
    record(checks, "INV-0048", control_path_ok, f"control_path_status={control_surface_path_integrity.get('status')} references={control_path_summary.get('path_reference_count')} unique={control_path_summary.get('unique_path_reference_count')} missing={control_path_summary.get('missing_reference_count')} nonportable={control_path_summary.get('nonportable_reference_count')} unsafe={control_path_summary.get('unsafe_reference_count')}")

    duplicate_content_summary = duplicate_content_policy.get("summary", {})
    duplicate_content_ok = (
        duplicate_content_policy.get("status") == "pass"
        and duplicate_content_policy.get("generated_for_revision") == release_manifest["revision"]
        and duplicate_content_policy.get("checked_bundle") == release_manifest["bundle"]
        and duplicate_content_policy.get("publication_authorized") is False
        and duplicate_content_summary.get("checks_failed") == 0
        and duplicate_content_summary.get("unexpected_duplicate_group_count") == 0
        and duplicate_content_summary.get("missing_allowlist_path_count") == 0
    )
    record(checks, "INV-0049", duplicate_content_ok, f"duplicate_content_status={duplicate_content_policy.get('status')} groups={duplicate_content_summary.get('duplicate_group_count')} duplicate_files={duplicate_content_summary.get('duplicate_file_count')} unexpected={duplicate_content_summary.get('unexpected_duplicate_group_count')} missing_allowlist={duplicate_content_summary.get('missing_allowlist_path_count')}")


    tex_summary = tex_source_safety.get("summary", {})
    tex_source_safety_ok = (
        tex_source_safety.get("status") == "pass"
        and tex_source_safety.get("generated_for_revision") == release_manifest["revision"]
        and tex_source_safety.get("checked_bundle") == release_manifest["bundle"]
        and tex_source_safety.get("publication_authorized") is False
        and tex_summary.get("checks_failed") == 0
        and tex_summary.get("finding_count") == 0
    )
    record(checks, "INV-0050", tex_source_safety_ok, f"tex_source_safety_status={tex_source_safety.get('status')} tex_files={tex_summary.get('tex_file_count')} findings={tex_summary.get('finding_count')}")

    secret_summary = secret_material_quarantine.get("summary", {})
    secret_material_ok = (
        secret_material_quarantine.get("status") == "pass"
        and secret_material_quarantine.get("generated_for_revision") == release_manifest["revision"]
        and secret_material_quarantine.get("checked_bundle") == release_manifest["bundle"]
        and secret_material_quarantine.get("publication_authorized") is False
        and secret_summary.get("checks_failed") == 0
        and secret_summary.get("finding_count") == 0
        and secret_summary.get("private_key_marker_count") == 0
        and secret_summary.get("token_like_pattern_count") == 0
    )
    record(checks, "INV-0051", secret_material_ok, f"secret_material_status={secret_material_quarantine.get('status')} text_surfaces={secret_summary.get('text_surface_count')} findings={secret_summary.get('finding_count')} token_like={secret_summary.get('token_like_pattern_count')}")

    makefile_summary = makefile_target_integrity.get("summary", {})
    makefile_target_ok = (
        makefile_target_integrity.get("status") == "pass"
        and makefile_target_integrity.get("generated_for_revision") == release_manifest["revision"]
        and makefile_target_integrity.get("checked_bundle") == release_manifest["bundle"]
        and makefile_target_integrity.get("publication_authorized") is False
        and makefile_summary.get("checks_failed") == 0
        and makefile_summary.get("missing_phony_count") == 0
        and makefile_summary.get("missing_target_count") == 0
        and makefile_summary.get("dangerous_command_count") == 0
        and makefile_summary.get("unsafe_python_command_count") == 0
    )
    record(checks, "INV-0052", makefile_target_ok, f"makefile_integrity_status={makefile_target_integrity.get('status')} targets={makefile_summary.get('parsed_target_count')} commands={makefile_summary.get('command_count')} failures={makefile_summary.get('checks_failed')}")

    manifest_canon_summary = manifest_canonicality.get("summary", {})
    manifest_canon_ok = (
        manifest_canonicality.get("status") == "pass"
        and manifest_canonicality.get("generated_for_revision") == release_manifest["revision"]
        and manifest_canonicality.get("checked_bundle") == release_manifest["bundle"]
        and manifest_canonicality.get("publication_authorized") is False
        and manifest_canon_summary.get("checks_failed") == 0
        and manifest_canon_summary.get("digest_mismatch_count") == 0
    )
    record(checks, "INV-0053", manifest_canon_ok, f"manifest_canonicality_status={manifest_canonicality.get('status')} files={manifest_canon_summary.get('manifest_json_file_count')} sha_entries={manifest_canon_summary.get('manifest_sha256_entry_count')} failures={manifest_canon_summary.get('checks_failed')}")

    freeze_warning_summary = freeze_warning_resolution.get("summary", {})
    freeze_warning_ok = (
        freeze_warning_resolution.get("status") == "pass"
        and freeze_warning_resolution.get("generated_for_revision") == release_manifest["revision"]
        and freeze_warning_resolution.get("checked_bundle") == release_manifest["bundle"]
        and freeze_warning_resolution.get("publication_authorized") is False
        and freeze_warning_summary.get("checks_failed") == 0
        and freeze_warning_summary.get("unresolved_notice_count") == 0
    )
    record(checks, "INV-0054", freeze_warning_ok, f"freeze_warning_status={freeze_warning_resolution.get('status')} notices={freeze_warning_summary.get('preflight_notice_count')} resolved={freeze_warning_summary.get('resolved_notice_count')} unresolved={freeze_warning_summary.get('unresolved_notice_count')}")

    fingerprint_summary = toolchain_fingerprint.get("summary", {})
    fingerprint_ok = (
        toolchain_fingerprint.get("status") == "pass"
        and toolchain_fingerprint.get("generated_for_revision") == release_manifest["revision"]
        and toolchain_fingerprint.get("checked_bundle") == release_manifest["bundle"]
        and toolchain_fingerprint.get("publication_authorized") is False
        and fingerprint_summary.get("checks_failed") == 0
        and (fingerprint_summary.get("fingerprint_present") is True or fingerprint_summary.get("fingerprint_required") is False)
        and fingerprint_summary.get("compile_surface_fingerprint_count") == fingerprint_summary.get("compile_surface_fingerprint_expected_count")
        and fingerprint_summary.get("compile_surface_fingerprint_fail_count") == 0
        and fingerprint_summary.get("compile_surface_path_missing_count") == 0
        and fingerprint_summary.get("compile_surface_fingerprint_missing_count") == 0
        and fingerprint_summary.get("compile_surface_fingerprint_mismatch_count") == 0
        and fingerprint_summary.get("negative_control_failed_count") == 0
    )
    record(checks, "INV-0055", fingerprint_ok, f"toolchain_fingerprint_status={toolchain_fingerprint.get('status')} command={fingerprint_summary.get('latex_command')} gate={fingerprint_summary.get('compile_gate_status')} present={fingerprint_summary.get('fingerprint_present')} failures={fingerprint_summary.get('checks_failed')} compile_surfaces={fingerprint_summary.get('compile_surface_fingerprint_count')}/{fingerprint_summary.get('compile_surface_fingerprint_expected_count')} surface_failures={fingerprint_summary.get('compile_surface_fingerprint_fail_count')} negative_failures={fingerprint_summary.get('negative_control_failed_count')}")

    unicode_summary = unicode_control_hygiene.get("summary", {})
    unicode_hygiene_ok = (
        unicode_control_hygiene.get("status") == "pass"
        and unicode_control_hygiene.get("generated_for_revision") == release_manifest["revision"]
        and unicode_control_hygiene.get("checked_bundle") == release_manifest["bundle"]
        and unicode_control_hygiene.get("publication_authorized") is False
        and unicode_summary.get("checks_failed") == 0
        and unicode_summary.get("finding_count") == 0
        and unicode_summary.get("c0_or_del_control_count") == 0
        and unicode_summary.get("c1_control_count") == 0
        and unicode_summary.get("bidi_control_count") == 0
        and unicode_summary.get("invisible_format_control_count") == 0
        and unicode_summary.get("unicode_noncharacter_count") == 0
    )
    record(checks, "INV-0056", unicode_hygiene_ok, f"unicode_control_hygiene_status={unicode_control_hygiene.get('status')} text_surfaces={unicode_summary.get('text_surface_count')} findings={unicode_summary.get('finding_count')} c0={unicode_summary.get('c0_or_del_control_count')} bidi={unicode_summary.get('bidi_control_count')} invisible={unicode_summary.get('invisible_format_control_count')}")

    declared_ids = [inv["id"] for inv in invariants.get("invariants", [])]
    implemented_ids = {c["id"] for c in checks}
    for inv_id in declared_ids:
        if inv_id not in implemented_ids:
            record(checks, inv_id, False, "declared in archive_invariants.json but not implemented in checker")

    failures = [c for c in checks if c["status"] == "fail"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release_manifest["revision"],
        "checked_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "publication_authorized": False,
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
        },
        "fail_closed_rule": "If an archive invariant fails, default to no publication and repair the violated invariant before trusting the archive state.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
