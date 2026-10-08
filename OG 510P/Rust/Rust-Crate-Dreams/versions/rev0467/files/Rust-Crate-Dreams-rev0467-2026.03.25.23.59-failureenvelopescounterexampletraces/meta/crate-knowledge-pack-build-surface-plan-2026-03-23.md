# Crate Knowledge Pack Kit — build-surface / conditioned-availability plan (2026-03-23)

## Product shape

Deliver the next concrete **P-0536** step as two small first-class artifacts above the earlier material-basis / citation / item-witness lane:

- `build-surface.receipt.json`
- `conditioned-availability.report.json`

The point is not to restate all of Cargo or docs.rs.
The point is to export one reviewable answer to:

1. **what recipe produced this docs/API/example surface?**
2. **under what recipe changes does this claim stop being valid?**

## Why this move is warranted now

Current primary sources now make the gap too concrete to ignore:

- docs.rs build docs say hosted docs are built on nightly in a sandbox;
- `cfg(docsrs)` only applies to the final documented crate, not to dependencies;
- hosted docs targets are configurable and target-aware;
- non-default docs.rs targets are cross-compiled;
- rustdoc JSON downloads are version-windowed by `format_version`;
- Cargo docs/example scraping remains unstable and recipe-bound;
- example scraping now has target-level configuration and dev-dependency caveats;
- rustdoc-JSON-powered tools prove the substrate is useful, but not yet receiver-facing.

So the missing crate contribution is not another parser.
It is a **conditioned support contract** for visible crate knowledge.

## New first-class artifacts

### `build-surface.receipt.json`

Purpose:
Freeze the concrete recipe that produced a visible docs/API/example surface.

Core fields:
- crate / version / profile
- surface id
- source kind (`docsrs_hosted_html`, `docsrs_rustdoc_json`, `local_rustdoc_json`, `local_docsrs_simulation`, `manual_review_required`)
- toolchain channel/version
- rustdoc JSON `format_version` when applicable
- feature posture (`features`, `all_features`, `no_default_features`)
- `cfg` posture
- target posture (`target`, `default_target`, `additional_targets`)
- docs.rs-cfg scope class
- example-scrape posture and caveats
- notes / caveats

### `conditioned-availability.report.json`

Purpose:
Say whether an item/example/page/support claim is present only under one build surface, absent under another, or still manual-review-only.

Core fields:
- crate / version / profile
- subject id + subject kind (`item`, `module`, `example`, `docs_page`, `query_slice`)
- build surface id
- availability class (`present`, `absent`, `target_bound`, `feature_bound`, `recipe_bound`, `format_window_mismatch`, `manual_review_required`)
- authority basis (`rustdoc_json`, `docsrs_html`, `cargo_metadata`, `tool_output`, `inference`)
- reason classes (`cfg_docsrs_scope`, `feature_gate`, `target_gate`, `example_scrape_recipe`, `rustdoc_json_format_window`, `manual_review_required`)
- linked witness / locator ids where available
- caveats and review notes

## Working rule

Do not let the archive claim:
- “the item exists,”
- “the docs page exists,”
- “the example is visible,”
- or “the machine-readable surface is supported”

unless the bundle can say **under what build surface** that was true.

## First proving-ground scenarios

1. `docsrs_cfg_only_applies_to_final_documented_crate_not_dependencies`
2. `docsrs_metadata_recipe_defines_hosted_surface_not_one_universal_page_set`
3. `scrape_examples_recipe_and_dev_dep_caveat_make_example_presence_conditioned`
4. `rustdoc_json_format_window_makes_machine_surface_recipe_bound`
5. `portable_bundle_keeps_identity_locator_and_conditioned_availability_separate`

## Guardrails

- Do not flatten item witness identity into visible availability.
- Do not flatten docs.rs default-target visibility into whole-crate support truth.
- Do not flatten a rustdoc JSON file into consumer support truth unless the format window is declared.
- Do not flatten scraped examples into official example presence without recipe provenance.
- Prefer `manual_review_required` over pretending the recipe is universal.

## MVP path

### 0.1
- emit build-surface receipts from docs.rs metadata + local capture
- emit conditioned-availability reports for a small set of items/examples
- support docs.rs hosted HTML, docs.rs rustdoc JSON, and local rustdoc JSON as source kinds

### 0.2
- wire doctor checks for fake universal-visibility claims
- attach build-surface ids to item-witness / locator / slice exports
- add diffing between build surfaces

### 0.3
- standardize profile presets such as `default_docsrs_surface`, `targeted_api_surface`, `machine_ingest_surface`, and `example_surface`

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html
- https://docs.rs/crate/cargo-public-api/latest
- https://docs.rs/crate/cargo-semver-checks/latest
