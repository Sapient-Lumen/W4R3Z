# Epic proposal: DocProof Kit

## Thesis
Rust already has unusually strong documentation culture and tooling.
The next high-leverage contribution is not another renderer or another style guide.
It is a **shared executable-docs contract** that describes what learning surfaces a project supports, what examples or transcripts are promises, and what evidence came back when those surfaces were checked.

That would be a worthy ecosystem contribution because it helps:
- library maintainers keep API docs and examples honest,
- CLI authors keep quickstarts and transcripts current,
- platform/framework teams publish target-aware guide claims,
- docs.rs workflows become more legible and reviewable,
- and release/support decisions stop depending on vibes about documentation freshness.

## Why now
The timing is unusually good:
- the 2025 State of Rust survey says online docs remain the preferred canonical reference even as some traffic appears to move toward LLM/editor tooling;
- rustdoc doctests and mdBook tests already prove the executable-docs pattern is real;
- docs.rs metadata and CI guidance make documentation builds part of the public support story;
- Rust vision work says crates should provide better diagnostics and guidance, which raises the value of explicit teaching surfaces;
- ecosystem tools like `trycmd` and `trybuild` already cover important teaching modes that are not captured by doctests alone.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://docs.rs/trycmd
- https://docs.rs/trybuild

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `guide-profile/v0`, `example-catalog/v0`, `doc-check-plan/v0`, `doc-check-report/v0`, `doc-pack/v0`
2. validators + diff tooling
3. adapters for rustdoc doctests, mdBook tests, docs.rs builds, `trycmd`, and `trybuild`
4. example profiles for a library crate, a CLI crate, and a guide-heavy workspace
5. CI examples showing how doc evidence attaches to release review

The winning version is boring, adapter-heavy, and honest.
It should make today’s tools more legible rather than pretending to replace them.

## Initial pilots
- one library crate with doctests + examples + docs.rs custom metadata
- one CLI crate with `README.md` or book quickstarts backed by `trycmd`
- one macro or framework crate with compile-fail teaching examples backed by `trybuild`
- one guide-heavy workspace using mdBook plus platform/feature-specific skip reasons

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - include explicit support levels and illustrative-only semantics
2. **v0.2 adapters**
   - ingest rustdoc, mdBook, docs.rs, `trycmd`, and `trybuild` results
   - inventory examples from common repo conventions
3. **v0.3 release/support integration**
   - attach doc evidence to release review and support claims
   - diff documentation support surfaces across revisions
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one monorepo or one docs stack

## Success metrics
- Teams can move docs support claims out of vague prose and into portable artifacts.
- A failing guide or CLI transcript yields a structured report instead of only a local CI log.
- docs.rs metadata, docs-only cfgs, and guide/test assumptions become reviewable support inputs.
- Public API and release changes can link directly to documentation evidence.

## Archive fit
This proposal fills a real hole in the concise archive.
The repo is already strong on build, supply-chain, safety, and execution evidence.
DocProof Kit adds a missing **learning-surface and support-claim substrate** without duplicating Public API Kit, Config Set Kit, Release Pipeline Kit, or A11yKit.


See [`design/docproof-pilot-program.md`](../design/docproof-pilot-program.md) for the ranked rollout that keeps API docs, hosted docs, CLI transcripts, guide books, compile-fail teaching, and downstream consumers distinct instead of collapsing them into one generic “docs pass.”
