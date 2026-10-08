---
id: P-0528
title: Cargo Feature Surface Contract Kit — public feature maps, activation profiles, unification-risk receipts, and conflict-policy witnesses
status: idea
domains: [cargo, crates, features, semver, dx, docs, supportiveness]
last_reviewed: 2026-03-22
evidence:
  - https://doc.rust-lang.org/cargo/reference/features.html
  - https://doc.rust-lang.org/cargo/reference/resolver.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/commands/cargo-tree.html
  - https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html
  - https://docs.rs/about/metadata
  - https://doc.rust-lang.org/beta/releases.html
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://rust-lang.github.io/rfcs/2957-cargo-features2.html
  - https://rust-lang.github.io/rfcs/3143-cargo-weak-namespaced-features.html
  - https://docs.rs/cargo-hakari/latest/cargo_hakari/about/index.html
  - https://github.com/taiki-e/cargo-hack
  - https://docs.rs/cargo-feature-combinations/latest/cargo_feature_combinations/
---

# Problem

Rust already has a lot of Cargo feature substrate, but it still lacks one boring, reviewable answer to a downstream question that comes up constantly:

> “What does enabling this feature *really* mean, which combinations are actually supported, and what unification/default-set traps are still in play?”

Current Cargo and ecosystem signals make that gap unusually concrete.

Cargo’s feature reference already documents several sharp truths:

- default features are convenient but hard to suppress across a graph,
- removing features or optional dependencies is usually not SemVer-compatible,
- optional dependencies create implicit features unless the author uses `dep:`,
- `?`-qualified dependency features exist because feature forwarding should not always auto-enable an optional dependency,
- mutually exclusive features should be avoided if at all possible,
- and no project can realistically test the full exponential space of feature combinations.

The resolver docs make the story sharper still:

- resolver v2 avoids unifying features across some target/build/dev boundaries,
- feature selection can pin the graph to versions that still contain a required feature,
- and minor feature changes can strand dependents on older releases.

The ecosystem also has real tooling:

- `cargo tree -e features` can help explain *why* features were enabled,
- `cargo hack` and `cargo-feature-combinations` can exercise many combinations,
- `cargo hakari` can intentionally unify workspace features for faster builds,
- and RFC 2957 is explicit that `cargo metadata` still does not fully expose the newer resolver story.

That means the missing crate is **not** another feature enumerator, **not** another combo runner, and **not** another workspace-hack generator.
It is a **Cargo Feature Surface Contract Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **Which feature names are part of the public support surface, and which are internal dependency toggles or grouped switches?**
2. **Which named activation profiles are actually supported, tested, or only recipe-level?**
3. **Which feature relationships are cumulative, mutually exclusive, precedence-based, or still manual-review territory?**
4. **Which default-set and resolver/unification behaviors can still surprise downstream users?**
5. **What changed in the crate’s feature-support surface across releases?**

That is more useful than a raw feature list.

# What it provides

- `feature-surface.toml` — maintainer-declared feature classes, named profiles, compatibility notes, and manual-review zones.
- `feature-surface.receipt.json` — normalized view of which features are public, hidden dependency wiring, grouped toggles, defaults, and optional-dependency exposure.
- `activation-profile.report.json` — named support profiles such as `default`, `no_default`, `serde`, `tokio`, `rustls`, `std`, or `minimal_cli`, with status like `observed`, `sampled`, `recipe_only`, or `manual_review_required`.
- `conflict-policy.receipt.json` — explicit statement of whether features compose, are mutually exclusive, select one winner, or must fail fast with `compile_error!`.
- `unification-risk.report.json` — receiver-facing account of where feature unification, resolver-v2 splitting, workspace hacks, build/proc-macro duplication, or default-feature leakage can still alter the effective surface.
- `combination-witness.report.json` — which feature combinations were actually exercised by CI or fixture runs, and which remain intentionally out of scope.
- `feature-surface-diff.report.json` — release-to-release changes such as `public_feature_added`, `public_feature_removed`, `default_set_changed`, `grouping_changed`, `conflict_policy_changed`, `unification_risk_changed`, and `coverage_changed`.
- `resolution-scope.receipt.json` — exact observation scope: selected package(s), resolver version, command family, target/host posture, and feature flags used for the capture.
- `hosted-feature-profile.receipt.json` — records what docs.rs or equivalent hosted docs surface is actually showing users, including `features`, `all-features`, `no-default-features`, and target/default-target choices.
- `feature-support-bundle.manifest.json` — portable review bundle that ties together the contract, observed scope, hosted-doc posture, conflict policy, and unification risk.
- `feature-surface.summary.md` — compact human-facing summary for docs, release notes, and support portals.
- `cargo feature-surface init`
- `cargo feature-surface observe`
- `cargo feature-surface check`
- `cargo feature-surface doctor`
- `cargo feature-surface summary`
- `cargo feature-surface diff <old> <new>`
- `cargo feature-surface pack`

