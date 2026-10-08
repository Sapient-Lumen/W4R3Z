---
id: P-0488
title: Cargo Minimal-Version Witness Kit — lower-bound receipts, direct-minimal CI bundles, and dependency-floor blame reports
status: idea
domains: [cargo, dependencies, semver, ci, maintenance, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/reference/lints.html
  - https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
  - https://doc.rust-lang.org/cargo/faq.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://crates.io/crates/cargo-minimal-versions
---

# Problem

Rust teams increasingly know that a dependency requirement is not just a loose preference. It is part of the public maintenance contract of a crate.

Cargo now has real substrate for checking lower bounds:

- `-Z minimal-versions` and `-Z direct-minimal-versions` can generate lockfiles at the dependency floor instead of the newest compatible versions,
- Cargo’s own docs say the intended use-case is CI validation of whether `Cargo.toml` really matches the minimum versions a crate uses,
- the Cargo FAQ now documents common lower-bound conflicts for `direct-minimal-versions`,
- and Cargo lints now include `implicit_minimum_version_req`, which helps make minimum version requirements explicit.

That is meaningful progress, but maintainers still do not have a boring workflow for questions like:

- which dependency floor did we actually validate,
- which direct dependency forced a higher floor and why,
- which failures were feature-selection mistakes versus truly wrong lower bounds,
- which exceptions are temporary and owned,
- and how did the lower-bound story change between two releases or two pull requests?

Today the workflow is still improvised:

- maybe turn on `direct-minimal-versions` in one nightly CI job,
- maybe inspect a failing lockfile or solver error,
- maybe hand-edit one dependency version requirement,
- maybe add a note to a PR,
- and maybe lose all of that context before the next release.

The missing crate is not another dependency updater.

The missing crate is a **Cargo minimal-version witness kit**: a crate and cargo-adjacent tool that turn lower-bound validation into a durable **policy, blame report, waiver ledger, and diffable witness bundle**.

# What it provides

- `lower-bound-policy.toml` — declares whether the workflow is `direct_only` or `all_transitive`, which targets/features are in scope, how nightly is pinned, and whether results are advisory or blocking.
- `minimal.lock.snapshot.json` — normalized summary of the lockfile selected under one lower-bound run, with direct dependencies, chosen versions, and feature context.
- `lower-bound-blame.json` — explains which dependency requirement, selected feature, or solver conflict forced each floor.
- `constraint-conflicts.report.json` — classifies failures as `missing_feature`, `version_floor_too_low`, `resolver_conflict`, `duplicate-version-floor_conflict`, `manual_review_required`, or `tooling_gap`.
- `lower-bound-waivers.toml` — explicit exceptions with owner, rationale, expiry, and whether the waiver is temporary, ecosystem-blocked, or intentional.
- `minimal-witness.receipt.json` — records toolchain, Cargo flags, workspace selection, policy, and overall witness verdict.
- `minimal-witness.diff.json` — compares two witnesses and classifies `floor_raised`, `floor_lowered`, `new_waiver`, `waiver_expired`, `conflict_resolved`, and `review_required`.
- `cargo minimal-witness capture` — run one lower-bound validation and emit a witness bundle.
- `cargo minimal-witness blame <dep>` — explain why one dependency floor ended up where it did.
- `cargo minimal-witness diff <old> <new>` — compare two lower-bound runs.
- `*.minwitness.zip` — portable artifact for CI, release review, and dependency-policy discussions.

# What the crate should provide other people

1. **A boring proof artifact** that a crate really checked its stated lower bounds.
2. **A blame surface** for why each direct dependency floor is where it is.
3. **A durable exception ledger** instead of scattered CI comments and tribal knowledge.
4. **A diffable review layer** for dependency-floor drift across releases.
5. **A bridge** between Cargo’s lower-bound substrate and everyday maintainer workflows.

# Persona / who it’s for

- library maintainers publishing reusable crates
- CI and release engineers
- workspace owners trying to keep version requirements honest
- support/reviewers diagnosing lower-bound failures

# Users & user stories

- **Maintainer**: “Prove that our version requirements are not looser than what the code really needs.”
- **Reviewer**: “Show me which dependency floor rose in this PR and whether that was intentional.”
- **CI owner**: “Keep one witness bundle from the nightly lower-bound job instead of a pile of logs.”
- **Support engineer**: “Explain whether this `direct-minimal-versions` failure is a real floor problem or just feature selection mismatch.”

# Prior art (and why it’s insufficient)

- Cargo’s unstable `minimal-versions` and `direct-minimal-versions` flags are exactly the right substrate, but they are raw command behavior, not a stable review artifact.
- Cargo’s new `implicit_minimum_version_req` lint helps make version requirements explicit, but the docs themselves say it does **not** guarantee correctness.
- `cargo-minimal-versions` proves real demand, but it is still a command wrapper rather than a durable blame/waiver/diff workflow.
- The archive already has **P-0036 MSRV Workspace Lab** and **P-0051 Cargo Update Policy**. Those are adjacent but different: MSRV is about the **toolchain floor**, and update policy is about **rolling versions forward safely**. This proposal is about the **truthfulness of dependency lower bounds**.

What remains missing is a **policy + blame + waiver + diff bundle** above Cargo’s lower-bound checks.

# Design goals

1. **Direct-dependency first** — optimize first for `direct-minimal-versions`, because Cargo itself warns that full transitive minimal versions is often too blunt today.
2. **Lower-bound specific** — keep the workflow narrower than generic compatibility or dependency-governance platforms.
3. **Feature-aware** — record feature-selection context so failures are explainable.
4. **Waiver-explicit** — let teams stage adoption without losing intent.
5. **Nightly-honest** — preserve the fact that the witness may depend on unstable Cargo flags.

# MVP surface

- Minimal types: `LowerBoundPolicy`, `MinimalLockSnapshot`, `LowerBoundBlame`, `ConstraintConflictReport`, `LowerBoundWaiver`, `MinimalWitnessReceipt`, `MinimalWitnessDiff`, `MinimalWitnessBundle`
- Minimal functions:
  - `capture_minimal_witness()`
  - `build_lower_bound_blame()`
  - `classify_constraint_conflicts()`
  - `diff_minimal_witnesses()`
  - `write_minimal_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `nightly`
  - `cargo-lints`
  - `markdown`

# Compatibility story

- Works first with nightly Cargo because `direct-minimal-versions` remains unstable.
- Must remain useful even if Cargo later stabilizes a better lower-bound story, because review bundles and waiver ledgers still live above raw resolution behavior.
- Should record whether `implicit_minimum_version_req` or similar lint guidance was available, but must not treat lint results as proof.
- Must stay distinct from MSRV resolution and broader semver/public-API workflows.

# Conformance & fixtures

- One fixture where the stated direct dependency floor is correct.
- One fixture where a newer feature accidentally raises the real floor.
- One fixture with a direct-minimal solver conflict caused by feature/version interactions.
- One fixture with an intentional waiver for an ecosystem-blocked lower bound.
- Goldens for `floor_raised`, `missing_feature`, `resolver_conflict`, `waived`, and `manual_review_required`.

# Path to boring stability

- Stabilize the witness, blame, and waiver schemas before adding many automated fixers.
- Start with capture, blame, diff, and explanation before any manifest rewriting.
- Prefer direct-dependency lower-bound validation first.
- Keep “why did this floor move?” more important than “automatically change my dependency requirement.”

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that run one direct-minimal validation, emit a structured witness with blame per direct dependency, classify conflicts, and export a diffable waiver-aware bundle for CI and release review.

# De-risk plan

1. Start with `direct-minimal-versions` rather than full transitive minimal versions.
2. Keep the first blame model simple: dependency requirement, selected features, and solver conflict class.
3. Validate on one small library crate and one multi-feature workspace.
4. Treat automatic requirement rewriting as out of scope until the witness vocabulary feels trustworthy.

# Non-goals

- Not a dependency updater.
- Not a replacement for Cargo’s resolver.
- Not an MSRV tool.
- Not a promise that one successful lower-bound run proves every downstream combination is safe.

# Architecture & API sketch

```rust
pub struct MinimalWitnessReceipt {
    pub cargo_version: String,
    pub policy_mode: String,
    pub direct_dependencies: Vec<String>,
    pub verdict: String,
}

pub fn capture_minimal_witness(root: &Path, policy: &LowerBoundPolicy) -> Result<MinimalWitnessReceipt>;
pub fn build_lower_bound_blame(receipt: &MinimalWitnessReceipt) -> Result<LowerBoundBlame>;
pub fn diff_minimal_witnesses(old: &MinimalWitnessReceipt, new: &MinimalWitnessReceipt) -> MinimalWitnessDiff;
```

Bundle draft: `lower-bound-policy.toml`, `minimal.lock.snapshot.json`, `lower-bound-blame.json`, `constraint-conflicts.report.json`, `lower-bound-waivers.toml`, `minimal-witness.receipt.json`, `minimal-witness.diff.json`, `notes.md`.

# Security / safety model

- Treat manifests, lockfiles, and solver output as untrusted input.
- Record exact nightly/toolchain provenance for any witness bundle.
- Never silently rewrite dependency requirements.
- Support redaction of private registry URLs or internal package names in exported bundles.

# Maintenance & governance plan

- Track Cargo lower-bound work, `direct-minimal-versions`, and Cargo-lint evolution closely.
- Keep schemas compact and versioned.
- Maintain fixtures for version-floor drift, feature mismatches, and waiver expiration.
- Publish guidance on advisory versus blocking lower-bound CI modes.

# Milestones

## 0.1
- capture witness
- lower-bound blame report
- diffable receipt

## 0.2
- waiver ledger
- conflict classification improvements
- CI bundle export

## 1.0
- stable witness schema
- curated lower-bound fixture corpus
- downstream adapters for release-review workflows

# Open questions

- What is the smallest blame vocabulary that still explains real direct-minimal failures?
- How much feature exploration should the MVP attempt before it stops being predictable?
- Which lower-bound failures deserve automatic suggestions versus manual review only?

# Sources

- Cargo unstable features (`minimal-versions`, `direct-minimal-versions`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo lints (`implicit_minimum_version_req`): https://doc.rust-lang.org/cargo/reference/lints.html
- Cargo dependency version requirements: https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- Cargo FAQ (`direct-minimal-versions` conflicts): https://doc.rust-lang.org/cargo/faq.html
- Cargo changelog (resolver v3, cargo lints): https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-minimal-versions`: https://crates.io/crates/cargo-minimal-versions
