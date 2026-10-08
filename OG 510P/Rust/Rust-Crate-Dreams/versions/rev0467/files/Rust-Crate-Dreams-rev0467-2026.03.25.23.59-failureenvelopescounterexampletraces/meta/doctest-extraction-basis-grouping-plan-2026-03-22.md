# Doctest extraction pipeline — basis and grouping plan (2026-03-22)

## Product goal

Deepen **P-0455 Doctest Extraction & Support Contract Kit** so that a bundle can answer not only “what examples exist and how did they run?” but also:

1. what exact authority and format produced the extracted manifest,
2. whether two doctest bundles are honestly comparable given grouping / edition / target / attribute drift,
3. and what exact artifacts should be handed to another maintainer as one portable doctest-support bundle.

## New first-class artifacts

- `extraction-basis.receipt.json`
  - extraction authority (`rustdoc_output_format_doctest`, `rustdoc_test_collection_import`, `preextracted_bundle_import`, `markdown_fallback`, `manual_inventory`, `manual_review_required`)
  - toolchain channel/version and `format_version` when applicable
  - source root and selected manifest scope
  - notes on whether hidden lines, wrapper text, or crate injection facts come from first-party rustdoc output or downstream reconstruction

- `grouping-comparison.report.json`
  - left/right bundle ids
  - comparison verdict (`like_for_like`, `grouping_drift`, `target_scope_drift`, `attribute_scope_drift`, `basis_drift`, `not_comparable`, `manual_review_required`)
  - explicit blockers such as edition 2024 merge semantics, `standalone_crate`, `compile_fail`, target-specific ignores, or runner-policy imports
  - safe human summary for PR review or support replies

- `doctest-support-bundle.manifest.json`
  - compact manifest pointing to the doctest manifest, extraction-basis receipt, rewrite-lineage receipt, execution-mode receipt, docs-example-support report, drift reports, grouping-comparison reports, and imported adjacent-lane receipts
  - redaction/manual-review section for private support material
  - share-safe summary for issue filing or release-review handoff

## Suggested commands / UX

- `cargo doctest-contract inspect-basis`
  - emits an extraction-basis receipt before or after extraction
- `cargo doctest-contract compare old.bundle new.bundle`
  - emits a grouping-comparison report before showing doctest deltas
- `cargo doctest-contract bundle`
  - assembles a portable doctest-support bundle from current receipts

## Theory-of-practice rules

Never treat a scraped Markdown inventory as the same authority class as rustdoc’s `--output-format doctest` JSON.

Never compare a 2024-edition merged doctest bundle to a standalone- or `standalone_crate`-heavy bundle without an explicit grouping-comparison report.

Never let docs.rs rendering, `cargo test --doc`, or a cross-target runner import silently stand in for extraction authority.

Never let a passing doctest trend claim ignore basis drift, grouping drift, target drift, or attribute drift.

## MVP order

1. stabilize `extraction-basis.receipt.json`,
2. stabilize `grouping-comparison.report.json`,
3. stabilize `doctest-support-bundle.manifest.json`,
4. teach the existing support/drift artifacts to reference them,
5. add tiny scenario fixtures for nightly JSON basis, merged-vs-standalone comparability, and portable bundle inventory,
6. only then widen docs.rs / runner / coverage imports.