# What the crate should provide other people

1. **A public feature contract** above bare `[features]` syntax.
2. **A feature-class receipt** so hidden `dep:` wiring does not masquerade as supported public switches.
3. **Named activation profiles** so downstream teams can ask for supported *sets* rather than reverse-engineering individual flags.
4. **Conflict-policy truth** so “don’t enable these together” is not left to folklore.
5. **Unification-risk truth** so default leakage, resolver-v2 splits, or workspace unification are visible support boundaries instead of surprising build behavior.
6. **Combination coverage witnesses** so `all-features` success does not masquerade as profile-level support.
7. **Observation-scope honesty** so one workspace/build/docs command is not mistaken for a global support verdict.
8. **Hosted-doc feature-profile truth** so public docs posture stays separate from support meaning.
9. **Portable review bundles** so another engineer can archive one coherent pack instead of scraping Cargo output.

# Persona / who it’s for

- library authors with more than a trivial feature set
- framework authors who forward dependency features but want a smaller public surface
- workspace maintainers balancing `cargo hakari` / feature-unification behavior against support clarity
- downstream teams choosing between `default`, `minimal`, `std`, `serde`, runtime, TLS, or backend profiles
- release reviewers who need to know whether a new release changed feature policy in a support-relevant way

# Prior art (and why it’s insufficient)

- Cargo’s feature reference is the canonical semantics source, but it is not a per-crate support contract.
- `cargo tree -e features` helps explain activation causes, but not whether the resulting surface is part of the crate’s supported contract.
- `cargo hack` and `cargo-feature-combinations` help execute combinations, but they do not publish durable support artifacts about meaning, conflicts, or unification risk.
- `cargo hakari` intentionally unifies workspace features for build speed, but it does not publish a receiver-facing warning about how that can differ from default user activation.
- RFC 2957 explicitly notes that `cargo metadata` does not fully expose the newer feature-resolver story, which makes a higher-level receipt layer more valuable.

What remains missing is a crate-authored workflow that can say:

- which feature names are public policy,
- which are dependency plumbing,
- which combinations are really supported,
- where resolver or workspace behavior can still surprise consumers,
- and how that feature surface changed over time.

# Design goals

1. **Receiver-facing support first** — optimize for the person enabling features, not just the author editing `Cargo.toml`.
2. **Feature-name honesty** — keep public feature names separate from hidden dependency plumbing.
3. **Profile-first support** — let maintainers publish supported combinations instead of pretending every combination is equally meaningful.
4. **Conflict honesty** — exclusive, precedence-based, cumulative, and runtime-selected behavior must not collapse into one fake “feature support” story.
5. **Resolver/unification honesty** — default leakage, target/build/dev splits, and workspace unification must stay reviewable.
6. **Narrow enough to ship** — start with observe/check/diff/summary above existing Cargo tooling rather than trying to replace Cargo resolution.

# MVP surface

