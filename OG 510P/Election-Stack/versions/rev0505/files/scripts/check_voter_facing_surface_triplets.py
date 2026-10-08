#!/usr/bin/env python3
"""Triplet/orphan firewall for voter-facing public-answer surfaces."""

from __future__ import annotations

from pathlib import Path
import re

from _shared.voter_surface_registry import load_surface_registry, surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
TEMPLATES_DIR = ROOT / "artifacts" / "templates"
CHECKLISTS_DIR = ROOT / "artifacts" / "checklists"

ALLOWED_EXTRA_TEMPLATE_NAMES = {
    "voting-location-directory-payload.json",
    "ballot-style-directory-payload.json",
    "automated-voter-information-assistant-surface-payload.json",
    "official-voter-faq-answer-surface-payload.json",
    "official-voter-information-video-surface-payload.json",
    "official-voter-information-email-surface-payload.json",
    "official-voter-information-community-partner-distribution-payload.json",
    "official-voter-information-site-signage-surface-payload.json",
    "official-voter-information-form-surface-payload.json",
    "official-voter-information-router-surface-payload.json",
    "official-voter-information-site-search-surface-payload.json",
    "official-voter-information-map-surface-payload.json",
    "official-voter-information-language-selector-surface-payload.json",
    "official-voter-information-file-delivery-surface-payload.json",
    "official-voter-information-link-recovery-surface-payload.json",
    "official-voter-information-site-alert-surface-payload.json",
    "official-voter-information-qr-shortlink-surface-payload.json",
    "official-voter-information-search-result-surface-payload.json",
    "official-voter-information-social-profile-surface-payload.json",
    "official-voter-information-mobile-app-surface-payload.json",
    "official-voter-information-place-card-surface-payload.json",
    "official-voter-information-ai-answer-surface-payload.json",
    "official-voter-information-voice-answer-surface-payload.json",
    "official-voter-information-link-preview-surface-payload.json",
    "official-voter-information-calendar-reminder-surface-payload.json",
    "official-voter-information-api-surface-payload.json",
    "official-voter-information-discovery-surface-payload.json",
    "official-voter-information-identity-surface-payload.json",
    "official-voter-information-search-appearance-markup-surface-payload.json",
    "official-voter-information-search-removal-and-recrawl-surface-payload.json",
    "official-voter-information-snippet-preview-surface-payload.json",
    "official-voter-information-date-cues-surface-payload.json",
    "official-voter-information-alternate-language-discovery-surface-payload.json",
    "official-voter-information-domain-migration-surface-payload.json",
    "official-voter-information-search-console-control-plane-surface-payload.json",
    "official-voter-information-search-observability-surface-payload.json",
    "official-voter-information-url-inspection-surface-payload.json",
    "official-voter-information-page-performance-surface-payload.json",
    "official-voter-information-progressive-enhancement-surface-payload.json",
    "official-voter-information-cache-freshness-surface-payload.json",
    "official-voter-information-anti-bot-challenge-surface-payload.json",
    "official-voter-information-request-context-variance-surface-payload.json",
    "official-voter-information-secure-transport-surface-payload.json",
    "official-voter-information-overload-surface-payload.json",
    "official-voter-information-public-read-access-surface-payload.json",
    "official-voter-information-third-party-dependency-surface-payload.json",
    "official-voter-information-first-load-overlay-surface-payload.json",
    "official-voter-information-browser-permission-surface-payload.json",
    "official-voter-information-external-handoff-surface-payload.json",
    "official-voter-information-embedded-browser-surface-payload.json",
    "official-voter-information-low-connectivity-surface-payload.json",
    "official-voter-information-reflow-surface-payload.json",
    "official-voter-information-keyboard-focus-surface-payload.json",
    "official-voter-information-screen-reader-surface-payload.json",
    "official-voter-information-color-contrast-surface-payload.json",
    "official-voter-information-motion-surface-payload.json",
    "official-voter-information-pointer-operability-surface-payload.json",
    "official-voter-information-field-entry-surface-payload.json",
    "official-voter-information-date-entry-surface-payload.json",
    "official-voter-information-address-entry-surface-payload.json",
    "official-voter-information-name-entry-surface-payload.json",
    "official-voter-information-fixed-format-identifier-entry-surface-payload.json",
    "official-voter-information-contact-target-verification-surface-payload.json",
    "official-voter-information-document-upload-surface-payload.json",
    "official-voter-information-multi-step-progress-surface-payload.json",
    "official-voter-information-submission-confirmation-surface-payload.json",
    "official-voter-information-timeout-recovery-surface-payload.json",
    "official-voter-information-processing-wait-state-surface-payload.json",
    "official-voter-information-post-submit-pending-status-surface-payload.json",
    "official-voter-information-unsuccessful-outcome-surface-payload.json",
    "official-voter-information-service-unavailable-surface-payload.json",
    "official-voter-information-shared-device-exit-surface-payload.json",
    "official-voter-information-portable-record-surface-payload.json",
    "official-voter-information-share-safe-link-surface-payload.json",
    "official-voter-information-history-restore-surface-payload.json",
    "official-voter-information-reader-mode-surface-payload.json",
    "official-voter-information-browser-chrome-identity-surface-payload.json",
    "official-voter-information-section-target-surface-payload.json",
    "official-voter-information-collapsed-answer-surface-payload.json",
    "official-voter-information-unobscured-target-surface-payload.json",
    "official-voter-information-tab-panel-surface-payload.json",
}

