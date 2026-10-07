#!/usr/bin/env python3
"""Check coherence across compact archive control surfaces.

This script is intentionally fail-closed: if the compact state surfaces disagree,
a future operator should default to no publication until the disagreement is fixed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime

from render_queue_surfaces import render_latest_decision_md, render_queue_md, render_status_md


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_queue_notes(directory: pathlib.Path) -> int:
    if not directory.exists():
        return 0
    return len([p for p in directory.glob("*.md") if p.name != "README.md"])


def manifest_sha256_paths(path: pathlib.Path) -> list[str]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"malformed MANIFEST.sha256 line: {line!r}")
        entries.append(parts[1])
    return entries


def parse_latest_decision_pointer(path: pathlib.Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"`(release_queue/decisions/[^`]+\.md)`", line)
        if m:
            return m.group(1)
    return None


def md_count(text: str, label: str) -> int | None:
    m = re.search(rf"- {re.escape(label)}: (\d+)", text)
    return int(m.group(1)) if m else None




COMPILE_RECEIPT_POLICY_V2 = "tex_compile_receipt_v2_deterministic_pdf_normalized_log"

def compile_digest_receipt_missing(row: dict) -> bool:
    """Return True when a compile row lacks raw PDF/log digest receipts."""
    if row.get("pdf_output_created") is not True:
        return True
    for key in ("pdf_sha256", "combined_log_sha256", "final_log_sha256"):
        value = row.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            return True
    for key in ("pdf_output_bytes", "combined_log_bytes", "final_log_bytes"):
        try:
            if int(row.get(key, 0)) <= 0:
                return True
        except (TypeError, ValueError):
            return True
    return False

def compile_reproducible_receipt_missing(row: dict) -> bool:
    """Return True when a compile row lacks deterministic normalized receipt evidence."""
    if row.get("compile_receipt_policy") != COMPILE_RECEIPT_POLICY_V2:
        return True
    source_date_epoch = str(row.get("source_date_epoch", ""))
    if not re.fullmatch(r"\d{9,12}", source_date_epoch):
        return True
    for key in ("normalized_pdf_sha256", "normalized_combined_log_sha256", "normalized_final_log_sha256", "pdf_trailer_id"):
        value = row.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            return True
    for key in ("normalized_pdf_bytes", "normalized_combined_log_bytes", "normalized_final_log_bytes"):
        try:
            if int(row.get(key, 0)) <= 0:
                return True
        except (TypeError, ValueError):
            return True
    if row.get("pdf_normalization_policy") != "normalize-pdftex-trailer-id-and-dates-v1":
        return True
    if row.get("log_normalization_policy") != "normalize-volatile-compile-paths-v1":
        return True
    return False

def parse_unqueued_inventory(text: str) -> tuple[dict[str, int | None], list[str]]:
    counts = {
        "queued": md_count(text, "Queued paper.tex sources"),
        "series": md_count(text, "Total series paper.tex sources"),
        "unqueued": md_count(text, "Unqueued paper.tex sources"),
    }
    paths = sorted(set(re.findall(r"`(series/[^`]+/paper\.tex)`", text)))
    return counts, paths


def check(root: pathlib.Path) -> dict:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    revision_receipt = load_json(root / "REVISION_RECEIPT.json")
    archive_index = load_json(root / "ARCHIVE_INDEX.json")
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    review_inventory = load_json(root / "release_queue" / "REVIEW_INVENTORY.json")
    citation_heads = load_json(root / "published" / "citation_heads.json")
    publication_classification = load_json(root / "published" / "publication_classification.json")
    legacy_links = load_json(root / "published" / "legacy_published_links.json")
    public_surface = load_json(root / "published" / "PUBLIC_SURFACE.json")
    published_compile_triage = load_json(root / "published" / "PUBLISHED_COMPILE_TRIAGE.json") if (root / "published" / "PUBLISHED_COMPILE_TRIAGE.json").exists() else {"status": "missing", "summary": {}}
    auxiliary_tex_compile_triage = load_json(root / "index" / "AUXILIARY_TEX_COMPILE_TRIAGE.json") if (root / "index" / "AUXILIARY_TEX_COMPILE_TRIAGE.json").exists() else {"status": "missing", "summary": {}}
    control_surfaces = load_json(root / "publishing" / "control_surfaces.json")
    canonical_policy = load_json(root / "publishing" / "CANONICAL_POLICY.json")
    context_pack = load_json(root / "CONTEXT_PACK.json")
    decision_index = load_json(root / "release_queue" / "DECISION_INDEX.json")
    latest_decision_json = load_json(root / "release_queue" / "LATEST_DECISION.json")
    surface_schema_validation = load_json(root / "reports" / "surface_schema_validation.json")
    archive_invariants = load_json(root / "reports" / "archive_invariants.json")
    context_pack_contract = load_json(root / "reports" / "context_pack_contract.json")
    context_pack_budget = load_json(root / "reports" / "context_pack_budget.json")
    archive_budget = load_json(root / "reports" / "archive_budget.json")
    transient_audit = load_json(root / "reports" / "transient_surface_audit.json")
    manifest_verification = load_json(root / "reports" / "manifest_sha256_verification.json")
    manifest_coverage = load_json(root / "reports" / "manifest_coverage_audit.json")
    lifecycle_gate_status = load_json(root / "reports" / "lifecycle_gate_status.json")
    transfer_source_receipt = load_json(root / "reports" / "transfer_source_receipt.json")
    support_manifest_integrity = load_json(root / "reports" / "support_manifest_integrity.json")
    review_inventory_coverage = load_json(root / "reports" / "review_inventory_coverage.json")
    citation_closure_audit = load_json(root / "reports" / "citation_closure_audit.json")
    release_readiness_audit = load_json(root / "reports" / "release_readiness_audit.json")
    queue_note_source_binding = load_json(root / "reports" / "queue_note_source_binding.json")
    queue_compile_smoke = load_json(root / "reports" / "queue_compile_smoke.json")
    hold_compile_triage = load_json(root / "release_queue" / "HOLD_COMPILE_TRIAGE.json")
    unqueued_compile_triage = load_json(root / "release_queue" / "UNQUEUED_COMPILE_TRIAGE.json")
    hold_compile_md_path = root / "release_queue" / "HOLD_COMPILE_TRIAGE.md"
    unqueued_compile_md_path = root / "release_queue" / "UNQUEUED_COMPILE_TRIAGE.md"
    published_compile_md_path = root / "published" / "PUBLISHED_COMPILE_TRIAGE.md"
    auxiliary_tex_compile_md_path = root / "index" / "AUXILIARY_TEX_COMPILE_TRIAGE.md"
    hold_compile_md_text = hold_compile_md_path.read_text(encoding="utf-8") if hold_compile_md_path.exists() else ""
    unqueued_compile_md_text = unqueued_compile_md_path.read_text(encoding="utf-8") if unqueued_compile_md_path.exists() else ""
    published_compile_md_text = published_compile_md_path.read_text(encoding="utf-8") if published_compile_md_path.exists() else ""
    auxiliary_tex_compile_md_text = auxiliary_tex_compile_md_path.read_text(encoding="utf-8") if auxiliary_tex_compile_md_path.exists() else ""
    unqueued_inventory_path = root / "release_queue" / "UNQUEUED_SOURCE_INVENTORY.md"
    unqueued_inventory_text = unqueued_inventory_path.read_text(encoding="utf-8") if unqueued_inventory_path.exists() else ""
    evidence_pack_audit = load_json(root / "reports" / "evidence_pack_audit.json")
    evidence_pack_integrity = load_json(root / "reports" / "evidence_pack_integrity.json")
    freeze_compile_witness = load_json(root / "reports" / "freeze_compile_witness.json")
    freeze_packet_integrity = load_json(root / "reports" / "freeze_packet_integrity.json")
    publication_boundary = load_json(root / "reports" / "publication_boundary.json")
    release_freeze_plan = load_json(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json")
    review_inventory_integrity = load_json(root / "reports" / "review_inventory_integrity.json")
    operator_command_hygiene = load_json(root / "reports" / "operator_command_hygiene.json")
    assurance_catalog_integrity = load_json(root / "reports" / "assurance_catalog_integrity.json")
    tooling_inventory = load_json(root / "publishing" / "TOOLING_INVENTORY.json")
    tooling_inventory_integrity = load_json(root / "reports" / "tooling_inventory_integrity.json")
    report_schema_coverage = load_json(root / "reports" / "report_schema_coverage.json")
    report_identity_coverage = load_json(root / "reports" / "report_identity_coverage.json")
    report_warning_policy = load_json(root / "reports" / "report_warning_policy.json")
    publication_artifact_quarantine = load_json(root / "reports" / "publication_artifact_quarantine.json")
    publication_target_portability = load_json(root / "reports" / "publication_target_portability.json")
    path_portability = load_json(root / "reports" / "path_portability.json")
    archive_packaging_reproducibility = load_json(root / "reports" / "archive_packaging_reproducibility.json")
    archive_entry_security = load_json(root / "reports" / "archive_entry_security.json")
    bundle_identity_consistency = load_json(root / "reports" / "bundle_identity_consistency.json")
    control_surface_path_integrity = load_json(root / "reports" / "control_surface_path_integrity.json")
    duplicate_content_policy = load_json(root / "reports" / "duplicate_content_policy.json")
    tex_source_safety = load_json(root / "reports" / "tex_source_safety.json")
    secret_material_quarantine = load_json(root / "reports" / "secret_material_quarantine.json")
    makefile_target_integrity = load_json(root / "reports" / "makefile_target_integrity.json")
    manifest_canonicality = load_json(root / "reports" / "manifest_canonicality.json")
    freeze_warning_resolution = load_json(root / "reports" / "freeze_warning_resolution.json")
    toolchain_fingerprint = load_json(root / "reports" / "toolchain_fingerprint.json")
    json_surface_catalog = load_json(root / "reports" / "json_surface_catalog.json")
    content_leakage = load_json(root / "reports" / "content_leakage.json")
    decision_note_integrity = load_json(root / "reports" / "decision_note_integrity.json")
    schema_catalog_integrity = load_json(root / "reports" / "schema_catalog_integrity.json")
    tooling_static_integrity = load_json(root / "reports" / "tooling_static_integrity.json")
    python_entrypoint_smoke = load_json(root / "reports" / "python_entrypoint_smoke.json")
    json_key_integrity = load_json(root / "reports" / "json_key_integrity.json")
    text_surface_normalization = load_json(root / "reports" / "text_surface_normalization.json")
    unicode_control_hygiene = load_json(root / "reports" / "unicode_control_hygiene.json")
    invariant_catalog_integrity = load_json(root / "reports" / "invariant_catalog_integrity.json")
    archive_index_integrity = load_json(root / "reports" / "archive_index_integrity.json")
    rebuild_fixed_point_coverage = load_json(root / "reports" / "rebuild_fixed_point_coverage.json")
    publication_decision_template = load_json(root / "reports" / "publication_decision_template.json")
    publication_decision_authorization = load_json(root / "reports" / "publication_decision_authorization.json")
    archive_packaging_recipe = load_json(root / "reports" / "archive_packaging_recipe.json")
    freeze_toolchain = load_json(root / "reports" / "freeze_toolchain.json")
    publication_rehearsal = load_json(root / "reports" / "publication_rehearsal.json")
    research_metadata_integrity = load_json(root / "reports" / "research_metadata_integrity.json")
    transfer_sources = load_json(root / "TRANSFER_SOURCES.json")
    assurance_artifacts = load_json(root / "ASSURANCE_ARTIFACTS.json")
    version_text = (root / "VERSION").read_text(encoding="utf-8").strip()
    citation_heads_md = (root / "published" / "CITATION_HEADS.md").read_text(encoding="utf-8")
    latest_decision_md_actual = (root / "release_queue" / "LATEST_DECISION.md").read_text(encoding="utf-8")
    status_md_actual = (root / "release_queue" / "STATUS.md").read_text(encoding="utf-8")
    queue_md_actual = (root / "release_queue" / "QUEUE.md").read_text(encoding="utf-8")
    human_entry_surfaces = {
        name: (root / name).read_text(encoding="utf-8", errors="replace")
        for name in ["README.md", "START_HERE.md", "NOTICE", "codemeta.json", "ro-crate-metadata.json"]
        if (root / name).exists()
    }
    latest_decision_pointer = parse_latest_decision_pointer(root / "release_queue" / "LATEST_DECISION.md")
    latest_decision_md_expected = render_latest_decision_md(root)
    status_md_expected = render_status_md(root)
    queue_md_expected = render_queue_md(root)

    checks = []

    def record(name: str, ok: bool, details: str):
        checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})

    receipt_revision = f"rev{int(revision_receipt['revision']):04d}"
    latest_archive_entry = archive_index["revisions"][0]
    parsed_ts_local = datetime.fromisoformat(revision_receipt["timestamp_local"]).strftime("%Y.%m.%d.%H.%M")
    artifact_stem = revision_receipt["artifact_stem"]
    expected_bundle = artifact_stem + ".zip"

    record(
        "revision_identity_alignment",
        release_manifest["revision"] == receipt_revision == archive_index["latest_revision"] == latest_archive_entry["revision"] == version_text,
        f"release_manifest={release_manifest['revision']} receipt={receipt_revision} archive_index={archive_index['latest_revision']} version={version_text}",
    )

    record(
        "bundle_and_timestamp_alignment",
        release_manifest["bundle"] == expected_bundle
        and release_manifest["bundle"] == latest_archive_entry["bundle"]
        and release_manifest["timestamp"] == parsed_ts_local
        and release_manifest["timestamp"] in artifact_stem,
        f"bundle={release_manifest['bundle']} expected_bundle={expected_bundle} manifest_timestamp={release_manifest['timestamp']} receipt_timestamp={parsed_ts_local}",
    )

    bundle_pattern = re.compile(r"Anonymity-rev\d{4}-\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-[A-Za-z0-9_.()\-]+\.zip")
    human_entry_bundle_hits = {
        name: sorted(set(bundle_pattern.findall(text)))
        for name, text in human_entry_surfaces.items()
    }
    stale_human_entry_hits = {
        name: hits for name, hits in human_entry_bundle_hits.items()
        if any(hit != release_manifest["bundle"] for hit in hits)
    }
    missing_current_human_entries = sorted(
        name for name in ["README.md", "START_HERE.md", "NOTICE", "codemeta.json", "ro-crate-metadata.json"]
        if release_manifest["bundle"] not in human_entry_surfaces.get(name, "")
    )
    record(
        "human_entry_surfaces_reference_current_bundle_only",
        not stale_human_entry_hits and not missing_current_human_entries,
        f"stale_hits={stale_human_entry_hits} missing_current={missing_current_human_entries}",
    )

    record(
        "queue_index_revision_marker",
        queue_index.get("generated_for_revision") == release_manifest["revision"],
        f"queue_index.generated_for_revision={queue_index.get('generated_for_revision')} release_manifest.revision={release_manifest['revision']}",
    )

    candidate_count = count_queue_notes(root / "release_queue" / "candidates")
    hold_count = count_queue_notes(root / "release_queue" / "hold")
    published_ready_count = count_queue_notes(root / "release_queue" / "published_ready")
    published_count = count_queue_notes(root / "release_queue" / "published")
    queue_state_ok = (
        queue_index["summary"]["candidate"] == candidate_count
        and queue_index["summary"]["hold"] == hold_count
        and queue_index["summary"]["published_ready"] == published_ready_count
        and queue_index["summary"].get("published", 0) == published_count
        and len(queue_index["states"]["candidate"]) == candidate_count
        and len(queue_index["states"]["hold"]) == hold_count
        and len(queue_index["states"]["published_ready"]) == published_ready_count
        and len(queue_index["states"].get("published", [])) == published_count
    )
    record(
        "queue_counts_match_directories_and_state_arrays",
        queue_state_ok,
        f"summary(candidate={queue_index['summary']['candidate']}, hold={queue_index['summary']['hold']}, published_ready={queue_index['summary']['published_ready']}, published={queue_index['summary'].get('published', 0)}) vs directories(candidate={candidate_count}, hold={hold_count}, published_ready={published_ready_count}, published={published_count})",
    )

    bucket_counts = review_inventory["review_bucket_counts"]
    review_coverage = review_inventory.get("queue_coverage", {})
    review_ok = (
        review_inventory.get("generated_for_revision") == release_manifest["revision"]
        and queue_index["summary"]["reviewable_unpublished_papers"] == review_inventory["reviewable_unpublished_papers"] == len(review_inventory["entries"])
        and queue_index["summary"]["standalone_series_review_first"] == bucket_counts["standalone_series_review_first"]
        and queue_index["summary"]["synthesis_foundation_review_later"] == bucket_counts["synthesis_foundation_review_later"]
        and queue_index["summary"]["synthesis_tail_defer_high_churn"] == bucket_counts["synthesis_tail_defer_high_churn"]
        and review_coverage.get("queued_count") == queue_index["summary"]["candidate"] + queue_index["summary"]["hold"] + queue_index["summary"]["published_ready"] + queue_index["summary"].get("published", 0)
        and review_coverage.get("unqueued_count") == review_inventory["reviewable_unpublished_papers"] - review_coverage.get("queued_count", -1)
    )
    record(
        "review_inventory_counts_match_queue_summary",
        review_ok,
        f"reviewable={review_inventory['reviewable_unpublished_papers']} bucket_counts={bucket_counts} queue_coverage={review_coverage}",
    )

    legacy_paths = [x["path"] for x in publication_classification["legacy_canonical_public_wiki_targets"]]
    legacy_wikilinks = [x["wikilink"] for x in publication_classification["legacy_canonical_public_wiki_targets"]]
    citation_paths = [x["path"] for x in citation_heads["current_public_citation_heads"]]
    citation_wikilinks = [x["wikilink"] for x in citation_heads["current_public_citation_heads"]]
    legacy_json_paths = [x["path"] for x in legacy_links["canonical_legacy_links"]]
    legacy_json_wikilinks = [x["wikilink"] for x in legacy_links["canonical_legacy_links"]]
    frozen_paths = [x["path"] for x in publication_classification["repo_frozen_noncanonical_entries"]]
    new_paths = [x["path"] for x in publication_classification.get("new_post_policy_anonymity_entries", [])]
    new_wikilinks = [x["wikilink"] for x in publication_classification.get("new_post_policy_anonymity_entries", [])]
    citation_new_paths = [x["path"] for x in citation_heads.get("new_post_policy_anonymity_heads", [])]
    citation_new_wikilinks = [x["wikilink"] for x in citation_heads.get("new_post_policy_anonymity_heads", [])]
    citation_frozen_paths = [x["path"] for x in citation_heads["repo_frozen_noncanonical_entries"]]
    citation_ok = (
        citation_paths == legacy_paths + new_paths
        and citation_wikilinks == legacy_wikilinks + new_wikilinks
        and legacy_paths == legacy_json_paths
        and legacy_wikilinks == legacy_json_wikilinks
        and frozen_paths == citation_frozen_paths
        and new_paths == citation_new_paths
        and new_wikilinks == citation_new_wikilinks
        and citation_heads["summary"]["legacy_public_head_count"] == len(legacy_paths)
        and citation_heads["summary"]["new_post_policy_anonymity_head_count"] == len(citation_heads["new_post_policy_anonymity_heads"])
        and citation_heads["summary"]["repo_frozen_noncanonical_entry_count"] == len(frozen_paths)
    )
    record(
        "citation_heads_match_classification_and_legacy_register",
        citation_ok,
        f"legacy_public_heads={len(legacy_paths)} new_post_policy={len(new_paths)} frozen_noncanonical={len(frozen_paths)}",
    )

    public_surface_expected_heads = legacy_paths + new_paths
    public_surface_ok = (
        public_surface["current_public_citation_heads"] == public_surface_expected_heads
        and public_surface["repo_frozen_noncanonical_entries"] == frozen_paths
    )
    record(
        "public_surface_matches_citation_and_classification",
        public_surface_ok,
        f"public_surface_heads={len(public_surface['current_public_citation_heads'])} public_surface_frozen={len(public_surface['repo_frozen_noncanonical_entries'])}",
    )

    md_ok = (
        md_count(citation_heads_md, "Legacy public citation heads") == citation_heads["summary"]["legacy_public_head_count"]
        and md_count(citation_heads_md, "New post-policy Anonymity citation heads") == citation_heads["summary"]["new_post_policy_anonymity_head_count"]
        and md_count(citation_heads_md, "Repo-frozen noncanonical entries under `published/`") == citation_heads["summary"]["repo_frozen_noncanonical_entry_count"]
        and md_count(citation_heads_md, "Ambiguous public-head lineages") == citation_heads["summary"]["ambiguous_public_head_count"]
    )
    record(
        "citation_heads_markdown_summary_matches_json",
        md_ok,
        "checked summary-count lines in published/CITATION_HEADS.md against published/citation_heads.json",
    )

    latest_decision_files = sorted(p.name for p in (root / "release_queue" / "decisions").glob("*.md"))
    latest_decision_expected = f"release_queue/decisions/{latest_decision_files[-1]}" if latest_decision_files else None
    latest_decision_ok = latest_decision_pointer == latest_decision_expected and latest_decision_pointer is not None and (root / latest_decision_pointer).exists()
    record(
        "latest_decision_pointer_is_present_and_latest",
        latest_decision_ok,
        f"pointer={latest_decision_pointer} expected_latest={latest_decision_expected}",
    )

    decision_index_ok = (
        decision_index.get("generated_for_revision") == release_manifest["revision"]
        and decision_index.get("latest_decision") == latest_decision_expected
        and decision_index.get("decision_count") == len(latest_decision_files)
        and decision_index.get("decisions", [{}])[0].get("path") == latest_decision_expected
        and latest_decision_json.get("generated_for_revision") == release_manifest["revision"]
        and latest_decision_json.get("path") == latest_decision_expected
        and latest_decision_json.get("decision_id") == pathlib.Path(latest_decision_expected).stem
    )
    record(
        "decision_index_and_latest_decision_json_align",
        decision_index_ok,
        f"decision_index.latest={decision_index.get('latest_decision')} latest_json.path={latest_decision_json.get('path')} decision_count={decision_index.get('decision_count')} actual_files={len(latest_decision_files)}",
    )

    record(
        "queue_index_latest_decision_pointer_aligns",
        queue_index.get("latest_decision") == latest_decision_expected == latest_decision_json.get("path"),
        f"queue_index.latest_decision={queue_index.get('latest_decision')} latest_json.path={latest_decision_json.get('path')} expected={latest_decision_expected}",
    )

    record(
        "rendered_queue_markdown_surfaces_match_machine_state",
        latest_decision_md_actual == latest_decision_md_expected and status_md_actual == status_md_expected and queue_md_actual == queue_md_expected,
        "release_queue/LATEST_DECISION.md, release_queue/STATUS.md, and release_queue/QUEUE.md compared against publishing/render_queue_surfaces.py output",
    )

    referenced_paths = []
    for paths in control_surfaces["question_map"].values():
        if isinstance(paths, str):
            referenced_paths.append(paths)
        else:
            referenced_paths.extend(paths)
    referenced_paths.extend([
        canonical_policy["queue_index"],
        canonical_policy["citation_heads"],
        canonical_policy["citation_heads_json"],
        canonical_policy["public_surface_manifest"],
        canonical_policy["revision_receipt"],
        canonical_policy["manifest_sha256"],
        canonical_policy["control_surfaces"],
        canonical_policy["control_surfaces_json"],
        canonical_policy["archive_index"],
        canonical_policy["archive_index_json"],
        canonical_policy["release_manifest"],
        canonical_policy["version_file"],
        canonical_policy["archive_surface_coherence_check"],
        canonical_policy["archive_surface_coherence_report"],
        canonical_policy["start_here"],
        canonical_policy["context_pack"],
        canonical_policy["pruning_policy"],
        canonical_policy["pruned_transient_paths"],
        canonical_policy["transient_surface_audit_check"],
        canonical_policy["transient_surface_audit_report"],
        canonical_policy["manifest_verification_check"],
        canonical_policy["manifest_verification_report"],
        canonical_policy["decision_index"],
        canonical_policy["latest_decision_json"],
        canonical_policy["decision_index_builder"],
        canonical_policy["context_pack_contract_check"],
        canonical_policy["context_pack_contract_report"],
        canonical_policy["manifest_coverage_check"],
        canonical_policy["manifest_coverage_report"],
        canonical_policy["decision_index_markdown"],
        canonical_policy["lifecycle_gates"],
        canonical_policy["lifecycle_gates_json"],
        canonical_policy["lifecycle_gate_status_builder"],
        canonical_policy["lifecycle_gate_status_report"],
        canonical_policy["surface_rebuild_script"],
        canonical_policy["makefile"],
        canonical_policy["datacube_transfer_ledger"],
        canonical_policy["datacube_transfer_ledger_json"],
        canonical_policy["transfer_sources"],
        canonical_policy["transfer_sources_markdown"],
        canonical_policy["transfer_inputs_sha256"],
        canonical_policy["transfer_source_receipt_check"],
        canonical_policy["transfer_source_receipt_report"],
        canonical_policy["support_manifest_integrity_check"],
        canonical_policy["support_manifest_integrity_report"],
        canonical_policy["citation_closure_audit"],
        canonical_policy["citation_closure_audit_report"],
        canonical_policy["release_readiness_audit"],
        canonical_policy["release_readiness_audit_report"],
        canonical_policy["evidence_pack_policy_check"],
        canonical_policy["evidence_pack_policy_report"],
        canonical_policy["evidence_pack_builder"],
        canonical_policy["evidence_pack_registry"],
        canonical_policy["evidence_pack_integrity_check"],
        canonical_policy["evidence_pack_integrity_report"],
        canonical_policy["freeze_compile_witness"],
        canonical_policy["freeze_compile_witness_check"],
        canonical_policy["freeze_compile_witness_report"],
        canonical_policy["freeze_toolchain_check"],
        canonical_policy["freeze_toolchain_report"],
        canonical_policy["freeze_packet_builder"],
        canonical_policy["freeze_packet_registry"],
        canonical_policy["freeze_packet_integrity_check"],
        canonical_policy["freeze_packet_integrity_report"],
        canonical_policy["publication_boundary_check"],
        canonical_policy["publication_boundary_report"],
        canonical_policy["publication_rehearsal_check"],
        canonical_policy["publication_rehearsal_report"],
        canonical_policy["release_freeze_plan_builder"],
        canonical_policy["release_freeze_plan_json"],
        canonical_policy["release_freeze_plan_markdown"],
        canonical_policy["review_inventory_integrity_check"],
        canonical_policy["review_inventory_integrity_report"],
        canonical_policy["operator_command_hygiene_check"],
        canonical_policy["operator_command_hygiene_report"],
        canonical_policy["assurance_artifacts"],
        canonical_policy["assurance_artifacts_markdown"],
        canonical_policy["assurance_catalog_renderer"],
        canonical_policy["assurance_catalog_integrity_check"],
        canonical_policy["assurance_catalog_integrity_report"],
        canonical_policy["tooling_inventory_builder"],
        canonical_policy["tooling_inventory"],
        canonical_policy["tooling_inventory_integrity_check"],
        canonical_policy["tooling_inventory_integrity_report"],
        canonical_policy["report_schema_coverage_check"],
        canonical_policy["report_schema_coverage_report"],
        canonical_policy["report_warning_policy_check"],
        canonical_policy["report_warning_policy_report"],
        canonical_policy["report_warning_policy_schema"],
        canonical_policy["rebuild_fixed_point_coverage_check"],
        canonical_policy["rebuild_fixed_point_coverage_report"],
        canonical_policy["rebuild_fixed_point_coverage_schema"],
        canonical_policy["research_metadata_integrity_check"],
        canonical_policy["research_metadata_integrity_report"],
        canonical_policy["publication_target_portability_check"],
        canonical_policy["publication_target_portability_report"],
        canonical_policy["publication_target_portability_schema"],
        canonical_policy["path_portability_check"],
        canonical_policy["path_portability_report"],
        canonical_policy["path_portability_schema"],
        canonical_policy["archive_packaging_reproducibility_check"],
        canonical_policy["archive_packaging_reproducibility_report"],
        canonical_policy["archive_packaging_reproducibility_schema"],
        canonical_policy["archive_entry_security_check"],
        canonical_policy["archive_entry_security_report"],
        canonical_policy["archive_entry_security_schema"],
        canonical_policy["bundle_identity_consistency_check"],
        canonical_policy["bundle_identity_consistency_report"],
        canonical_policy["bundle_identity_consistency_schema"],
        canonical_policy["control_surface_path_integrity_check"],
        canonical_policy["control_surface_path_integrity_report"],
        canonical_policy["control_surface_path_integrity_schema"],
        canonical_policy["duplicate_content_policy_check"],
        canonical_policy["duplicate_content_policy_report"],
        canonical_policy["duplicate_content_policy_schema"],
        canonical_policy["tex_source_safety_check"],
        canonical_policy["tex_source_safety_report"],
        canonical_policy["tex_source_safety_schema"],
        canonical_policy["secret_material_quarantine_check"],
        canonical_policy["secret_material_quarantine_report"],
        canonical_policy["secret_material_quarantine_schema"],
        canonical_policy["makefile_target_integrity_check"],
        canonical_policy["makefile_target_integrity_report"],
        canonical_policy["makefile_target_integrity_schema"],
        canonical_policy["manifest_canonicality_check"],
        canonical_policy["manifest_canonicality_report"],
        canonical_policy["manifest_canonicality_schema"],
        canonical_policy["freeze_warning_resolution_check"],
        canonical_policy["freeze_warning_resolution_report"],
        canonical_policy["freeze_warning_resolution_schema"],
        canonical_policy["toolchain_fingerprint_check"],
        canonical_policy["toolchain_fingerprint_report"],
        canonical_policy["toolchain_fingerprint_schema"],
        canonical_policy["json_surface_catalog_check"],
        canonical_policy["json_surface_catalog_report"],
        canonical_policy["json_surface_catalog_schema"],
        canonical_policy["schema_catalog_integrity_check"],
        canonical_policy["schema_catalog_integrity_report"],
        canonical_policy["schema_catalog_integrity_schema"],
        canonical_policy["json_key_integrity_check"],
        canonical_policy["json_key_integrity_report"],
        canonical_policy["json_key_integrity_schema"],
        canonical_policy["text_surface_normalization_check"],
        canonical_policy["text_surface_normalization_report"],
        canonical_policy["text_surface_normalization_schema"],
        canonical_policy["unicode_control_hygiene_check"],
        canonical_policy["unicode_control_hygiene_report"],
        canonical_policy["unicode_control_hygiene_schema"],
        canonical_policy["tooling_static_integrity_check"],
        canonical_policy["tooling_static_integrity_report"],
        canonical_policy["tooling_static_integrity_schema"],
    ])
    research_object_paths = list(canonical_policy.get("research_object_metadata", {}).values())
    referenced_paths.extend(research_object_paths)
    missing_paths = sorted({p for p in referenced_paths if not p.endswith('/') and not (root / p).exists()})
    record(
        "control_surface_paths_exist",
        not missing_paths,
        "missing=" + (", ".join(missing_paths) if missing_paths else "none"),
    )
    research_object_missing = sorted({p for p in research_object_paths if not (root / p).exists()})
    record(
        "research_object_metadata_paths_exist",
        not research_object_missing,
        "missing=" + (", ".join(research_object_missing) if research_object_missing else "none"),
    )

    manifest_paths = load_json(root / "MANIFEST.json")["files"]
    sha_paths = manifest_sha256_paths(root / "MANIFEST.sha256")
    manifest_ok = sorted(manifest_paths) == sorted(set(sha_paths + ["MANIFEST.sha256"]))
    record(
        "manifest_sha256_covers_manifest_json_files",
        manifest_ok,
        f"manifest_json_files={len(manifest_paths)} manifest_sha256_entries={len(sha_paths)}",
    )

    context_pack_ok = (
        context_pack["revision"] == release_manifest["revision"]
        and context_pack["bundle"] == release_manifest["bundle"]
        and context_pack["current_posture"]["queue"] == {
            "candidate": queue_index["summary"]["candidate"],
            "published_ready": queue_index["summary"]["published_ready"],
            "hold": queue_index["summary"]["hold"],
            "published": queue_index["summary"].get("published", 0),
        }
        and context_pack["current_posture"]["legacy_public_head_count"] == citation_heads["summary"]["legacy_public_head_count"]
        and context_pack["current_posture"]["new_post_policy_anonymity_head_count"] == citation_heads["summary"]["new_post_policy_anonymity_head_count"]
        and context_pack["current_posture"]["repo_frozen_noncanonical_entry_count"] == citation_heads["summary"]["repo_frozen_noncanonical_entry_count"]
        and all((root / p).exists() for p in context_pack["must_read"])
    )
    record(
        "context_pack_matches_revision_and_state",
        context_pack_ok,
        f"context_pack.revision={context_pack['revision']} bundle={context_pack['bundle']} must_read_count={len(context_pack['must_read'])}",
    )

    surface_schema_ok = surface_schema_validation.get("status") == "pass" and surface_schema_validation.get("summary", {}).get("checks_failed") == 0
    record(
        "surface_schema_validation_is_pass",
        surface_schema_ok,
        f"surface_schema_status={surface_schema_validation.get('status')} failed={surface_schema_validation.get('summary', {}).get('checks_failed')}",
    )

    archive_invariants_ok = archive_invariants.get("status") == "pass" and archive_invariants.get("summary", {}).get("checks_failed") == 0
    record(
        "archive_invariants_are_pass",
        archive_invariants_ok,
        f"archive_invariants_status={archive_invariants.get('status')} failed={archive_invariants.get('summary', {}).get('checks_failed')}",
    )

    context_pack_contract_ok = context_pack_contract.get("status") == "pass" and context_pack_contract.get("summary", {}).get("checks_failed") == 0
    record(
        "context_pack_contract_is_pass",
        context_pack_contract_ok,
        f"context_pack_contract_status={context_pack_contract.get('status')} failed={context_pack_contract.get('summary', {}).get('checks_failed')}",
    )

    context_pack_budget_ok = context_pack_budget.get("status") == "pass" and context_pack_budget.get("summary", {}).get("checks_failed") == 0
    record(
        "context_pack_budget_is_pass",
        context_pack_budget_ok,
        f"context_pack_budget_status={context_pack_budget.get('status')} failed={context_pack_budget.get('summary', {}).get('checks_failed')} bytes={context_pack_budget.get('summary', {}).get('bytes')}",
    )

    archive_budget_ok = archive_budget.get("status") == "pass" and archive_budget.get("summary", {}).get("checks_failed") == 0
    record(
        "archive_budget_is_pass",
        archive_budget_ok,
        f"archive_budget_status={archive_budget.get('status')} failed={archive_budget.get('summary', {}).get('checks_failed')} bytes={archive_budget.get('summary', {}).get('bytes')} files={archive_budget.get('summary', {}).get('file_count')}",
    )

    transient_ok = transient_audit.get("status") == "pass" and transient_audit.get("summary", {}).get("disallowed_file_count") == 0
    record(
        "transient_surface_audit_is_pass",
        transient_ok,
        f"transient_status={transient_audit.get('status')} disallowed={transient_audit.get('summary', {}).get('disallowed_file_count')}",
    )

    manifest_verification_ok = manifest_verification.get("status") == "pass" and not manifest_verification.get("missing_paths") and not manifest_verification.get("mismatched_paths")
    record(
        "manifest_sha256_verification_is_pass",
        manifest_verification_ok,
        f"manifest_verification_status={manifest_verification.get('status')} verified={manifest_verification.get('verified_entry_count')}",
    )

    manifest_coverage_ok = (
        manifest_coverage.get("status") == "pass"
        and not manifest_coverage.get("unexpected_unlisted_paths")
        and not manifest_coverage.get("missing_paths")
        and not manifest_coverage.get("duplicate_entries")
    )
    record(
        "manifest_coverage_audit_is_pass",
        manifest_coverage_ok,
        f"manifest_coverage_status={manifest_coverage.get('status')} unlisted={manifest_coverage.get('summary', {}).get('unlisted_file_count')} missing={manifest_coverage.get('summary', {}).get('missing_path_count')}",
    )


    path_summary = path_portability.get("summary", {})
    path_portability_ok = (
        path_portability.get("status") == "pass"
        and path_portability.get("generated_for_revision") == release_manifest["revision"]
        and path_portability.get("checked_bundle") == release_manifest["bundle"]
        and path_portability.get("publication_authorized") is False
        and path_summary.get("checks_failed") == 0
        and path_summary.get("nfc_collision_count") == 0
        and path_summary.get("casefold_collision_count") == 0
    )
    record(
        "path_portability_is_pass",
        path_portability_ok,
        f"path_portability_status={path_portability.get('status')} paths={path_summary.get('path_count')} max_path_bytes={path_summary.get('max_path_bytes')} nfc_collisions={path_summary.get('nfc_collision_count')} casefold_collisions={path_summary.get('casefold_collision_count')} failed={path_summary.get('checks_failed')}",
    )


    lifecycle_ok = (
        lifecycle_gate_status.get("generated_for_revision") == release_manifest["revision"]
        and lifecycle_gate_status.get("bundle") == release_manifest["bundle"]
        and len(lifecycle_gate_status.get("gates", [])) >= 5
    )
    record(
        "lifecycle_gate_status_matches_bundle",
        lifecycle_ok,
        f"lifecycle_revision={lifecycle_gate_status.get('generated_for_revision')} lifecycle_bundle={lifecycle_gate_status.get('bundle')} gate_count={len(lifecycle_gate_status.get('gates', []))}",
    )

    transfer_source_receipt_ok = transfer_source_receipt.get("status") == "pass" and transfer_source_receipt.get("summary", {}).get("checks_failed") == 0
    record(
        "transfer_source_receipt_is_pass",
        transfer_source_receipt_ok,
        f"transfer_source_receipt_status={transfer_source_receipt.get('status')} failed={transfer_source_receipt.get('summary', {}).get('checks_failed')}",
    )


    support_manifest_integrity_ok = support_manifest_integrity.get("status") == "pass" and support_manifest_integrity.get("summary", {}).get("checks_failed") == 0
    record(
        "support_manifest_integrity_is_pass",
        support_manifest_integrity_ok,
        f"support_manifest_integrity_status={support_manifest_integrity.get('status')} failed={support_manifest_integrity.get('summary', {}).get('checks_failed')} file_rows={support_manifest_integrity.get('summary', {}).get('file_rows_checked')}",
    )

    citation_closure_ok = (
        citation_closure_audit.get("status") == "pass"
        and citation_closure_audit.get("generated_for_revision") == release_manifest["revision"]
        and citation_closure_audit.get("summary", {}).get("papers_failed") == 0
        and citation_closure_audit.get("summary", {}).get("globally_undefined_citation_count") == 0
    )
    record(
        "citation_closure_audit_is_pass",
        citation_closure_ok,
        f"citation_closure_status={citation_closure_audit.get('status')} papers_checked={citation_closure_audit.get('summary', {}).get('papers_checked')} papers_failed={citation_closure_audit.get('summary', {}).get('papers_failed')} global_undefined={citation_closure_audit.get('summary', {}).get('globally_undefined_citation_count')}",
    )

    review_inventory_integrity_ok = review_inventory_integrity.get("status") == "pass" and review_inventory_integrity.get("generated_for_revision") == release_manifest["revision"] and review_inventory_integrity.get("summary", {}).get("checks_failed") == 0 and review_inventory_integrity.get("summary", {}).get("sha256_prefix_mismatch_count") == 0
    record(
        "review_inventory_integrity_is_pass",
        review_inventory_integrity_ok,
        f"review_inventory_status={review_inventory_integrity.get('status')} entries={review_inventory_integrity.get('summary', {}).get('inventory_entry_count')} sha_mismatches={review_inventory_integrity.get('summary', {}).get('sha256_prefix_mismatch_count')} unqueued={review_inventory_integrity.get('summary', {}).get('unqueued_inventory_entry_count')}",
    )

    operator_command_hygiene_ok = operator_command_hygiene.get("status") == "pass" and operator_command_hygiene.get("generated_for_revision") == release_manifest["revision"] and operator_command_hygiene.get("summary", {}).get("unsafe_command_line_count") == 0
    record(
        "operator_command_hygiene_is_pass",
        operator_command_hygiene_ok,
        f"operator_command_hygiene_status={operator_command_hygiene.get('status')} unsafe_lines={operator_command_hygiene.get('summary', {}).get('unsafe_command_line_count')} checked_files={operator_command_hygiene.get('summary', {}).get('checked_file_count')}",
    )

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
    record(
        "assurance_catalog_integrity_is_pass",
        assurance_catalog_ok,
        f"assurance_status={assurance_catalog_integrity.get('status')} paths={assurance_summary.get('catalog_path_count')} missing={assurance_summary.get('missing_path_count')} markdown_matches_json={assurance_summary.get('markdown_matches_json')}",
    )

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
    record(
        "tooling_inventory_integrity_is_pass",
        tooling_ok,
        f"tooling_status={tooling_inventory_integrity.get('status')} scripts={tooling_summary.get('actual_script_count')} inventory={tooling_summary.get('inventory_script_count')} sha_mismatches={tooling_summary.get('sha256_mismatch_count')} publication_authorized={tooling_inventory_integrity.get('publication_authorized')}",
    )

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
    record(
        "report_schema_coverage_is_pass",
        report_schema_ok,
        f"report_schema_status={report_schema_coverage.get('status')} reports={report_schema_summary.get('report_json_count')} checked={report_schema_summary.get('report_json_schema_checked_count')} generic={report_schema_summary.get('generic_report_schema_count')} failed={report_schema_summary.get('failed_report_schema_count')}",
    )

    report_identity_summary = report_identity_coverage.get("summary", {})
    report_identity_ok = (
        report_identity_coverage.get("status") == "pass"
        and report_identity_coverage.get("generated_for_revision") == release_manifest["revision"]
        and report_identity_coverage.get("checked_bundle") == release_manifest["bundle"]
        and report_identity_coverage.get("publication_authorized") is False
        and report_identity_summary.get("checks_failed") == 0
        and report_identity_summary.get("identity_bound_report_count") == report_identity_summary.get("report_json_count")
    )
    record(
        "report_identity_coverage_is_pass",
        report_identity_ok,
        f"report_identity_status={report_identity_coverage.get('status')} reports={report_identity_summary.get('report_json_count')} bound={report_identity_summary.get('identity_bound_report_count')} failed={report_identity_summary.get('checks_failed')}",
    )

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
    record(
        "report_warning_policy_is_pass",
        report_warning_ok,
        f"report_warning_status={report_warning_policy.get('status')} reports={report_warning_summary.get('report_json_count')} with_warnings={report_warning_summary.get('reports_with_warnings')} warning_count_fields={report_warning_summary.get('positive_warning_count_field_count')}",
    )

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
    record(
        "publication_artifact_quarantine_is_pass",
        quarantine_ok,
        f"publication_artifact_quarantine_status={publication_artifact_quarantine.get('status')} disallowed={quarantine_summary.get('disallowed_artifact_count')} compile_digest_hits={quarantine_summary.get('shipped_compile_output_digest_hit_count')} failed={quarantine_summary.get('checks_failed')}",
    )

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
    record(
        "publication_target_portability_is_pass",
        target_port_ok,
        f"publication_target_portability_status={publication_target_portability.get('status')} rows={target_port_summary.get('target_row_count')} nonportable={target_port_summary.get('nonportable_count')} already_exists={target_port_summary.get('already_exists_count')}",
    )

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
    record(
        "archive_entry_security_is_pass",
        entry_security_ok,
        f"archive_entry_security_status={archive_entry_security.get('status')} tree_files={entry_security_summary.get('tree_file_count')} zip_members={entry_security_summary.get('zip_member_count')} symlink_or_special={entry_security_summary.get('symlink_or_special_count')} unexpected_executable={entry_security_summary.get('unexpected_executable_count')} failed={entry_security_summary.get('checks_failed')}",
    )

    bundle_identity_summary = bundle_identity_consistency.get("summary", {})
    bundle_identity_ok = (
        bundle_identity_consistency.get("status") == "pass"
        and bundle_identity_consistency.get("generated_for_revision") == release_manifest["revision"]
        and bundle_identity_consistency.get("checked_bundle") == release_manifest["bundle"]
        and bundle_identity_consistency.get("publication_authorized") is False
        and bundle_identity_summary.get("checks_failed") == 0
    )
    record(
        "bundle_identity_consistency_is_pass",
        bundle_identity_ok,
        f"bundle_identity_status={bundle_identity_consistency.get('status')} surfaces={bundle_identity_summary.get('identity_surface_count')} failed={bundle_identity_summary.get('checks_failed')}",
    )

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
    record(
        "control_surface_path_integrity_is_pass",
        control_path_ok,
        f"control_path_status={control_surface_path_integrity.get('status')} references={control_path_summary.get('path_reference_count')} unique={control_path_summary.get('unique_path_reference_count')} missing={control_path_summary.get('missing_reference_count')} nonportable={control_path_summary.get('nonportable_reference_count')} unsafe={control_path_summary.get('unsafe_reference_count')}",
    )

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
    record(
        "duplicate_content_policy_is_pass",
        duplicate_content_ok,
        f"duplicate_content_status={duplicate_content_policy.get('status')} groups={duplicate_content_summary.get('duplicate_group_count')} duplicate_files={duplicate_content_summary.get('duplicate_file_count')} unexpected={duplicate_content_summary.get('unexpected_duplicate_group_count')} missing_allowlist={duplicate_content_summary.get('missing_allowlist_path_count')}",
    )
    tex_summary = tex_source_safety.get("summary", {})
    tex_safety_ok = (
        tex_source_safety.get("status") == "pass"
        and tex_source_safety.get("generated_for_revision") == release_manifest["revision"]
        and tex_source_safety.get("checked_bundle") == release_manifest["bundle"]
        and tex_source_safety.get("publication_authorized") is False
        and tex_summary.get("checks_failed") == 0
        and tex_summary.get("finding_count") == 0
        and tex_summary.get("negative_control_count", 0) >= 6
        and tex_summary.get("negative_control_failed_count") == 0
        and "suspicious_doubled_command_escape" in tex_source_safety.get("policy", {}).get("risk_categories", [])
    )
    record(
        "tex_source_safety_is_pass",
        tex_safety_ok,
        f"tex_source_safety_status={tex_source_safety.get('status')} tex_files={tex_summary.get('tex_file_count')} findings={tex_summary.get('finding_count')} negative_controls={tex_summary.get('negative_control_count')} negative_control_failures={tex_summary.get('negative_control_failed_count')}",
    )

    secret_summary = secret_material_quarantine.get("summary", {})
    secret_quarantine_ok = (
        secret_material_quarantine.get("status") == "pass"
        and secret_material_quarantine.get("generated_for_revision") == release_manifest["revision"]
        and secret_material_quarantine.get("checked_bundle") == release_manifest["bundle"]
        and secret_material_quarantine.get("publication_authorized") is False
        and secret_summary.get("checks_failed") == 0
        and secret_summary.get("finding_count") == 0
        and secret_summary.get("private_key_marker_count") == 0
        and secret_summary.get("token_like_pattern_count") == 0
    )
    record(
        "secret_material_quarantine_is_pass",
        secret_quarantine_ok,
        f"secret_material_status={secret_material_quarantine.get('status')} text_surfaces={secret_summary.get('text_surface_count')} findings={secret_summary.get('finding_count')} token_like={secret_summary.get('token_like_pattern_count')}",
    )

    makefile_summary = makefile_target_integrity.get("summary", {})
    makefile_integrity_ok = (
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
    record(
        "makefile_target_integrity_is_pass",
        makefile_integrity_ok,
        f"makefile_integrity_status={makefile_target_integrity.get('status')} targets={makefile_summary.get('parsed_target_count')} commands={makefile_summary.get('command_count')} failures={makefile_summary.get('checks_failed')}",
    )

    manifest_canon_summary = manifest_canonicality.get("summary", {})
    manifest_canon_ok = (
        manifest_canonicality.get("status") == "pass"
        and manifest_canonicality.get("generated_for_revision") == release_manifest["revision"]
        and manifest_canonicality.get("checked_bundle") == release_manifest["bundle"]
        and manifest_canonicality.get("publication_authorized") is False
        and manifest_canon_summary.get("checks_failed") == 0
        and manifest_canon_summary.get("digest_mismatch_count") == 0
    )
    record(
        "manifest_canonicality_is_pass",
        manifest_canon_ok,
        f"manifest_canonicality_status={manifest_canonicality.get('status')} files={manifest_canon_summary.get('manifest_json_file_count')} sha_entries={manifest_canon_summary.get('manifest_sha256_entry_count')} failures={manifest_canon_summary.get('checks_failed')}",
    )

    warning_resolution_summary = freeze_warning_resolution.get("summary", {})
    warning_resolution_ok = (
        freeze_warning_resolution.get("status") == "pass"
        and freeze_warning_resolution.get("generated_for_revision") == release_manifest["revision"]
        and freeze_warning_resolution.get("checked_bundle") == release_manifest["bundle"]
        and freeze_warning_resolution.get("publication_authorized") is False
        and warning_resolution_summary.get("checks_failed") == 0
        and warning_resolution_summary.get("unresolved_notice_count") == 0
    )
    record(
        "freeze_warning_resolution_is_pass",
        warning_resolution_ok,
        f"freeze_warning_status={freeze_warning_resolution.get('status')} notices={warning_resolution_summary.get('preflight_notice_count')} resolved={warning_resolution_summary.get('resolved_notice_count')} unresolved={warning_resolution_summary.get('unresolved_notice_count')}",
    )

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
    record(
        "toolchain_fingerprint_is_pass",
        fingerprint_ok,
        f"toolchain_fingerprint_status={toolchain_fingerprint.get('status')} command={fingerprint_summary.get('latex_command')} gate={fingerprint_summary.get('compile_gate_status')} present={fingerprint_summary.get('fingerprint_present')} failures={fingerprint_summary.get('checks_failed')} compile_surfaces={fingerprint_summary.get('compile_surface_fingerprint_count')}/{fingerprint_summary.get('compile_surface_fingerprint_expected_count')} surface_failures={fingerprint_summary.get('compile_surface_fingerprint_fail_count')} negative_failures={fingerprint_summary.get('negative_control_failed_count')}",
    )

    archive_index_summary = archive_index_integrity.get("summary", {})
    archive_index_ok = (
        archive_index_integrity.get("status") == "pass"
        and archive_index_integrity.get("generated_for_revision") == release_manifest["revision"]
        and archive_index_integrity.get("checked_bundle") == release_manifest["bundle"]
        and archive_index_integrity.get("publication_authorized") is False
        and archive_index_summary.get("checks_failed") == 0
    )
    record(
        "archive_index_integrity_is_pass",
        archive_index_ok,
        f"archive_index_status={archive_index_integrity.get('status')} checks_failed={archive_index_summary.get('checks_failed')} recent_checked={archive_index_summary.get('recent_revision_count_checked')}",
    )

    rebuild_fixed_point_summary = rebuild_fixed_point_coverage.get("summary", {})
    rebuild_fixed_point_ok = (
        rebuild_fixed_point_coverage.get("status") == "pass"
        and rebuild_fixed_point_coverage.get("generated_for_revision") == release_manifest["revision"]
        and rebuild_fixed_point_coverage.get("checked_bundle") == release_manifest["bundle"]
        and rebuild_fixed_point_coverage.get("publication_authorized") is False
        and rebuild_fixed_point_summary.get("checks_failed") == 0
        and rebuild_fixed_point_summary.get("missing_tail_target_count") == 0
        and rebuild_fixed_point_summary.get("missing_tail_target_file_count") == 0
    )
    record(
        "rebuild_fixed_point_coverage_is_pass",
        rebuild_fixed_point_ok,
        f"rebuild_fixed_point_status={rebuild_fixed_point_coverage.get('status')} tail_outputs={rebuild_fixed_point_summary.get('tail_output_count')} tail_targets={rebuild_fixed_point_summary.get('tail_target_count')} missing={rebuild_fixed_point_summary.get('missing_tail_target_count')} failed={rebuild_fixed_point_summary.get('checks_failed')}",
    )

    invariant_catalog_summary = invariant_catalog_integrity.get("summary", {})
    invariant_catalog_ok = (
        invariant_catalog_integrity.get("status") == "pass"
        and invariant_catalog_integrity.get("generated_for_revision") == release_manifest["revision"]
        and invariant_catalog_integrity.get("checked_bundle") == release_manifest["bundle"]
        and invariant_catalog_integrity.get("publication_authorized") is False
        and invariant_catalog_summary.get("checks_failed") == 0
        and invariant_catalog_summary.get("declared_invariant_count") == invariant_catalog_summary.get("checked_invariant_count") == invariant_catalog_summary.get("markdown_invariant_count")
        and invariant_catalog_summary.get("duplicate_declared_id_count") == 0
        and invariant_catalog_summary.get("duplicate_checked_id_count") == 0
    )
    record(
        "invariant_catalog_integrity_is_pass",
        invariant_catalog_ok,
        f"invariant_catalog_status={invariant_catalog_integrity.get('status')} declared={invariant_catalog_summary.get('declared_invariant_count')} checked={invariant_catalog_summary.get('checked_invariant_count')} markdown={invariant_catalog_summary.get('markdown_invariant_count')} failed={invariant_catalog_summary.get('checks_failed')}",
    )

    publication_decision_template_ok = (
        publication_decision_template.get("status") == "pass"
        and publication_decision_template.get("generated_for_revision") == release_manifest["revision"]
        and publication_decision_template.get("checked_bundle") == release_manifest["bundle"]
        and publication_decision_template.get("publication_authorized") is False
        and publication_decision_template.get("summary", {}).get("checks_failed") == 0
    )
    record(
        "publication_decision_template_is_pass",
        publication_decision_template_ok,
        f"publication_decision_template_status={publication_decision_template.get('status')} required_present={publication_decision_template.get('summary', {}).get('required_fragments_present')} publication_authorized={publication_decision_template.get('publication_authorized')}",
    )

    authorization_summary = publication_decision_authorization.get("summary", {})
    publication_decision_authorization_ok = (
        publication_decision_authorization.get("status") == "pass"
        and publication_decision_authorization.get("generated_for_revision") == release_manifest["revision"]
        and publication_decision_authorization.get("checked_bundle") == release_manifest["bundle"]
        and publication_decision_authorization.get("publication_authorized") is False
        and authorization_summary.get("checks_failed") == 0
        and authorization_summary.get("publish_decision_count") == authorization_summary.get("valid_publish_decision_count")
    )
    record(
        "publication_decision_authorization_scan_is_pass",
        publication_decision_authorization_ok,
        f"publication_decision_authorization_status={publication_decision_authorization.get('status')} publish_decisions={authorization_summary.get('publish_decision_count')} valid={authorization_summary.get('valid_publish_decision_count')} failed={authorization_summary.get('checks_failed')}",
    )

    archive_packaging_recipe_ok = (
        archive_packaging_recipe.get("status") == "pass"
        and archive_packaging_recipe.get("generated_for_revision") == release_manifest["revision"]
        and archive_packaging_recipe.get("checked_bundle") == release_manifest["bundle"]
        and archive_packaging_recipe.get("publication_authorized") is False
        and archive_packaging_recipe.get("summary", {}).get("checks_failed") == 0
    )
    record(
        "archive_packaging_recipe_is_pass",
        archive_packaging_recipe_ok,
        f"archive_packaging_recipe_status={archive_packaging_recipe.get('status')} input_files={archive_packaging_recipe.get('summary', {}).get('input_file_count')} manifest_files={archive_packaging_recipe.get('summary', {}).get('manifest_file_count')} dry_run={archive_packaging_recipe.get('summary', {}).get('dry_run_status')}",
    )



    reproducibility_summary = archive_packaging_reproducibility.get("summary", {})
    archive_packaging_reproducibility_ok = (
        archive_packaging_reproducibility.get("status") == "pass"
        and archive_packaging_reproducibility.get("generated_for_revision") == release_manifest["revision"]
        and archive_packaging_reproducibility.get("checked_bundle") == release_manifest["bundle"]
        and archive_packaging_reproducibility.get("publication_authorized") is False
        and reproducibility_summary.get("checks_failed") == 0
        and reproducibility_summary.get("two_trial_zip_sha256_equal") is True
        and reproducibility_summary.get("two_trial_member_metadata_equal") is True
    )
    record(
        "archive_packaging_reproducibility_is_pass",
        archive_packaging_reproducibility_ok,
        f"packaging_reproducibility_status={archive_packaging_reproducibility.get('status')} trials={reproducibility_summary.get('trial_count')} sha_equal={reproducibility_summary.get('two_trial_zip_sha256_equal')} metadata_equal={reproducibility_summary.get('two_trial_member_metadata_equal')} failed={reproducibility_summary.get('checks_failed')}",
    )

    json_catalog_summary = json_surface_catalog.get("summary", {})
    json_surface_catalog_ok = (
        json_surface_catalog.get("status") == "pass"
        and json_surface_catalog.get("generated_for_revision") == release_manifest["revision"]
        and json_surface_catalog.get("checked_bundle") == release_manifest["bundle"]
        and json_surface_catalog.get("publication_authorized") is False
        and json_catalog_summary.get("checks_failed") == 0
        and json_catalog_summary.get("unclassified_json_count") == 0
    )
    record(
        "json_surface_catalog_is_pass",
        json_surface_catalog_ok,
        f"json_surface_catalog_status={json_surface_catalog.get('status')} json_files={json_catalog_summary.get('json_file_count')} schema_checked={json_catalog_summary.get('schema_checked_json_count')} unclassified={json_catalog_summary.get('unclassified_json_count')} failed={json_catalog_summary.get('checks_failed')}",
    )

    content_leakage_summary = content_leakage.get("summary", {})
    content_leakage_ok = (
        content_leakage.get("status") == "pass"
        and content_leakage.get("generated_for_revision") == release_manifest["revision"]
        and content_leakage.get("checked_bundle") == release_manifest["bundle"]
        and content_leakage.get("publication_authorized") is False
        and content_leakage_summary.get("finding_count") == 0
        and content_leakage_summary.get("checks_failed") == 0
    )
    record(
        "content_leakage_guard_is_pass",
        content_leakage_ok,
        f"content_leakage_status={content_leakage.get('status')} text_files={content_leakage_summary.get('text_file_count')} findings={content_leakage_summary.get('finding_count')} failed={content_leakage_summary.get('checks_failed')}",
    )



    decision_note_summary = decision_note_integrity.get("summary", {})
    decision_action_counts = decision_note_summary.get("publication_action_counts", {}) if isinstance(decision_note_summary.get("publication_action_counts", {}), dict) else {}
    decision_note_ok = (
        decision_note_integrity.get("status") == "pass"
        and decision_note_integrity.get("generated_for_revision") == release_manifest["revision"]
        and decision_note_integrity.get("checked_bundle") == release_manifest["bundle"]
        and decision_note_integrity.get("publication_authorized") is False
        and decision_note_summary.get("checks_failed") == 0
        and decision_note_summary.get("decision_note_count") == decision_note_summary.get("decision_index_count")
        and (int(decision_action_counts.get("none", 0)) + int(decision_action_counts.get("publish", 0))) == decision_note_summary.get("decision_note_count")
        and decision_note_summary.get("subject_path_missing_count") == 0
    )
    record(
        "decision_note_integrity_is_pass",
        decision_note_ok,
        f"decision_note_status={decision_note_integrity.get('status')} notes={decision_note_summary.get('decision_note_count')} action_counts={decision_action_counts} subject_missing={decision_note_summary.get('subject_path_missing_count')} failed={decision_note_summary.get('checks_failed')}",
    )

    schema_catalog_summary = schema_catalog_integrity.get("summary", {})
    schema_catalog_ok = (
        schema_catalog_integrity.get("status") == "pass"
        and schema_catalog_integrity.get("generated_for_revision") == release_manifest["revision"]
        and schema_catalog_integrity.get("checked_bundle") == release_manifest["bundle"]
        and schema_catalog_integrity.get("publication_authorized") is False
        and schema_catalog_summary.get("checks_failed") == 0
        and schema_catalog_summary.get("missing_referenced_schema_count") == 0
    )
    record(
        "schema_catalog_integrity_is_pass",
        schema_catalog_ok,
        f"schema_catalog_status={schema_catalog_integrity.get('status')} schemas={schema_catalog_summary.get('schema_document_count')} referenced={schema_catalog_summary.get('referenced_schema_count')} missing={schema_catalog_summary.get('missing_referenced_schema_count')} unreferenced={schema_catalog_summary.get('unreferenced_schema_count')} failed={schema_catalog_summary.get('checks_failed')}",
    )

    tooling_static_summary = tooling_static_integrity.get("summary", {})
    tooling_static_ok = (
        tooling_static_integrity.get("status") == "pass"
        and tooling_static_integrity.get("generated_for_revision") == release_manifest["revision"]
        and tooling_static_integrity.get("checked_bundle") == release_manifest["bundle"]
        and tooling_static_integrity.get("publication_authorized") is False
        and tooling_static_summary.get("checks_failed") == 0
        and tooling_static_summary.get("syntax_failure_count") == 0
        and tooling_static_summary.get("duplicate_literal_dict_key_count") == 0
        and tooling_static_summary.get("unexpected_top_level_statement_count") == 0
    )
    record(
        "tooling_static_integrity_is_pass",
        tooling_static_ok,
        f"tooling_static_status={tooling_static_integrity.get('status')} scripts={tooling_static_summary.get('script_count')} syntax_failures={tooling_static_summary.get('syntax_failure_count')} duplicate_keys={tooling_static_summary.get('duplicate_literal_dict_key_count')} top_level={tooling_static_summary.get('unexpected_top_level_statement_count')} failed={tooling_static_summary.get('checks_failed')}",
    )

    py_smoke_summary = python_entrypoint_smoke.get("summary", {})
    py_smoke_ok = (
        python_entrypoint_smoke.get("status") == "pass"
        and python_entrypoint_smoke.get("generated_for_revision") == release_manifest["revision"]
        and python_entrypoint_smoke.get("checked_bundle") == release_manifest["bundle"]
        and python_entrypoint_smoke.get("publication_authorized") is False
        and py_smoke_summary.get("checks_failed") == 0
        and py_smoke_summary.get("compile_failed") == 0
        and py_smoke_summary.get("entrypoint_failed") == 0
        and py_smoke_summary.get("compile_checked") == py_smoke_summary.get("python_source_count")
        and py_smoke_summary.get("entrypoint_checked", 0) >= tooling_inventory.get("script_count", 0)
        and py_smoke_summary.get("unexpected_external_import_count") == 0
        and py_smoke_summary.get("external_import_path_violation_count") == 0
        and py_smoke_summary.get("external_dependency_unavailable_count") == 0
        and py_smoke_summary.get("import_negative_control_count", 0) >= 5
        and py_smoke_summary.get("import_negative_control_failed_count") == 0
    )
    record(
        "python_entrypoint_smoke_is_pass_and_tooling_current",
        py_smoke_ok,
        f"python_entrypoint_status={python_entrypoint_smoke.get('status')} sources={py_smoke_summary.get('python_source_count')} compile_failed={py_smoke_summary.get('compile_failed')} entrypoint_failed={py_smoke_summary.get('entrypoint_failed')} unexpected_external={py_smoke_summary.get('unexpected_external_import_count')} path_violations={py_smoke_summary.get('external_import_path_violation_count')} unavailable_external={py_smoke_summary.get('external_dependency_unavailable_count')} import_negative_failures={py_smoke_summary.get('import_negative_control_failed_count')} entrypoints={py_smoke_summary.get('entrypoint_checked')} tooling_scripts={tooling_inventory.get('script_count')}",
    )

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
    record(
        "json_key_integrity_is_pass",
        json_key_ok,
        f"json_key_status={json_key_integrity.get('status')} json_files={json_key_summary.get('json_file_count')} duplicate_key_failures={json_key_summary.get('duplicate_key_failure_count')} nonfinite_failures={json_key_summary.get('non_finite_numeric_literal_failure_count')} failed={json_key_summary.get('checks_failed')}",
    )

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
    record(
        "text_surface_normalization_is_pass",
        text_norm_ok,
        f"text_norm_status={text_surface_normalization.get('status')} text_files={text_norm_summary.get('text_surface_count')} cr={text_norm_summary.get('carriage_return_failure_count')} nul={text_norm_summary.get('nul_byte_failure_count')} utf8={text_norm_summary.get('utf8_failure_count')} warnings={text_norm_summary.get('warning_count')} failed={text_norm_summary.get('checks_failed')}",
    )

    unicode_summary = unicode_control_hygiene.get("summary", {})
    unicode_hygiene_ok = (
        unicode_control_hygiene.get("status") == "pass"
        and unicode_control_hygiene.get("generated_for_revision") == release_manifest["revision"]
        and unicode_control_hygiene.get("checked_bundle") == release_manifest["bundle"]
        and unicode_control_hygiene.get("publication_authorized") is False
        and unicode_summary.get("checks_failed") == 0
        and unicode_summary.get("finding_count") == 0
        and unicode_summary.get("bidi_control_count") == 0
        and unicode_summary.get("invisible_format_control_count") == 0
    )
    record(
        "unicode_control_hygiene_is_pass",
        unicode_hygiene_ok,
        f"unicode_hygiene_status={unicode_control_hygiene.get('status')} text_files={unicode_summary.get('text_surface_count')} codepoints={unicode_summary.get('codepoints_scanned')} findings={unicode_summary.get('finding_count')} bidi={unicode_summary.get('bidi_control_count')} invisible={unicode_summary.get('invisible_format_control_count')} failed={unicode_summary.get('checks_failed')}",
    )

    research_metadata_ok = research_metadata_integrity.get("status") == "pass" and research_metadata_integrity.get("generated_for_revision") == release_manifest["revision"] and research_metadata_integrity.get("summary", {}).get("checks_failed") == 0
    record(
        "research_metadata_integrity_is_pass",
        research_metadata_ok,
        f"research_metadata_status={research_metadata_integrity.get('status')} failed={research_metadata_integrity.get('summary', {}).get('checks_failed')} provenance_subjects={research_metadata_integrity.get('summary', {}).get('provenance_subject_count')}",
    )

    evidence_integrity_summary = evidence_pack_integrity.get("summary", {})
    evidence_integrity_ok = (
        evidence_pack_integrity.get("status") == "pass"
        and evidence_pack_integrity.get("generated_for_revision") == release_manifest["revision"]
        and evidence_pack_integrity.get("checked_bundle") == release_manifest["bundle"]
        and evidence_pack_integrity.get("publication_authorized") is False
        and evidence_integrity_summary.get("checks_failed") == 0
        and evidence_integrity_summary.get("attached_entry_count", 0) >= 1
    )
    record(
        "evidence_pack_integrity_is_pass_and_attached",
        evidence_integrity_ok,
        f"evidence_integrity_status={evidence_pack_integrity.get('status')} attached={evidence_integrity_summary.get('attached_entry_count')} failed={evidence_integrity_summary.get('checks_failed')}",
    )

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
    compile_witness_ok = (
        freeze_compile_witness.get("status") == "pass"
        and freeze_compile_witness.get("generated_for_revision") == release_manifest["revision"]
        and freeze_compile_witness.get("checked_bundle") == release_manifest["bundle"]
        and freeze_compile_witness.get("publication_authorized") is False
        and compile_summary.get("checks_failed") == 0
        and compile_summary.get("witness_present") is True
        and compile_summary.get("witness_current_revision") is True
        and compile_summary.get("source_bound") is True
        and (compile_gate_closed or compile_gate_refresh_pending or compile_gate_evidence_pending)
    )
    record(
        "freeze_compile_witness_is_pass_and_source_bound",
        compile_witness_ok,
        f"compile_witness_status={freeze_compile_witness.get('status')} gate={compile_gate_status} source={freeze_compile_witness.get('selected_source')} final_warnings={freeze_compile_witness.get('compile', {}).get('final_warning_count') if isinstance(freeze_compile_witness.get('compile'), dict) else None} deterministic={compile_summary.get('deterministic_compile_evidence')} failed={compile_summary.get('checks_failed')}",
    )

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
    record(
        "freeze_packet_integrity_is_pass_and_materialized",
        freeze_packet_ok,
        f"freeze_packet_status={freeze_packet_integrity.get('status')} materialized={freeze_packet_summary.get('materialized_entry_count')} unregistered={freeze_packet_summary.get('unregistered_packet_dir_count')} failed={freeze_packet_summary.get('checks_failed')}",
    )

    publication_boundary_summary = publication_boundary.get("summary", {})
    publication_boundary_ok = (
        publication_boundary.get("status") == "pass"
        and publication_boundary.get("generated_for_revision") == release_manifest["revision"]
        and publication_boundary.get("checked_bundle") == release_manifest["bundle"]
        and publication_boundary.get("publication_authorized") is False
        and publication_boundary_summary.get("checks_failed") == 0
        and publication_boundary_summary.get("legacy_public_head_count") == 5
        and publication_boundary_summary.get("new_post_policy_anonymity_head_count") == citation_heads.get("summary", {}).get("new_post_policy_anonymity_head_count", 0)
        and publication_boundary_summary.get("unknown_published_tex_count") == 0
    )
    record(
        "publication_boundary_audit_is_pass",
        publication_boundary_ok,
        f"publication_boundary_status={publication_boundary.get('status')} legacy={publication_boundary_summary.get('legacy_public_head_count')} new={publication_boundary_summary.get('new_post_policy_anonymity_head_count')} unknown_tex={publication_boundary_summary.get('unknown_published_tex_count')} failed={publication_boundary_summary.get('checks_failed')}",
    )

    readiness_summary = release_readiness_audit.get("summary", {})
    readiness_counts = readiness_summary.get("release_readiness_counts", {})
    readiness_state_counts = readiness_summary.get("state_counts", {})
    published_ready_total = queue_index["summary"]["published_ready"]
    candidate_total = queue_index["summary"]["candidate"]
    published_ready_items_ok = all(
        item.get("release_readiness") == "static_preflight_pass" and item.get("blocker_count") == 0
        for item in release_readiness_audit.get("items", [])
        if item.get("queue_state") == "published_ready"
    )
    candidate_items_ok = all(
        item.get("release_readiness") == "not_a_release_target" and item.get("blocker_count") == 0
        for item in release_readiness_audit.get("items", [])
        if item.get("queue_state") == "candidate"
    )
    release_readiness_ok = (
        release_readiness_audit.get("status") == "pass"
        and release_readiness_audit.get("generated_for_revision") == release_manifest["revision"]
        and release_readiness_audit.get("publication_authorized") is False
        and readiness_state_counts.get("published_ready") == published_ready_total
        and readiness_state_counts.get("candidate") == candidate_total
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
        and published_ready_items_ok
        and candidate_items_ok
    )
    record(
        "release_readiness_audit_is_pass_and_queue_bound",
        release_readiness_ok,
        f"readiness_status={release_readiness_audit.get('status')} published_ready_static_pass={readiness_counts.get('static_preflight_pass', 0)} candidate_not_target={readiness_counts.get('not_a_release_target', 0)} malformed={readiness_summary.get('malformed_bibliography_command_count')} source_hash_bound={readiness_summary.get('source_hash_bound_count')} source_hash_missing={readiness_summary.get('source_hash_missing_count')} source_hash_mismatch={readiness_summary.get('source_hash_mismatch_count')} publication_authorized={release_readiness_audit.get('publication_authorized')}",
    )

    queue_binding_summary = queue_note_source_binding.get("summary", {})
    queue_binding_ok = (
        queue_note_source_binding.get("status") == "pass"
        and queue_note_source_binding.get("generated_for_revision") == release_manifest["revision"]
        and queue_note_source_binding.get("checked_bundle") == release_manifest["bundle"]
        and queue_note_source_binding.get("publication_authorized") is False
        and queue_binding_summary.get("queue_note_count") == (published_ready_total + candidate_total + queue_index["summary"].get("hold", 0))
        and queue_binding_summary.get("queue_note_pass_count") == queue_binding_summary.get("queue_note_count")
        and queue_binding_summary.get("failure_count") == 0
        and queue_binding_summary.get("duplicate_source_binding_count") == 0
    )
    record(
        "queue_note_source_binding_is_pass",
        queue_binding_ok,
        f"queue_binding_status={queue_note_source_binding.get('status')} notes={queue_binding_summary.get('queue_note_count')} pass={queue_binding_summary.get('queue_note_pass_count')} failures={queue_binding_summary.get('failure_count')} duplicates={queue_binding_summary.get('duplicate_source_binding_count')}",
    )

    queue_compile_summary = queue_compile_smoke.get("summary", {})
    queue_compile_rows = queue_compile_smoke.get("results", []) if isinstance(queue_compile_smoke.get("results", []), list) else []
    queue_compile_result_by_path = {str(row.get("path", "")): row for row in queue_compile_rows if isinstance(row, dict)}
    queue_compile_expected_sources = {
        item.get("source_tex")
        for state in ("published_ready", "candidate")
        for item in queue_index.get("states", {}).get(state, [])
        if isinstance(item, dict) and item.get("source_tex")
    }
    queue_compile_hash_mismatches = []
    for source in sorted(queue_compile_expected_sources):
        source_path = root / source
        row = queue_compile_result_by_path.get(source)
        if row and source_path.exists() and row.get("source_sha256") != sha256_file(source_path):
            queue_compile_hash_mismatches.append(source)
    queue_compile_final_warning_paths = [
        source
        for source, row in sorted(queue_compile_result_by_path.items())
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0))
    ]
    queue_compile_short_pass_paths = [
        source
        for source, row in sorted(queue_compile_result_by_path.items())
        if int(row.get("passes_completed", 0)) < 3
    ]
    queue_compile_digest_missing_paths = [
        source
        for source, row in sorted(queue_compile_result_by_path.items())
        if compile_digest_receipt_missing(row)
    ]
    queue_compile_digest_summary_ok = (
        queue_compile_summary.get("pdf_output_created_count") == len(queue_compile_expected_sources)
        and queue_compile_summary.get("digest_receipt_count") == len(queue_compile_expected_sources)
        and int(queue_compile_summary.get("digest_receipt_missing_count", -1)) == 0
    )
    queue_compile_reproducible_missing_paths = [
        source
        for source, row in sorted(queue_compile_result_by_path.items())
        if compile_reproducible_receipt_missing(row)
    ]
    queue_compile_reproducible_summary_ok = (
        queue_compile_summary.get("reproducible_receipt_count") == len(queue_compile_expected_sources)
        and int(queue_compile_summary.get("reproducible_receipt_missing_count", -1)) == 0
        and queue_compile_summary.get("reproducible_receipts_required") is True
        and queue_compile_summary.get("compile_receipt_policy") == COMPILE_RECEIPT_POLICY_V2
        and str(queue_compile_summary.get("source_date_epoch", "")) == "1700000000"
        and queue_compile_summary.get("pdf_normalization_policy") == "normalize-pdftex-trailer-id-and-dates-v1"
        and queue_compile_summary.get("log_normalization_policy") == "normalize-volatile-compile-paths-v1"
    )
    queue_compile_ok = (
        queue_compile_smoke.get("status") == "pass"
        and queue_compile_smoke.get("generated_for_revision") == release_manifest["revision"]
        and queue_compile_smoke.get("checked_bundle") == release_manifest["bundle"]
        and queue_compile_smoke.get("publication_authorized") is False
        and queue_compile_summary.get("targets_failed") == 0
        and queue_compile_summary.get("targets_checked") == len(queue_compile_expected_sources)
        and set(queue_compile_result_by_path) == queue_compile_expected_sources
        and not queue_compile_hash_mismatches
        and queue_compile_summary.get("toolchain_available") is True
        and int(queue_compile_summary.get("passes_requested_per_target", 0)) >= 3
        and int(queue_compile_summary.get("final_unresolved_warning_hits_total", 0)) == 0
        and int(queue_compile_summary.get("final_rerun_warning_hits_total", 0)) == 0
        and not queue_compile_short_pass_paths
        and not queue_compile_final_warning_paths
        and not queue_compile_digest_missing_paths
        and queue_compile_digest_summary_ok
        and not queue_compile_reproducible_missing_paths
        and queue_compile_reproducible_summary_ok
    )
    record(
        "queue_compile_smoke_is_pass_and_source_current",
        queue_compile_ok,
        f"queue_compile_status={queue_compile_smoke.get('status')} checked={queue_compile_summary.get('targets_checked')} failed={queue_compile_summary.get('targets_failed')} passes={queue_compile_summary.get('passes_requested_per_target')} final_unresolved={queue_compile_summary.get('final_unresolved_warning_hits_total')} final_rerun={queue_compile_summary.get('final_rerun_warning_hits_total')} short_passes={len(queue_compile_short_pass_paths)} hash_mismatches={len(queue_compile_hash_mismatches)} digest_missing={len(queue_compile_digest_missing_paths)} digest_summary_ok={queue_compile_digest_summary_ok} reproducible_missing={len(queue_compile_reproducible_missing_paths)} reproducible_summary_ok={queue_compile_reproducible_summary_ok} toolchain_available={queue_compile_summary.get('toolchain_available')}",
    )

    hold_compile_summary = hold_compile_triage.get("summary", {}) if isinstance(hold_compile_triage.get("summary", {}), dict) else {}
    hold_compile_rows = hold_compile_triage.get("results", []) if isinstance(hold_compile_triage.get("results", []), list) else []
    hold_compile_result_by_path = {str(row.get("path", "")): row for row in hold_compile_rows if isinstance(row, dict)}
    hold_expected_items = [
        item for item in queue_index.get("states", {}).get("hold", [])
        if isinstance(item, dict) and item.get("source_tex")
    ]
    hold_expected_sources = {str(item.get("source_tex")) for item in hold_expected_items}
    hold_expected_notes = {str(item.get("source_tex")): str(item.get("path", "")) for item in hold_expected_items}
    hold_expected_order = {str(item.get("source_tex")): idx for idx, item in enumerate(hold_expected_items, 1)}
    hold_hash_mismatches = []
    hold_state_mismatches = []
    hold_queue_note_mismatches = []
    hold_queue_order_mismatches = []
    for source in sorted(hold_expected_sources):
        source_path = root / source
        row = hold_compile_result_by_path.get(source)
        if row and source_path.exists() and row.get("source_sha256") != sha256_file(source_path):
            hold_hash_mismatches.append(source)
        if row and row.get("state") != "hold":
            hold_state_mismatches.append(source)
        if row and row.get("queue_note") != hold_expected_notes.get(source):
            hold_queue_note_mismatches.append(source)
        if row:
            try:
                actual_order = int(row.get("queue_order_index", row.get("index", -1)))
            except (TypeError, ValueError):
                actual_order = -1
            if actual_order != hold_expected_order.get(source):
                hold_queue_order_mismatches.append(source)
    hold_compile_final_warning_paths = [
        source
        for source, row in sorted(hold_compile_result_by_path.items())
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0))
    ]
    hold_compile_short_pass_paths = [
        source
        for source, row in sorted(hold_compile_result_by_path.items())
        if int(row.get("passes_completed", 0)) < 3
    ]
    hold_digest_missing_paths = [
        source
        for source, row in sorted(hold_compile_result_by_path.items())
        if compile_digest_receipt_missing(row)
    ]
    hold_digest_summary_ok = (
        hold_compile_summary.get("pdf_output_created_count") == len(hold_expected_sources)
        and hold_compile_summary.get("digest_receipt_count") == len(hold_expected_sources)
        and int(hold_compile_summary.get("digest_receipt_missing_count", -1)) == 0
    )
    hold_reproducible_missing_paths = [
        source
        for source, row in sorted(hold_compile_result_by_path.items())
        if compile_reproducible_receipt_missing(row)
    ]
    hold_reproducible_summary_ok = (
        hold_compile_summary.get("reproducible_receipt_count") == len(hold_expected_sources)
        and int(hold_compile_summary.get("reproducible_receipt_missing_count", -1)) == 0
        and hold_compile_summary.get("reproducible_receipts_required") is True
        and hold_compile_summary.get("compile_receipt_policy") == COMPILE_RECEIPT_POLICY_V2
        and str(hold_compile_summary.get("source_date_epoch", "")) == "1700000000"
        and hold_compile_summary.get("pdf_normalization_policy") == "normalize-pdftex-trailer-id-and-dates-v1"
        and hold_compile_summary.get("log_normalization_policy") == "normalize-volatile-compile-paths-v1"
    )
    hold_toolchain = hold_compile_triage.get("toolchain", {}) if isinstance(hold_compile_triage.get("toolchain", {}), dict) else {}
    hold_toolchain_available = hold_compile_summary.get("toolchain_available", hold_toolchain.get("toolchain_available"))
    hold_scope = hold_compile_triage.get("scope", {}) if isinstance(hold_compile_triage.get("scope", {}), dict) else {}
    hold_state_counts = hold_compile_summary.get("state_counts", {}) if isinstance(hold_compile_summary.get("state_counts", {}), dict) else {}
    hold_state_count = hold_state_counts.get("hold", {}) if isinstance(hold_state_counts.get("hold", {}), dict) else {}
    hold_compile_ok = (
        hold_compile_triage.get("status") == "pass"
        and hold_compile_triage.get("generated_for_revision") == release_manifest["revision"]
        and hold_compile_triage.get("checked_bundle") == release_manifest["bundle"]
        and hold_compile_triage.get("publication_authorized") is False
        and (hold_scope.get("states") == ["hold"] or hold_scope.get("checked_states") == ["hold"])
        and hold_compile_summary.get("targets_failed") == 0
        and hold_compile_summary.get("targets_checked") == len(hold_expected_sources)
        and hold_compile_summary.get("targets_passed") == len(hold_expected_sources)
        and hold_state_count.get("expected", len(hold_expected_sources)) == len(hold_expected_sources)
        and hold_state_count.get("passed", len(hold_expected_sources)) == len(hold_expected_sources)
        and set(hold_compile_result_by_path) == hold_expected_sources
        and not hold_hash_mismatches
        and not hold_state_mismatches
        and not hold_queue_note_mismatches
        and not hold_queue_order_mismatches
        and hold_toolchain_available is True
        and "-no-shell-escape" in str(hold_compile_triage.get("command_family", ""))
        and int(hold_compile_summary.get("passes_requested_per_target", 0)) >= 3
        and int(hold_compile_summary.get("minimum_required_passes", 0)) >= 3
        and int(hold_compile_summary.get("final_unresolved_warning_hits_total", 0)) == 0
        and int(hold_compile_summary.get("final_rerun_warning_hits_total", 0)) == 0
        and not hold_compile_short_pass_paths
        and not hold_compile_final_warning_paths
        and not hold_digest_missing_paths
        and hold_digest_summary_ok
        and not hold_reproducible_missing_paths
        and hold_reproducible_summary_ok
    )
    record(
        "hold_compile_triage_is_pass_and_source_current",
        hold_compile_ok,
        f"hold_compile_status={hold_compile_triage.get('status')} checked={hold_compile_summary.get('targets_checked')} failed={hold_compile_summary.get('targets_failed')} passes={hold_compile_summary.get('passes_requested_per_target')} final_unresolved={hold_compile_summary.get('final_unresolved_warning_hits_total')} final_rerun={hold_compile_summary.get('final_rerun_warning_hits_total')} short_passes={len(hold_compile_short_pass_paths)} hash_mismatches={len(hold_hash_mismatches)} state_mismatches={len(hold_state_mismatches)} queue_note_mismatches={len(hold_queue_note_mismatches)} queue_order_mismatches={len(hold_queue_order_mismatches)} digest_missing={len(hold_digest_missing_paths)} digest_summary_ok={hold_digest_summary_ok} reproducible_missing={len(hold_reproducible_missing_paths)} reproducible_summary_ok={hold_reproducible_summary_ok} toolchain_available={hold_toolchain_available}",
    )

    unqueued_summary = unqueued_compile_triage.get("summary", {}) if isinstance(unqueued_compile_triage.get("summary", {}), dict) else {}
    unqueued_rows = unqueued_compile_triage.get("results", []) if isinstance(unqueued_compile_triage.get("results", []), list) else []
    unqueued_result_by_path = {str(row.get("path", "")): row for row in unqueued_rows if isinstance(row, dict)}
    queued_sources_all = {
        str(item.get("source_tex"))
        for rows in queue_index.get("states", {}).values()
        for item in rows
        if isinstance(item, dict) and item.get("source_tex")
    }
    unqueued_expected_sources = [
        path.relative_to(root).as_posix()
        for path in sorted(root.glob("series/**/paper.tex"))
        if path.relative_to(root).as_posix() not in queued_sources_all
    ]
    unqueued_hash_mismatches = []
    for source in unqueued_expected_sources:
        row = unqueued_result_by_path.get(source)
        if row and (root / source).exists() and row.get("source_sha256") != sha256_file(root / source):
            unqueued_hash_mismatches.append(source)
    unqueued_short_pass_paths = [
        source
        for source, row in sorted(unqueued_result_by_path.items())
        if int(row.get("passes_completed", 0)) < 3
    ]
    unqueued_final_warning_paths = [
        source
        for source, row in sorted(unqueued_result_by_path.items())
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0))
    ]
    unqueued_digest_missing_paths = [
        source
        for source, row in sorted(unqueued_result_by_path.items())
        if compile_digest_receipt_missing(row)
    ]
    unqueued_digest_summary_ok = (
        unqueued_summary.get("pdf_output_created_count") == len(unqueued_expected_sources)
        and unqueued_summary.get("digest_receipt_count") == len(unqueued_expected_sources)
        and int(unqueued_summary.get("digest_receipt_missing_count", -1)) == 0
    )
    unqueued_reproducible_missing_paths = [
        source
        for source, row in sorted(unqueued_result_by_path.items())
        if compile_reproducible_receipt_missing(row)
    ]
    unqueued_reproducible_summary_ok = (
        unqueued_summary.get("reproducible_receipt_count") == len(unqueued_expected_sources)
        and int(unqueued_summary.get("reproducible_receipt_missing_count", -1)) == 0
        and unqueued_summary.get("reproducible_receipts_required") is True
        and unqueued_summary.get("compile_receipt_policy") == COMPILE_RECEIPT_POLICY_V2
        and str(unqueued_summary.get("source_date_epoch", "")) == "1700000000"
        and unqueued_summary.get("pdf_normalization_policy") == "normalize-pdftex-trailer-id-and-dates-v1"
        and unqueued_summary.get("log_normalization_policy") == "normalize-volatile-compile-paths-v1"
    )
    unqueued_toolchain = unqueued_compile_triage.get("toolchain", {}) if isinstance(unqueued_compile_triage.get("toolchain", {}), dict) else {}
    unqueued_compile_ok = (
        unqueued_compile_triage.get("status") == "pass"
        and unqueued_compile_triage.get("generated_for_revision") == release_manifest["revision"]
        and unqueued_compile_triage.get("checked_bundle") == release_manifest["bundle"]
        and unqueued_compile_triage.get("publication_authorized") is False
        and unqueued_compile_triage.get("partial") is False
        and unqueued_summary.get("targets_failed") == 0
        and unqueued_summary.get("targets_checked") == len(unqueued_expected_sources)
        and unqueued_summary.get("targets_passed") == len(unqueued_expected_sources)
        and list(unqueued_result_by_path) == unqueued_expected_sources
        and not unqueued_hash_mismatches
        and unqueued_toolchain.get("toolchain_available") is True
        and "-no-shell-escape" in str(unqueued_compile_triage.get("command_family", ""))
        and int(unqueued_summary.get("passes_requested_per_target", 0)) >= 3
        and int(unqueued_summary.get("final_unresolved_warning_hits_total", 0)) == 0
        and int(unqueued_summary.get("final_rerun_warning_hits_total", 0)) == 0
        and not unqueued_short_pass_paths
        and not unqueued_final_warning_paths
        and not unqueued_digest_missing_paths
        and unqueued_digest_summary_ok
        and not unqueued_reproducible_missing_paths
        and unqueued_reproducible_summary_ok
    )
    record(
        "unqueued_compile_triage_is_pass_and_source_current",
        unqueued_compile_ok,
        f"unqueued_compile_status={unqueued_compile_triage.get('status')} checked={unqueued_summary.get('targets_checked')} failed={unqueued_summary.get('targets_failed')} passes={unqueued_summary.get('passes_requested_per_target')} final_unresolved={unqueued_summary.get('final_unresolved_warning_hits_total')} final_rerun={unqueued_summary.get('final_rerun_warning_hits_total')} short_passes={len(unqueued_short_pass_paths)} hash_mismatches={len(unqueued_hash_mismatches)} digest_missing={len(unqueued_digest_missing_paths)} digest_summary_ok={unqueued_digest_summary_ok} reproducible_missing={len(unqueued_reproducible_missing_paths)} reproducible_summary_ok={unqueued_reproducible_summary_ok} toolchain_available={unqueued_toolchain.get('toolchain_available')}",
    )

    unqueued_inventory_counts, unqueued_inventory_paths = parse_unqueued_inventory(unqueued_inventory_text)
    all_series_sources = sorted(path.relative_to(root).as_posix() for path in root.glob("series/**/paper.tex"))
    queued_sources_for_inventory = sorted(queued_sources_all)
    expected_unqueued_sources_for_inventory = sorted(source for source in all_series_sources if source not in set(queued_sources_for_inventory))
    unqueued_inventory_ok = (
        unqueued_inventory_path.exists()
        and unqueued_inventory_counts.get("queued") == len(queued_sources_for_inventory)
        and unqueued_inventory_counts.get("series") == len(all_series_sources)
        and unqueued_inventory_counts.get("unqueued") == len(expected_unqueued_sources_for_inventory)
        and sorted(unqueued_inventory_paths) == expected_unqueued_sources_for_inventory
        and "not a publication authorization" in unqueued_inventory_text.lower()
        and "outside Candidate / Published-ready / Hold queue-note coverage" in unqueued_inventory_text
    )
    record(
        "unqueued_source_inventory_matches_series_minus_queue",
        unqueued_inventory_ok,
        f"inventory_exists={unqueued_inventory_path.exists()} queued_count={unqueued_inventory_counts.get('queued')} expected_queued={len(queued_sources_for_inventory)} series_count={unqueued_inventory_counts.get('series')} expected_series={len(all_series_sources)} unqueued_count={unqueued_inventory_counts.get('unqueued')} expected_unqueued={len(expected_unqueued_sources_for_inventory)} path_count={len(unqueued_inventory_paths)}",
    )

    release_compile_paths = [str(row.get("path", "")) for row in queue_compile_rows if isinstance(row, dict)]
    hold_compile_paths = [str(row.get("path", "")) for row in hold_compile_rows if isinstance(row, dict)]
    unqueued_compile_paths = [str(row.get("path", "")) for row in unqueued_rows if isinstance(row, dict)]
    compile_partition_union = sorted(set(release_compile_paths) | set(hold_compile_paths) | set(unqueued_compile_paths))
    compile_partition_overlaps = {
        "release_hold": sorted(set(release_compile_paths) & set(hold_compile_paths)),
        "release_unqueued": sorted(set(release_compile_paths) & set(unqueued_compile_paths)),
        "hold_unqueued": sorted(set(hold_compile_paths) & set(unqueued_compile_paths)),
    }
    compile_partition_duplicates = {
        "release": sorted({path for path in release_compile_paths if release_compile_paths.count(path) > 1}),
        "hold": sorted({path for path in hold_compile_paths if hold_compile_paths.count(path) > 1}),
        "unqueued": sorted({path for path in unqueued_compile_paths if unqueued_compile_paths.count(path) > 1}),
    }
    published_source_tex_paths = set()
    for receipt_path in sorted((root / "published").glob("*/PUBLICATION_RECEIPT.json")):
        try:
            receipt = load_json(receipt_path)
        except Exception:
            continue
        source_tex = str(receipt.get("source_tex", ""))
        if source_tex.startswith("series/") and source_tex.endswith("/paper.tex"):
            published_source_tex_paths.add(source_tex)
    unpublished_series_sources = sorted(path for path in all_series_sources if path not in published_source_tex_paths)
    compile_partition_ok = (
        compile_partition_union == unpublished_series_sources
        and not any(compile_partition_overlaps.values())
        and not any(compile_partition_duplicates.values())
    )
    record(
        "all_series_compile_evidence_partition_is_complete",
        compile_partition_ok,
        f"unpublished_series_sources={len(unpublished_series_sources)} published_series_sources={len(published_source_tex_paths)} release_compile={len(release_compile_paths)} hold_compile={len(hold_compile_paths)} unqueued_compile={len(unqueued_compile_paths)} union={len(compile_partition_union)} overlaps={sum(len(v) for v in compile_partition_overlaps.values())} duplicate_rows={sum(len(v) for v in compile_partition_duplicates.values())}",
    )

    typography_rows = [
        row
        for row in [*queue_compile_rows, *hold_compile_rows, *unqueued_rows]
        if isinstance(row, dict)
    ]
    typography_overfull_threshold = 300
    typography_underfull_threshold = 300
    typography_overfull_alerts = sorted(
        str(row.get("path", ""))
        for row in typography_rows
        if int(row.get("overfull_hbox", 0)) > typography_overfull_threshold
    )
    typography_underfull_alerts = sorted(
        str(row.get("path", ""))
        for row in typography_rows
        if int(row.get("underfull_hbox", 0)) > typography_underfull_threshold
    )
    record(
        "compile_typography_debt_below_alert_threshold",
        not typography_overfull_alerts and not typography_underfull_alerts,
        f"rows={len(typography_rows)} overfull_threshold={typography_overfull_threshold} overfull_alerts={len(typography_overfull_alerts)} underfull_threshold={typography_underfull_threshold} underfull_alerts={len(typography_underfull_alerts)} max_overfull={max([int(row.get('overfull_hbox', 0)) for row in typography_rows] or [0])} max_underfull={max([int(row.get('underfull_hbox', 0)) for row in typography_rows] or [0])}",
    )

    release_typography_rows = [row for row in queue_compile_rows if isinstance(row, dict)]
    release_typography_overfull_threshold = 50
    release_typography_underfull_threshold = 60
    release_typography_overfull_alerts = sorted(
        str(row.get("path", ""))
        for row in release_typography_rows
        if int(row.get("overfull_hbox", 0)) > release_typography_overfull_threshold
    )
    release_typography_underfull_alerts = sorted(
        str(row.get("path", ""))
        for row in release_typography_rows
        if int(row.get("underfull_hbox", 0)) > release_typography_underfull_threshold
    )
    record(
        "release_lane_typography_debt_below_tight_threshold",
        not release_typography_overfull_alerts and not release_typography_underfull_alerts,
        f"rows={len(release_typography_rows)} overfull_threshold={release_typography_overfull_threshold} overfull_alerts={len(release_typography_overfull_alerts)} underfull_threshold={release_typography_underfull_threshold} underfull_alerts={len(release_typography_underfull_alerts)} max_overfull={max([int(row.get('overfull_hbox', 0)) for row in release_typography_rows] or [0])} max_underfull={max([int(row.get('underfull_hbox', 0)) for row in release_typography_rows] or [0])}",
    )


    def md_has_compile_summary(md_text: str, report: dict, checked_label: str) -> bool:
        summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
        fragments = [
            f"Generated for revision: `{report.get('generated_for_revision')}`",
            f"Checked bundle: `{report.get('checked_bundle')}`",
            "Publication authorized: false",
            f"- Status: **{report.get('status')}**",
            checked_label,
            f"- Passed: {summary.get('targets_passed')}",
            f"- Failed: {summary.get('targets_failed')}",
        ]
        if "final_unresolved_warning_hits_total" in summary:
            fragments.append(str(summary.get("final_unresolved_warning_hits_total")))
        if "final_rerun_warning_hits_total" in summary:
            fragments.append(str(summary.get("final_rerun_warning_hits_total")))
        return bool(md_text) and all(fragment in md_text for fragment in fragments)

    hold_md_ok = md_has_compile_summary(
        hold_compile_md_text,
        hold_compile_triage,
        f"- Hold targets checked: {hold_compile_summary.get('targets_checked')} / {hold_compile_summary.get('targets_expected') or hold_compile_summary.get('targets_checked')}",
    ) and "does not move any Hold item" in hold_compile_md_text
    record(
        "hold_compile_triage_markdown_matches_json",
        hold_md_ok,
        f"md_exists={hold_compile_md_path.exists()} json_revision={hold_compile_triage.get('generated_for_revision')} md_has_revision={hold_compile_triage.get('generated_for_revision') in hold_compile_md_text} checked={hold_compile_summary.get('targets_checked')} passed={hold_compile_summary.get('targets_passed')}",
    )

    unqueued_md_ok = md_has_compile_summary(
        unqueued_compile_md_text,
        unqueued_compile_triage,
        f"- Targets checked: {unqueued_summary.get('targets_checked')} / {unqueued_summary.get('target_count_total')}",
    ) and "does not promote any source" in unqueued_compile_md_text
    record(
        "unqueued_compile_triage_markdown_matches_json",
        unqueued_md_ok,
        f"md_exists={unqueued_compile_md_path.exists()} json_revision={unqueued_compile_triage.get('generated_for_revision')} md_has_revision={unqueued_compile_triage.get('generated_for_revision') in unqueued_compile_md_text} checked={unqueued_summary.get('targets_checked')} passed={unqueued_summary.get('targets_passed')}",
    )

    published_expected_rows: list[dict] = []
    published_seen: set[str] = set()
    for item in publication_classification.get("legacy_canonical_public_wiki_targets", []):
        if isinstance(item, dict) and item.get("path") and str(item.get("path")) not in published_seen:
            published_seen.add(str(item.get("path")))
            published_expected_rows.append({"path": str(item.get("path")), "role": "legacy_canonical_public_head"})
    for item in publication_classification.get("repo_frozen_noncanonical_entries", []):
        if isinstance(item, dict) and item.get("path") and str(item.get("path")) not in published_seen:
            published_seen.add(str(item.get("path")))
            published_expected_rows.append({"path": str(item.get("path")), "role": "repo_frozen_noncanonical_entry"})
    for item in publication_classification.get("new_post_policy_anonymity_entries", []):
        if isinstance(item, dict) and item.get("path") and str(item.get("path")) not in published_seen:
            published_seen.add(str(item.get("path")))
            published_expected_rows.append({"path": str(item.get("path")), "role": "new_post_policy_anonymity_entry"})
    published_expected_paths = [row["path"] for row in published_expected_rows]
    actual_published_tex_paths = sorted(path.relative_to(root).as_posix() for path in root.glob("published/**/paper.tex"))
    published_rows = published_compile_triage.get("results", []) if isinstance(published_compile_triage.get("results", []), list) else []
    published_result_by_path = {str(row.get("path", "")): row for row in published_rows if isinstance(row, dict)}
    published_row_paths = [str(row.get("path", "")) for row in published_rows if isinstance(row, dict)]
    published_duplicate_rows = sorted({path for path in published_row_paths if published_row_paths.count(path) > 1})
    published_hash_mismatches = []
    published_role_mismatches = []
    published_index_mismatches = []
    published_pdf_missing = []
    published_digest_missing = []
    published_reproducible_missing = []
    published_nonpass = []
    published_short_passes = []
    published_final_warning_paths = []
    published_fatal_paths = []
    published_expected_roles = {row["path"]: row["role"] for row in published_expected_rows}
    for index, path in enumerate(published_expected_paths, 1):
        row = published_result_by_path.get(path)
        source_path = root / path
        if not row:
            continue
        if source_path.exists() and row.get("source_sha256") != sha256_file(source_path):
            published_hash_mismatches.append(path)
        if row.get("role") != published_expected_roles.get(path):
            published_role_mismatches.append(path)
        try:
            actual_index = int(row.get("index", -1))
        except (TypeError, ValueError):
            actual_index = -1
        if actual_index != index:
            published_index_mismatches.append(path)
        if row.get("status") != "pass":
            published_nonpass.append(path)
        if int(row.get("passes_completed", 0)) < 3:
            published_short_passes.append(path)
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0)):
            published_final_warning_paths.append(path)
        if int(row.get("fatal_pattern_hits", 0)):
            published_fatal_paths.append(path)
        if row.get("pdf_output_created") is not True or int(row.get("pdf_output_bytes", 0) or 0) <= 0:
            published_pdf_missing.append(path)
        if compile_digest_receipt_missing(row):
            published_digest_missing.append(path)
        if compile_reproducible_receipt_missing(row):
            published_reproducible_missing.append(path)
    published_summary = published_compile_triage.get("summary", {}) if isinstance(published_compile_triage.get("summary", {}), dict) else {}
    published_toolchain = published_compile_triage.get("toolchain", {}) if isinstance(published_compile_triage.get("toolchain", {}), dict) else {}
    published_reproducible_summary_ok = (
        published_summary.get("reproducible_receipt_count") == len(published_expected_paths)
        and int(published_summary.get("reproducible_receipt_missing_count", -1)) == 0
        and published_summary.get("reproducible_receipts_required") is True
        and published_summary.get("compile_receipt_policy") == COMPILE_RECEIPT_POLICY_V2
        and str(published_summary.get("source_date_epoch", "")) == "1700000000"
        and published_summary.get("pdf_normalization_policy") == "normalize-pdftex-trailer-id-and-dates-v1"
        and published_summary.get("log_normalization_policy") == "normalize-volatile-compile-paths-v1"
    )
    published_scope_ok = (
        sorted(published_expected_paths) == actual_published_tex_paths
        and published_row_paths == published_expected_paths
        and not published_duplicate_rows
    )
    record(
        "published_compile_triage_scope_matches_classified_published_tex",
        published_scope_ok,
        f"classified={len(published_expected_paths)} actual_published_tex={len(actual_published_tex_paths)} stored_rows={len(published_row_paths)} duplicates={len(published_duplicate_rows)}",
    )
    published_compile_ok = (
        published_compile_triage.get("status") == "pass"
        and published_compile_triage.get("generated_for_revision") == release_manifest["revision"]
        and published_compile_triage.get("checked_bundle") == release_manifest["bundle"]
        and published_compile_triage.get("publication_authorized") is False
        and published_compile_triage.get("partial") is False
        and published_summary.get("targets_failed") == 0
        and published_summary.get("targets_checked") == len(published_expected_paths)
        and published_summary.get("targets_passed") == len(published_expected_paths)
        and published_summary.get("pdf_output_created_count") == len(published_expected_paths)
        and published_toolchain.get("toolchain_available") is True
        and "-no-shell-escape" in str(published_compile_triage.get("command_family", ""))
        and int(published_summary.get("passes_requested_per_target", 0)) >= 3
        and int(published_summary.get("minimum_required_passes", 0)) >= 3
        and int(published_summary.get("final_unresolved_warning_hits_total", 0)) == 0
        and int(published_summary.get("final_rerun_warning_hits_total", 0)) == 0
        and not published_hash_mismatches
        and not published_nonpass
        and not published_short_passes
        and not published_final_warning_paths
        and not published_fatal_paths
        and not published_role_mismatches
        and not published_index_mismatches
        and not published_pdf_missing
        and not published_digest_missing
        and not published_reproducible_missing
        and published_reproducible_summary_ok
    )
    record(
        "published_compile_triage_is_pass_source_current_pdf_backed",
        published_compile_ok,
        f"published_compile_status={published_compile_triage.get('status')} checked={published_summary.get('targets_checked')} failed={published_summary.get('targets_failed')} passes={published_summary.get('passes_requested_per_target')} final_unresolved={published_summary.get('final_unresolved_warning_hits_total')} final_rerun={published_summary.get('final_rerun_warning_hits_total')} pdf_missing={len(published_pdf_missing)} digest_missing={len(published_digest_missing)} reproducible_missing={len(published_reproducible_missing)} reproducible_summary_ok={published_reproducible_summary_ok} hash_mismatches={len(published_hash_mismatches)} role_mismatches={len(published_role_mismatches)} index_mismatches={len(published_index_mismatches)} toolchain_available={published_toolchain.get('toolchain_available')}",
    )
    published_md_ok = md_has_compile_summary(
        published_compile_md_text,
        published_compile_triage,
        f"- Targets checked: {published_summary.get('targets_checked')} / {published_summary.get('target_count_total')}",
    ) and "does not authorize a new publication" in published_compile_md_text
    record(
        "published_compile_triage_markdown_matches_json",
        published_md_ok,
        f"md_exists={published_compile_md_path.exists()} json_revision={published_compile_triage.get('generated_for_revision')} md_has_revision={published_compile_triage.get('generated_for_revision') in published_compile_md_text} checked={published_summary.get('targets_checked')} passed={published_summary.get('targets_passed')}",
    )


    auxiliary_expected_paths = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*.tex")
        if not (path.relative_to(root).as_posix().startswith("series/") and path.relative_to(root).as_posix().endswith("/paper.tex"))
        and not (path.relative_to(root).as_posix().startswith("published/") and path.relative_to(root).as_posix().endswith("/paper.tex"))
    )
    auxiliary_expected_roles = {}
    for path in auxiliary_expected_paths:
        if path == "index/SERIES_INDEX.tex":
            auxiliary_expected_roles[path] = "series_index_auxiliary_source"
        elif path.startswith("release_queue/freeze_packets/") and path.endswith("/FROZEN_SOURCE.tex"):
            auxiliary_expected_roles[path] = "freeze_packet_frozen_source_copy"
        else:
            auxiliary_expected_roles[path] = "auxiliary_nonpaper_tex_source"
    auxiliary_rows = auxiliary_tex_compile_triage.get("results", []) if isinstance(auxiliary_tex_compile_triage.get("results", []), list) else []
    auxiliary_row_paths = [str(row.get("path", "")) for row in auxiliary_rows if isinstance(row, dict)]
    auxiliary_result_by_path = {str(row.get("path", "")): row for row in auxiliary_rows if isinstance(row, dict)}
    auxiliary_duplicate_rows = sorted({path for path in auxiliary_row_paths if auxiliary_row_paths.count(path) > 1})
    auxiliary_hash_mismatches = []
    auxiliary_role_mismatches = []
    auxiliary_index_mismatches = []
    auxiliary_pdf_missing = []
    auxiliary_digest_missing = []
    auxiliary_reproducible_missing = []
    auxiliary_nonpass = []
    auxiliary_short_passes = []
    auxiliary_final_warning_paths = []
    auxiliary_fatal_paths = []
    for index, path in enumerate(auxiliary_expected_paths, 1):
        row = auxiliary_result_by_path.get(path)
        source_path = root / path
        if not row:
            continue
        if source_path.exists() and row.get("source_sha256") != sha256_file(source_path):
            auxiliary_hash_mismatches.append(path)
        if row.get("role") != auxiliary_expected_roles.get(path):
            auxiliary_role_mismatches.append(path)
        try:
            actual_index = int(row.get("index", -1))
        except (TypeError, ValueError):
            actual_index = -1
        if actual_index != index:
            auxiliary_index_mismatches.append(path)
        if row.get("status") != "pass":
            auxiliary_nonpass.append(path)
        if int(row.get("passes_completed", 0)) < 3:
            auxiliary_short_passes.append(path)
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0)):
            auxiliary_final_warning_paths.append(path)
        if int(row.get("fatal_pattern_hits", 0)):
            auxiliary_fatal_paths.append(path)
        if row.get("pdf_output_created") is not True or int(row.get("pdf_output_bytes", 0) or 0) <= 0:
            auxiliary_pdf_missing.append(path)
        if compile_digest_receipt_missing(row):
            auxiliary_digest_missing.append(path)
        if compile_reproducible_receipt_missing(row):
            auxiliary_reproducible_missing.append(path)
    auxiliary_summary = auxiliary_tex_compile_triage.get("summary", {}) if isinstance(auxiliary_tex_compile_triage.get("summary", {}), dict) else {}
    auxiliary_toolchain = auxiliary_tex_compile_triage.get("toolchain", {}) if isinstance(auxiliary_tex_compile_triage.get("toolchain", {}), dict) else {}
    auxiliary_reproducible_summary_ok = (
        auxiliary_summary.get("reproducible_receipt_count") == len(auxiliary_expected_paths)
        and int(auxiliary_summary.get("reproducible_receipt_missing_count", -1)) == 0
        and auxiliary_summary.get("reproducible_receipts_required") is True
        and auxiliary_summary.get("compile_receipt_policy") == COMPILE_RECEIPT_POLICY_V2
        and str(auxiliary_summary.get("source_date_epoch", "")) == "1700000000"
        and auxiliary_summary.get("pdf_normalization_policy") == "normalize-pdftex-trailer-id-and-dates-v1"
        and auxiliary_summary.get("log_normalization_policy") == "normalize-volatile-compile-paths-v1"
    )
    auxiliary_compile_ok = (
        auxiliary_tex_compile_triage.get("status") == "pass"
        and auxiliary_tex_compile_triage.get("generated_for_revision") == release_manifest["revision"]
        and auxiliary_tex_compile_triage.get("checked_bundle") == release_manifest["bundle"]
        and auxiliary_tex_compile_triage.get("publication_authorized") is False
        and auxiliary_tex_compile_triage.get("partial") is False
        and auxiliary_summary.get("targets_failed") == 0
        and auxiliary_summary.get("targets_checked") == len(auxiliary_expected_paths)
        and auxiliary_summary.get("targets_passed") == len(auxiliary_expected_paths)
        and auxiliary_summary.get("pdf_output_created_count") == len(auxiliary_expected_paths)
        and auxiliary_row_paths == auxiliary_expected_paths
        and not auxiliary_duplicate_rows
        and auxiliary_toolchain.get("toolchain_available") is True
        and "-no-shell-escape" in str(auxiliary_tex_compile_triage.get("command_family", ""))
        and int(auxiliary_summary.get("passes_requested_per_target", 0)) >= 3
        and int(auxiliary_summary.get("minimum_required_passes", 0)) >= 3
        and int(auxiliary_summary.get("final_unresolved_warning_hits_total", 0)) == 0
        and int(auxiliary_summary.get("final_rerun_warning_hits_total", 0)) == 0
        and not auxiliary_hash_mismatches
        and not auxiliary_nonpass
        and not auxiliary_short_passes
        and not auxiliary_final_warning_paths
        and not auxiliary_fatal_paths
        and not auxiliary_role_mismatches
        and not auxiliary_index_mismatches
        and not auxiliary_pdf_missing
        and not auxiliary_digest_missing
        and not auxiliary_reproducible_missing
        and auxiliary_reproducible_summary_ok
    )
    record(
        "auxiliary_tex_compile_triage_is_complete_source_current_pdf_backed",
        auxiliary_compile_ok,
        f"auxiliary_status={auxiliary_tex_compile_triage.get('status')} expected={len(auxiliary_expected_paths)} checked={auxiliary_summary.get('targets_checked')} failed={auxiliary_summary.get('targets_failed')} final_unresolved={auxiliary_summary.get('final_unresolved_warning_hits_total')} final_rerun={auxiliary_summary.get('final_rerun_warning_hits_total')} pdf_missing={len(auxiliary_pdf_missing)} digest_missing={len(auxiliary_digest_missing)} reproducible_missing={len(auxiliary_reproducible_missing)} reproducible_summary_ok={auxiliary_reproducible_summary_ok} hash_mismatches={len(auxiliary_hash_mismatches)} role_mismatches={len(auxiliary_role_mismatches)} duplicates={len(auxiliary_duplicate_rows)} toolchain_available={auxiliary_toolchain.get('toolchain_available')}",
    )
    auxiliary_md_ok = md_has_compile_summary(
        auxiliary_tex_compile_md_text,
        auxiliary_tex_compile_triage,
        f"- Targets checked: {auxiliary_summary.get('targets_checked')} / {auxiliary_summary.get('target_count_total')}",
    ) and "does not authorize publication" in auxiliary_tex_compile_md_text
    record(
        "auxiliary_tex_compile_triage_markdown_matches_json",
        auxiliary_md_ok,
        f"md_exists={auxiliary_tex_compile_md_path.exists()} json_revision={auxiliary_tex_compile_triage.get('generated_for_revision')} md_has_revision={auxiliary_tex_compile_triage.get('generated_for_revision') in auxiliary_tex_compile_md_text} checked={auxiliary_summary.get('targets_checked')} passed={auxiliary_summary.get('targets_passed')}",
    )

    all_tex_sources = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.tex"))
    all_tex_sources_expected_for_compile_evidence = sorted(path for path in all_tex_sources if path not in published_source_tex_paths)
    all_tex_compile_union = sorted(set(compile_partition_union) | set(actual_published_tex_paths) | set(auxiliary_row_paths))
    all_tex_overlaps = {
        "series_published": sorted(set(compile_partition_union) & set(actual_published_tex_paths)),
        "series_auxiliary": sorted(set(compile_partition_union) & set(auxiliary_row_paths)),
        "published_auxiliary": sorted(set(actual_published_tex_paths) & set(auxiliary_row_paths)),
    }
    all_tex_duplicate_rows = sorted(
        path for path in set(release_compile_paths + hold_compile_paths + unqueued_compile_paths + actual_published_tex_paths + auxiliary_row_paths)
        if (release_compile_paths + hold_compile_paths + unqueued_compile_paths + actual_published_tex_paths + auxiliary_row_paths).count(path) > 1
    )
    all_tex_partition_ok = all_tex_compile_union == all_tex_sources_expected_for_compile_evidence and not any(all_tex_overlaps.values()) and not all_tex_duplicate_rows
    record(
        "all_tex_compile_evidence_partition_is_complete",
        all_tex_partition_ok,
        f"all_tex_expected={len(all_tex_sources_expected_for_compile_evidence)} excluded_published_series={len(published_source_tex_paths)} series={len(compile_partition_union)} published={len(actual_published_tex_paths)} auxiliary={len(auxiliary_row_paths)} union={len(all_tex_compile_union)} overlaps={sum(len(v) for v in all_tex_overlaps.values())} duplicate_rows={len(all_tex_duplicate_rows)}",
    )

    all_tex_receipt_rows = [*queue_compile_rows, *hold_compile_rows, *unqueued_rows, *published_rows, *auxiliary_rows]
    all_tex_receipt_paths = [str(row.get("path", "")) for row in all_tex_receipt_rows if str(row.get("path", ""))]
    all_tex_receipt_duplicates = sorted({path for path in all_tex_receipt_paths if all_tex_receipt_paths.count(path) > 1})
    all_tex_receipt_missing_paths = sorted(
        str(row.get("path", ""))
        for row in all_tex_receipt_rows
        if isinstance(row, dict) and compile_digest_receipt_missing(row)
    )
    all_tex_receipt_ok = (
        sorted(set(all_tex_receipt_paths)) == all_tex_sources_expected_for_compile_evidence
        and len(all_tex_receipt_paths) == len(all_tex_sources_expected_for_compile_evidence)
        and not all_tex_receipt_duplicates
        and not all_tex_receipt_missing_paths
    )
    record(
        "all_tex_compile_digest_receipts_are_complete",
        all_tex_receipt_ok,
        f"all_tex_expected={len(all_tex_sources_expected_for_compile_evidence)} excluded_published_series={len(published_source_tex_paths)} receipt_rows={len(all_tex_receipt_paths)} unique_receipt_paths={len(set(all_tex_receipt_paths))} missing_receipts={len(all_tex_receipt_missing_paths)} duplicate_receipt_rows={len(all_tex_receipt_duplicates)}",
    )
    all_tex_reproducible_missing_paths = sorted(
        str(row.get("path", ""))
        for row in all_tex_receipt_rows
        if isinstance(row, dict) and compile_reproducible_receipt_missing(row)
    )
    all_tex_reproducible_ok = (
        all_tex_receipt_ok
        and not all_tex_reproducible_missing_paths
    )
    record(
        "all_tex_compile_reproducible_receipts_are_complete",
        all_tex_reproducible_ok,
        f"all_tex_expected={len(all_tex_sources_expected_for_compile_evidence)} excluded_published_series={len(published_source_tex_paths)} receipt_rows={len(all_tex_receipt_paths)} missing_reproducible_receipts={len(all_tex_reproducible_missing_paths)} duplicate_receipt_rows={len(all_tex_receipt_duplicates)} policy={COMPILE_RECEIPT_POLICY_V2}",
    )

    evidence_summary = evidence_pack_audit.get("summary", {})
    evidence_gate = evidence_pack_audit.get("next_release_evidence_gate", {})
    recommended_source = release_readiness_audit.get("next_release_recommendation", {}).get("source_tex")
    evidence_ok = (
        evidence_pack_audit.get("status") == "pass"
        and evidence_pack_audit.get("generated_for_revision") == release_manifest["revision"]
        and evidence_pack_audit.get("publication_authorized") is False
        and evidence_summary.get("checked_item_count") == (published_ready_total + candidate_total)
        and evidence_summary.get("missing_evidence_warning_count") == 0
        and evidence_summary.get("evidence_pack_integrity_status") == "pass"
        and evidence_gate.get("source_tex") == recommended_source
        and evidence_gate.get("status") in {"pending_attach_or_waive", "attached_evidence_pack"}
        and (evidence_gate.get("publication_blocking_until_resolved") is True or evidence_gate.get("evidence_pack_manifest"))
    )
    record(
        "evidence_pack_policy_audit_is_pass_and_bound",
        evidence_ok,
        f"evidence_status={evidence_pack_audit.get('status')} checked={evidence_summary.get('checked_item_count')} likely={evidence_summary.get('artifact_governance_likely_count')} missing_warning={evidence_summary.get('missing_evidence_warning_count')} next_gate={evidence_gate.get('status')} publication_authorized={evidence_pack_audit.get('publication_authorized')}",
    )

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
        and selected_source.get("source_sha256") == release_readiness_audit.get("next_release_recommendation", {}).get("source_sha256")
        and direct_preflight.get("status") == "pass"
        and (evidence_resolution_gate.get("status") == "pass" or evidence_resolution_pending)
        and freeze_gates.get("manual_clean_latex_compile", {}).get("status") in {"pass", "pending"}
        and freeze_summary.get("failed_gates") == 0
        and freeze_summary.get("pending_gates", 0) >= 1
    )
    record(
        "release_freeze_plan_is_non_authorizing_and_bound",
        freeze_ok,
        f"freeze_status={release_freeze_plan.get('status')} selected={selected_source.get('source_tex')} passed={freeze_summary.get('passed_gates')} pending={freeze_summary.get('pending_gates')} failed={freeze_summary.get('failed_gates')} publication_authorized={release_freeze_plan.get('publication_authorized')}",
    )

    toolchain_summary = freeze_toolchain.get("summary", {})
    toolchain_ok = (
        freeze_toolchain.get("status") == "pass"
        and freeze_toolchain.get("generated_for_revision") == release_manifest["revision"]
        and freeze_toolchain.get("checked_bundle") == release_manifest["bundle"]
        and freeze_toolchain.get("publication_authorized") is False
        and freeze_toolchain.get("toolchain_gate_status") in {"available", "unavailable"}
    )
    record(
        "freeze_toolchain_status_is_current_and_non_authorizing",
        toolchain_ok,
        f"toolchain_status={freeze_toolchain.get('toolchain_gate_status')} available={toolchain_summary.get('available_command_count')} publication_blocking={toolchain_summary.get('publication_blocking_when_compile_witness_not_current')}",
    )

    rehearsal_summary = publication_rehearsal.get("summary", {})
    rehearsal_ok = (
        publication_rehearsal.get("status") == "pass"
        and publication_rehearsal.get("generated_for_revision") == release_manifest["revision"]
        and publication_rehearsal.get("checked_bundle") == release_manifest["bundle"]
        and publication_rehearsal.get("publication_authorized") is False
        and rehearsal_summary.get("surface_failures") == 0
        and publication_rehearsal.get("source_binding", {}).get("source_tex") == recommended_source
    )
    record(
        "publication_rehearsal_is_bound_and_non_authorizing",
        rehearsal_ok,
        f"rehearsal_status={publication_rehearsal.get('readiness_status')} blockers={rehearsal_summary.get('blocking_gate_count')} surface_failures={rehearsal_summary.get('surface_failures')} publication_authorized={publication_rehearsal.get('publication_authorized')}",
    )

    assurance_paths = []
    for group in assurance_artifacts.get("groups", []):
        assurance_paths.extend(group.get("paths", []))
    assurance_missing = sorted({path for path in assurance_paths if not path.endswith('/') and not (root / path).exists()})
    assurance_ok = assurance_artifacts.get("generated_for_revision") == release_manifest["revision"] and not assurance_missing
    record(
        "assurance_artifact_catalog_matches_revision_and_paths",
        assurance_ok,
        f"assurance_revision={assurance_artifacts.get('generated_for_revision')} missing={'none' if not assurance_missing else ', '.join(assurance_missing)}",
    )

    transfer_sources_ok = (
        transfer_sources.get("generated_for_revision") == release_manifest["revision"]
        and transfer_sources.get("source_bundle_count") == len(transfer_sources.get("source_bundles", []))
    )
    record(
        "transfer_sources_match_revision_and_count",
        transfer_sources_ok,
        f"transfer_revision={transfer_sources.get('generated_for_revision')} source_bundle_count={transfer_sources.get('source_bundle_count')} actual={len(transfer_sources.get('source_bundles', []))}",
    )

    failures = [c for c in checks if c["status"] == "fail"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release_manifest["revision"],
        "checked_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "publication_authorized": False,
        "generated_at": revision_receipt["timestamp_local"],
        "fail_closed_rule": "If this report fails, default to no publication and repair the compact surfaces before relying on them.",
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
        },
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
