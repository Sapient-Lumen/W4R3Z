# Crate configuration-scenario product plan — 2026-03-17

This note exists to keep **P-0516 Crate Configuration Scenario Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing setup / scenario / recipe contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0516** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which named scenarios the crate actually intends,
- which features, env knobs, docs.rs settings, target assumptions, and backend/runtime choices belong to each one,
- which scenario is the honest default or recommended starting path,
- which docs-only or workspace-only surfaces drift away from ordinary builds,
- how much of the scenario matrix was actually checked,
- and what changed between releases.

It should **not** try to become a generic Cargo config explainer, a powerset executor for every feature combination, a docs portal, or a whole project template engine.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and docs/tool authors, the crate should provide:

1. **One compact scenario contract** instead of README folklore, scattered feature comments, docs.rs metadata, and CI YAML archaeology.
2. **A scenario-class policy** so `recommended_default`, `minimal_supported`, `backend_choice`, `docs_only`, `integration_heavy`, `board_only`, and `manual_review_required` stop being implicit vibes.
3. **Named recipe manifests** so “use rustls on Tokio” or “use the honest `no_std + alloc` lane” is encoded as a checked path rather than prose.
4. **Origin receipts** so each important fact says whether it came from Cargo manifests, docs.rs metadata, observed builds, maintainer policy, or hand-linked docs.
5. **Matrix-fidelity reports** so people can tell whether a scenario was fully observed, partially sampled, docs-only, or merely declared.
6. **Conflict classification** so “these two backends technically compile together but we only support one at a time” is first-class.
7. **A short human summary** that can be pasted into release notes, docs portals, and issue templates.
8. **A release diff** that makes quiet setup drift loud.

For maintainers, the crate should provide:

1. a compact pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches instead of fake certainty,
3. a way to import Cargo/docs.rs/build metadata instead of replacing it,
4. one place to declare which scenario is the official onboarding lane,
5. and a CI gate for “this release changed what a downstream user should set up.”

## Recommended `0.1` command surface

### `cargo scenario-pack init`
Create a starter `scenario-pack.toml` by importing obvious candidates from:

- Cargo manifest features and optional dependencies,
- target tables using `required-features`,
- `[package.metadata.docs.rs]`,
- selected `cargo metadata` output,
- maintainer-declared environment knobs,
- and obvious README / docs anchors when explicitly requested.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo scenario-pack capture`
Emit one normalized receipt bundle from the declared scenario surface.
This should capture:

- scenario inventory,
- scenario classes,
- feature/env/docs.rs/target/runtime facts,
- recipe references,
- imported origins,
- and matrix coverage observations.

`capture` should work even when some scenarios are docs-only or board-only.
It must preserve uncertainty instead of silently synthesizing support claims.

### `cargo scenario-pack check`
Run the local validation pass:

- do declared scenarios parse,
- do recipe manifests resolve,
- do target/example `required-features` facts match the policy,
- do imported docs.rs settings agree with declared docs scenarios,
- can selected scenarios build/test/doc under the advertised matrix,
- and which parts remain partial or manual-review-only?

### `cargo scenario-pack doctor`
Render human-facing warnings for suspicious situations such as:

- `docsrs_surface_exceeds_default_build`
- `backend_choice_not_marked_explicit`
- `no_std_claim_without_example_or_test_honesty`
- `required_features_hide_official_recipe`
- `workspace_only_recipe_presented_as_single_crate_default`
- `environment_knob_missing_from_recipe`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo scenario-pack summary`
Render a short receiver-facing note that answers:

- what the official start path is,
- what the main alternative scenarios are,
- which choices are runtime/backend/select-one boundaries,
- how docs.rs differs from ordinary builds,
- and where manual review still begins.

### `cargo scenario-pack diff <old> <new>`
Compare two receipts or packs and classify:

- `scenario_added`
- `scenario_removed`
- `scenario_class_changed`
- `recommended_default_changed`
- `feature_bundle_changed`
- `env_contract_changed`
- `docs_surface_changed`
- `required_features_changed`
- `matrix_fidelity_changed`
- `manual_review_required`

### `cargo scenario-pack pack`
Emit one compact `.scenariopack.zip` bundle for CI artifacts, release review, docs generation, and support handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `scenario_pack_model`
  - shared Rust types for packs, receipts, reports, manifests, evidence classes, and diffs
- `scenario_pack_discovery`
  - import logic for manifest features, target tables, docs.rs metadata, and declared env/config knobs
- `scenario_pack_check`
  - recipe validation, conflict classification, matrix-coverage checks, and doctor warnings
- `scenario_pack_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-scenario-pack`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `scenario_pack_docsrs`
- `scenario_pack_cargo_metadata`
- `scenario_pack_cargo_hack`
- `scenario_pack_document_features`
- `scenario_pack_workspace`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `scenario-pack.toml`
- `config-surface.receipt.json`
- `scenario-profile.report.json`
- `scenario-recipe.manifest.json`
- `scenario-check.report.json`
- `scenario-conflict.report.json`
- `scenario-diff.report.json`
- `scenario-notes.summary.md`

This pass adds three more important artifacts:

- `scenario-class.policy.json` — what `recommended_default`, `minimal_supported`, `backend_choice_required`, `docs_only`, `integration_heavy`, `board_only`, and `manual_review_required` mean and what minimum evidence each class expects.
- `config-origin.receipt.json` — where important facts came from: manifest, docs.rs metadata, observed build/test/doc run, maintainer declaration, or external-doc/manual import.
- `matrix-fidelity.report.json` — how much of the advertised scenario matrix was actually observed versus sampled, imported, inferred, or left manual-review-only.

Those files matter because setup stories get vague again if the archive only records feature bundles and recipes but not:

