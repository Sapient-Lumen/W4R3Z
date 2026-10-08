---
id: P-0516
title: Crate Configuration Scenario Pack Kit — checked feature/profile/env recipes, scenario receipts, and config diffs for library authors
status: idea
domains: [crates, cargo, configuration, features, docsrs, supportiveness, adoption]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/cargo/reference/features.html
  - https://doc.rust-lang.org/cargo/reference/semver.html
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://doc.rust-lang.org/cargo/commands/cargo-build.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/resolver.html
  - https://docs.rs/about/metadata
  - https://docs.rs/about/builds
  - https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
  - https://rust-lang.github.io/rfcs/3416-feature-metadata.html
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  - https://docs.rs/crate/cargo-hack/latest
  - https://docs.rs/crate/document-features/latest
  - https://docs.rs/cargo-feature-combinations
---

# Problem

The archive now has much better answers for:

- **which crate to choose**,
- **what a crate claims to support**,
- **which shared interop profile it fits**,
- **what guidance it gives before failure**,
- **what it hands off after runtime failure**,
- **how a downstream user should upgrade between releases**,
- and **how a crate helps people leave it**.

But it still has a conspicuous gap between **selection** and **failure**:

- what a chosen crate hands other people when they ask **“which feature/profile/env recipe should I actually use for my scenario?”**

That hole matters because current Rust/Cargo substrate already covers only fragments of the story:

1. Cargo features are real public interface and configuration surface area.
2. Cargo’s feature docs explicitly say features should usually be additive, and they warn that mutually exclusive features are hard to manage.
3. The Cargo resolver and `cargo tree --edges features` can explain why features were activated, but they do not tell a receiver which named scenario is the intended one.
4. `cargo build` and `cargo doc` already use `required-features`, which means crates can expose target/example/bin surfaces that exist only for some configurations.
5. Cargo environment variables, docs.rs metadata, and build-script behavior create additional receiver-facing configuration pressure beyond simple feature toggles.
6. The Inside Rust `hint-mostly-unused` writeup says feature flags can help compile times but add user complexity, and it calls feature flags part of a crate’s stable interface.
7. RFC 3416 exists because feature documentation, deprecation, and visibility are still too implicit in today’s manifests.
8. Existing tools like `cargo-hack`, `cargo-feature-combinations`, and `document-features` each solve slices of the problem, but not the joined receiver-facing **scenario contract**.

The missing crate is therefore **not** another generic Cargo config inspector, **not** another feature-powerset runner, and **not** just another feature-doc macro.
It is a **Crate Configuration Scenario Pack Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What are the named, intended scenarios for using this crate?**
2. **Which features, env vars, docs.rs knobs, profiles, and target assumptions belong to each scenario?**
3. **Which scenarios are minimal, production-oriented, docs-only, runtime-specific, or interop-specific?**
4. **Which combinations were actually checked, and under which target/profile/runtime matrices?**
5. **Which options are mutually awkward, deprecated, or only conditionally honest?**
6. **How did the crate’s configuration surface change across releases?**

That is more valuable than leaving users to reconstruct a scenario from README snippets, CI files, docs.rs quirks, and `cargo tree` output.

# What it provides

- `scenario-pack.toml` — versioned declaration of named crate usage scenarios, feature bundles, env knobs, docs.rs assumptions, required-features surfaces, target notes, and manual-review zones.
- `config-surface.receipt.json` — observed receiver-facing configuration facts imported from Cargo manifests, docs.rs metadata, feature docs, target/example declarations, and selected environment-variable surfaces.
- `scenario-profile.report.json` — machine-readable summary of named scenarios such as `minimal`, `std_default`, `no_std_alloc`, `tokio_runtime`, `docsrs_full`, `native_tls`, `rustls`, or other crate-specific lanes.
- `scenario-recipe.manifest.json` — smallest before/after dependency and environment recipes for each named scenario, including manifest snippets and doc/test/build commands.
- `scenario-check.report.json` — verifies whether each advertised scenario actually builds/tests/docs under the stated feature/target/profile matrix.
- `scenario-conflict.report.json` — classifies `mutually_awkward`, `runtime_choice_required`, `docs_only_surface`, `adapter_needed`, `manual_review_required`, and `unsupported_combo` cases.
- `scenario-diff.report.json` — compares two scenario packs and classifies `scenario_added`, `scenario_removed`, `default_changed`, `feature_bundle_changed`, `env_contract_changed`, `required_features_changed`, and `manual_review_boundary_changed`.
- `scenario-class.policy.json` — explicit meaning for which scenarios are `recommended_default`, `minimal_supported`, `backend_choice_required`, `docs_only`, or `manual_review_required`.
- `config-origin.receipt.json` — explicit record of whether important setup facts came from manifests, docs.rs metadata, observed checks, maintainer declarations, or manual-review-only notes.
- `matrix-fidelity.report.json` — explicit classification of how much of the advertised target/runtime/example/docs matrix was actually observed.
- `scenario-notes.summary.md` — compact human-facing explanation derived from the structured artifacts.
- `cargo scenario-pack capture` — capture one crate’s scenario bundle from manifests, docs metadata, fixtures, and selected checks.
- `cargo scenario-pack doctor` — render human-facing warnings about docs.rs/default drift, backend-choice ambiguity, and scenario-coverage gaps.
- `cargo scenario-pack check` — verify the selected scenarios.
- `cargo scenario-pack diff <old> <new>` — compare scenario surfaces across releases.
- `cargo scenario-pack summary` — render a reviewable summary from structured artifacts.

