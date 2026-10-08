# Design: Canonical Learning Stack (DocProof + Compile Guidance)

This is a stack note explaining how existing archive pieces should compose, and it should now be read together with [`design/canonical-learning-execution-blueprint-2026Q1.md`](./canonical-learning-execution-blueprint-2026Q1.md), [`design/canonical-learning-lane-map.md`](./canonical-learning-lane-map.md), [`design/canonical-learning-pilot-program.md`](./canonical-learning-pilot-program.md), [`design/canonical-learning-consumer-pilot-program.md`](./canonical-learning-consumer-pilot-program.md), and [`proposals/epic-canonical-learning-stack.md`](../proposals/epic-canonical-learning-stack.md).

## Goal
Describe one strategically important missing seam in the Rust ecosystem:
**maintainer-authored canonical learning truth**.

Rust already has many excellent point tools for docs, examples, diagnostics, compile-fail tests, and editor assistance.
What it still lacks is a cleanly articulated stack in which:
- maintainers publish reviewable learning surfaces,
- those surfaces stay canonical for both humans and tools,
- and downstream consumers (editors, assistants, atlas/guides, release/support review) import that truth instead of silently replacing it.

This stack is the archive’s answer to that missing seam.

The concrete rule for what must stay separate now lives in [`design/canonical-learning-lane-map.md`](./canonical-learning-lane-map.md): **API-doc/reference + guide/tutorial + executable-example proof + compile-guidance/negative-teaching + docs-host/build posture + structured machine-import + derived consumer overlays + review/handoff imports** should remain distinct lanes rather than collapsing into one “docs quality” or “smart docs” verdict.

## Why this now matters more
Three current Rust signals line up unusually well:

1. The 2025 State of Rust survey says online docs remain the preferred canonical reference, while some learning traffic appears to be shifting toward LLM tooling and agentic editors.
2. Rust’s recent vision work explicitly recommends expanding extensibility to include **better diagnostics and guidance from crates**.
3. docs.rs, rustdoc, mdBook, and compile-fail tooling already provide enough primitives that the missing work is now orchestration, artifacts, and boundaries — not basic feasibility.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://docs.rs/about/metadata
- https://doc.rust-lang.org/rustdoc/documentation-tests.html
- https://rust-lang.github.io/mdBook/cli/test.html
- https://docs.rs/trybuild

## Stack members

### 1) DocProof Kit
Owns:
- guide surfaces,
- example inventories,
- validation plans and reports,
- docs-host assumptions,
- transcript and guide verification.

Primary artifacts:
- `guide-profile/v0`
- `example-catalog/v0`
- `doc-check-plan/v0`
- `doc-check-report/v0`
- `doc-pack/v0`

