# Crate interop-profile product plan — 2026-03-17

This note exists to keep **P-0511 Crate Interop Profile Pack Kit** disciplined.
The archive already decided that the missing value is a **shared ecosystem boundary contract** above individual crate metadata.
This pass answers a narrower question:

> If somebody actually started building **P-0511** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps profile authors, crate maintainers, and downstream adopters publish one reviewable answer to:

- which shared ecosystem profile is actually in view,
- which public traits/types/boundaries are required or forbidden by that profile,
- which adapters or bridge obligations are part of fitting the profile,
- how much evidence is static versus pairwise versus behavioral,
- and where compatibility ends and manual review still begins.

It should **not** try to become a task-ranking engine, a producer-side capability contract, a semver checker, or a full protocol-conformance suite.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream adopters, crate authors, and docs/tool authors, the crate should provide:

1. **Shared interop profiles** so important library boundaries stop living only in README folklore and issue-thread lore.
2. **A profile-class policy** so “baseline building block”, “adapter bridge”, “behavior probe required”, and “manual review required” stop being implicit vibes.
3. **Boundary-obligation receipts** so required public surfaces, forbidden public coupling, adapter requirements, and explicit runtime/body/error expectations become reviewable artifacts.
4. **Static conformance receipts** so a crate can be checked against a profile without pretending that static evidence settles everything.
5. **Pair-compatibility reports** so provider/consumer combinations can be checked at the actual seam instead of only one crate at a time.
6. **Pair-fidelity reports** so teams can see whether a pairwise verdict came from static analysis only, from compile witnesses, from behavioral probes, or from a partial/manual-review lane.
7. **Migration-hazard diffs** so releases that quietly narrow interoperability or add adapter requirements become loud.
8. **A small portable bundle** that pathfinder-style tools, capability contracts, release review, and CI can all import.

For profile authors and maintainers, the crate should provide:

1. a compact profile-pack file that is cheap to review,
2. conservative `manual_review_required` escape hatches instead of fake certainty,
3. one place to join Rustdoc/Cargo facts with tiny compile/probe witnesses,
4. a reusable vocabulary that other support crates can import,
5. and a CI gate for “this crate or this release drifted away from the shared ecosystem boundary we claimed.”

## Recommended `0.1` command surface

### `cargo interop-profile init`
Create a starter `interop-profile-pack.toml` from either:

- a built-in profile catalog entry,
- an imported profile pack,
- or a maintainer-authored profile seed.

The generated pack should stay intentionally narrow.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo interop-profile observe`
Emit one normalized static receipt bundle from the current crate.
This should capture:

- selected profile identity and class,
- required and forbidden public surfaces,
- public runtime/body/error/format coupling,
- adapter obligations,
- and known manual-review zones.

### `cargo interop-profile check --profile <profile>`
Run the local validation pass:

- does the profile pack parse,
- do required surfaces appear in the public boundary,
- do forbidden couplings leak publicly,
- do adapter obligations resolve cleanly,
- and which facts remain inferred-only or manual-review-only?

### `cargo interop-profile pair --profile <profile> --provider <crate> --consumer <crate>`
Run the pairwise seam check.
This should answer:

- whether the provider and consumer meet at the same boundary,
- whether adapters/features are required,
- whether body/error/runtime expectations line up,
- and how much of the verdict is static versus witnessed.

### `cargo interop-profile doctor`
Render human-facing warnings for suspicious situations such as:

- `public_tokio_type_leaks_runtime_neutral_profile`
- `profile_declares_http_boundary_but_public_types_skip_http`
- `service_trait_matches_but_body_or_error_shape_unknown`
- `serde_model_profile_eroded_by_format_specific_public_helpers`
- `adapter_required_but_not_declared`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo interop-profile summary`
Render a short receiver-facing note that answers:

- which shared profile is in play,
- what the profile requires and forbids,
- which adapters or caveats matter,
- how the provider/consumer pair was actually checked,
- and where manual review still begins.

### `cargo interop-profile diff <old> <new>`
Compare two receipts or profile bundles and classify:

- `profile_class_changed`
- `required_surface_added`
- `required_surface_removed`
- `forbidden_coupling_added`
- `adapter_obligation_changed`
- `pair_fidelity_changed`
- `migration_hazard_added`
- `manual_review_boundary_changed`

### `cargo interop-profile pack`
Emit one compact `.interopprofile.zip` bundle for CI artifacts, release review, documentation generation, and downstream handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `interop_profile_model`
  - shared Rust types for profile packs, receipts, reports, and diffs
- `interop_profile_import`
  - manifest/rustdoc/Cargo metadata import logic
- `interop_profile_check`
  - required-surface checks, forbidden-coupling checks, adapter-obligation checks, and doctor warnings
- `interop_profile_probe`
  - compile witnesses and optional behavioral probes for pairs
- `interop_profile_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-interop-profile`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `interop_profile_http`
- `interop_profile_tower`
- `interop_profile_serde`
- `interop_profile_semver`
- `interop_profile_pathfinder_import`

## `0.1` artifact set

The archive already had a good core.
`0.1` should still revolve around:

- `interop-profile-pack.json`
- `static-conformance.receipt.json`
- `behavioral-probe.report.json`
- `pair-compatibility.report.json`
- `migration-hazards.report.json`
- `interop-summary.md`

This pass adds three more important artifacts:

