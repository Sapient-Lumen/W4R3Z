# Crate Knowledge Pack — review bundle plan (2026-03-24)

This note deepens **P-0536 Crate Knowledge Pack Kit** around one practical product question:

> what should another engineer actually receive on day one when a crate maintainer wants to hand over a compact, reviewable support packet?

## Main judgment

The missing value is not just “machine-readable crate data”.
It is a **review bundle** that serves three different receivers without bluffing:
- a human reviewer,
- a support or integration engineer,
- and a tool / assistant consumer.

The review bundle should stay compact.
It should not try to replace a full doc host, search engine, or chat product.

## `0.1` review bundle family

A worthy first release should center on six files:

1. `review-packet.manifest.json`
2. `assistant-context.pack.json`
3. `query-support.matrix.json`
4. `claim-trace.report.json`
5. `citation-locator.receipt.json`
6. `answer-boundary.note.md`

These sit above the earlier basis files such as:
- `material-basis.receipt.json`
- `export-policy.receipt.json`
- `excerpt-lineage.report.json`
- `item-witness.manifest.json`
- `build-surface.receipt.json`
- `conditioned-availability.report.json`

## Why a manifest is the missing layer

The archive already had strong artifact ideas.
What it still needed was the one file that says:
- which members are in this support packet,
- which audiences it serves,
- which question classes it is meant for,
- and which packet members are required for reuse.

That is what `review-packet.manifest.json` should do.

## Proposed `review-packet.manifest.json`

Suggested fields:
- `schema_name`
- `schema_version`
- `crate`
- `profile`
- `packet_members[]`
  - `name`
  - `kind`
  - `required`
  - `purpose`
- `primary_receivers[]`
- `supported_query_classes[]`
- `manual_review_query_classes[]`
- `derived_from[]`
- `notes[]`

Questions it answers:
- What exact packet is this?
- Who should receive it?
- Which files are optional versus required?
- Which question classes is it intended to support?

## Receiver-specific promise

### 1. Reviewer
Should be able to answer:
- what claims are supported,
- which claims are only partial,
- and what still requires manual review.

### 2. Support / integration engineer
Should be able to answer:
- where the getting-started and API packet is,
- whether feature/target differences matter,
- and whether setup/performance/security/safety questions are inside or outside scope.

### 3. Tool / assistant consumer
Should be able to answer:
- what machine-facing slice exists,
- what citation routes are legal,
- and what question classes must still be refused.

## CLI shape

Suggested commands:
- `cargo crate-knowledge review-bundle`
- `cargo crate-knowledge doctor review-bundle`
- `cargo crate-knowledge explain-query-class <class>`
- `cargo crate-knowledge diff-review-bundle <old> <new>`

## Library split

Suggested modules:
- `basis` — materials, exports, excerpts, hosted imports
- `identity` — item witnesses and locator integrity
- `availability` — build surface and conditioned availability
- `answerability` — query-support and answer-boundary rules
- `review_bundle` — review-packet manifest and emitters
- `doctor` — conservative checks

## Good first proving grounds

1. a crate with strong docs.rs pages and a README, but where task-fit questions still need manual review;
2. a target-sensitive crate where the default docs.rs route is not the whole story;
3. a crate used in a pathfinder packet, where the decision packet needs a pinned review packet beneath it.

## Early doctor checks

- warn when a review bundle points at floating `latest` locators without a resolved version basis;
- warn when `supported_query_classes` contradict `query-support.matrix.json`;
- warn when a supported class lacks locator or claim-trace coverage;
- warn when performance/security/safety classes are exported without explicit manual-review posture;
- warn when a packet looks assistant-ready but has no answer-boundary note.

## Boundaries that matter

This crate should refuse to claim:
- that a review bundle replaces the full documentation set,
- that a citation-ready packet proves task fit,
- that a compact pack answers performance or safety questions by default,
- or that one bundle is equally appropriate for teaching, shipping, and regulated review.

## Product rule

A worthy `0.1` should make one support conversation boring:

> “Here is the exact packet, what it can answer, what it cites, and what still needs human judgment.”

If it can do that honestly, it is already useful.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