Reference files:
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/docproof-pilot-program.md`](./docproof-pilot-program.md)
- [`proposals/epic-docproof-kit.md`](../proposals/epic-docproof-kit.md)

### 2) Compile Guidance Kit
Owns:
- crate-authored compile-time diagnostics,
- lint catalogs and fix posture,
- compile-fail guidance examples,
- hook-profile imports,
- guidance check reports.

Primary artifacts:
- `guidance-surface/v0`
- `diagnostic-catalog/v0`
- `lint-catalog/v0`
- `guidance-example-catalog/v0`
- `guidance-check-report/v0`
- `guidance-pack/v0`

Reference files:
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`design/compile-guidance-pilot-program.md`](./compile-guidance-pilot-program.md)
- [`proposals/epic-compile-guidance-kit.md`](../proposals/epic-compile-guidance-kit.md)

## Why these belong together
They are both **maintainer-authored canonical learning layers**.
They differ in medium, but not in role:
- DocProof covers API-doc/reference, guide/tutorial, transcript, and positive executable-example lanes.
- Compile Guidance covers compiler-time explanations, lint/help text, and negative-teaching / compile-fail lanes.
- The canonical-learning consumer layer then imports those lanes as structured machine inputs and renders bounded overlays without becoming the new canon.

Together they answer a missing ecosystem question:
> what is the intended way this crate teaches people how to use it, and what evidence shows that teaching surface still works?

That is stronger than either docs-only or diagnostics-only framing.

## Attachment points that must stay distinct
This stack is useful only if it refuses to become a mega-schema.

### Support Envelope Kit imports docs/support truth
Support Envelope may consume docs target and support-level facts, but it should not redefine guide/example inventories.

### Semantic Context Kit imports canonical inputs
Semantic Context can ingest rustdoc JSON, docs metadata, and guidance artifacts, but it is a consumer and derived-query substrate, not the maintainer-authored truth source.

### Edit Workflow Kit consumes guidance; it does not replace it
Fix suggestions, refactors, and assistant proposals may use compile-guidance artifacts, but edit tooling should not silently rewrite or infer the canonical guidance contract.

### Ecosystem Atlas can derive guidance overlays
Atlas/guides may use docproof and guidance packs as freshness-aware inputs, but curation overlays remain derived outputs, not the underlying canonical learning record.

## Shared consumer-execution layer
The stack now needs an explicit downstream import contract.

That layer is captured in [`design/canonical-learning-consumer-pilot-program.md`](./canonical-learning-consumer-pilot-program.md).
Its job is to prove that docs hosts, CI, editors, assistants, atlas views, and release/support consumers can import canonical learning artifacts while staying visibly **derived**.

The stack-level execution order that places this consumer lane after canonical authoring but before wider atlas/support/release reuse now lives in [`design/canonical-learning-pilot-program.md`](./canonical-learning-pilot-program.md).

The key rule is simple:
> maintainers author canon; consumers import, render, suggest, and review — but do not silently replace it.

This means future canonical-learning work should prefer:
- explicit consumer profiles over ambient scraping,
- import reports over hidden caches,
- overlay reports over silent synthesis,
- and authority boundaries over vague “AI-enhanced docs” claims.

## Ranked contribution program
The strongest practical path is now the stack-level rollout in [`design/canonical-learning-pilot-program.md`](./canonical-learning-pilot-program.md):
1. publish the lane catalog and API-doc/reference lane first,
2. guide/tutorial lane second,
3. executable-example + compile-guidance evidence lanes third,
4. bounded consumer-import / overlay lane fourth,
5. atlas/support/release-review handoff lane fifth.

Under that rollout:
- the **DocProof pilot program** turns public docs/guides/transcripts into attachable evidence;
- the **Compile Guidance pilot program** stops crate-authored diagnostics and compile-fail teaching from living only in stderr fixtures and local lore;
- the shared **canonical-learning consumer pilot** proves that docs hosts, CI, editors, and assistants can import canonical surfaces with explicit derivation markers and authority boundaries.

This is intentionally the reverse of a tool-first strategy.
The archive should prefer canonical inputs first and derived automation second.

## What a worthy contribution would look like
A serious contribution here would:
- preserve source-of-truth boundaries between docs, compile guidance, and derived tool context;
- attach artifacts to releases, CI, and guide consumers;
- make support levels and illustrative-only zones explicit;
- survive multi-target, multi-feature, multi-toolchain reality;
- and improve what assistants/editors can do **without** making assistants/editors the new canon.

## Anti-goals
Do not turn this stack into:
- one giant “learning schema” that absorbs everything;
- a ranking engine for documentation quality;
- an assistant-specific index format;
- or a cargo command that claims to replace rustdoc, mdBook, `trybuild`, `trycmd`, or editor tooling.

The stack is a **strategic composition**, not a replacement platform.

## Why this is strategically missing
Rust has already learned that public APIs, release evidence, support claims, and supply-chain signals benefit from attachable artifacts.
The same is increasingly true for learning surfaces.
As docs remain canonical and more people arrive through LLM/editor mediation, the ecosystem needs **canonical learning artifacts** that are explicit enough for humans, CI, docs hosts, editors, and assistants to share.

That is why this stack now deserves promotion in the archive.
