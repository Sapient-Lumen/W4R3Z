# Assurance Case Workbench Kit — product plan (2026-03-21)

This note sharpens **P-0503 Assurance Case Workbench Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0503** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not become a certification workflow platform, a requirements database, or a graphical editor suite.
It should provide one boring, reviewable **assurance-pack contract** above today's verification, coverage, lint, conformance, and evidence-bundle substrate.

`0.1` should make five things first-class:

1. **claim-library basis** — which reusable argument/profile basis is actually in use;
2. **import policy** — which evidence classes are admissible, what freshness/trust minima apply, and when import falls back to manual review;
3. **assumption ledger** — which assumptions remain unresolved, who owns them, and what they block;
4. **review gate** — why the pack is green/yellow/red/blocked rather than only what each claim says;
5. **export projection** — what a GSN- or SACM-shaped export preserves, redacts, or loses relative to the internal model.

## What `0.1` should provide other people

- one compact `assurance-profile.toml`
- one compact `claim-graph.json`
- one compact `evidence-index.json`
- one compact `claim-status.report.json`
- one compact `import-policy.receipt.json`
- one compact `assumption-ledger.report.json`
- one compact `review-gate.report.json`
- one compact `export-projection.receipt.json`
- one compact `assurance-diff.report.json`
- one compact `review-pack-manifest.json`
- one portable review/support bundle

## Commands worth shipping first

- `cargo assurance-case assemble`
- `cargo assurance-case review`
- `cargo assurance-case diff`
- `cargo assurance-case export --format gsn`
- `cargo assurance-case export --format sacm`
- `cargo assurance-case bundle`

## What to import, not reinvent

- verification-campaign bundles such as **P-0485** outputs
- evidence-bundle substrate such as **P-0256** profiles
- coverage / conformance / lint / unsafe-audit receipts when present
- maintainer-authored assumption or manual-review notes
- optional standards/editor exports rather than in-tree diagram editors

## Suggested `0.1` doctor warnings

- `top_claim_green_but_unresolved_assumption_present`
- `evidence_import_allowed_without_trust_or_freshness_basis`
- `export_projection_claims_roundtrip_without_status_mapping`
- `gsn_export_drops_manual_review_reasoning`
- `sacm_export_redacts_lineage_without_receipt`
- `mixed_evidence_pack_missing_review_gate_summary`
- `stale_campaign_import_not_escalated_to_block_or_manual_review`

## First proving-ground scenarios

1. **A mixed pack with verification, conformance, and manual review imports should still keep import-policy basis explicit.**
2. **A single unresolved assumption should block a top release claim even when most imported evidence is green.**
3. **A stale or low-trust imported campaign should change the review gate without corrupting the claim graph.**
4. **A GSN-shaped export should preserve status class and claim lineage even when local review-only fields are omitted.**
5. **A SACM-shaped export should state what was redacted or projected instead of implying full round-trip fidelity.**

## What to leave for later

- interactive diagram editing
- regulator- or standard-specific submission workflows
- full requirements/hazard-log lifecycle management
- organization-specific approval routing
- automatic import adapters for every evidence producer in the archive