ALLOWED_EXTRA_CHECKLIST_NAMES = {
    "automated-voter-information-assistant-surface-checklist.md",
    "official-voter-faq-answer-surface-checklist.md",
    "official-voter-information-video-surface-checklist.md",
    "official-voter-information-email-surface-checklist.md",
    "official-voter-information-community-partner-distribution-checklist.md",
    "official-voter-information-site-signage-checklist.md",
    "official-voter-information-form-surface-checklist.md",
    "official-voter-information-router-surface-checklist.md",
    "official-voter-information-site-search-surface-checklist.md",
    "official-voter-information-map-surface-checklist.md",
    "official-voter-information-language-selector-surface-checklist.md",
    "official-voter-information-file-delivery-surface-checklist.md",
    "official-voter-information-link-recovery-surface-checklist.md",
    "official-voter-information-site-alert-surface-checklist.md",
    "official-voter-information-qr-shortlink-surface-checklist.md",
    "official-voter-information-search-result-surface-checklist.md",
    "official-voter-information-social-profile-surface-checklist.md",
    "official-voter-information-mobile-app-surface-checklist.md",
    "official-voter-information-place-card-surface-checklist.md",
    "official-voter-information-ai-answer-surface-checklist.md",
    "official-voter-information-voice-answer-surface-checklist.md",
    "official-voter-information-link-preview-surface-checklist.md",
    "official-voter-information-calendar-reminder-surface-checklist.md",
    "official-voter-information-api-surface-checklist.md",
    "official-voter-information-discovery-surface-checklist.md",
    "official-voter-information-identity-surface-checklist.md",
    "official-voter-information-search-appearance-markup-surface-checklist.md",
    "official-voter-information-search-removal-and-recrawl-surface-checklist.md",
    "official-voter-information-snippet-preview-surface-checklist.md",
    "official-voter-information-date-cues-surface-checklist.md",
    "official-voter-information-alternate-language-discovery-surface-checklist.md",
    "official-voter-information-domain-migration-surface-checklist.md",
    "official-voter-information-search-console-control-plane-surface-checklist.md",
    "official-voter-information-search-observability-surface-checklist.md",
    "official-voter-information-url-inspection-surface-checklist.md",
    "official-voter-information-page-performance-surface-checklist.md",
    "official-voter-information-progressive-enhancement-surface-checklist.md",
    "official-voter-information-cache-freshness-surface-checklist.md",
    "official-voter-information-anti-bot-challenge-surface-checklist.md",
    "official-voter-information-request-context-variance-surface-checklist.md",
    "official-voter-information-secure-transport-surface-checklist.md",
    "official-voter-information-overload-surface-checklist.md",
    "official-voter-information-public-read-access-surface-checklist.md",
    "official-voter-information-third-party-dependency-surface-checklist.md",
    "official-voter-information-first-load-overlay-surface-checklist.md",
    "official-voter-information-browser-permission-surface-checklist.md",
    "official-voter-information-external-handoff-surface-checklist.md",
    "official-voter-information-embedded-browser-surface-checklist.md",
    "official-voter-information-low-connectivity-surface-checklist.md",
    "official-voter-information-reflow-surface-checklist.md",
    "official-voter-information-keyboard-focus-surface-checklist.md",
    "official-voter-information-screen-reader-surface-checklist.md",
    "official-voter-information-color-contrast-surface-checklist.md",
    "official-voter-information-motion-surface-checklist.md",
    "official-voter-information-pointer-operability-surface-checklist.md",
    "official-voter-information-field-entry-surface-checklist.md",
    "official-voter-information-date-entry-surface-checklist.md",
    "official-voter-information-address-entry-surface-checklist.md",
    "official-voter-information-name-entry-surface-checklist.md",
    "official-voter-information-fixed-format-identifier-entry-surface-checklist.md",
    "official-voter-information-contact-target-verification-surface-checklist.md",
    "official-voter-information-document-upload-surface-checklist.md",
    "official-voter-information-multi-step-progress-surface-checklist.md",
    "official-voter-information-submission-confirmation-surface-checklist.md",
    "official-voter-information-timeout-recovery-surface-checklist.md",
    "official-voter-information-processing-wait-state-surface-checklist.md",
    "official-voter-information-post-submit-pending-status-surface-checklist.md",
    "official-voter-information-unsuccessful-outcome-surface-checklist.md",
    "official-voter-information-service-unavailable-surface-checklist.md",
    "official-voter-information-shared-device-exit-surface-checklist.md",
    "official-voter-information-portable-record-surface-checklist.md",
    "official-voter-information-share-safe-link-surface-checklist.md",
    "official-voter-information-history-restore-surface-checklist.md",
    "official-voter-information-reader-mode-surface-checklist.md",
    "official-voter-information-browser-chrome-identity-surface-checklist.md",
    "official-voter-information-section-target-surface-checklist.md",
    "official-voter-information-collapsed-answer-surface-checklist.md",
    "official-voter-information-unobscured-target-surface-checklist.md",
    "official-voter-information-tab-panel-surface-checklist.md",
}