# What the crate should provide other people

1. **A crate-authored scenario contract** above README folklore and below whole-workspace policy tooling.
2. **Named configuration recipes** for common adoption lanes instead of forcing users to infer them from feature names.
3. **Scenario honesty** about defaults, tradeoffs, docs-only knobs, runtime choices, and manual-review boundaries.
4. **Checked scenario receipts** so maintainers can prove which feature/profile/env bundles really work.
5. **A reusable import layer** for pathfinders, docs portals, support bots, template generators, and org dependency policy tooling.
6. **A diffable configuration surface** so maintainers can review whether crate setup became clearer, riskier, or more fragmented over time.
7. **Better support for wide use cases** — from `no_std` embedded builds and WASM, to server runtimes, TLS backend choices, CLI-vs-library modes, docs.rs-friendly surfaces, and feature-heavy workspace crates.

# Persona / who it’s for

- library maintainers whose crates have multiple meaningful feature/profile/env lanes
- framework teams supporting several runtimes or backend adapters
- downstream adopters who want one boring, checked setup recipe for their scenario
- template/tool authors who need stable config artifacts instead of scraped prose
- support/release reviewers who want to diff configuration promises across versions

# Users & user stories

- **App developer**: “Tell me the smallest supported recipe for a Tokio + rustls server, not every feature flag the crate has ever grown.”
- **Embedded maintainer**: “Show me the honest `no_std + alloc` lane and whether docs/tests actually cover it.”
- **Library author**: “Publish one scenario pack so downstream users can choose between runtime backends and see the real tradeoffs.”
- **Docs/site maintainer**: “Import a stable scenario artifact instead of hand-curating feature tables and setup prose.”
- **Release reviewer**: “See whether the default scenario changed or whether a previously checked lane became manual-review-only.”

# Prior art (and why it’s insufficient)

- Cargo features, resolver diagnostics, `cargo tree`, and `cargo metadata` provide raw substrate.
- docs.rs metadata and `#[cfg(docsrs)]` workflows help with documentation builds.
- `cargo-hack` and `cargo-feature-combinations` help check feature combinations.
- `document-features` helps render feature docs from `Cargo.toml`.
- RFC 3416 and related Cargo work improve feature metadata vocabulary.

What remains missing is the joined artifact that says:

- which **named scenarios** the maintainer intends,
- which features/env/profile/docs knobs belong to each one,
- which scenarios were actually checked,
- which choices are mutually awkward or runtime-selecting,
- and where the maintainer still needs the user to decide.

That is a different lane from:

- **P-0509** task-first crate choice,
- **P-0510** producer-side capability contracts,
- **P-0511** shared interop profiles,
- **P-0512** compile-time guidance packs,
- **P-0513** runtime handoff packs,
- **P-0514** release-to-release upgrade packs,
- **P-0515** off-ramp packs,
- generic Cargo config-layer receipts,
- or feature-powerset test tools.

# Design goals

1. **Receiver-facing first** — optimize for downstream setup clarity, not maintainer self-description.
2. **Scenario over flag soup** — name the real use cases instead of just listing toggles.
3. **Join, don’t replace** — import Cargo/doc/build metadata where possible.
4. **Honest conflicts** — allow `runtime_choice_required`, `mutually_awkward`, and `manual_review_required` as first-class outcomes.
5. **Recipe-backed** — the best configuration claim is a small passing recipe, not a prose promise.
6. **Diffability** — support review of how the config surface changes over time.
7. **Wide-scope usefulness** — remain relevant across embedded, server, CLI, WASM, docs-only, native-linking, and feature-heavy crates.
8. **Explicit provenance and fidelity** — preserve where setup facts came from and how much of the claimed matrix was actually observed.

# MVP surface

- Minimal types: `ScenarioPack`, `ConfigSurfaceReceipt`, `ScenarioProfileReport`, `ScenarioRecipeManifest`, `ScenarioCheckReport`, `ScenarioConflictReport`, `ScenarioDiffReport`, `ScenarioNotesSummary`, `ScenarioClassPolicy`, `ConfigOriginReceipt`, `MatrixFidelityReport`
- Minimal functions:
  - `load_scenario_pack()`
  - `capture_config_surface()`
  - `import_docsrs_and_feature_facts()`
  - `validate_scenarios()`
  - `classify_scenario_conflicts()`
  - `capture_config_origins()`
  - `report_matrix_fidelity()`
  - `diff_scenario_bundles()`
  - `render_scenario_summary()`
