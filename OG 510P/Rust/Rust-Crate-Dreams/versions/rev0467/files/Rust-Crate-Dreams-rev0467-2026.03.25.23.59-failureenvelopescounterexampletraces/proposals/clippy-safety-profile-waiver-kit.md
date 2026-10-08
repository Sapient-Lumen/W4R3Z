---
id: P-0459
title: Clippy Safety Profile & Waiver Kit — lint-policy authority, checked-scope matrices, and reviewable waiver evidence for safety-critical Rust teams
status: idea
domains: [clippy, lints, cargo, safety, ci, tooling, maintenance, devx, compliance]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://doc.rust-lang.org/cargo/reference/manifest.html
  - https://doc.rust-lang.org/cargo/reference/workspaces.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/stable/clippy/lint_configuration.html
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
---

# Problem

Rust now has enough real lint-policy substrate that teams can start making stronger claims:

- the 2026 flagship goals explicitly call out a home for **safety-critical lints in Clippy**,
- Cargo has first-class manifest lint configuration via `[lints]` and inheritance via `workspace.lints`,
- nightly Cargo has an emerging `[lints.cargo]` surface,
- and Clippy configuration is detailed enough to materially change the meaning of a run (for example `check-private-items`, `check-incompatible-msrv-in-tests`, and test-specific allow/deny knobs).

That is progress, but it creates a new failure mode: teams can now say “we run strict Clippy” while leaving four crucial questions unanswered:

1. **who actually set the policy**,
2. **which packages / targets / features / test-private scopes were actually checked**,
3. **which findings came from stable rustc/Clippy versus nightly Cargo lints**, and
4. **which exceptions were explicit, owned, and time-bounded**.

So the missing crate is not another lint engine.

The missing crate is a **reviewable lint-policy contract layer** above Cargo manifests, Clippy configuration, and CI scripts.

# What it provides

- `lint-policy.toml` — versioned intent file for required lint posture, rollout stage, severity mapping, waiver rules, and expected execution matrix.
- `policy-authority.receipt.json` — records whether each effective lint decision came from `workspace.lints`, package `[lints]`, `clippy.toml`, inline source attributes, or imported review policy.
- `checked-scope.matrix.json` — proves what packages / targets / feature sets / test scopes / private-item scopes / toolchains were actually checked.
- `diagnostic-channel.receipt.json` — records whether a finding came from stable `rustc`, stable `clippy`, nightly `cargo` lints, or another adapter, and whether that source is normative or advisory.
- `waiver-decision.record.json` — explicit exception record with scope, rationale, owner, expiry, and source location.
- `lint-policy-drift.diff.json` — classifies `policy_authority_changed`, `scope_shrunk`, `nightly_channel_added`, `waiver_added`, `waiver_expired`, `finding_reclassified`, and `profile_escalated`.
- `lint-support-bundle.manifest.json` — portable manifest joining the receipts, raw findings, policy file, and notes.
- `cargo clippy-profile capture` — execute a declared profile and emit a bundle.
- `cargo clippy-profile explain` — show why a particular lint fired, where its level came from, and whether a waiver covered it.
- `cargo clippy-profile diff` — compare lint posture between branches, releases, or toolchains.
- `*.lintbundle.zip` — compact artifact for code review, safety review, CI debugging, or downstream customer/auditor handoff.

# What the crate should provide other people

1. **A boring policy-authority answer**
   - people should be able to tell whether a lint level came from workspace policy, package override, Clippy config, inline attributes, or nightly-only Cargo settings.
2. **An honest checked-scope answer**
   - people should be able to tell what was and was not checked: package selection, features, targets, tests, private items, and MSRV-sensitive test code.
3. **A diagnostic-channel answer**
   - people should be able to tell whether a reported issue came from stable compiler/clippy surfaces or from experimental nightly Cargo linting.
4. **A waiver ledger**
   - people should be able to inspect exceptions without hunting through scattered `#[allow]`, CI glue, and comments.
5. **A release-to-release drift answer**
   - people should be able to compare posture changes without reverse-engineering every manifest and config file.

# Persona / who it’s for

- safety-critical or regulated Rust teams
- workspace maintainers trying to standardize lint posture
- release/CI engineers staging stricter policies
- maintainers of foundational crates with explicit unsafe / docs / panic / MSRV posture
- downstream adopters who want evidence instead of “we lint in CI”

# Users & user stories

- **Safety engineer**: “Show me which findings came from stable Clippy and which are nightly Cargo-lint experiments before I accept this as release evidence.”
- **Workspace maintainer**: “Which crates failed to inherit the root lint posture, and was that intentional?”
- **Reviewer**: “Why did this warning disappear — did we fix it, narrow scope, change configuration, or add a waiver?”
- **CI owner**: “Prove that we checked test code, private items, and the promised feature matrix rather than just one green `cargo clippy` job.”

# Prior art (and why it’s insufficient)

- Cargo manifest `[lints]` and `workspace.lints` are real policy knobs.
- Nightly Cargo exposes `[lints.cargo]` behind `-Zcargo-lints`.
- Clippy has a rich configuration surface that changes what counts as a finding.
- The 2026 safety-critical roadmap says Clippy is expected to host safety-critical lint work.

What remains missing is a **portable policy / scope / waiver / channel artifact layer**. Today, teams mostly infer that state by reading manifests, `clippy.toml`, inline `allow` attributes, and CI logs by hand.

