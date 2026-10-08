---
id: P-0507
title: Cargo Fix Campaign Kit — target-batch plans, lint-selection ledgers, and per-pass receipts for Rust lint-fix orchestration
status: idea
domains: [cargo, linting, edition, diagnostics, maintenance, ci, release-engineering]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  - https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  - https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://doc.rust-lang.org/cargo/commands/cargo-check.html
---

# Problem

`cargo fix` is one of Rust’s most important “boring maintenance” tools.

Official docs are very clear about the substrate:

- `cargo fix` applies rustc suggestions to source code,
- it works by running the equivalent of `cargo check`,
- it may run multiple times until no new warnings appear,
- and edition migration often requires multiple configurations, targets, or feature sets to be checked separately.

That is already useful — but it leaves a broad missing layer above the raw mechanism.

The 2025 GSoC work made that gap much more concrete.
The Rust project’s own write-up says today’s architecture is limited because:

- it can be slow,
- it only applies a subset of possible lints,
- it does not make lint selection easy,
- and the existing design uses a special rustc-proxy mode with a cross-process lock that limits interactivity and coordination.

The alternative `cargo-fixit` prototype moved orchestration to the top level:

- spawn `cargo check` in a loop,
- decide which build targets are safe to fix in a pass,
- apply suggestions batch by batch,
- and open the door to interactive selection.

That is a big signal.
The missing crate is **not** another codemod engine.
The missing crate is **not** an edition-specific assistant alone.
The missing crate is a **Cargo Fix Campaign Kit**: a crate and cargo-adjacent tool that plans and records *which* lints to fix, *which* targets/packages to batch together, *which* passes succeeded or backed out, and *what* still needs human review.

# Main judgment

This is worthy because it solves a general Rust maintenance seam that appears in:

- edition migrations,
- new-lint adoption,
- future-incompat cleanup,
- workspace hygiene sweeps,
- and reviewer-friendly “apply automation, then inspect what changed” workflows.

The missing value is not smarter rewriting by itself.
The missing value is **orchestration with receipts**.

# What it provides

- `fix-campaign.toml` — declares workspace scope, target/profile/feature matrix, lint groups or explicit lint allowlist, preview-versus-apply mode, pass budget, and review policy.
- `lint-selection.ledger.json` — records candidate lints, selected lints, skipped lints, why they were selected, and whether they came from edition compatibility, future-incompat cleanup, or general warnings.
- `target-batches.plan.json` — groups targets or packages into safe fix passes and records why they can or cannot be fixed together.
- `fix-pass.receipt.json` — captures one pass: commands run, targets included, edits applied, suggestions skipped, verification result, rollback status, and caveats.
- `manual-review.queue.json` — locations that still need human review because of macros, generated code, conflicting suggestions, or failed verification.
- `fix-preview.diff` — reviewable preview of edits for one pass or the whole campaign.
- `fix-campaign.diff.json` — compare two campaign bundles and classify `lint_scope_changed`, `target_batch_changed`, `pass_succeeded`, `pass_backed_out`, `manual_review_grew`, and `manual_review_shrank`.
- `cargo fix-campaign plan` — build the lint + target batching plan.
- `cargo fix-campaign rehearse` — run preview passes and emit receipts without leaving final edits applied.
- `cargo fix-campaign apply` — apply selected passes with verification.
- `cargo fix-campaign resume` — continue a partially completed campaign from saved receipts.
- `*.fixcampaign.zip` — portable artifact for PRs, release prep, and CI handoff.

# What the crate should provide other people

1. **A boring fix plan** instead of “rerun `cargo fix` with random flags until it settles”.
2. **A lint-selection ledger** that explains what automation was allowed to touch.
3. **A target-batch plan** for workspaces, multi-target code, and multi-feature migrations.
4. **A per-pass receipt** that says what changed, what got backed out, and why.
5. **A manual-review queue** so automation boundaries are obvious.
6. **A reusable campaign artifact** for edition upgrades, lint adoption, and cleanup drives.

# Persona / who it’s for

- workspace maintainers
- release engineers
- CI owners running maintenance sweeps
- library authors adopting new lints over time
- teams preparing edition migrations or future-incompat cleanup

# Users & user stories

- **Workspace maintainer**: “Tell me which bins/tests/examples can be fixed together and which ones need separate passes.”
- **Reviewer**: “Show me the exact diff and receipt for each automated pass instead of one giant surprise commit.”
- **CI owner**: “Run a rehearse-only campaign in CI and fail only when manual review or rollback conditions remain.”
- **Edition migration owner**: “Use the same orchestration substrate for `cargo fix --edition`, but keep edition-specific evidence separate.”
- **Lint champion**: “Adopt a new lint group gradually and keep a ledger of what we intentionally skipped.”

# Prior art (and why it’s insufficient)

- `cargo fix` is the core substrate, but it is intentionally a direct command rather than a planning and receipt system.
- The Edition Guide explains how `cargo fix --edition` works and why multiple configurations may need separate runs, but that is process guidance, not a reusable campaign artifact.
- The `cargo-fixit` prototype proves a top-level orchestration design is plausible, but it is not yet a stable crate ecosystem contract.
- The archive already has **P-0461 Edition Drift Witness Kit** for **edition-specific rehearsal bundles**.
- The archive already has **P-0478 Cargo Future-Incompat Triage Kit** for **owner/waiver/upgrade-path ledgers**.
- The archive already has **P-0432 Cargo Plumbing Interop Kit** for **phase capture and blocker-aware Cargo receipts**.