- Feature flags:
  - `serde`
  - `cargo`
  - `docsrs`
  - `markdown`
  - `command-recipes`

# Compatibility story

- Should work in a stable-first mode by importing facts from manifests, `cargo metadata`, `cargo tree`, docs.rs metadata, and maintainer-authored recipes.
- Must preserve which facts were **imported**, which were **observed**, which were **maintainer-authored**, and which remain **manual-review-only**.
- Should remain useful whether the crate’s choice points are runtime, backend, `std`/`no_std`, target-family, docs-only, or optional-integration driven.
- Must remain honest when a crate only has one real supported scenario and many theoretical combinations.
- Should be importable by crate-selection tools without pretending a chosen scenario is universally best for every project.

# 0.1 scenario families

1. `minimal_default`
   - captures the smallest honest buildable lane for ordinary adopters
   - records default features, minimal recipe, and excluded optional integrations
2. `no_std_or_embedded`
   - captures `no_std`, `alloc`, or target-constrained support when relevant
   - records missing tests/docs coverage and manual-review boundaries honestly
3. `runtime_or_backend_choice`
   - records choices such as `tokio` vs `async-std`, `rustls` vs `native-tls`, or pure-Rust vs system-backend lanes
   - keeps “pick one” or “can coexist” semantics explicit
4. `docs_surface`
   - records docs.rs feature assumptions, `cfg(docsrs)` posture, and whether docs-only surfaces differ materially from ordinary builds
5. `integration_heavy_workspace`
   - reserved for crates whose public scenario surface only makes sense across workspace members or large optional sets
6. `backend_choice_required`
   - records technically buildable but policy-sensitive backend/runtime combinations where the maintainer still wants a single recommended recipe

# Conformance & fixtures

- one `minimal_default` fixture with a checked dependency snippet and command recipe
- one `no_std_or_embedded` fixture with explicit coverage gaps and target notes
- one `runtime_or_backend_choice` fixture with mutually awkward backend lanes
- one `docs_surface` fixture with docs.rs metadata and cfg assumptions
- goldens for `default_honest`, `runtime_choice_required`, `mutually_awkward`, `docs_only_surface`, `manual_review_required`, `unsupported_combo`, and `docsrs_surface_exceeds_default_build`

# Path to boring stability

- Stabilize the pack/check/diff schemas before adding editor or registry integrations.
- Start with import + recipe verification rather than trying to solve all Cargo configuration provenance.
- Keep the first scenario vocabulary small and sharp.
- Treat “one honest scenario only” as a valid outcome.
- Add deeper build-script or workspace adapters only after maintainers trust the artifact vocabulary.

# Why this could matter

This is the crate that would let maintainers say:

- “Here are the real scenarios we intend, not just the full list of toggles.”
- “Here is the smallest recipe for each one.”
- “Here is whether the docs surface differs from normal builds.”
- “Here is where a runtime/backend choice is required.”
- “Here is which scenarios we actually checked and where manual review still begins.”

That is the boring supportiveness layer missing between “the crate exists” and “good luck assembling the right configuration.”

# Why now

1. The official Rust vision work now names supportive crate interfaces directly.
2. The survey still says docs and code are the main learning surfaces, so setup guidance should not be left to scattered prose.
3. Cargo’s feature/config/docs substrate keeps growing, which raises the value of a joined receiver-facing artifact above raw knobs.
4. Feature flags remain a stable interface and a real source of user complexity.
5. Existing tools already cover documentation and feature-matrix testing slices, which makes the missing value sharper rather than more speculative.

# Sharp edges / open questions

- What is the smallest scenario vocabulary that works across crates without turning into a fake standard?
- How should a scenario pack represent “these features can coexist technically, but we only recommend one backend at a time”?
- How much environment-variable surface should be imported by default before redaction concerns dominate?
- How should docs.rs-only surfaces be presented without misleading users about ordinary builds?
- When should a crate publish many named scenarios versus one honest default plus optional appendix lanes?

# Suggested 0.1 deliverable

A crate and cargo subcommand that load one `scenario-pack.toml`, import Cargo/docs.rs feature facts, validate a few named recipes, and emit:

- one `config-surface.receipt.json`,
- one `scenario-profile.report.json`,
- one `scenario-recipe.manifest.json`,
- one `scenario-check.report.json`,
- one `scenario-conflict.report.json`,
- one `scenario-diff.report.json`,
- and one short `scenario-notes.summary.md`.

That would already be enough to prove the lane is real.

# Adoption plan

## 0.1
- schema + recipe verification
- feature/docs.rs/env fact import
- compact summary generation
- docs-site friendly scenario rendering

## 0.2
- target/profile matrix expansion
- backend-choice classification
- pathfinder import support
- org-policy hooks for scenario review

## 0.3
- richer workspace scenario capture
- editor/template integrations
- cross-release scenario regression review
- deeper import of feature-metadata once stabilized