# Design goals

1. **Authority-explicit** — every effective lint level should be attributable.
2. **Scope-honest** — results must say what was actually checked, not just what the policy intended.
3. **Channel-explicit** — stable and experimental finding sources must stay distinct.
4. **Waiver-visible** — exceptions must be owned, diffable, and reviewable.
5. **Safety-review-friendly** — artifacts should be small, portable, and boring to inspect.

# MVP surface

- Minimal types: `LintPolicy`, `PolicyAuthorityReceipt`, `CheckedScopeMatrix`, `DiagnosticChannelReceipt`, `WaiverDecisionRecord`, `LintPolicyDrift`, `LintSupportBundle`
- Minimal functions:
  - `load_lint_policy()`
  - `capture_lint_bundle()`
  - `explain_effective_lint()`
  - `diff_lint_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `clippy`
  - `cargo-nightly`
  - `sarif`
  - `markdown`

# Compatibility story

- Works in stable-first mode using Cargo manifest lint configuration plus stable rustc/Clippy results.
- Can optionally ingest nightly Cargo lint findings, but must keep them clearly labeled as experimental.
- Must not assume one `cargo clippy` invocation covers tests, private items, or every workspace member.
- Should remain useful even if Clippy safety-critical lint sets evolve, because the crate’s core value is the reviewable contract layer.

# Conformance & fixtures

- Fixture where root `workspace.lints` forbids `unsafe_code` but one member forgot `[lints] workspace = true`.
- Fixture where `check-private-items = true` changes documentation-safety findings.
- Fixture where `check-incompatible-msrv-in-tests = false` hides test-only MSRV issues.
- Fixture where nightly Cargo-lint findings must remain a separate advisory channel.
- Goldens for `scope_shrunk`, `waiver_added`, `waiver_expired`, `policy_authority_changed`, and `channel_changed`.

# Path to boring stability

- Stabilize the authority / scope / waiver / channel schemas before building dashboards.
- Start with read-only capture and diffing.
- Treat inline source attributes as imported evidence, not as the only source of truth.
- Keep nightly Cargo-lint ingestion optional until the upstream surface settles.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that load one versioned lint policy, compute effective policy authority and checked scope, record stable versus nightly finding channels, and emit one diffable lint support bundle.

# De-risk plan

1. Start with stable rustc/Clippy plus manifest/config capture before handling many lint producers.
2. Keep the first waiver schema strict: scope, owner, rationale, expiry, and source reference.
3. Treat nightly Cargo lints as an adapter, not as the product’s foundation.
4. Validate on one safety-oriented workspace and one large legacy workspace doing staged cleanup.

# Non-goals

- Not a replacement for rustc, Clippy, or Cargo lint engines.
- Not a promise of certification or standards compliance.
- Not a generic policy platform for every Cargo or CI setting.
- Not a requirement that all waivers live outside source code.

# Architecture & API sketch

```rust
pub struct WaiverDecisionRecord {
    pub lint: String,
    pub scope: String,
    pub owner: String,
    pub rationale: String,
    pub expires: Option<String>,
    pub source: String,
}

pub fn load_lint_policy(path: &Path) -> Result<LintPolicy>;
pub fn capture_lint_bundle(root: &Path) -> Result<LintSupportBundle>;
pub fn explain_effective_lint(bundle: &LintSupportBundle, lint: &str) -> Result<String>;
pub fn diff_lint_bundles(old: &LintSupportBundle, new: &LintSupportBundle) -> LintPolicyDrift;
pub fn write_bundle(bundle: &LintSupportBundle, out: &Path) -> Result<()>;
```

Bundle draft: `lint-policy.toml`, `policy-authority.receipt.json`, `checked-scope.matrix.json`, `diagnostic-channel.receipt.json`, `waiver-decision.record.json`, `lint-policy-drift.diff.json`, `notes.md`.

# Security / safety model

- Never silently merge stable and nightly findings into one undifferentiated severity stream.
- Preserve where every effective lint level came from.
- Keep waivers explicit and auditable.
- Support path and crate-name redaction for exported bundles when needed.

# Maintenance & governance plan

- Track Cargo `[lints]`, `workspace.lints`, and `[lints.cargo]` evolution.
- Track Clippy configuration keys that materially change checked scope or finding meaning.
- Keep schemas small and conservative.
- Maintain fixture workspaces that exercise inheritance gaps, scope drift, and waiver expiry.

# Milestones

## 0.1
- policy file
- policy-authority receipt
- checked-scope matrix
- waiver ledger

## 0.2
- diagnostic-channel receipt
- drift diffing
- optional nightly Cargo-lints adapter

## 1.0
- stable bundle schema
- CI/review integrations
- public example profile pack

# Open questions

- What is the smallest checked-scope vocabulary that still catches real blind spots?
- How should inline `allow` / `warn` / `deny` attributes be represented without pretending they are the whole policy?
- Which findings should be allowed to participate in blocking decisions when they come from nightly Cargo lints?

# Sources

- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo manifest `[lints]`: https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo `workspace.lints`: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo unstable `[lints.cargo]`: https://doc.rust-lang.org/cargo/reference/unstable.html
- Clippy configuration docs: https://doc.rust-lang.org/stable/clippy/lint_configuration.html
- Cargo 1.93 development notes: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
