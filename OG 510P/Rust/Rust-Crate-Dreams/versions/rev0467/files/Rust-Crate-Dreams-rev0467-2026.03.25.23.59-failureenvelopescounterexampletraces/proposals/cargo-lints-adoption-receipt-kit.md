---
id: P-0473
title: Cargo Lints Adoption Receipt Kit — workspace-lint rollout plans, inheritance matrices, and waiver bundles
status: idea
domains: [cargo, linting, workspaces, ci, policy, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/cargo/reference/manifest.html
  - https://doc.rust-lang.org/cargo/reference/workspaces.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
---

# Problem

Cargo now has meaningful lint-policy substrate:

- the manifest-level `[lints]` table gives packages a first-class place to set lint levels and priorities,
- `workspace.lints` lets workspaces inherit shared lint policy and is respected as of Rust 1.74,
- nightly Cargo has an emerging `[lints.cargo]` surface for Cargo-emitted lints,
- and Cargo’s 1.93 development notes show that workspace-level and dependency-tree linting semantics are still an active design seam.

That is a big improvement over ad-hoc `RUSTFLAGS` folklore.

But ordinary teams still lack a boring answer to questions like:

- which packages are actually inheriting workspace lint policy,
- which lint levels differ across workspace members and why,
- which waivers are temporary, intentional, or overdue,
- how a rollout changes when a lint moves from `allow` to `warn` to `deny` or `forbid`,
- and how nightly Cargo-emitted lints should be integrated into otherwise stable workspace policy.

So the missing crate is not another lint runner.

The missing crate is a **Cargo lints adoption receipt kit**: a small crate and cargo subcommand that turn workspace lint posture into a reviewable rollout artifact.

# What it provides

- `lint-policy.toml` — pins selected tools (`rust`, `clippy`, `rustdoc`, optional `cargo`), rollout stages, expiration rules for waivers, and CI policy.
- `lint-inheritance.matrix.json` — package-by-package matrix showing direct lint settings, inherited workspace settings, priorities, and effective merged levels.
- `lint-findings.report.json` — normalized lint findings grouped by package, target, tool, and rollout profile.
- `lint-waivers.json` — explicit waiver records with rationale, owner, expiry, and whether the waiver is advisory or blocking.
- `lint-rollout.diff.json` — compare two policy states or two runs and classify escalations, new findings, resolved findings, and changed inheritance.
- `cargo lint-adoption capture` — emit one workspace lint posture bundle.
- `cargo lint-adoption diff <old> <new>` — compare workspace lint posture across branches or toolchains.
- `cargo lint-adoption doctor` — flag suspicious inheritance gaps, expired waivers, or nightly/stable mismatch.
- `*.lintbundle.zip` — portable artifact for code review, CI policy gates, or workspace cleanup campaigns.

# What the crate should provide other people

1. **A boring workspace lint-policy receipt** instead of scattered manifest snippets and CI logs.
2. **An explicit inheritance matrix** for package and workspace lint settings.
3. **A safe rollout artifact** for moving from advisory to blocking lint levels.
4. **A structured waiver ledger** with ownership and expiry instead of hidden allowlists.
5. **A bridge** between today’s stable workspace-lints substrate and tomorrow’s Cargo-emitted lint surfaces.

# Persona / who it’s for

- workspace maintainers trying to align lint posture
- CI/release engineers staging lint rollouts
- teams cleaning up legacy crates gradually
- orgs that need auditable exceptions and policy drift review
- tool authors building workspace governance or migration bots

# Users & user stories

- **Workspace maintainer**: “Show me which crates are not actually inheriting the root lint policy.”
- **CI owner**: “Promote this lint from `warn` to `deny`, but keep a receipt of temporary exceptions.”
- **Reviewer**: “Tell me whether this PR changed policy, findings, or just waiver metadata.”
- **Tooling author**: “Consume one stable artifact instead of reverse-engineering manifests and CI output.”

# Prior art (and why it’s insufficient)

- Cargo manifest `[lints]` is a real configuration surface.
- `workspace.lints` gives workspaces inheritance on stable Rust.
- Nightly Cargo already has an emerging `[lints.cargo]` surface.
- The Cargo team’s 1.93 notes show active discussion around workspace-level lint semantics and how lints should apply to inherited dependencies and virtual workspaces.

What remains missing is a **rollout / waiver / inheritance artifact layer**. The raw knobs exist, but teams still do policy review mostly by reading `Cargo.toml` files and CI logs by hand.

# Design goals

1. **Adoption-first** — optimize for staging and reviewing lint policy, not finding new lint categories.
2. **Inheritance-explicit** — effective levels and priorities must be visible package-by-package.
3. **Waiver-visible** — exceptions must be first-class data with expiry and rationale.
4. **Nightly-honest** — optional Cargo-emitted lint support must stay clearly labeled as unstable.
5. **CI-friendly** — one compact artifact should be enough for review and gating.

# MVP surface

- Minimal types: `LintPolicy`, `LintInheritanceMatrix`, `EffectiveLintLevel`, `LintFinding`, `LintWaiver`, `LintRolloutDiff`, `LintBundle`
- Minimal functions:
  - `capture_lint_bundle()`
  - `compute_inheritance_matrix()`
  - `diff_lint_bundles()`
  - `run_lint_doctor()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `clippy`
  - `cargo-nightly`
  - `markdown`

# Compatibility story

- Works in a stable-first mode using manifest/workspace lint configuration plus compiler/clippy results.
- Can optionally ingest nightly Cargo-emitted lints when `-Zcargo-lints` is available.
- Must keep the difference visible between “configured policy”, “observed findings”, and “nightly-only findings”.
- Should remain useful even if Cargo later stabilizes more lint surfaces, because the adoption/waiver/diff bundle still matters.

# Conformance & fixtures

- One fixture workspace where some members inherit root policy and others diverge intentionally.
- One fixture with staged rollout from `warn` to `deny`.
- One fixture with expired waivers and stale package-level overrides.
- One fixture with nightly Cargo-lint findings imported alongside stable rust/clippy findings.
- Goldens for `inherited_policy_gap`, `waiver_expired`, `lint_escalated`, and `nightly_only_finding`.

# Path to boring stability

- Stabilize the inheritance/waiver/diff schema before adding dashboards.
- Start with read-only capture and comparison.
- Keep the first waiver vocabulary small and auditable.
- Treat nightly Cargo-lint integration as an adapter, not as the whole product.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read workspace/package lint configuration, build an effective inheritance matrix, record current findings plus waivers, and emit a diffable rollout bundle.

# De-risk plan

1. Start with config capture and inheritance explanation before handling many lint producers.
2. Keep waiver semantics strict and small: owner, reason, expiry, optional tracking link.
3. Treat nightly Cargo-lint integration as optional until the surface settles.
4. Validate on one large workspace with staged lint cleanup and one small greenfield workspace.

# Non-goals

- Not a replacement for rustc, Clippy, or Cargo lint engines.
- Not a generic policy platform for everything in `Cargo.toml`.
- Not a new SARIF warehouse.
- Not a promise that nightly Cargo lint semantics are stable.

# Architecture & API sketch

```rust
pub struct EffectiveLintLevel {
    pub tool: String,
    pub name: String,
    pub level: String,
    pub source: String,
}

pub fn capture_lint_bundle(root: &Path) -> Result<LintBundle>;
pub fn compute_inheritance_matrix(root: &Path) -> Result<LintInheritanceMatrix>;
pub fn diff_lint_bundles(old: &LintBundle, new: &LintBundle) -> LintRolloutDiff;
pub fn run_lint_doctor(bundle: &LintBundle) -> Vec<String>;
```

Bundle draft: `lint-policy.toml`, `lint-inheritance.matrix.json`, `lint-findings.report.json`, `lint-waivers.json`, `lint-rollout.diff.json`, `notes.md`.

# Security / safety model

- Treat imported lint findings and logs as untrusted input.
- Support path/package redaction for exported bundles.
- Never hide waivers or downgrade them silently.
- Preserve whether a finding came from stable Cargo/rustc/Clippy surfaces or nightly Cargo linting.

# Maintenance & governance plan

- Track Cargo manifest/workspace lint changes and nightly cargo-lints evolution.
- Keep schemas versioned and compact.
- Maintain fixtures for inheritance edge cases, waiver expiry, and staged rollout diffs.
- Publish guidance for orgs integrating the bundle into CI or review bots.

# Milestones

## 0.1
- inheritance matrix
- findings bundle
- waiver ledger

## 0.2
- rollout diffing
- doctor checks
- optional nightly Cargo-lints adapter

## 1.0
- stable bundle schema
- CI/review integrations
- curated workspace corpus

# Open questions

- What is the smallest waiver schema that still works for real teams?
- How should package-level overrides and workspace inheritance be rendered when priorities conflict?
- Which Cargo-emitted lint findings deserve first-class stable categories once the nightly surface matures?

# Sources

- Cargo manifest `[lints]`: https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo `workspace.lints`: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo unstable `[lints.cargo]`: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 development notes: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