- what *kind* of scenario is being claimed,
- where the claim came from,
- and how complete the real coverage was.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Manifest and target facts**
   - `[features]`
   - optional dependencies
   - target tables and `required-features`
2. **Docs.rs facts**
   - `[package.metadata.docs.rs]`
   - `cfg(docsrs)` notes when explicitly declared
3. **Maintainer policy**
   - named scenarios
   - scenario classes
   - preferred default / deprecated lanes
4. **Observed checks**
   - build/test/doc receipts
   - selected target/profile/runtime observations
5. **Manual-review zones**
   - board-only, workspace-only, credentialed, or non-local scenarios

The importer should prefer visible uncertainty over synthesis.

## Scenario-class policy

The first implementation should treat **scenario classes as first-class review objects** and keep them separate from the raw feature list.

### What should count as scenario classes in `0.1`

- `recommended_default`
- `minimal_supported`
- `backend_choice_required`
- `docs_only`
- `integration_heavy`
- `board_only`
- `manual_review_required`
- `deprecated_scenario`

### What should *not* be encoded as scenario classes in `0.1`

- “all features enabled” as a fake scenario class
- “whatever docs.rs shows” as a default scenario
- “it compiles in one CI job” as proof a scenario is recommended
- “there are features for it” as proof a scenario is supported

The scenario-class policy should be versioned and diffable.
If a maintainer cannot explain why a scenario is `recommended_default`, it should fall back to `minimal_supported` or `manual_review_required`.

## Origin policy

The first implementation should treat **fact provenance** as explicit review material.
A good `0.1` should model origins such as:

- `manifest_import`
- `docsrs_metadata_import`
- `observed_build`
- `observed_test`
- `observed_doc_build`
- `maintainer_declared`
- `external_doc_reference`
- `manual_review_required`

with optional notes about:

- command lines,
- target triples,
- profile/runtime/backend assumptions,
- env variables intentionally relied on,
- and why an origin is only partial.

If a scenario fact only exists in docs.rs metadata or in README prose, the receipt should say so.
`0.1` should prefer “we imported this from docs.rs metadata only” over pretending it was broadly observed.

## Matrix-fidelity policy

The first implementation should treat **coverage completeness** as a first-class review object.
A good `0.1` should model:

- `fully_observed`
- `sampled`
- `docs_only`
- `declared_not_observed`
- `workspace_only`
- `board_only`
- `manual_review_required`

with explicit matrix dimensions such as:

- features,
- targets,
- runtimes/backends,
- profile/doc mode,
- and example/bin/test surfaces.

The point is not to execute every powerset.
The point is to make it obvious which parts of the support story were *actually* checked.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **minimal default library**
   - honest default features
   - smallest supported dependency snippet
2. **backend/runtime choice crate**
   - exactly-one or best-one backend guidance
   - conflict classification for technically possible but discouraged combos
3. **`no_std` / embedded-adjacent crate**
   - explicit `alloc` / target / board-only boundaries
   - docs/examples honesty when host-only examples exist
4. **docs.rs-distorted crate**
   - docs metadata or `cfg(docsrs)` makes the docs surface diverge from ordinary builds
5. **integration-heavy workspace crate**
   - official recipe spans multiple members, env files, or `required-features`-gated examples

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump to a fully automated workflow at once.

### Stage 1 — import and annotate
- generate a starter pack
- let maintainers name real scenarios and mark the default

### Stage 2 — local checks
- verify recipes, build/doc/test paths, and obvious conflict classes
- keep docs.rs and target drift explicit

### Stage 3 — release diffs
- compare current release versus previous release
- make setup regressions visible

### Stage 4 — optional adapters
- import `cargo-hack`, feature-doc hints, and workspace-specific helpers
- remain adapter-first, not replacement-first

### Stage 5 — docs/review export
- stable summary and bundle output for docs portals, release review, and support threads

## What should wait until later

Leave these for later unless `0.1` proves cramped without them:

- full Cargo config-precedence explanation
- exhaustive feature-powerset execution
- hosted scenario registries
- project template generation
- IDE/editor integrations
- organization-wide policy engines
- automated scraping of every README in the ecosystem

## Good failure modes

The crate should fail conservatively.
Preferred failure behavior:

- docs.rs metadata changes default docs surface → `docs_surface_changed`
- backend choice exists but no preferred recipe is named → `backend_choice_not_marked_explicit`
- `no_std` lane builds but examples/tests only cover `std` → `matrix_fidelity_changed`
- example/bin requires features not mentioned in the official recipe → `required_features_changed`
- workspace-only recipe presented as single-crate quickstart → `manual_review_required`

## Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.

- Cargo already exposes features, target tables, `required-features`, and stable metadata surfaces.
- docs.rs already exposes a meaningful build/customization surface and explicitly documents important hosted-vs-local differences.
- RFC 3416 exists because feature documentation, deprecation, and visibility still need more structure.
- `document-features` already keeps feature comments near `Cargo.toml`.
- `cargo-feature-combinations` already runs commands across feature combinations.
- `cargo-hack` already gives a widely used powerset/checking workflow.
- Rust’s vision work still argues that crates need more supportive interfaces.

That combination strengthens the case that the missing value is the **crate-authored scenario / recipe / provenance / fidelity contract above them**, not another attempt to replace them.

## Non-goals for `0.1`

- not a replacement for Cargo
- not a replacement for docs.rs
- not a replacement for `cargo-hack` or feature-powerset tools
- not a replacement for feature-doc renderers
- not a universal workspace deployment orchestrator
- not a promise that every scenario can be executed in CI

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://docs.rs/crate/document-features/latest
- https://docs.rs/cargo-feature-combinations
- https://crates.io/crates/cargo-hack
