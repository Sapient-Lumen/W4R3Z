# Gap: canonical learning, maintainer-authored teaching truth, and bounded derived consumers

## What is missing
Rust has real documentation, diagnostics, examples, hosted docs, and compile-fail teaching primitives, but it still lacks a **boring canonical-learning layer**.

Today teams can separately:
- publish rustdoc API docs,
- ship READMEs and mdBook guides,
- run doctests,
- test book examples,
- maintain compile-fail fixtures,
- and increasingly feed all of that into editors, search tools, and assistants.

What is still missing is the shared layer that answers:
- what explicit learning lanes exist at all,
- what the maintainer-authored learning surface actually is,
- which parts are API docs versus long-form guides versus compile guidance,
- what feature/target/docs-host assumptions shaped those surfaces,
- what was actually validated,
- which downstream consumers are only rendering or summarizing,
- and what portable pack a docs host, CI job, editor, assistant, atlas, or support reviewer should import.

## Why it matters
This is not just a docs-quality problem.

The 2025 State of Rust survey says online docs remain the preferred canonical reference while some learning traffic appears to be shifting toward LLM tooling and editor/agentic workflows.
Rust’s 2025 vision work explicitly recommends expanding Rust’s extensibility to include **better diagnostics and guidance from crates**.
That combination means learning truth is now both a **human reference** problem and a **machine-consumption** problem.

Without a real canonical-learning substrate, projects keep rebuilding the same fragile pattern:
- docs are authored in one place,
- compile guidance lives in stderr fixtures or ad hoc examples,
- docs-host assumptions live in metadata tables,
- CI only checks a subset,
- editor/assistant overlays silently reinterpret everything,
- and nobody can tell what is canonical versus derived.

A worthy contribution here would let Rust learning surfaces become easier to **review, validate, diff, host, summarize, and reuse** without making assistants or docs portals the new source of truth.

## Existing building blocks worth composing
- The 2025 State of Rust survey says online docs remain the preferred canonical reference and also notes rising LLM/editor use.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2025 vision work explicitly recommends “better diagnostics and guidance from crates”.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs lets crates declare docs-build metadata through `[package.metadata.docs.rs]`.
  https://docs.rs/about/metadata
- docs.rs automatically builds crate documentation, exposes docs-specific cfg/env behavior, and documents CI-facing ways to catch docs.rs-specific failures.
  https://docs.rs/about/builds
- docs.rs now builds and hosts rustdoc JSON, which is a structured programmatic documentation surface.
  https://docs.rs/about/rustdoc-json
- rustdoc executes documentation examples as tests and supports `compile_fail`, `no_run`, and edition-tagged doctests.
  https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
- Rust 1.94 also added `#[cfg(doctest)]`, which further sharpens documentation-test-specific surfaces.
  https://doc.rust-lang.org/beta/releases.html
- mdBook has a first-class `test` command and documents CI use for validating Rust examples in books.
  https://rust-lang.github.io/mdBook/cli/test.html
  https://rust-lang.github.io/mdBook/continuous-integration.html
- `trybuild` already provides a serious compile-fail teaching/testing lane.
  https://docs.rs/trybuild

## Why existing tools are not yet the whole answer
Rust already has **docs engines, docs hosts, guide tooling, and compile-fail fixtures**, but not the **shared canonical-learning pack**:
- rustdoc helps you write and test API-adjacent examples;
- docs.rs helps you host and parameterize docs builds;
- mdBook helps you write and test guide books;
- `trybuild` helps you validate compile-fail teaching flows;
- editors and assistants help you surface or summarize learning content.

But teams still have to invent their own answers for:
- learning-surface identity,
- docs-host assumption capture,
- canonical-vs-derived consumer boundaries,
- feature/target/toolchain slice truth,
- validation-plan and validation-report packaging,
- and assistant/editor overlay freshness and authority limits.

That is the same pattern seen elsewhere in this archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this is the maintainer-authored learning surface,”
- “these are the docs/guides/examples/compile-guidance lanes it contains,”
- “these feature/target/docs-host assumptions shaped it,”
- “these checks were actually run,”
- “these downstream consumers are only rendering or deriving overlays,”
- and “this is the portable pack humans and tools may consume.”

That is bigger than doctests and smaller than a universal docs platform.

The sharpened rule is that the missing layer must keep **API docs, guides, executable proof, compile guidance, docs-host posture, structured machine imports, and derived consumer overlays** visibly separate instead of flattening them into a single documentation story.
