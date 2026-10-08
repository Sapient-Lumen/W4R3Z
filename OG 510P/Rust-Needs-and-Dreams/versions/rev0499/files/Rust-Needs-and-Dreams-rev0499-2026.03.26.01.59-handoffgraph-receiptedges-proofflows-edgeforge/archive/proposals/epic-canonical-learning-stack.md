# Epic Proposal: Canonical Learning Stack (`cargo learncanon` + `canonical-learning-pack/v0`)

## One-sentence pitch
Make Rust learning surfaces boring by standardizing a thin review boundary that keeps **API docs, guides, executable proof, compile guidance, docs-host assumptions, structured machine imports, and derived consumer overlays** distinct instead of forcing every project to scatter its teaching truth across prose, stderr, CI glue, and assistant memory.

## Deliverables
- reference command:
  - `cargo learncanon`
- schemas:
  - `learning-lane-catalog/v0`
  - `canonical-learning-brief/v0`
  - `canonical-learning-sources/v0`
  - `canonical-learning-check-report/v0`
  - `canonical-learning-consumer-handoff/v0`
  - `canonical-learning-pack/v0`
  - `canonical-learning-diff/v0`
- adapters/importers for:
  - `doc-pack/v0`
  - `guidance-pack/v0`
  - docs.rs metadata / docs-host posture
  - docs.rs rustdoc JSON pointers
  - rustdoc doctest results
  - mdBook test results
  - compile-fail teaching results
  - consumer-profile / overlay imports from the canonical-learning consumer lane
- docs:
  - API-doc + docs.rs recipe
  - guide-book + mdBook recipe
  - compile-guidance + compile-fail recipe
  - consumer-overlay / assistant-boundary recipe
  - atlas/support/release import guide

## Why now (signals)
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference while some learning traffic appears to be shifting toward LLM tooling, and it separately notes that editors with agentic support are on the rise.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2025 vision work explicitly recommends extending crates toward **better diagnostics and guidance from crates**. That is direct evidence that compile-time teaching belongs in the same strategic conversation as docs.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs already provides configurable docs-build metadata, documents docs-host-specific cfg/env/build behavior, and now builds and hosts rustdoc JSON. That means Rust already has both human-facing and machine-facing documentation surfaces worth importing rather than recomputing.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
  https://docs.rs/about/rustdoc-json
- rustdoc already executes documentation examples as tests and supports `compile_fail`, `no_run`, and edition-tagged doctests; Rust 1.94 also added `#[cfg(doctest)]`, which makes docs-test-specific surfaces even more explicit.
  https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
  https://doc.rust-lang.org/beta/releases.html
- mdBook has a first-class `test` command and documents CI use for validating Rust code examples in books.
  https://rust-lang.github.io/mdBook/cli/test.html
  https://rust-lang.github.io/mdBook/continuous-integration.html
- `trybuild` already gives Rust a credible compile-fail teaching/testing lane.
  https://docs.rs/trybuild

## Non-goals
- replacing rustdoc, docs.rs, mdBook, `trybuild`, editors, or assistants;
- defining one universal docs format or one giant learning schema;
- inventing a scalar documentation-quality score;
- making hosted docs or assistant summaries the new source of truth;
- silently flattening docs, diagnostics, guide books, support posture, and release review into one mega-surface.

## Strategic value
This deserves promotion because it gives the archive a missing **teaching-truth composition point**.
With it:
- API docs, guide books, and compile guidance can share one explicit learning subject;
- docs-host assumptions and validation evidence can travel with that subject;
- editors, assistants, atlas systems, and release/support tooling can import canonical learning truth without quietly becoming the new canon;
- maintainers can publish teaching surfaces once and let many downstream tools reuse them honestly.

The prize is not a better docs portal.
The prize is a durable record of **what the maintainer intended to teach, what assumptions shaped that teaching surface, what was actually checked, what downstream consumers merely derived, and what they are allowed to conclude**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
0. publish `learning-lane-catalog/v0` first so API-doc/reference, guide/tutorial, executable-proof, compile-guidance, docs-host, machine-import, consumer-overlay, and review/handoff lanes stay explicit;
1. make `canonical-learning-brief/v0` the canonical declaration of learning subject, present lanes, assumptions, intended consumers, and success bar;
2. import `doc-pack/v0` and `guidance-pack/v0` as the maintainer-authored canonical learning surfaces;
3. import docs.rs metadata / docs-host posture, rustdoc doctest results, mdBook test results, and compile-fail teaching results as explicit evidence lanes;
4. emit `canonical-learning-check-report/v0`, `canonical-learning-consumer-handoff/v0`, `canonical-learning-pack/v0`, and `canonical-learning-diff/v0` so editors/assistants/atlas/release/support consumers can reuse learning truth without scraping;
5. preserve a hard rule that consumer overlays stay visibly **derived** and never silently promote themselves to canon.

## Critical design bet
The critical bet is that **canonical learning becomes useful before Rust converges on one universal docs host, one universal editor surface, or one universal AI context format**.
That means:
- rustdoc, docs.rs, mdBook, and compile-fail fixtures already provide enough substrate to anchor canonical teaching artifacts;
- structured imports like rustdoc JSON already justify machine consumers;
- rising editor/assistant use makes explicit authority boundaries more necessary, not less;
- partial, target-specific, or docs-host-specific learning coverage is still worth packaging if uncertainty remains visible.

Without that boundary, every downstream learning consumer either stays too local to reuse or quietly starts pretending it owns the truth.

## Milestones
1. **v0 API-doc + docs-host lane**
   - `canonical-learning-brief/v0`
   - `canonical-learning-sources/v0`
   - docs.rs metadata / docs-host imports
2. **v0.2 guide-book lane**
   - mdBook test imports
   - guide-oriented validation reporting
3. **v0.3 compile-guidance lane**
   - `guidance-pack/v0` imports
   - compile-fail / compile-guidance evidence
4. **v0.4 consumer-overlay lane**
   - `canonical-learning-consumer-handoff/v0`
   - explicit derived/not-canonical markers
5. **v1 cross-stack consumers**
   - `canonical-learning-pack/v0`
   - `canonical-learning-diff/v0`
   - atlas / support / release-review / assistant slices with bounded authority

## Execution order
Use [`design/canonical-learning-pilot-program.md`](../design/canonical-learning-pilot-program.md) as the stack-level rollout:
1. API docs + docs.rs lane,
2. guide-book lane,
3. compile-guidance lane,
4. shared consumer-import lane,
5. atlas/support/release-review lane.

Use [`proposals/epic-docproof-kit.md`](./epic-docproof-kit.md) and [`proposals/epic-compile-guidance-kit.md`](./epic-compile-guidance-kit.md) as the leaf-level execution guides beneath it, and use [`design/canonical-learning-consumer-pilot-program.md`](../design/canonical-learning-consumer-pilot-program.md) as the bounded-consumer execution layer.

## Success metrics
- reviewers can distinguish canonical docs/guides/compile guidance from derived overlays without reading CI glue or assistant prompts;
- docs-host assumptions and validation coverage remain explicit instead of hiding in metadata tables or failing builds;
- at least two downstream consumers can import the same canonical-learning pack without bespoke scraping;
- assistant/editor consumers can stay useful without pretending they own support, policy, or mutation authority;
- the ecosystem gets one explainable canonical-learning seam instead of scattered READMEs, book tests, stderr fixtures, docs-host quirks, and memory.
