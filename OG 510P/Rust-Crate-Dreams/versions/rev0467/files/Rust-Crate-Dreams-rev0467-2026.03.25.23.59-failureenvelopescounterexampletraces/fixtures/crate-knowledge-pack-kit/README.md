# Crate Knowledge Pack Kit fixtures

This fixture family exists to make **P-0536 Crate Knowledge Pack Kit** less abstract.

The point is not to replace rustdoc, docs.rs, or doctest tooling.
The point is to standardize one small, provenance-aware crate handoff bundle another maintainer can review.

## Core bundle files

- `api-surface.receipt.json`
- `docs-source.manifest.json`
- `example-lineage.report.json`
- `feature-target-visibility.report.json`
- `docsrs-presence.import.json`
- `material-basis.receipt.json`
- `knowledge-slice.manifest.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`
- `assistant-context.pack.json`
- `query-support.matrix.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `citation-capability.report.json`
- `item-witness.manifest.json`
- `identity-fidelity.report.json`
- `build-surface.receipt.json`
- `conditioned-availability.report.json`
- optional `knowledge-diff.report.json`
- `knowledge-pack.manifest.json`
- `notes.md`

## Scenario families

### `docsrs_readme_and_target_choices_need_hosted_presence_import`
Proves that docs.rs-hosted README and target choices are real receiver-facing facts and must stay separate from local intent.

### `example_lineage_separates_official_runnable_from_illustrative_snippets`
Proves that a README snippet can be useful without being an official runnable example.

### `feature_gated_api_needs_visibility_not_just_rustdoc_name`
Proves that an item named by rustdoc still needs a visibility/gating explanation for ordinary users.

### `support_slice_excludes_internal_scaffolding_but_keeps_provenance`
Proves that small machine-consumable slices need explicit inclusion/exclusion policy rather than silent pruning.

### `release_drift_changes_api_example_and_hosted_truth`
Proves that release review needs one diff object connecting API, examples, and hosted docs drift.

## Design guardrails

- Keep authority, import, and inference separate.
- Keep docs.rs presence separate from local build observations.
- Keep example lineage separate from example execution truth.
- Keep small slices explicit about what they excluded.
- Prefer `manual_review_required` over fake certainty.

## 2026-03-22 artifact-rich additions

### New first-class artifacts

- `api-surface.receipt.json`
- `docs-source.manifest.json`
- `example-lineage.report.json`
- `docsrs-presence.import.json`
- `knowledge-slice.manifest.json`
- `knowledge-diff.report.json`
- `knowledge-pack.manifest.json`

### New scenario families

#### `docsrs_readme_and_target_choices_need_hosted_presence_import`
Proves that hosted README/default-target truth must be imported explicitly.

#### `example_lineage_separates_official_runnable_from_illustrative_snippets`
Proves that official, compile-only, illustrative, and generated examples must stay separate.

#### `feature_gated_api_needs_visibility_not_just_rustdoc_name`
Proves that rustdoc item inventory alone is not enough for end-user visibility truth.

#### `support_slice_excludes_internal_scaffolding_but_keeps_provenance`
Proves that support/assistant slices must publish exclusion notes and provenance.

#### `release_drift_changes_api_example_and_hosted_truth`
Proves that a single knowledge diff can connect multiple drift classes without flattening them.

### `latest_or_semver_docsrs_url_requires_resolved_material_basis`
Proves that convenient docs.rs shorthand URLs are not the same thing as a pinned review surface.

### `pre_2025_release_lacks_docsrs_rustdoc_json_and_keeps_gap_explicit`
Proves that older releases may still need an explicit hosted-material gap instead of a silent omission.

### `download_archive_material_basis_carries_static_root_and_target_caveats`
Proves that docs.rs download archives are valuable materials but still carry static-root and all-target caveats.

### `support_export_policy_redacts_internal_playbooks_but_keeps_excerpt_lineage`
Proves that a compact support/assistant slice should publish both its export policy and the exact excerpt lineage it relied on.


## 2026-03-22 material-basis / export-policy additions

### New first-class artifacts

- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`

### `assistant_context_declares_supported_queries_and_manual_review_zones`
Proves that a compact machine-facing pack must declare supported questions, manual-review zones, refusals, and linked artifacts.

### `query_support_matrix_separates_supported_partial_and_refused_question_classes`
Proves that support/search/assistant consumers need one explicit matrix for what the pack can answer honestly.

### `claim_trace_keeps_machine_summary_claims_tied_to_excerpts_and_materials`
Proves that exported summaries still need exact trace edges back to excerpt IDs and source-material IDs.


## 2026-03-23 citation-locator additions

### New first-class artifacts

- `citation-locator.receipt.json`
- `citation-capability.report.json`
- `item-witness.manifest.json`
- `identity-fidelity.report.json`

### `latest_docsrs_redirect_resolves_to_pinned_citation_locator`
Proves that a convenient docs.rs shorthand URL is not itself a frozen citation surface.

### `target_specific_docs_item_needs_target_aware_locator_and_fallback`
Proves that target-sensitive support claims need target-aware locators and visible fallbacks.

### `query_pack_has_citation_ready_getting_started_but_manual_review_perf`
Proves that a compact pack can be citation-ready for setup/API lookup while still refusing or routing performance questions to manual review.


## 2026-03-23 item-witness additions

The next fixture step for **P-0536** is to separate reviewable item identity from raw locators and raw rustdoc JSON IDs.

### `rustdoc_json_opaque_ids_need_item_witness_not_cross_blob_reuse`
Proves that a raw rustdoc JSON item ID can be recorded for auditability while still being treated as blob-local and non-durable across bundles.

### `version_bump_keeps_same_item_witness_even_when_locator_route_changes`
Proves that the same conceptual item can survive a route/version-selector change only through an explicit witness and recheck rule, not by URL similarity alone.

### `target_specific_item_witness_stays_distinct_from_default_target_locator`
Proves that target-sensitive item identity cannot be inferred from a convenient default-target docs.rs route.


## 2026-03-23 build-surface additions

### New first-class artifacts

- `build-surface.receipt.json`
- `conditioned-availability.report.json`

### `docsrs_cfg_only_applies_to_final_documented_crate_not_dependencies`
Proves that docsrs-only visibility must keep cfg scope explicit instead of becoming a workspace-wide claim.

### `docsrs_metadata_recipe_defines_hosted_surface_not_one_universal_page_set`
Proves that docs.rs metadata defines one hosted build surface rather than a universal crate view.

### `scrape_examples_recipe_and_dev_dep_caveat_make_example_presence_conditioned`
Proves that scraped-example presence depends on build recipe and dev-dependency posture.

### `rustdoc_json_format_window_makes_machine_surface_recipe_bound`
Proves that machine-facing support claims need a build-surface receipt with toolchain and format-window context.

### `portable_bundle_keeps_identity_locator_and_conditioned_availability_separate`
Proves that item identity, citation routes, and conditioned availability are separate bundle lanes.


## 2026-03-24 intake/materialization additions

### New first-class artifacts

- `intake.receipt.json`
- `materialization-plan.json`

### `latest_docsrs_download_materialization_resolves_pin_and_preserves_offline_caveats`
Proves that a convenient `latest` docs.rs download route can still become part of a frozen basis, but only through an explicit intake receipt plus a materialization plan that keeps target-layout, static-root, and missing-asset caveats visible.
