# Gap: macro workflows and proc-macro migration

## What is missing
Rust now has a clearer long-range direction for macros than it did a year ago, but the day-to-day workflow is still fragmented.

Upstream language work is explicitly trying to make `macro_rules!` capable enough to cover much more of today’s proc-macro territory, with the stated goal of making many projects build faster, simplifying macros, and reducing the dependency supply chain. At the same time, the reflection-and-comptime work says outright that proc-macro derives have historically been hard to debug and bootstrap from scratch. Meanwhile, the current practical toolbox is still split across:
- Cargo visibility aids (`cargo tree` hiding/marking proc-macro crates),
- textual expansion tools like `cargo-expand`,
- IDE-side proc-macro toggles and ignore lists in rust-analyzer,
- and the raw compiler/proc-macro execution model.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://docs.rs/crate/cargo-expand/latest
- https://rust-analyzer.github.io/book/configuration
- https://doc.rust-lang.org/beta/releases.html
- https://doc.rust-lang.org/reference/procedural-macros.html

## The current seam is awkward
Today, teams can usually answer one macro question at a time, but not all of them together.
They can often:
- inspect expanded text with `cargo expand`,
- enable or disable proc-macro support in the IDE,
- and notice proc-macro crates in dependency trees.

But they still struggle to answer, in one coherent workflow:
- which proc macros are present and why,
- what compile-time cost they are adding,
- which expansions are stable enough to review,
- where a macro panic or bad expansion is easiest to reproduce,
- which proc macros are plausible candidates for future declarative/reflection migration,
- and how to publish those answers as CI-reviewable artifacts instead of screenshots and ad hoc notes.

`cargo-expand` itself documents that expansion-to-text is a lossy debugging aid. rust-analyzer also still models proc-macro support as a configurable feature with explicit ignore lists. Cargo has improved visibility by marking proc-macro crates in `cargo tree`, but that is still inventory, not workflow.

Sources:
- https://docs.rs/crate/cargo-expand/latest
- https://rust-analyzer.github.io/book/configuration
- https://doc.rust-lang.org/beta/releases.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html

## Why this matters
This gap is strategically larger than macro ergonomics alone.
It affects:
1. **build time and cacheability** — heavy proc-macro stacks amplify compile cost and dependency churn;
2. **supply-chain review** — proc macros execute during compilation with the compiler’s ambient resources and have the same security concerns as build scripts;
3. **IDE and debugging quality** — expansion, ignored macros, and reproducible failures remain split across tools;
4. **migration planning** — if Rust succeeds in shifting more derive/attribute use cases toward declarative macros or reflection/comptime workflows, teams will need help deciding what to migrate first and how to measure the benefit.

The reference model for procedural macros is still a separate `proc-macro` crate that cannot use its own macros and that runs during compilation with compiler-level file-access concerns. That makes the workflow problem real even before sandboxing or language evolution enter the picture.

Source:
- https://doc.rust-lang.org/reference/procedural-macros.html

## What “good” looks like
A worthy contribution here is not “replace proc macros” and not “invent a new macro system”.
It is a shared workflow and artifact layer:
- one `macro-inventory/v0` that records proc-macro crates, macro kinds, dependency weight, and call sites;
- one `macro-expansion-pack/v0` for targeted expansion snapshots with explicit lossy/raw markers;
- one `macro-cost-report/v0` for compile-time attribution and hotspots;
- one `macro-debug-report/v0` for panics, failing inputs, and minimal repro handles;
- one `macro-migration-hints/v0` for plausible declarative/reflection/comptime candidates;
- and one `macro-pack/v0` bundle for CI, issue attachments, release notes, or design review.

That would let Rust improve macro workflows now, while also creating a practical bridge toward any future proc-macro-reduction story.
