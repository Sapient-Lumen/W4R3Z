# Gap: executable docs and guide verification

## What is missing
Rust has strong documentation primitives, but it still lacks a **shared executable-documentation contract**.

Today there is no standard way to describe, exchange, and diff:
- which documentation surfaces a crate or workspace intends to support,
- which features / targets / audiences those surfaces assume,
- which examples are validated as doctests, mdBook snippets, CLI transcripts, compile-fail examples, or docs.rs builds,
- which examples are merely illustrative and which are support claims,
- and what evidence came back from documentation checks.

That missing layer matters because documentation in Rust is not a side dish.
It is one of the main adoption and maintenance surfaces for libraries, CLIs, frameworks, and platform crates.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/rustdoc/scraped-examples.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://docs.rs/trycmd
- https://docs.rs/trybuild

## The current seam is awkward
The ecosystem has real building blocks:
- rustdoc doctests for API examples,
- mdBook testing for long-form guide snippets,
- docs.rs metadata and `cargo docs-rs`-style CI checks for hosted docs builds,
- unstable scraped examples for example-driven API docs,
- `trycmd` for CLI transcript-style testing,
- `trybuild` for compile-fail and diagnostic expectations.

But each real project still hand-assembles its learning surface out of:
- doc comments,
- book chapters or guides,
- `examples/` folders,
- README snippets,
- docs.rs target/feature metadata,
- ad hoc CLI snapshot tests,
- and CI YAML that only maintainers understand.

The result is not that Rust lacks documentation tools.
The result is that there is no portable way to say:
- “these targets/features are the documented support envelope,”
- “these examples are executable promises,”
- “these guide chapters were actually checked,”
- or “this docs.rs configuration is part of the product surface.”

Sources:
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/rustdoc/scraped-examples.html
- https://docs.rs/trycmd
- https://docs.rs/trybuild

## Why this matters
This gap is bigger than nicer rendered docs.
It affects:
1. **adoption and learning** — the 2025 State of Rust survey says online docs remain the preferred canonical reference even as some learning traffic appears to shift toward LLM tooling and agentic editors;
2. **support claims** — docs.rs target/feature metadata and docs-only cfgs already make documentation builds part of the public support surface;
3. **guide drift** — rustdoc doctests and mdBook tests validate pieces, but there is no shared artifact for “which guide/example surface was actually checked under which assumptions”;
4. **CLI and diagnostic UX** — command examples and compile-fail teaching snippets rely on external harnesses like `trycmd` and `trybuild`, but their results stay local to each repo;
5. **platform enablement** — Rust-for-Linux explicitly called out hacky rustdoc/doctest integration as something that needed a stable foundation, which shows documentation execution is a systems-tooling issue too.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/trycmd
- https://docs.rs/trybuild
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html

## What “good” looks like
A worthy contribution here is **not** “one documentation host,” “one static-site generator,” or “one snapshot-testing framework.”

It is a shared executable-docs boundary:
- one `guide-profile/v0` describing documentation surfaces, intended audiences, target/feature assumptions, and docs.rs/profile settings,
- one `example-catalog/v0` inventorying examples, snippets, transcripts, and compile-fail cases with provenance and applicability,
- one `doc-check-plan/v0` declaring which validators should run against which surfaces,
- one `doc-check-report/v0` recording what passed, failed, was skipped, or was only illustrative,
- and one `doc-pack/v0` bundle for CI, release review, docs hosting, and downstream support promises.

That would let Public API Kit, Config Set Kit, Release Pipeline Kit, docs.rs workflows, mdBook guides, CLI tools, and future rustdoc features talk about the same learning surface instead of scattering the truth across prose and one-off test harnesses.


See also [`design/docproof-pilot-program.md`](../design/docproof-pilot-program.md). The next credible move is a ranked pilot sequence rather than another docs-only helper: API-docs + docs.rs first, CLI transcripts second, guide books third, compile-fail teaching fourth, and release/support consumers fifth.
