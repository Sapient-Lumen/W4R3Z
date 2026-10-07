#!/usr/bin/env python3
"""Check coherence across compact archive control surfaces.

This script is intentionally fail-closed: if the compact state surfaces disagree,
a future operator should default to no publication until the disagreement is fixed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime

from render_queue_surfaces import render_latest_decision_md, render_queue_md, render_status_md


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
    transfer_sources = load_json(root / "TRANSFER_SOURCES.json")
    assurance_artifacts = load_json(root / "ASSURANCE_ARTIFACTS.json")
    version_text = (root / "VERSION").read_text(encoding="utf-8").strip()
    citation_heads_md = (root / "published" / "CITATION_HEADS.md").read_text(encoding="utf-8")
    latest_decision_md_actual = (root / "release_queue" / "LATEST_DECISION.md").read_text(encoding="utf-8")
    status_md_actual = (root / "release_queue" / "STATUS.md").read_text(encoding="utf-8")
    queue_md_actual = (root / "release_queue" / "QUEUE.md").read_text(encoding="utf-8")
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
    review_ok = (
        queue_index["summary"]["reviewable_unpublished_papers"] == review_inventory["reviewable_unpublished_papers"] == len(review_inventory["entries"])
        and queue_index["summary"]["standalone_series_review_first"] == bucket_counts["standalone_series_review_first"]
        and queue_index["summary"]["synthesis_foundation_review_later"] == bucket_counts["synthesis_foundation_review_later"]
        and queue_index["summary"]["synthesis_tail_defer_high_churn"] == bucket_counts["synthesis_tail_defer_high_churn"]
    )
    record(
        "review_inventory_counts_match_queue_summary",
        review_ok,
        f"reviewable={review_inventory['reviewable_unpublished_papers']} bucket_counts={bucket_counts}",
    )

    legacy_paths = [x["path"] for x in publication_classification["legacy_canonical_public_wiki_targets"]]
    legacy_wikilinks = [x["wikilink"] for x in publication_classification["legacy_canonical_public_wiki_targets"]]
    citation_paths = [x["path"] for x in citation_heads["current_public_citation_heads"]]
    citation_wikilinks = [x["wikilink"] for x in citation_heads["current_public_citation_heads"]]
    legacy_json_paths = [x["path"] for x in legacy_links["canonical_legacy_links"]]
    legacy_json_wikilinks = [x["wikilink"] for x in legacy_links["canonical_legacy_links"]]
    frozen_paths = [x["path"] for x in publication_classification["repo_frozen_noncanonical_entries"]]
    citation_frozen_paths = [x["path"] for x in citation_heads["repo_frozen_noncanonical_entries"]]
    citation_ok = (
        legacy_paths == citation_paths == legacy_json_paths
        and legacy_wikilinks == citation_wikilinks == legacy_json_wikilinks
        and frozen_paths == citation_frozen_paths
        and citation_heads["summary"]["legacy_public_head_count"] == len(legacy_paths)
        and citation_heads["summary"]["new_post_policy_anonymity_head_count"] == len(citation_heads["new_post_policy_anonymity_heads"])
        and citation_heads["summary"]["repo_frozen_noncanonical_entry_count"] == len(frozen_paths)
    )
    record(
        "citation_heads_match_classification_and_legacy_register",
        citation_ok,
        f"legacy_public_heads={len(legacy_paths)} frozen_noncanonical={len(frozen_paths)}",
    )

    public_surface_ok = (
        public_surface["current_public_citation_heads"] == legacy_paths
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
        canonical_policy["assurance_artifacts"],
        canonical_policy["assurance_artifacts_markdown"],
    ])
    missing_paths = sorted({p for p in referenced_paths if not p.endswith('/') and not (root / p).exists()})
    record(
        "control_surface_paths_exist",
        not missing_paths,
        "missing=" + (", ".join(missing_paths) if missing_paths else "none"),
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
        "checked_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
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
