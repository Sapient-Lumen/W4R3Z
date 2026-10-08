# Epic proposal: Migration Kit

## Thesis
Rust already has strong tools for individual parts of change.
The next high-leverage contribution is not another dependency updater, another edition helper, or another autofix wrapper.
It is a **shared migration-program contract** that records:
- the source state,
- the intended destination,
- the configuration slices in scope,
- the evidence gathered before execution,
- the ordered plan,
- what actually happened,
- and the final support/API/docs/downstream claims that the team now stands behind.

That would be a worthy ecosystem contribution because it helps maintainers and teams treat upgrades as reviewable engineering instead of chat-thread choreography.

## Why now
The timing is unusually good:
- Rust 2024 is stable and the official migration path is explicitly staged;
- the Edition Guide still says some migrations need manual work or custom tooling;
- Rust 1.85 says `cargo fix` output is intentionally conservative and not a recommendation;
- Cargo’s own 1.90 cycle says the current `cargo fix` architecture is slow, incomplete, and awkward for selective or interactive fixing;
- the 2025 GSoC work on alternative `cargo fix` architecture confirms active upstream interest in better execution mechanics;
- Cargo’s `rust-version` docs say workspace verification gets complicated when policies differ;
- and rustup already makes committed toolchain selection explicit enough that migration packs can capture it directly.

Sources:
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://rust-lang.github.io/rustup/overrides.html

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `migration-subject/v0`, `migration-intent/v0`, `migration-analysis-report/v0`, `migration-plan/v0`, `migration-run-report/v0`, `migration-outcome-report/v0`, optional `migration-waiver/v0`, and `migration-pack/v0`
2. adapters for `cargo fix`, dependency-upgrade lanes, MSRV/toolchain checks, public-API / semver checks, and rustup/toolchain inputs
3. explicit configuration-scope recording so features / targets / workspace subsets are reviewable
4. CI examples that attach migration packs to PR review and release prep
5. guidance for staged transitions, partial completion, and accepted waivers without forcing one policy

The winning version is boring, adapter-heavy, and honest.
It should make today’s tools compose better rather than pretending to replace them.

## Initial pilots
- one crate moving from edition 2021 to 2024 with explicit feature/target coverage
- one library crate taking a major dependency upgrade and attaching API + semver evidence
- one workspace ratcheting `rust-version` and `rust-toolchain.toml` with package-specific verification
- one project changing support-envelope claims (for example, toolchain floor or target posture) and recording the outcome explicitly

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - distinguish source state, intended destination, executed edits, and final outcome
2. **v0.2 adapters**
   - ingest Cargo/rustup/MSRV/API-diff tool outputs
   - normalize blocker, configuration-coverage, auto-edit, and waiver reporting
3. **v0.3 cross-kit integration**
   - consume Edit Workflow, Public API, Support Envelope, DocProof, and Downstream Testing artifacts
   - support diffs between attempted migrations and completed outcomes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one monorepo or one migration pattern

## Success metrics
- Teams can review upgrades as explicit source→destination migration programs.
- Conservative auto-fixes and deliberate destination choices are no longer conflated.
- Toolchain/MSRV/edition/dependency/support changes can attach durable evidence packs.
- Release notes and support claims can cite structured migration outcomes.
- Repeating or auditing a migration months later no longer depends on maintainer memory.

## Archive fit
This proposal fills a real hole in the concise archive.
The repo is already strong on edit capture, API evidence, support contracts, docs validation, downstream checks, and release evidence.
Migration Kit is the missing **orchestration-and-outcome substrate** that lets those evidence lanes describe one explicit transition instead of staying as disconnected checks.


## Execution posture
- Execute this through the ranked rollout in [`design/migration-pilot-program.md`](../design/migration-pilot-program.md), beginning with edition and workspace toolchain lanes before widening to API/support/docs/downstream and release consumers.
- Treat Migration Kit as the orchestration layer in the broader [`design/migration-truth-stack.md`](../design/migration-truth-stack.md) rather than as a universal auto-upgrade engine.
