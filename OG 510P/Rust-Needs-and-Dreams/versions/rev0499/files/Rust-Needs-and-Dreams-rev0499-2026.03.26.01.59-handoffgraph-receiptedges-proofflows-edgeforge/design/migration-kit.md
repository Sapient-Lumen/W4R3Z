# Design: Migration Kit (`cargo migrate`, `migration-pack/v0`)

## Goal
Define a portable contract for planning, reviewing, executing, and auditing **Rust migration programs**: edition upgrades, toolchain/MSRV ratchets, dependency upgrades, support-envelope changes, public-API-sensitive transitions, and other source→destination moves that affect what a crate or workspace claims to support.

This should **not** replace `cargo fix`, `cargo update`, `cargo upgrade`, `cargo msrv`, `cargo public-api`, `cargo semver-checks`, rustup, or future Cargo-native upgrade features.
It should make them compose into one reviewable change program.

## Why this needs a sharper design now
- The Rust Edition Guide already describes edition migration as a staged workflow: run `cargo fix --edition`, update `Cargo.toml`, then test and iterate. That is strong evidence that migration is already a multi-step program, not a single command.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- The guide also says `cargo fix` may need multiple passes, only works on one configuration at a time, and may require manual help for macros or other edge cases. That means configuration scope and incomplete automation are part of migration truth.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Rust 1.85 / Rust 2024 explicitly says the output of `cargo fix` is conservative and “should not be considered a recommendation”. That is a crucial design boundary: auto-applied edits are not the same thing as intended destination semantics.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 development report and the 2025 GSoC results both say `cargo fix` is slow, only covers a subset of lints, and is hard to make selective or interactive because of its current architecture. That is strong evidence the ecosystem needs a durable orchestration/evidence layer above whichever edit architecture wins.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s `rust-version` docs say workspaces can have multiple Rust-version policies and that verifying them can get complicated. That means toolchain/MSRV migrations are not just local manifest edits.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- rustup already makes toolchain overrides and committed `rust-toolchain.toml` files first-class. That means migration plans can and should record toolchain-selection truth explicitly.
  https://rust-lang.github.io/rustup/overrides.html

## Core components

### 1) `migration-subject/v0`
Declares what is being migrated.