def numbered_doc_id(path: Path) -> int | None:
    m = re.match(r"^(\d{1,3})[-_].*\.md$", path.name)
    if not m:
        return None
    return int(m.group(1))


def main() -> int:
    errors: list[str] = []
    table = load_surface_registry()
    registry_doc_ids: set[int] = set()
    registry_doc_paths: set[str] = set()
    registry_template_paths: set[str] = set()
    registry_checklist_paths: set[str] = set()

    for i, row in enumerate(table.rows, start=2):
        if not any(row.values()):
            continue
        try:
            doc_id = int(row["doc_id"])
        except ValueError:
            errors.append(f"L{i}: invalid doc_id {row['doc_id']!r}")
            continue

        doc_path = row["doc_path"]
        template_path = row["template_path"]
        checklist_path = row["checklist_path"]

        if doc_id in registry_doc_ids:
            errors.append(f"L{i}: duplicate doc_id in registry: {doc_id}")
        registry_doc_ids.add(doc_id)

        for label, rel, seen in [
            ("doc_path", doc_path, registry_doc_paths),
            ("template_path", template_path, registry_template_paths),
            ("checklist_path", checklist_path, registry_checklist_paths),
        ]:
            if rel in seen:
                errors.append(f"L{i}: duplicate {label}: {rel}")
            seen.add(rel)

    expected_doc_ids = surface_doc_ids(table)
    if registry_doc_ids != expected_doc_ids:
        missing_ids = sorted(expected_doc_ids - registry_doc_ids)
        extra_ids = sorted(registry_doc_ids - expected_doc_ids)
        if missing_ids:
            errors.append(f"registry missing family doc_ids: {missing_ids}")
        if extra_ids:
            errors.append(f"registry has out-of-family doc_ids: {extra_ids}")

    numbered_surface_docs = {
        doc_id
        for p in DOCS_DIR.glob("*.md")
        if (doc_id := numbered_doc_id(p)) is not None
        and doc_id in expected_doc_ids
        and "tombstone" not in p.read_text(encoding="utf-8", errors="ignore")[:200].lower()
    }
    if numbered_surface_docs != expected_doc_ids:
        missing_ids = sorted(expected_doc_ids - numbered_surface_docs)
        extra_ids = sorted(numbered_surface_docs - expected_doc_ids)
        if missing_ids:
            errors.append(f"missing canonical numbered docs in family registry: {missing_ids}")
        if extra_ids:
            errors.append(f"unexpected numbered docs in family registry: {extra_ids}")

    unregistered_surface_checklists = sorted(
        str(p.relative_to(ROOT))
        for p in CHECKLISTS_DIR.glob("*surface-checklist.md")
        if str(p.relative_to(ROOT)) not in registry_checklist_paths
        and p.name not in ALLOWED_EXTRA_CHECKLIST_NAMES
    )
    if unregistered_surface_checklists:
        errors.append(
            "unregistered voter-facing surface checklists: "
            + ", ".join(unregistered_surface_checklists)
        )

    candidate_template_paths = set()
    for p in TEMPLATES_DIR.glob("*surface-payload.json"):
        candidate_template_paths.add(str(p.relative_to(ROOT)))
    for name in ALLOWED_EXTRA_TEMPLATE_NAMES:
        p = TEMPLATES_DIR / name
        if p.exists():
            candidate_template_paths.add(str(p.relative_to(ROOT)))

    unregistered_surface_templates = sorted(
        rel
        for rel in candidate_template_paths
        if rel not in registry_template_paths
        and Path(rel).name not in ALLOWED_EXTRA_TEMPLATE_NAMES
    )
    if unregistered_surface_templates:
        errors.append(
            "unregistered voter-facing surface templates: "
            + ", ".join(unregistered_surface_templates)
        )

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: voter-facing public-answer surface triplets/orphans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