What remains missing is the **generic fix orchestration layer** above `cargo check` / `cargo fix` and below edition-specific or warning-specific policy crates.

# Design goals

1. **Campaign-first** — treat lint fixing as a planned sequence of reviewable passes.
2. **Selection-explicit** — which lints are in or out must be first-class data.
3. **Batch-aware** — targets, features, and workspace packages should be groupable and explainable.
4. **Rollback-honest** — failed verification or backed-out edits must be preserved as artifacts.
5. **Review-friendly** — optimize for PR review and maintenance meetings, not only terminal UX.
6. **Substrate-friendly** — reuse Cargo and rustfix behavior rather than reimplementing rewriting logic.

# MVP surface

- Minimal types: `FixCampaign`, `LintSelectionLedger`, `TargetBatchPlan`, `FixPassReceipt`, `ManualReviewQueue`, `FixCampaignDiff`, `FixCampaignBundle`
- Minimal functions:
  - `plan_fix_campaign()`
  - `select_lints()`
  - `batch_targets_for_fixing()`
  - `run_fix_pass()`
  - `verify_fix_pass()`
  - `diff_fix_campaigns()`
- Feature flags:
  - `cargo`
  - `rustfix`
  - `serde`
  - `edition`
  - `ci`

# Compatibility story

- Works above stable `cargo fix` first.
- Should optionally learn from `cargo-fixit`-style orchestration without depending on that prototype becoming the official implementation.
- Must remain useful when campaigns require multiple features or targets because the official edition guidance says that is normal.
- Should compose with edition witness and future-incompat triage bundles rather than replacing them.

# Conformance & fixtures

- One fixture for a Rust 2021 → 2024 migration requiring multiple targets or feature sets.
- One fixture for partial lint adoption where only a selected lint subset should be touched.
- One fixture where a pass verifies cleanly but leaves macro-generated code in manual review.
- One fixture where a fix pass is backed out after verification failure.
- Goldens for `target_batch_changed`, `pass_backed_out`, `manual_review_needed`, and `lint_scope_changed`.

# Path to boring stability

- Freeze the campaign, batch, and receipt vocabularies before building fancy TUI or editor UX.
- Start with rehearsal and pass receipts before ambitious interactive editing.
- Treat macros and generated sources as explicit boundaries.
- Prefer small conservative lint-selection categories over magic auto-grouping.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that plan a lint-fix campaign for one workspace, select a lint subset, batch targets into reviewable passes, run or rehearse those passes, and emit receipts plus a manual-review queue.

# De-risk plan

1. Start with rehearse-only and preview-diff workflows.
2. Support a small target-batching vocabulary before attempting deep auto-scheduling.
3. Validate first on one edition migration and one ordinary lint-adoption campaign.
4. Keep per-pass rollback and verification data explicit.

# Non-goals

- Not a replacement for `cargo fix`.
- Not a general codemod platform.
- Not a new lint engine.
- Not a promise that all macros or generated code can be fixed automatically.

# Architecture & API sketch

```rust
pub struct FixPassReceipt {
    pub pass_id: String,
    pub selected_lints: Vec<String>,
    pub targets: Vec<String>,
    pub verification_status: String,
    pub rollback_performed: bool,
}

pub fn plan_fix_campaign(root: &Path, cfg: &FixCampaign) -> Result<TargetBatchPlan>;
pub fn select_lints(root: &Path, cfg: &FixCampaign) -> Result<LintSelectionLedger>;
pub fn run_fix_pass(plan: &TargetBatchPlan, pass: &str) -> Result<FixPassReceipt>;
pub fn diff_fix_campaigns(old: &FixCampaignBundle, new: &FixCampaignBundle) -> FixCampaignDiff;
```

Bundle draft: `fix-campaign.toml`, `lint-selection.ledger.json`, `target-batches.plan.json`, `fix-pass.receipt.json`, `manual-review.queue.json`, `fix-preview.diff`, `fix-campaign.diff.json`, `notes.md`.

# Security / safety model

- Never hide whether edits were backed out after failed verification.
- Treat source diffs and paths as potentially sensitive and support redaction.
- Keep lint selection, skipped suggestions, and manual-review boundaries explicit.
- Do not claim semantic correctness beyond the verification actually performed.

# Maintenance & governance plan

- Track Cargo fix behavior and future interface changes.
- Keep the core campaign schema small and policy-light.
- Maintain fixtures for edition, feature-gated, multi-target, and rollback scenarios.
- Publish guidance on composing campaign bundles with edition witness and future-incompat ledgers.

# Milestones

## 0.1
- campaign config
- lint-selection ledger
- target-batch plan
- rehearse and preview diff

## 0.2
- apply mode with per-pass receipts
- resume support
- manual-review queue

## 1.0
- stable bundle schema
- CI/PR integrations
- richer campaign comparison reports

# Open questions

- What is the smallest useful target-batching vocabulary?
- How should lint groups versus explicit lint allowlists interact in mixed campaigns?
- How much interactive selection belongs in the crate before it becomes a UI product?

# Sources

- `cargo fix` command docs: https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Edition Guide advanced migrations: https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo 1.90 development cycle update (`cargo-fixit`): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- GSoC 2025 results (`cargo-fixit` summary): https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- `cargo check` command docs: https://doc.rust-lang.org/cargo/commands/cargo-check.html