Required ideas:
- subject identity (crate/workspace/revision)
- current source state (`edition`, `rust-version`, toolchain pin, dependency posture, support envelope)
- package / target / feature / profile slices in scope
- related repositories or downstream sets when relevant
- authoritative source references (`Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, CI lane ids)

Design rule: **migration review starts from an explicit baseline**.
If the starting state is vague, every later claim becomes harder to audit.

### 2) `migration-intent/v0`
Describes the desired destination and why it is being attempted.

Should record:
- source state → destination state
- change kinds (`edition`, `toolchain`, `msrv`, `dependency`, `support`, `api`, `docs`, `policy`)
- motivation (`security`, `compatibility`, `ecosystem-alignment`, `new-language-features`, `maintenance-cost`, `release-readiness`)
- compatibility posture (`strict-preserve`, `conservative-upgrade`, `intentional-break`, `staged-transition`)
- rollout posture (`single-shot`, `branch-staged`, `workspace-staged`, `feature-bridged`, `deprecation-window`)
- approval policy (`maintainer-review`, `manual-audit-required`, `downstream-signoff`, `release-gate-required`)

Design rule: **destination semantics are first-class**.
A migration is not “whatever the tools changed until CI went green”.

### 3) `migration-analysis-report/v0`
Summarizes what preflight analysis discovered before the migration is approved.

Should support normalized summaries or raw attachments from:
- `cargo fix --edition` / lint-harvest passes
- dependency-upgrade analysis (`cargo update`, `cargo upgrade`, lockfile diffs)
- MSRV/toolchain checks
- public-API / semver checks
- Config Set / Resolution Doctor / Support Envelope inputs
- docs / downstream / release-impact checks
- blocker inventory (`manual-edit-required`, `inactive-config-untested`, `macro-break`, `msrv-conflict`, `support-drop`, `downstream-risk`)

This is the missing “what did we learn before choosing a migration program?” artifact.

### 4) `migration-plan/v0`
Declares the intended execution strategy.

Should record:
- selected `migration-subject/v0` + `migration-intent/v0`
- ordered steps with adapters (`cargo-fix`, `cargo-upgrade`, `cargo-update`, `cargo-msrv`, `cargo-api`, `custom-rustfix`, `manual-edit`, `rustup-toolchain-change`)
- chosen package / target / feature / profile slices
- edit policy (`allow-batch-fixes`, `interactive-selection`, `manual-only-for-listed-areas`)
- required evidence from other kits before completion
- rollback / abort conditions
- release-note / support-note / deprecation-note obligations

A good plan is durable after the original CI run and chat context disappear.

### 5) `migration-run-report/v0`
Records what actually happened while executing the plan.

Should support:
- tool identities / versions / toolchains used
- attempted steps, completed steps, skipped steps, deferred steps
- auto-applied edits versus manual edits versus rejected candidate edits
- configuration slices actually exercised
- blockers, waivers, and unresolved follow-up items
- changed files / artifact classes (`Cargo.toml`, `Cargo.lock`, source, docs, CI, toolchain files)
- raw attachments or digests from edit / API / MSRV / downstream / docs checks

Design rule: **execution truth is distinct from intent**.
A finished run may still fall short of the intended destination.

### 6) `migration-outcome-report/v0`
Declares the final supported claim after the run.

Should record:
- final edition / `rust-version` / toolchain posture
- dependency and feature-policy deltas
- API/semver results and whether they were accepted or waived
- support-envelope / docs / downstream / release conclusions
- explicit remaining debt (`follow-up-fixes`, `nightly-only-gap`, `deferred-target`, `future-major-release`)

This report is what release notes, support docs, and future maintainers should cite.

### 7) `migration-waiver/v0`
Optional artifact for intentionally accepted incompleteness.

Examples:
- a target not yet exercised
- a macro-generated region that still needs manual cleanup
- a downstream break intentionally deferred to the next major release
- an MSRV ratchet accepted with a support-window note

### 8) `migration-pack/v0`
Bundle containing:
- `migration-subject/v0`
- `migration-intent/v0`
- optional `migration-analysis-report/v0`
- `migration-plan/v0`
- optional `migration-run-report/v0`
- optional `migration-outcome-report/v0`
- optional `migration-waiver/v0`
- raw attachments from adapter tools

This is the unit that should travel through PR review, CI, release prep, and later archaeology.

### 9) `cargo migrate`
Reference UX:
- `cargo migrate doctor`
- `cargo migrate analyze`
- `cargo migrate plan`
- `cargo migrate run`
- `cargo migrate outcome`
- `cargo migrate pack`
- `cargo migrate diff`

`cargo migrate` should begin as an explainer / adapter / packer.
It should not pretend to be a universal auto-upgrade engine.

## What the kit should provide to others
- **Edit Workflow Kit:** consume candidate-edit, selection, apply, and verify reports without owning the source→destination migration story.
- **Public API Kit:** attach semver consequences to the same migration program instead of a separate ritual.
- **Resolution Doctor Kit / Feature Kit / Config Set Kit:** reuse explicit configuration and dependency reasoning instead of rediscovering it per upgrade.
- **Support Envelope Kit:** let migrations declare when platform/runtime support claims changed.
- **Downstream Testing Kit / DocProof Kit / Release Pipeline Kit:** require evidence before a migration is considered complete.
- **Lifecycle Ledger Kit:** link deprecations, successors, or support-window changes to explicit migration outcomes.

## Non-goals
- Do **not** replace Cargo’s resolver or dependency semantics.
- Do **not** guarantee one-click automatic migrations.
- Do **not** become a generic database or data-migration framework.
- Do **not** flatten edit suggestions, API diffs, MSRV checks, docs checks, and downstream runs into one fake score.
- Do **not** treat auto-generated edits as self-justifying recommendations.

## Overlap boundaries
- **Not Edit Workflow Kit:** that kit owns candidate edit capture, selection, application, and verification mechanics; Migration Kit owns source/destination intent, scope, approvals, orchestration, and final support claims.
- **Not Public API Kit:** that kit owns API/semver evidence; Migration Kit decides when that evidence is required as part of a change program.
- **Not Resolution Doctor Kit:** that kit explains dependency selection and feature activation; Migration Kit consumes those explanations as inputs.
- **Not Config Set Kit:** that kit defines bounded configuration subsets; Migration Kit records which subsets were exercised for a specific transition.
- **Not Release Pipeline Kit:** that kit packages releases; Migration Kit describes the compatibility-sensitive transition leading into or between releases.
- **Not Lifecycle Ledger Kit:** lifecycle declarations remain separate; Migration Kit can justify them but does not replace them.

## Why this could matter
A good Migration Kit would make Rust upgrades feel less like bespoke maintainer folklore and more like reviewable engineering.
It would give the ecosystem:
- explicit source→destination migration claims,
- honest separation between conservative auto-fixes and intended destination semantics,
- reusable evidence across edition, dependency, MSRV, docs, downstream, and release lanes,
- and durable support/outcome records after the original author or CI logs are gone.


## Execution posture
- Treat this kit as the orchestration layer in a broader **Migration Truth Stack** with [`design/migration-truth-stack.md`](./migration-truth-stack.md).
- The next credible move is a ranked pilot program rather than a bigger auto-upgrade wrapper. See [`design/migration-pilot-program.md`](./migration-pilot-program.md).
- Start with edition transitions and workspace toolchain / `rust-version` ratchets before widening to dependency/API, docs/support/downstream, and release/archaeology lanes.

## Pilot-specific success bar
- A maintainer can distinguish conservative tool output from deliberate destination semantics.
- Configuration scope, partial completion, and accepted waivers remain reviewable after the original CI run disappears.
- Public API, support, docs, downstream, and release consumers can import the result without redefining the migration subject.
