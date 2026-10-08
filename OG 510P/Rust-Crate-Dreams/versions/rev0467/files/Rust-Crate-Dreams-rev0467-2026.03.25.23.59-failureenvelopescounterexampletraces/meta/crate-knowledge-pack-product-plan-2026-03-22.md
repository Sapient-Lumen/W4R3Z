# Crate Knowledge Pack Kit — product plan (2026-03-22)

## Product shape

Deliver **P-0536** as:

1. a library for import / normalize / classify / slice / diff / pack;
2. a cargo-adjacent CLI for local capture, hosted-import reconciliation, and machine-consumable export;
3. a compact schema family that support systems, search indices, CI jobs, and assistant pipelines can import without scraping docs HTML directly.

## Receiver-facing promise

Given a Rust crate, another engineer should be able to tell:

- what public items exist and which source of authority named them;
- which docs pages and README/tutorial sources are canonical versus merely imported;
- which examples are official, runnable, compile-only, illustrative, generated, stale, or manual-review-only;
- which features / targets / `cfg`s materially change visibility;
- what docs.rs actually hosted;
- and what small slice should be handed to support/search/assistant consumers.

## v0.1 commands

- `cargo crate-knowledge pack`
- `cargo crate-knowledge doctor <bundle>`
- `cargo crate-knowledge slice <bundle> <profile>`
- `cargo crate-knowledge diff <old> <new>`
- `cargo crate-knowledge explain-provenance <bundle>`

## v0.1 artifact set

- `api-surface.receipt.json`
- `docs-source.manifest.json`
- `example-lineage.report.json`
- `feature-target-visibility.report.json`
- `docsrs-presence.import.json`
- `knowledge-slice.manifest.json`
- `assistant-context.pack.json`
- `knowledge-diff.report.json`
- `knowledge-pack.manifest.json`

## v0.1 implementation stance

- import rustdoc JSON and cargo metadata first;
- import docs.rs hosted facts conservatively and keep them separate from local observations;
- maintain a strict distinction between **authority**, **import**, and **inference**;
- start with non-executing capture plus imported doctest/example support facts rather than trying to execute examples directly;
- prefer small stable slice profiles over free-form prompt generation.

## Stage 1

Freeze the core authority/provenance vocabulary:

- `api-surface.receipt`
- `docs-source.manifest`
- `example-lineage.report`
- `docsrs-presence.import`
- `knowledge-pack.manifest`

Do not build a UI, indexer, or hosted service yet.

## Stage 2

Add standard slice profiles such as:

- `getting_started`
- `public_api_minimal`
- `feature_gated_surface`
- `ffi_surface`
- `async_usage`
- `support_triage`

## Stage 3

Add richer diffing, redaction presets, docs-debt imports, and issue-template / CI adapters.

## Adoption targets

1. crate maintainers who want a canonical export above rustdoc/docs.rs fragments;
2. support engineers answering repeated “how do I use this crate?” questions;
3. local search / docs indexing tools;
4. assistant and IDE workflows that need a compact crate-shaped handoff object;
5. release reviewers checking docs/example/API drift before publish.

## Why this is worth building now

The official ecosystem signal is unusually aligned:

- the 2025 State of Rust survey says online docs remain the preferred canonical reference, code study remains a major learning route, and LLM-like tooling is increasingly part of learning behavior;
- docs.rs now explicitly hosts rustdoc JSON and documents hosted README behavior, metadata knobs, target posture, and resource ceilings;
- the RFC and rustdoc/Cargo books keep stressing that JSON output exists to support alternative tooling fronts, but it remains experimental and version-sensitive;
- the broader Rust challenge story keeps pointing toward domain-specific friction, which raises the value of compact, provenance-aware handoff artifacts over generic portals.

## Design guardrails

- Never flatten “docs.rs page exists” into “this is canonical guidance.”
- Never flatten “README snippet exists” into “official runnable example.”
- Never flatten “rustdoc JSON named an item” into “all users can see it under current feature/target choices.”
- Never flatten “assistant slice exists” into “the assistant is authoritative.”
- Never mix imported upstream facts and locally inferred facts without an exactness class.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- https://doc.rust-lang.org/rustdoc/unstable-features.html
- https://rust-lang.github.io/rfcs/2963-rustdoc-json.html

## 2026-03-22 artifact-completeness addendum

The next high-leverage product move is **not** a retrieval UI.
It is to make the compact export itself reviewable.

Promote these three artifacts to first-class status:

- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`

Working rule:
- do not ship a “small assistant/support slice” unless it can say what exact materials fed it,
- whether those materials were pinned or floating,
- what export/redaction policy shaped it,
- and which exact excerpts entered the result.


## 2026-03-23 citation-locator addendum

The next high-leverage move is **not** a retrieval UI.
It is to make exported citations reviewable.

Promote these two artifacts to first-class status:

- `citation-locator.receipt.json`
- `citation-capability.report.json`

Working rule:
- do not call a compact export “citation-ready” unless it can resolve floating docs.rs routes to an exact version where possible, keep targets explicit, and publish which query classes still require manual review because locator fidelity is missing.


## 2026-03-23 item-witness addendum

The next high-leverage move is **not** a smarter retrieval stack.
It is to make item identity reviewable.

Promote these two artifacts to first-class status:

- `item-witness.manifest.json`
- `identity-fidelity.report.json`

Working rule:
- do not claim that two excerpts, claims, or locators refer to “the same item” across bundles unless the pack exports a witness record that keeps version, target, path/kind, raw opaque-ID scope, and any available source-span context explicit.

## 2026-03-23 build-surface / conditioned-availability addendum

The next high-leverage move is **not** a smarter retrieval stack.
It is to make visible crate knowledge recipe-aware.

Promote these two artifacts to first-class status:

- `build-surface.receipt.json`
- `conditioned-availability.report.json`

Working rule:
- do not claim that a docs/API/example surface is generally visible unless the pack can say which feature/target/docs-build recipe produced it,
- and do not let item identity or citation routing silently stand in for availability truth.
