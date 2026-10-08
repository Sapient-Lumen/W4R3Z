## 2026Q1 promotion note
This epic now sits directly under [`design/migration-truth-contract-2026Q1.md`](../design/migration-truth-contract-2026Q1.md).
The repo is no longer treating migration truth as a latent stack only; it is treating it as an explicit frontier for source state, destination intent, edit provenance, compatibility imports, outcome truth, and downstream handoff.

# Epic Proposal: Migration Truth Stack (`cargo migrate` + `migration-pack/v0`)

## One-sentence pitch
Make Rust migrations boring by standardizing a thin review boundary that keeps **source state, destination intent, suggested/applied edits, compatibility/support/docs/downstream evidence, waivers, and final claims** distinct instead of forcing every upgrade to live in CI logs, shell transcripts, and maintainer memory.

## Deliverables
- reference command:
  - `cargo migrate`
- schemas:
  - `migration-brief/v0`
  - `migration-pack/v0`
  - `migration-diff/v0`
  - `migration-handoff/v0`
  - `migration-scope-report/v0`
  - `migration-edit-handoff/v0`
  - `migration-compatibility-handoff/v0`
  - `migration-archaeology-note/v0`
- adapters/importers for:
  - `migration-subject/v0`
  - `migration-intent/v0`
  - `migration-analysis-report/v0`
  - `migration-plan/v0`
  - `migration-run-report/v0`
  - `migration-outcome-report/v0`
  - `migration-waiver/v0`
  - `edit-pack/v0`
  - `api-pack/v0`
  - `support-pack/v0`
  - `doc-pack/v0`
  - downstream testing attachments
  - optional dependency-control / resolution-strategy / rust-version posture imports
- docs:
  - edition-transition guide
  - workspace `rust-version` / toolchain-ratchet guide
  - dependency-upgrade + API/MSRV guide
  - docs/support/downstream import guide
  - release/archeology / migration-diff guide

## Why now (signals)
- The Edition Guide says advanced edition migration is staged and configuration-sensitive, and explicitly says `cargo fix` can only work with one configuration at a time, may need multiple runs, cannot update documentation tests, and may require manual macro or generated-code work.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo’s own `cargo fix` docs say the command applies rustc suggestions and behaves like `cargo check --all-targets` by default, which is useful but much narrower than a full migration program.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Rust 1.85 / Rust 2024 says automatic fixes via `cargo fix` are **very conservative** and should not be treated as a recommendation. That is direct evidence that mechanical edit output and destination semantics must stay separate.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 development-cycle report says the current `cargo fix` architecture makes selectivity and interaction difficult, and the 2025 GSoC results describe `cargo-fixit` as a proof of concept for an alternative architecture that puts the top-level program in charge of what fixes get applied.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s `rust-version` docs say workspaces can support multiple policies and that verification can get complicated because shared dependencies are unified, while rustup already makes directory overrides and committed toolchain selection explicit.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
  https://rust-lang.github.io/rustup/overrides.html
- Rust’s 2026 flagship slate still includes public/private dependencies and SBOM support, and the `cargo-semver-checks` goal says cross-crate items and richer type-aware checking are still active work. That means API-sensitive migrations have increasingly real downstream consumers.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs hosts rustdoc JSON, and the 2025 State of Rust survey says online docs remain the canonical reference while LLM/editor workflows are rising. That makes durable migration evidence for docs/support surfaces more valuable than it used to be.
  https://docs.rs/about/rustdoc-json
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Non-goals
- replacing `cargo fix`, rust-analyzer quick-fixes, rustfix, `cargo update`, `cargo upgrade`, rustup, or `cargo-semver-checks`;
- defining one universal upgrade policy for all Rust projects;
- inventing a scalar “migration health” score;
- pretending green CI is the same thing as a completed migration;
- silently absorbing API, docs, support, or downstream verification into one mega-schema.

## Strategic value
This deserves promotion because it gives the archive a missing **change-program continuity seam**.
With it:
- edition upgrades can be reviewed as explicit source→destination programs rather than shell history;
- workspace toolchain / `rust-version` ratchets can preserve package-specific verification and waiver posture;
- dependency upgrades can import API and MSRV evidence without pretending those are the same thing as edit application;
- docs/support/downstream consequences can attach to the same migration subject that triggered them;
- release notes, support pages, policy review, and later maintainers can import one durable migration pack instead of reconstructing the story from folklore.