- Minimal types: `FeatureSurface`, `FeatureClass`, `ActivationProfile`, `ConflictPolicyReceipt`, `UnificationRiskReport`, `CombinationWitnessReport`, `FeatureSurfaceDiffReport`, `FeatureSurfaceSummary`
- Minimal functions:
  - `load_feature_surface()`
  - `observe_feature_surface()`
  - `check_activation_profiles()`
  - `render_feature_surface_summary()`
  - `diff_feature_surface()`
- Feature flags:
  - `serde`
  - `cargo`
  - `metadata`
  - `markdown`

# 0.1 first-class review objects

## `feature-surface.receipt.json`

Should record at least:

- `public_feature`
- `group_toggle`
- `internal_dep_toggle`
- `default_member`
- `hidden_optional_dependency`
- `manual_review_required`

## `activation-profile.report.json`

Should allow named profiles such as:

- `default`
- `no_default`
- `minimal`
- `serde`
- `tokio`
- `rustls`
- `blocking`
- `manual_review_required`

with support states such as:

- `observed`
- `sampled`
- `recipe_only`
- `manual_review_required`
- `unsupported`

## `conflict-policy.receipt.json`

Should make explicit whether a pair/group is:

- `composes`
- `mutually_exclusive_compile_error`
- `precedence_selects_one`
- `runtime_selectable`
- `manual_review_required`

## `unification-risk.report.json`

Should classify risks such as:

- `default_feature_leakage`
- `resolver_v2_host_target_split`
- `resolver_v2_dev_normal_split`
- `workspace_unification_override`
- `duplicate_builds_with_different_feature_sets`
- `metadata_insufficient_for_full_cause_graph`
- `manual_review_required`

## Additional first-class review objects

### `resolution-scope.receipt.json`

Should record at least:

- subject package/workspace
- resolver version
- command family (`build`, `check`, `test`, `doc`, `metadata`, `tree`)
- selected packages / workspace-wide selection
- target / host posture
- requested feature flags (`features`, `all_features`, `no_default_features`)
- caveats about what this scope does **not** prove

### `hosted-feature-profile.receipt.json`

Should record at least:

- source (`docs_rs`, `local_docs_build`, `manual_review_required`)
- explicit `features` list
- `all-features` and `no-default-features` posture
- default target and target set
- what public page/profile this influences
- why hosted docs posture is not automatically runtime/support posture

### `feature-support-bundle.manifest.json`

Should inventory at least:

- required artifacts
- optional/imported artifacts
- supported named profiles
- manual-review zones
- hosted-doc imports
- sharing posture

# Recommended workspace split

- `feature_surface_model`
  - shared Rust types and schemas
- `feature_surface_observe`
  - import from `Cargo.toml`, `cargo tree -e features`, and optional command receipts
- `feature_surface_check`
  - profile checks, conflict checks, unification-risk checks, and doctor warnings
- `feature_surface_pack`
  - markdown summary, diff output, and zip bundle emission
- `cargo-feature-surface`
  - user-facing cargo subcommand

Optional adapters should remain optional in `0.1`:

- `feature_surface_hack` for `cargo hack` receipts
- `feature_surface_fc` for `cargo-feature-combinations`
- `feature_surface_hakari` for workspace-hack receipts

# Discovery order

1. **Raw manifest and feature facts**
   - `[features]`
   - optional dependencies
   - `dep:` and `?` feature wiring
   - default set
2. **Activation-cause facts**
   - dependency feature forwarding
   - `cargo tree -e features`
   - resolver-v2 split situations
3. **Observed coverage facts**
   - named profile runs
   - combo runner receipts
4. **Conflict and policy facts**
   - compile-time exclusivity guards
   - precedence notes
   - runtime-choice notes
5. **Unification-risk facts**
   - default leakage
   - workspace unification
   - build/dev/target duplication

# Why this could matter

This is the crate that would let maintainers say:

- “These are the public features we actually support.”
- “These dependency toggles are intentionally hidden plumbing.”
- “Here are the named combinations we test and support.”
- “These backend features are exclusive, and here is the policy.”
- “This workspace uses unification tricks for speed, but here is the downstream risk.”

That is a real missing support layer in Rust’s Cargo ecosystem.
