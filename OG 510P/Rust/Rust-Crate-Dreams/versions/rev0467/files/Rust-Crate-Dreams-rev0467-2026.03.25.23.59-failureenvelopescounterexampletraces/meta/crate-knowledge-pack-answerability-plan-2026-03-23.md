# Crate Knowledge Pack — answerability and claim-trace plan (2026-03-23)

This note deepens **P-0536 Crate Knowledge Pack Kit** around one product question:

> when a maintainer exports a compact support/search/assistant slice, what should another engineer be able to verify about what that slice can answer and how its claims trace back to source material?

## Main judgment

The next high-leverage move is to freeze three more receiver-facing artifacts:

1. `assistant-context.pack.json`
2. `query-support.matrix.json`
3. `claim-trace.report.json`

These should sit above:
- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`

Do not flatten those into one fake “assistant-ready crate context” story.

## 1. `assistant-context.pack.json`

Purpose:
- define the compact machine-facing slice itself;
- declare stable sections, linked artifacts, explicit exclusions, and manual-review zones.

Suggested fields:
- `crate`
- `profile`
- `sections[]`
  - `id`
  - `title`
  - `purpose`
  - `excerpt_ids[]`
  - `authority`
- `supported_query_classes[]`
- `manual_review_query_classes[]`
- `refused_query_classes[]`
- `linked_artifacts[]`
- `notes[]`

Questions it answers:
- what exact slice was exported?
- what is in it?
- what was excluded?
- which question classes are visibly outside scope?

## 2. `query-support.matrix.json`

Purpose:
- state what ordinary question classes this pack can answer directly, partially, only with human review, or not at all.

Suggested fields:
- `crate`
- `profile`
- `query_classes[]`
  - `class`
  - `status` (`supported`, `partial`, `manual_review_required`, `refused`)
  - `required_artifacts[]`
  - `evidence_basis[]`
  - `notes[]`
- `global_limitations[]`

Good early query classes:
- `getting_started`
- `public_api_navigation`
- `feature_flag_overview`
- `example_selection`
- `docsrs_visibility`
- `platform_support`
- `performance_tuning`
- `safety_invariants`
- `security_posture`
- `migration_guidance`

Questions it answers:
- what can this pack honestly answer without improvisation?
- which classes are only partial?
- which classes should force manual review or refusal?

## 3. `claim-trace.report.json`

Purpose:
- let a downstream reviewer trace compact claims back to exact excerpt IDs and source-material IDs.

Suggested fields:
- `crate`
- `profile`
- `claims[]`
  - `claim_id`
  - `text`
  - `authority`
  - `exactness`
  - `excerpt_ids[]`
  - `source_material_ids[]`
  - `manual_review_required`
  - `notes[]`
- `untraced_claim_classes[]`

Questions it answers:
- which summaries were direct extractions?
- which were conservative inference?
- which claims still require review because source material is incomplete or policy-restricted?

## Product stance

The crate should remain bundle-first and review-first.
Do **not** spend the next serious implementation pass on:
- conversational UX,
- model prompts,
- retrieval ranking,
- or hosted docs search.

Those consumers can arrive later.
First freeze the boring contract.

## Good proving grounds

1. a README-driven crate with one clear quickstart and a few public API sections;
2. a feature-heavy crate where docs.rs visibility does not match all local possibilities;
3. a crate where performance/security/safety questions should be marked `manual_review_required` or `refused` even though setup/API questions are supported.

## Doctor checks worth adding early

- warn when `assistant-context.pack.json` lists supported query classes without a matching `query-support.matrix.json` entry;
- warn when a supported query class has no evidence-basis entry;
- warn when assistant/exported summary claims lack `claim-trace` edges;
- warn when a slice includes inferred claims but no manual-review zones;
- warn when refused query classes are absent for obviously unsupported domains such as performance/security/safety.
