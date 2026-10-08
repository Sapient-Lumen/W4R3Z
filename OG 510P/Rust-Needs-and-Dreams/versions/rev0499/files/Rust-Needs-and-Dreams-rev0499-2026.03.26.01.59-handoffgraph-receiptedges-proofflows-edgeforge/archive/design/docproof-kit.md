# Design: DocProof Kit (`cargo docproof`, `doc-pack/v0`)

## Goal
Define a portable contract for describing Rust documentation surfaces, executable examples, guide-validation plans, and the evidence produced by documentation checks.

This should **not** replace rustdoc, mdBook, docs.rs, `trycmd`, `trybuild`, or future rustdoc/rust-analyzer work.
It should make them compose better and make documentation support claims reviewable.

## References (signals)
- Rust’s 2024 survey results say people learn Rust primarily from official documentation, *The Rust Programming Language* book, and crate source code. That is strong evidence that documentation quality and reliability are ecosystem infrastructure, not just polish.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- rustdoc documentation tests already make API examples executable, which proves the core pattern is right but leaves the broader multi-surface workflow fragmented.
  https://doc.rust-lang.org/rustdoc/documentation-tests.html
- mdBook already provides `mdbook test`, which means long-form guide snippets are executable too, but the resulting status is not normalized with doctests or other doc lanes.
  https://rust-lang.github.io/mdBook/cli/test.html
- docs.rs build metadata and build docs show that features, targets, and docs-specific cfg behavior are part of the published support surface, and docs.rs explicitly recommends CI checks to catch environment drift.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- Cargo/rustdoc unstable docs show that scraped examples are real and increasingly important, but still not a stable universal story.
  https://doc.rust-lang.org/cargo/reference/unstable.html
  https://doc.rust-lang.org/rustdoc/scraped-examples.html
- Rust-for-Linux explicitly said its doctest flow relied on hacky rustdoc integration and needed a stable foundation, which is a strong sign that executable docs are not just a beginner problem.
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- `trycmd` and `trybuild` show that CLI transcripts and compile-fail examples are already valuable point solutions in the ecosystem, but still lack a shared plan/report layer.
  https://docs.rs/trycmd
  https://docs.rs/trybuild

## Core components

### 1) `guide-profile/v0`
Describes a crate or workspace’s documentation surfaces and support assumptions.

Required ideas:
- subject identity (crate/workspace/version/revision)
- documented surfaces (`api-docs`, `readme`, `guide-book`, `examples`, `cli-transcripts`, `compile-fail-teaching`, `hosted-docs`)
- audience tags (`library-user`, `cli-user`, `platform-integrator`, `contributor`, `operator`)
- target / feature / cfg / toolchain assumptions
- docs.rs metadata snapshot when relevant
- docs-only cfgs or doc-generation special cases
- “support level” per surface (`guaranteed`, `best-effort`, `illustrative`, `experimental`)
- source roots / chapter roots / example roots

Design rule: **document the real support envelope, not the marketing copy**.
If a guide only works on Linux or only with `--all-features`, the profile must be able to say so.

### 2) `example-catalog/v0`
Inventories examples and teaching artifacts.

Should support:
- artifact id + source location
- artifact kind (`doctest`, `guide-snippet`, `example-bin`, `cli-transcript`, `compile-fail`, `hidden-setup`, `scraped-example`)
- owning surface (`api-docs`, `book`, `readme`, etc.)
- applicability (target/features/profile/toolchain)
- execution mode (`rustdoc`, `mdbook`, `cargo run`, `trycmd`, `trybuild`, `manual`, `not-executable`)
- provenance (`src/lib.rs`, `README.md`, `book/src/chXX.md`, `tests/cmd/*.toml`, etc.)
- optional linkage back to the public API items or commands the artifact teaches

This is the missing inventory layer between “we have examples somewhere” and “we know what our learning surface actually contains.”

### 3) `doc-check-plan/v0`
Declares an intended documentation-validation run.

Should record:
- subject + selected `guide-profile/v0`
- selected surfaces / example subsets
- validators to run (`rustdoc-doctest`, `mdbook-test`, `docsrs-build`, `trycmd`, `trybuild`, custom adapter)
- target / feature / cfg / environment assumptions
- skip reasons and allowed illustrative-only zones
- artifact retention policy for rendered docs / stderr snapshots / transcript diffs
- optional support assertions (“README install path works”, “all docs.rs targets build”, “CLI quickstart transcript matches current output”)

