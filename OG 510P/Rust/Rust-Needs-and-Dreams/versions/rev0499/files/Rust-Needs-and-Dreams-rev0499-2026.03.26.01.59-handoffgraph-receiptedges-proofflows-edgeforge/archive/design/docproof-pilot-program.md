# Design: DocProof Pilot Program (`cargo docproof pilot`)

## Purpose
Turn DocProof Kit from a good artifact family into a **ranked execution program**.

The archive already has the right conceptual pieces: `guide-profile/v0`, `example-catalog/v0`, `doc-check-plan/v0`, `doc-check-report/v0`, and `doc-pack/v0`.
What it lacked was a concrete statement of **which documentation surfaces should be proven first**, what counts as success, and which consumers should be allowed to rely on the result.

This pilot program answers that gap.

## Why now
The timing is better than it first appears:
- the 2025 State of Rust survey says online docs remain the preferred canonical reference even as some traffic shifts toward LLM tooling and agentic editors;
- Rust’s vision work says crates should be able to provide better diagnostics and guidance, which raises the value of reviewable teaching surfaces rather than prose-only help;
- docs.rs already exposes build metadata that materially shapes the published docs surface (`default-target`, `targets`, `additional-targets`, feature flags, rustdoc args);
- rustdoc doctests and `mdbook test` already prove that executable documentation is a viable pattern today;
- `trybuild` shows compile-fail teaching examples are already treated as part of library UX in real projects.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://docs.rs/about/metadata
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/trybuild

## Ranked rollout

### Pilot 1 — API-docs + docs.rs lane
**Target subject**
A library crate with doctests, examples, and non-trivial docs.rs metadata.

**Why first**
This is the narrowest lane that still reaches a public, ecosystem-visible learning surface.
It proves that documentation support claims are not limited to local `cargo test --doc`, but include docs-host posture and declared target/feature assumptions.

**Required artifacts**
- `guide-profile/v0` with `api-docs` and `hosted-docs` surfaces
- `example-catalog/v0` for doctests and example bins actually taught in docs
- `doc-check-plan/v0` including rustdoc and docs.rs-style assumptions
- `doc-check-report/v0` with pass/fail/skipped/illustrative status

**Minimum success bar**
- docs.rs target/feature assumptions are explicit
- doctests and hosted-doc assumptions are diffable
- the project can say which examples are promises versus illustration

### Pilot 2 — CLI quickstart / transcript lane
**Target subject**
A CLI-oriented crate or workspace with README or guide quickstarts backed by `trycmd`-style transcript testing.

**Why second**
CLI adoption often depends on install/run examples staying correct.
This lane proves DocProof is not only for API documentation.

**Required artifacts**
- `guide-profile/v0` covering `readme`, `cli-transcripts`, and optional hosted docs
- `example-catalog/v0` for transcript cases and shell/environment assumptions
- `doc-check-report/v0` with transcript drift reasons (`stdout-drift`, `stderr-drift`, `manual-step-required`, etc.)

**Minimum success bar**
- quickstarts can be reviewed as support claims rather than screenshots
- transcript failures produce structured reports instead of only local diffs

### Pilot 3 — Guide-book / mdBook lane
**Target subject**
A guide-heavy crate or workspace using mdBook.

**Why third**
This is where documentation starts to behave like a product surface rather than attached comments.
The lane should prove chapter-scoped validation, skip reasons, and feature/target assumptions.

**Required artifacts**
- `guide-profile/v0` including `guide-book`
- `example-catalog/v0` for guide snippets with chapter provenance
- `doc-check-plan/v0` calling out `mdbook test` and any companion validators
- `doc-check-report/v0` preserving chapter-level status and skip reasons

**Minimum success bar**
- guide validation can be scoped by chapter or book
- feature/target assumptions and illustrative-only zones are explicit
- CI or release review can consume a stable report rather than a raw job log

### Pilot 4 — Compile-fail teaching lane
**Target subject**
A macro-heavy or teaching-oriented crate using compile-fail examples (`trybuild`, rustdoc compile_fail, or equivalent).

**Why fourth**
This is the first lane where DocProof must coordinate with Compile Guidance Kit rather than pretending docs and diagnostics are separate worlds.
It should remain a distinct learning-surface lane, but import compile-guidance truth where relevant.

**Required artifacts**
- docproof-side example inventory and report
- optional linkage to `guidance-example-catalog/v0` or `diagnostic-catalog/v0`
- explicit normalization rules for compiler-version noise

**Minimum success bar**
- teaching examples can be reviewed as learning artifacts without flattening them into generic stderr snapshots
- overlap with Compile Guidance stays explicit instead of becoming one mega-schema

### Pilot 5 — Release / support consumer lane
**Target subject**
Any earlier pilot adopted by release review, support review, or atlas-style guidance consumers.

**Why fifth**
The point of DocProof is not only to test docs.
It is to let other ecosystem decisions consume documentation truth honestly.
This lane proves external value.

**Required artifacts**
- attachable `doc-pack/v0`
- explicit consumer notes (release, support envelope, atlas/guide generation, policy intake)
- freshness window or verification timestamp

**Minimum success bar**
- at least one non-doc tool or process imports doc evidence without pretending it generated the canonical truth itself

## Cross-lane invariants
Every pilot must preserve:
1. **surface identity** — API docs, long-form guides, transcripts, compile-fail teaching, and hosted docs are not the same thing;
2. **support level** — `guaranteed`, `best-effort`, `illustrative`, and `experimental` must stay explicit;
3. **environment truth** — features, targets, docs-only cfgs, and external tool assumptions must be recorded;
4. **consumer humility** — editor, assistant, release, and support consumers may import docproof artifacts but must not overwrite maintainer-authored truth;
5. **overlap boundaries** — Compile Guidance Kit owns compile-time guidance semantics; Support Envelope owns wider platform/support claims.

## Scorecard questions
A pilot is stronger when it can answer:
- Which doc surfaces were actually checked?
- Which examples are promises versus illustration?
- Which features/targets/toolchains/docs-host assumptions were in force?
- Which failures were product issues versus infra issues?
- What changed between two versions?
- Which downstream consumer can now rely on this pack?

## Anti-goals
Do not use this pilot program to:
- design a universal docs renderer;
- force every snippet to be executable;
- erase the difference between docs evidence and compile-guidance evidence;
- or hide complexity under one green “docs healthy” badge.

## Relationship to the broader archive
- [`design/docproof-kit.md`](./docproof-kit.md) defines the artifact family.
- [`proposals/epic-docproof-kit.md`](../proposals/epic-docproof-kit.md) argues for the ecosystem contribution.
- [`design/compile-guidance-pilot-program.md`](./compile-guidance-pilot-program.md) is the sibling execution track for crate-authored diagnostics and compile-time guidance.
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md) explains why DocProof + Compile Guidance now belong to one strategic band without being collapsed into one tool.