The prize is not a smarter fixer.
The prize is a durable record of **what state a project started from, what state it intended to reach, what edits were merely suggested, what evidence was imported, what was actually executed, what remained partial, and what downstream consumers may honestly conclude**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `migration-brief/v0` the canonical declaration of subject class, source state, destination posture, intended consumers, and success bar;
2. import `migration-subject/v0`, `migration-intent/v0`, `migration-analysis-report/v0`, `migration-plan/v0`, `migration-run-report/v0`, `migration-outcome-report/v0`, and optional `migration-waiver/v0` as the canonical core migration lane;
3. import `edit-pack/v0` as the canonical suggested-vs-applied edit lane;
4. import `api-pack/v0`, `support-pack/v0`, `doc-pack/v0`, and downstream testing attachments as the canonical compatibility/support/docs/downstream lane;
5. emit `migration-scope-report/v0`, `migration-edit-handoff/v0`, `migration-compatibility-handoff/v0`, `migration-pack/v0`, `migration-diff/v0`, `migration-handoff/v0`, and `migration-archaeology-note/v0` so release/policy/support/atlas/assistant consumers can reuse migration truth without silently recomputing it.

## Critical design bet
The critical bet is that **migration truth becomes useful before Cargo settles on one final fix architecture or one universal publish-time compatibility gate**.
That means:
- the current edition and `cargo fix` workflow is already enough to anchor explicit source/destination/scope artifacts;
- rustup and `rust-version` are already enough to justify toolchain-policy handoff artifacts;
- rustdoc JSON, semver checking, public/private dependency work, and support/docproof lanes are already enough to justify downstream imports;
- partial or inconclusive migrations are still worth packaging if their uncertainty is preserved honestly.

Without that boundary, every migration remains either too local to reuse or too grandiose to trust.

## Milestones
1. **v0 edition lane**
   - `migration-brief/v0`
   - `migration-scope-report/v0`
   - `migration-pack/v0`
2. **v0.2 toolchain / `rust-version` lane**
   - explicit package/target slice reports
   - waiver-friendly outcome packaging
3. **v0.3 dependency/API lane**
   - `migration-compatibility-handoff/v0`
   - optional dependency-control / resolution-strategy imports
4. **v0.4 docs/support/downstream lane**
   - support/doc/downstream attachments with explicit incompleteness markers
5. **v1 archaeology / consumer handoffs**
   - `migration-diff/v0`
   - `migration-handoff/v0`
   - `migration-archaeology-note/v0`

## Execution order
Use [`design/migration-pilot-program.md`](../design/migration-pilot-program.md) as the stack-level rollout:
1. edition transition truth,
2. workspace toolchain / `rust-version` truth,
3. dependency-upgrade + API/MSRV truth,
4. docs/support/downstream truth,
5. release / archaeology / migration-diff truth.

Use [`proposals/epic-migration-kit.md`](./epic-migration-kit.md), [`proposals/epic-edit-workflow-kit.md`](./epic-edit-workflow-kit.md), [`proposals/epic-public-api-kit.md`](./epic-public-api-kit.md), [`proposals/epic-support-envelope-kit.md`](./epic-support-envelope-kit.md), [`proposals/epic-docproof-kit.md`](./epic-docproof-kit.md), and [`proposals/epic-downstream-testing-kit.md`](./epic-downstream-testing-kit.md) as the leaf-level execution guides beneath it.

## Success metrics
- reviewers can distinguish source state, destination intent, exercised scope, suggested edits, approved/applied changes, imported compatibility evidence, waivers, and final claims without reading CI shell glue;
- edition and toolchain transitions stay reviewable across feature/target/package slices;
- dependency/API-sensitive migrations can attach semver/MSRV/docs/support/downstream evidence without flattening it;
- at least two downstream consumers can import the same migration pack without bespoke scraping;
- the archive gets one explainable migration seam instead of scattered issue comments, green-check folklore, and archaeology-by-guesswork.
