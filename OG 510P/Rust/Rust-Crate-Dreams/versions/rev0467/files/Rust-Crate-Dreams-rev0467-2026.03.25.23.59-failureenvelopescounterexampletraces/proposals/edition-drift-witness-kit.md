---
id: P-0461
title: Edition Drift Witness Kit — cargo-fix rehearsal bundles, lint-ledger receipts, and macro-sensitive migration witnesses for Rust edition upgrades
status: idea
domains: [edition, migration, cargo, compiler, macros, docs, ci, maintenance]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
  - https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  - https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
  - https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/Rust-2024-Edition.html
---

# Problem

Rust editions are one of the language’s great strengths, but the project-goals page itself says organizing an edition can become a fire drill. The official story is intentionally good — `cargo fix --edition`, compatibility lint groups, and the edition guide make migration largely automated — yet real maintainers still hit awkward edges:

- macros and generated code often require extra review,
- large workspaces want to rehearse the migration before changing `Cargo.toml`,
- CI owners want proof of which lints fired and which edits were suggested,
- and library maintainers need a compact way to show “we checked edition drift and here is what still needs humans.”

The missing crate is not another general codemod engine.

The missing crate is an **edition witness layer** that rehearses migration, records compatibility-lint results, and turns edition upgrades into reviewable bundles.

# What it provides

- `edition-plan.toml` — declares source and target edition, workspace scope, lint policy, and rehearse-only versus apply mode.
- `edition.lints.json` — records which edition-compatibility lints fired and in which crates/modules.
- `fix-preview.diff` — a reviewable diff showing what `cargo fix --edition` would change.
- `macro-risk.json` — records modules, macros, generated code, or build-generated sources that likely need human review.
- `edition.receipt.json` — captures toolchain, guide assumptions, migration status, and unresolved items.
- `cargo edition-witness rehearse` — run a dry migration and emit receipts without flipping the edition field.
- `cargo edition-witness diff` — compare two rehearsals or two releases.
- `cargo edition-witness explain` — map findings back to edition-guide topics and lint names.
- `*.editionbundle.zip` — shareable artifact for release planning, team review, or upstream bug reports.

# What the crate should provide other people

1. **A dry-run migration artifact** that is more reviewable than console output.
2. **A lint ledger** that shows exactly which edition-compatibility lints mattered.
3. **A macro-risk receipt** for the parts automation cannot safely settle.
4. **A bridge** between the edition guide’s official process and real multi-crate release planning.
5. **A compact proof-of-work bundle** for maintainers who want to say “we rehearsed the upgrade responsibly.”

# Persona / who it’s for

- maintainers of large workspaces
- library authors who support several toolchain windows
- CI/release engineers
- teams migrating generated code or macro-heavy codebases

# Users & user stories

- **Workspace maintainer**: “Rehearse the next edition upgrade without changing every manifest yet.”
- **Reviewer**: “Show me which of these edits came from compatibility lints and which parts still need human judgment.”
- **CI owner**: “Keep an artifact of what we checked before deciding whether to flip the edition field.”
- **Language contributor**: “Collect real migration witnesses where automation still falls short.”

# Prior art (and why it’s insufficient)

- The edition guide documents the official migration path and advanced migrations.
- `cargo fix --edition` and compatibility lint groups already do valuable work.
- Rust 2024 is now stable and therefore real migration pressure exists, not just planning.
- The project goals explicitly note that editions can still feel like a fire drill organizationally.

What remains missing is a **maintainer-facing rehearsal artifact**: a boring receipt that records what automation did, what it could not do, and where macro/generated-code risk remains.

# Design goals

1. **Rehearsal-first** — dry-run migration should be first-class.
2. **Lint-explicit** — every compatibility lint should become structured evidence.
3. **Macro-aware** — highlight likely human-review zones instead of pretending automation solved them.
4. **Workspace-friendly** — support staged adoption across many crates.
5. **Edition-specific** — stay sharper than a generic codemod platform.

# MVP surface