A good v0 can be generated from conventions, but the plan artifact must stand on its own.

### 4) `doc-check-report/v0`
Records what actually happened.

Should support:
- plan id + profile id
- validator identities and versions
- which surfaces ran
- structured results (`passed`, `failed`, `skipped`, `unsupported`, `illustrative-only`, `infra-failed`)
- failure class (`compile`, `runtime`, `stdout-drift`, `stderr-drift`, `docsrs-env`, `target-mismatch`, `feature-mismatch`, `missing-example`, `manual-step-required`)
- produced attachments (stderr snapshots, transcript diffs, rendered-book warnings, docs.rs logs, scraped-example inventory)
- comparability metadata across toolchain changes
- optional support verdicts per surface

This report is the missing unit for CI diffs, release review, and support-claim auditing.

### 5) `doc-pack/v0`
Bundle containing:
- `guide-profile/v0`
- optional `example-catalog/v0`
- `doc-check-plan/v0`
- optional `doc-check-report/v0`
- optional raw attachments

This is the unit that should travel through CI, release review, hosted-docs validation, and downstream support review.

### 6) `cargo docproof`
Reference UX:
- `cargo docproof doctor`
- `cargo docproof inventory`
- `cargo docproof plan`
- `cargo docproof run`
- `cargo docproof pack`
- `cargo docproof diff`

`cargo docproof` should begin as an explainer / adapter / packer.
It should not try to become a universal docs engine or IDE.

## What the kit should provide to others
- **Public API Kit:** connect API changes to concrete guide/example breakage instead of only surface diffs.
- **Config Set Kit:** let documentation checks reuse explicit target/feature selections instead of hidden doc-only matrices.
- **Release Pipeline Kit:** allow releases to attach “what docs/guides were actually verified” evidence.
- **Build Interop Kit:** expose docs validation as structured build-adjacent work, not opaque scripts.
- **Schema Contract Kit / CLI tools:** attach transcript or compile-fail teaching evidence to user-facing boundary changes.
- **Lifecycle Ledger Kit / Trust Signals Kit:** support claims can reference recent documentation evidence rather than README optimism.

## Non-goals
- Do **not** replace rustdoc, mdBook, docs.rs, `trycmd`, or `trybuild`.
- Do **not** standardize rendered HTML themes or docs hosting infrastructure.
- Do **not** force every snippet to be executable; illustrative-only zones must remain possible, but explicit.
- Do **not** pretend docs validity is target-free or feature-free.
- Do **not** reduce long-form guides to API docs only.

## Overlap boundaries
- **Not Public API Kit:** that kit describes public surface and semver/MSRV evidence; DocProof Kit describes learning surfaces, executable examples, and guide verification.
- **Not Config Set Kit:** that kit selects bounded configurations; DocProof Kit consumes those selections when validating docs.
- **Not Release Pipeline Kit:** that kit packages releases; DocProof Kit contributes support evidence about docs/guides.
- **Not A11yKit:** accessibility/UI semantics stay separate; DocProof Kit only records how guide/example surfaces were checked.
- **Not rustdoc JSON work:** rustdoc JSON and scraped examples are inputs and adapters, not the whole workflow.

See also [`design/docproof-pilot-program.md`](./docproof-pilot-program.md) for the ranked rollout plan. The next credible move is not another docs host, theme, or snapshot harness; it is a staged pilot sequence proving API-docs, CLI-transcript, guide-book, compile-fail-teaching, and release/support consumer lanes.

## Why this could matter
A good DocProof Kit would make Rust documentation feel less like a collection of admirable but disconnected habits.
It would give the ecosystem:
- a durable inventory of what is actually being taught,
- explicit support envelopes for docs surfaces,
- fewer stale quickstarts and drifting CLI transcripts,
- better reuse of docs.rs / rustdoc / mdBook / CLI-test machinery,
- and a way for documentation reliability to plug into the same evidence-first archive pattern as coverage, reproducibility, and release review.
See also [`design/canonical-learning-consumer-pilot-program.md`](./canonical-learning-consumer-pilot-program.md): the next shared stack move above DocProof is an explicit downstream import contract for docs hosts, CI, editors, assistants, and review consumers.
