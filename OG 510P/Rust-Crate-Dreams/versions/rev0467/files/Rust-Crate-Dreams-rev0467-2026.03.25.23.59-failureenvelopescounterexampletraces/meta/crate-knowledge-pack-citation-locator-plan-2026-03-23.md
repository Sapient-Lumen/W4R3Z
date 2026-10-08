# Crate Knowledge Pack — citation locator and citation-capability plan (2026-03-23)

This note deepens **P-0536 Crate Knowledge Pack Kit** around one product question:

> when a maintainer says “this compact support/search/assistant pack is citation-ready”, what exactly should another engineer be able to review about the URLs, versions, targets, anchors, and fallback routes used by that pack?

## Main judgment

The next high-leverage move is to freeze two more receiver-facing artifacts:

1. `citation-locator.receipt.json`
2. `citation-capability.report.json`

These should sit above:
- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`
- `assistant-context.pack.json`
- `query-support.matrix.json`
- `claim-trace.report.json`

Do not flatten those into one fake “assistant pack is grounded” story.

## Why this matters now

Fresh official docs make the missing layer unusually concrete:

- docs.rs shorthand URLs intentionally float across `latest`, semver ranges, and page redirects;
- docs.rs hosted builds are target-aware and the default target is configurable;
- docs.rs rustdoc JSON availability is version-windowed and rebuild-sensitive;
- docs.rs download archives are valuable import materials but not equivalent to a self-contained offline citation surface;
- `cargo rustdoc` keeps target/example/bin selection explicit;
- and Cargo metadata still recommends pinning an output format version.

That means a worthy crate here should no longer stop at “we know where the docs came from.”
It should export a reviewable answer for **what another tool should cite**.

## 1. `citation-locator.receipt.json`

Purpose:
- resolve convenient documentation routes into reviewable, target-aware locators;
- keep floating shorthand, pinned pages, local unpublished paths, and fallback routes visibly separate.

Suggested fields:
- `crate`
- `profile`
- `locators[]`
  - `id`
  - `source_material_id`
  - `excerpt_ids[]`
  - `locator_class` (`docsrs_item_page`, `docsrs_readme_section`, `docsrs_target_page`, `docsrs_download_archive_path`, `local_unpublished`, `manual_review_required`)
  - `canonical_locator`
  - `fetched_locator`
  - `version_selector` (`exact`, `semver_range`, `latest`, `workspace_head`)
  - `resolved_version`
  - `target`
  - `anchor_kind` (`item_path`, `html_fragment`, `readme_heading`, `archive_path`, `none`)
  - `pin_status` (`pinned`, `resolved_from_floating`, `floating`, `local_only`)
  - `citation_ready`
  - `fallback_locators[]`
  - `caveats[]`
- `notes[]`

Questions it answers:
- What exact page/path should a downstream tool cite?
- Was it pinned or silently derived from `latest`/semver shorthand?
- Was the locator target-aware?
- What fallback remains if the hosted anchor or target page is unavailable?

## 2. `citation-capability.report.json`

Purpose:
- say which exported sections or query classes can honestly produce item/page/package-level citations and which still require manual review.

Suggested fields:
- `crate`
- `profile`
- `query_classes[]`
  - `class`
  - `citation_level` (`item_anchor`, `page_anchor`, `page_only`, `package_only`, `manual_review_required`, `refused`)
  - `required_locator_classes[]`
  - `target_sensitive`
  - `notes[]`
  - `gaps[]`
- `global_limitations[]`

Good early query classes:
- `getting_started`
- `public_api_navigation`
- `feature_flag_overview`
- `example_selection`
- `docsrs_visibility`
- `platform_support`
- `performance_tuning`
- `security_posture`
- `safety_invariants`
- `migration_guidance`

Questions it answers:
- Which question classes can this pack cite at item/page level?
- Which only have package-level or archive-level locators?
- Which classes must still be manual-review-only or refused?

## Product stance

The crate should remain bundle-first and review-first.
Do **not** spend the next serious implementation pass on:
- answer generation,
- prompt templates,
- ranking,
- embeddings,
- or offline docs hosting.

Those consumers can arrive later.
First freeze the boring locator contract.

## Good proving grounds

1. a crate whose public API docs are citation-ready on the default docs.rs target;
2. a crate where a target-specific page or example changes what can honestly be cited;
3. a crate where setup/API questions are citation-ready but performance/security/safety answers remain manual-review-only.

## Doctor checks worth adding early

- warn when a `supported` query class has no citation-capability entry;
- warn when a citation-ready claim lacks a locator receipt edge;
- warn when `latest` or semver-range locators are exported without a resolved exact version;
- warn when target-sensitive claims point only at default-target locators;
- warn when manual-review-only classes are emitted as citation-ready.

## Worked boundary examples to keep straight

- **`docs.rs/crate/foo/latest`** is a useful browsing route, but not the same thing as a pinned citation surface.
- **A docs.rs default-target page** is not evidence that the same page/anchor exists on a different target.
- **A docs.rs download archive path** can be a useful fallback locator without being equivalent to a public hosted item anchor.
- **A local unpublished workspace path** can support internal review while still being inappropriate for public citation.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/redirections
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