- Minimal types: `EditionPlan`, `LintLedger`, `MacroRiskReport`, `EditionReceipt`, `EditionDiff`, `EditionBundle`
- Minimal functions:
  - `rehearse_migration()`
  - `collect_lint_ledger()`
  - `summarize_macro_risk()`
  - `diff_receipts()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `rustfix`
  - `rustdoc`
  - `html-report`

# Compatibility story

- Works above the official edition process instead of replacing it.
- Must support “rehearse only” mode on stable toolchains where possible.
- Should remain useful for future editions as long as compatibility lint groups continue to exist.
- Must keep automation boundaries explicit for macros and generated code.

# Conformance & fixtures

- One small crate with automatic identifier rewrites.
- One macro-heavy crate with edition-specific fragment or prelude issues.
- One workspace with staged crate-by-crate adoption.
- Goldens for `lint_fired`, `auto_fix_applied`, `macro_review_needed`, and `manifest_change_pending`.
- Example bundle generated from a Rust 2021 → 2024 rehearsal.

# Path to boring stability

- Stabilize the receipt and lint-ledger schema before fancier dashboards.
- Start with rehearsal and evidence, not automatic manifest flipping.
- Reuse official lints and `cargo fix` behavior instead of re-implementing them.
- Keep macro risk conservative and explainable.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that rehearse one edition migration for a workspace, collect the compatibility-lint ledger plus fix preview diff, and emit an `edition.receipt.json` identifying manual-review hotspots.

# De-risk plan

1. Start with read-only rehearsal, not applying edits automatically.
2. Focus first on Rust 2021 → 2024 transitions.
3. Reuse `cargo fix --edition` and the compatibility lint groups directly.
4. Validate on one macro-heavy workspace before broadening.

# Non-goals

- Not a replacement for `cargo fix --edition`.
- Not a general codemod marketplace.
- Not a promise that macros or generated code can always be migrated automatically.
- Not a guarantee that a successful rehearsal means zero semantic drift.

# Architecture & API sketch

```rust
pub struct EditionReceipt {
    pub from_edition: String,
    pub to_edition: String,
    pub lints_fired: Vec<String>,
    pub macro_review_needed: Vec<String>,
}

pub fn rehearse_migration(plan: &EditionPlan, root: &Path) -> Result<EditionReceipt>;
pub fn collect_lint_ledger(root: &Path) -> Result<LintLedger>;
pub fn summarize_macro_risk(root: &Path) -> Result<MacroRiskReport>;
pub fn write_bundle(bundle: &EditionBundle, out: &Path) -> Result<()>;
```

Bundle draft: `edition-plan.toml`, `edition.lints.json`, `fix-preview.diff`, `macro-risk.json`, `edition.receipt.json`, `notes.md`.

# Security / safety model

- Never silently apply edition changes in rehearse mode.
- Record exact toolchain and lint-group assumptions.
- Keep generated-code and macro uncertainty explicit.
- Support path redaction for exported bundles.

# Maintenance & governance plan

- Track new edition-guide changes and future compatibility lint groups closely.
- Keep the schema edition-agnostic enough for future cycles.
- Maintain a small casebook of macro-heavy and generated-code migrations.
- Document where rehearsals stop and human review begins.

# Milestones

## 0.1
- rehearsal mode
- lint ledger
- fix preview diff

## 0.2
- macro-risk report
- receipt diffing
- bundle export

## 1.0
- stable receipt schema
- CI/release adapters
- public casebook

# Open questions

- Which macro/generated-code heuristics are conservative enough to trust?
- How should staged workspaces represent mixed-edition intermediate states?
- What is the smallest useful “manual review needed” vocabulary?

# Sources

- Transitioning an existing project to a new edition: https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
- Advanced migrations: https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Announcing Rust 1.85.0 and Rust 2024: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Allowed-by-default lints: https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html
- Rust 2024 Edition project goal: https://rust-lang.github.io/rust-project-goals/2024h2/Rust-2024-Edition.html
