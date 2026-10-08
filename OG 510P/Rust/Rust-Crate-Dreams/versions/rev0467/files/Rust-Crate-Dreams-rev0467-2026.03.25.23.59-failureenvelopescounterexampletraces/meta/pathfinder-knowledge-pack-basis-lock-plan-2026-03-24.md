# Pathfinder + knowledge-pack basis-lock plan — 2026-03-24

## Purpose

This note makes one implementation point concrete:

> a Pathfinder decision packet should not stand alone; it should be able to point to a replayable basis lock assembled by the Knowledge Pack lane.

This is the narrowest practical move that makes the archive’s “front-door stack” credible.

## Product idea in one sentence

**P-0509** should hand another engineer a decision packet.
**P-0536** should hand that packet a frozen basis lock and review packet.

Together, they should let a team answer:
- what did we choose,
- what did we exclude,
- what evidence basis supported that,
- and what still needs manual review.

## Proposed artifact family

### Pathfinder-facing
- `task-profile.json`
- `decision-packet.manifest.json`
- `candidate-elimination.receipt.json`
- `starter-set.lock.json`
- `answer-boundary.note.md`

### Knowledge-pack-facing
- `review-packet.manifest.json`
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `query-support.matrix.json`
- `citation-locator.receipt.json`
- `basis-lock.manifest.json`

### Shared cross-lane members
- `basis-lock.manifest.json`
- `manual-gap.note.md`
- `imported-trust-surface.import.json`

## What the basis lock should capture

The lock should say, at minimum:
- exact crate version or versions under review,
- registry/index route and checksum-bearing release identity where available,
- publication-time information when the decision has a freeze window,
- docs.rs hosted recipe and rustdoc JSON format/version details,
- workspace and target filters if the packet is target-specific,
- packaged-state / VCS witness if repository drift versus package state matters,
- imported trust or advisory signals kept separate from task fit,
- and declared incompletenesses.

## Suggested CLI shape

This is theory/planning, not a fixed API, but a worthy first cut might look like:

```text
cargo crate-knowledge pack --crate iced --version 0.13.1 --emit out/knowledge-pack
cargo crate-knowledge basis-lock --crate iced --version 0.13.1 --emit out/basis-lock
cargo crate-pathfinder decide --task-profile gui-task.json --knowledge-pack out/knowledge-pack --basis-lock out/basis-lock --emit out/decision
```

The core idea is not the exact flags.
It is that Pathfinder should be able to consume a pinned basis packet instead of freehand browsing.

## What this should provide other people

For another team, this pairing should provide:
- a compact **decision packet**,
- a compact **review packet**,
- a frozen **basis lock**,
- and a clear **answer boundary**.

That is enough for architecture review, support triage, or an assistant/tool import loop.

## Failure modes this prevents

This plan is specifically trying to prevent:
- ranking pages with no replayable basis,
- decisions built from floating `latest` links,
- target-blind task-fit claims,
- trust surfaces being mistaken for architecture review,
- and future archive passes pretending that “we looked at the docs” is a reusable artifact.

## Phase order

### Phase 1 — narrow replayable basis
- capture registry, docs, and package witnesses for a single crate/version
- emit `basis-lock.manifest.json`
- emit `review-packet.manifest.json`

### Phase 2 — decision packet integration
- let Pathfinder consume basis locks for candidate crates
- emit candidate elimination receipts and a starter-set lock

### Phase 3 — cross-target and policy variants
- add target-filtered topology witnesses
- add source/mirror policy variants for restricted delivery
- add more explicit manual-gap notes for safety-critical and interop-heavy use

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
