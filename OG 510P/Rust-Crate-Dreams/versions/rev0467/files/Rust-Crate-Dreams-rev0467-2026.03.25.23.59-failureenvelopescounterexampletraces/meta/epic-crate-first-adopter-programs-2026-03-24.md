# Epic crate first-adopter programs — 2026-03-24

This note turns the archive’s “worth it in theory” work into a tighter operational question:

> What narrow first-adopter programs would prove that the leading crates are valuable in practice?

The point is not to design giant launches.
It is to define `0.1` adoption loops that are small enough to ship and honest enough to evaluate.

## Main judgment

A worthy first-adopter program should have all of these:

1. a **specific cohort**,
2. a **single recurring task**,
3. a **compact packet family**,
4. a **clear success / failure test**,
5. and an explicit **non-claim**.

If a proposed crate cannot survive that structure, it still may be important, but it is not yet a real near-term build target.

## P-0509 — Crate Ecosystem Pathfinder

### First cohort
Small platform or application teams standardizing a starter stack for one concrete scenario:
- desktop GUI,
- Wasm component/plugin host,
- mixed-language interop,
- local-first sync,
- air-gapped enterprise,
- safety-critical boundary stack.

### Recurring task
“Choose a starter set and hand it to another team without starting the debate from scratch next month.”

### `0.1` packet family
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `manual-review.note.md`
- `revisit-trigger.policy.json`

### Success test
A second team can replay the packet, understand the trade-offs, and either adopt or challenge the choice without redoing raw crate discovery from zero.

### Failure test
The packet still reads like a list of crates plus vibes, or it cannot explain why an excluded candidate lost.

### Non-claim
Pathfinder does **not** determine the globally best crate.
It only freezes and explains a choice for a scoped task profile.

## P-0536 — Crate Knowledge Pack

### First cohort
Teams or tools that need current crate knowledge with pinned sources:
- internal assistants,
- review bots,
- human reviewers who keep reopening the same docs tabs.

### Recurring task
“Answer the same crate support and capability question twice and get the same grounded answer.”

### `0.1` packet family
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `query-support.matrix.json`
- `answer-boundary.note.md`

### Success test
A consumer can answer a bounded question with citations, identify where the answer came from, and know when to refuse.

### Failure test
The pack degrades into generic summaries, uncited imports, or unsupported cross-version identity assumptions.

### Non-claim
This crate does **not** prove semantic correctness of every answer or replace human review of ambiguous substrate.

## P-0486 — Debuggability Support Contract

### First cohort
Teams debugging one recurring session family:
- local dev sessions,
- CI artifact analysis,
- containerized reproduction,
- remote process attach,
- post-mortem crash inspection.

### Recurring task
“Tell another engineer what debugging workflows are actually available before they lose an hour discovering missing symbols or backend ceilings.”

### `0.1` packet family
- `session-family.report.json`
- `capability-witness.report.json`
- `claim-ceiling.report.json`
- `debug-support-bundle.manifest.json`
- `manual-review.note.md`

### Success test
An engineer can tell whether a given session family supports attach, stepping, variable inspection, async visibility, or expression evaluation without discovering the answer ad hoc.

### Failure test
The packet collapses all debugging capability into one score or hides backend/toolchain/target splits.

### Non-claim
This crate does **not** prove that a debugging session will be pleasant or successful in every environment.

## P-0496 — Cargo Vendor & Source Parity

### First cohort
Teams that already use one of these and keep getting surprised:
- `cargo vendor`,
- source replacement,
- local mirrors,
- CI-local registries,
- path/git exceptions in otherwise vendored graphs.

### Recurring task
“Hand another person one honest report of where the graph really came from and whether the build is as offline/mirrored/vendored as claimed.”

### `0.1` packet family
- `source-origin.receipt.json`
- `source-parity.lock`
- `source-coverage.report.json`
- `vendor-parity.report.json`
- optional `mirror-verification.import.json`

### Success test
A reviewer can tell which logical source IDs resolved, which physical roots were used, what stayed outside the covered boundary, and whether imported mirror verification changes the workspace-local verdict.

### Failure test
The tool turns mirror verification into a fake universal parity claim or hides `[patch]`, path, git, or alias splits.

### Non-claim
This crate does **not** replace mirror infrastructure, artifact transfer tooling, or a package-review system.

## Shared launch rule

For all four programs:
- the first release should privilege **boring packets** over richer UI;
- each packet should be inspectable in version control;
- each program should start with one or two task profiles, not a universal taxonomy.

## Why this matters for ranking

These adopter loops strengthen the current practical queue because they reveal which lanes can plausibly ship useful `0.1`s soonest:

1. **P-0509**
2. **P-0536**
3. **P-0486**
4. **P-0496**
5. **P-0472**
6. **P-0489**

That order does not mean other lanes are unimportant.
It means these are the ones the archive can now describe most concretely in product terms.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