- `profile-class.policy.json` — what `shared_baseline`, `ecosystem_boundary`, `adapter_bridge`, `behavior_probe_required`, `deprecated_profile`, and `manual_review_required` mean and what minimum evidence each class expects.
- `boundary-obligation.receipt.json` — where required surfaces, forbidden couplings, adapter requirements, runtime/body/error expectations, and manual-review caveats came from.
- `pair-fidelity.report.json` — how complete a pairwise verdict really is across static API checks, compile witnesses, behavioral probes, adapter coverage, and manual-review boundaries.

Those files matter because interop stories get vague again if the archive only records a profile and a pass/fail verdict but not:

- what *kind* of profile is being claimed,
- which obligations were really part of fitting that profile,
- and how much of a provider/consumer verdict was actually observed.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Profile-pack facts**
   - profile id/version
   - profile class
   - required surfaces
   - forbidden public coupling
2. **Manifest and graph facts**
   - features
   - dependency edges
   - optional adapter crates
3. **Public API facts**
   - rustdoc JSON
   - compile witnesses
4. **Pairwise seam facts**
   - provider/consumer type alignment
   - feature and adapter resolution
5. **Behavioral probe facts**
   - middleware stacking
   - request/response round-trip or trait-behavior checks
6. **Manual-review zones**
   - runtime-specific caveats
   - format-specific helper leakage
   - body/error semantics that static checks could not fully prove

The importer should prefer visible uncertainty over synthesis.

## Profile-class policy

The first implementation should treat **profile class** as a first-class review object and keep it separate from the raw profile id.

### What should count as profile classes in `0.1`

- `shared_baseline`
- `ecosystem_boundary`
- `adapter_bridge`
- `behavior_probe_required`
- `deprecated_profile`
- `manual_review_required`

### What should *not* count as profile classes in `0.1`

- “popular on crates.io”
- “many crates happen to use it”
- “docs mention it somewhere”
- “one framework supports it”

## Boundary-obligation policy

The first implementation should treat **boundary obligations** as explicit review material.
A good `0.1` should model obligations such as:

- `required_public_surface`
- `forbidden_public_coupling`
- `adapter_feature_required`
- `runtime_coupling_must_be_explicit`
- `body_error_shape_alignment_required`
- `format_specific_helpers_must_stay_internal`
- `manual_review_required`

with origin classes such as:

- `profile_pack_declared`
- `manifest_observed`
- `rustdoc_json_observed`
- `compile_witness_observed`
- `behavior_probe_observed`
- `pair_probe_observed`
- `maintainer_declared`

## Pair-fidelity policy

The first implementation should treat **pairwise confidence** as explicit review material.
A good `0.1` should model fidelity classes such as:

- `static_only`
- `static_plus_pair_build`
- `behaviorally_observed`
- `adapter_assumed`
- `sampled_pair_only`
- `manual_review_required`

The first implementation should **not** flatten all pair verdicts into one simple “compatible / incompatible” bit.

## Built-in profile families worth shipping first

A disciplined `0.1` should stay boring and ship only a few profiles:

1. `async_runtime_neutral_public_api`
   - internal runtime use allowed
   - public runtime lock-in must be explicit
2. `tower_http_service_boundary`
   - boundary built around `tower-service` and `http`
   - body/error caveats stay explicit
3. `serde_data_model_boundary`
   - public model crates stay format-neutral
   - format-specific helpers or transport-specific wrappers stay quarantined or explicit

## Preferred proving grounds

- libraries that use Tokio internally but want runtime-neutral public APIs
- middleware ecosystems built on `tower-service` plus `http`
- model crates trying to stay Serde-friendly without turning into format-specific frameworks
- adapter-heavy ecosystems where compatibility is real but not native
- releases that look semver-compatible while quietly tightening ecosystem lock-in

## Milestones

### `0.1`
- profile-pack schema
- profile-class policy
- boundary-obligation receipts
- static conformance receipts
- pair compatibility reports
- pair fidelity reports
- migration-hazard diffs
- three narrow built-in profiles

### `0.2`
- compile-witness generator
- richer behavioral probes
- markdown summary exporter
- CI action for profile drift

### `1.0`
- stable schemas
- public profile-pack catalog process
- broad fixture corpus across at least six ecosystem lanes
- importer guidance for pathfinder, capability-contract, and docs/support surfaces

## Open questions

- Which shared ecosystem profiles are stable enough to bless without becoming political or bloated?
- How much pairwise probing is enough before the artifact stops being “small and boring”?
- Which body/error/runtime mismatches should be hard incompatibilities versus advisory hazards?
- Should built-in profiles live in the CLI crate, a separate catalog crate, or both?
- What is the cleanest division of labor between shared interop profiles, producer-side capability contracts, and task-first crate selection?

## Sources

- Rust vision-doc post on crate navigation and smoother library interop: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Externally Implementable Items goal: https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- Evolving trait hierarchies goal: https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- `http` crate docs: https://docs.rs/http/latest/http/
- `tower-service` trait docs: https://docs.rs/tower-service/latest/tower_service/trait.Service.html
- `tower` crate overview: https://docs.rs/tower/latest/tower/
- `axum` docs on shared `tower::Service` middleware: https://docs.rs/axum/latest/axum/
- `futures-core::Stream` docs: https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- Serde docs: https://docs.rs/serde/latest/serde/
